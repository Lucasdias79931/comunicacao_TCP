from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///usuarios.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Usuario(Base):
    __tablename__ = 'usuarios'  

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    diretorio_root = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def adicionar_usuario(nome: str, senha: str, diretorio_root: str):
    session = SessionLocal()
    try:
        novo = Usuario(nome=nome, senha=senha, diretorio_root=diretorio_root)
        session.add(novo)
        session.commit()
        print(f"Usuário '{nome}' adicionado com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar usuário: {e}")
    finally:
        session.close()

def remover_usuario(nome: str):
    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter_by(nome=nome).first()
        if usuario:
            session.delete(usuario)
            session.commit()
            print(f"Usuário '{nome}' removido.")
        else:
            print(f"Usuário '{nome}' não encontrado.")
    finally:
        session.close()

def alterar_senha(nome: str, nova_senha: str):
    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter_by(nome=nome).first()
        if usuario:
            usuario.senha = nova_senha
            session.commit()
            print(f"Senha de '{nome}' alterada.")
        else:
            print(f"Usuário '{nome}' não encontrado.")
    finally:
        session.close()

def validar_credenciais(nome: str, senha: str):
    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter_by(nome=nome, senha=senha).first()
        if usuario:
            return usuario.diretorio_root
        return None
    finally:
        session.close()
        
def usuario_existe(nome: str):
    session = SessionLocal()
    try:
        return session.query(Usuario).filter_by(nome=nome).first() is not None
    finally:
        session.close()


if __name__ == "__main__":
    adicionar_usuario("lucas", "1234", "/diretorio/lucas")
    alterar_senha("lucas", "nova123")
    remover_usuario("lucas")
