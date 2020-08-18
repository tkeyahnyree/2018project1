import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        if session.get("user"):
            return render_template('index.html', session=session["user"])
        return render_template('index.html')
    else:
        usr=request.form.get("usr")
        pwd=request.form.get("pwd")
        data=db.execute("Select * from users where username=:username and password=:password", {"username": usr, "password": pwd}).fetchall()

        if not data:
            return render_template("index.html", msg="Incorrect username and/or password. Please try again.")
        else:
            print(data)
            session["user"]=data[0][0]
            return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
        if request.method == "GET":
            if session.get("user"):
                return render_template('register.html')
        else:
            usr=request.form.get("usr")
            pwd=request.form.get("pwd")
            data=db.execute("Select * from users where username=username", {"username": usr}).fetchall()

            if not data:
                db.execute("Insert into users (username, password) Values(:username, :password)",{"username":usr, "password": pwd}).fetchall()
                session["user"]=data[0][0]
                return render_template("index.html", session=session['user'])
            else:
                return render_template("register.html", msg="username is unavailable")

@app.route("/lookup", methods=['GET', 'POST'])
def lookup():
        if request.method == "GET":
            return render_template('lookup.html')
        else:
            isbn=request.form.get("isbn")
            title=request.form.get("title")
            author=request.form.get("author")
            year=request.form.get("year")
            data=[]
            if isbn:
                isn=db.execute("Select * from books where isbn like :isbn",{"isbn":"%"+isbn+"%"})
                data.append(isn)
            if title:
                ttl=db.execute("Select * from books where title like :title",{"title":"%"+title+"%"})
                data.append(ttl)
            if author:
                ath=db.execute("Select * from books where author like :author",{"author":"%"+author+"%"})
                data.append(ath)
            if year:
                ath=db.execute("Select * from books where year like :year",{"year":"%"+year+"%"})
                data.append(ath)

            if not data:
                return render_template("lookup.html", msg="no results found")
            else:
                return render_template("lookup.html", dat=data)

@app.route("/review/<bid>", methods=['GET', 'POST'])
def review(bid):
        if request.method == "GET":
                return render_template('review.html', bid=bid)
        else:
            rat=request.form.get('rating')
            rev=request.form.get('review')
            uid=session["user"]

            revdata=db.execute("Select * from review where uid=:uid and bid=:bid",{"uid":uid, "bid":bid}).fetchall()
            if revdata:
                return render_template("review.html", msg="Review has been submitted already")
            else:
                db.execute("Insert into review (uid, bid, rating, review) values(:uid, :bid, :rating, :review)",{"uid":uid, "bid":bid, "rating":rat, "review":rev})
                db.commit()
                return render_template('review.html', msg=" Review sent")

@app.route("/info/<bid>", methods=['GET', 'POST'])
def info(bid):
    book=db.execute("Select * from books where id=:bid",{"bid":bid}).fetchall()
    revs=db.execute("Select * from books where id=:bid",{"bid":bid}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9FkGE7rOgx17E0xn9rCc0w", "isbns": "1416949658"})

    if res.status_code == 200:
        receive=res.json()
        avg=receive["books"][0]["average_rating"]
        cnt=receive["books"][0]["work_ratings_count"]
    if not revs:
        return render_template('info.html', book=book, msg="no reviews at this time", avg=avg, cnt=cnt)
    return render_template('info.html', book=book, revs=revs, avg=avg, cnt=cnt)

@app.route("/signout")
def signout():
    session.pop('user')
    return render_template('index.html', msg="you are now signed out")

@app.route("/api/<isbn>")
def api(isbn):
    isn=db.execute("Select * from books where isbn like :isbn",{"isbn":"%"+isbn+"%"}).fetchall()

    data={}
    data['title']=isn[0][2]
    data['year']=isn[0][4]
    data['author']=isn[0][3]
    data['isbn']=isbn
    data['review_count']=len(isn)
    bid=db.execute("Select id from books where isbn=:isbn",{"isbn":isbn}).fetchall()
    val=db.execute("Select avg(rating) from review where bid=:bid",{"bid":bid[0][0]}).fetchall()
    data['average_score']=val[0][0]
    return render_template('feedback.html', dat=data)
