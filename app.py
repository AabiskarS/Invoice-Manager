from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from weasyprint import HTML
import sqlite3
import io

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Change this in production

@app.context_processor
def inject_now():
    return {'now': datetime.now()}
DB = "invoice.db"

# Helpers
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/")
@login_required
def index():
    db = get_db()
    total_paid = db.execute("SELECT SUM(total) AS sum FROM invoices WHERE user_id = ? AND status = 'paid'", (session["user_id"],)).fetchone()["sum"] or 0
    total_unpaid = db.execute("SELECT SUM(total) AS sum FROM invoices WHERE user_id = ? AND status = 'unpaid'", (session["user_id"],)).fetchone()["sum"] or 0
    upcoming = db.execute("SELECT * FROM invoices WHERE user_id = ? AND status = 'unpaid' AND due_date >= DATE('now') ORDER BY due_date ASC LIMIT 5", (session["user_id"],)).fetchall()
    return render_template("index.html", total_paid=total_paid, total_unpaid=total_unpaid, upcoming=upcoming)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password required")
            return redirect("/register")
        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("Username already taken")
            return redirect("/register")
        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_pw))
        db.commit()
        flash("Registered! Please log in.")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user or not check_password_hash(user["hash"], password):
            flash("Invalid credentials")
            return redirect("/login")
        session["user_id"] = user["id"]
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Clients
@app.route("/clients")
@login_required
def clients():
    db = get_db()
    clients = db.execute("SELECT * FROM clients WHERE user_id = ?", (session["user_id"],)).fetchall()
    return render_template("clients.html", clients=clients)

@app.route("/clients/add", methods=["GET", "POST"])
@login_required
def add_client():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        db = get_db()
        db.execute("INSERT INTO clients (user_id, name, email, phone, address) VALUES (?, ?, ?, ?, ?)",
                   (session["user_id"], name, email, phone, address))
        db.commit()
        return redirect("/clients")
    return render_template("add_client.html")

