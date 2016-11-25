from . import db,login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer#生成确认令牌
from flask import current_app#程序上下文


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True,index=True)
    users=db.relationship('User',backref='role',lazy='dynamic')
    def __repr__(self):
        return '<Role %r>'%self.name


class User(UserMixin,db.Model):#UserMixin类，其中包括P82四种方法的默认实现,为了使用Flask-Login，必须实现这四个方法
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)#默认设置为False当这个值为True时，验证通过

    def generate_confirmation_token(self,expiration=3600):#这个方法生成一个令牌,默认值是3600秒
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):#这个方法是用来验证令牌的
        s = Serializer(current_app.config['SECRET_KEY'])#构建编解安全令牌函数s
        try:
            data = s.loads(token)#解码
        except:
            return False #如果token不能解码成数字，则返回FALSE，验证不通过
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True


    def generate_Reset_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})

    def Reset(self,token,new_password):#创建判断函数
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('reset')!=self.id:
            return False
        self.password=new_password
        db.session.add(self)
        return True



    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')


    @password.setter#这里的修饰器是让password的参数用等号赋值，u.password=‘’而不能用u.password('')，去掉修饰器就可以用常规的赋值了
    def password(self,password):#User的一个属性password
        self.password_hash=generate_password_hash(password)


    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)


    def __repr__(self):
        return '<User %r>'%self.username



@login_manager.user_loader#加载用户的回调函数接受以Unicode字符串形式的用户标识符，如果能找到用户，必须返回用户对象
def load_user(user_id):
    return User.query.get(int(user_id))