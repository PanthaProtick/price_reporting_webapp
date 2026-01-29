from flask import Blueprint, flash, redirect, render_template, request, session
from helpers import apology, login_required, score_electronics, score_pharma, score_food, score_apparel
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

        return render_template("create_price_report.html", shops=shops, product_aliases=product_aliases)


@user_bp.route("/user/price_reports")
@login_required
def user_price_reports():
    try:
        price_reports = db.execute(
            "SELECT pr.id, s.name AS shop_name, pa.alias_name, p.canonical_name, p.category, pr.price_paid, pr.quantity, "
            "qr.id AS quality_report_id "
            "FROM price_reports pr "
            "JOIN shops s ON pr.shop_id = s.id "
            "JOIN product_aliases pa ON pr.product_alias_id = pa.id "
            "JOIN products p ON pa.product_id = p.id "
            "LEFT JOIN quality_reports qr ON qr.price_report_id = pr.id "
            "WHERE pr.user_id = ? "
            "ORDER BY pr.reported_at DESC",
            session.get("user_id")
        )
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to load price reports", 500)

    return render_template("user_price_reports.html", price_reports=price_reports)

@user_bp.route("/create/quality_report/<int:price_report_id>", methods=["GET", "POST"])
@login_required
def create_quality_report(price_report_id):
    # Verify price report exists and belongs to current user
    try:
        pr = db.execute(
            "SELECT pr.id, pr.user_id, p.category "
            "FROM price_reports pr "
            "JOIN product_aliases pa ON pr.product_alias_id = pa.id "
            "JOIN products p ON pa.product_id = p.id "
            "WHERE pr.id = ?",
            price_report_id
        )
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Database error", 500)

    if not pr:
        return apology("Price report not found", 404)
    
    if pr[0]['user_id'] != session.get("user_id"):
        return apology("Access denied", 403)

    # Check if quality report already exists
    try:
        existing_qr = db.execute(
            "SELECT id FROM quality_reports WHERE price_report_id = ?",
            price_report_id
        )
    except Exception as e:
        print(f"Database error checking existing quality report: {e}")
        return apology("Database error", 500)
    
    category = pr[0]['category']
    is_update = len(existing_qr) > 0

    if request.method == "POST":
        # Process form based on category
        if category == 'electronics':
            return process_electronics_quality(price_report_id, category, is_update)
        elif category == 'pharma':
            return process_pharma_quality(price_report_id, category, is_update)
        elif category == 'food':
            return process_food_quality(price_report_id, category, is_update)
        elif category == 'apparel':
            return process_apparel_quality(price_report_id, category, is_update)
        else:
            return apology("Invalid category", 400)
    
    else:
        # Load existing data if updating
        existing_data = None
        if is_update:
            existing_data = get_existing_quality_data(price_report_id, category)
        
        return render_template("create_quality_report.html", 
                             price_report_id=price_report_id, 
                             category=category,
                             is_update=is_update,
                             existing_data=existing_data)


def get_existing_quality_data(price_report_id, category):
    """Fetch existing quality report data based on category"""
    try:
        qr = db.execute(
            "SELECT * FROM quality_reports WHERE price_report_id = ?",
            price_report_id
        )
        if not qr:
            return None
        
        quality_report_id = qr[0]['id']
        
        if category == 'electronics':
            data = db.execute(
                "SELECT * FROM electronics_quality_reports WHERE quality_report_id = ?",
                quality_report_id
            )
        elif category == 'pharma':
            data = db.execute(
                "SELECT * FROM pharma_quality_reports WHERE quality_report_id = ?",
                quality_report_id
            )
        elif category == 'food':
            data = db.execute(
                "SELECT * FROM food_quality_reports WHERE quality_report_id = ?",
                quality_report_id
            )
        elif category == 'apparel':
            data = db.execute(
                "SELECT * FROM apparel_quality_reports WHERE quality_report_id = ?",
                quality_report_id
            )
        else:
            return None
        
        if data:
            return {**qr[0], **data[0]}
        return qr[0]
    except Exception as e:
        print(f"Error fetching existing quality data: {e}")
        return None


