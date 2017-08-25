#!/usr/bin/env python3.5
# -*- coding:utf-8 -*-
import os

COV=None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV=coverage.coverage(branch=True,include='app/*')
    COV.start()

from app import create_app,db
from app.models import User,Role,Post,Comment,Source,PostType
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app=create_app('default' or os.getenv('FLASK_CONFIG'))#getenv用来读取环境变量=environ.get差不多吧
manager=Manager(app)
migrate=Migrate(app,db)

def make_context_shell():
    return dict(User=User,Role=Role,Post=Post,db=db,app=app,Comment=Comment,Source=Source,PostType=PostType)
manager.add_command('shell',Shell(make_context=make_context_shell))
manager.add_command('db',MigrateCommand)

@manager.command
def test(coverage=False):
    """Run the unit tests"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE']='1'
        os.execvp(sys.executable,[sys.executable] + sys.argv)

    import unittest
    tests=unittest.TestLoader().discover('tests')#这里应该是指定测试包的名字把
    unittest.TextTestRunner(verbosity=2).run(tests)#verbosity有三个模式，0静默模式，1默认模式，2详细模式
    """verbosity=0,则不会显示具体测试内容，这里如果设置为0则显示：
    Ran 2 tests in 0.811s
    OK
    """
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@manager.command
def profile(length=25,profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app=ProfilerMiddleware(app.wsgi_app,restrictions=[length],profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    """RUn deployment tasks"""
    from flask_migrate import upgrade
    from app.models import Role,User,Comment
    upgrade()
    Role.insert_roles()
    Source.insert_source()
    PostType.insert_type()
    User.generate_fake(100)
    Post.generate_fake(500)
    Comment.generate_fake(1000)#添加1000个回复博文的评论
    Comment.generate_fake_reply(1000)#添加1000个回复别人的评论
    User.add_followed_self()

if __name__ == '__main__':
    manager.run()