from flask_wtf import Form
from ..models import User
from wtforms import ValidationError
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
#regexp第一个参数使用正则表达式确保输入字段只包含字母，数字，下划线和点号


class LoginForm(Form):
    email=StringField('邮箱用户',validators=[Required(),Email(),Length(1,64)])
    password=PasswordField('密码',validators=[Required()])
    remember_me=BooleanField('记住账号')
    submit=SubmitField('登录')


class RegistrationForm(Form):
    email=StringField('注册新用户/邮箱',validators=[Required(),Email(),Length(1,64)])
    username=StringField('用户名',validators=[Required(),Length(1,64),
                                           Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                  '用户名只能使用字母，数字，下划线和点号')])
    password=PasswordField('密码',validators=[Required(),EqualTo('password2','你两次输入的密码不同')])
    password2=PasswordField('请再次输入密码',validators=[Required()])
    submit=SubmitField('注册')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该账号已经被注册!')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已经被使用!')


class PasswordForm(Form):
    oldpassword=PasswordField('旧密码',validators=[Required()])
    newpassword=PasswordField('新密码',validators=[Required()])
    newpassword2=PasswordField('请再次输入',
                               validators=[Required(),
                               EqualTo('newpassword',message='你两次输入的密码不同')])
    submit=SubmitField('确认修改')#别把这个忘记了！

class FindForm(Form):
    email=StringField('请输入你要找回的账户邮箱',validators=[Required(),Email(),Length(1,64)])
    submit=SubmitField('发送邮件')

class ChongsheForm(Form):
    email=StringField('邮箱',validators=[Required(),Email(),Length(1,64)])
    new_password=PasswordField('新密码',validators=[Required()])
    new_password2=PasswordField('再次输入',validators=[Required(),EqualTo('new_password',message='你两次输入的密码不同')])
    submit=SubmitField('确认重设')

    def validators_email(self,firld):
        if User.query.filter_by(email=firld.data).first() is None:
            raise ValidationError('找不到用户名邮箱')


class NewemailForm(Form):
    email=StringField('新的邮箱地址',validators=[Required(),Email(),Length(1,64)])
    password=PasswordField('用户密码',validators=[Required()])
    submit=SubmitField('发送邮箱验证')

    def valitators_newemail(self,firld):
        if User.query.filter_by(email=firld.data).first():
            raise ValidationError('用户邮箱已存在')
