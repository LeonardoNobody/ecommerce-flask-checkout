from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from extensions import db
from flask import Flask, jsonify, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta
import random
import secrets

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "chave_secreta_ecommerce_faculdade"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            checkout_paths = {"/address", "/shipping", "/payment", "/checkout"}
            if request.path not in checkout_paths:
                flash("Entre na sua conta para continuar.", "info")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


db.init_app(app)
from models import Order, OrderItem, User

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
        "category": "Esportivos",
        "stock": 8
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
        "category": "Acessórios",
        "stock": 25
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
        "category": "Tecnologia",
        "stock": 5
    },
    {
        "id": 4,
        "name": "Aviator Classic",
        "price": 899.90,
        "image": "Model code RB3025 001 62-14.png",
        "short_description": "Modelo clássico com visual elegante e confortável para uso diário.",
        "description": "Armação elegante e confortável para uso cotidiano.",
        "category": "Armações",
        "stock": 10
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
        "category": "Acessórios",
        "stock": 30
    },
    {
        "id": 6,
        "name": "Solar Wayfarer Preto",
        "price": 349.90,
        "image": "solar-wayfarer-preto.jpg",
        "short_description": "Óculos solar preto com formato wayfarer e lentes escuras.",
        "description": (
            "Modelo solar de linhas clássicas, armação encorpada e lentes escuras para uso urbano. "
            "Indicado para quem busca um visual versátil, confortável e fácil de combinar no dia a dia."
        ),
        "category": "Solares",
        "stock": 12
    },
    {
        "id": 7,
        "name": "Solar Wayfarer Vinho",
        "price": 329.90,
        "image": "solar-wayfarer-vinho.jpg",
        "short_description": "Modelo wayfarer em tom vinho com lentes degradê.",
        "description": (
            "Óculos solar com armação em tom vinho e lentes degradê, ideal para quem prefere um acessório "
            "marcante sem abrir mão da elegância. Formato clássico com presença moderna."
        ),
        "category": "Solares",
        "stock": 9
    },
    {
        "id": 8,
        "name": "Solar Wayfarer Azul",
        "price": 319.90,
        "image": "solar-wayfarer-azul.jpg",
        "short_description": "Óculos solar azul com visual casual e lentes escuras.",
        "description": (
            "Armação azul de perfil casual, lentes escuras e desenho quadrado inspirado nos modelos wayfarer. "
            "Uma opção leve e descontraída para compor looks de lazer e rotina."
        ),
        "category": "Solares",
        "stock": 8
    },
    {
        "id": 9,
        "name": "Armação Retangular Vinho",
        "price": 289.90,
        "image": "armacao-retangular-vinho.jpg",
        "short_description": "Armação retangular em tom vinho para lentes de grau.",
        "description": (
            "Armação de grau com formato retangular e acabamento vinho translúcido. "
            "Combina estrutura discreta, boa área de lente e personalidade para uso profissional ou cotidiano."
        ),
        "category": "Armações",
        "stock": 7
    },
    {
        "id": 10,
        "name": "Armação Retangular Preta Fina",
        "price": 259.90,
        "image": "armacao-retangular-preta-fina.jpg",
        "short_description": "Armação preta leve com desenho retangular discreto.",
        "description": (
            "Modelo de grau com aro fino, formato retangular e acabamento preto. "
            "Indicado para quem busca uma armação discreta, funcional e confortável para longos períodos."
        ),
        "category": "Armações",
        "stock": 11
    },
    {
        "id": 11,
        "name": "Armação Metal Dourada",
        "price": 299.90,
        "image": "armacao-metal-dourada.jpg",
        "short_description": "Armação metálica dourada com visual leve e sofisticado.",
        "description": (
            "Armação em metal dourado, estrutura fina e design minimalista. "
            "Boa escolha para lentes de grau em composições elegantes e discretas."
        ),
        "category": "Armações",
        "stock": 6
    },
    {
        "id": 12,
        "name": "Ray-Ban Meta Wayfarer - Gen 2 Preto",
        "price": 3029.90,
        "image": "armacao-retangular-preta-bold.jpg",
        "short_description": "Óculos inteligente com câmera, áudio, comandos por voz e estojo carregador.",
        "description": (
            "Ray-Ban Meta Wayfarer de segunda geração com design preto clássico, câmera integrada, "
            "áudio embutido, microfones, comandos por voz e estojo carregador Ray-Ban. "
            "Ideal para registrar momentos, ouvir música, atender chamadas e usar recursos conectados com praticidade."
        ),
        "category": "Tecnologia",
        "stock": 10
    },
    {
        "id": 13,
        "name": "Aviador Verde Clássico",
        "price": 429.90,
        "image": "aviador-verde-classico.jpg",
        "short_description": "Óculos aviador com lentes verdes e armação metálica.",
        "description": (
            "Modelo solar aviador com lentes verdes, ponte dupla e armação metálica. "
            "Um clássico para dirigir, viajar e usar em produções casuais com acabamento refinado."
        ),
        "category": "Solares",
        "stock": 9
    },
    {
        "id": 14,
        "name": "Aviador Degradê Dourado",
        "price": 459.90,
        "image": "aviador-degrade-dourado.jpg",
        "short_description": "Aviador dourado com lentes degradê para uso diário.",
        "description": (
            "Óculos solar aviador com armação dourada e lentes degradê. "
            "Entrega visual clássico com toque sofisticado para ambientes externos e direção."
        ),
        "category": "Solares",
        "stock": 8
    },
    {
        "id": 15,
        "name": "Dolce & Gabbana DG4501 501/8G",
        "price": 1199.90,
        "image": "solar-square-preto-luxo.jpg",
        "short_description": "Óculos de sol Dolce & Gabbana em acetato preto com lentes cinza degradê.",
        "description": (
            "Dolce & Gabbana DG4501 501/8G com armação em acetato preto, formato butterfly "
            "e lentes cinza degradê. Modelo feminino de presença sofisticada, com detalhe metálico "
            "DG nas hastes, calibre 54, ponte 17 mm e hastes 145 mm."
        ),
        "category": "Solares",
        "stock": 6
    },
    {
        "id": 16,
        "name": "Solar Oval Preto",
        "price": 389.90,
        "image": "solar-oval-preto.jpg",
        "short_description": "Óculos solar oval preto com perfil retrô.",
        "description": (
            "Armação oval preta com lentes escuras e inspiração retrô. "
            "Modelo compacto, estiloso e indicado para quem busca um visual diferente dos formatos tradicionais."
        ),
        "category": "Solares",
        "stock": 7
    },
    {
        "id": 17,
        "name": "Swarovski SK6005 1001/8G",
        "price": 799.90,
        "image": "solar-cat-eye-preto.jpg",
        "short_description": "Óculos de sol Swarovski preto com lentes cinza degradê.",
        "description": (
            "Swarovski SK6005 1001/8G com armação em acetato preto, formato octogonal fashion "
            "e lentes cinza degradê categoria 3. Traz acabamento elegante, brilho discreto e medidas "
            "53-20-140 para encaixe confortável."
        ),
        "category": "Solares",
        "stock": 8
    },
    {
        "id": 18,
        "name": "Solar Cat Eye Marrom",
        "price": 419.90,
        "image": "solar-cat-eye-marrom.jpg",
        "short_description": "Modelo gatinho marrom com lentes em tom quente.",
        "description": (
            "Óculos solar cat eye com acabamento marrom e lentes em tom quente. "
            "Equilibra feminilidade, estilo e proteção para uso em dias ensolarados."
        ),
        "category": "Solares",
        "stock": 7
    },
    {
        "id": 19,
        "name": "Prada SPR A51 ZVN-30C",
        "price": 1699.90,
        "image": "solar-retangular-rimless.jpg",
        "short_description": "Óculos de sol Prada em metal dourado com lentes degradê.",
        "description": (
            "Prada SPR A51 ZVN-30C com armação metálica dourada, desenho geométrico retangular "
            "e lentes cinza/azul degradê. Modelo unissex com detalhe triangular Prada nas hastes, "
            "medidas 58-17-140 e visual refinado de luxo contemporâneo."
        ),
        "category": "Solares",
        "stock": 5
    },
    {
        "id": 20,
        "name": "Solar Slim Retangular Preto",
        "price": 359.90,
        "image": "solar-slim-retangular-preto.jpg",
        "short_description": "Óculos solar slim retangular com armação preta.",
        "description": (
            "Formato retangular estreito, lentes escuras e acabamento preto. "
            "Tendência urbana para quem busca um acessório compacto, moderno e fácil de usar."
        ),
        "category": "Solares",
        "stock": 9
    },
    {
        "id": 21,
        "name": "Miu Miu SMU 04Z 19P-2Z1",
        "price": 1499.90,
        "image": "solar-round-tartaruga.jpg",
        "short_description": "Óculos Miu Miu oval em havana claro com lentes marrons.",
        "description": (
            "Miu Miu SMU 04Z 19P-2Z1 em acetato havana claro, formato oval e lentes marrons. "
            "Modelo de passarela com assinatura Miu Miu vertical nas hastes, medidas 50-18-140 "
            "e estilo sofisticado com leitura retrô."
        ),
        "category": "Solares",
        "stock": 6
    },
    {
        "id": 22,
        "name": "Miu Miu SMU A04 16K-08Z",
        "price": 1599.90,
        "image": "solar-oval-detalhe-dourado.jpg",
        "short_description": "Óculos Miu Miu cat eye preto com detalhe dourado nas hastes.",
        "description": (
            "Miu Miu SMU A04 16K-08Z com armação em acetato preto brilhante, formato cat eye/butterfly "
            "e lentes cinza escuras. O logotipo dourado nas hastes reforça a proposta fashion da peça, "
            "com medidas 54-20-140."
        ),
        "category": "Solares",
        "stock": 5
    },
    {
        "id": 23,
        "name": "Versace VE 4479-U GB1/87",
        "price": 1299.90,
        "image": "solar-square-medusa-preto.jpg",
        "short_description": "Óculos Versace quadrado preto com lentes cinza.",
        "description": (
            "Versace VE 4479-U GB1/87 com armação preta em acetato, formato quadrado e lentes cinza. "
            "Integra a linha Medusa Biggie, marcada pelo detalhe Medusa nas hastes largas, "
            "com medidas 52-19-140 e presença visual premium."
        ),
        "category": "Solares",
        "stock": 4
    },
    {
        "id": 24,
        "name": "Versace VE 4479-U 148/80",
        "price": 1299.90,
        "image": "solar-cristal-retangular.jpg",
        "short_description": "Óculos Versace cristal com lentes azuis e detalhe Medusa Biggie.",
        "description": (
            "Versace VE 4479-U 148/80 com armação cristal transparente, lentes azuis e formato quadrado. "
            "Modelo Medusa Biggie com hastes largas e assinatura lateral, medidas 52-19-140, "
            "ideal para quem busca um acessório de luxo com acabamento translúcido."
        ),
        "category": "Solares",
        "stock": 6
    }
]

