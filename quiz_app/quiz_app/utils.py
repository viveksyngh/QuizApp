import hashlib
from django.http.response import JsonResponse
from datetime import datetime, timedelta
import json
from redis_utils import get_token, refresh_token
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

def gen_password_hash(passwd):
    return str(hashlib.sha256(passwd).hexdigest())


def validate_params(req_data, required_params):
    missing_params = []
    for param in required_params:
        if req_data.get(param) in [None, '']:
            missing_params.append(param)
    if len(missing_params) > 0:
        return False, 'Paramteres missing: ' + ','.join(missing_params)
    return True, None


def _send(data, status_code):
    return JsonResponse(data=data, status=status_code)


def send_200(data):
    return _send(data, 200)


def send_201(data):
    return _send(data, 201)


def send_400(data):
    return _send(data, 400)


def send_404(data):
    return _send(data, 404)


def send_204(data):
    return _send(data, 204)


def send_401(data):
    return _send(data, 401)


def send_410(data):
    return _send(data, 410)


def send_403(data):
    return _send(data, 403) 


def login(func):
    def inner(self, request, *args, **kwargs):
        response = {
            'message': '',
            'result': {}
        }
        request_method = request.method
        param_dict = getattr(request, request_method)
        if 'cid' not in param_dict:
            response["message"] = "Parameter missing cid."
            return send_400(response)

        if 'token' not in param_dict:
            response["message"] = "Parameter missing token"
            return send_400(response)
        
        cid = param_dict.get('cid')
        token = param_dict.get('token')

        stored_id = get_token(cid)
        if (not stored_id < 0) and (stored_id == token):
            refresh_token(cid)
        else:
            response["message"] = "Unauthorized"
            return send_401(response)
        return func(self, request, *args, **kwargs)
    return inner


INDEX_NAME = 'quiz'
DOC_TYPE = 'questions'


def create_index_in_elastic_search(body, id):
    es = Elasticsearch()
    es.create(index=INDEX_NAME, doc_type=DOC_TYPE, body=body, id=id)

def search_in_elastic(search_text):
    client = Elasticsearch()
    if search_text.strip() == '':
        s = Search(index=INDEX_NAME, doc_type=DOC_TYPE).using(client).query()
    else:     
        s = Search(index=INDEX_NAME, doc_type=DOC_TYPE).using(client).query("fuzzy", question=search_text)
    result = s.execute()
    print redis_utils
    return result


