#设置了三个不同的子类，URI变量被指定了不同的值，这样程序就可在不同的配置环境中运行
import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to gruss string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='18435151481@163.com'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE=5
    FLASKY_FOLLOWERS_PER_PAGE=5

    @staticmethod#主要起作用的还是修饰器里的函数，
    def init_app(app):#配置类可以定义init_app()类方法，其参数是程序实例。在这个方法中，可以执行对当前环境的初始化
        pass
class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER='smtp.163.com'
    MAIL_PORT=25
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')


class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data_test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data.sqlite')

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig#这个是默认值
}
