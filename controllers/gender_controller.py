from models import Gender
from controllers.helper import *

def get_gender_by_id(_id, lang='en'):
    if lang == 'en':
        item = Gender.objects(_id=_id).exclude("_id").exclude("translation")
        item = json.loads(item.to_json())[0]
        return item

    elif lang:
        item = Gender.objects(_id=_id, translation__language=lang).only("translation").exclude("_id")[0]
        item = item2dict(item)
        item = translation_unify(item, lang)
        return item
    else:
        return []

def get_gender(lang):
    if lang == 'en':
        items = Gender.objects().exclude("translation")
        items = items2dict(items)

    elif lang:
        items = Gender.objects(translation__language=lang).exclude("name")
        items = items2dict(items)
        items = translations_unify(items, lang)
    else:
        items = []

    return items