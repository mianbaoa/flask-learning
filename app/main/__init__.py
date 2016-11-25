from flask import Blueprint

main=Blueprint('main',__name__)

from . import views,errors#这些模块在__init__.py脚本的末尾导入，这是为了避免循环导入依赖，
# 因为在views.py和errors.py中还要导入main