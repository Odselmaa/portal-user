import datetime

import mongoengine
from bson import ObjectId
from flask import json
from mongoengine import *

from bson import json_util


class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

# class MyDocument(Document):


class Translation(EmbeddedDocument):
    name = StringField(required=True)
    language = StringField(required=True)


class TranslationCode(EmbeddedDocument):
    code = StringField(required=True)
    name = StringField(required=True)
    language = StringField(required=True)


class TranslationUnit(EmbeddedDocument):
    code = StringField(required=True)
    name = StringField(required=True)
    language = StringField(required=True)
    description = StringField(default="Yass")


class AccessToken(EmbeddedDocument):

    provider = StringField(required=True)
    token = StringField(required=True)
    created_when = DateTimeField(required=True, default=datetime.datetime.now())
    expired_when = DateTimeField(required=True)

    meta = {'queryset_class': CustomQuerySet}

    def to_json(self):
        data = self.to_mongo()
        print(self)
        data['expired_when'] = data['expired_when'].timestamp()
        data['created_when'] = data['created_when'].timestamp()
        return json_util.dumps(data)


class Language(Document):
    _id = StringField(primary_key=True)
    _id.db_field = '_id'
    native_name = StringField(required=True)
    native_name.db_field = 'nativeName'
    language = StringField(required=True)
    name = StringField(required=True)
    translation = ListField(EmbeddedDocumentField(Translation))
    meta = {'queryset_class': CustomQuerySet}

    def get_l(self, lang = 'en'):
        if lang == 'en':
            return {'_id':self._id, 'native':self.native_name,'name':self.name }
        else:
            t = [item for item in self.translation if item["language"] == lang]

            return {'_id':self._id, 'native':self.native_name, 'name': t[0].name}


class Country(Document):
    _id = StringField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = ReferenceField(Language)
    languages = ListField(ReferenceField(Language))
    translation = ListField(EmbeddedDocumentField(Translation))
    meta = {
        'collection': 'country'
    }

    def get(self, lang = 'en'):
        if lang == 'en':
            return {'_id':self._id, 'name':self.name}
        else:
            t = [item for item in self.translation if item["language"] == lang]
            return {'_id':self._id,  'name': t[0].name }



