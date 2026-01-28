from flask import Blueprint, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, is_valid_email
from cs50 import SQL

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Database connection
db = SQL("sqlite:///app.db")


@auth_bp.route("/login", methods=["GET", "POST"])
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["passhash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must provide username", 400)
        if not email:
            return apology("Must provide email", 400)
        elif not is_valid_email(email):
            return apology("Invalid email format", 400)
        if not password:
            return apology("Must provide password", 400)
        if not confirmation:
            return apology("Must confirm password", 400)

        if password != confirmation:
            return apology("Passwords do not match", 400)

        # check username/email uniqueness
        if db.execute("SELECT id FROM users WHERE username = ?", username):
            return apology("Username already exists", 400)
        if db.execute("SELECT id FROM users WHERE email = ?", email):
            return apology("Email already registered", 400)

        try:
            db.execute(
                "INSERT INTO users (username, email, passhash, user_type) VALUES(?,?,?,?)",
                username,
                email,
                generate_password_hash(password),
                'user'
            )
        except Exception:
            return apology("Registration failed", 400)

        return redirect("/login")
    else:
        return render_template("register.html")