PRODUCT_VARIANT_GROUPS = {
    "wayfarer-solar": {
        "label": "Wayfarer Solar",
        "products": [
            {"id": 6, "color": "Preto", "frame": "Preto", "lenses": "Escuras"},
            {"id": 7, "color": "Vinho", "frame": "Vinho", "lenses": "Degradê"},
            {"id": 8, "color": "Azul", "frame": "Azul", "lenses": "Escuras"},
        ],
    },
    "armacao-retangular": {
        "label": "Armação Retangular",
        "products": [
            {"id": 9, "color": "Vinho", "frame": "Vinho translúcido", "lenses": "Grau"},
            {"id": 10, "color": "Preto fino", "frame": "Preto", "lenses": "Grau"},
        ],
    },
    "meta-wayfarer": {
        "label": "Ray-Ban Meta Wayfarer",
        "products": [
            {"id": 3, "color": "Gen 2", "frame": "Wayfarer", "lenses": "Tecnologia inteligente"},
            {"id": 12, "color": "Preto", "frame": "Preto", "lenses": "Transparente"},
        ],
    },
    "aviador": {
        "label": "Aviador",
        "products": [
            {"id": 13, "color": "Verde", "frame": "Metal", "lenses": "Verdes"},
            {"id": 14, "color": "Dourado", "frame": "Dourado", "lenses": "Degradê"},
        ],
    },
}

