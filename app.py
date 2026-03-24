from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from extensions import db
from flask import Flask, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "chave_secreta_ecommerce_faculdade"

db.init_app(app)
from models import User

PRODUCTS = [
    {
        "id": 1,
        "name": "Flak 2.0",
        "price": 1500.00,
        "image": "flak 01.png",
        "short_description": "Óculos esportivo premium com conforto e design moderno.",
        "description": (
            "A edição XL oferece uma armação em tamanho padrão com cobertura da lente incrementada "
            "e até o último milímetro da visão periférica é otimizado graças à High Definition Optics®. "
            "Design durável e leve que conduz o desempenho a um nível mais alto. "
            "Material O Matter™, detalhes metálicos, almofadas Unobtainium®, lentes Prizm™, etc."
        ),
        "category": "Esportivos"
    },
    {
        "id": 2,
        "name": "Flanela Mágica",
        "price": 50.90,
        "image": "lencomagico3.png",
        "short_description": "Flanela prática e reutilizável para limpeza de lentes e telas.",
        "description": (
            "Alta eficiência: remove poeira, manchas e impressões digitais sem riscar. "
            "Versátil: perfeita para telas e superfícies delicadas. "
            "Durável: reutilizável e fácil de lavar. "
            "Garanta já a sua e mantenha suas lentes sempre limpas e brilhantes."
        ),
        "category": "Acessórios"
    },
    {
        "id": 3,
        "name": "Ray-Ban Meta Wayfarer - Gen 2",
        "price": 3029.90,
        "image": "meta foto1.png",
        "short_description": "Óculos inteligente com câmera, áudio e comandos por voz.",
        "description": (
            "Óculos inteligente com recursos de Meta AI, câmera integrada, áudio embutido "
            "e comandos por voz. Ideal para capturar fotos, gravar vídeos, ouvir música, "
            "realizar chamadas e obter respostas rápidas no dia a dia."
        ),
        "category": "Tecnologia"
    },
    {
        "id": 4,
        "name": "Aviator Classic",
        "price": 899.90,
        "image": "Model code RB3025 001 62-14.png",
        "short_description": "Modelo clássico com visual elegante e confortável para uso diário.",
        "description": "Armação elegante e confortável para uso cotidiano.",
        "category": "Armações"
    },
    {
        "id": 5,
        "name": "Lens Wipes",
        "price": 115.90,
        "image": "lens wipes foto1.png",
        "short_description": "Lenços umedecidos para limpeza rápida e segura de lentes.",
        "description": (
            "Lenços umedecidos ZEISS para limpeza de lentes e superfícies delicadas. "
            "Livre de amônia, tecido microfino não abrasivo e antiestático. "
            "Remove manchas com praticidade e segurança."
        ),
        "category": "Acessórios"
    }
]


def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


def get_product_by_id(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def calculate_cart_details():
    cart = get_cart()
    cart_items = []
    total = 0

    for product_id_str, quantity in cart.items():
        product = get_product_by_id(int(product_id_str))
        if product:
            subtotal = product["price"] * quantity
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "image": product["image"],
                "subtotal": subtotal,
                "category": product["category"]
            })
            total += subtotal

    return cart_items, total


def generate_fake_barcode():
    blocks = [
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000000000, 99999999999))
    ]
    return " ".join(blocks)


def get_categories():
    return sorted(list(set(product["category"] for product in PRODUCTS)))


@app.route("/")
def index():
    cart = get_cart()
    cart_count = sum(cart.values())
    categories = get_categories()

    selected_category = request.args.get("category", "").strip()

    if selected_category:
        filtered_products = [
            product for product in PRODUCTS
            if product["category"].lower() == selected_category.lower()
        ]
    else:
        filtered_products = PRODUCTS

    return render_template(
        "index.html",
        products=filtered_products,
        categories=categories,
        cart_count=cart_count,
        current_category=selected_category
    )


