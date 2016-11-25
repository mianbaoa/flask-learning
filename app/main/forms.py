#这个文件可以直接从视图函数文件中导入程序form=NameForm()
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('你叫什么名字?', validators=[Required()])
    submit = SubmitField('确定')