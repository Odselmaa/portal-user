from werkzeug.exceptions import BadRequest

from models import Department
from controllers.helper import *


def get_dep_by_id(_id, lang='en', fields=[]):
    item = {}
    if lang == 'en':
        item = Department.objects(_id=_id).only(*fields).exclude('translation').first()

    elif lang:
        item = Department.objects(_id=_id, translation__language=lang).first()
    return item


def get_dep_by_code(code, lang='en', fields=[]):
    item = {}
    if lang == 'en':
        item = Department.objects(code=code).only(*fields).exclude('translation').first()

    elif lang:
        item = Department.objects(code=code, translation__language=lang).first()

    return item


def get_departments(lang='en', fields=[]):
    if lang == 'en':
        items = Department.objects().exclude("translation").only(*fields).order_by('code')
        items = items2dict(items)

    elif lang:
        items = Department.objects(translation__language=lang).only(*fields).only('translation').order_by('translation.code')
        items = items2dict(items)
        items = translations_unify(items, lang)
    else:
        raise BadRequest

    return items

