from . import db,login_manager
from flask_login import UserMixin,AnonymousUserMixin#程序不用先检查用户是否登录，就能调用current_user.can()
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer#生成确认令牌
from flask import current_app,request,url_for#程序上下文
from markdown import markdown
import bleach
from datetime import datetime
import hashlib  #md5散列值
from app.exceptions import ValidationError


class Permission:#定义权限常量
    FOLLOW=0x01#关注其他用户
    COMMENT=0x02#在他人撰写的文章中发表评论
    WRITE_ARTICLES=0x04#发表文章
    MODERATE_COMMENTS=0x08#查处他人发表的不当评论
    ADMINISTER=0x80#0b10000000 管理网站，管理员
    """
    只用到了5位，其他三位将来可以扩展
    创建insert_roles定义角色
    匿  名 0x00 只有阅读权限
    用  户 0x07 发表文章，关注他人，评论
    协管员 0x0f 在用户的基础上增加审查不当评论的权限
    管理员 0xff 具有所有权限
    """

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)#权限
    users=db.relationship('User',backref='role',lazy='dynamic')

    @staticmethod#staticmethod将class中的方法变成静态方法，可以当做普通方法一样调用 ，而不会将类实例本身作为第一个self参数传给方法
    def insert_roles():#这个函数并不直接创建新角色对象，而是通过角色名查找现有的角色，然后再进行更新,记住每次更新数据库都要在命令行写入角色
        roles={
            'User':(Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                         Permission.COMMENT |
                         Permission.WRITE_ARTICLES |
                         Permission.MODERATE_COMMENTS, False),
            'Administrator':(0xff, False)
        }
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            #在Role里创建三个角色，只有数据库里没有某个角色名时才会创建新角色对象，方便以后执行更新角色列表操作
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()



    def __repr__(self):
        return '<Role %r>'%self.name


class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user=AnonymousUser


class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    tit = db.Column(db.String(64))#这里好像不能使用unique参数 不知道为什么
    num_of_view=db.Column(db.Integer,default=0)
    disable=db.Column(db.Boolean,default=False)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    comments=db.relationship('Comment',backref='post',lazy='dynamic')

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post',id=self.id,_external=True),
            'body': self.body,
            'body_html':self.body_html,
            'timestamp':self.timestamp,
            'author':url_for('api.get_users',id=self.author_id,_external=True),
            'comments':url_for('api.get_post_comments',id=self.id,_external=True),
            'comment_count':self.comments.count()

        }
        return json_post

    @staticmethod
    def add_view(post,db):
        post.num_of_view=post.num_of_view+1
        db.session.add(post)
        db.session.commit()

    @staticmethod#这个修饰器非常有用，可以在命令行单独启用他，让他生成数据库的很多虚拟用户
    def generate_fake(count=100):#创建虚拟的博文。。
        from random import seed,randint
        import forgery_py

        seed()
        user_count=User.query.count()#查找有多少数量用户,p54
        for i in range(count):
            u=User.query.offset(randint(0,user_count-1)).first()#P53,偏移原查询返回的结果，查询一个新的，意思就是每个用户都能赋值给u
            p=Post(tit=forgery_py.lorem_ipsum.title(randint(3, 5)),
                   body=forgery_py.lorem_ipsum.sentences(randint(15, 35)),#每个用户写一到二个文章
                   timestamp=forgery_py.date.date(True),
                   num_of_view=randint(100, 15000),author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('没有内容的博文！')
        return Post(body=body)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul'
                , 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags,
                                                           strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)


class Follow(db.Model):
    __tablename__='follows'
    followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled=db.Column(db.Boolean)#默认为空，即为False,该评论没有被禁用
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                        'em', 'i','strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags,
                                                       strip=True))

    def to_json(self):
        json_comment={
            'url':url_for('api.get_comments',id=self.id,_external=True),
            'body':self.body,
            'body_html':self.body_html,
            'timestamp':self.timestamp,
            'author':url_for('api.get_users',id=self.author_id,_external=True),
            'post':url_for('api.get_posts',id=self.post_id,_external=True)
        }

        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('没有内容的评论！')
        return Comment(body=body)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        Post_count = Post.query.count()
        User_count = User.query.count()
        for i in range(count):
            a = Post.query.offset(randint(0, Post_count - 1)).first()
            b = User.query.offset(randint(0, User_count - 1)).first()
            c = Comment(body=forgery_py.lorem_ipsum.sentences(randint(3, 5)),
                        timestamp=forgery_py.date.date(True),
                        author=b,
                        post=a)
            db.session.add(c)
        try:
            db.session.commit()
        except:
            db.session.rollback()

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

