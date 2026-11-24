import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

# Lê o arquivo .env (se existir). Nenhuma credencial fica escrita no código.
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24)

PRODUTOS = [
    {"id": "espresso", "nome": "Café Espresso", "imagem": "cafeExpresso.jpg",
     "resumo": "Café intenso e aromático.",
     "descricao": "Café intenso e aromático, extraído na hora para garantir todo o sabor.",
     "preco": "8,90"},
    {"id": "cappuccino", "nome": "Cappuccino", "imagem": "cappuccino.jpg",
     "resumo": "Espresso, leite vaporizado e espuma cremosa.",
     "descricao": "Espresso, leite vaporizado e espuma cremosa, na medida certa para quem gosta de uma bebida macia.",
     "preco": "12,00"},
    {"id": "croissant", "nome": "Croissant", "imagem": "croissant.jpg",
     "resumo": "Croissant artesanal, leve e crocante.",
     "descricao": "Croissant artesanal, crocante por fora e macio por dentro, assado todos os dias.",
     "preco": "9,50"},
    {"id": "latte", "nome": "Café Latte", "imagem": "cafe-latte.jpg",
     "resumo": "Espresso suave com bastante leite vaporizado e um toque de espuma.",
     "descricao": "Espresso suave com bastante leite vaporizado e um toque de espuma, uma bebida leve para qualquer hora.",
     "preco": "11,00"},
    {"id": "mocha", "nome": "Mocha", "imagem": "mocha.jpg",
     "resumo": "Café, chocolate cremoso e chantilly para os dias que pedem um mimo.",
     "descricao": "Café, chocolate cremoso e chantilly para os dias que pedem um mimo.",
     "preco": "14,00"},
    {"id": "pao-de-queijo", "nome": "Pão de queijo", "imagem": "pao-de-queijo.jpg",
     "resumo": "Quentinho e macio por dentro, com casquinha dourada por fora.",
     "descricao": "Quentinho e macio por dentro, com casquinha dourada por fora. Perfeito para acompanhar um café.",
     "preco": "6,50"},
    {"id": "bolo-de-cenoura", "nome": "Bolo de cenoura", "imagem": "bolo-de-cenoura.jpg",
     "resumo": "Fatia fofinha coberta com calda de chocolate, feita na casa todos os dias.",
     "descricao": "Fatia fofinha coberta com calda de chocolate, feita na casa todos os dias.",
     "preco": "10,00"},
    {"id": "brownie", "nome": "Brownie de chocolate", "imagem": "brownie.jpg",
     "resumo": "Macio por dentro, com aquela casquinha crocante e sabor irresistível.",
     "descricao": "Macio por dentro, com casquinha crocante e sabor irresistível de chocolate.",
     "preco": "11,50"},
]


def get_connection():
    """Abre uma conexão com o MySQL usando as variáveis do .env."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cardapio")
def cardapio():
    return render_template("cardapio.html", produtos=PRODUTOS)


@app.route("/sobre")
def sobre():
    return render_template("sobre-nos.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        assunto = request.form.get("assunto", "").strip()
        mensagem = request.form.get("mensagem", "").strip()

        if not email or not assunto or not mensagem:
            flash("Preencha todos os campos.", "warning")
            return render_template("contatos.html")

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Consulta parametrizada: os valores nunca são concatenados na string SQL.
            cursor.execute(
                "INSERT INTO mensagens (email, assunto, mensagem) VALUES (%s, %s, %s)",
                (email, assunto, mensagem),
            )
            conn.commit()
            cursor.close()
        except mysql.connector.Error as erro:
            app.logger.error("Erro ao inserir no banco: %s", erro)
            flash("Não foi possível salvar sua mensagem. Tente novamente.", "danger")
            return render_template("contatos.html")
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

        flash("Mensagem enviada com sucesso!", "success")
        return redirect(url_for("contato"))

    return render_template("contatos.html")


@app.route("/listar")
def listar():
    mensagens = []
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, email, assunto, mensagem, criado_em FROM mensagens ORDER BY id DESC"
        )
        mensagens = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as erro:
        app.logger.error("Erro ao consultar o banco: %s", erro)
        flash("Não foi possível consultar o banco de dados.", "danger")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

    return render_template("listar.html", mensagens=mensagens)


if __name__ == "__main__":
    # host 0.0.0.0 = aceita conexões externas (não só localhost)
    app.run(host="0.0.0.0", port=5000)
