from cs50 import SQL
from flask import Flask, render_template
from flask_session import Session
from helpers import login_required

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
    """Home page with user statistics"""
    from flask import session
    
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    
    # Get user's price report count
    price_report_count = db.execute(
        "SELECT COUNT(*) as count FROM price_reports WHERE user_id = ?",
        user_id
    )[0]['count']
    
    # Get user's quality report count
    quality_report_count = db.execute(
        "SELECT COUNT(*) as count FROM quality_reports WHERE user_id = ?",
        user_id
    )[0]['count']
    
    # If admin, get pending review counts
    pending_shops = 0
    pending_aliases = 0
    if user_type == 'admin':
        pending_shops = db.execute(
            "SELECT COUNT(*) as count FROM shop_proposals WHERE status = 'pending'"
        )[0]['count']
        pending_aliases = db.execute(
            "SELECT COUNT(*) as count FROM product_alias_proposals WHERE status = 'pending'"
        )[0]['count']
    
    return render_template("index.html", 
                         price_report_count=price_report_count,
                         quality_report_count=quality_report_count,
                         pending_shops=pending_shops,
                         pending_aliases=pending_aliases)


# Register blueprints
from routes import register_blueprints
register_blueprints(app)