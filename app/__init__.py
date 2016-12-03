from flask import Flask,render_template
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config#top-level package可以直接引用，不需要加上相对路径‘..’

bootstrap=Bootstrap()
mail=Mail()#这里是在其他函数文件里面要用到这些模块
db=SQLAlchemy()
moment=Moment()
pagedown=PageDown()
login_manager=LoginManager()
login_manager.session_protection='strong'#加强会话保护，设为strong时，flask-login记下ip和浏览器代理信息，
# 如果发生异动就登出用户
login_manager.login_view='auth.login'#设置登录页面的端点，这里应该是输入端点名（蓝本中视图函数的名字）

def create_app(config_name):#程序工厂函数，连接蓝本，创建实例，给实例提供配置，对实例进行初始化
    app=Flask(__name__)
    app.config.from_object(config[config_name])#这里的from_object是Flask提供的，可以直接把配置文件导入程序
    mail.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint#蓝本在工厂函数create_app()中注册到程序上
    app.register_blueprint(main_blueprint)#使用Flask提供的register_blueprint

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')#注册蓝本使用url_prefix参数后，
    # 蓝本中所有路由都会加上指定的前缀'/auth'

    return app