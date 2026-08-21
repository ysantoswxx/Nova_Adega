from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

<<<<<<< HEAD
from starlette.middleware.sessions import SessionMiddleware
from app.database import SessionLocal, Base, engine
from app.models import Produto, Movimentacao, Usuario, Cliente
=======
from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacao_controller
>>>>>>> 43f5764ddd5543ebf85457be27bf32ff66b81b4d

app = FastAPI(title="Adega Premium")

# Sessão para login/logout
app.add_middleware(SessionMiddleware, secret_key="chave-secreta-muito-dificil-123")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# ============================================
# DEPENDÊNCIA DO BANCO
# ============================================

def get_db():
    """Cria uma nova sessão do banco para cada requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Compara a senha digitada com o hash salvo."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(senha_plana, senha_hash)


# ============================================
# CRIAR TABELAS (se não existirem)
# ============================================
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL DEFAULT 0.0,
            valor_total REAL NOT NULL DEFAULT 0.0,
            observacao TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            produto_id INTEGER,
            usuario_id INTEGER,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """))
    conn.commit()


# ============================================
# ROTA PRINCIPAL (PDV)
# ============================================

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "produtos": produtos}
    )


# ============================================
# MOVIMENTAÇÕES
# ============================================

@app.get("/movimentacoes")
async def movimentacoes(request: Request, db: Session = Depends(get_db)):
    lista = db.query(Movimentacao).order_by(Movimentacao.criado_em.desc()).all()
    produtos = db.query(Produto).all()
    return templates.TemplateResponse(
        "movimentacoes/index.html",
        {
            "request": request,
            "produtos": produtos,
            "movimentacoes": lista,
            "produto_id": None,
            "tipo": None,
        }
    )


# ============================================
# PRODUTOS
# ============================================

@app.get("/produtos")
async def produtos(request: Request, db: Session = Depends(get_db)):
    produtos_lista = db.query(Produto).all()
    return templates.TemplateResponse(
        "produtos.html",
        {"request": request, "produtos": produtos_lista}
    )


@app.get("/produtos/novo")
async def produto_novo_form(request: Request):
    return templates.TemplateResponse(
        "produto_form.html",
        {"request": request}
    )


@app.post("/produtos/novo")
async def produto_novo(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    nome = form.get("nome")
    categoria = form.get("categoria")
    preco = float(form.get("preco"))
    estoque = int(form.get("estoque"))
    observacao = form.get("observacao")

    novo_produto = Produto(
        nome=nome,
        categoria=categoria,
        preco=preco,
        estoque=estoque,
        observacao=observacao,
    )
    db.add(novo_produto)
    db.commit()

    return RedirectResponse(url="/produtos", status_code=303)


# ============================================
# CLIENTES
# ============================================

@app.get("/clientes")
async def clientes(request: Request, db: Session = Depends(get_db)):
    lista = db.query(Cliente).all()
    return templates.TemplateResponse(
        "clientes.html",
        {"request": request, "clientes": lista}
    )


# ============================================
# AUTENTICAÇÃO
# ============================================

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@app.post("/auth/login")
async def login_submit(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    usuario = form.get("usuario")
    senha = form.get("senha")

    user = db.query(Usuario).filter(Usuario.email == usuario).first()

    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "erro": "Usuário não encontrado"},
        )

    if not verificar_senha(senha, user.senha_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "erro": "Senha incorreta"},
        )

    request.session["user_id"] = user.id
    request.session["user_nome"] = user.nome

    return RedirectResponse(url="/", status_code=303)


@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)


# ============================================
# VENDAS (Finalizar compra)
# ============================================

@app.post("/vendas")
async def finalizar_venda(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    itens = body.get("itens", [])
    total = sum(i["preco"] * i["quantidade"] for i in itens)

    for item in itens:
        db.query(Produto).filter(Produto.id == item["id"]).update(
            {Produto.estoque_atual: Produto.estoque_atual - item["quantidade"]}
        )

    db.commit()
    return {"status": "ok", "total": total}
