#设置了三个不同的子类，URI变量被指定了不同的值，这样程序就可在不同的配置环境中运行
import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to gruss string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True#每次请求结束后都会自动提交数据库的变动
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='18435151481@163.com'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE=5
    FLASKY_FOLLOWERS_PER_PAGE=5
    FLASKY_COMMENTS_PER_PAGE=5
    FLASKY_SLOW_DB_QUERY_TIME=0.5
    SQLALCHEMY_RECORD_QUERIES=True#告诉SQLALchemy启用记录查询统计数字的功能


    @staticmethod#主要起作用的还是修饰器里的函数，
    def init_app(app):#配置类可以定义init_app()类方法，其参数是程序实例。在这个方法中，可以执行对当前环境的初始化
        pass
class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER='smtp.163.com'
    MAIL_PORT=25
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME') or '18435151481@163.com'
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD') or 'zhang6291652'
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')
    WHOOSH_BASE = os.path.join(basedir,'data-dev.sqlite')

    """为了账号的安全性，一般账号密码是不会写在代码中，在这里是为了学习需要，交流需要。"""


class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data_test.sqlite')
    WTF_CSRF_ENABLED=False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI=\
    'sqlite:///'+os.path.join(basedir,'data.sqlite')

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig#这个是默认值
}
