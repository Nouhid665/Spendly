from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, get_user_by_id

app = Flask(__name__)
app.secret_key = "spendly-secret-key-change-in-production"

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    # Redirect logged-in users to profile page
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect logged-in users to landing page
    if "user_id" in session:
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        # Validation
        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        if "@" not in email:
            return render_template("register.html", error="Please enter a valid email address")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")

        if password != password_confirm:
            return render_template("register.html", error="Passwords do not match")

        # Create user
        user_id = create_user(name, email, password)

        if user_id is None:
            return render_template("register.html", error="Email already registered")

        # Success - redirect to login with success message
        return redirect(url_for("login") + "?success=1")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged-in users to landing page
    if "user_id" in session:
        return redirect(url_for("landing"))

    # Check for success message from registration
    success = None
    if request.args.get("success"):
        success = "Account created! Please sign in."

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validate email format
        if not email or "@" not in email:
            return render_template("login.html", error="Invalid email or password")

        if not password:
            return render_template("login.html", error="Invalid email or password")

        # Get user from database
        user = get_user_by_email(email)

        if user is None:
            return render_template("login.html", error="Invalid email or password")

        # Verify password
        if not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password")

        # Create session
        session["user_id"] = user["id"]

        return redirect(url_for("profile"))

    return render_template("login.html", success=success)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    # Guard: redirect unauthenticated users to login
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Fetch user data from database
    user = get_user_by_id(user_id)

    # Hardcoded user info (Step 4 only - will be replaced in Step 5)
    user_info = {
        "name": user["name"] if user else "Demo User",
        "email": user["email"] if user else "demo@spendly.com",
        "member_since": "April 2026"
    }

    # Hardcoded summary stats
    summary_stats = {
        "total_spent": "₹4,893",
        "transaction_count": 8,
        "top_category": "Shopping"
    }

    # Hardcoded transaction history (minimum 3 rows)
    transactions = [
        {"date": "2026-04-14", "description": "Coffee and pastries", "category": "Food", "amount": "₹12.75"},
        {"date": "2026-04-12", "description": "Gift for friend", "category": "Other", "amount": "₹25.00"},
        {"date": "2026-04-10", "description": "New shoes", "category": "Shopping", "amount": "₹200.00"},
        {"date": "2026-04-07", "description": "Movie tickets and dinner", "category": "Entertainment", "amount": "₹60.00"},
        {"date": "2026-04-05", "description": "Pharmacy - vitamins", "category": "Health", "amount": "₹35.00"},
    ]

    # Hardcoded category breakdown (minimum 3 categories)
    category_breakdown = [
        {"category": "Shopping", "amount": "₹200.00", "percentage": 41},
        {"category": "Bills", "amount": "₹120.00", "percentage": 25},
        {"category": "Entertainment", "amount": "₹60.00", "percentage": 12},
        {"category": "Transport", "amount": "₹45.00", "percentage": 9},
        {"category": "Health", "amount": "₹35.00", "percentage": 7},
    ]

    return render_template("profile.html",
                           user=user_info,
                           stats=summary_stats,
                           transactions=transactions,
                           categories=category_breakdown)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
