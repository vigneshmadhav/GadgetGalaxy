from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change to a secure key

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------- #
# Home Page - Show all products #
# ----------------------------- #
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# ----------------------------- #
# Product Details Page #
# ----------------------------- #
@app.route('/product/<int:id>')
def product_detail(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product)


# ----------------------------- #
# Cart Page #
# ----------------------------- #
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    conn = get_db_connection()
    products = []
    total = 0
    for item_id in cart_items:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (item_id,)).fetchone()
        if product:
            products.append(product)
            total += product['price']
    conn.close()
    return render_template('cart.html', cart=products, total=total)
@app.route('/checkout')
def checkout():
    # Ensure user is logged in
    if not session.get('user_id'):
        flash("You must be logged in to checkout.", "error")
        return redirect(url_for('login'))

    cart_items = session.get('cart', [])
    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for('cart'))

    conn = get_db_connection()
    products = []
    total = 0
    for item_id in cart_items:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (item_id,)).fetchone()
        if product:
            products.append(product)
            total += product['price']

            # Save order
            conn.execute('INSERT INTO orders (user_id, product_id) VALUES (?, ?)',
                         (session['user_id'], product['id']))
    conn.commit()
    conn.close()

    # Clear cart after checkout
    session['cart'] = []

    flash("Order placed successfully!", "success")
    return render_template('checkout.html', products=products, total=total)

# ----------------------------- #
# Add to Cart #
# ----------------------------- #
@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    cart = session.get('cart', [])
    cart.append(id)
    session['cart'] = cart
    flash("Product added to cart!", "success")
    return redirect(url_for('cart'))

# ----------------------------- #
# Remove from Cart #
# ----------------------------- #
@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart = session.get('cart', [])
    if id in cart:
        cart.remove(id)
    session['cart'] = cart
    flash("Product removed from cart.", "success")
    return redirect(url_for('cart'))

# ----------------------------- #
# Admin Panel #
# ----------------------------- #
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.form['image']
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)',
                     (name, description, price, image))
        conn.commit()
        conn.close()
        flash("Product added!", "success")
        return redirect(url_for('admin'))

    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('admin.html', products=products)

# ----------------------------- #
# Signup #
# ----------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            conn.close()
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists.", "error")
            conn.close()
            return redirect(url_for('signup'))

    return render_template('signup.html')

# ----------------------------- #
# Login #
# ----------------------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# ----------------------------- #
# Logout #
# ----------------------------- #
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))

# ----------------------------- #
# Run App #
# ----------------------------- #
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT if available
    app.run(host='0.0.0.0', port=port, debug=True)