@app.route("/clients/edit/<int:client_id>", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        db.execute("UPDATE clients SET name = ?, email = ?, phone = ?, address = ? WHERE id = ? AND user_id = ?",
                   (name, email, phone, address, client_id, session["user_id"]))
        db.commit()
        return redirect("/clients")
    client = db.execute("SELECT * FROM clients WHERE id = ? AND user_id = ?", (client_id, session["user_id"])).fetchone()
    return render_template("edit_client.html", client=client)

@app.route("/clients/delete/<int:client_id>")
@login_required
def delete_client(client_id):
    db = get_db()
    db.execute("DELETE FROM clients WHERE id = ? AND user_id = ?", (client_id, session["user_id"]))
    db.commit()
    return redirect("/clients")

# Invoices
@app.route("/invoices")
@login_required
def invoices():
    db = get_db()
    rows = db.execute("""
        SELECT invoices.*, clients.name AS client_name
        FROM invoices
        JOIN clients ON invoices.client_id = clients.id
        WHERE invoices.user_id = ?
        ORDER BY invoices.date DESC
    """, (session["user_id"],)).fetchall()
    return render_template("invoices.html", invoices=rows)

@app.route("/invoices/new", methods=["GET", "POST"])
@login_required
def new_invoice():
    db = get_db()
    if request.method == "POST":
        client_id = request.form.get("client_id")
        date = request.form.get("date")
        due_date = request.form.get("due_date")
        items = []
        total = 0.0
        for i in range(1, 6):
            desc = request.form.get(f"desc{i}")
            qty = request.form.get(f"qty{i}")
            price = request.form.get(f"price{i}")
            if desc and qty and price:
                qty = int(qty)
                price = float(price)
                total += qty * price
                items.append((desc, qty, price))
        invoice_id = db.execute("INSERT INTO invoices (user_id, client_id, date, due_date, total, status) VALUES (?, ?, ?, ?, ?, ?)",
                                (session["user_id"], client_id, date, due_date, total, 'unpaid')).lastrowid
        for desc, qty, price in items:
            db.execute("INSERT INTO invoice_items (invoice_id, description, quantity, unit_price) VALUES (?, ?, ?, ?)",
                       (invoice_id, desc, qty, price))
        db.commit()
        return redirect("/invoices")
    clients = db.execute("SELECT * FROM clients WHERE user_id = ?", (session["user_id"],)).fetchall()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template("new_invoice.html", clients=clients, today=today)

@app.route("/invoices/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    db = get_db()
    invoice = db.execute("""
        SELECT invoices.*, clients.name AS client_name, clients.email
        FROM invoices
        JOIN clients ON invoices.client_id = clients.id
        WHERE invoices.id = ? AND invoices.user_id = ?
    """, (invoice_id, session["user_id"])).fetchone()
    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    payments = db.execute("SELECT * FROM payments WHERE invoice_id = ?", (invoice_id,)).fetchall()
    return render_template("view_invoice.html", invoice=invoice, items=items, payments=payments)

@app.route("/invoices/edit/<int:invoice_id>", methods=["GET", "POST"])
@login_required
def edit_invoice(invoice_id):
    db = get_db()
    invoice = db.execute("SELECT * FROM invoices WHERE id = ? AND user_id = ?", (invoice_id, session["user_id"])).fetchone()

    if not invoice:
        return "Invoice not found", 404

    if request.method == "POST":
        date = request.form.get("date")
        due_date = request.form.get("due_date")
        db.execute("UPDATE invoices SET date = ?, due_date = ? WHERE id = ?", (date, due_date, invoice_id))
        db.commit()
        flash("Invoice updated.")
        return redirect(f"/invoices/{invoice_id}")

    return render_template("edit_invoice.html", invoice=invoice)

@app.route("/invoices/delete/<int:invoice_id>")
@login_required
def delete_invoice(invoice_id):
    db = get_db()

    # Delete invoice items and payments first (foreign key constraint safe)
    db.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    db.execute("DELETE FROM payments WHERE invoice_id = ?", (invoice_id,))
    db.execute("DELETE FROM invoices WHERE id = ? AND user_id = ?", (invoice_id, session["user_id"]))

    db.commit()
    flash("Invoice deleted successfully.")
    return redirect("/invoices")

@app.route("/invoices/<int:invoice_id>/pay", methods=["GET", "POST"])
@login_required
def add_payment(invoice_id):
    db = get_db()
    invoice = db.execute("SELECT * FROM invoices WHERE id = ? AND user_id = ?", (invoice_id, session["user_id"])).fetchone()
    if not invoice:
        return "Invoice not found", 404
    if request.method == "POST":
        amount = float(request.form.get("amount"))
        date = request.form.get("date")
        db.execute("INSERT INTO payments (invoice_id, amount, date) VALUES (?, ?, ?)", (invoice_id, amount, date))
        payments = db.execute("SELECT SUM(amount) as total_paid FROM payments WHERE invoice_id = ?", (invoice_id,)).fetchone()
        total_paid = payments["total_paid"] or 0.0
        if total_paid >= invoice["total"]:
            db.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (invoice_id,))
        db.commit()
        return redirect(f"/invoices/{invoice_id}")
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template("add_payment.html", invoice=invoice, today=today)

@app.route("/invoices/<int:invoice_id>/pdf")
@login_required
def invoice_pdf(invoice_id):
    db = get_db()
    invoice = db.execute("""
        SELECT invoices.*, clients.name AS client_name
        FROM invoices
        JOIN clients ON invoices.client_id = clients.id
        WHERE invoices.id = ? AND invoices.user_id = ?
    """, (invoice_id, session["user_id"])).fetchone()
    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    html = render_template("invoice_pdf.html", invoice=invoice, items=items)
    pdf = HTML(string=html).write_pdf()
    return send_file(io.BytesIO(pdf), mimetype="application/pdf", download_name=f"invoice_{invoice_id}.pdf")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
