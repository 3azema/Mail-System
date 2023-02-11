import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def inbox():
    """Show all email received"""
    user_id = session["user_id"]
    emails = db.execute("SELECT * FROM emails WHERE recipient_id = ?", user_id)
    return render_template("inbox.html", emails=emails)


@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    """Write an emalil to someone"""
    if request.method == "GET":
        return render_template("compose.html")
    else:
        user_id = session["user_id"]
        sender_db = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        sender_real = sender_db[0]["username"]
        recipient = request.form.get("recipient")
        subject = request.form.get("subject")
        body = request.form.get("body")
        sender_id = user_id
        recipient_id = db.execute("SELECT id FROM users WHERE username = ?", recipient)
        recipient_id_real = recipient_id[0]["id"]
        try:
            user = db.execute("SELECT username FROM users WHERE username LIKE  ?  ", recipient)
            user_real = user[0]["username"]
        except:
            return apology("This Recipient Does Not Exist")
        
        if not subject: 
            return apology("Please Enter Subject")
        if not body:
            return apology("Please Enter Body")
        
        db.execute("INSERT INTO emails (sender, recipient, subject, body, sender_id, recipient_id) VALUES (?, ?, ?, ?, ?, ?)",sender_real, user_real, subject, body, sender_id, recipient_id_real)
        
        flash("Email Have Been Sent!")
        
        return redirect("/sent")

@app.route("/sent")
@login_required
def sent():
    """Show history of transactions"""
    user_id = session["user_id"]
    email = db.execute("SELECT * FROM emails WHERE sender_id = ?", user_id)
    return render_template("sent.html", email=email)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/email", methods=["POST"])
@login_required
def email():
    """View email details"""
    emailId = request.form.get("emailId")
    emailDetailDB = db.execute("SELECT * FROM emails WHERE id = ?", emailId)
    emailDetail = emailDetailDB[0]
    return render_template("email.html", emailDetail=emailDetail)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not email:
            return apology("Pleas enter an email")
        if not username:
            return apology("Pleas enter an username")
        if not password:
            return apology("Pleas enter an password")
        if not confirmation:
            return apology("Pleas enter a confirmation")
        if confirmation != password:
            return apology("Confirmation does not match")
        
        try:
            new_user = db.execute("INSERT INTO users (email, username, hash) VALUES (?, ?, ?)", email, username, generate_password_hash(password))
        except:
            return apology("Sorry This Username Is Already Exists")
        
        session["user_id"] = new_user
        return redirect("/login")
    
    
@app.route("/reply", methods=["POST"])
@login_required
def reply():
    return apology("TODO")
