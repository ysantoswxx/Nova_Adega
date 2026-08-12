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

<<<<<<< HEAD
templates = Jinja2Templates(
    directory="app/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# app.include_router(produtos.router)
app.include_router(auth.router)
app.include_router(vendas.router)
app.include_router(estoques.router)
app.include_router(dashboard.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(movimentacoes.router)
app.include_router(relatorio.router)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
=======
@app.get("/")
def tela_inicial(
    request: Request,
    usuario = Depends(get_usuario_opcional)
):
    #Tela não logado
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"request": request}
        )
    #Logado - exibir a tela de funcionario
>>>>>>> e04597d8e9c259cf3c1f43c9877f6cffc6bc4ca8
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request, "usuario": usuario}
    )