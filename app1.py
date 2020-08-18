from flask import Flask, session, render_template, request, redirect, g, url_for, flash
import psycopg2
import os

app=Flask(__name__)

app.secret_key=os.urandom(24)

conn=psycopg2.connect(host="ec2-34-194-198-176.compute-1.amazonaws.com",user="pojjdqksnwytgl",password="1219bb2855217392d028d369dea787f7ef35062326a0d6ee981ae50e04d7fc33",database="darirtpmg37nkh",port=5432)
cursor=conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['password'] == 'password':
            session['user'] = request.form['username']
            return redirect(url_for('homepage'))

    return render_template('index.html')

@app.route('/homepage')
def homepage():
    if g.user:
        return render_template('homepage.html', user=session['user'])
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']

@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return render_template('index.html')


if __name__=="__main__":
    app.run(debug=True)