def process_electronics_quality(price_report_id, category, is_update=False):
    """Process electronics quality report"""
    device_functional = request.form.get('device_functional')
    authenticity_confidence = request.form.get('authenticity_confidence')
    condition_match = request.form.get('condition_match')
    warranty_honored = request.form.get('warranty_honored')
    accessories_complete = request.form.get('accessories_complete')
    reported_issue = request.form.get('reported_issue', '')

    if not all([device_functional, authenticity_confidence, condition_match, accessories_complete]):
        return apology("All required fields must be filled", 400)

    try:
        data = {
            'device_functional': int(device_functional),
            'authenticity_confidence': int(authenticity_confidence),
            'condition_match': int(condition_match),
            'warranty_honored': int(warranty_honored) if warranty_honored else None,
            'accessories_complete': int(accessories_complete),
            'reported_issue': reported_issue
        }
    except (ValueError, TypeError):
        return apology("Invalid input data", 400)

    # Calculate quality score
    quality_score = score_electronics(data)

    try:
        if is_update:
            # Get existing quality report id
            qr = db.execute(
                "SELECT id FROM quality_reports WHERE price_report_id = ?",
                price_report_id
            )
            quality_report_id = qr[0]['id']
            
            # Update electronics_quality_reports
            db.execute(
                "UPDATE electronics_quality_reports SET "
                "device_functional = ?, authenticity_confidence = ?, condition_match = ?, "
                "warranty_honored = ?, accessories_complete = ?, reported_issue = ?, "
                "normalized_quality_score = ? "
                "WHERE quality_report_id = ?",
                data['device_functional'],
                data['authenticity_confidence'],
                data['condition_match'],
                data['warranty_honored'],
                data['accessories_complete'],
                data['reported_issue'],
                quality_score,
                quality_report_id
            )
            
            # Update timestamp in quality_reports
            db.execute(
                "UPDATE quality_reports SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                quality_report_id
            )
            
            flash("Quality report updated successfully!")
        else:
            # Insert into quality_reports
            db.execute(
                "INSERT INTO quality_reports (price_report_id, user_id, category) VALUES (?, ?, ?)",
                price_report_id,
                session.get("user_id"),
                category
            )
            
            quality_report_id = db.execute("SELECT last_insert_rowid() AS id")[0]['id']

            # Insert into electronics_quality_reports
            db.execute(
                "INSERT INTO electronics_quality_reports "
                "(quality_report_id, device_functional, authenticity_confidence, condition_match, "
                "warranty_honored, accessories_complete, reported_issue, normalized_quality_score, scoring_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                quality_report_id,
                data['device_functional'],
                data['authenticity_confidence'],
                data['condition_match'],
                data['warranty_honored'],
                data['accessories_complete'],
                data['reported_issue'],
                quality_score,
                "v1.0"
            )

            flash("Quality report submitted successfully!")
        
        return redirect("/user/price_reports")
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to create quality report", 500)


