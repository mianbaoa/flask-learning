"""import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post, Comment
#这个api测试感觉教材里的运行出来是错的```不是很明白```先放一放吧
class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()#获得程序上下文
        self.app_context.push()#推送上下文
        db.create_all()#相当于运行了一次配置名为testing的程序
        Role.insert_roles()
        self.client = self.app.test_client()#API不使用cookie所以不需要使用相应支持
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self,username,password):
        return {
            'Authorization':
                'Basic' + b64encode(
                    (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type':'application/json'
                }

    def test_no_auth(self):
        response=self.client.get(url_for('api.get_posts'),
                                 content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_posts(self):
        #添加一个用户
        r=Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u=User(email='john@exampel.com',password='cat',confirmed=True,role=r)
        db.session.add(u)
        db.session.commit()
        #写一篇文章
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)

        response=self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('john@exampel.com','cat'),
            data=json.dumps({'body':'body of the *blog* post'})
        )
        self.assertTrue(response.status_code== 201 )
        url=response.headers.get('Location')
        self.assertIsNotNone(url)
        #获取刚发布的文章
        response=self.client.get(url,
                                 headers=self.get_api_headers('john@exampel.com','cat'))
        self.assertTure(response.status_code==200)
        json_response=json.loads(response.data.decode('utf-8'))
        self.assertTure(json_response['url']==url)
        self.assertTure(json_response['body'=='body of the *blog* post'])
        self.assertTure(json_response['body_html'=='<p>body of the <em>blog<em> post<p>'])

    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('john@example.com', 'dog'))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)
"""
