from marshmallow import fields 
from app import ma



class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    


class ProductSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    price = fields.Float(required=True)

    class Meta:
        fields = ("id", "name", "price")



class OrderProductSchema(ma.Schema):
    id = fields.Integer(required=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)

    class Meta:
        fields = ("id", "order_id", "product_id", "quantity")



class OrderSchema(ma.Schema):
    id = fields.Integer(required=True)
    date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)
    status = fields.String(required=True)
    products = fields.List(fields.Nested(OrderProductSchema))  

    


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)