import json

from werkzeug.exceptions import BadRequest

from controllers.helper import item2dict, translation_unify, items2dict, translations_unify
from models import Language

def get_language_by_id(_id, lang):
    item = {}
    if lang == 'en':
        item = Language.objects(_id=_id).exclude("translation").first()
        item = item2dict(item)

    elif lang == 'ru':
        item = Language.objects(_id=_id, translation__language=lang).only("translation")
        if item:
            item = item[0]
            item = item2dict(item)
            item = translation_unify(item, lang)
        else:
            item = {}
    return item


def get_languages(lang):
    items = []
    if lang == 'en':
        items = Language.objects().exclude("translation").order_by("name")
        items = items2dict(items)

    elif lang == 'ru':
        items = Language.objects(translation__language=lang).exclude("name").exclude("language")
        items = items2dict(items)
        items = translations_unify(items, lang)
    else:
        raise BadRequest

    return items