import random
import string
from functools import wraps

import bson
from flask import Flask
from werkzeug.exceptions import InternalServerError, BadRequest, MethodNotAllowed, NotFound, Unauthorized
from mongoengine.errors import FieldDoesNotExist

from controllers.counry_controller import get_country
from controllers.gender_controller import get_gender
from flask import jsonify, request
import jwt
import requests
from flask_mongoengine import MongoEngine

from controllers.user_controller import *
from controllers.department_contoller import *
from controllers.language_controller import *
from controllers.chair_controller import *
from controllers.report_controller import *
from constants import *

app = Flask(__name__)
# mongodb://admin_od:SlzSc3ojy57B1L1s@cluster0-shard-00-00-prwwe.mongodb.net:27017,cluster0-shard-00-01-prwwe.mongodb.net:27017,cluster0-shard-00-02-prwwe.mongodb.net:27017/test?replicaSet=Cluster0-shard-0

app.config['MONGODB_DB'] = 'Portal'
app.config['MONGODB_HOST'] = 'mongodb://admin_od:SlzSc3ojy57B1L1s@cluster0-shard-00-00-prwwe.mongodb.net:27017,cluster0-shard-00-01-prwwe.mongodb.net:27017,cluster0-shard-00-02-prwwe.mongodb.net:27017/Portal?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin'
    # 'mongodb://admin_odko:WinniePooh@portalinternational-shard-00-00-3b6lw.mongodb.net:27017,' \
    #                   'portalinternational-shard-00-01-3b6lw.mongodb.net:27017,' \
    #                   'portalinternational-shard-00-02-3b6lw.mongodb.net:27017/Portal?ssl=true&replicaSet=PortalInternational-shard-0&authSource=admin'
app.config['MONGODB_USERNAME'] = 'admin_od'
app.config['MONGODB_PASSWORD'] = 'SlzSc3ojy57B1L1s'
db = MongoEngine()
db.init_app(app)

def only_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = (request.headers.get('Authorization'))
        bearer, access_token = auth_header.split()
        user = get_user_by_token(access_token)

        if user:
            if user.role.name == 'admin':
                return f(*args, **kwargs)
            else:
                return jsonify({STATUS_CODE: 400, RESPONSE: ADMIN_AUTHORIZATION_REQUIRED})
        else:
            return jsonify({STATUS_CODE: 404, RESPONSE: NOT_FOUND+' user'})

    return decorated_function


@app.route('/api/user/<string:user_id>', methods=['GET', 'DELETE', 'PUT'])
def specific_user(user_id):
    if request.method == 'GET':
        lang = request.args.get('lang', 'en')
        fields = request.args.get('fields', [])
        if fields!=[]:
            fields = fields.split(',')
        response = json.loads(get_user_by_id(ObjectId(user_id), fields).to_json(lang))
        return jsonify({'response': response,
                        'statusCode': 200}), 200

    elif request.method == 'PUT':
        payload = request.json
        if 'languages[]' in payload: payload['languages'] = payload.pop('languages[]')
        payload['user_id'] = user_id
        is_updated, user = update_user(payload)

        if is_updated:
            return jsonify({'response': "OK",
                        'statusCode': 200}), 200
        else:
            return jsonify({'response': BAD_REQUEST,
                            'statusCode': 400}), 400


@app.route('/api/user/<string:user_id>/block', methods=['POST'])
@only_admin
def block_user(user_id):
    if request.method == 'POST':
        should_block = request.json['blocked']
        
        response = set_user_block(user_id, should_block)
        return jsonify({'response': response,
                        'statusCode': 201}), 201
    else:
        raise MethodNotAllowed


@app.route('/api/user', methods=['GET', 'POST'])
def many_user():
    if request.method == 'GET':
        fields = request.args.get('fields', '')
        fields = fields.split(',')

        search_keys = request.args
        lang = request.args.get('lang', 'en')
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))

        users = get_users(fields, search_keys, limit, skip)
        users_json = []
        for user in users:
            user = json.loads(user.to_json(lang=lang))
            users_json.append(user)

        return jsonify({'response':
                            users_json,
                        'count':
                            get_count(),
                        'statusCode': 200}), 200

    elif request.method == 'POST':  # it returns access_token
        payload = request.json

        if 'payload' in payload:
            print(payload)
            user_json = jwt.decode(payload['payload'], 'f*ckyou', algorithms=['HS256'])
            del user_json['iat']
            if get_user_by_email(email=user_json['email'], fields=[]):
                return jsonify({'error': 'Email is already registered',
                                'statusCode': 409}), 409
            else:
                return jsonify({'response': add_user(user_json),
                                'statusCode': 201}), 201
        else:
            raise BadRequest


