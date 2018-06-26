from models import University
from controllers.helper import *

def get_university_by_id(_id, lang='en'):
    item = []
    if lang == 'en':
        item = University.objects(_id=_id).exclude("_id").exclude("translation")
        item = json.loads(item.to_json())[0]
    elif lang is not None:
        item = University.objects(_id=_id, translation__language=lang).only("translation").exclude("_id")[0]
        item = item2dict(item)
        item = translation_unify(item, lang)
    else:
        item = []
    return item