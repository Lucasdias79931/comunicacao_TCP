
import os
from until import recv_line
from hashlib import sha512

class fileControle:
    def __init__(self, baseDir):
        self.baseDir = baseDir



    
            
    def _salvar_arquivo(self, root, command, conn,lock):
        try:
            _, filePath = command.split(maxsplit=1)
            filepath = os.path.join(self.baseDir, root, filePath)

            tamanho = int(recv_line(conn)) 
            recebido = 0

            with open(filepath, 'wb') as f, lock:
                while recebido < tamanho:
                    data = conn.recv(min(4096, tamanho - recebido))
                    if not data:
                        break  
                    f.write(data)
                    recebido += len(data)

            if recebido == tamanho:
                conn.sendall(b"Arquivo salvo com sucesso\n")
            else:
                conn.sendall(b"Erro: arquivo incompleto\n")
                if os.path.exists(filepath):
                    os.remove(filepath)

        except Exception as e:
            conn.sendall(f"Erro ao salvar arquivo: {str(e)}\n".encode())


    def enviar_arquivo(self, root, filename, conn, lock):
        filepath = os.path.join(self.baseDir, root, filename)
        with lock:
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

    def excluir_arquivo(self, root, nome, conn,lock):
        with lock:
            path = os.path.join(self.baseDir, root, nome)
            if os.path.exists(path):
                os.remove(path)
                conn.sendall(b"Arquivo removido\n")
            else:
                conn.sendall(b"Arquivo nao encontrado\n")

  