def process_pharma_quality(price_report_id, category, is_update=False):
    """Process pharmaceutical quality report"""
    packaging_sealed = request.form.get('packaging_sealed')
    expiry_date_present = request.form.get('expiry_date_present')
    expiry_status = request.form.get('expiry_status')
    label_completeness = request.form.get('label_completeness')
    dosage_label_matches_expected = request.form.get('dosage_label_matches_expected')
    physical_anomalies_present = request.form.get('physical_anomalies_present')
    evidence_photos = request.form.get('evidence_photos', '')

    if not all([packaging_sealed, expiry_date_present, expiry_status, label_completeness, 
                dosage_label_matches_expected, physical_anomalies_present]):
        return apology("All required fields must be filled", 400)

    try:
        data = {
            'packaging_sealed': int(packaging_sealed),
            'expiry_date_present': int(expiry_date_present),
            'expiry_status': expiry_status,
            'label_completeness': label_completeness,
            'dosage_label_matches_expected': int(dosage_label_matches_expected),
            'physical_anomalies_present': int(physical_anomalies_present),
            'evidence_photos': evidence_photos
        }
    except (ValueError, TypeError):
        return apology("Invalid input data", 400)

    quality_score = score_pharma(data)

    try:
        if is_update:
            # Get existing quality report id
            qr = db.execute(
                "SELECT id FROM quality_reports WHERE price_report_id = ?",
                price_report_id
            )
            quality_report_id = qr[0]['id']
            
            # Update pharma_quality_reports
            db.execute(
                "UPDATE pharma_quality_reports SET "
                "packaging_sealed = ?, expiry_date_present = ?, expiry_status = ?, "
                "label_completeness = ?, dosage_label_matches_expected = ?, "
                "physical_anomalies_present = ?, evidence_photos = ?, normalized_quality_score = ? "
                "WHERE quality_report_id = ?",
                data['packaging_sealed'],
                data['expiry_date_present'],
                data['expiry_status'],
                data['label_completeness'],
                data['dosage_label_matches_expected'],
                data['physical_anomalies_present'],
                data['evidence_photos'],
                quality_score,
                quality_report_id
            )
            
            # Update timestamp in quality_reports
            db.execute(
                "UPDATE quality_reports SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                quality_report_id
            )
            
            flash("Quality report updated successfully!")
        else:
            db.execute(
                "INSERT INTO quality_reports (price_report_id, user_id, category) VALUES (?, ?, ?)",
                price_report_id,
                session.get("user_id"),
                category
            )
            
            quality_report_id = db.execute("SELECT last_insert_rowid() AS id")[0]['id']

            db.execute(
                "INSERT INTO pharma_quality_reports "
                "(quality_report_id, packaging_sealed, expiry_date_present, expiry_status, "
                "label_completeness, dosage_label_matches_expected, physical_anomalies_present, "
                "evidence_photos, normalized_quality_score, scoring_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                quality_report_id,
                data['packaging_sealed'],
                data['expiry_date_present'],
                data['expiry_status'],
                data['label_completeness'],
                data['dosage_label_matches_expected'],
                data['physical_anomalies_present'],
                data['evidence_photos'],
                quality_score,
                "v1.0"
            )

            flash("Quality report submitted successfully!")
        
        return redirect("/user/price_reports")
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to create quality report", 500)


def process_food_quality(price_report_id, category, is_update=False):
    """Process food quality report"""
    packaging_intact = request.form.get('packaging_intact')
    expiry_status = request.form.get('expiry_status')
    weight_or_volume_matches_label = request.form.get('weight_or_volume_matches_label')
    visible_spoilage_present = request.form.get('visible_spoilage_present')
    abnormal_smell_or_appearance = request.form.get('abnormal_smell_or_appearance')
    evidence_photos = request.form.get('evidence_photos', '')

    if not all([packaging_intact, expiry_status, weight_or_volume_matches_label,
                visible_spoilage_present, abnormal_smell_or_appearance]):
        return apology("All required fields must be filled", 400)

    try:
        data = {
            'packaging_intact': int(packaging_intact),
            'expiry_status': expiry_status,
            'weight_or_volume_matches_label': int(weight_or_volume_matches_label),
            'visible_spoilage_present': int(visible_spoilage_present),
            'abnormal_smell_or_appearance': int(abnormal_smell_or_appearance),
            'evidence_photos': evidence_photos
        }
    except (ValueError, TypeError):
        return apology("Invalid input data", 400)

    quality_score = score_food(data)

    try:
        if is_update:
            # Get existing quality report id
            qr = db.execute(
                "SELECT id FROM quality_reports WHERE price_report_id = ?",
                price_report_id
            )
            quality_report_id = qr[0]['id']
            
            # Update food_quality_reports
            db.execute(
                "UPDATE food_quality_reports SET "
                "packaging_intact = ?, expiry_status = ?, weight_or_volume_matches_label = ?, "
                "visible_spoilage_present = ?, abnormal_smell_or_appearance = ?, "
                "evidence_photos = ?, normalized_quality_score = ? "
                "WHERE quality_report_id = ?",
                data['packaging_intact'],
                data['expiry_status'],
                data['weight_or_volume_matches_label'],
                data['visible_spoilage_present'],
                data['abnormal_smell_or_appearance'],
                data['evidence_photos'],
                quality_score,
                quality_report_id
            )
            
            # Update timestamp in quality_reports
            db.execute(
                "UPDATE quality_reports SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                quality_report_id
            )
            
            flash("Quality report updated successfully!")
        else:
            db.execute(
                "INSERT INTO quality_reports (price_report_id, user_id, category) VALUES (?, ?, ?)",
                price_report_id,
                session.get("user_id"),
                category
            )
            
            quality_report_id = db.execute("SELECT last_insert_rowid() AS id")[0]['id']

            db.execute(
                "INSERT INTO food_quality_reports "
                "(quality_report_id, packaging_intact, expiry_status, weight_or_volume_matches_label, "
                "visible_spoilage_present, abnormal_smell_or_appearance, evidence_photos, "
                "normalized_quality_score, scoring_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                quality_report_id,
                data['packaging_intact'],
                data['expiry_status'],
                data['weight_or_volume_matches_label'],
                data['visible_spoilage_present'],
                data['abnormal_smell_or_appearance'],
                data['evidence_photos'],
                quality_score,
                "v1.0"
            )

            flash("Quality report submitted successfully!")
        
        return redirect("/user/price_reports")
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to create quality report", 500)


