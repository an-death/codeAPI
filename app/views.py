
from functools import wraps
from requests import codes as HTTP_CODE

from app import app
from app.models import User, AuthCode

from flask import jsonify, request, make_response


class Method:
    GET = 'GET'
    POST = 'POST'


def _validate_required_field(field, request):
    if field not in request.get_json():
        raise ValueError(f'Отсутствует обязательное поле {field}')


@app.route('/token', methods=['POST'])
def token():
    created = False

    try:
        _validate_required_field('email', request)
    except ValueError as e:
        return make_response(jsonify({'error': f'{e}'})), HTTP_CODE.bad

    data = request.get_json()
    email = data['email']

    if email and not User.is_exist(email=email):
        user = User.create_user(email=email)
        created = True
        payload = {'created': created, 'token': user.token}
        return make_response(jsonify(payload)), HTTP_CODE.created

    user = User.query.filter_by(email=email).first()
    payload = {'created': created, 'token': user.token}
    return make_response(jsonify(payload)), HTTP_CODE.ok


@app.route('/get_code', methods=['POST'])
def get_code():
    try:
        _validate_required_field('token', request)
    except ValueError as e:
        return make_response(jsonify({'error': f'{e}'})), HTTP_CODE.bad

    data = request.get_json()
    token = data['token']
    try:
        user = User.get_by_token(token)
        code = user.session.create_code()
    except ValueError as e:
        return make_response(jsonify({'error': f'{e}'})), HTTP_CODE.bad

    return make_response(jsonify({
        'code': code.code,
        'exp_period': app.config['EXP_SEC']
    })), HTTP_CODE.ok


@app.route('/valid_code', methods=['POST'])
def valid_code():
    try:
        _validate_required_field('token', request)
        _validate_required_field('code', request)
    except ValueError as e:
        return make_response(jsonify({'error': f'{e}'})), HTTP_CODE.bad

    data = request.get_json()
    token = data['token']
    code = data['code']

    try:
        user = User.get_by_token(token)
    except ValueError as e:
        make_response(jsonify({'error': f'{e}'})), HTTP_CODE.bad

    auth_code = AuthCode.query.filter(AuthCode.session == user.session).filter(AuthCode.code == code).first()

    if auth_code.is_code_valid():
        return make_response(jsonify({'valid': True})), HTTP_CODE.ok
    else:
        return make_response(jsonify({'valid': False})), HTTP_CODE.ok
