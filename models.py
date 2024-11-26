from app import db

class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    status = db.Column(db.String(50), nullable=False, default="Pending")
    products = db.relationship('OrderProduct', backref='order', lazy=True)

class OrderProduct(db.Model):
    __tablename__ = "OrderProduct"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref ='customer')


class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id', ondelete="CASCADE") )
    customer = db.relationship( "Customer", backref=db.backref("customer_account", cascade="all, delete-orphan"), uselist=False) 

order_product = db.Table('Order_Product', 
                 db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
                 db.Column('product_id',db.Integer,db.ForeignKey('Products.id'), primary_key=True))


class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('OrderProduct', backref='product', lazy=True)

