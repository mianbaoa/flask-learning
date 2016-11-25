#创建视图文件很麻烦，仔细看看。
from flask import render_template
from datetime import datetime
from . import main
@main.route('/',methods=['GET','POST'])
def index():

    return render_template('index.html',
                           current_time=datetime.utcnow())
