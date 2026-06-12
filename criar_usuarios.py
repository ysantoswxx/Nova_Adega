# Script para popular o banco de dados com usuarios admin

from app.database import Session
from app.models.usuarios import Usuario
from app.auth import hash_senha


#funçaõ para cadastrar os usuarios 
def seed():
    db = Session()
    try:
        nome_usuario = "admin"
        email_usuario = "admin@teste.com"
        senha_usuario = "admin@123"
        perfil = "admin"

        #verificar se o usuario já existe
        existente = db.query(Usuario).filter_by(email=email_usuario).first()

        if not existente:
            #criar o usuario 
            usuario = Usuario(
                nome=nome_usuario,
                email=email_usuario, 
                senha_hash=hash_senha(senha_usuario), 
                role=perfil
                )
            db.add(usuario)
            db.commit()
            print(f"Usuario cadastrado com sucesso {nome_usuario}!")
        else:
            print(f"Esse email já está cadastrado: {email_usuario}")

    except Exception as erro:
        db.rollback()
        print(f"Erro: {erro}")
    finally:
        db.close()

#chamar a afunção
seed()