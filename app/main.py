# Ponte de entrada do meu sistema
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import get_usuario_opcional

from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacao_controller
from app.controllers import cliente_controller
from app.controllers import pdv_controller

app = FastAPI(title="Sistema de Ponto de venda")

#Configurar a pasta para servir os arquivos estáticos (CSS, JS e IMG)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

#Configurar o jinja2 para renderizar os HTML
templates = Jinja2Templates(directory="app/templates")

#Inclui os routers dos controladores
app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(movimentacao_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pdv_controller.router)


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return templates.TemplateResponse("home.html", {"request": request, "produtos": produtos})

@app.get("/movimentacoes")
async def movimentacoes(request: Request, db: Session = Depends(get_db)):
    lista = db.query(Movimentacao).order_by(Movimentacao.criado_em.desc()).all()
    produtos = db.query(Produto).all()
    return templates.TemplateResponse("movimentacoes/index.html", {"request": request, "produtos": produtos, "movimentacoes": lista, "produto_id": None, "tipo": None})

@app.get("/produtos")
async def produtos(request: Request, db: Session = Depends(get_db)):
    produtos_lista = db.query(Produto).all()
    return templates.TemplateResponse("produtos.html", {"request": request, "produtos": produtos_lista})

@app.get("/produtos/novo")
async def produto_novo_form(request: Request):
    return templates.TemplateResponse("produto_form.html", {"request": request})

@app.post("/produtos/novo")
async def produto_novo(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    novo_produto = Produto(
        nome=form.get("nome"),
        preco=float(form.get("preco")),
        estoque_atual=int(form.get("estoque")),
        imagem_path=form.get("imagem"),
    )
    db.add(novo_produto)
    db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/clientes")
async def clientes(request: Request, db: Session = Depends(get_db)):
    lista = db.query(Cliente).all()
    return templates.TemplateResponse("clientes.html", {"request": request, "clientes": lista})

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/auth/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    usuario = form.get("usuario")
    senha = form.get("senha")
    user = db.query(Usuario).filter(Usuario.email == usuario).first()

    if not user:
        return templates.TemplateResponse("auth/login.html", {"request": request, "erro": "Usuário não encontrado"})
    if not verificar_senha(senha, user.senha_hash):
        return templates.TemplateResponse("auth/login.html", {"request": request, "erro": "Senha incorreta"})

    request.session["user_id"] = user.id
    request.session["user_nome"] = user.nome
    return RedirectResponse(url="/", status_code=303)

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)

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
