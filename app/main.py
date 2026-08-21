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
    try: yield db
    finally: db.close()

def verificar_senha(senha_plana, senha_hash):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    try: return pwd_context.verify(senha_plana, senha_hash)
    except: return False

# --- ROTAS PDV E HOME ---
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"): return RedirectResponse(url="/auth/login")
    produtos = db.query(Produto).filter(Produto.ativo == True).all()
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "produtos": produtos, 
        "categorias": categorias,
        "usuario_nome": request.session.get("user_nome")
    })

@app.post("/vendas")
async def processar_venda(request: Request, db: Session = Depends(get_db)):
    dados = await request.json()
    for item in dados["itens"]:
        produto = db.query(Produto).filter(Produto.id == item["id"]).first()
        if produto:
            produto.estoque_atual -= item["quantidade"]
            mov = Movimentacao(
                produto_id=produto.id, tipo="Saída", 
                quantidade=item["quantidade"], observacao="Venda PDV",
                usuario_id=request.session.get("user_id")
            )
            db.add(mov)
    db.commit()
    return JSONResponse({"status": "sucesso"})

# --- PRODUTOS ---
@app.get("/produtos")
async def listar_produtos(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"): return RedirectResponse(url="/auth/login")
    produtos = db.query(Produto).all()
    return templates.TemplateResponse("produtos.html", {"request": request, "produtos": produtos})

@app.get("/produtos/novo")
async def form_produto(request: Request):
    return templates.TemplateResponse("produto_form.html", {"request": request})

@app.post("/produtos/novo")
async def salvar_produto(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    novo = Produto(nome=form.get("nome"), preco=float(form.get("preco")), estoque_atual=int(form.get("estoque")))
    db.add(novo); db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/produtos/{id}/excluir")
async def excluir_prod(id: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id == id).first()
    if p: db.delete(p); db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

# --- CLIENTES ---
@app.get("/clientes")
async def listar_clientes(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return templates.TemplateResponse("clientes.html", {"request": request, "clientes": clientes})

@app.get("/clientes/novo")
async def form_cliente(request: Request):
    return templates.TemplateResponse("cliente_form.html", {"request": request})

@app.post("/clientes/novo")
async def salvar_cliente(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    novo = Cliente(nome=form.get("nome"), telefone=form.get("telefone"), email=form.get("email"), cpf=form.get("cpf"))
    db.add(novo); db.commit()
    return RedirectResponse(url="/clientes", status_code=303)

# --- HISTÓRICO ---
@app.get("/movimentacoes")
async def historico(request: Request, db: Session = Depends(get_db)):
    movs = db.query(Movimentacao).order_by(Movimentacao.criado_em.desc()).all()
    return templates.TemplateResponse("movimentacoes/movimentacoes-index.html", {"request": request, "movimentacoes": movs})

# --- LOGIN ---
@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def login_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    user = db.query(Usuario).filter(Usuario.email == form.get("usuario")).first()
    if user and verificar_senha(form.get("senha"), user.senha_hash):
        request.session["user_id"] = user.id
        request.session["user_nome"] = user.nome
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request, "erro": "Credenciais Inválidas"})

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
