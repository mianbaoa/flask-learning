from selenium import webdriver
import unittest
from app.models import User,Role,Post
from app import db,create_app
from flask import url_for
import threading
import re
import time


class SeleniumTestCase(unittest.TestCase):
    client=None

    @classmethod
    def setUpClass(cls):
        #启动Firedox
        try:
            cls.client=webdriver.Firedox()
        except:
            pass
        if cls.client:
            #创建程序
            cls.app=create_app('testing')
            cls.app_context=cls.app.app_context()
            cls.app_context.push()#推动上下文
            #禁止日志，保持输出简洁，暂时不懂
            import logging
            logger=logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            #创建数据库，使用虚拟数据填充
            db.creat_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)
            #添加管理员
            admin_role=Role.query.filter_by(permissions=0xff).first()
            admin=User(email='592516704@qq.com',
                       password='z6291652',
                       confirmed=True,
                       username='Mr.zhang',
                       role=admin_role)
            db.session.add(admin)
            db.session.commit()
            #在一个线程中启动Flask服务器
            threading.Thread(target=cls.app.run).start()
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            #关闭Flask服务器跟浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            #销毁数据库
            db.drop_all
            db.session.remove()
            #删除程序上下文
            cls.app_context.pop()

    #如果不能用setupclass启动浏览器，client是空的，则直接跳过测试。返回到‘web浏览器无法使用’
    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        #进入首页
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+探险家',self.client.page_source))#后面的参数是打开的页面的所有内容


