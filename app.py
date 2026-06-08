from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from extensions import db
from flask import Flask, jsonify, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
import random
import secrets
import smtplib

app = Flask(__name__)
app.config.from_object(Config)
STORE_NAME = "VistaPrime Ótica"
STORE_LEGAL_NAME = "VistaPrime Ótica Ltda."
STORE_EMAIL = "atendimento@vistaprime.com.br"

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
        "price": 23.90,
        "image": "lencomagico.png",
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
        "price": 3299.90,
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
        "price": 89.90,
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
        "price": 999.90,
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
        "price": 899.90,
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
        "price": 899.90,
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
        "price": 329.90,
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
        "price": 329.90,
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
        "price": 349.90,
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
        "price": 3299.90,
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
        "price": 899.90,
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
        "price": 949.90,
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
        "price": 1699.90,
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
        "price": 1110.00,
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
        "price": 1290.00,
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
        "price": 1290.00,
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
        "price": 2399.90,
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
        "price": 2199.90,
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
        "price": 2299.90,
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
        "price": 2599.90,
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
        "price": 1289.90,
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
        "price": 1289.90,
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

PRODUCTS = [product for product in PRODUCTS if product["id"] != 1]

PRODUCT_VARIANT_GROUPS = {
    "wayfarer-solar": {
        "label": "Wayfarer Solar",
        "products": [
            {"id": 6, "color": "Preto", "frame": "Preto", "lenses": "Escuras"},
            {"id": 7, "color": "Vinho", "frame": "Vinho", "lenses": "Degradê"},
            {"id": 8, "color": "Azul", "frame": "Azul", "lenses": "Escuras"},
        ],
    },
    "tigor-vtt152": {
        "label": "Tigor T. Tigre VTT152",
        "products": [
            {"id": 10, "color": "Azul", "frame": "Azul bic", "lenses": "Apresentação"},
            {"id": 11, "color": "Dourado", "frame": "Dourado", "lenses": "Apresentação"},
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
        "label": "Ray-Ban Aviator Classic",
        "products": [
            {"id": 4, "color": "Dourado-arista", "frame": "Polido Dourado-arista", "lenses": "Verde G-15"},
            {"id": 13, "color": "Verde G-15", "frame": "Metal dourado", "lenses": "Verde G-15"},
            {"id": 14, "color": "Degradê dourado", "frame": "Dourado", "lenses": "Degradê"},
        ],
    },
    "swarovski-sk6047": {
        "label": "Swarovski SK6047",
        "products": [
            {"id": 17, "color": "Preto", "frame": "Preto", "lenses": "Cinza degradê"},
            {"id": 18, "color": "Marrom", "frame": "Marrom", "lenses": "Marrom degradê"},
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

PRODUCT_GALLERIES[2] = [
    {"label": "Cores variadas", "image": "lencomagico.png"},
    {"label": "Opções de cor", "image": "lencomagico2.png"},
    {"label": "Flanela individual", "image": "lencomagico3.png"},
]

PRODUCT_OPTICAL_SPECS = {
    1: {"lens_type": "Solar esportivo", "frame_color": "Preto", "lens_color": "Cinza Prizm", "measurements": "Ajuste esportivo XL"},
    2: {"lens_type": "Acessório de limpeza", "frame_color": "Não se aplica", "lens_color": "Não se aplica", "measurements": "Flanela reutilizável"},
    3: {"lens_type": "RX compatível / tecnologia", "frame_color": "Preto", "lens_color": "Transparente", "measurements": "53-22"},
    4: {"lens_type": "Solar", "frame_color": "Metal dourado", "lens_color": "Verde clássica", "measurements": "62-14"},
    5: {"lens_type": "Acessório de limpeza", "frame_color": "Não se aplica", "lens_color": "Não se aplica", "measurements": "Lenços individuais"},
    6: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza escura", "measurements": "Wayfarer padrão"},
    7: {"lens_type": "Solar", "frame_color": "Vinho", "lens_color": "Degradê", "measurements": "Wayfarer padrão"},
    8: {"lens_type": "Solar", "frame_color": "Azul", "lens_color": "Cinza escura", "measurements": "Wayfarer padrão"},
    9: {"lens_type": "RX / receituário", "frame_color": "Vinho translúcido", "lens_color": "Demo transparente", "measurements": "Retangular padrão"},
    10: {"lens_type": "RX / receituário", "frame_color": "Preto", "lens_color": "Demo transparente", "measurements": "Retangular fino"},
    11: {"lens_type": "RX / receituário", "frame_color": "Metal dourado", "lens_color": "Demo transparente", "measurements": "Metal leve"},
    12: {"lens_type": "RX compatível / tecnologia", "frame_color": "Preto fosco", "lens_color": "Transparente", "measurements": "53-22"},
    13: {"lens_type": "Solar", "frame_color": "Metal dourado", "lens_color": "Verde", "measurements": "Aviador padrão"},
    14: {"lens_type": "Solar", "frame_color": "Dourado", "lens_color": "Degradê marrom", "measurements": "Aviador padrão"},
    15: {"lens_type": "Solar", "frame_color": "Acetato preto", "lens_color": "Cinza degradê", "measurements": "54-17-145"},
    16: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza escura", "measurements": "Oval padrão"},
    17: {"lens_type": "Solar", "frame_color": "Acetato preto", "lens_color": "Cinza degradê", "measurements": "53-20-140"},
    18: {"lens_type": "Solar", "frame_color": "Marrom", "lens_color": "Marrom quente", "measurements": "Cat eye padrão"},
    19: {"lens_type": "Solar", "frame_color": "Metal dourado", "lens_color": "Cinza/azul degradê", "measurements": "58-17-140"},
    20: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza escura", "measurements": "Retangular slim"},
    21: {"lens_type": "Solar", "frame_color": "Havana claro", "lens_color": "Marrom", "measurements": "50-18-140"},
    22: {"lens_type": "Solar", "frame_color": "Preto brilhante", "lens_color": "Cinza escura", "measurements": "54-20-140"},
    23: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza", "measurements": "52-19-140"},
    24: {"lens_type": "Solar", "frame_color": "Cristal transparente", "lens_color": "Azul", "measurements": "52-19-140"},
}

PRODUCT_DETAIL_SECTIONS = {
    2: [
        {
            "title": "Características e especificações",
            "items": [
                ("Formato do item", "Tecido em microfibra"),
                ("Aroma", "Sem perfume"),
                ("Usos recomendados", "Limpeza de óculos, lentes solares, lentes de grau, celulares, tablets, câmeras e telas delicadas."),
                ("Benefícios", "Remove poeira, marcas e impressões digitais sem riscar. Produto lavável e reutilizável."),
            ],
        },
        {
            "title": "Detalhes do produto",
            "items": [
                ("Dimensões aproximadas", "15 x 15 cm"),
                ("Material", "Microfibra macia"),
                ("Quantidade", "1 unidade"),
                ("País de origem", "Brasil"),
            ],
        },
        {
            "title": "Informações de segurança",
            "items": [
                ("Uso", "Apenas uso externo"),
                ("Cuidados", "Evite contato com produtos abrasivos. Lave separadamente e deixe secar totalmente antes de reutilizar."),
            ],
        },
    ],
    5: [
        {
            "title": "Características e especificações",
            "items": [
                ("Formato do item", "Lenços umedecidos individuais"),
                ("Aroma", "Sem perfume"),
                ("Usos recomendados", "Limpeza rápida de óculos, lentes, câmeras, celulares, tablets, notebooks, monitores e superfícies delicadas."),
                ("Benefícios", "Ajuda a remover oleosidade, marcas e poeira com praticidade, sem amônia e com tecido microfino não abrasivo."),
            ],
        },
        {
            "title": "Detalhes do produto",
            "items": [
                ("Apresentação", "Sachês individuais"),
                ("Material", "Tecido microfino umedecido"),
                ("Indicação", "Uso pontual em lentes e telas"),
                ("Fabricante", "ZEISS"),
            ],
        },
        {
            "title": "Informações de segurança",
            "items": [
                ("Uso", "Apenas uso externo"),
                ("Cuidados", "Não ingerir. Evite contato com olhos e pele irritada. Mantenha fora do alcance de crianças."),
            ],
        },
    ],
    12: [
        {
            "title": "Descrição da armação",
            "items": [
                ("Código do modelo", "RW4012 601S1Z 53-22"),
                ("Formato", "Quadrado"),
                ("Cor da armação", "Fosco Preto"),
                ("Material", "Injetado"),
                ("Cor das hastes", "Preto"),
                ("Ponte e plaquetas", "Ponte alta"),
            ],
        },
        {
            "title": "Informações das lentes",
            "items": [
                ("Cor da lente", "Transparente/Cinza"),
                ("Tratamento", "Transitions"),
                ("Categoria", "3F"),
                ("Uso", "RX compatível / tecnologia"),
            ],
        },
        {
            "title": "Medidas",
            "items": [
                ("Tamanho", "53-22"),
                ("Altura da lente", "43,6 mm"),
                ("Comprimento da haste", "155 mm"),
                ("Cobertura facial", "Padrão"),
            ],
        },
        {
            "title": "Tecnologia",
            "items": [
                ("Câmera", "Fotos 3024x4032 px"),
                ("Vídeo", "Até 2203 x 2938 px a 30 fps"),
                ("Áudio", "2 alto-falantes Open Ear"),
                ("Microfones", "5 microfones"),
                ("Controle", "Toque e comando de voz"),
                ("Assistente", "Meta AI"),
            ],
        },
        {
            "title": "Bateria e conectividade",
            "items": [
                ("Bateria", "Até 8 horas por carga"),
                ("Memória", "32 GB: 500+ fotos ou 100+ vídeos de 30s"),
                ("Wi-Fi", "Wi-Fi 6E"),
                ("Bluetooth", "Bluetooth 5.3"),
                ("Compatibilidade", "iOS 14.4 / Android 10 ou superior"),
            ],
        },
    ]
}

DEFAULT_DETAIL_SECTIONS = [
    {
        "title": "Descrição da armação",
        "items": [
            ("Tipo de lente", "lens_type"),
            ("Cor da armação", "frame_color"),
            ("Cor da lente", "lens_color"),
            ("Medidas", "measurements"),
        ],
    },
    {
        "title": "Compra e uso",
        "items": [
            ("Disponibilidade", "Produto disponível para compra"),
            ("Entrega", "Frete calculado no checkout"),
            ("Garantia de atendimento", "Suporte para troca, devolução e dúvidas"),
        ],
    },
]

PRODUCT_INCLUDED_ITEMS = {
    2: [
        ("Flanela de microfibra", "Produto reutilizável para limpeza diária."),
        ("Embalagem individual", "Item protegido para transporte e armazenamento."),
        ("Suporte VistaPrime", "Atendimento para dúvidas sobre uso, troca e devolução."),
    ],
    5: [
        ("Lenços de limpeza", "Sachês individuais para limpeza rápida."),
        ("Embalagem do produto", "Proteção adequada para transporte e armazenamento."),
        ("Suporte VistaPrime", "Atendimento para dúvidas sobre uso, troca e devolução."),
    ],
    12: [
        ("Estojo carregador", "Case Ray-Ban Meta para recarga e transporte."),
        ("Flanela de limpeza", "Tecido macio para lentes e armação."),
        ("Guia rápido", "Orientações iniciais de uso e pareamento."),
    ]
}

PRODUCT_SUMMARY_SPECS = {
    2: [
        ("Tipo", "Acessório de limpeza"),
        ("Formato", "Tecido em microfibra"),
        ("Aroma", "Sem perfume"),
        ("Apresentação", "Flanela reutilizável"),
    ],
    5: [
        ("Tipo", "Acessório de limpeza"),
        ("Formato", "Lenços umedecidos"),
        ("Aroma", "Sem perfume"),
        ("Apresentação", "Sachês individuais"),
    ],
}

PRODUCT_PAGE_UPDATES = {
    4: {
        "name": "Ray-Ban Aviator Classic RB3025 W3234",
        "short_description": "Aviador clássico em metal dourado-arista com lentes Verde G-15.",
        "description": (
            "Atualmente um dos modelos de óculos de sol mais icônicos do mundo, o Ray-Ban Aviator Classic "
            "foi originalmente criado para pilotos americanos em 1937. É um modelo atemporal que combina "
            "o grande estilo aviador com qualidade, desempenho e conforto excepcionais."
        ),
    },
    5: {
        "name": "ZEISS Lens Wipes",
        "short_description": "Lenços umedecidos ZEISS para lentes, telas e superfícies de vidro.",
        "description": (
            "Solução ideal para limpeza de lentes de óculos, lentes de máquinas fotográficas, telas de "
            "computadores, tablets, smartphones e outras superfícies de vidro. Remova a poeira com o lenço "
            "dobrado, desdobre e limpe em movimentos circulares; em cerca de 10 segundos a superfície fica "
            "limpa e seca."
        ),
    },
    6: {
        "name": "Ray-Ban Original Wayfarer Classic RB2140 901/58",
        "short_description": "Wayfarer clássico preto com lentes Verde G-15 polarizadas.",
        "description": (
            "Os Ray-Ban Original Wayfarer Classics estão entre os estilos mais reconhecidos da história dos "
            "óculos de sol. Desde 1952, o modelo ganhou fama entre celebridades, músicos, artistas e pessoas "
            "com forte senso de moda. A armação preta com lente verde polarizada mantém a assinatura icônica "
            "do Wayfarer."
        ),
    },
    9: {
        "name": "Lilica Ripilica Armação Retangular Vinho",
        "short_description": "Armação infantil feminina em acetato vinho para lentes de grau.",
        "description": (
            "Armação Lilica Ripilica em acetato, formato quadrado e acabamento vinho. A marca nasceu no fim "
            "da década de 1980 e ficou conhecida por unir moda infantil, cor e personalidade em peças de uso "
            "diário."
        ),
    },
    10: {
        "name": "Tigor T. Tigre VTT152 C05 Azul",
        "short_description": "Armação infantil retangular azul em acetato para lentes graduadas.",
        "description": (
            "Tigor T. Tigre é uma grife infantil versátil e moderna. A armação VTT152 C05 tem visual azul "
            "bic com interior azul celeste, formato retangular e é recomendada para aplicação de lentes "
            "graduadas."
        ),
    },
    11: {
        "name": "Tigor T. Tigre VTT152 C05 Dourada",
        "short_description": "Variação da armação infantil Tigor T. Tigre para lentes graduadas.",
        "description": (
            "Modelo infantil da linha Tigor T. Tigre com proposta moderna para uso receituário. Mantém o "
            "formato retangular, estrutura leve e indicação para lentes graduadas."
        ),
    },
    13: {
        "name": "Ray-Ban Aviator Classic Verde G-15",
        "short_description": "Aviador em metal com lentes Verde G-15 e plaquetas ajustáveis.",
        "description": (
            "Variação do Aviator Classic com a leitura tradicional de lentes verdes, ponte dupla e estrutura "
            "metálica. Um clássico para dirigir, viajar e compor produções casuais com conforto."
        ),
    },
    14: {
        "name": "Ray-Ban Aviator Classic Degradê Dourado",
        "short_description": "Aviador clássico dourado com lentes degradê.",
        "description": (
            "Variação do Aviator Classic com armação dourada e lentes degradê. Combina o desenho piloto "
            "atemporal com uma leitura mais suave e sofisticada para uso diário."
        ),
    },
    15: {
        "description": (
            "A essência Dolce & Gabbana é artística e criativa, explorando cor, textura e autoexpressão. "
            "O DG4501 501/8G tem formato borboleta, armação preta em acetato e lentes cinza degradê, com "
            "presença sofisticada e visual moderno."
        ),
    },
    16: {
        "name": "Swarovski SK6005 1001/8G",
        "short_description": "Óculos Swarovski em acetato preto com formato irregular e lentes cinza degradê.",
        "description": (
            "Experimente o luxo do Swarovski SK6005, uma peça sofisticada para qualquer coleção. Produzido "
            "em acetato preto com formato irregular, lentes cinza degradê e detalhes de cristais na frente, "
            "o modelo combina elegância, brilho e funcionalidade para um visual cotidiano de confiança."
        ),
    },
    17: {
        "name": "Swarovski SK6047 1001/8G",
        "short_description": "Óculos Swarovski gatinho preto com lentes cinza degradê.",
        "description": (
            "Valorize seu estilo com o design requintado do Swarovski SK6047. A armação preta, adornada "
            "com cristais brilhantes da Swarovski, exala elegância atemporal. O formato gatinho e as lentes "
            "cinza degradê combinam sofisticação com presença visual marcante."
        ),
    },
    18: {
        "name": "Swarovski SK6047 Marrom",
        "short_description": "Variação marrom do Swarovski SK6047 em formato gatinho.",
        "description": (
            "Variação do Swarovski SK6047 em acabamento marrom, mantendo o formato gatinho, a proposta "
            "sofisticada e o visual feminino da linha."
        ),
    },
    19: {
        "description": (
            "Dentro do triângulo, fica o logotipo Prada, símbolo imediatamente reconhecido da marca. "
            "O PR A51S traz armação em metal ouro-pálido, formato irregular e lentes prata espelhado "
            "azul degradê para uma leitura contemporânea de luxo."
        ),
    },
    20: {
        "name": "Prada PR 14YS",
        "short_description": "Óculos Prada retangular preto com lentes cinza-escuras.",
        "description": (
            "Uma reinterpretação do novo logo triângulo Prada, com sinergia entre sofisticação e tendência. "
            "Frente em acetato retangular, lente baixa e acabamento preto para um visual icônico e contemporâneo."
        ),
    },
    21: {
        "description": (
            "O Miu Miu MU 04ZS tem formato oval em havana claro e lentes marrons. A peça adiciona elegância "
            "ao visual com charme retrô, conforto para uso diário e acabamento em acetato premium."
        ),
    },
    22: {
        "description": (
            "O Miu Miu MU A04S traz formato butterfly preto, lentes cinza-escuras e hastes metálicas com "
            "acabamento sofisticado. A silhueta inspirada nos anos 50 combina elegância vintage e presença "
            "fashion para diferentes ocasiões."
        ),
    },
    23: {
        "description": (
            "Versace VE4479 em armação preta com detalhe Medusa Biggie nas hastes. O desenho retangular, "
            "a lente cinza e a construção robusta reforçam a estética marcante da marca."
        ),
    },
    24: {
        "description": (
            "Versace VE4479-U 148/80 com armação cristal transparente, lentes azul cristal e detalhe Medusa "
            "nas hastes. Um modelo retangular de presença premium para quem busca acabamento translúcido."
        ),
    },
}

PRODUCT_OPTICAL_SPECS.update({
    4: {"lens_type": "Solar", "frame_color": "Polido Dourado-arista", "lens_color": "Verde G-15", "measurements": "55-14"},
    5: {"lens_type": "Acessório de limpeza", "frame_color": "Não se aplica", "lens_color": "Não se aplica", "measurements": "Sachês individuais"},
    6: {"lens_type": "Solar polarizado", "frame_color": "Polido Preto", "lens_color": "Verde polarizado", "measurements": "50-22"},
    9: {"lens_type": "RX / receituário", "frame_color": "Vinho", "lens_color": "Apresentação", "measurements": "51-12"},
    10: {"lens_type": "RX / receituário", "frame_color": "Azul bic com interior azul celeste", "lens_color": "Apresentação", "measurements": "49-15-130"},
    11: {"lens_type": "RX / receituário", "frame_color": "Dourado", "lens_color": "Apresentação", "measurements": "49-15-130"},
    13: {"lens_type": "Solar", "frame_color": "Metal dourado", "lens_color": "Verde G-15", "measurements": "55-14"},
    14: {"lens_type": "Solar", "frame_color": "Dourado", "lens_color": "Degradê", "measurements": "55-14"},
    15: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza degradê", "measurements": "54-17-145"},
    16: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza degradê", "measurements": "53-20"},
    17: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza degradê", "measurements": "54-17"},
    18: {"lens_type": "Solar", "frame_color": "Marrom", "lens_color": "Marrom degradê", "measurements": "54-17"},
    19: {"lens_type": "Solar", "frame_color": "Ouro-pálido", "lens_color": "Prata espelhado azul degradê", "measurements": "58-17"},
    20: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza-escuro", "measurements": "53-19"},
    21: {"lens_type": "Solar", "frame_color": "Havana claro", "lens_color": "Marrom", "measurements": "50-18"},
    22: {"lens_type": "Solar", "frame_color": "Preto brilhante", "lens_color": "Cinza escuro", "measurements": "54-20"},
    23: {"lens_type": "Solar", "frame_color": "Preto", "lens_color": "Cinza", "measurements": "52-19-140"},
    24: {"lens_type": "Solar", "frame_color": "Cristal transparente", "lens_color": "Azul cristal", "measurements": "52-19-140"},
})

PRODUCT_SUMMARY_SPECS.update({
    4: [("Armação", "Polido Dourado-arista"), ("Lentes", "Verde G-15"), ("Tamanho", "55-14"), ("Geofit", "Plaquetas ajustáveis")],
    6: [("Armação", "Polido Preto"), ("Lentes", "Verde polarizado"), ("Tamanho", "50-22"), ("Geofit", "Ponte alta")],
    7: [("Armação", "Vinho translúcido"), ("Lentes", "Marrom degradê"), ("Tamanho", "50-22"), ("Geofit", "Ponte alta")],
    8: [("Armação", "Azul cristal"), ("Lentes", "Cinza escuro"), ("Tamanho", "50-22"), ("Geofit", "Ponte alta")],
    9: [("Marca", "Lilica Ripilica"), ("Material", "Acetato"), ("Formato", "Quadrado"), ("Tamanho", "51-12")],
    10: [("Marca", "Tigor T. Tigre"), ("Modelo", "VTT152 C05"), ("Cor", "Azul bic"), ("Tamanho", "49-15-130")],
    11: [("Marca", "Tigor T. Tigre"), ("Modelo", "VTT152 C05"), ("Cor", "Dourado"), ("Tamanho", "49-15-130")],
    13: [("Armação", "Metal dourado"), ("Lentes", "Verde G-15"), ("Tamanho", "55-14"), ("Geofit", "Plaquetas ajustáveis")],
    14: [("Armação", "Dourado"), ("Lentes", "Degradê"), ("Tamanho", "55-14"), ("Geofit", "Plaquetas ajustáveis")],
    15: [("Marca", "Dolce & Gabbana"), ("Armação", "Preto"), ("Lentes", "Cinza degradê"), ("Tamanho", "54-17-145")],
    16: [("Marca", "Swarovski"), ("Armação", "Preto"), ("Lentes", "Cinza degradê"), ("Tamanho", "53-20")],
    17: [("Marca", "Swarovski"), ("Armação", "Preto"), ("Lentes", "Cinza degradê"), ("Tamanho", "54-17")],
    18: [("Marca", "Swarovski"), ("Armação", "Marrom"), ("Lentes", "Marrom degradê"), ("Tamanho", "54-17")],
    19: [("Marca", "Prada"), ("Armação", "Ouro-pálido"), ("Lentes", "Prata espelhado azul degradê"), ("Tamanho", "58-17")],
    20: [("Marca", "Prada"), ("Armação", "Preto"), ("Lentes", "Cinza-escuro"), ("Tamanho", "53-19")],
    21: [("Marca", "Miu Miu"), ("Armação", "Havana claro"), ("Lentes", "Marrom"), ("Tamanho", "50-18")],
    22: [("Marca", "Miu Miu"), ("Armação", "Preto"), ("Lentes", "Cinza escuro"), ("Tamanho", "54-20")],
    23: [("Marca", "Versace"), ("Armação", "Preto"), ("Lentes", "Cinza"), ("Tamanho", "52-19-140")],
    24: [("Marca", "Versace"), ("Armação", "Cristal transparente"), ("Lentes", "Azul cristal"), ("Tamanho", "52-19-140")],
})

PRODUCT_DETAIL_SECTIONS.update({
    4: [
        {"title": "Descrição da armação", "items": [("Código do modelo", "RB3025 W3234 55-14"), ("Formato", "Piloto"), ("Cor da armação", "Polido Dourado-arista"), ("Material", "Metal"), ("Cor da haste", "Dourado-arista")]},
        {"title": "Informações das lentes", "items": [("Cor das lentes", "Verde G-15"), ("Tratamento", "Cor uniforme"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "55-14"), ("Altura da lente", "47,5 mm"), ("Comprimento da haste", "135 mm"), ("Cobertura facial", "Padrão"), ("Geofit", "Plaquetas ajustáveis para o nariz")]},
    ],
    6: [
        {"title": "Descrição da armação", "items": [("Código do modelo", "RB2140 901/58 50-22"), ("Formato", "Quadrado"), ("Cor da armação", "Polido Preto"), ("Material", "Acetato"), ("Cor da haste", "Preto")]},
        {"title": "Informações das lentes", "items": [("Cor das lentes", "Verde polarizado"), ("Tratamento", "Cor uniforme"), ("Categoria da lente", "3P"), ("Polarizada", "Sim")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "50-22"), ("Altura da lente", "41 mm"), ("Comprimento da haste", "150 mm"), ("Cobertura facial", "Padrão"), ("Geofit", "Ajuste para ponte alta")]},
    ],
    9: [
        {"title": "Características do produto", "items": [("Marca", "Lilica Ripilica"), ("Gênero", "Feminino"), ("Material", "Acetato"), ("Formato", "Quadrado"), ("Tipo de produto", "Armação vista")]},
        {"title": "Medidas", "items": [("Horizontal", "51"), ("Ponte", "12"), ("Vertical", "48"), ("Lente", "Apresentação")]},
    ],
    10: [
        {"title": "Características principais", "items": [("Marca", "Tigor T. Tigre"), ("Linha", "Receituário"), ("Modelo", "VTT152 C05"), ("Material", "Acetato"), ("Gênero", "Masculino"), ("Forma", "Retangular")]},
        {"title": "Detalhes e medidas", "items": [("Cor frontal", "Azul bic com interior azul celeste"), ("Cor da haste", "Azul bic com interior azul celeste"), ("Apoio nasal", "Sem plaqueta"), ("Lentes graduadas", "Sim"), ("Tamanho", "49"), ("Ponte", "15"), ("Haste", "130")]},
    ],
    11: [
        {"title": "Características principais", "items": [("Marca", "Tigor T. Tigre"), ("Linha", "Receituário"), ("Modelo", "VTT152 C05"), ("Material", "Acetato"), ("Forma", "Retangular")]},
        {"title": "Detalhes e medidas", "items": [("Cor frontal", "Dourado"), ("Lente", "Apresentação"), ("Apoio nasal", "Sem plaqueta"), ("Lentes graduadas", "Sim"), ("Tamanho", "49"), ("Ponte", "15"), ("Haste", "130")]},
    ],
    13: [
        {"title": "Descrição da armação", "items": [("Código do modelo", "RB3025 55-14"), ("Formato", "Piloto"), ("Cor da armação", "Metal dourado"), ("Material", "Metal"), ("Geofit", "Plaquetas ajustáveis")]},
        {"title": "Informações das lentes", "items": [("Cor das lentes", "Verde G-15"), ("Tratamento", "Cor uniforme"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "55-14"), ("Altura da lente", "47,5 mm"), ("Comprimento da haste", "135 mm"), ("Cobertura facial", "Padrão")]},
    ],
    14: [
        {"title": "Descrição da armação", "items": [("Código do modelo", "RB3025 55-14"), ("Formato", "Piloto"), ("Cor da armação", "Dourado"), ("Material", "Metal"), ("Geofit", "Plaquetas ajustáveis")]},
        {"title": "Informações das lentes", "items": [("Cor das lentes", "Degradê"), ("Tratamento", "Degradê"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "55-14"), ("Altura da lente", "47,5 mm"), ("Comprimento da haste", "135 mm"), ("Cobertura facial", "Padrão")]},
    ],
    15: [
        {"title": "Características principais", "items": [("Marca", "Dolce & Gabbana"), ("Tipo de produto", "Óculos de sol"), ("Gênero", "Feminino"), ("Estilo do modelo", "Borboleta"), ("Cor da armação", "Preto"), ("Material", "Acetato")]},
        {"title": "Lentes e medidas", "items": [("Tipo de lente", "Degradê"), ("Cor da lente", "Cinza"), ("Tamanho", "54"), ("Ponte", "1,7 cm"), ("Altura da lente", "4,8 cm"), ("Largura da lente", "5,4 cm"), ("Haste", "14,5 cm"), ("Largura frontal", "13,2 cm")]},
    ],
    16: [
        {"title": "Detalhes do produto", "items": [("Estilo", "SK6005"), ("Código do modelo", "SK6005 1001/8G 53-20"), ("Indicação", "Não indicado para direção e uso em estrada")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Preto"), ("Material", "Acetato"), ("Formato", "Irregular")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Cinza degradê"), ("Material", "Poliamida"), ("Tecnologia", "Degradê"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "S 53-20"), ("Ajuste", "Amplo"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    17: [
        {"title": "Detalhes do produto", "items": [("Estilo", "SK6047"), ("Código do modelo", "SK6047 1001/8G 54-17")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Preto"), ("Material", "Injetado"), ("Formato", "Gatinho")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Cinza degradê"), ("Material", "Poliamida"), ("Tecnologia", "Degradê"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "XS 54-17"), ("Ajuste", "Estreito"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    18: [
        {"title": "Detalhes do produto", "items": [("Estilo", "SK6047"), ("Código do modelo", "SK6047 54-17")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Marrom"), ("Material", "Injetado"), ("Formato", "Gatinho")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Marrom degradê"), ("Material", "Poliamida"), ("Tecnologia", "Degradê"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "XS 54-17"), ("Ajuste", "Estreito"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    19: [
        {"title": "Detalhes do produto", "items": [("Estilo", "PR A51S"), ("Código do modelo", "PR A51S ZVN30C 58-17"), ("Made in", "Itália")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Ouro-pálido"), ("Material", "Metal"), ("Formato", "Irregular")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Prata espelhado azul degradê"), ("Material", "Poliamida"), ("Tecnologia", "Degradê espelhado"), ("Categoria da lente", "2N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "XL 58-17"), ("Ajuste", "Estreito"), ("Ponte e plaquetas", "Plaquetas ajustáveis")]},
    ],
    20: [
        {"title": "Detalhes do produto", "items": [("Estilo", "PR 14YS"), ("Código do modelo", "PR14YS 1AB5S0 53-19"), ("Made in", "Itália")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Preto"), ("Material", "Acetato"), ("Formato", "Retangular")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Cinza-escuro"), ("Material", "Poliamida"), ("Tecnologia", "Cor uniforme"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "L 53-19"), ("Ajuste", "Padrão"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    21: [
        {"title": "Detalhes do produto", "items": [("Estilo", "MU 04ZS"), ("Código do modelo", "MU 04ZS 19P2Z1 50-18"), ("Made in", "Itália")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Havana claro"), ("Material", "Acetato"), ("Formato", "Oval")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Marrom"), ("Material", "Poliamida"), ("Tecnologia", "Cor uniforme"), ("Categoria da lente", "2N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "S 50-18"), ("Ajuste", "Estreito"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    22: [
        {"title": "Detalhes do produto", "items": [("Estilo", "MU A04S"), ("Código do modelo", "MU A04S 16K08Z 54-20"), ("Made in", "Itália")]},
        {"title": "Detalhes da armação", "items": [("Cor", "Preto"), ("Material", "Acetato"), ("Formato", "Butterfly")]},
        {"title": "Detalhes das lentes", "items": [("Cor", "Cinza escuro"), ("Material", "Poliamida Bio"), ("Tecnologia", "Cor uniforme"), ("Categoria da lente", "3N")]},
        {"title": "Tamanho e ajuste", "items": [("Tamanho", "L 54-20"), ("Ajuste", "Regular"), ("Ponte e plaquetas", "Ponte alta")]},
    ],
    23: [
        {"title": "Características principais", "items": [("Marca", "Versace"), ("Linha", "Solar"), ("Modelo", "VE4479"), ("Desenho", "Retangular"), ("Cor", "Preto"), ("Cor da lente", "Cinza")]},
        {"title": "Outros", "items": [("Modelo detalhado", "VE4479"), ("Largura da lente", "52 mm"), ("Gênero", "Sem gênero"), ("Proteção UV", "Sim"), ("Material da armação", "Injetado"), ("Material da haste", "Acetato"), ("Tamanho", "M")]},
    ],
    24: [
        {"title": "Características principais", "items": [("Marca", "Versace"), ("Linha", "Solar"), ("Modelo", "VE4479-U"), ("Desenho", "Retangular"), ("Cor", "Cristal transparente"), ("Cor da lente", "Azul cristal")]},
        {"title": "Outros", "items": [("Modelo detalhado", "VE4479-U 148/80"), ("Largura da lente", "52 mm"), ("Gênero", "Sem gênero"), ("Proteção UV", "Sim"), ("Material da armação", "Acetato"), ("Tamanho", "52/19/140")]},
    ],
})

PRODUCT_DETAIL_SECTIONS[5].append({
    "title": "Composição",
    "items": [
        ("Ingrediente ativo", "Isopropanol"),
        ("Conservantes", "Mistura MIT/CMIT 1:3 - Metil Isotiazolina/Metilcloro Isotiazolinona"),
        ("Base", "Água deionizada"),
    ],
})

for product in PRODUCTS:
    product.update(PRODUCT_PAGE_UPDATES.get(product["id"], {}))

COUPONS = {
    "VISTA10": {"label": "10% OFF em produtos selecionados", "percent": 10},
    "FRETEGRATIS": {"label": "5% de desconto em produtos selecionados", "percent": 5},
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
        product_with_reviews["optical_specs"] = get_product_optical_specs(product["id"])
        variants = get_product_variants(product["id"])
        product_with_reviews["variant_count"] = len(variants)
        product_with_reviews["variant_swatches"] = variants[:4]
        enriched.append(product_with_reviews)
    return enriched


def compact_variant_products(products):
    product_ids = {product["id"] for product in products}
    hidden_variant_ids = set()

    for group in PRODUCT_VARIANT_GROUPS.values():
        group_ids = [variant["id"] for variant in group["products"] if variant["id"] in product_ids]
        if len(group_ids) > 1:
            hidden_variant_ids.update(group_ids[1:])

    return [product for product in products if product["id"] not in hidden_variant_ids]


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


VARIANT_SECTION_BASE = {
    "meta-wayfarer": 12,
}

VARIANT_TECHNICAL_OVERRIDES = {
    3: {
        "Cor da armação": "Preto",
        "Cor das hastes": "Preto",
        "Cor da lente": "Transparente",
        "Cor das lentes": "Transparente",
    },
    7: {
        "Cor da armação": "Vinho translúcido",
        "Cor da haste": "Vinho translúcido",
        "Cor das hastes": "Vinho translúcido",
        "Cor da lente": "Marrom degradê",
        "Cor das lentes": "Marrom degradê",
    },
    8: {
        "Cor da armação": "Azul cristal",
        "Cor da haste": "Azul cristal",
        "Cor das hastes": "Azul cristal",
        "Cor da lente": "Cinza escuro",
        "Cor das lentes": "Cinza escuro",
    },
    13: {
        "Cor da armação": "Metal dourado",
        "Cor da haste": "Dourado-arista",
        "Cor das lentes": "Verde G-15",
    },
    14: {
        "Cor da armação": "Dourado",
        "Cor da haste": "Dourado",
        "Cor das lentes": "Marrom degradê",
    },
    18: {
        "Cor": "Marrom",
        "Cor da armação": "Marrom",
        "Cor da lente": "Marrom degradê",
        "Cor das lentes": "Marrom degradê",
    },
}

def get_variant_base_product_id(product_id):
    group_key, group = get_product_variant_group(product_id)
    if not group:
        return product_id
    return VARIANT_SECTION_BASE.get(group_key, group["products"][0]["id"])


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


def get_product_optical_specs(product_id):
    base_product_id = get_variant_base_product_id(product_id)
    return PRODUCT_OPTICAL_SPECS.get(product_id) or PRODUCT_OPTICAL_SPECS.get(base_product_id, {
        "lens_type": "Consultar atendimento",
        "frame_color": "Consultar atendimento",
        "lens_color": "Consultar atendimento",
        "measurements": "Consultar atendimento",
    })


def apply_variant_technical_overrides(product_id, sections):
    overrides = VARIANT_TECHNICAL_OVERRIDES.get(product_id)
    if not overrides:
        return sections

    adjusted_sections = []
    for section in sections:
        adjusted_items = []
        for label, value in section["items"]:
            adjusted_items.append((label, overrides.get(label, value)))
        adjusted_sections.append({"title": section["title"], "items": adjusted_items})
    return adjusted_sections


def get_product_detail_sections(product_id):
    if product_id in PRODUCT_DETAIL_SECTIONS:
        return apply_variant_technical_overrides(product_id, PRODUCT_DETAIL_SECTIONS[product_id])

    base_product_id = get_variant_base_product_id(product_id)
    if base_product_id != product_id and base_product_id in PRODUCT_DETAIL_SECTIONS:
        return apply_variant_technical_overrides(product_id, PRODUCT_DETAIL_SECTIONS[base_product_id])

    specs = get_product_optical_specs(product_id)
    sections = []
    for section in DEFAULT_DETAIL_SECTIONS:
        items = []
        for label, value in section["items"]:
            items.append((label, specs.get(value, value)))
        sections.append({"title": section["title"], "items": items})
    return apply_variant_technical_overrides(product_id, sections)

def get_product_included_items(product_id):
    base_product_id = get_variant_base_product_id(product_id)
    inherited_items = PRODUCT_INCLUDED_ITEMS.get(product_id) or PRODUCT_INCLUDED_ITEMS.get(base_product_id)
    if inherited_items:
        return inherited_items

    return [
        ("Produto selecionado", "Item conferido e embalado para envio."),
        ("Flanela de limpeza", "Cuidado básico para lentes e armação."),
        ("Suporte VistaPrime", "Atendimento para dúvidas sobre compra, troca e devolução."),
    ]


def get_product_summary_specs(product_id):
    if product_id in PRODUCT_SUMMARY_SPECS:
        return PRODUCT_SUMMARY_SPECS[product_id]

    base_product_id = get_variant_base_product_id(product_id)
    if base_product_id != product_id and base_product_id in PRODUCT_SUMMARY_SPECS:
        return PRODUCT_SUMMARY_SPECS[base_product_id]

    specs = get_product_optical_specs(product_id)
    return [
        ("Tipo", specs["lens_type"]),
        ("Armação", specs["frame_color"]),
        ("Lentes", specs["lens_color"]),
        ("Tamanho", specs["measurements"]),
    ]

def user_has_purchased_product(user_id, product):
    if not user_id or not product:
        return False

    return db.session.query(OrderItem.id).join(Order).filter(
        Order.user_id == user_id,
        OrderItem.product_name == product["name"],
    ).first() is not None


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


def persist_email_preview(to_email, subject, body):
    outbox_dir = Path(app.instance_path) / "email_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    safe_subject = "".join(char if char.isalnum() else "-" for char in subject.lower()).strip("-")[:42]
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe_subject or 'email'}.txt"
    message = f"Para: {to_email}\nAssunto: {subject}\n\n{body}"
    (outbox_dir / filename).write_text(message, encoding="utf-8")
    return outbox_dir / filename


def send_customer_email(to_email, subject, body):
    sender = app.config.get("MAIL_DEFAULT_SENDER") or STORE_EMAIL
    mail_server = app.config.get("MAIL_SERVER")

    if not mail_server:
        preview_path = persist_email_preview(to_email, subject, body)
        app.logger.info("E-mail salvo localmente em %s", preview_path)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(mail_server, app.config.get("MAIL_PORT", 587), timeout=12) as smtp:
            if app.config.get("MAIL_USE_TLS", True):
                smtp.starttls()
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                smtp.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            smtp.send_message(message)
        return True
    except Exception as error:
        preview_path = persist_email_preview(to_email, subject, body)
        app.logger.warning("Falha ao enviar e-mail por SMTP (%s). Preview salvo em %s", error, preview_path)
        return False


def send_welcome_email(user):
    body = f"""Olá, {user.name}!

Sua conta na {STORE_NAME} foi criada com sucesso.

Com sua conta, você pode:
- favoritar produtos;
- acompanhar seus pedidos;
- salvar endereço para compras futuras;
- receber confirmações de compra e atendimento.

E-mail cadastrado: {user.email}

Se você não realizou esse cadastro, entre em contato pelo e-mail {STORE_EMAIL}.

Atenciosamente,
Equipe {STORE_NAME}
"""
    return send_customer_email(user.email, f"Bem-vindo(a) à {STORE_NAME}", body)


def send_order_confirmation_email(order, order_items, coupon=None, coupon_discount=0):
    item_lines = []
    for item in order_items:
        item_lines.append(
            f"- {item['quantity']}x {item['name']} | {format_currency(item['price'])} cada | "
            f"Subtotal: {format_currency(item['subtotal'])}"
        )

    coupon_line = "Nenhum cupom aplicado"
    if coupon:
        coupon_line = f"{coupon['code']} ({coupon['percent']}% OFF): -{format_currency(coupon_discount)}"

    body = f"""Olá, {order.customer_name}!

Recebemos o seu pedido na {STORE_NAME}.

Pedido: {order.order_number}
Data: {order.created_at.strftime('%d/%m/%Y %H:%M')}
Status do pagamento: {order.payment_status}
Forma de pagamento: {order.payment_method.title()}
Entrega: {order.shipping_type} ({format_currency(order.shipping_price)})

Itens do pedido:
{chr(10).join(item_lines)}

Cupom/desconto: {coupon_line}
Total do pedido: {format_currency(order.total)}

Endereço de entrega:
{order.customer_address}

Você também pode acompanhar seus pedidos acessando sua conta na {STORE_NAME}.

Atenciosamente,
Equipe {STORE_NAME}
"""
    return send_customer_email(order.customer_email, f"Pedido {order.order_number} confirmado - {STORE_NAME}", body)


def validate_password_strength(password):
    requirements = [
        (len(password) >= 8, "mínimo de 8 caracteres"),
        (any(char.islower() for char in password), "uma letra minúscula"),
        (any(char.isupper() for char in password), "uma letra maiúscula"),
        (any(char.isdigit() for char in password), "um número"),
        (any(not char.isalnum() for char in password), "um caractere especial"),
    ]
    missing = [label for valid, label in requirements if not valid]
    if missing:
        return False, "A senha deve conter " + ", ".join(missing) + "."
    return True, ""


@app.context_processor
def inject_cart_drawer():
    mini_cart_items, mini_cart_total = calculate_cart_details()
    mini_coupon_discount, mini_active_coupon = get_coupon_discount(mini_cart_total)
    return {
        "store_name": STORE_NAME,
        "store_email": STORE_EMAIL,
        "mini_cart_items": mini_cart_items,
        "mini_cart_total": mini_cart_total,
        "mini_cart_final_total": max(mini_cart_total - mini_coupon_discount, 0),
        "mini_active_coupon": mini_active_coupon,
        "mini_coupon_discount": mini_coupon_discount,
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
        "coupon_discount_formatted": format_currency(coupon_discount),
    }


def generate_fake_barcode():
    blocks = [
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000, 99999)),
        str(random.randint(10000000000, 99999999999))
    ]
    return " ".join(blocks)


def generate_fake_pix_code(order_number, total):
    reference = str(order_number).replace("-", "")
    cents = int(round(total * 100))
    return f"00020126580014BR.GOV.BCB.PIX0136vistaprime-{reference}520400005303986540{cents}5802BR5910VISTAPRIME6009SAO PAULO62070503***6304"


def generate_order_number():
    while True:
        order_number = str(random.randint(100000, 999999))
        if not Order.query.filter_by(order_number=order_number).first():
            return order_number


def redirect_after_login(default_endpoint="index"):
    next_page = request.args.get("next") or session.pop("next_page", None)
    if next_page and next_page.startswith("/") and not next_page.startswith("//"):
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

    filtered_products = compact_variant_products(filtered_products)
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
    filtered_products = compact_variant_products(filtered_products)

    cart_count = sum(session.get("cart", {}).values())
    categories = get_categories()
    spotlight_product = max(PRODUCTS, key=lambda product: product["price"]).copy()
    spotlight_product["review_summary"] = get_review_summary(spotlight_product["id"])

    return render_template(
        "index.html",
        products=enrich_products_with_reviews(filtered_products),
        all_products=PRODUCTS,
        spotlight_product=spotlight_product,
        deal_products=enrich_products_with_reviews(sorted(PRODUCTS, key=lambda product: product["price"], reverse=True)[:3]),
        categories=categories,
        cart_count=cart_count,
        current_category=category_name,
        search_query="",
        favorites=get_favorites()
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
    can_review = user_has_purchased_product(session.get("user_id"), product)

    return render_template(
        "product_detail.html",
        product=product,
        cart_count=cart_count,
        favorites=favorites,
        reviews=reviews,
        review_summary=review_summary,
        optical_specs=get_product_optical_specs(product_id),
        summary_specs=get_product_summary_specs(product_id),
        detail_sections=get_product_detail_sections(product_id),
        included_items=get_product_included_items(product_id),
        can_review=can_review,
        variant_group=variant_group,
        variant_group_key=variant_group_key,
        variants=variants,
        active_variant=active_variant,
        gallery=gallery
    )


@app.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("index"))

    if not user_has_purchased_product(session.get("user_id"), product):
        flash("Apenas clientes que compraram este produto podem publicar avaliação.", "error")
        return redirect(url_for("product_detail", product_id=product_id))

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
            return jsonify({"error": "Quantidade máxima disponível já está no carrinho."}), 400
        flash("Quantidade máxima disponível já está no carrinho.", "error")
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
@login_required
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
@login_required
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
        flash("Cupom invalido. Tente VISTA10 para aplicar desconto.", "error")
        return redirect(url_for("cart"))

    session["coupon_code"] = coupon_code
    coupon = COUPONS[coupon_code]
    flash(f"Cupom {coupon_code} aplicado: {coupon['percent']}% de desconto no pedido.", "success")
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
                "status": "Boleto gerado com sucesso",
                "due_date": due_date,
                "beneficiary": STORE_LEGAL_NAME
            })

        elif payment_method == "pix":
            if request.form.get("save_payment") and user:
                user.preferred_payment = "pix"
                db.session.commit()

            payment_data.update({
                "pix_code": generate_fake_pix_code(order_number, discounted_total + shipping_price),
                "status": "Pix aguardando pagamento",
                "beneficiary": STORE_LEGAL_NAME
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
        send_order_confirmation_email(order_record, cart_items, active_coupon, coupon_discount)

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

        password_is_valid, password_message = validate_password_strength(password)
        if not password_is_valid:
            flash(password_message, "error")
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
        send_welcome_email(user)

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

        password_is_valid, password_message = validate_password_strength(password)
        if not password_is_valid:
            flash(password_message, "error")
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
    flash("Login social não está disponível no momento.", "error")
    return redirect(url_for("login")), 404


@app.route("/login/facebook-disabled")
def login_facebook():
    flash("Login social não está disponível no momento.", "error")
    return redirect(url_for("login")), 404


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


@app.route("/quem-somos")
def about():
    cart_count = sum(session.get("cart", {}).values())
    return render_template("about.html", cart_count=cart_count)


@app.route("/faq")
def faq():
    cart_count = sum(session.get("cart", {}).values())
    return render_template("faq.html", cart_count=cart_count)


@app.route("/contato", methods=["GET", "POST"])
def contact():
    cart_count = sum(session.get("cart", {}).values())

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not subject or not message:
            flash("Preencha todos os campos para enviar sua mensagem.", "error")
            return redirect(url_for("contact"))

        session["last_contact_message"] = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "sent_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        flash("Mensagem recebida. Nossa equipe retornará pelo e-mail informado.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", cart_count=cart_count)


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


    

