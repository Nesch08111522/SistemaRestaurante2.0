"""Generate the business import templates in memory."""
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


FIELDS = (
    ('empresa', 'Nombre legal o comercial de la empresa', 'Sabores del Norte S.A.C.', 'Sí', ''),
    ('restaurante', 'Nombre visible para clientes', 'Restaurante Sol', 'Sí', ''),
    ('id_categoria', 'ID de categoría gastronómica', '', 'No', 'Elige un ID de la hoja Categorías.'),
    ('tipo_cocina', 'Especialidad gastronómica', 'Cocina criolla', 'No', ''),
    ('modalidad_servicio', 'Cómo atiende el negocio', 'dine_in_and_delivery', 'No', 'pickup_only | dine_in_only | dine_in_and_delivery | delivery_only'),
    ('tipo_menu', 'Tipo de carta', 'mixed', 'No', 'daily | a_la_carte | mixed'),
    ('precio_promedio', 'Precio promedio por persona en soles', '35.00', 'No', 'Número positivo con dos decimales.'),
    ('hora_apertura', 'Horario de apertura', '09:00', 'No', 'Formato HH:MM.'),
    ('hora_cierre', 'Horario de cierre', '22:00', 'No', 'Formato HH:MM.'),
    ('distrito', 'Distrito donde opera', 'Trujillo', 'Sí', ''),
    ('direccion', 'Dirección física', 'Av. Ejemplo 123', 'No', 'Vacío si publicarás solo distrito.'),
    ('latitud', 'Coordenada de latitud', '-8.1116', 'No', 'Úsala junto con longitud.'),
    ('longitud', 'Coordenada de longitud', '-79.0287', 'No', 'Úsala junto con latitud.'),
    ('telefono', 'Teléfono de atención', '+51 999 999 999', 'No', ''),
    ('url_imagen', 'URL HTTPS de portada', 'https://ejemplo.com/portada.jpg', 'No', 'Debe iniciar con https://'),
    ('descripcion', 'Presentación del restaurante', 'Cocina casera con ingredientes locales.', 'No', ''),
    ('etiquetas', 'Palabras clave', 'Criollo, familiar, almuerzos', 'No', 'Separar con comas.'),
    ('caracteristicas', 'Servicios y características', 'Terraza, wifi, estacionamiento', 'No', 'Separar con comas.'),
    ('restricciones_dieteticas', 'Opciones dietéticas', 'Vegetariano, sin gluten', 'No', 'Separar con comas.'),
    ('promocion_texto', 'Promoción o mensaje destacado', 'Menú especial de lunes a viernes', 'No', ''),
)


def _escape(value):
    return escape(str(value))


def _zip(entries):
    output = BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content.encode('utf-8'))
    output.seek(0)
    return output


def _cell(ref, value, style=None):
    styled = f' s="{style}"' if style is not None else ''
    return f'<c r="{ref}" t="inlineStr"{styled}><is><t>{_escape(value)}</t></is></c>'


def _row(number, values, style=None):
    return '<row r="%s">%s</row>' % (number, ''.join(_cell(f'{chr(65 + index)}{number}', value, style) for index, value in enumerate(values)))


def excel_template(categories):
    data_rows = [_row(1, ('Campo', 'Valor', 'Ejemplo', 'Obligatorio', 'Regla'), 1)]
    data_rows.extend(_row(index, value) for index, value in enumerate(FIELDS, 2))
    category_rows = [_row(1, ('ID', 'Categoría'), 1)]
    category_rows.extend(_row(index, (item['id_categoria'], item['nombre'])) for index, item in enumerate(categories, 2))
    sheet_one = ('<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" state="frozen"/></sheetView></sheetViews>'
        '<cols><col min="1" max="1" width="28" customWidth="1"/><col min="2" max="2" width="46" customWidth="1"/><col min="3" max="3" width="38" customWidth="1"/><col min="4" max="4" width="15" customWidth="1"/><col min="5" max="5" width="65" customWidth="1"/></cols>'
        f'<sheetData>{"".join(data_rows)}</sheetData><autoFilter ref="A1:E{len(data_rows)}"/></worksheet>')
    sheet_two = ('<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" state="frozen"/></sheetView></sheetViews>'
        '<cols><col min="1" max="1" width="12" customWidth="1"/><col min="2" max="2" width="36" customWidth="1"/></cols>'
        f'<sheetData>{"".join(category_rows)}</sheetData></worksheet>')
    return _zip({
        '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
        '_rels/.rels': '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        'xl/workbook.xml': '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Datos del negocio" sheetId="1" r:id="rId1"/><sheet name="Categorías" sheetId="2" r:id="rId2"/></sheets></workbook>',
        'xl/_rels/workbook.xml.rels': '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
        'xl/worksheets/sheet1.xml': sheet_one, 'xl/worksheets/sheet2.xml': sheet_two,
        'xl/styles.xml': '<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF167C80"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellXfs count="2"><xf fontId="0" fillId="0" borderId="0"/><xf fontId="1" fillId="1" borderId="0" applyFont="1" applyFill="1"/></cellXfs></styleSheet>',
    })


def word_template(categories):
    rows = ''.join('<w:tr>' + ''.join(f'<w:tc><w:p><w:r><w:t>{_escape(value)}</w:t></w:r></w:p></w:tc>' for value in field[:3]) + '</w:tr>' for field in FIELDS)
    category_text = ', '.join(f"{item['id_categoria']}: {item['nombre']}" for item in categories) or 'No hay categorías registradas aún.'
    document = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
        '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Plantilla de datos del negocio SmartResto</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Completa la columna Valor. Conserva los nombres de campo para que la IA los reconozca. Usa un solo negocio por documento.</w:t></w:r></w:p>'
        '<w:tbl><w:tr><w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Campo</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Valor</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Ejemplo</w:t></w:r></w:p></w:tc></w:tr>'
        f'{rows}</w:tbl><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Categorías disponibles</w:t></w:r></w:p><w:p><w:r><w:t>{_escape(category_text)}</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Valores permitidos: modalidad_servicio = pickup_only, dine_in_only, dine_in_and_delivery, delivery_only. tipo_menu = daily, a_la_carte, mixed. Horarios: HH:MM. Etiquetas y servicios: separados por comas.</w:t></w:r></w:p>'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')
    return _zip({
        '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        '_rels/.rels': '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        'word/document.xml': document,
    })
