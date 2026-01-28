from flask import Blueprint, flash, redirect, render_template, request, session
from helpers import apology, login_required
from cs50 import SQL

# Create blueprint
user_bp = Blueprint('user', __name__)

# Database connection
db = SQL("sqlite:///app.db")


@user_bp.route("/create/shop", methods=["GET", "POST"])
@login_required
def create_shop():
    if request.method == "POST":
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
            latitude = float(lat)
            longitude = float(lon)
        except (ValueError, TypeError):
            return apology("Invalid latitude/longitude", 400)

        try:
            db.execute(
                "INSERT INTO shop_proposals (proposed_name, proposed_address, latitude, longitude, proposed_by) VALUES (?, ?, ?, ?, ?)",
                name,
                address,
                latitude,
                longitude,
                session.get("user_id"),
            )
        except Exception:
            return apology("Failed to create shop (database error)", 500)

        return redirect("/")

    else:
        return render_template("create_shop.html")


@user_bp.route("/create/product_alias", methods=["GET", "POST"])
@login_required
def create_product_alias():
    if request.method == "POST":
        product_id_str = request.form.get('product_id')
        alias_name = request.form.get('alias_name')

        if not product_id_str:
            return apology("Must select a canonical product", 400)
        if not alias_name:
            return apology("Must provide alias name", 400)

        try:
            product_id = int(product_id_str)
        except (ValueError, TypeError):
            return apology("Invalid product id", 400)

        try:
            db.execute(
                "INSERT INTO product_alias_proposals (product_id, proposed_alias, proposed_by) VALUES (?, ?, ?)",
                product_id,
                alias_name,
                session.get("user_id"),
            )
        except Exception:
            return apology("Failed to create product alias (database error)", 500)

        return redirect("/")

    else:
        # provide list of canonical products for selection
        try:
            products = db.execute("SELECT id, canonical_name, category FROM products ORDER BY canonical_name")
        except Exception:
            return apology("Failed to load products", 500)

        return render_template("create_product_alias.html", products=products)


@user_bp.route("/create/price_report", methods=["GET", "POST"])
@login_required
def create_price_report():
    if request.method == "POST":
        shop_id_str = request.form.get('shop_id')
        product_alias_id_str = request.form.get('product_alias_id')
        price_paid_str = request.form.get('price_paid')
        quantity_str = request.form.get('quantity', '1')

        if not shop_id_str:
            return apology("Must select a shop", 400)
        if not product_alias_id_str:
            return apology("Must select a product", 400)
        if not price_paid_str:
            return apology("Must provide price paid", 400)

        try:
            shop_id = int(shop_id_str)
            product_alias_id = int(product_alias_id_str)
            price_paid = float(price_paid_str)
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            return apology("Invalid input data", 400)

        if price_paid <= 0:
            return apology("Price must be positive", 400)
        if quantity <= 0:
            return apology("Quantity must be positive", 400)

        try:
            db.execute(
                "INSERT INTO price_reports (user_id, shop_id, product_alias_id, price_paid, quantity) VALUES (?, ?, ?, ?, ?)",
                session.get("user_id"),
                shop_id,
                product_alias_id,
                price_paid,
                quantity,
            )
        except Exception:
            return apology("Failed to create price report (database error)", 500)

        flash("Price report submitted successfully!")
        return redirect("/")

    else:
        try:
            shops = db.execute("SELECT id, name, address FROM shops ORDER BY name")
            product_aliases = db.execute(
                "SELECT pa.id, pa.alias_name, p.canonical_name, p.category "
                "FROM product_aliases pa JOIN products p ON pa.product_id = p.id "
                "ORDER BY p.canonical_name, pa.alias_name"
            )
        except Exception:
            return apology("Failed to load data", 500)

        return render_template("create_price_reports.html", shops=shops, product_aliases=product_aliases)


@user_bp.route("/user/price_reports")
@login_required
def user_price_reports():
    try:
        price_reports = db.execute(
            "SELECT pr.id, s.name AS shop_name, pa.alias_name, p.canonical_name, p.category, pr.price_paid, pr.quantity "
            "FROM price_reports pr "
            "JOIN shops s ON pr.shop_id = s.id "
            "JOIN product_aliases pa ON pr.product_alias_id = pa.id "
            "JOIN products p ON pa.product_id = p.id "
            "WHERE pr.user_id = ? "
            "ORDER BY pr.reported_at DESC",
            session.get("user_id")
        )
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to load price reports", 500)

    return render_template("user_price_reports.html", price_reports=price_reports)
