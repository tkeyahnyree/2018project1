from flask import Flask, session, render_template, request, url_for
from flask_mysqldb import MySQL
import pymysql
from datetime import timedelta

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
global COOKIE_TIME_OUT
#COOKIE_TIME_OUT = 60*60*24*7 #7 days
COOKIE_TIME_OUT = 60*5 #5 minutes
#db config
mysql = MySQL()

#mysql config
app.config['MYSQL_DATABASE_USER'] = 'pojjdqksnwytgl'
app.config['MYSQL_DATABASE_DB'] = 'darirtpmg37nkh'
app.config['MYSQL_DATABASE_PASSWORD'] = '1219bb2855217392d028d369dea787f7ef35062326a0d6ee981ae50e04d7fc33'
app.config['MYSQL_DATABASE_HOST'] = 'ec2-34-194-198-176.compute-1.amazonaws.com'
mysql.init_app(app)

@app.route('/')
def index():
    if 'email' in session:
        username = session['email']
        return 'Logged in as ' +username+ '<br>' + "<b><a href = '/logout'>Click here to logout</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + "click here to login</b></a>"

@app.route('/login')
def login():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
