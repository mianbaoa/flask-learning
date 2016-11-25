import unittest
from app.models import User
from app import db
import time

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):#只写属性测试
        u=User(password='cat')
        self.assertTrue(u.password_hash is not None)
    def test_no_password_getter(self):#读取属性时报错测试
        u=User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
    def test_password_verification(self):#测试verifu_password函数
        u=User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    def test_password_salts_are_random(self):#测试不同用户相同密码，他们的密码散列值不同
        u=User(password='cat')
        u_2=User(password='dog')
        self.assertTrue(u.password_hash != u_2.password_hash)
    def test_valid_confirmation_token(self):#这个是测试confirm函数
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_confirm_confirmation_token(self):#这个是验证confirm函数，不同id的令牌肯定不同
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add_all([u1,u2])
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_time_confirmation_token(self):#这个是验证过期令牌不能使用
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