def process_apparel_quality(price_report_id, category, is_update=False):
    """Process apparel quality report"""
    material_quality = request.form.get('material_quality')
    stitching_quality = request.form.get('stitching_quality')
    fit_consistency = request.form.get('fit_consistency')
    early_wear_present = request.form.get('early_wear_present')
    color_or_print_fading = request.form.get('color_or_print_fading')
    evidence_photos = request.form.get('evidence_photos', '')

    if not all([material_quality, stitching_quality, fit_consistency,
                early_wear_present, color_or_print_fading]):
        return apology("All required fields must be filled", 400)

    try:
        data = {
            'material_quality': material_quality,
            'stitching_quality': stitching_quality,
            'fit_consistency': fit_consistency,
            'early_wear_present': int(early_wear_present),
            'color_or_print_fading': int(color_or_print_fading),
            'evidence_photos': evidence_photos
        }
    except (ValueError, TypeError):
        return apology("Invalid input data", 400)

    quality_score = score_apparel(data)

    try:
        if is_update:
            # Get existing quality report id
            qr = db.execute(
                "SELECT id FROM quality_reports WHERE price_report_id = ?",
                price_report_id
            )
            quality_report_id = qr[0]['id']
            
            # Update apparel_quality_reports
            db.execute(
                "UPDATE apparel_quality_reports SET "
                "material_quality = ?, stitching_quality = ?, fit_consistency = ?, "
                "early_wear_present = ?, color_or_print_fading = ?, "
                "evidence_photos = ?, normalized_quality_score = ? "
                "WHERE quality_report_id = ?",
                data['material_quality'],
                data['stitching_quality'],
                data['fit_consistency'],
                data['early_wear_present'],
                data['color_or_print_fading'],
                data['evidence_photos'],
                quality_score,
                quality_report_id
            )
            
            # Update timestamp in quality_reports
            db.execute(
                "UPDATE quality_reports SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                quality_report_id
            )
            
            flash("Quality report updated successfully!")
        else:
            db.execute(
                "INSERT INTO quality_reports (price_report_id, user_id, category) VALUES (?, ?, ?)",
                price_report_id,
                session.get("user_id"),
                category
            )
            
            quality_report_id = db.execute("SELECT last_insert_rowid() AS id")[0]['id']

            db.execute(
                "INSERT INTO apparel_quality_reports "
                "(quality_report_id, material_quality, stitching_quality, fit_consistency, "
                "early_wear_present, color_or_print_fading, evidence_photos, "
                "normalized_quality_score, scoring_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                quality_report_id,
                data['material_quality'],
                data['stitching_quality'],
                data['fit_consistency'],
                data['early_wear_present'],
                data['color_or_print_fading'],
                data['evidence_photos'],
                quality_score,
                "v1.0"
            )

            flash("Quality report submitted successfully!")
        
        return redirect("/user/price_reports")
    except Exception as e:
        print(f"Database error: {e}")
        return apology("Failed to create quality report", 500)
    