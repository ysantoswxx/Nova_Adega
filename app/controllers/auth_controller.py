# Rotas de autenticação vai ficar aqui

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.usuarios import Usuario
from app.auth import hash_senha, verificar_senha, criar_token

# APIRouter agrupa as rotas dentro desse módulo com o prefixo /auth
router = APIRouter(prefix="/auth", tags=["Autenticação"])

templates = Jinja2Templates(directory="app/templates")
#Tela de cadastro
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/cadastro.html",
        {"request": request}
    )

#Tela de login
@router.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"request": request}
    )

# Rota para criar o usuario
@router.post("/cadastro")
def fazer_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar se o email já está cadastrado
    usuario_existente = db.query(Usuario).filter_by(email=email).first()

    # Mensagem de erro se o email estiver cadastrado
    if usuario_existente:
        return templates.TemplateResponse(
            request,
            "auth/cadastro.html",
            {"request": request, "erro": "Este E-mail já está cadastrado."},
            status_code=400
        )
   
    #Criar o usuario - criar o objeto
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha(senha)      
    )

    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/auth/login?erro=cadastro=ok", status_code=302)


# Fazer o login
@router.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    print("LOGIN RECEBIDO")
    print("EMAIL:", email)

    usuario = db.query(Usuario).filter_by(email=email).first()

    print("USUARIO:", usuario)

    senha_correta = (
        usuario is not None and verificar_senha(senha, usuario.senha_hash)
    )

    print("SENHA CORRETA:", senha_correta)

    if not senha_correta:
        print("LOGIN NEGADO")
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "request": request,
                "erro": "E-mail ou senha incorretos"
            }
        )

    if not usuario.ativo:
        print("USUARIO INATIVO")
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "request": request,
                "erro": "Usuário inativo. Contate o administrador."
            }
        )

    print("USUARIO AUTENTICADO")

    token_data = {
        "sub": usuario.email,
        "nome": usuario.nome,
        "role": usuario.role,
        "id": usuario.id
    }

    token = criar_token(token_data)

    print("TOKEN CRIADO")

    response = RedirectResponse(url="/", status_code=302)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )

    print("COOKIE CRIADO")
    print("REDIRECIONANDO PARA /")

    return response


@router.get("/logout")
def sair(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response