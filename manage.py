#!/usr/bin/env python3.5
import os
from app import create_app,db
from app.models import User,Role,Post
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app=create_app('default' or os.getenv('FLASK_CONFIG'))#getenv用来读取环境变量=environ.get差不多吧
manager=Manager(app)
migrate=Migrate(app,db)

def make_context_shell():
    return dict(User=User,Role=Role,Post=Post,db=db,app=app)
manager.add_command('shell',Shell(make_context=make_context_shell))
manager.add_command('db',MigrateCommand)


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests=unittest.TestLoader().discover('tests')#这里应该是指定测试包的名字把
    unittest.TextTestRunner(verbosity=2).run(tests)#verbosity有三个模式，0静默模式，1默认模式，2详细模式
    """verbosity=0,则不会显示具体测试内容，这里如果设置为0则显示：
    Ran 2 tests in 0.811s
    OK
    """
if __name__ == '__main__':
    manager.run()