import json
import re
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

from django.conf import settings
from django.core.exceptions import ValidationError


def safe_filename(ext):
    """Генерируем своё имя — имени пользователя не доверяем."""
    return f'file_{uuid.uuid4().hex[:12]}{ext}'


def allowed_extension(filename):
    ext = Path(filename).suffix.lower()
    return ext if ext in ('.json', '.xml') else None


def validate_record(data):
    """Проверяет одну книгу. Возвращает очищенную или бросает ValidationError."""
    if not isinstance(data, dict):
        raise ValidationError('Запись должна быть объектом.')
    for field in ('title', 'author', 'year'):
        if not data.get(field):
            raise ValidationError(f'Поле "{field}" обязательно.')
    try:
        year = int(data['year'])
    except (TypeError, ValueError):
        raise ValidationError('year должен быть числом.')
    if not (1000 <= year <= 2100):
        raise ValidationError('year должен быть в диапазоне 1000..2100.')
    return {
        'title': str(data['title'])[:200],
        'author': str(data['author'])[:200],
        'year': year,
        'isbn': str(data.get('isbn', ''))[:20],
        'pages': int(data.get('pages') or 0),
    }


def validate_records(records):
    if not isinstance(records, list) or not records:
        raise ValidationError('Ожидается непустой список книг.')
    return [validate_record(r) for r in records]


def parse_file(path, ext):
    """Читает и валидирует файл .json или .xml."""
    try:
        if ext == '.json':
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        else:
            root = ET.parse(path).getroot()
            if root.tag != 'books':
                raise ValidationError('Корневой тег XML должен быть <books>.')
            data = [{c.tag: (c.text or '') for c in item} for item in root.findall('book')]
    except (json.JSONDecodeError, ET.ParseError) as e:
        raise ValidationError(f'Файл повреждён: {e}')
    return validate_records(data)


def save_file(records, fmt):
    """Сохраняет записи в файл .json или .xml."""
    ext = '.json' if fmt == 'json' else '.xml'
    path = settings.UPLOAD_DIR / safe_filename(ext)

    if ext == '.json':
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        root = ET.Element('books')
        for rec in records:
            item = ET.SubElement(root, 'book')
            for key in ('title', 'author', 'year', 'isbn', 'pages'):
                ET.SubElement(item, key).text = str(rec.get(key, ''))
        ET.indent(root)
        path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')

    return path


def list_files():
    """Возвращает список файлов из папки uploads с содержимым."""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    result = []
    for p in sorted(settings.UPLOAD_DIR.iterdir(), reverse=True):
        if p.is_file() and p.suffix.lower() in ('.json', '.xml'):
            result.append({
                'name': p.name,
                'content': p.read_text(encoding='utf-8'),
            })
    return result