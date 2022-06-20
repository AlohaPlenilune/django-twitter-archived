from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from rest_framework.test import APIClient

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    def setUp(self):
        # This function will be executed whenever each test function is executed.
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@example.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        # 不能写成 User.objects.create()
        # 因为password需要被加密，username和email需要进行一些normalize处理
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # 每个测试函数必须以test_开头，才会被自动调用进行测试
        # 测试必须用POST而不是GET
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 登录失败，http status code 返回405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # 用了POST但密码错了
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        #验证还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # 用了正确的密码
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@example.com')

        # 验证已经登录了
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # 先登录
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # 验证用户已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 测试必须用post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 改用post成功logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        #验证用户已经登出
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)


    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@example.com',
            'password': 'any password',
        }

        # 测试get请求失败
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        #测试错误的邮箱
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试密码太短
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@example.com',
            'password': 'pass',
        })
        # print(response.data)
        self.assertEqual(response.status_code , 400)

        # 测试用户名太长
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooo loooooooong',
            'email': 'someone@example.com',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        # 成功注册
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'someone')

        # 验证用户已经登入
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