@app.route('/api/user/<string:user_id>/friend', methods=['GET'])
def friends(user_id):
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])
    if fields != []:
        fields = fields.split(',')

    return jsonify({'response': get_friends(user_id, fields, lang),
                    'statusCode': 200}), 200


@app.route('/api/user/<string:user_id>/friend/<string:friend_id>', methods=['POST', 'DELETE'])
def manage_friend(user_id, friend_id):
    if request.method == 'POST':
        if len(friend_id) == 24:
            user1 = get_user_by_id(user_id, fields=['friends'])
            if user1.friends is not None and friend_id in user1.friends:
                return jsonify({'statusCode': 200, 'response': 'Already friend'}), 200
            else:
                friend = get_user_by_id(friend_id, fields=['friends'])
                update1 = user1.update(push__friends=friend_id)
                update2 = friend.update(push__friends=user_id)
                
                return jsonify({'statusCode': 201, 'response': 'Friend added successfully'}), 201
        else:
            raise BadRequest
    elif request.method == 'DELETE':
        user1 = get_user_by_id(user_id, [])
        if user1.friends is not None and friend_id not in user1.friends:
            return jsonify({'statusCode': 200, 'response': 'Not a friend'}), 200
        else:
            friend = get_user_by_id(friend_id, [])
            update1 = user1.update(pull__friends=friend_id)
            update2 = friend.update(pull__friends=user_id)
            
            return jsonify({'statusCode': 200, 'response': 'Friend deleted successfully'}), 200


@app.route('/api/department', methods=['GET'])
# @login_required
def department():
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])
    if fields != []:
        fields = fields.split(',')
    return jsonify({'response': get_departments(lang=lang, fields=fields), 'statusCode': 200}), 200


@app.route('/api/department/<string:id_or_code>', methods=['GET'])
def spec_department(id_or_code):
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])

    if fields != []:
        fields = fields.split(',')
        if 'chairs' in fields:
            fields.remove('chairs')
    if id_or_code.isdigit():
        dep = get_dep_by_id(id_or_code, lang, fields)
    else:
        dep = get_dep_by_code(id_or_code.lower(), lang, fields)

    if dep:
        
        return jsonify({'response': dep.to_json(lang, fields), 'statusCode': 200}), 200
    else:
        raise NotFound

@app.route('/api/languages', methods=['GET'])
def languages():
    lang = request.args.get('lang', 'en')
    return jsonify({'response': get_languages(lang=lang), 'statusCode': 200}), 200


@app.route('/api/chair', methods=['GET'])
def chairs():
    lang = request.args.get('lang', 'en')
    return jsonify({'response': get_chairs(lang=lang), 'statusCode': 200}), 200


@app.route('/api/chair/<string:id_or_code>', methods=['GET'])
def chair(id_or_code):
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])
    if fields != []:
        fields = fields.split(',')

    if id_or_code.isdigit():
        chair = get_chair_by_id(id_or_code, lang, fields)
    else:
        chair = get_chair_by_code(id_or_code.lower(), lang, fields)
    if chair:
        response = chair.to_json(lang, fields)
        statusCode = 200
    else:
        response = {}
        statusCode = 404
    return jsonify({'response':response, 'statusCode': statusCode}), statusCode



@app.route('/api/chair/department/<int:dep_id>', methods=['GET'])
def chairs_by_dep_id(dep_id):
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])
    if fields != []:
        fields = fields.split(',')
    return jsonify({'response': get_chairs_by_dep_id(dep_id, lang=lang), 'statusCode': 200}), 200


@app.route('/api/gender', methods=['GET'])
def gender():
    lang = request.args.get('lang', 'en')
    return jsonify({'response': get_gender(lang=lang), 'statusCode': 200}), 200


@app.route('/api/country', methods=['GET'])
def country():
    lang = request.args.get('lang', 'en')
    fields = request.args.get('fields', [])
    if fields != []:
        fields = fields.split(',')
    return jsonify({'response': get_country(fields,lang=lang), 'statusCode': 200}), 200


