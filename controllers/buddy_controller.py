import datetime

from models import Buddy


def add_buddy_request(request_json):
    arrival_date = request_json.pop('arrival_date')
    buddy = Buddy(**request_json)
    buddy.created_when = datetime.datetime.now()
    buddy.arrival_date = datetime.datetime.fromtimestamp(arrival_date)
    buddy.save()
    return {'buddy_id': str(buddy.id)}


def get_buddies(l=10, s=10, fields=[]):
    buddies = Buddy.objects.order_by('-created_when').only(*fields)
    return buddies


def get_buddy(_id):
    return Buddy.objects(id=_id).first()