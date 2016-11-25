from . import main
from flask import render_template

@main.errorhandler(404)
def error_notfound(e):
    return render_template('404.html'),404

@main.errorhandler(500)
def error_Internet(e):
    return render_template('500.html'),500