PRODUCT_GALLERIES = {
    product_id: [
        {"label": "Frente", "image": f"product_gallery/produto-{product_id}-front.jpg"},
        {"label": "Lateral", "image": f"product_gallery/produto-{product_id}-side.jpg"},
        {"label": "Vista interna", "image": f"product_gallery/produto-{product_id}-back.jpg"},
    ]
    for product_id in [6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
}

PRODUCT_GALLERIES[7] = [
    {"label": "Frente", "image": "product_gallery/produto-7-front.jpg"},
    {"label": "Lateral", "image": "product_gallery/produto-7-side.jpg"},
]

PRODUCT_GALLERIES[11] = [
    {"label": "Frente", "image": "product_gallery/produto-11-front.jpg"},
    {"label": "Lateral", "image": "product_gallery/produto-11-side.jpg"},
]

PRODUCT_GALLERIES[12] = [
    {"label": "Frente", "image": "product_gallery/produto-12-front.jpg"},
    {"label": "Lateral", "image": "product_gallery/produto-12-side.jpg"},
    {"label": "Vista interna", "image": "product_gallery/produto-12-back.jpg"},
    {"label": "Estojo carregador", "image": "product_gallery/produto-12-case.jpg"},
]

COUPONS = {
    "LOJA10": {"label": "10% OFF em produtos selecionados", "percent": 10},
    "FRETEGRATIS": {"label": "Cupom demonstrativo de frete grátis", "percent": 5},
}

PRODUCT_REVIEWS = {
    1: [
        {"name": "Mariana", "rating": 5, "comment": "Ótimo para dirigir e praticar esporte. Leve e firme no rosto."},
        {"name": "Carlos", "rating": 4, "comment": "Produto bonito, chegou bem embalado e com boa qualidade."},
    ],
    2: [
        {"name": "Bianca", "rating": 5, "comment": "Limpa bem as lentes e não deixa marcas."},
    ],
    3: [
        {"name": "Rafael", "rating": 5, "comment": "A câmera e o áudio deixam o produto muito completo para o dia a dia."},
        {"name": "Ana", "rating": 4, "comment": "Gostei bastante, principalmente dos comandos por voz."},
    ],
    4: [
        {"name": "Lucas", "rating": 4, "comment": "Modelo clássico, confortável e combina com tudo."},
    ],
    5: [
        {"name": "Fernanda", "rating": 5, "comment": "Prático para carregar na bolsa e limpar rapidamente."},
    ],
    6: [{"name": "Bruno", "rating": 5, "comment": "Modelo clássico, firme no rosto e combina com tudo."}],
    7: [{"name": "Patrícia", "rating": 4, "comment": "A cor vinho é bonita e a lente degradê deixa o visual elegante."}],
    8: [{"name": "Gustavo", "rating": 4, "comment": "Ótimo para uso casual, bem leve e diferente dos modelos comuns."}],
    9: [{"name": "Camila", "rating": 5, "comment": "Armação confortável e com uma cor discreta, mas cheia de estilo."}],
    10: [{"name": "Eduardo", "rating": 4, "comment": "Leve para trabalhar o dia todo e não pesa no rosto."}],
    11: [{"name": "Helena", "rating": 5, "comment": "Acabamento delicado e elegante, ficou muito bom com lente de grau."}],
    12: [{"name": "Diego", "rating": 5, "comment": "O estojo carregador é prático e os recursos inteligentes deixam o óculos muito completo."}],
    13: [{"name": "Renato", "rating": 5, "comment": "Aviador clássico, confortável para dirigir e usar no dia a dia."}],
    14: [{"name": "Juliana", "rating": 4, "comment": "As lentes degradê são bonitas e deixam o modelo sofisticado."}],
    15: [{"name": "Larissa", "rating": 5, "comment": "Óculos marcante, acabamento bonito e lente ampla."}],
    16: [{"name": "Sofia", "rating": 4, "comment": "Formato oval estiloso, gostei bastante do visual retrô."}],
    17: [{"name": "Vanessa", "rating": 5, "comment": "Modelo gatinho elegante e muito bonito no rosto."}],
    18: [{"name": "Aline", "rating": 5, "comment": "O tom marrom é sofisticado e combina bem com vários looks."}],
    19: [{"name": "Marcelo", "rating": 4, "comment": "Bem leve por ser sem aro e com visual moderno."}],
    20: [{"name": "Thiago", "rating": 4, "comment": "Modelo compacto e atual, excelente para um visual urbano."}],
    21: [{"name": "Isabela", "rating": 5, "comment": "A estampa tartaruga deixou o óculos muito charmoso."}],
    22: [{"name": "Priscila", "rating": 5, "comment": "Os detalhes dourados fazem diferença no acabamento."}],
    23: [{"name": "Maurício", "rating": 5, "comment": "Visual premium, armação robusta e muito estilosa."}],
    24: [{"name": "Natália", "rating": 4, "comment": "A armação transparente é leve visualmente e combina com tudo."}],
}


def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


def get_favorites():
    if "favorites" not in session:
        session["favorites"] = []
    return session["favorites"]


def get_session_reviews():
    return session.get("reviews", {})


def get_product_reviews(product_id):
    reviews = list(PRODUCT_REVIEWS.get(product_id, []))
    session_reviews = get_session_reviews().get(str(product_id), [])
    reviews.extend(session_reviews)
    return reviews


def get_review_summary(product_id):
    reviews = get_product_reviews(product_id)
    if not reviews:
        return {"average": 0, "count": 0}

    average = sum(review["rating"] for review in reviews) / len(reviews)
    return {"average": round(average, 1), "count": len(reviews)}


def enrich_products_with_reviews(products):
    enriched = []
    for product in products:
        product_with_reviews = product.copy()
        product_with_reviews["review_summary"] = get_review_summary(product["id"])
        variants = get_product_variants(product["id"])
        product_with_reviews["variant_count"] = len(variants)
        product_with_reviews["variant_swatches"] = variants[:4]
        enriched.append(product_with_reviews)
    return enriched


def get_product_by_id(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def get_product_variant_group(product_id):
    for group_key, group in PRODUCT_VARIANT_GROUPS.items():
        if any(variant["id"] == product_id for variant in group["products"]):
            return group_key, group
    return None, None


def get_product_variants(product_id):
    _, group = get_product_variant_group(product_id)
    if not group:
        return []

    variants = []
    for variant in group["products"]:
        variant_product = get_product_by_id(variant["id"])
        if variant_product:
            variants.append({
                **variant,
                "name": variant_product["name"],
                "image": variant_product["image"],
                "price": variant_product["price"],
                "stock": variant_product["stock"],
                "active": variant_product["id"] == product_id,
            })
    return variants


def get_product_gallery(product):
    gallery = PRODUCT_GALLERIES.get(product["id"])
    if gallery:
        return gallery
    return [{"label": "Produto", "image": product["image"]}]


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
                "category": product["category"],
                "stock": product["stock"]
            })
            total += subtotal

    return cart_items, total


