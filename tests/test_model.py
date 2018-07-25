import time

from app import app, db
from app.models import User, AuthCode
from tests.base import BaseTestCase


class BaseModelsTestCase(BaseTestCase):
    def setUp(self):
        user = User.create_user(email='test@test.com')
        self.user = user
        self.session = user.session


class UserModelTests(BaseModelsTestCase):

    def test_user_created_and_have_token(self):
        new_user = User.create_user(email='new_user@email.ru')
        self.assertTrue(new_user.id)
        self.assertTrue(new_user.token)

    def test_user_exist_method_positive_test_case(self):
        self.assertTrue(User.is_exist(id=self.user.id), 'Проверка сущестрования User по id провалилась')
        self.assertTrue(User.is_exist(email=self.user.email), 'Проверка сущестрования User по email провалилась')

    def test_user_exist_method_negative_test_case(self):
        self.assertFalse(User.is_exist(id=123))
        self.assertFalse(User.is_exist(email='not_exist'))

    def test_user_token_property(self):
        token = self.user.token
        self.assertIsInstance(token, str)
        self.assertEqual(token, self.session.token.decode())

    def test_user_get_by_token_must_return_exist_user(self):
        expected_user = self.user
        token = expected_user.token
        user_by_token = User.get_by_token(token)

        self.assertEqual(expected_user, user_by_token)


class SessionModelTests(BaseModelsTestCase):

    def test_encode_auth_token(self):
        auth_token = self.session.encode_auth_token()
        self.assertIsInstance(auth_token, bytes)

    def test_decode_auth_token(self):
        expected_session_id = 1
        auth_token = self.session.encode_auth_token()
        self.assertIsInstance(auth_token, bytes)
        self.assertEqual(expected_session_id, self.session.decode_auth_token(auth_token))

    def test_decode_auth_token_must_raise_ValueError_for_corrupt_token(self):
        token = 'asdasdasd123'
        self.assertRaises(ValueError, self.session.decode_auth_token, token)

    def test_create_code_must_return_instance_of_AuthCode_with_code_value(self):
        auth_code = self.session.create_code()
        self.assertIsInstance(auth_code, AuthCode)
        self.assertTrue(auth_code.code)
        # Длина кода соответствет конффигу
        self.assertEqual(app.config['CODE_LENGTH'], len(str(auth_code.code)))


class AuthCodeTests(BaseTestCase):
    def setUp(self):
        self.auth_code = AuthCode()
        db.session.add(self.auth_code)
        db.session.commit()

    def test_generate_code_mist_return_instance_with_code(self):
        # До создания кода нет
        self.assertIsNone(self.auth_code.code)
        # Создаём код
        same_auth_code_with_code = self.auth_code.generate_code()

        self.assertEqual(self.auth_code, same_auth_code_with_code )
        self.assertEqual(app.config['CODE_LENGTH'], len(str(same_auth_code_with_code .code)))

    def test_is_valid_code_must_return_True(self):
        self.assertTrue(self.auth_code.is_code_valid())

    def test_is_valid_code_must_return_False(self):
        # wait 1 sec after create code
        time.sleep(1)
        # set exp_sec = 1
        self.assertFalse(self.auth_code.is_code_valid(1))

