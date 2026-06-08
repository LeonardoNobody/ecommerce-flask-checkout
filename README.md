# VistaPrime Ótica

E-commerce acadêmico desenvolvido em Flask para simular uma loja online de ótica, com catálogo de produtos, variações, favoritos, avaliações verificadas, carrinho, checkout, endereço, pagamento simulado e área do usuário.

## Funcionalidades

- Catálogo de óculos solares, armações, tecnologia e acessórios
- Página de produto com galeria, ficha técnica, variações de cor e avaliações
- Carrinho lateral e página de carrinho estilizada
- Cadastro, login e recuperação de senha simulada
- Favoritos vinculados ao usuário logado
- Checkout com endereço, entrega e pagamento simulado
- Cupom com exibição de desconto em valor e porcentagem
- Perfil com dados pessoais e endereço padrão
- Termos de serviço, política de privacidade, FAQ, contato e página institucional

## Tecnologias

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML, CSS e JavaScript

## Rodando localmente

```bash
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

Acesse:

```text
http://127.0.0.1:5000
```

## Deploy no Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

Configure a variável de ambiente:

```text
SECRET_KEY=uma-chave-segura
```

Para envio real de e-mails, configure também:

```text
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
MAIL_DEFAULT_SENDER=seu-email@gmail.com
```

Sem essas variáveis, o sistema salva uma prévia dos e-mails em `instance/email_outbox`, útil para demonstração local.

## Observação

Projeto criado para fins acadêmicos. Pagamentos, autenticações externas e integrações reais são simulados.