def cart_has_stock(cart_items):
    for item in cart_items:
        if item["quantity"] > item["stock"]:
            return False, item["name"]
    return True, None


def format_currency(value):
    return f"R$ {value:.2f}".replace(".", ",")


def get_coupon_discount(total):
    coupon_code = session.get("coupon_code")
    coupon = COUPONS.get(coupon_code)

    if not coupon:
        return 0, None

    discount = round(total * (coupon["percent"] / 100), 2)
    return discount, {"code": coupon_code, **coupon}


@app.context_processor
def inject_cart_drawer():
    mini_cart_items, mini_cart_total = calculate_cart_details()
    mini_coupon_discount, mini_active_coupon = get_coupon_discount(mini_cart_total)
    return {
        "mini_cart_items": mini_cart_items,
        "mini_cart_total": mini_cart_total,
        "mini_cart_final_total": max(mini_cart_total - mini_coupon_discount, 0),
        "mini_active_coupon": mini_active_coupon,
        "show_cart_drawer": session.pop("cart_drawer_open", False),
    }


def build_cart_payload(message=None):
    cart_items, total = calculate_cart_details()
    coupon_discount, active_coupon = get_coupon_discount(total)
    final_total = max(total - coupon_discount, 0)

    return {
        "message": message,
        "count": sum(session.get("cart", {}).values()),
        "items": cart_items,
        "subtotal": total,
        "subtotal_formatted": format_currency(total),
        "final_total": final_total,
        "final_total_formatted": format_currency(final_total),
        "active_coupon": active_coupon,
        "coupon_discount": coupon_discount,
    }


