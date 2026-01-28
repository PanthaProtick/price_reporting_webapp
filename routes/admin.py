from flask import Blueprint, redirect, render_template, request, session
from helpers import apology, login_required, is_admin
from cs50 import SQL

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Database connection
db = SQL("sqlite:///app.db")


@admin_bp.route("/review/shops")
@login_required
def review_shops():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)
    
    proposals = db.execute("SELECT * FROM shop_proposals WHERE status = 'pending'")
    return render_template("review_shops.html", proposals=proposals)


@admin_bp.route("/review/shops/approve", methods=["POST"])
@login_required
def review_shops_approve():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)

    proposal_id = request.form.get("id")
    if not proposal_id:
        return apology("Missing proposal id", 400)

    try:
        # ensure proposal exists and is pending
        p = db.execute("SELECT * FROM shop_proposals WHERE id = ? AND status = 'pending'", proposal_id)
    except Exception:
        return apology("Database error", 500)

    if not p:
        return apology("Proposal not found or already reviewed", 404)

    prop = p[0]
    try:
        db.execute(
            "INSERT INTO shops (name, address, latitude, longitude) VALUES (?, ?, ?, ?)",
            prop['proposed_name'],
            prop['proposed_address'],
            prop['latitude'],
            prop['longitude'],
        )

        db.execute(
            "UPDATE shop_proposals SET status = 'approved', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            session.get("user_id"),
            proposal_id,
        )
    except Exception:
        return apology("Failed to approve proposal", 500)

    return redirect("/admin/review/shops")


@admin_bp.route("/review/shops/reject", methods=["POST"])
@login_required
def review_shops_reject():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)

    proposal_id = request.form.get("id")
    if not proposal_id:
        return apology("Missing proposal id", 400)

    try:
        db.execute(
            "UPDATE shop_proposals SET status = 'rejected', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            session.get("user_id"),
            proposal_id,
        )
    except Exception:
        return apology("Failed to reject proposal", 500)

    return redirect("/admin/review/shops")


@admin_bp.route("/review/product_aliases")
@login_required
def review_product_aliases():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)

    # join product details for display
    try:
        proposals = db.execute(
            "SELECT pap.id, pap.product_id, pap.proposed_alias, pap.proposed_by, p.canonical_name "
            "FROM product_alias_proposals pap JOIN products p ON p.id = pap.product_id "
            "WHERE pap.status = 'pending'"
        )
    except Exception:
        return apology("Database error", 500)

    return render_template("review_product_aliases.html", proposals=proposals)


@admin_bp.route("/review/product_aliases/approve", methods=["POST"])
@login_required
def review_product_aliases_approve():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)

    proposal_id = request.form.get("id")
    if not proposal_id:
        return apology("Missing proposal id", 400)

    try:
        p = db.execute("SELECT * FROM product_alias_proposals WHERE id = ? AND status = 'pending'", proposal_id)
    except Exception:
        return apology("Database error", 500)

    if not p:
        return apology("Proposal not found or already reviewed", 404)

    prop = p[0]
    try:
        db.execute(
            "INSERT INTO product_aliases (product_id, alias_name) VALUES (?, ?)",
            prop['product_id'],
            prop['proposed_alias'],
        )

        db.execute(
            "UPDATE product_alias_proposals SET status = 'approved', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            session.get("user_id"),
            proposal_id,
        )
    except Exception:
        return apology("Failed to approve proposal", 500)

    return redirect("/admin/review/product_aliases")


@admin_bp.route("/review/product_aliases/reject", methods=["POST"])
@login_required
def review_product_aliases_reject():
    try:
        row = db.execute("SELECT user_type FROM users WHERE id = ?", session.get("user_id"))
    except Exception:
        return apology("Database error", 500)
    if len(row) != 1 or not is_admin(row[0]):
        return apology("Access denied", 403)

    proposal_id = request.form.get("id")
    if not proposal_id:
        return apology("Missing proposal id", 400)

    try:
        db.execute(
            "UPDATE product_alias_proposals SET status = 'rejected', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
            session.get("user_id"),
            proposal_id,
        )
    except Exception:
        return apology("Failed to reject proposal", 500)

    return redirect("/admin/review/product_aliases")
