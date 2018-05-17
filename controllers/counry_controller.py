from controllers.helper import *
from models import Country


def get_country(fields=[], lang='en'):
    items = []
    if lang == 'en':
        items = Country.objects().exclude("translation")
        items = items2dict(items)
        # items = json.dumps(items)
    elif lang:
        items = Country.objects(translation__language=lang).exclude("name").exclude("language").order_by("translation__name")
        items = items2dict(items)

        items = translations_unify(items, lang)
    return items