@app.route('/api/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        payload = request.json
        if 'desc' in payload and 'user_id' in payload and 'user_informed':
            if add_report(payload['desc'], payload['user_id'], payload['user_informed']):
                return jsonify({'response': 'OK', 'statusCode': 200}), 200
            else:
                raise BadRequest
        else:
            raise BadRequest
    else:
        return jsonify({'response': get_reports(), 'statusCode':200}), 200


@app.route('/api/report/<string:status>', methods=['GET', 'PUT'])
def report_with(status):
    if request.method == 'GET':
        limit = int(request.args.get('limit'))
        reports = get_reports(status, limit)

        return jsonify({'response': json.loads(reports.to_json()), 'statusCode':200}), 200
    else:

        payload = request.json

        if 'id' in payload:
            updated = update_report(payload['id'], status)
            if updated == 0:
                return jsonify({STATUS_CODE: 404, RESPONSE: NOT_FOUND})
            else:
                return jsonify({'response': 'OK', 'statusCode': 200}), 200
        else:
            return jsonify({STATUS_CODE: 400, RESPONSE: BAD_REQUEST})


@app.route('/api/report/count', methods=['GET'])
def report_count():
    payload = request.json
    
    if 'desc' in payload and 'user_id' in payload and 'user_informed':
        if add_report(payload['desc'], payload['user_id'], payload['user_informed']):
            return jsonify({'response': 'OK', 'statusCode': 200}), 200
        else:
            raise BadRequest
    else:
        raise BadRequest


@app.route("/api/auth", methods=["POST"])
def authenticate():
    if "payload" in request.json:
        try:
            payload = request.json["payload"]

            user_json = jwt.decode(payload, "f*ckyou", algorithms=['HS256'])
            email = user_json.get("email", None)
            user = get_user_by_email(email, fields=["email", "password"])
            print(user_json)
            if user is not None and user.password == user_json["password"]:
                code = generate_code()
                result, access_token = add_access_token(user, code)
                return jsonify({"response": {"access_token": json.loads(access_token.to_json()), "user_id":str(user.pk)},
                                "statusCode": 200}), 200
            else:
                return jsonify({"response": "User not found",
                                "statusCode": 404}), 404
        except Exception as e:
            print(e)
            raise BadRequest
    else:
        raise BadRequest


@app.route("/api/token", methods=["POST"])
def refresh_token():
    if "access_token" in request.json:
        token = request.json["access_token"]
        user = get_user_by_token(token)
        if user:
            code = generate_code()
            _, token = add_access_token(user, code)
            return jsonify({"response": token, "statusCode": 200}), 200
        else:
            return jsonify({"response": "User not found", "statusCode": 404}), 404
    else:
        raise BadRequest


@app.route("/api/check_authorization/<string:access_token>", methods=["GET"])
def check_authorization(access_token):
    user = get_user_by_token(access_token)
    if user is not None:
        expired_when = user.access_token["expired_when"]
        if expired_when > datetime.datetime.now():
            return jsonify({"statusCode": 200, "response": "OK"}), 200
        else:
            raise Unauthorized

    else:
        raise NotFound


def generate_code():
    return "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))


@app.errorhandler(InternalServerError)
def gh_500(e):
    print(e)
    return jsonify({'statusCode': 500, 'response': str(e)}), 500


@app.errorhandler(Exception)
def gh_ex(e):
    return jsonify({'statusCode': 500, 'response': str(e)}), 500


@app.errorhandler(FieldDoesNotExist)
def gh_file_doesnt_exist(e):
    return jsonify({'statusCode': 400, 'response': str(e)}), 400


@app.errorhandler(Unauthorized)
def global_handler_bad_request(e):
    return jsonify({"statusCode": 401, "response": "Unauthorized"}), 401


@app.errorhandler(NotFound)
def global_handler_bad_request(e):
    return jsonify({"statusCode": 404, "response": "User not found"}), 404


@app.errorhandler(BadRequest)
def gh_bad_request(e):
    return jsonify({'statusCode': 400, 'response': str(e)}), 400


@app.errorhandler(bson.errors.InvalidId)
def gh_invalid_id(e):
    return jsonify({'statusCode': 404, 'response': 'Not found'}), 404


@app.errorhandler(MethodNotAllowed)
def gh_not(e):

    return jsonify({'statusCode': 400, 'response': str(e)}), 400


def send_request(URL, method, json):
    result = {}
    if method == 'GET':
        result = requests.get(URL, json=json).json()
    elif method == 'POST':
        result = requests.post(URL, json=json).json()
    elif method == 'PUT':
        result = requests.put(URL, json=json).json()
    elif method == 'DELETE':

        result = requests.delete(URL, json=json).json()
    return result


if __name__ == '__main__':
    app.run(port=5004)
