
import os
class fileControle:
    def __init__(self, baseDir):
        self.baseDir = baseDir



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

  