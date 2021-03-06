# -*- coding:utf-8 -*-
from . import mail
from flask_mail import Message
from flask import render_template,current_app
from threading import Thread

def send_yibu_email(app,msg):
    with app.app_context():
        mail.send(msg)
def send_email(to,subject,template,**kwargs):
    app=current_app._get_current_object()#这里不是很懂,现在懂了程序上下文，是指在当前的程序实例中进行
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+' '+subject,
                sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_yibu_email,args=[app,msg])
    thr.start()
    return thr