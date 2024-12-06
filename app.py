from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError


db = SQLAlchemy()
ma = Marshmallow()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Godswill150@127.0.0.1/e_commerce_db1"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)
ma.init_app(app)

# Models
class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer', cascade="all, delete-orphan")

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id', ondelete="CASCADE"), nullable=False)

class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    products = db.relationship('OrderProduct', backref='order', lazy="joined")

class OrderProduct(db.Model):
    __tablename__ = "OrderProduct"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id', ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id', ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

# Schemas
class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "phone")

class CustomerAccountSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "customer_id")

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "price")

class OrderProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "order_id", "product_id", "quantity")

class OrderSchema(ma.Schema):
    products = fields.List(fields.Nested(OrderProductSchema))

    class Meta:
        fields = ("id", "date", "customer_id", "status", "products")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True)


@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        data = customer_schema.load(request.json)
        new_customer = Customer(**data)
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except ValidationError as e:
        return jsonify(e.messages), 400

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        data = customer_schema.load(request.json)
        for key, value in data.items():
            setattr(customer, key, value)
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except ValidationError as e:
        return jsonify(e.messages), 400

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200


@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    try:
        data = customer_account_schema.load(request.json)
        new_account = CustomerAccount(**data)
        db.session.add(new_account)
        db.session.commit()
        return customer_account_schema.jsonify(new_account), 201
    except ValidationError as e:
        return jsonify(e.messages), 400

@app.route('/customer_accounts', methods=['GET'])
def get_customer_accounts():
    accounts = CustomerAccount.query.all()
    return customer_accounts_schema.jsonify(accounts)

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully"}), 200


@app.route('/products', methods=['POST'])
def add_product():
    try:
        data = product_schema.load(request.json)
        new_product = Product(**data)
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product), 201
    except ValidationError as e:
        return jsonify(e.messages), 400

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        new_order = Order(
            date=db.func.current_date(),
            customer_id=data['customer_id'],
            status=data.get('status', 'Pending')
        )
        db.session.add(new_order)
        db.session.flush()  
        for product in data.get('products', []):
            product_obj = Product.query.get(product['product_id'])
            if not product_obj:
                return jsonify({"message": f"Product with ID {product['product_id']} not found"}), 404
            new_order_product = OrderProduct(
                order_id=new_order.id,
                product_id=product['product_id'],
                quantity=product['quantity']
            )
            db.session.add(new_order_product)

        db.session.commit()
        return jsonify({"message": "Order Created Successfully", "order_id": new_order.id}), 201

    except ValidationError as e:
        return jsonify(e.messages), 400

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    results = [
        {
            "id": order.id,
            "date": order.date,
            "customer_id": order.customer_id,
            "status": order.status,
            "products": [
                {
                    "product_id": op.product_id,
                    "quantity": op.quantity
                } for op in order.products
            ]
        } for order in orders
    ]
    return jsonify(results), 200

@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)
    result = {
        "id": order.id,
        "date": order.date,
        "customer_id": order.customer_id,
        "status": order.status,
        "products": [
            {
                "product_id": op.product_id,
                "quantity": op.quantity
            } for op in order.products
        ]
    }
    return jsonify(result), 200

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    data = request.json

    order.status = data.get('status', order.status)
    db.session.commit()
    return jsonify({"message": "Order Updated Successfully"}), 200

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order Deleted Successfully"}), 200


@app.route('/order_products', methods=['POST'])
def create_order_product():
    data = request.json
    if not Order.query.get(data['order_id']):
        return jsonify({"message": "Order ID not found"}), 404
    if not Product.query.get(data['product_id']):
        return jsonify({"message": "Product ID not found"}), 404

    new_order_product = OrderProduct(
        order_id=data['order_id'],
        product_id=data['product_id'],
        quantity=data['quantity']
    )
    db.session.add(new_order_product)
    db.session.commit()
    return jsonify({"message": "Order Product Created Successfully"}), 201

@app.route('/order_products', methods=['GET'])
def get_order_products():
    order_products = OrderProduct.query.all()
    results = [
        {
            "id": op.id,
            "order_id": op.order_id,
            "product_id": op.product_id,
            "quantity": op.quantity
        } for op in order_products
    ]
    return jsonify(results), 200

@app.route('/order_products/<int:id>', methods=['GET'])
def get_order_product(id):
    order_product = OrderProduct.query.get_or_404(id)
    result = {
        "id": order_product.id,
        "order_id": order_product.order_id,
        "product_id": order_product.product_id,
        "quantity": order_product.quantity
    }
    return jsonify(result), 200

@app.route('/order_products/<int:id>', methods=['PUT'])
def update_order_product(id):
    order_product = OrderProduct.query.get_or_404(id)
    data = request.json

    order_product.order_id = data.get('order_id', order_product.order_id)
    order_product.product_id = data.get('product_id', order_product.product_id)
    order_product.quantity = data.get('quantity', order_product.quantity)
    db.session.commit()
    return jsonify({"message": "Order Product Updated Successfully"}), 200

@app.route('/order_products/<int:id>', methods=['DELETE'])
def delete_order_product(id):
    order_product = OrderProduct.query.get_or_404(id)
    db.session.delete(order_product)
    db.session.commit()
    return jsonify({"message": "Order Product Deleted Successfully"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