def generate_fake_barcode():
    blocks = [
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000000000, 99999999999))
    ]
    return " ".join(blocks)


def generate_order_number():
    while True:
        order_number = str(random.randint(100000, 999999))
        if not Order.query.filter_by(order_number=order_number).first():
            return order_number


def redirect_after_login(default_endpoint="index"):
    next_page = request.args.get("next") or session.pop("next_page", None)
    if next_page and next_page.startswith("/"):
        return redirect(next_page)
    return redirect(url_for(default_endpoint))


def login_user(user):
    session["user_id"] = user.id
    session["user_name"] = user.name


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def user_checkout_defaults(user):
    if not user:
        return {}

    return {
        "customer_name": user.name or "",
        "customer_email": user.email or "",
        "cep": user.cep or "",
        "rua": user.rua or "",
        "numero": user.numero or "",
        "bairro": user.bairro or "",
        "cidade": user.cidade or "",
        "estado": user.estado or "",
        "complemento": user.complemento or "",
        "preferred_payment": user.preferred_payment or "cartao",
        "card_flag": user.card_flag or "",
        "card_name": user.card_name or "",
        "card_expiry": user.card_expiry or "",
        "card_number_masked": f"**** **** **** {user.card_last4}" if user.card_last4 else "",
    }


def get_categories():
    return sorted(list(set(product["category"] for product in PRODUCTS)))


def get_favorite_products():
    favorite_ids = set(get_favorites())
    return [product for product in PRODUCTS if product["id"] in favorite_ids]


@app.route("/")
def index():
    cart = get_cart()
    cart_count = sum(cart.values())
    categories = get_categories()

    selected_category = request.args.get("category", "").strip()
    search_query = request.args.get("q", "").strip()

    if selected_category:
        filtered_products = [
            product for product in PRODUCTS
            if product["category"].lower() == selected_category.lower()
        ]
    else:
        filtered_products = PRODUCTS

    if search_query:
        search_lower = search_query.lower()
        filtered_products = [
            product for product in filtered_products
            if search_lower in product["name"].lower()
            or search_lower in product["short_description"].lower()
            or search_lower in product["description"].lower()
            or search_lower in product["category"].lower()
        ]

    spotlight_product = max(PRODUCTS, key=lambda product: product["price"]).copy()
    spotlight_product["review_summary"] = get_review_summary(spotlight_product["id"])
    deal_products = enrich_products_with_reviews(sorted(PRODUCTS, key=lambda product: product["price"], reverse=True)[:3])

    return render_template(
        "index.html",
        products=enrich_products_with_reviews(filtered_products),
        all_products=PRODUCTS,
        spotlight_product=spotlight_product,
        deal_products=deal_products,
        categories=categories,
        cart_count=cart_count,
        current_category=selected_category,
        search_query=search_query,
        favorites=get_favorites()
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
    favorites = get_favorites()
    reviews = get_product_reviews(product_id)
    review_summary = get_review_summary(product_id)
    variant_group_key, variant_group = get_product_variant_group(product_id)
    variants = get_product_variants(product_id)
    active_variant = next((variant for variant in variants if variant["active"]), None)
    gallery = get_product_gallery(product)

    return render_template(
        "product_detail.html",
        product=product,
        cart_count=cart_count,
        favorites=favorites,
        reviews=reviews,
        review_summary=review_summary,
        variant_group=variant_group,
        variant_group_key=variant_group_key,
        variants=variants,
        active_variant=active_variant,
        gallery=gallery
    )


@app.route("/product/<int:product_id>/review", methods=["POST"])
def add_review(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    name = request.form.get("name", "").strip() or session.get("user_name", "Cliente")
    comment = request.form.get("comment", "").strip()

    try:
        rating = int(request.form.get("rating", "5"))
    except ValueError:
        rating = 5

    rating = max(1, min(rating, 5))

    if not comment:
        flash("Escreva um comentário para enviar sua avaliação.", "error")
        return redirect(url_for("product_detail", product_id=product_id))

    reviews = get_session_reviews()
    product_reviews = reviews.get(str(product_id), [])
    product_reviews.append({"name": name, "rating": rating, "comment": comment})
    reviews[str(product_id)] = product_reviews
    session["reviews"] = reviews

    flash("Avaliação publicada com sucesso.", "success")
    return redirect(url_for("product_detail", product_id=product_id))


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = get_product_by_id(product_id)

    if not product:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Produto não encontrado."}), 404
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    if product["stock"] <= 0:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Produto indisponível no estoque."}), 400
        flash("Produto indisponível no estoque.", "error")
        return redirect(request.referrer or url_for("index"))

    cart = get_cart()
    product_id_str = str(product_id)
    current_quantity = cart.get(product_id_str, 0)

    if current_quantity >= product["stock"]:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "Quantidade máxima em estoque já está no carrinho."}), 400
        flash("Quantidade máxima em estoque já está no carrinho.", "error")
        return redirect(request.referrer or url_for("index"))

    cart[product_id_str] = current_quantity + 1

    session["cart"] = cart
    session["cart_drawer_open"] = True
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(build_cart_payload(f"{product['name']} foi adicionado ao carrinho."))
    flash(f"{product['name']} foi adicionado ao carrinho.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/buy_now/<int:product_id>")
