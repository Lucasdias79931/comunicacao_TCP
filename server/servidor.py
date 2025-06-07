import socket
import threading
import os
from db import usersControllers
from fileContoller import fileControle 

HOST = '0.0.0.0'
PORT = 5000

# Diretório base para diretórios dos usuários
BASE_DIR = os.path.abspath('./alldir')
os.makedirs(BASE_DIR, exist_ok=True)

users_controller = usersControllers(BASE_DIR)
fc = fileControle(BASE_DIR)
lock = threading.Lock()

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        data += conn.recv(1)
    return data.decode().strip()

def handle_client(conn, addr):
    conn.settimeout(60)
    print(f"[+] Nova conexão de {addr}")
    try:
        while True:
            conn.sendall("CONEXÃO INICIADA\n".encode())
            data = conn.recv(1024).decode().strip()
            if data.startswith("REGISTRAR"):
                _, nome, senha = data.split()
                success = users_controller.criar_usuario(nome, senha, lock)
                if success:
                    msg = b"Registro realizado com sucesso\n"
                    break
                else:
                    msg = b"Erro ao registrar\n"
                conn.sendall(msg)
            elif data.startswith("ENTRAR"):
                _, nome, senha = data.split()
                root = users_controller.validar_usuario(nome, senha)
                if not root:
                    conn.sendall(b"Login invalido\n")
                else:
                    conn.sendall(b"Login bem-sucedido.\n")
                    break
            else:
                conn.sendall(b"Comando invalido\n")

        while True:
            cmd = recv_line(conn)
            if cmd == "QUIT":
                print("cliente desconectando")
                conn.sendall(b'[servidor]desconectando')
                break
            elif cmd.startswith("UPLOAD"):
                _, filename = cmd.split(maxsplit=1)
                tamanho = int(recv_line(conn))
                conteudo = b""
                while len(conteudo) < tamanho:
                    chunk = conn.recv(min(4096, tamanho - len(conteudo)))
                    if not chunk:
                        break
                    conteudo += chunk
                fc.salvar_arquivo(root, filename, conteudo, conn)
            elif cmd.startswith("DOWNLOAD"):
                _, nome_arquivo = cmd.split()
                fc.enviar_arquivo(root, nome_arquivo, conn)
            elif cmd == "LIST":
                fc.listar_arquivos(root, conn)
            elif cmd.startswith("DELETE"):
                _, nome_arquivo = cmd.split()
                fc.excluir_arquivo(root, nome_arquivo, conn)

            elif cmd == "DELETE_ACCOUNT":
                users_controller.excluir_conta(nome, root, conn)
                conn.sendall("conta excluida!\ndesconectando!".encode())
                break
            else:
                conn.sendall(b"Comando invalido\n")
        
    except Exception as e:
        print(f"[-] Erro com cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Conexao encerrada com {addr}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[+] Servidor ouvindo em {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

