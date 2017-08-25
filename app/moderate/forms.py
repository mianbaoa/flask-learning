# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp
class AddPostType(Form):
    name = StringField('分类名称',validators=[Required()])
    submit = SubmitField('确定')