def buy_now(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    if product["stock"] <= 0:
        flash("Produto indisponível no estoque.", "error")
        return redirect(url_for("index"))

    session["cart"] = {str(product_id): 1}
    flash(f"{product['name']} foi adicionado para compra imediata.", "success")
    return redirect(url_for("address"))


@app.route("/toggle_favorite/<int:product_id>")
def toggle_favorite(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    favorites = get_favorites()

    if product_id in favorites:
        favorites.remove(product_id)
        flash(f"{product['name']} foi removido dos favoritos.", "success")
    else:
        favorites.append(product_id)
        flash(f"{product['name']} foi adicionado aos favoritos.", "success")

    session["favorites"] = favorites
    return redirect(request.referrer or url_for("favorites"))


@app.route("/favorites")
def favorites():
    cart_count = sum(session.get("cart", {}).values())
    favorite_products = get_favorite_products()
    return render_template(
        "favorites.html",
        cart_count=cart_count,
        products=favorite_products,
        favorites=get_favorites()
    )


@app.route("/cart")
def cart():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())
    coupon_discount, active_coupon = get_coupon_discount(total)
    final_total = max(total - coupon_discount, 0)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        coupon_discount=coupon_discount,
        active_coupon=active_coupon,
        final_total=final_total,
        cart_count=cart_count
    )


@app.route("/apply_coupon", methods=["POST"])
def apply_coupon():
    coupon_code = request.form.get("coupon_code", "").strip().upper()

    if not coupon_code:
        session.pop("coupon_code", None)
        flash("Cupom removido.", "success")
        return redirect(url_for("cart"))

    if coupon_code not in COUPONS:
        flash("Cupom inválido. Tente LOJA10 para demonstração.", "error")
        return redirect(url_for("cart"))

    session["coupon_code"] = coupon_code
    flash(f"Cupom {coupon_code} aplicado com sucesso.", "success")
    return redirect(url_for("cart"))


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
                    product = get_product_by_id(int(product_id))
                    if product:
                        cart[product_id] = min(quantity, product["stock"])
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
@login_required
def checkout():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    has_stock, product_name = cart_has_stock(cart_items)
    if not has_stock:
        flash(f"A quantidade de {product_name} excede o estoque disponível.", "error")
        return redirect(url_for("cart"))

    return render_template(
        "address.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


@app.route("/address", methods=["GET", "POST"])
@login_required
def address():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())
    user = get_current_user()

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    has_stock, product_name = cart_has_stock(cart_items)
    if not has_stock:
        flash(f"A quantidade de {product_name} excede o estoque disponível.", "error")
        return redirect(url_for("cart"))

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
            "complemento": request.form.get("complemento", "").strip(),
            "save_address": bool(request.form.get("save_address"))
        }
        if request.form.get("save_address") and user:
            user.cep = session["checkout_data"]["cep"]
            user.rua = session["checkout_data"]["rua"]
            user.numero = session["checkout_data"]["numero"]
            user.bairro = session["checkout_data"]["bairro"]
            user.cidade = session["checkout_data"]["cidade"]
            user.estado = session["checkout_data"]["estado"]
            user.complemento = session["checkout_data"]["complemento"]
            db.session.commit()
            flash("Endereço salvo no perfil para próximas compras.", "success")
        return redirect(url_for("shipping"))

    return render_template(
        "address.html",
        cart_count=cart_count,
        checkout_defaults=user_checkout_defaults(user),
        current_step="address"
    )



