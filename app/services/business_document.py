"""Bounded, in-memory OOXML text extraction. No formulas, macros or links execute."""
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZipFile, BadZipFile
from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException
from app.blueprints.workspace import WorkspaceError

MAX_UPLOAD = 1024 * 1024
MAX_TEXT = 60000
S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def extract_document(data, filename):
    suffix = PurePosixPath(filename.lower()).suffix
    if suffix not in {'.xlsx','.docx'}:
        raise WorkspaceError('Usa Excel .xlsx o Word .docx. Convierte primero los archivos .xls o .doc.')
    if not data or len(data)>MAX_UPLOAD:
        raise WorkspaceError('Selecciona un archivo de hasta 1 MB.',413)
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries)>300 or sum(x.file_size for x in entries)>12*1024*1024 or len({x.filename for x in entries})!=len(entries):
                raise WorkspaceError('El documento contiene demasiados datos. Usa un archivo más pequeño.')
            if any(x.flag_bits & 1 or 'vbaproject' in x.filename.lower() for x in entries):
                raise WorkspaceError('No se admiten documentos cifrados ni archivos con macros.')
            def xml(name):
                return ET.fromstring(archive.read(name))
            lines=[]
            warnings=[]
            if suffix=='.docx':
                root=xml('word/document.xml')
                for paragraph in root.iter(W+'p'):
                    # Deleted revisions, drawings and embedded objects are not imported.
                    words=[]
                    def visit(node):
                        if node.tag in {W+'del',W+'drawing',W+'object'}: return
                        if node.tag==W+'t' and node.text: words.append(node.text)
                        for child in node: visit(child)
                    visit(paragraph)
                    if words: lines.append(''.join(words))
            else:
                workbook=xml('xl/workbook.xml')
                relationships={r.attrib['Id']:r.attrib.get('Target','') for r in xml('xl/_rels/workbook.xml.rels') if r.attrib.get('TargetMode')!='External'}
                shared=[]
                if 'xl/sharedStrings.xml' in archive.namelist():
                    shared=[''.join(x.text or '' for x in item.iter(S+'t')) for item in xml('xl/sharedStrings.xml')]
                for sheet in workbook.iter(S+'sheet'):
                    if sheet.attrib.get('state','visible')!='visible':
                        warnings.append('Se omitieron hojas ocultas.'); continue
                    target=relationships.get(sheet.attrib.get(R+'id'),'')
                    path=target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl')/target)
                    if not path.startswith('xl/worksheets/') or '..' in PurePosixPath(path).parts:
                        raise WorkspaceError('El libro tiene una estructura de hojas no compatible.')
                    lines.append('HOJA: '+sheet.attrib.get('name',''))
                    for row in xml(path).iter(S+'row'):
                        if row.attrib.get('hidden')=='1': continue
                        cells=[]
                        for cell in row.findall(S+'c'):
                            if cell.find(S+'f') is not None:
                                warnings.append('Se omitieron fórmulas; convierte sus resultados en valores para importarlos.'); continue
                            kind=cell.attrib.get('t')
                            value=cell.findtext(S+'v','')
                            if kind=='s': value=shared[int(value)]
                            elif kind=='inlineStr': value=''.join(x.text or '' for x in cell.iter(S+'t'))
                            elif kind=='e': continue
                            if value: cells.append(f"{cell.attrib.get('r','celda')}: {value}")
                        if cells: lines.append(' | '.join(cells))
            text='\n'.join(lines).strip()
            if not text or (suffix=='.xlsx' and all(line.startswith('HOJA: ') for line in lines)):
                raise WorkspaceError('No encontramos texto. Usa un documento con texto o celdas, no solo imágenes.')
            if len(text)>MAX_TEXT:
                raise WorkspaceError('El texto supera 60 000 caracteres. Separa los datos de un solo negocio en otro archivo.')
            return text,list(dict.fromkeys(warnings))
    except WorkspaceError:
        raise
    except (BadZipFile, KeyError, ValueError, IndexError, ET.ParseError, DefusedXmlException, RuntimeError, NotImplementedError):
        raise WorkspaceError('No se pudo leer el archivo. Comprueba que sea un .xlsx o .docx válido y sin contraseña.') from None