@app.route("/category/<category_name>")
def category(category_name):
    filtered_products = [
        p for p in PRODUCTS
        if p["category"].lower() == category_name.lower()
    ]

    cart_count = sum(session.get("cart", {}).values())
    categories = get_categories()

    return render_template(
        "index.html",
        products=filtered_products,
        categories=categories,
        cart_count=cart_count,
        current_category=category_name
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    cart_count = sum(session.get("cart", {}).values())

    return render_template(
        "product_detail.html",
        product=product,
        cart_count=cart_count
    )


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    cart = get_cart()
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    session["cart"] = cart
    flash(f"{product['name']} foi adicionado ao carrinho.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
def cart():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


@app.route("/update_cart", methods=["POST"])
def update_cart():
    cart = get_cart()

    for key, value in request.form.items():
        if key.startswith("quantity_"):
            product_id = key.split("_")[1]

            try:
                quantity = int(value)
                if quantity <= 0:
                    cart.pop(product_id, None)
                else:
                    cart[product_id] = quantity
            except ValueError:
                pass

    session["cart"] = cart
    flash("Carrinho atualizado com sucesso.", "success")
    return redirect(url_for("cart"))


@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("Produto removido do carrinho.", "success")
    return redirect(url_for("cart"))


@app.route("/checkout")
def checkout():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    return render_template(
        "address.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


@app.route("/address", methods=["GET", "POST"])
def address():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        session["checkout_data"] = {
            "customer_name": request.form.get("customer_name", "").strip(),
            "customer_email": request.form.get("customer_email", "").strip(),
            "cep": request.form.get("cep", "").strip(),
            "rua": request.form.get("rua", "").strip(),
            "numero": request.form.get("numero", "").strip(),
            "bairro": request.form.get("bairro", "").strip(),
            "cidade": request.form.get("cidade", "").strip(),
            "estado": request.form.get("estado", "").strip(),
            "complemento": request.form.get("complemento", "").strip()
        }
        return redirect(url_for("shipping"))

    return render_template(
        "address.html",
        cart_count=cart_count,
        current_step="address"
    )



@app.route("/shipping", methods=["GET", "POST"])
def shipping():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    checkout_data = session.get("checkout_data")

    if not checkout_data:
        flash("Preencha o endereço antes de continuar.", "error")
        return redirect(url_for("address"))

    if request.method == "POST":
        shipping_type = request.form.get("shipping_type", "Padrao")

        if shipping_type == "Expressa":
            shipping_price = 29.90
        else:
            shipping_type = "Padrao"
            shipping_price = 15.90

        checkout_data["shipping_type"] = shipping_type
        checkout_data["shipping_price"] = shipping_price
        session["checkout_data"] = checkout_data

        return redirect(url_for("payment"))

    return render_template(
        "shipping.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count,
        current_step="shipping"
    )

@app.route("/payment", methods=["GET", "POST"])
def payment():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    checkout_data = session.get("checkout_data", {})

    if not checkout_data:
        flash("Preencha o endereço antes de continuar.", "error")
        return redirect(url_for("address"))

    shipping_price = checkout_data.get("shipping_price", 0)

    if request.method == "POST":
        customer_name = checkout_data.get("customer_name", "").strip()
        customer_email = checkout_data.get("customer_email", "").strip()

        cep = checkout_data.get("cep", "").strip()
        rua = checkout_data.get("rua", "").strip()
        numero = checkout_data.get("numero", "").strip()
        bairro = checkout_data.get("bairro", "").strip()
        cidade = checkout_data.get("cidade", "").strip()
        estado = checkout_data.get("estado", "").strip()
        complemento = checkout_data.get("complemento", "").strip()

        payment_method = request.form.get("payment_method", "").strip()

        # monta endereço formatado
        customer_address = f"{rua}, {numero}"
        if complemento:
            customer_address += f" - {complemento}"
        customer_address += f" | {bairro} - {cidade}/{estado} | CEP: {cep}"

        # validação dos campos obrigatórios
        if not all([customer_name, customer_email, cep, rua, numero, bairro, cidade, estado, payment_method]):
            flash("Preencha todos os campos obrigatórios.", "error")
            return redirect(url_for("address"))

        order_number = random.randint(100000, 999999)
        order_date = datetime.now().strftime("%d/%m/%Y")
        due_date = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")

        payment_data = {"method": payment_method}

        if payment_method == "cartao":
            card_flag = request.form.get("card_flag", "").strip()
            card_number = request.form.get("card_number", "").strip()
            card_name = request.form.get("card_name", "").strip()
            card_expiry = request.form.get("card_expiry", "").strip()
            card_cvv = request.form.get("card_cvv", "").strip()
            installments = request.form.get("installments", "").strip()

            if not all([card_flag, card_number, card_name, card_expiry, card_cvv, installments]):
                flash("Preencha todos os dados do cartão.", "error")
                return redirect(url_for("payment"))

            only_digits_card = "".join(filter(str.isdigit, card_number))
            only_digits_cvv = "".join(filter(str.isdigit, card_cvv))

            if len(only_digits_card) != 16:
                flash("Número do cartão inválido. Digite 16 números.", "error")
                return redirect(url_for("payment"))

            if len(only_digits_cvv) not in [3, 4]:
                flash("CVV inválido.", "error")
                return redirect(url_for("payment"))

            payment_data.update({
                "card_flag": card_flag,
                "card_number_masked": "**** **** **** " + only_digits_card[-4:],
                "installments": installments,
                "status": "Pagamento aprovado"
            })

        elif payment_method == "boleto":
            payment_data.update({
                "barcode": generate_fake_barcode(),
                "status": "Boleto gerado com sucesso (simulado)",
                "due_date": due_date,
                "beneficiary": "LojaFácil Comércio Virtual Ltda."
            })

        else:
            flash("Forma de pagamento inválida.", "error")
            return redirect(url_for("payment"))

        order = {
            "order_number": order_number,
            "order_date": order_date,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_address": customer_address,
            "customer_zipcode": cep,
            "items": cart_items,
            "total": total + shipping_price,
            "payment": payment_data,
            "shipping_type": checkout_data.get("shipping_type", "Padrao"),
            "shipping_price": shipping_price
        }

        session["cart"] = {}
        session.pop("checkout_data", None)

        return render_template(
            "success.html",
            order=order,
            cart_count=0,
            current_step="success"
        )

    return render_template(
        "payment.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count,
        shipping_price=shipping_price,
        current_step="payment"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    cart_count = sum(session.get("cart", {}).values())

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not name or not email or not password or not confirm_password:
            flash("Preencha todos os campos.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Já existe um usuário com esse e-mail.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Cadastro realizado com sucesso. Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", cart_count=cart_count)


@app.route("/login", methods=["GET", "POST"])
def login():
    cart_count = sum(session.get("cart", {}).values())

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Preencha e-mail e senha.", "error")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("E-mail ou senha inválidos.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.name

        flash(f"Bem-vindo, {user.name}!", "success")
        return redirect(url_for("index"))

    return render_template("login.html", cart_count=cart_count)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)


    