@app.route("/shipping", methods=["GET", "POST"])
@login_required
def shipping():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())
    coupon_discount, active_coupon = get_coupon_discount(total)
    discounted_total = max(total - coupon_discount, 0)

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    has_stock, product_name = cart_has_stock(cart_items)
    if not has_stock:
        flash(f"A quantidade de {product_name} excede o estoque disponível.", "error")
        return redirect(url_for("cart"))

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
        total=discounted_total,
        coupon_discount=coupon_discount,
        active_coupon=active_coupon,
        cart_count=cart_count,
        current_step="shipping"
    )

@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    cart_items, total = calculate_cart_details()
    cart_count = sum(session.get("cart", {}).values())
    user = get_current_user()

    if not cart_items:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    has_stock, product_name = cart_has_stock(cart_items)
    if not has_stock:
        flash(f"A quantidade de {product_name} excede o estoque disponível.", "error")
        return redirect(url_for("cart"))

    checkout_data = session.get("checkout_data", {})

    if not checkout_data:
        flash("Preencha o endereço antes de continuar.", "error")
        return redirect(url_for("address"))

    shipping_price = checkout_data.get("shipping_price", 0)
    coupon_discount, active_coupon = get_coupon_discount(total)
    discounted_total = max(total - coupon_discount, 0)

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

        order_number = generate_order_number()
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
            saved_last4 = user.card_last4 if user else None
            using_saved_card = saved_last4 and card_number.strip().endswith(saved_last4)

            if not all([card_flag, card_number, card_name, card_expiry, card_cvv, installments]):
                flash("Preencha todos os dados do cartão.", "error")
                return redirect(url_for("payment"))

            only_digits_card = "".join(filter(str.isdigit, card_number))
            only_digits_cvv = "".join(filter(str.isdigit, card_cvv))

            if not using_saved_card and len(only_digits_card) != 16:
                flash("Número do cartão inválido. Digite 16 números.", "error")
                return redirect(url_for("payment"))

            if len(only_digits_cvv) not in [3, 4]:
                flash("CVV inválido.", "error")
                return redirect(url_for("payment"))

            payment_data.update({
                "card_flag": card_flag,
                "card_number_masked": "**** **** **** " + (saved_last4 if using_saved_card else only_digits_card[-4:]),
                "installments": installments,
                "status": "Pagamento aprovado"
            })

            if request.form.get("save_card") and user:
                user.preferred_payment = "cartao"
                user.card_flag = card_flag
                user.card_name = card_name
                user.card_expiry = card_expiry
                user.card_last4 = saved_last4 if using_saved_card else only_digits_card[-4:]
                db.session.commit()

        elif payment_method == "boleto":
            if request.form.get("save_payment") and user:
                user.preferred_payment = "boleto"
                db.session.commit()

            payment_data.update({
                "barcode": generate_fake_barcode(),
                "status": "Boleto gerado com sucesso (simulado)",
                "due_date": due_date,
                "beneficiary": "LojaFácil Comércio Virtual Ltda."
            })

        else:
            flash("Forma de pagamento inválida.", "error")
            return redirect(url_for("payment"))

        user_id = session.get("user_id")
        order_record = Order(
            user_id=user_id,
            order_number=order_number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            shipping_type=checkout_data.get("shipping_type", "Padrao"),
            shipping_price=shipping_price,
            payment_method=payment_method,
            payment_status=payment_data["status"],
            total=discounted_total + shipping_price
        )

        for item in cart_items:
            order_record.items.append(OrderItem(
                product_name=item["name"],
                product_category=item["category"],
                unit_price=item["price"],
                quantity=item["quantity"],
                subtotal=item["subtotal"]
            ))

        db.session.add(order_record)
        db.session.commit()

        order = {
            "order_number": order_number,
            "order_date": order_date,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_address": customer_address,
            "customer_zipcode": cep,
            "items": cart_items,
            "total": discounted_total + shipping_price,
            "coupon": active_coupon,
            "coupon_discount": coupon_discount,
            "payment": payment_data,
            "shipping_type": checkout_data.get("shipping_type", "Padrao"),
            "shipping_price": shipping_price
        }

        session["cart"] = {}
        session.pop("checkout_data", None)
        session.pop("coupon_code", None)

        return render_template(
            "success.html",
            order=order,
            cart_count=0,
            current_step="success"
        )

    return render_template(
        "payment.html",
        cart_items=cart_items,
        total=discounted_total,
        coupon_discount=coupon_discount,
        active_coupon=active_coupon,
        checkout_defaults=user_checkout_defaults(user),
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
    next_url = request.args.get("next", "")
    checkout_paths = {"/address", "/shipping", "/payment", "/checkout"}
    is_checkout_login = next_url in checkout_paths

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

        login_user(user)

        flash(f"Bem-vindo, {user.name}!", "success")
        return redirect_after_login()

    return render_template(
        "login.html",
        cart_count=cart_count,
        is_checkout_login=is_checkout_login
    )


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    cart_count = sum(session.get("cart", {}).values())

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Informe o e-mail cadastrado.", "error")
            return redirect(url_for("forgot_password"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Não encontramos uma conta com esse e-mail.", "error")
            return redirect(url_for("forgot_password"))

        token = secrets.token_urlsafe(24)
        session["password_reset_token"] = token
        session["password_reset_email"] = email

        flash("Solicitação validada. Redefina sua senha na próxima tela.", "success")
        return redirect(url_for("reset_password", token=token))

    return render_template("forgot_password.html", cart_count=cart_count)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    cart_count = sum(session.get("cart", {}).values())
    saved_token = session.get("password_reset_token")
    email = session.get("password_reset_email")

    if not saved_token or token != saved_token or not email:
        flash("Link de recuperação inválido ou expirado.", "error")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not password or not confirm_password:
            flash("Preencha a nova senha e a confirmação.", "error")
            return redirect(url_for("reset_password", token=token))

        if len(password) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "error")
            return redirect(url_for("reset_password", token=token))

        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("reset_password", token=token))

        user.password = generate_password_hash(password)
        db.session.commit()
        session.pop("password_reset_token", None)
        session.pop("password_reset_email", None)

        flash("Senha redefinida com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", cart_count=cart_count, email=email)


@app.route("/login/google-disabled")
def login_google():
    email = "cliente.google@lojafacil.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            name="Cliente Google",
            email=email,
            password=generate_password_hash(secrets.token_urlsafe(16))
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Login com Google realizado em modo demonstração.", "success")
    return redirect_after_login()


@app.route("/login/facebook-disabled")
def login_facebook():
    email = "cliente.facebook@lojafacil.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            name="Cliente Facebook",
            email=email,
            password=generate_password_hash(secrets.token_urlsafe(16))
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Login com Facebook realizado em modo demonstração.", "success")
    return redirect_after_login()


@app.route("/terms")
@app.route("/termos")
def terms():
    cart_count = sum(session.get("cart", {}).values())
    return render_template("terms.html", cart_count=cart_count)


@app.route("/privacy")
@app.route("/privacidade")
def privacy():
    cart_count = sum(session.get("cart", {}).values())
    return render_template("privacy.html", cart_count=cart_count)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("index"))



