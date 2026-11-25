# Completar la ficha desde Excel o Word

En el formulario de registro o edición, selecciona **Analizar archivo con IA**.
Admite `.xlsx` y `.docx` de hasta 1 MB, con texto/celdas de un solo negocio.
Los formatos antiguos `.xls` y `.doc` deben convertirse primero. No hay OCR de
fotografías ni ejecución de fórmulas/macros. Las fórmulas se omiten con aviso.

Incluye, cuando los conozcas: nombre de empresa y restaurante, categoría,
dirección, distrito, teléfono, descripción, especialidad, modalidad de atención,
horarios, precio promedio por persona, coordenadas, portada HTTPS, etiquetas,
servicios, opciones dietéticas y promoción. Un Excel con columnas **Campo** y
**Valor**, o un Word con esos mismos títulos, facilita la lectura. No es obligatorio
seguir una plantilla. Para horarios usa texto HH:MM en Excel.

La IA devuelve sugerencias con referencias del documento. Selecciona los campos
que quieras aplicar. Los campos con contenido previo aparecen desmarcados.
Aplicar solo modifica el formulario; guardar es una acción posterior. La opción
de privacidad de distrito prevalece sobre la importación de dirección y pin.

## Configuración

Instalar `requirements.txt`; se añadió `defusedxml` para analizar XML sin entidades
externas. Se reutiliza la configuración `OPENROUTER_API_KEY`, `AI_MODEL`,
`AI_BASE_URL` y `AI_TIMEOUT` del cliente existente. Reiniciar el servidor tras
cambiar variables. Sin clave o ante error del proveedor se muestra un error;
no se devuelven datos simulados como si fueran extraídos del documento.

El archivo se procesa en memoria y el texto extraído se envía al proveedor
configurado. El cliente IA conserva su auditoría de decisiones existente. El
documento es fuente de datos, no de instrucciones. Solo se devuelven campos
permitidos con evidencia literal y validación de formato. Los archivos tienen
límites de tamaño, contenido expandido y longitud de texto.

## Verificación

`python -m pytest tests/test_business_document.py -q`

Las pruebas usan archivos OOXML mínimos generados en memoria y respuestas
simuladas del proveedor. No envían documentos reales ni gastan créditos.
