from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, score_apparel, score_electronics, score_food, score_pharma, is_valid_email, is_admin

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///app.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Home page"""
    return render_template("index.html")


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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
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
        rows = db.execute("SELECT id FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("Username already exists", 400)
        rows = db.execute("SELECT id FROM users WHERE email = ?", email)
        if len(rows) > 0:
            return apology("Email already registered", 400)

        passhash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, email, passhash, user_type) VALUES(?,?,?,?)", username, email, passhash, 'user')
        except Exception:
            return apology("Registration failed", 400)

        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/create/price_report", methods=["GET", "POST"])
@login_required
def create_price_report():
    if request.method == "POST":
        # process form submission
        pass

    else:
        pass
    return

@app.route("/create/shop", methods=["GET", "POST"])
@login_required
def create_shop():
    if request.method == "POST":
        # process form submission
        name = request.form.get('name')
        address = request.form.get('address')
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')

        if not name:
            return apology("Must provide shop name", 400)
        if not address:
            return apology("Must provide shop address", 400)
        if not lat or not lon:
            return apology("Location required", 400)

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except ValueError:
            return apology("Invalid latitude/longitude", 400)

        try:
            db.execute(
                "INSERT INTO shop_proposals (proposed_name, proposed_address, latitude, longitude, proposed_by) VALUES (?, ?, ?, ?, ?)",
                name,
                address,
                lat_f,
                lon_f,
                session.get("user_id"),
            )
        except Exception:
            return apology("Failed to create shop (database error)", 500)

        return redirect("/")

    else:
        return render_template("create_shop.html")

@app.route("/create/product_alias", methods=["GET", "POST"])
@login_required
def create_product_alias():
    if request.method == "POST":
        # process form submission
        pass

    else:
        pass
    return