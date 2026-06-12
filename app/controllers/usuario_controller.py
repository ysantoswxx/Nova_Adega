#Gerenciamento de usuarios

#rots acessiveis apenas por administradores

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuarios import Usuario
from app.auth import get_admin, hash_senha


router = APIRouter(prefix="/usuarios", tags=["Usuários"])

templates = Jinja2Templates(directory="app/templates")


#listagem dos usuarios
@router.get("/")
def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
): 
    
    #buscar todos os usuarios no banco de dados
    usuarios = db.query(Usuario).order_by(Usuario.nome).all()

    return templates.TemplateResponses(
        request, 
        "usuarios/index.html",
        {
            "request": request,
            "usuarios": usuarios, #Lista para exibir na tabela
            "admin": admin #dados de quem está logado.
        }
    )