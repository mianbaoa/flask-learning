#这个文件可以直接从视图函数文件中导入程序form=NameForm()
from flask_wtf import Form
from wtforms import StringField, SubmitField,TextAreaField,BooleanField,SelectField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Required,Length,Email,Regexp
from wtforms import ValidationError
from ..models import Role,User


class NameForm(Form):
    name = StringField('你叫什么名字?', validators=[Required()])
    submit = SubmitField('确定')

class AddprofileForm(Form):#用户添加个人资料表单
    name=StringField('真实姓名',validators=[Length(0,64)])
    location=StringField('家庭地址',validators=[Length(0,64)])#这两个可以为空
    about_me=TextAreaField('自我介绍')
    submit=SubmitField('确定')

class EditProfileAdminForm(Form):
    email=StringField('用户邮箱',validators=[Required(),Length(1,64),Email()])
    username=StringField('用户名',validators=[Required(),Length(1,64),
                                           Regexp('^[a-zA-Z][a-zA-Z0-9._]*$',0,
                                                  '用户名只允许包含字母数字小点及下划线，且以字母开头')])
    confirmed=BooleanField('激活与否')#勾上即为Turn,否则为False
    role=SelectField('用户权限',coerce=int)#是以整数形式Role角色的id储存在数据库的 所以要把他转化为整数，这里是一个下拉菜单选择框
    name=StringField('用户真实姓名',validators=[Length(1,64)])
    location=StringField('用户地址',validators=[Length(1,64)])
    about_me=TextAreaField('用户个人信息')
    submit=SubmitField('确认修改当前用户的信息')

    def __init__(self,user,*args,**kwargs):#这个地方不是很懂,给类定义user参数，在视图函数中会用到form=EditProfileAdminForm(user=user)
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name)
                           for role in Role.query.order_by(Role.name).all()]#order_by是按查询条件对查询结果进行排列
        self.user=user

    def validate_email(self,field):
        if field.data!=self.user.email and \
                User.query.filter_by(email=field.data).first:#两个判断条件，先执行靠前的一个，按顺序执行，
            # 这里是表示如果用户email不是原来的email，管理员强行要换用户邮箱的话
            raise ValidationError('该邮箱已有用户使用')

    def validate_username(self,field):
        if field.data!=self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已经被使用')


class PostForm(Form):
    body=PageDownField('你在想些什么呢？',validators=[Required()])
    submit=SubmitField('确定')

class CommentForm(Form):
    body=PageDownField('添加评论',validators=[Required()])
    submit=SubmitField('确定')
