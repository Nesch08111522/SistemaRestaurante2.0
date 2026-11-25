from io import BytesIO
from zipfile import ZipFile
from unittest.mock import Mock
import pytest
from app.services.business_document import extract_document, MAX_UPLOAD
from app.ai.business_document import analyze_document
from app.blueprints.workspace import WorkspaceError
from tests.test_qa_regression import app, data, sign_in


def archive(files):
    out=BytesIO()
    with ZipFile(out,'w') as z:
        for name,content in files.items():z.writestr(name,content)
    return out.getvalue()


def word(text='Restaurante Sol. Distrito Lima.'):
    return archive({'word/document.xml':f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>'})


def excel():
    return archive({'xl/workbook.xml':'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Negocio" sheetId="1" r:id="rId1"/></sheets></workbook>',
    'xl/_rels/workbook.xml.rels':'<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>',
    'xl/sharedStrings.xml':'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Restaurante</t></si></sst>',
    'xl/worksheets/sheet1.xml':'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="inlineStr"><is><t>Sol</t></is></c><c r="C1"><f>1+1</f><v>2</v></c></row></sheetData></worksheet>'})


def test_extract_word():
    text,warnings=extract_document(word(),'local.docx')
    assert text=='Restaurante Sol. Distrito Lima.'
    assert warnings==[]


def test_extract_excel_shared_inline_and_skip_formula():
    text,warnings=extract_document(excel(),'local.xlsx')
    assert 'A1: Restaurante | B1: Sol' in text
    assert 'C1:' not in text
    assert 'fórmulas' in warnings[0]


def test_parameterized_excel_and_word_templates_are_extractable():
    from app.services.business_templates import excel_template, word_template
    categories = [{'id_categoria': 4, 'nombre': 'Criollo'}]
    excel_text, _ = extract_document(excel_template(categories).getvalue(), 'plantilla.xlsx')
    word_text, _ = extract_document(word_template(categories).getvalue(), 'plantilla.docx')
    assert 'empresa' in excel_text and 'A2: 4 | B2: Criollo' in excel_text
    assert 'Plantilla de datos del negocio SmartResto' in word_text and '4: Criollo' in word_text


@pytest.mark.parametrize('content,name',[(b'bad','local.docx'),(word(),'local.xls'),(b'x'*(MAX_UPLOAD+1),'local.xlsx'),(word(''),'local.docx'),(word('x'*60001),'local.docx'),(archive({'word/document.xml':'<!DOCTYPE doc [<!ENTITY x SYSTEM "file:///secret">]><doc>&x;</doc>'}),'local.docx'),(archive({'word/document.xml':'<doc/>','vbaProject.bin':'x'}),'local.docx')])
def test_invalid_documents(content,name):
    with pytest.raises(WorkspaceError):extract_document(content,name)


def test_ai_only_returns_supported_fields_with_evidence(monkeypatch):
    monkeypatch.setattr('app.ai.business_document.is_configured',lambda:True)
    call=Mock(return_value={'fields':{
        'restaurante':{'value':'Sol','evidence':'Restaurante Sol'},
        'id_empresa':{'value':'99','evidence':'Restaurante Sol'},
        'telefono':{'value':'123','evidence':'not present'},
        'url_imagen':{'value':'javascript:alert(1)','evidence':'Restaurante Sol'},
        'id_categoria':{'value':'4','evidence':'Criollo'},
        'latitud':{'value':'1','evidence':'Restaurante Sol'}}})
    monkeypatch.setattr('app.ai.business_document.call_json',call)
    proposals,warnings=analyze_document('Restaurante Sol. Criollo',[{'id_categoria':4,'nombre':'Criollo'}],1)
    assert {p['field'] for p in proposals}=={'restaurante','id_categoria'}
    assert warnings
    assert 'untrusted_document' in call.call_args.kwargs['user_prompt']


@pytest.mark.parametrize('result',[{'mock':True},{'fields':[]},{'fields':{}},{'multiple_businesses':True,'fields':{}}])
def test_no_fake_success_for_provider_failures(monkeypatch,result):
    monkeypatch.setattr('app.ai.business_document.is_configured',lambda:True)
    monkeypatch.setattr('app.ai.business_document.call_json',lambda **k:result)
    with pytest.raises(WorkspaceError):analyze_document('text',[],1)


def test_unconfigured_does_not_call_provider(monkeypatch):
    monkeypatch.setattr('app.ai.business_document.is_configured',lambda:False)
    call=Mock();monkeypatch.setattr('app.ai.business_document.call_json',call)
    with pytest.raises(WorkspaceError) as error:analyze_document('text',[],1)
    assert error.value.status==503
    call.assert_not_called()


def test_upload_requires_owner(app,data,monkeypatch):
    analyze=Mock(return_value=([{'field':'restaurante','value':'Sol'}],[]))
    monkeypatch.setattr('app.blueprints.owner.document_routes.analyze_document',analyze)
    with app.test_client() as c:
        assert c.post('/owner/api/documento/analizar').status_code==401
        sign_in(c)
        assert c.post('/owner/api/documento/analizar').status_code==403
        data[0]['rol']='business_owner'
        response=c.post('/owner/api/documento/analizar',data={'file':(BytesIO(word()),'local.docx')})
        assert response.status_code==200
        assert response.json['success'] is True
        assert analyze.call_args.args[2]==1


@pytest.mark.parametrize('format_name,mimetype,extension', [
    ('xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
    ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
])
def test_owner_can_download_parameterized_template(app, data, format_name, mimetype, extension):
    data[0]['rol'] = 'business_owner'
    with app.test_client() as client:
        sign_in(client)
        response = client.get(f'/owner/documento/plantilla/{format_name}')
    assert response.status_code == 200
    assert response.mimetype == mimetype
    assert f'filename=Plantilla_datos_negocio_SmartResto{extension}' in response.headers['Content-Disposition']
    text, _ = extract_document(response.data, f'plantilla{extension}')
    assert 'restaurante' in text


def test_upload_invalid_does_not_call_ai(app,data,monkeypatch):
    data[0]['rol']='business_owner'
    analyze=Mock();monkeypatch.setattr('app.blueprints.owner.document_routes.analyze_document',analyze)
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/owner/api/documento/analizar',data={'file':(BytesIO(b'bad'),'bad.docx')}).status_code==400
    analyze.assert_not_called()


def test_upload_requires_csrf(app,data):
    app.config['WTF_CSRF_ENABLED']=True
    data[0]['rol']='business_owner'
    with app.test_client() as c:
        sign_in(c)
        assert c.post('/owner/api/documento/analizar',data={'file':(BytesIO(word()),'local.docx')}).status_code==400
