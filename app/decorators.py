# -*- coding:utf-8 -*-
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission
def permission_required(permission):#修饰器中使用参数，运用到了函数的嵌套
    def decorator(f):#定义这个函数应该是引入函数f变量
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

