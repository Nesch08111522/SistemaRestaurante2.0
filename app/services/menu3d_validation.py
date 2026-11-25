"""Bounded image decoding and self-contained GLB validation. No filename trust."""
import io
import json
import struct
import warnings
from decimal import Decimal, InvalidOperation
from PIL import Image, ImageOps

MAX_IMAGE = 2 * 1024 * 1024
MAX_GLB = 50 * 1024 * 1024


def image_bytes(data):
    if not data or len(data) > MAX_IMAGE:
        raise ValueError('Cada fotografía debe pesar como máximo 2 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as im:
                fmt = im.format
                if fmt not in {'JPEG', 'PNG', 'WEBP'} or getattr(im, 'n_frames', 1) != 1:
                    raise ValueError('Usa una fotografía JPEG, PNG o WebP sin animación.')
                if min(im.size) < 64 or im.width * im.height > 20_000_000:
                    raise ValueError('La fotografía debe tener al menos 64 px y como máximo 20 megapíxeles.')
                im.verify()
            with Image.open(io.BytesIO(data)) as im:
                im = ImageOps.exif_transpose(im).convert('RGB')
                im.thumbnail((1600, 1600))
                out = io.BytesIO()
                im.save(out, 'JPEG', quality=88, optimize=True)
                return out.getvalue(), {'JPEG':'jpeg','PNG':'png','WEBP':'webp'}[fmt]
    except (OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError('La fotografía no es válida o está dañada.') from exc


def validate_glb(data, mime='model/gltf-binary'):
    if mime.split(';')[0].strip().lower() not in {'model/gltf-binary', 'application/octet-stream'}:
        raise ValueError('El proveedor no devolvió un archivo GLB.')
    if not 28 <= len(data) <= MAX_GLB:
        raise ValueError('El modelo está vacío o supera los 50 MB.')
    magic, version, length = struct.unpack_from('<4sII', data)
    if (magic, version, length) != (b'glTF', 2, len(data)):
        raise ValueError('Cabecera GLB inválida.')
    chunks, offset = [], 12
    while offset < length:
        if offset + 8 > length:
            raise ValueError('GLB truncado.')
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        if size % 4 or offset + size > length:
            raise ValueError('Bloque GLB inválido.')
        chunks.append((kind, data[offset:offset+size]))
        offset += size
    if len(chunks) != 2 or [c[0] for c in chunks] != [0x4E4F534A, 0x004E4942]:
        raise ValueError('Se requiere un GLB autocontenido con JSON y geometría binaria.')
    try:
        doc = json.loads(chunks[0][1])
        if doc['asset']['version'] != '2.0' or not doc.get('meshes') or not doc.get('scenes'):
            raise ValueError('GLB sin escena o geometría.')
        def no_uri(obj):
            if isinstance(obj, dict):
                if 'uri' in obj:
                    raise ValueError('El GLB contiene recursos externos no permitidos.')
                for val in obj.values(): no_uri(val)
            elif isinstance(obj, list):
                for val in obj: no_uri(val)
        no_uri(doc)
        buffers = doc.get('buffers', [])
        if len(buffers) != 1 or not 0 < buffers[0]['byteLength'] <= len(chunks[1][1]):
            raise ValueError('Buffer GLB inválido.')
        for view in doc.get('bufferViews', []):
            if view['buffer'] != 0 or view.get('byteOffset', 0) < 0 or view['byteLength'] <= 0:
                raise ValueError('Vista de buffer inválida.')
            if view.get('byteOffset', 0) + view['byteLength'] > buffers[0]['byteLength']:
                raise ValueError('Vista de buffer fuera de límites.')
        def ref(items, index):
            if type(index) is not int or not 0 <= index < len(items):
                raise ValueError('Referencia GLB fuera de límites.')
            return items[index]
        views = doc.get('bufferViews', [])
        accessors = doc.get('accessors', [])
        for accessor in accessors:
            # This module accepts static, uncompressed food meshes. Fail closed for
            # sparse/compressed data until a dedicated validator supports it.
            if 'sparse' in accessor:
                raise ValueError('Los modelos con geometría dispersa no están admitidos.')
            view = ref(views, accessor['bufferView'])
            width = {5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[accessor['componentType']]
            components = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[accessor['type']]
            count = accessor['count']; start = accessor.get('byteOffset',0)
            stride = view.get('byteStride',width*components)
            if type(count) is not int or not 0 < count <= 2_000_000 or start<0 or start % width or stride<width*components:
                raise ValueError('Accessor GLB inválido.')
            if start + (count-1)*stride + width*components > view['byteLength']:
                raise ValueError('Accessor fuera del buffer.')
        for mesh in doc['meshes']:
            if not mesh.get('primitives'):
                raise ValueError('Malla sin geometría.')
            for primitive in mesh['primitives']:
                position = ref(accessors, primitive['attributes']['POSITION'])
                if position['type'] != 'VEC3': raise ValueError('Posiciones GLB inválidas.')
                for index in primitive['attributes'].values(): ref(accessors,index)
                if 'indices' in primitive: ref(accessors,primitive['indices'])
                if 'material' in primitive: ref(doc.get('materials',[]),primitive['material'])
        nodes = doc.get('nodes',[])
        for n in nodes:
            if 'mesh' in n: ref(doc['meshes'],n['mesh'])
            for index in n.get('children',[]): ref(nodes,index)
        for scene in doc['scenes']:
            for index in scene.get('nodes',[]): ref(nodes,index)
        if not any('mesh' in n for n in nodes): raise ValueError('Escena sin un plato visible.')
        # Detect cycles before the browser traverses the scene graph.
        visited, active = set(), set()
        def visit(index):
            if index in active: raise ValueError('Jerarquía GLB circular.')
            if index in visited: return
            active.add(index)
            for child in nodes[index].get('children',[]): visit(child)
            active.remove(index); visited.add(index)
        for index in range(len(nodes)): visit(index)
        for image in doc.get('images',[]):
            view = ref(views,image['bufferView'])
            if image.get('mimeType') not in ('image/png','image/jpeg','image/webp'):
                raise ValueError('Textura GLB no admitida.')
            start = view.get('byteOffset',0)
            with Image.open(io.BytesIO(chunks[1][1][start:start+view['byteLength']])) as texture:
                if texture.width*texture.height>20_000_000: raise ValueError('Textura GLB demasiado grande.')
                texture.verify()
        return doc
    except (KeyError, TypeError, IndexError, RecursionError, UnicodeError, OSError, json.JSONDecodeError) as exc:
        raise ValueError('Estructura GLB inválida.') from exc


def dish_payload(body):
    if not isinstance(body, dict):
        raise ValueError('Se requiere un objeto JSON.')
    result = {}
    for key, size in [('nombre', 160), ('descripcion', 2000), ('categoria', 100)]:
        value = body.get(key, '')
        if not isinstance(value, str) or len(value) > size:
            raise ValueError(f'Campo {key} inválido (máximo {size} caracteres).')
        result[key] = value.strip()
    if not result['nombre']:
        raise ValueError('Indica el nombre del plato.')
    try:
        price = Decimal(str(body.get('precio')))
        if not price.is_finite() or not 0 <= price <= 999999 or price != price.quantize(Decimal('.01')):
            raise ValueError()
        result['precio'] = price
    except (ValueError, InvalidOperation):
        raise ValueError('Precio inválido; usa hasta dos decimales.') from None
    for key in ('esta_disponible', 'es_recomendado'):
        if type(body.get(key, False)) is not bool:
            raise ValueError(f'{key} debe ser booleano.')
        result[key] = body.get(key, False)
    for key in ('ingredientes', 'etiquetas', 'restricciones_dieteticas', 'alergenos'):
        items = body.get(key, [])
        if not isinstance(items, list) or len(items) > 40 or any(not isinstance(i,str) or len(i)>100 for i in items):
            raise ValueError(f'{key}: máximo 40 elementos de 100 caracteres.')
        result[key] = list(dict.fromkeys(i.strip() for i in items if i.strip()))
    return result
