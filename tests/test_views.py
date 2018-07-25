import json
import mock
from requests import codes as HTTP_CODE

from app import app
from app.models import User
from tests.base import BaseTestCase


class BaseViewTestCase(BaseTestCase):
    URL = None

    def _post(self, data):
        with self.client:
            response = self.client.post(self.URL, data=json.dumps(data),
                                        content_type='application/json'
                                        )

        return response


class TokenViewTests(BaseViewTestCase):
    URL = '/token'

    def test_empty_request(self):
        response = self._post({})
        # code is bad (400) and it`s ok
        self.assertEqual(HTTP_CODE.bad, response.status_code)
        self.assertIn('error', response.json)

    def test_create_user_if_not_exist_and_return_token(self):
        """ Test for user creation if not exist"""

        response = self._post({'email': 'email@email.ru'})
        # code is created (201)
        self.assertEqual(HTTP_CODE.created, response.status_code)

        data = response.json
        self.assertTrue(data['created'], 'Новый User не создан')
        self.assertTrue(data['token'], 'Отсутствует token')

    def test_return_token_for_exist_user(self):
        user = User.create_user('test@test.ru')

        response = self._post({'email': 'test@test.ru'})
        # code is ok
        self.assertEqual(HTTP_CODE.ok, response.status_code)

        data = response.json
        self.assertTrue(data['token'], 'Отсутствует token')
        # Not user created
        self.assertFalse(data['created'], 'Новый User создан, когда не должен был быть создан')
        # Token`s are same
        self.assertEqual(user.token, data['token'])


class GetCodeViewTests(BaseViewTestCase):
    URL = '/get_code'

    def test_get_code_return_error_without_token(self):
        response = self._post({})

        self.assertEqual(HTTP_CODE.bad, response.status_code)
        self.assertIn('error', response.json)

    def test_get_code_return_error_for_invalid_token(self):
        with mock.patch('app.models.user.User.get_by_token', side_effect=ValueError):
            response = self._post({})

        self.assertEqual(HTTP_CODE.bad, response.status_code)
        self.assertIn('error', response.json)

    def test_get_code_must_return_code_for_user(self):
        user = User.create_user('test@test.ru')
        response = self._post({'token': user.token})

        self.assertEqual(HTTP_CODE.ok, response.status_code)
        self.assertIn('code', response.json)

        data = response.json

        self.assertEqual(len(str(data['code'])), app.config['CODE_LENGTH'])


class ValidCodeViews(BaseViewTestCase):
    URL = '/valid_code'

    def test_get_code_return_error_without_token(self):
        response = self._post({})

        self.assertEqual(HTTP_CODE.bad, response.status_code)
        self.assertIn('error', response.json)

    def test_get_code_return_error_without_code(self):
        response = self._post({'token': 'test_token'})

        self.assertEqual(HTTP_CODE.bad, response.status_code)
        self.assertIn('error', response.json)

    def test_valid_code_view_must_return_True(self):
        user = User.create_user('test@test.ru')
        code = user.session.create_code()

        response = self._post({'token': user.token, 'code': code.code})

        self.assertEqual(HTTP_CODE.ok, response.status_code)

        self.assertTrue(response.json['valid'])

    def test_valid_code_view_must_return_False(self):
        user = User.create_user('test@test.ru')
        code = user.session.create_code()
        with mock.patch('app.models.session.AuthCode.is_code_valid', return_value=False):
            response = self._post({'token': user.token, 'code': code.code})

        self.assertEqual(HTTP_CODE.ok, response.status_code)

        self.assertFalse(response.json['valid'])
