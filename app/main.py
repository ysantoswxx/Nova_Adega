from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from app.database import SessionLocal, engine
from app.models import Produto, Movimentacao, Usuario, Cliente
from app.models.categoria import Categoria
from sqlalchemy import text
import datetime

app = FastAPI(title="Adega Premium")
app.add_middleware(SessionMiddleware, secret_key="chave-secreta-muito-dificil-123")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    try:
        return pwd_context.verify(senha_plana, senha_hash)
    except Exception:
        return False

# --- ROTAS DE NAVEGAÇÃO ---

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    produtos = db.query(Produto).filter(Produto.ativo == True).all()
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "produtos": produtos, 
        "categorias": categorias,
        "usuario_nome": request.session.get("user_nome")
    })

# --- GERENCIAMENTO DE PRODUTOS ---

@app.get("/produtos")
async def listar_produtos(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/auth/login", status_code=303)
    produtos = db.query(Produto).all()
    return templates.TemplateResponse("produtos.html", {"request": request, "produtos": produtos})

@app.get("/produtos/novo")
async def produto_novo_form(request: Request):
    return templates.TemplateResponse("produto_form.html", {"request": request, "produto": None})

@app.post("/produtos/novo")
async def produto_novo(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    categoria_nome = form.get("categoria")
    cat = db.query(Categoria).filter(Categoria.nome == categoria_nome).first()
    if not cat:
        cat = Categoria(nome=categoria_nome)
        db.add(cat); db.flush()
    
    novo = Produto(
        nome=form.get("nome"),
        preco=float(form.get("preco")),
        estoque_atual=int(form.get("estoque")),
        categoria=cat
    )
    db.add(novo); db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/produtos/{id}/editar")
async def editar_form(id: int, request: Request, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id == id).first()
    return templates.TemplateResponse("produto_form.html", {"request": request, "produto": p})

@app.post("/produtos/{id}/editar")
async def editar_post(id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    p = db.query(Produto).filter(Produto.id == id).first()
    if p:
        p.nome = form.get("nome")
        p.preco = float(form.get("preco"))
        p.estoque_atual = int(form.get("estoque"))
        categoria_nome = form.get("categoria")
        cat = db.query(Categoria).filter(Categoria.nome == categoria_nome).first()
        if not cat:
            cat = Categoria(nome=categoria_nome)
            db.add(cat); db.flush()
        p.categoria = cat
        db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/produtos/{id}/excluir")
async def excluir_prod(id: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id == id).first()
    if p: 
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

# --- MOVIMENTAÇÕES (ESTOQUE) ---

@app.get("/movimentacoes")
async def listar_movimentacoes(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/auth/login", status_code=303)
    movs = db.query(Movimentacao).order_by(Movimentacao.criado_em.desc()).all()
    return templates.TemplateResponse("movimentacoes/movimentacoes-index.html", {"request": request, "movimentacoes": movs})

@app.get("/movimentacoes/nova")
async def nova_movimentacao_form(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(Produto).filter(Produto.ativo == True).all()
    return templates.TemplateResponse("movimentacoes/form.html", {"request": request, "produtos": produtos})

@app.post("/movimentacoes/nova")
async def nova_movimentacao_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    produto_id = int(form.get("produto_id"))
    tipo = form.get("tipo") # "Entrada" ou "Saída"
    quantidade = int(form.get("quantidade"))
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        if tipo == "Entrada":
            produto.estoque_atual += quantidade
        else:
            produto.estoque_atual -= quantidade
        
        nova_mov = Movimentacao(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            observacao=form.get("observacao"),
            usuario_id=request.session.get("user_id")
        )
        db.add(nova_mov); db.commit()
        
    return RedirectResponse(url="/movimentacoes", status_code=303)

# --- CLIENTES ---

@app.get("/clientes")
async def listar_clientes(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id: return RedirectResponse(url="/auth/login", status_code=303)
    clientes = db.query(Cliente).all()
    return templates.TemplateResponse("clientes.html", {"request": request, "clientes": clientes})

@app.get("/clientes/novo")
async def cliente_novo_form(request: Request):
    return templates.TemplateResponse("cliente_form.html", {"request": request, "cliente": None})

@app.post("/clientes/novo")
async def cliente_novo(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    novo = Cliente(
        nome=form.get("nome"),
        telefone=form.get("telefone"),
        email=form.get("email"),
        cpf=form.get("cpf")
    )
    db.add(novo); db.commit()
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/clientes/{id}/excluir")
async def excluir_cliente(id: int, db: Session = Depends(get_db)):
    c = db.query(Cliente).filter(Cliente.id == id).first()
    if c:
        db.delete(c)
        db.commit()
    return RedirectResponse(url="/clientes", status_code=303)

# --- VENDAS (PDV) ---

@app.post("/vendas")
async def finalizar_venda(request: Request, db: Session = Depends(get_db)):
    dados = await request.json()
    itens = dados.get("itens", [])
    
    for item in itens:
        produto = db.query(Produto).filter(Produto.id == item["id"]).first()
        if produto:
            produto.estoque_atual -= item["quantidade"]
            nova_mov = Movimentacao(
                produto_id=produto.id,
                tipo="Saída",
                quantidade=item["quantidade"],
                observacao="Venda realizada via PDV",
                usuario_id=request.session.get("user_id")
            )
            db.add(nova_mov)
    
    db.commit()
    return JSONResponse({"status": "ok"})

# --- AUTENTICAÇÃO ---

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    usuario = form.get("usuario")
    senha = form.get("senha")
    user = db.query(Usuario).filter(Usuario.email == usuario).first()

    if not user or not verificar_senha(senha, user.senha_hash):
        return templates.TemplateResponse("auth/login.html", {"request": request, "erro": "Login inválido"})

    request.session["user_id"] = user.id
    request.session["user_nome"] = user.nome
    return RedirectResponse(url="/", status_code=303)

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
