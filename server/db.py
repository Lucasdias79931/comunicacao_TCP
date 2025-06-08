from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import uuid
import shutil

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
        return f"Usuário '{nome}' adicionado com sucesso."
        
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





class usersControllers:
    def __init__(self, baseDir):
        self.baseDir = baseDir

    def criar_usuario(self, name, password, lock):
        try:
            lock.acquire()
            if not usuario_existe(name):
                id_root = str(uuid.uuid4())
                user_path = os.path.join(self.baseDir, id_root)
                
                os.makedirs(user_path)
                adicionar_usuario(name, password, id_root)
                return True, 'Usuário Registrado'.encode()
            else:
                return False, 'usuário existente'.encode()
            
        finally:
            lock.release()

    def validar_usuario(self, name, password):
        return validar_credenciais(name, password)

    def salvar_arquivo(self, root, filename, conteudo, conn):
        filepath = os.path.join(self.baseDir, root, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(conteudo)
            conn.sendall(b"Arquivo salvo com sucesso\n")
        except Exception as e:
            conn.sendall(f"Erro ao salvar arquivo: {str(e)}\n".encode())

    def enviar_arquivo(self, root, filename, conn):
        filepath = os.path.join(self.baseDir, root, filename)
        if not os.path.exists(filepath):
            conn.sendall(f"Arquivo nao encontrado\n".encode())
            return
        size = os.path.getsize(filepath)
        conn.sendall(f"{size}\n".encode())
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)

    def listar_arquivos(self, root, conn):
        path = os.path.join(self.baseDir, root)
        arquivos = os.listdir(path)
        if not arquivos:
            conn.sendall(b"Diretorio vazio\n")
        else:
            lista = "\n".join(arquivos) + "\n"
            conn.sendall(lista.encode())

    def excluir_arquivo(self, root, nome, conn):
        path = os.path.join(self.baseDir, root, nome)
        if os.path.exists(path):
            os.remove(path)
            conn.sendall(b"Arquivo removido\n")
        else:
            conn.sendall(b"Arquivo nao encontrado\n")

    def excluir_conta(self, nome, root):
        path = os.path.join(self.baseDir, root)
        try:
            
            shutil.rmtree(path)
            remover_usuario(nome)
            return True, "Conta e arquivos removidos com sucesso\n".encode()
        except Exception as e:
            print(f"erro ao tentar excluir conta <{e}>")
            return False, f"Erro ao remover conta!\n".encode()




if __name__ == "__main__":
    adicionar_usuario("lucas", "1234", "/diretorio/lucas")
    
    remover_usuario("lucas")
