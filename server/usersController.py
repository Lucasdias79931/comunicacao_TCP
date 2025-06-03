from db import adicionar_usuario, validar_credenciais, remover_usuario
import os
import uuid
import shutil

class usersControllers:
    def __init__(self, baseDir):
        self.baseDir = baseDir

    def criar_usuario(self, name, password, lock):
        try:
            lock.acquire()
            while True:
                id_root = str(uuid.uuid4())
                user_path = os.path.join(self.baseDir, id_root)
                if not os.path.exists(user_path):
                    os.makedirs(user_path)
                    adicionar_usuario(name, password, id_root)
                    return True
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
            conn.sendall(b"Arquivo nao encontrado\n")
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

    def excluir_conta(self, nome, root, conn):
        path = os.path.join(self.baseDir, root)
        try:
            shutil.rmtree(path)
            remover_usuario(nome)
            conn.sendall(b"Conta e arquivos removidos com sucesso\n")
        except Exception as e:
            conn.sendall(f"Erro ao remover conta: {str(e)}\n".encode())
