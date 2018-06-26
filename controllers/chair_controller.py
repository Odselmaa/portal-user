from models import Chair
from controllers.helper import *

def get_chair_by_id(_id, lang='en', fields=[]):
    item = {}
    if lang == 'en':
        item = Chair.objects(_id=_id).only(*fields).exclude('translation').first()

    elif lang:
        item = Chair.objects(_id=_id, translation__language=lang).first()
    return item


def get_chair_by_code(code, lang='en', fields=[]):
    item = {}
    if lang == 'en':
        item = Chair.objects(code=code).only(*fields).exclude('translation').first()

    elif lang:
        item = Chair.objects(code=code, translation__language=lang).first()
    return item


def get_chairs(lang='en'):
    items = []
    if lang == 'en':
        items = Chair.objects().exclude("translation")
        items = items2dict(items)
    elif lang:
        items = Chair.objects(translation__language=lang).exclude("name").exclude("language")
        items = items2dict(items)
        items = translations_unify(items, lang)
    return items


def get_chairs_by_dep_id(dep_id, lang='en'):
    items = []
    if lang == 'en':
        items = Chair.objects(department=dep_id).exclude("translation").order_by('code')
        items = items2dict(items)
    elif lang:
        items = Chair.objects(translation__language=lang,department=dep_id).exclude("name").exclude("language").order_by('code')
        items = items2dict(items)
        items = translations_unify(items, lang)

    print(items)
    return items