class User(UserMixin,db.Model):#UserMixin类，其中包括P82四种方法的默认实现,为了使用Flask-Login，必须实现这四个方法
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)#Integer默认32位
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),index=True)
    password_hash = db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)#默认设置为False当这个值为True时，验证通过
    gravatar_hash=db.Column(db.String(32))
    posts=db.relationship('Post',backref='author',lazy='dynamic')
    followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],#为了消除外键间的歧义，必须指定外键
                              backref=db.backref('followed',lazy='joined'),
                              lazy='dynamic',cascade='all,delete-orphan')#这里后面四个参数都是面对第一个参数Follow
    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],
                             backref=db.backref('follower',lazy='joined'),
                             lazy='dynamic',cascade='all,delete-orphan')


    name=db.Column(db.String(64))
    location=db.Column(db.String(64))
    about_me=db.Column(db.Text())#Text与String的区别在于Test没有限制长度
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)#datetime.utcnow这里没有()，作为默认值函数
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)

    comments=db.relationship('Comment',backref='author',lazy='dynamic')#lazy参数设置为dynamic，返回的查询对象

    def to_json(self):
        json_user={
            'url':url_for('api.get_user',id=self.id,_external=True),
            'username':self.username,
            'member_since':self.member_since,
            'last_since':self.last_seen,
            'posts':url_for('api.get_user_posts',id=self.id,_external=True),
            'comments':url_for('api.get_user_comments',id=self.id,_external=True),
            'followed_posts':url_for('api.get_user_followed_posts',id=self.id,_external=True),
            'post_count':self.posts.count()
        }
        return json_user


#<<<-----创建四个关于关注者与被关注者的方法跟一个索引属性：self所关注人的博文----->>>
    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)

    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property#把followed_posts方法变为属性，在models中加入方法不用更新数据库，添加一行新字段时需要更新数据库
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)
        #这里不难理解，先在Follow表中过滤出self用户(self.id)对应的关注了的人的id，返回到Post然后再根据这些id在Post找作者为被关注者的博文
#<<<-----创建随机用户----->>>


    @staticmethod#添加一个在命令行执行的方法,这个方法可以使数据库的每个用户都关注自己,从而可以在首页关注者里看到自己的博文
    def add_followed_self():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


    @staticmethod
    def generate_fake(count=100):#创建100个随机的用户
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u=User(email=forgery_py.internet.email_address(),
                   username=forgery_py.internet.user_name(True),
                   password=forgery_py.lorem_ipsum.word(),
                   confirmed=True,
                   name=forgery_py.name.full_name(),
                   location=forgery_py.address.city(),
                   about_me=forgery_py.lorem_ipsum.sentence(),
                   member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:    #判断请求是否为https
            url='https://secure.gravatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'
        hash=self.gravatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()#先执行or前面的，若self没有gravatar_hash散列值再生成散列值
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,
                                                                     rating=rating)#d参数为头像生成器，有很多选择 参考p110
        #这里返回一个完整的url地址


    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)

    def __init__(self,**kwargs):#这个函数表示创建基类对象，应该就是表示注册完了之后赋予用户的属性
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()#管理员注册之后自动赋予管理员角色
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()#用户注册完之后自动赋予用户User角色
        if self.email is not None and self.gravatar_hash is None:
            self.gravatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()#用户注册完之后自动赋予用户头像散列值
        self.follow(self)#用户创建时就是在数据库里关注自己的

    #<<<-----定义判断是否为管理员的函数----->>>
    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    #<<<-----结束----->>>

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

    def generate_newemail_token(self,new_email, expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.gravatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True



    @property#这个修饰器是让password方法定义为属性,即self.password被调用时会返回一个自定义错误
    def password(self):
        raise AttributeError('password is not a readable attribute')


    @password.setter#这里的修饰器是让password的参数用等号赋值，u.password=‘’而不能用u.password('')，去掉修饰器就可以用常规的赋值了
    def password(self,password):#User的一个属性password
        self.password_hash=generate_password_hash(password)


    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_auth_token(self,expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id':self.id}).decode('ascii')#这里要加上ascii

    @staticmethod
    def verify_auth_token(token):#这个函数返回该id用户本身或者None
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data =s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


    def __repr__(self):
        return '<User %r>'%self.username



@login_manager.user_loader#加载用户的回调函数接受以Unicode字符串形式的用户标识符，如果能找到用户，必须返回用户对象
def load_user(user_id):
    return User.query.get(int(user_id))