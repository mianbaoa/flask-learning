from flask import render_template,redirect,request,url_for,flash
from . import auth
from .. import db
from .forms import LoginForm,RegistrationForm,PasswordForm,FindForm,ChongsheForm,NewemailForm
from ..models import User
from flask_login import login_user,logout_user,login_required
from ..emails import send_email
from flask_login import current_user
@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)#登录成功，在用户会话中把用户标记为已登录，
            # 第二个参数如果TURN,是记住用户,会在用户浏览器中写入一个长期有效的cookie，使用这个cookie可以复现用户会话
            return redirect(request.args.get('next') or url_for('main.index'))#重定向到登录成功的页面，参数next
        flash('输入的账号或者密码错误')#如果没有执行上面的if说明登录不成功，输入信息有错误

    return render_template('auth/login.html',form=form)

@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Accout','auth/email/confirm',user=user,token=token)
        flash('一个验证网址发送到了你的邮箱，请激活账号')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required#只有登录用户才能执行函数
def confirm(token):
    if current_user.confirmed:#先检查已登录的用户是否已经认证过，如果已认证执行if，下面的不用重复执行
        return redirect(url_for('main.index'))
    if current_user.confirm(token):#这里用户还没认证，，执行认证
        flash('认证成功，谢谢！')
    else:
        flash('认证链接是无效的或者过期的')
    return redirect(url_for('main.index'))

@auth.before_app_request#回调修饰器，可以在必要时拦截请求，拦截了登录请求，重定向到未认证的页面
# 这个修饰器是用来过滤未认证的用户的，当请求不是auth蓝本里的请求，而且用户登录了但是未认证
def before_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.'\
        and request.endpoint != 'static':#访问点endpoint应该就是跟url_for里的参数值一样吧
        return redirect(url_for('auth.unconfirmed'))


@auth.before_request#上面的before_app_request时全局请求钩子，这里是登录认证蓝本里的请求钩子
def updata_last_seen():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/newpassword',methods=['GET','POST'])
@login_required
def newpassword():
    form=PasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            current_user.password=form.newpassword.data
            db.session.add(current_user)
            flash('修改密码成功，请重新登录')
            return redirect(url_for('auth.login'))
        else:
            flash('你输入的密码不正确')

    return render_template('auth/newpassword.html',form=form)



@auth.route('/xiugai_email',methods=['GET','POST'])
@login_required
def xiugai_email():
    form=NewemailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email=form.email.data
            token=current_user.generate_newemail_token(new_email)
            send_email(new_email,'新邮箱验证','auth/email/change_email',user=current_user,
                       token=token,)
            flash('邮箱已发送,请验证你的新邮箱')
            return redirect(url_for('main.index'))
        flash('用户密码错误!')
    return render_template('auth/newemail.html',form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    #具体修改邮箱的方式是在User模块中进行,token里面解码出的是个字典，可以包含很多信息
    if current_user.change_email(token):
        flash('邮箱修改成功！')
    else:
        flash('邮箱修改失败！')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')#未认证用户的页面
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')#重新发送邮箱的路由
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'激活你的帐号','auth/email/confirm',
               user=current_user,token=token)
    flash('一封新的邮件已经发送到了你的邮箱，请查收')
    return redirect(url_for('main.index'))


@auth.route('/zhaohui',methods=['GET','POST'])
def zhaohui():
    form=FindForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token=user.generate_Reset_token()
            send_email(user.email,'找回密码','auth/email/findpassword',user=user,token=token,
                       next=request.args.get('next'))#next还是不懂什么意思
            flash('邮件已发送，请查收邮件')
            return redirect(url_for('auth.login'))
    return render_template('auth/findpassword.html',form=form)

@auth.route('/chongshe/<token>',methods=['GET','POST'])
def chongshe(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=ChongsheForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            if user.Reset(token,form.new_password.data):
                flash('重设密码成功，找回成功！现在可以登录了')
                return redirect(url_for('auth.login'))
            flash('重设失败')
            return redirect(url_for('main.index'))
        flash('找不到该用户名')
        return redirect(url_for('main.index'))
    return render_template('auth/findpassword.html',form=form)




@auth.route('/logout')
@login_required
def logout():
    logout_user()#会话登出
    flash('正在注销用户')
    return redirect(url_for('main.index'))