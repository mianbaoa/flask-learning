import unittest
from flask import current_app
from app import create_app,db
class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()#获得程序上下文
        self.app_context.push()#推送上下文
        db.create_all()#相当于运行了一次配置名为testing的程序
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_app_exists(self):#第一个测试确保程序实例存在
        self.assertFalse(current_app is None)
    def test_app_is_testing(self):#第二个测试确保程序在测试配置中运行
        self.assertTrue(current_app.config['TESTING'])

