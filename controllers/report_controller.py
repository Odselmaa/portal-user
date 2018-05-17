import json

import datetime

from bson import ObjectId
from werkzeug.exceptions import BadRequest

from controllers.helper import item2dict, translation_unify, items2dict, translations_unify
from models import Report

REPORT_STATUS = {"new": 1, "decided": 2}

def add_report(desc, user_id, user_informed):
    report = Report(description=desc,
                    user=user_id,
                    user_informed=user_informed,
                    status='new',
                    date_created=datetime.datetime.now())
    return report.save()


def get_reports(status='all', l=10):
    if status == 'all':
        return Report.objects.order_by('-date_created').limit(l)
    elif status in ["new", "decided"]:
        return Report.objects(status=status).order_by('-date_created').limit(l)
    else:
        return []


def update_report(_id, status):
    report = Report.objects(pk=ObjectId(_id))
    return report.update(status=status)