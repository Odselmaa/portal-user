from models import Role
from controllers.helper import *

def get_role_by_id(_id=1, lang="en"):
    item = []
    if lang == 'en':
        item = Role.objects(_id=_id).exclude("translation")
        item = json.loads(item.to_json())[0]

    elif lang is not None:
        item = Role.objects(_id=_id, translation__language=lang).only("translation")[0]
        item = item2dict(item)
        item = translation_unify(item, lang)
    else:
        item = []
    return item