@app.route("/profile")
@login_required
def profile():
    cart_count = sum(session.get("cart", {}).values())
    user = User.query.get(session["user_id"])
    user_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    total_spent = sum(order.total for order in user_orders)
    favorite_products = get_favorite_products()
    return render_template(
        "profile.html",
        cart_count=cart_count,
        user=user,
        orders=user_orders,
        favorite_products=favorite_products,
        total_spent=total_spent,
        format_currency=format_currency
    )


@app.route("/profile/preferences", methods=["POST"])
@login_required
def update_profile_preferences():
    user = get_current_user()

    user.phone = request.form.get("phone", "").strip()
    user.cep = request.form.get("cep", "").strip()
    user.rua = request.form.get("rua", "").strip()
    user.numero = request.form.get("numero", "").strip()
    user.bairro = request.form.get("bairro", "").strip()
    user.cidade = request.form.get("cidade", "").strip()
    user.estado = request.form.get("estado", "").strip()
    user.complemento = request.form.get("complemento", "").strip()

    db.session.commit()
    flash("Dados pessoais e endereço salvos com sucesso.", "success")
    return redirect(url_for("profile"))

@app.route("/orders")
@login_required
def orders():
    cart_count = sum(session.get("cart", {}).values())
    user_orders = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.created_at.desc()).all()
    return render_template(
        "orders.html",
        cart_count=cart_count,
        orders=user_orders,
        format_currency=format_currency
    )


with app.app_context():
    db.create_all()
    user_columns = {column["name"] for column in db.inspect(db.engine).get_columns("user")}
    profile_columns = {
        "phone": "VARCHAR(30)",
        "cep": "VARCHAR(12)",
        "rua": "VARCHAR(160)",
        "numero": "VARCHAR(30)",
        "bairro": "VARCHAR(100)",
        "cidade": "VARCHAR(100)",
        "estado": "VARCHAR(40)",
        "complemento": "VARCHAR(160)",
        "preferred_payment": "VARCHAR(30)",
        "card_flag": "VARCHAR(30)",
        "card_last4": "VARCHAR(4)",
        "card_name": "VARCHAR(120)",
        "card_expiry": "VARCHAR(5)",
    }
    for column_name, column_type in profile_columns.items():
        if column_name not in user_columns:
            db.session.execute(db.text(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"))
    db.session.commit()




if __name__ == "__main__":
    app.run(debug=True)


    
