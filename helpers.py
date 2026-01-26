import re
from flask import redirect, render_template, session
from functools import wraps

EMAIL_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
    r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
    r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@'
    r"(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,})$"
)


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def is_valid_email(email: str) -> bool:
    """
    Validates an email string against a strict RFC 5322 regex.
    Returns True if valid, False otherwise.
    """
    email = email.strip()
    return bool(EMAIL_REGEX.match(email))

def score_electronics(report: dict) -> float:
    """
    Electronics Quality Scoring
    Hard failures:
        - device_functional = 0
        - authenticity_confidence = 1
    Minor issues are penalized
    """
    # Hard failures
    if report['device_functional'] == 0 or report['authenticity_confidence'] == 1:
        return 0.0

    score = 1.0

    # Penalties
    score -= (5 - report['authenticity_confidence']) * 0.08
    score -= (5 - report['condition_match']) * 0.06

    warranty = report.get('warranty_honored')
    if warranty is True:
        score -= 0.0
    elif warranty is False:
        score -= 0.25
    else:  # None / not tested
        score -= 0.05

    score -= 0.1 if report['accessories_complete'] == 0 else 0.0

    return max(0.0, min(score, 1.0))


def score_pharma(report: dict) -> float:
    """
    Pharmaceutical Quality Scoring
    Hard failures:
        - expiry_status = 'expired'
        - dosage_label_matches_expected = 0
    Minor issues: packaging, labeling, anomalies
    """
    if report['expiry_status'] == 'expired' or report['dosage_label_matches_expected'] == 0:
        return 0.0

    score = 1.0
    score -= 0.2 if report['packaging_sealed'] == 0 else 0.0
    score -= 0.15 if report['expiry_date_present'] == 0 else 0.0
    score -= 0.1 if report['label_completeness'] != 'complete' else 0.0
    score -= 0.1 if report['physical_anomalies_present'] == 1 else 0.0

    return max(0.0, min(score, 1.0))


def score_food(report: dict) -> float:
    """
    Food & Beverage Quality Scoring
    Hard failures:
        - expiry_status = 'expired'
        - visible_spoilage_present = 1
    Minor issues: packaging, weight, smell/appearance
    """
    if report['expiry_status'] == 'expired' or report['visible_spoilage_present'] == 1:
        return 0.0

    score = 1.0
    score -= 0.1 if report['packaging_intact'] == 0 else 0.0
    score -= 0.1 if report['weight_or_volume_matches_label'] == 0 else 0.0
    score -= 0.15 if report['abnormal_smell_or_appearance'] == 1 else 0.0

    return max(0.0, min(score, 1.0))


def score_apparel(report: dict) -> float:
    """
    Apparel & Textiles Quality Scoring
    Hard failures:
        - stitching_quality = 'major_defects'
    Minor issues: material, minor defects, fit, early wear, fading
    """
    if report['stitching_quality'] == 'major_defects':
        return 0.0

    score = 1.0
    # Material quality
    if report['material_quality'] == 'below_expected':
        score -= 0.15
    elif report['material_quality'] == 'poor':
        score -= 0.3

    # Stitching minor defects
    score -= 0.1 if report['stitching_quality'] == 'minor_defects' else 0.0

    # Fit consistency
    score -= 0.1 if report['fit_consistency'] != 'as_expected' else 0.0

    # Early wear
    score -= 0.05 if report['early_wear_present'] == 1 else 0.0

    # Color/print fading
    score -= 0.05 if report['color_or_print_fading'] == 1 else 0.0

    return max(0.0, min(score, 1.0))

def is_admin(user):
    if user['user_type'] != 'admin':
        return False
