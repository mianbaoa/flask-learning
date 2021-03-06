"""import unittest
from app.models import User,Role,Permission,AnonymousUser,Follow
from app import db,create_app
import time
from datetime import datetime

class UserModelTestCase(unittest.TestCase):
    #前面这个两个函数是必不可少的，使测试能在测试数据库中运行，每当执行一个测试函数，都会已setUp开始，已tearDown结束！
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


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

    #<<<-----测试User里的验证邮箱的两个函数,generate_confirmtion_token跟confirm----->>>
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


    #<<<-----测试修改用户密码的两个函数generate_Reset_token跟Reset----->>>
    def test_valid_Reset_token(self):
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_Reset_token()
        self.assertTrue(u.Reset(token,'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_Reset_token(self):
        u1=User(password='cat')
        u2=User(password='dog')
        db.session.add_all([u1,u2])
        db.session.commit()
        token=u2.generate_Reset_token()
        self.assertFalse(u1.Reset(token,'pig'))
        self.assertTrue(u1.verify_password('cat'))

    #<<<-----测试修改邮箱账户的两个函数generate_newemail_token()跟change_email()----->>>

    def test_valid_email_change_token(self):
        u=User(email='zhang@163.com',password='cat')
        db.session.add(u)
        db.session.commit()
        token=u.generate_newemail_token('lu@163.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email=='lu@163.com')

    def test_invalid_email_change_token(self):
        u1=User(email='zhang@163.com',password='cat')
        u2=User(email='lu@163.com',password='dog')
        db.session.add_all([u1,u2])
        db.session.commit()
        token=u1.generate_newemail_token('zhong@163.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email=='lu@163.com')


    def test_duplicate_email_change_token(self):
        u1=User(email='zhang@163.com',password='cat')
        u2=User(email='lu@163.com',password='dog')
        db.session.add_all([u1,u2])
        db.session.commit()
        token=u2.generate_newemail_token('zhang@163.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email=='lu@163.com')


    def test_roles_and_permissions_admin(self):
        Role.insert_roles()
        u=User(email='592516704@qq.com',password='cat')
        self.assertTrue(u.is_administrator())

    def test_roles_and_permissions_putong(self):
        Role.insert_roles()
        u=User(email='lu@163.com',password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u=AnonymousUser()
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u=User(password='cat')
        db.session.add(u)
        db.session.commit()
        last_seen_before=u.last_seen
        time.sleep(2)
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_follow(self):
        u1=User(email='252353453@163.com',password='cat')
        u2=User(email='358648363@163.com',password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u1))
        self.assertTrue(u2.is_following(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u2)#这里的逻辑有点混乱
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)#测试删除一个用户，他的关注者和他的被关注者这层关系都会被删除
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)"""









