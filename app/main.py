from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException


from app.database import Base, engine

from app.models import (
    produtos,
    categorias,
    auth,
    vendas,
    estoques,
    dashboard,
    usuarios,
    movimentacoes,
    relatorio
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PDV ADEGA"
)

templates = Jinja2Templates(
    directory="app/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.include_router(produtos.router)
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
    return templates.TemplateResponse(
        "base.html",
        {"request": request}
    )

@app.exception_handler(404)
def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {
        "request": request
    }, status_code=404)

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):

    if exc.status_code == 401:
        return RedirectResponse(url="/auth/login")

    if exc.status_code == 403:
        return RedirectResponse(url="/auth/login")

    return RedirectResponse(url="/404")