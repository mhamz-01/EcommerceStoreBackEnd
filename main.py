from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route("/")
def landing_page():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add_product", methods=['GET', 'POST'])
def crud_operations():
    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            price = float(request.form['price'])
            image = request.form['image']
            quantity = int(request.form['quantity'])
            new_product = Product(name=name, price=price, image=image, quantity=quantity)
            db.session.add(new_product)
            db.session.commit()
        elif 'edit' in request.form:
            product_id = int(request.form['id'])
            product = Product.query.get(product_id)
            product.name = request.form['name']
            product.price = float(request.form['price'])
            product.image = request.form['image']
            product.quantity = int(request.form['quantity'])
            db.session.commit()
        elif 'delete' in request.form:
            product_id = int(request.form['id'])
            product = Product.query.get(product_id)
            db.session.delete(product)
            db.session.commit()
        return redirect(url_for('crud_operations'))
    products = Product.query.all()
    return render_template("crud_operations.html", products=products)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product and product.quantity > 0:
        if 'cart' not in session:
            session['cart'] = {}

        cart = session['cart']
        product_id_str = str(product_id)

        if not isinstance(cart, dict):
            session['cart'] = {}
            cart = session['cart']

        if product_id_str in cart:
            if cart[product_id_str] < product.quantity:
                cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1

        session['cart'] = cart
        print("Cart after adding product:", session['cart'])  # Debug statement

    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    if 'cart' in session:
        cart = session['cart']
        print("Cart in session:", cart)  # Debug statement

        if not isinstance(cart, dict):
            session['cart'] = {}
            cart = session['cart']

        for product_id_str, quantity in cart.items():
            product = Product.query.get(int(product_id_str))
            if product:
                cart_items.append({'product': product, 'quantity': quantity})
                total += product.price * quantity

    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    total = 0
    if request.method == "POST":
        if 'cart' in session:
            cart = session['cart']
            for product_id_str, quantity in cart.items():
                product = Product.query.get(int(product_id_str))
                if product:
                    total += product.price * quantity
                    product.quantity -= quantity
                    db.session.commit()

            session.pop('cart', None)
        return render_template("checkout.html", total=total)

    if 'cart' in session:
        cart = session['cart']
        for product_id_str, quantity in cart.items():
            product = Product.query.get(int(product_id_str))
            if product:
                total += product.price * quantity

    return render_template("checkout.html", total=total)

if __name__ == "__main__":
    app.run(debug=True)
