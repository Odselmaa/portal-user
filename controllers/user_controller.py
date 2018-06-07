import datetime
import json

from bson import ObjectId
from flask import jsonify
from mongoengine import Q

from controllers.chair_controller import get_chair_by_id
from controllers.department_contoller import get_dep_by_id
from controllers.gender_controller import get_gender_by_id
from controllers.role_controller import get_role_by_id
from controllers.university_controller import get_university_by_id
from controllers.language_controller import get_language_by_id
from models import User, AccessToken, Gender, Chair, Department, Language, Country


def update_user(payload = {}, fields = []):
    if 'user_id' in payload:
        user_id = payload.pop('user_id')
        print(payload)

        user = User.objects(pk=user_id)
        if user is not None:
            user = user.first()

            if 'country' in payload: payload['country'] = Country(pk=payload['country'])
            if 'gender' in payload and payload['gender'] is not None: payload['gender'] = Gender(pk=int(payload['gender']))
            if 'languages' in payload: payload['languages'] = [Language(pk=lang) for lang in payload['languages']]
            if 'department' in payload and payload['department'] is not None: payload['department'] = Department(pk=int(payload['department']))
            if 'chair' in payload and payload['chair'] is not None: payload['chair'] = Chair(pk=int(payload['chair']))
            if 'bio' in payload: payload["bio"] = payload['bio']
            updated = user.update(**payload)
            print(user)
            return updated >= 1, payload
        else:
            print("Not found")
            return False, None
    else:
        print("Not found")
        return False, None


def get_user_by_id(_id, fields=[]):
    return User.objects(pk=_id).only(*fields).exclude('password').exclude("access_token").first()


def get_user_by_email(email, fields=[]):
    return User.objects(email=email).only(*fields).first()


def get_user_by_token(token):
    user = User.objects(access_token__token=token).exclude('password').first()
    return user


def add_user(user_json):
    user = User(**user_json)
    user.save()
    return {'user_id': str(user.id)}


def add_access_token(user, token):
    access_token = AccessToken(token=token,
                               provider='this',
                               created_when=datetime.datetime.now(),
                               expired_when=datetime.datetime.now() + datetime.timedelta(days=1))
    updated = user.update(access_token=access_token)
    return updated, access_token


def get_count():
    return User.objects.count()


# for USERS
def get_users(fields, search_keys, l, s):
    print(search_keys)
    search_key = search_keys.get('search_key', None)
    print(search_key)
    if search_key is not None and search_key!='':
        key = search_keys.get('search_key', None)
        users = User.objects.filter(Q(firstname__icontains=key) or Q(lastname__icontains=key)).only(*fields).skip(s).limit(l)
    else:
        users = User.objects.order_by('-date_created').only(*fields).skip(s).limit(l)

    if search_keys.get('email', None):
        users = users(email=search_keys['email']).first()
    if search_keys.get('university', None):
        users = users(university=search_keys['university'])
    if search_keys.get('department', None):
        users = users(department=search_keys['department'])
    if search_keys.get('chair', None):
        users = users(chair=search_keys['chair'])
    if search_keys.get('ulang', None):
        users = users(languages=search_keys['ulang'])
    if search_keys.get('gender', None):
        users = users(gender=search_keys['gender'])
    if search_keys.get('country', None):
        users = users(country=search_keys['country'])
    # print(users)
    return users


def get_users_raw(fields, l, s):
    users = User.objects.order_by('-date_created').only(*fields).skip(s).limit(l)
    return users


def get_friends(user_id, fields = [], lang='en'):
    user = User.objects(id=ObjectId(user_id)).first()
    friend_list = []
    for friend in user.friends:
        if friend:
            item = User.objects(id=ObjectId(friend)).only(*fields).first()
            item = json.loads(item.to_json(lang))
            friend_list.append(item)
    return friend_list


def set_user_block(user_id, blocked):
    user = User.objects(id=user_id).first()
    updated = user.update(blocked=blocked)
    return updated


def user_aggregate(user, fields, lang='en'):

    if 'gender' in fields and 'gender' in user: user['gender'] = get_gender_by_id(user['gender'], lang)
    if 'role' in fields: user['role'] = get_role_by_id(user['role'], lang)
    if 'university' in fields and 'university' in user:
        user['university'] = get_university_by_id(user['university'], lang)
    if 'chair' in fields and 'chair' in user:
        user['chair'] = get_chair_by_id(user['chair'], lang)
    if 'friends' in fields:
        if 'friends' in user: user['friends'] = user['friends']
        else: user['friends'] = []
    if 'department' in fields and 'department' in user:
        user['department'] = get_dep_by_id(user['department'], lang)
    if 'languages' in fields and 'languages' in user:
        user['languages'] = [get_language_by_id(_id, lang) for _id in user['languages']]

    # if 'friends_count' in fields: user['friends_count'] =
    return user

