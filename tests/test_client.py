"""
import unittest
from app.models import User,Role
from app import db,create_app
from flask import url_for
import re

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client=self.app.test_client(use_cookies=True)#self.client是Flask测试客户端对象，
        # 在这个对象上可以调用方法 get put post等等。。

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()#结束程序上下文

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('探险家' in response.get_data(as_text=True))
        #as_text=True后得到的是一个更易于处理的Unicode字符串

    def test_register_and_login(self):
        #注册新用户
        response=self.client.post(url_for('auth.register'),data={
            'email':'john@example.com',
            'username':'john',
            'password':'cat',
            'password2':'cat'
        },follow_redirects=True)#post方法第一个参数是视图函数，第二个参数是视图函数中表单想要输入的信息,
        # 第三个参数是follow_redirects=Ture，让测试客户端与浏览器一样,进行重定向而不是一个302状态
        data=response.get_data(as_text=True)
        self.assertTrue('一个验证' in data)#这里是验证是否是重定向
        #登录新用户
        response=self.client.post(url_for('auth.login'),data={
            'email':'john@example.com',
            'password':'cat'
        },follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('Hello,john!!!' in data)
        self.assertTrue('你还没有激活你的账户。' in data)

        #发送确认激活令牌
        user = User.query.filter_by(email='john@example.com').first()
        token=user.generate_confirmation_token()
        response=self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('认证成功，谢谢' in data)
        #注销账户
        response=self.client.get(url_for('auth.logout'),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('正在注销用户' in data)
"""