class City(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = StringField(required=True)
    translation = ListField(EmbeddedDocumentField(Translation))


class Gender(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = StringField(required=True)
    translation = ListField(EmbeddedDocumentField(Translation))

    def get(self, lang = 'en'):
        if lang == 'en':
            return {'_id':self._id, 'name':self.name}
        else:
            t = [item for item in self.translation if item["language"] == lang]
            return {'_id':self._id, 'name': t[0].name }



class University(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = StringField(required=True)
    url = URLField()
    city = IntField()
    city.db_field = 'city_id'
    reviews = ListField()

    translation = EmbeddedDocumentListField(Translation)

    def get(self, lang = 'en'):
        if lang == 'en':
            return {'_id': self._id, 'code':self.name, 'url':self.url}
        else:
            return {'_id': self._id, 'code':self.translation[0].name, 'url': self.url}


class Department(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    code = StringField(required=True)
    name = StringField(required=True)
    language = StringField(required=True)
    link = StringField(required=True)
    description = StringField()
    translation = ListField(EmbeddedDocumentField(TranslationUnit))
    reviews = ListField(StringField(), default=[])
    # university = IntField()
    # university.db_field = 'uni_id'

    def get(self, lang = 'en'):
        if lang == 'en':
            return {'_id':self._id, 'code':self.code, 'name':self.name}
        else:
            t = [item for item in self.translation if item["language"] == lang]
            print(t)
            return {'_id':self._id, 'code':t[0].code, 'name':t[0].name}


    def to_json(self, lang='en', fields=[]):
        data = {}
        if lang != 'en':
            t = [item for item in self.translation if item["language"] == lang]
            if 'name' in fields: data['name'] = t[0].name
            if 'code' in fields: data['code'] = t[0].code
            if 'description' in fields: data['description'] = t[0].description
            if 'link' in fields: data['link'] =  self.link

            data['_id'] = self._id
        # del data['translation']
        else:
            data = self.to_mongo()
            del data['translation']
        return data


class Chair(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = StringField(required=True)
    code = StringField(required=True)
    description = StringField()
    department = IntField(required=True)
    department.db_field = "dep_id"

    translation = ListField(EmbeddedDocumentField(TranslationUnit))

    def get(self, lang = 'en'):
        if lang == 'en':
            return {'_id':self._id, 'code':self.code, 'name':self.name}
        else:
            t = [item for item in self.translation if item["language"] == lang]
            return {'_id':self._id, 'code':t[0].code, 'name':t[0].name}


    def to_json(self, lang='en', fields=[]):
        data = {}
        if lang != 'en':
            if 'name' in fields: data['name'] = self.translation[0].name
            if 'code' in fields: data['code'] = self.translation[0].code
            if 'description' in fields: data['description'] = self.translation[0].description
            if 'link' in fields: data['link'] = self.link

            data['_id'] = self._id
        # del data['translation']
        else:
            data = self.to_mongo()
            del data['translation']
        return data


class Role(Document):
    _id = IntField(primary_key=True)
    _id.db_field = '_id'
    name = StringField(required=True)
    language = StringField()
    translation = ListField(EmbeddedDocumentField(Translation))

    def get(self, lang='en'):
        if lang == 'en':
            return {'_id':self.id, 'name': self.name}
        else:
            t = [item for item in self.translation if item["language"] == lang]
            return {'_id':self.id, 'name': t[0].name}


class User(Document):
    firstname = StringField(required=True, max_length=512)
    lastname = StringField(required=True, max_length=512)
    role = ReferenceField(Role)
    country = ReferenceField(Country)
    # university = ReferenceField(University)
    department = ReferenceField(Department)
    chair = ReferenceField(Chair)
    blocked = BooleanField()
    socials = DictField(required=False)
    email = EmailField(required=True, max_length=256)
    verified_email = EmailField()
    is_verified = BooleanField(default=False)
    password = StringField(max_length=256)
    phone = StringField(max_length=15)
    bio = StringField(max_length=256)
    languages = ListField(ReferenceField(Language))
    friends = ListField(StringField(), max_length=1000)
    photos = ListField(max_length=1000)
    profile = StringField(max_length=40000)
    access_token = EmbeddedDocumentField(AccessToken)
    gender = ReferenceField(Gender)
    date_modified = DateTimeField()
    date_created = DateTimeField()
    news_tags = ListField(StringField(), default=[])
    meta = {'queryset_class': CustomQuerySet}

    def to_json(self, lang='en'):
        data = self.to_mongo()
        data['_id'] = str(self.id)
        if 'date_created' in data:
            data['date_created'] = self.date_created.timestamp()
        if 'department' in data:
            try:
                data['department'] = self.department.get(lang)
                # print(data['department'])
            except mongoengine.errors.DoesNotExist:
                data['department'] = {}

        if 'chair' in data:
            try:
                data['chair'] = self.chair.get(lang)
                # print(data['department'])
            except mongoengine.errors.DoesNotExist:
                data['chair'] = {}

        if 'role' in data:
            data['role'] = self.role.get(lang)

        if 'university' in data:
            data['university'] = self.university.get(lang)

        if 'country' in data:
            data['country'] = self.country.get(lang)

        if 'languages' in data:
            langs = []
            print(self.languages)
            for l in self.languages:
                langs.append(l.get_l(lang))
            data['languages'] = langs

        if 'gender' in data:
            data['gender'] = self.gender.get(lang)

        if 'friends' in data:
            for i, friend in enumerate(data['friends']):
                user = User.objects(id=friend).only(*['firstname', 'lastname', 'department']).first()
                data['friends'][i] = json.loads(user.to_json(lang))

        return json_util.dumps(data)

    def get_buddy(self):
        return {"id": str(self.id), "fullname": self.firstname + ' '+ self.lastname}


class Buddy(Document):
    user = ReferenceField(User)
    buddy = ReferenceField(User)
    arrival_date = DateTimeField(required=True)
    created_when = DateTimeField(required=True)

    place = StringField()
    confirmed = BooleanField(default=False)
    comment = StringField()
    meta = {'queryset_class': CustomQuerySet}

    def to_json(self):
        data = self.to_mongo()
        data['_id'] = str(self.id)
        if self.buddy:
            data['buddy'] = self.buddy.get_buddy()
        data['user'] = self.user.get_buddy()
        data['created_when'] = self.created_when.timestamp()
        data['arrival_date'] = self.arrival_date.timestamp()
        return json_util.dumps(data)

class Report(Document):
    description = StringField()
    user_informed = ReferenceField(User)
    user = ReferenceField(User)
    status = StringField(default='new')
    date_created = DateTimeField(required=True)
    date_modified = DateTimeField()
    meta = {'queryset_class': CustomQuerySet}

    def to_json(self):
        data = self.to_mongo()
        data['_id'] = str(self.id)
        data['user_informed'] = str(self.user_informed.id)
        data['user'] = str(self.user.id)
        data['users'] = {"user": {"fullname": self.user.firstname + " " +  self.user.lastname},
                                 "user_informed": {"fullname": self.user_informed.firstname + " "+ self.user_informed.lastname}}
        data['date_created'] = self.date_created.timestamp()
        return json_util.dumps(data)