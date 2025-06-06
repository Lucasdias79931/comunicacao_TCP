import os
import uuid


class fileController:
    def __init__(self):
        pass

    @staticmethod
    def salvar_arquivo(root, filename, conteudo, conn):
        filepath = os.path.join(root, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(conteudo)
            conn.sendall(b"Arquivo salvo com sucesso\n")
        except Exception as e:
            conn.sendall(f"Erro ao salvar arquivo: {str(e)}\n".encode())
    @staticmethod
    def enviar_arquivo(root, filename, conn):
        filepath = os.path.join(root, filename)
        if not os.path.exists(filepath):
            conn.sendall(b"Arquivo nao encontrado\n")
            return
        try:
            size = os.path.getsize(filepath)
            conn.sendall(f"{size}\n".encode())
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)
        except ConnectionAbortedError as e:
            print("Queda na conexão")
            return -1
        except Exception as e:
            print(e)
            error = "Algum erro ocorreu no servidor...\ndesconectando..."
            conn.sendall(error.encode())
            return -1
    @staticmethod
    def listar_arquivos(self, root, conn):
        
        arquivos = os.listdir(root)
        try:
            if not arquivos:
                conn.sendall(b"Diretorio vazio\n")
            else:
                lista = "\n".join(arquivos) + "\n"
                conn.sendall(lista.encode())
        except FileNotFoundError as e:
            print(e)
            error = "Algum erro ocorreu no servidor listar...\ndesconectando..."
            conn.sendall(error.encode())
            return -1
        except Exception as e:
            print(e)
            error = "Algum erro ocorreu no servidor listar...\ndesconectando..."
            conn.sendall(error.encode())
            return -1
    @staticmethod
    def excluir_arquivo(root, nome, conn):
        path = os.path.join(root, nome)
        if os.path.exists(path):
            try:
                os.remove(path)
                conn.sendall(b"Arquivo removido\n")
            except OSError as e:
                print(e)
                error = "Algum erro ocorreu no servidor e não foi possível deletar o arquivo...\ndesconectando..."
                conn.sendall(error.encode())
                return -1
            except Exception as e:
                print(e)
                error = "Algum erro ocorreu no servidor e não foi possível deletar o arquivo...\ndesconectando..."
                conn.sendall(error.encode())
                return -1
        else:
            conn.sendall("Arquivo não encontrado".encode())