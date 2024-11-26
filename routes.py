from flask import request, jsonify
from models import db, Customer, Product, Order, CustomerAccount, OrderProduct
from schemas import (
    customer_schema, customers_schema,
    product_schema, products_schema,
    order_schema, orders_schema,
    order_product_schema, order_products_schema
)
from marshmallow import ValidationError

def init_routes(app): 

    @app.route('/customers', methods=['GET'])
    def get_customer():
        customers = Customer.query.all()
        return customers_schema.jsonify(customers)

    @app.route('/customers', methods=['POST'])
    def add_customer():
        try:
            customer_data = customer_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        
        new_customer = Customer(name=customer_data['name'],email = customer_data['email'], phone = customer_data['phone'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'message': "New Customer Added Successfully "}), 201

    @app.route('/customers/<int:id>', methods=['PUT'])
    def update_customer(id):
        customer = Customer.query.get_or_404(id)
        try:
            customer_data = customer_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        
        customer.name = customer_data['name']
        customer.email = customer_data['email']
        customer.phone = customer_data['phone']
        db.session.commit()
        return jsonify({'message': "Customer Updated Successfully "}), 200



    @app.route('/customers/<int:id>', methods=['DELETE'])
    def delete_customer(id):
        customer = Customer.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer Removed Successfully "}), 200

    # MARK: CUSTOMER ACCOUNTS ROUTES

    @app.route('/customer_accounts', methods=['GET'])
    def get_customer_accounts():
        
        accounts = CustomerAccount.query.all()
        result = [
            {
                "id": account.id,
                "username": account.username,
                "customer_id": account.customer_id,
                "customer_name": account.customer.name if account.customer else None
            }
            for account in accounts
        ]
        return jsonify(result), 200


    @app.route('/customer_accounts/<int:id>', methods=['GET']) #to grab customers accounts by id
    def get_customer_account(id):
        
        account = CustomerAccount.query.get_or_404(id)
        result = {
            "id": account.id,
            "username": account.username,
            "customer_id": account.customer_id,
            "customer_name": account.customer.name if account.customer else None
        }
        return jsonify(result), 200


    @app.route('/customer_accounts', methods=['POST'])
    def create_customer_account():
    
        data = request.json

        
        if not all(key in data for key in ('username', 'password', 'customer_id')):
            return jsonify({"message": "Missing required fields"}), 400

    
        if CustomerAccount.query.filter_by(username=data['username']).first():
            return jsonify({"message": "Username already exists"}), 400

    
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({"message": "Customer ID does not exist"}), 404

        
        new_account = CustomerAccount(
            username=data['username'],
            password=data['password'],
            customer_id=data['customer_id']
        )
        db.session.add(new_account)
        db.session.commit()

        return jsonify({"message": "Customer Account Created Successfully"}), 201




    @app.route('/customer_accounts/<int:id>', methods=['PUT'])
    def update_customer_account(id):
    
        account = CustomerAccount.query.get_or_404(id)
        data = request.json

    
        if 'username' in data:
        
            if CustomerAccount.query.filter_by(username=data['username']).first():
                return jsonify({"message": "Username already exists"}), 400
            account.username = data['username']
        if 'password' in data:
            account.password = data['password']
        if 'customer_id' in data:
        
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({"message": "Customer ID does not exist"}), 404
            account.customer_id = data['customer_id']

        db.session.commit()
        return jsonify({"message": "Customer Account Updated Successfully"}), 200


    @app.route('/customer_accounts/<int:id>', methods=['DELETE'])
    def delete_customer_account(id):
    
        account = CustomerAccount.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "Customer Account Removed Successfully"}), 200

    # MARK: PRODUCTS ROUTES



    @app.route('/products', methods=['GET'])
    def get_products():
        
        products = Product.query.all()
        return products_schema.jsonify(products), 200



    @app.route('/products', methods=['POST'])
    def create_product():
    
        try:
            product_data = product_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        
        new_product = Product(name=product_data['name'], price=product_data['price'])
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': "New Product Added Successfully"}), 201


    @app.route('/products/<int:id>', methods=['PUT'])
    def update_product(id):
    
        product = Product.query.get_or_404(id)
        try:
            product_data = product_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400

        product.name = product_data['name']
        product.price = product_data['price']
        db.session.commit()
        return jsonify({'message': "Product Updated Successfully"}), 200


    @app.route('/products/<int:id>', methods=['DELETE'])
    def delete_product(id):
    
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': "Product Removed Successfully"}), 200





    @app.route('/order_products', methods=['POST'])
    def create_order_product():
        try:
            data = order_product_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400

    
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
        return jsonify({'message': "OrderProduct Added Successfully"}), 201



    @app.route('/order_products', methods=['GET'])
    def get_order_products():
        order_products = OrderProduct.query.all()
        return order_products_schema.jsonify(order_products), 200

    @app.route('/order_products/<int:id>', methods=['GET'])
    def get_order_product(id):
        order_product = OrderProduct.query.get_or_404(id)
        return order_product_schema.jsonify(order_product), 200

    @app.route('/order_products/<int:id>', methods=['PUT'])
    def update_order_product(id):
        order_product = OrderProduct.query.get_or_404(id)
        try:
            data = order_product_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400

        order_product.order_id = data['order_id']
        order_product.product_id = data['product_id']
        order_product.quantity = data['quantity']
        db.session.commit()
        return jsonify({'message': "OrderProduct Updated Successfully"}), 200

    @app.route('/order_products/<int:id>', methods=['DELETE'])
    def delete_order_product(id):
        order_product = OrderProduct.query.get_or_404(id)
        db.session.delete(order_product)
        db.session.commit()
        return jsonify({'message': "OrderProduct Deleted Successfully"}), 200


    @app.route('/orders', methods=['POST'])
    def place_order():
        try:
            data = order_schema.load(request.json)  
        except ValidationError as e:
            return jsonify(e.messages), 400

    
        new_order = Order(
            date=db.func.current_date(),
            customer_id=data['customer_id']
        )
        db.session.add(new_order)
        db.session.flush() 

        for product in data['products']:
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
        return order_schema.jsonify(new_order), 201


    @app.route('/orders', methods=['GET'])
    def get_orders():
        orders = Order.query.all()
        return orders_schema.jsonify(orders), 200

    @app.route('/orders/<int:id>', methods=['GET'])
    def get_order(id):
        order = Order.query.get_or_404(id)
        return order_schema.jsonify(order), 200