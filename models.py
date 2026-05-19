from datetime import datetime
from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    cep = db.Column(db.String(12), nullable=True)
    rua = db.Column(db.String(160), nullable=True)
    numero = db.Column(db.String(30), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(40), nullable=True)
    complemento = db.Column(db.String(160), nullable=True)
    preferred_payment = db.Column(db.String(30), nullable=True)
    card_flag = db.Column(db.String(30), nullable=True)
    card_last4 = db.Column(db.String(4), nullable=True)
    card_name = db.Column(db.String(120), nullable=True)
    card_expiry = db.Column(db.String(5), nullable=True)

    orders = db.relationship("Order", backref="user", lazy=True, cascade="all, delete-orphan")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)

    shipping_type = db.Column(db.String(50), nullable=False)
    shipping_price = db.Column(db.Float, nullable=False, default=0)

    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(100), nullable=False)

    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)

    product_name = db.Column(db.String(150), nullable=False)
    product_category = db.Column(db.String(100), nullable=True)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
