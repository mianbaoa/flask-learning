# -*- coding:utf-8 -*-
from flask import Blueprint

main=Blueprint('main',__name__)

from . import views,errors#这些模块在__init__.py脚本的末尾导入，这是为了避免循环导入依赖，
# 因为在views.py和errors.py中还要导入main
#把Permission类加入到模板上下文
from ..models import Permission
@main.app_context_processor
def inject_permisssion():
    return dict(Permission=Permission)
