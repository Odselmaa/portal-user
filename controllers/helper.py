import json


def translation_unify(object, lang):
    translation = object.pop("translation")
    translation = list(filter(lambda val: val["language"] == lang, translation))
    if len(translation) > 0:
        translation = translation[0]


    if len(translation) > 0:

        object.update(translation)
    # print(translation)
    # print(object)
    return object


def items2dict(items):
    if items == None:
        items = []
    else:
        items = json.loads(items.to_json())
    return items


def item2dict(items):
    if items == None:
        items = {}
    else:
        items = json.loads(items.to_json())
    return items

def translations_unify(objects, lang):
    objects = [translation_unify(object, lang) for object in objects]
    # print(objects)
    return objects
