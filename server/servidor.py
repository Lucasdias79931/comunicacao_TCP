import socket
import threading
import os
from db import usersControllers
from fileContoller import fileControle 
from until import recv_line

HOST = '0.0.0.0'
PORT = 5000

# Diretório base para diretórios dos usuários
BASE_DIR = os.path.abspath('./alldir')
os.makedirs(BASE_DIR, exist_ok=True)

users_controller = usersControllers(BASE_DIR)
fc = fileControle(BASE_DIR)
lock = threading.Lock()



def registrar(data, lock):
    
    _, nome, senha = data.split()
    success = users_controller.criar_usuario(nome, senha, lock)
    msg = b''
    if success:
        msg = b"Registro realizado com sucesso\n"
        
    else:
        msg = b"Erro ao registrar\n"
    
    return msg

def login(data, conn):
    _, nome, senha = data.split()
    root = users_controller.validar_usuario(nome, senha)
    if not root:
        conn.sendall(b"Login invalido\n")

        return False
    else:
        conn.sendall(b"Login bem-sucedido.\n")
        return True, root, nome




##################################################
########## Função Principal ######################
def conexao_cliente(conn, addr):
    conn.settimeout(60)
    print(f"[+] Nova conexão de {addr}")
    try:
        conn.sendall("CONEXÃO INICIADA\n".encode())
        root = ''
        nome = ''

        while True:
            
            data = conn.recv(1024).decode().strip()
            if data.startswith("REGISTRAR"):
                
                msg = registrar(data,lock)
                conn.sendall(msg)
                break
            elif data.startswith("ENTRAR"):
                sucess, root, nome = login(data, conn)

                if sucess:
                    break
            else:
                conn.sendall(b"Comando invalido\n")

        while True:
            command = recv_line(conn)

            if command == "QUIT":
                print("cliente desconectando")
                conn.sendall(b'[servidor]desconectando')
                break

            elif command.startswith("UPLOAD"):

                fc._salvar_arquivo(root,command,conn)

            elif command.startswith("DOWNLOAD"):
                _, nome_arquivo = command.split()
                fc.enviar_arquivo(root, nome_arquivo, conn)
            elif command == "LIST":
                fc.listar_arquivos(root, conn)
            elif command.startswith("DELETE"):
                _, nome_arquivo = command.split()
                fc.excluir_arquivo(root, nome_arquivo, conn)

            elif command == "DELETE_ACCOUNT":
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
        thread = threading.Thread(target=conexao_cliente, args=(conn, addr))
        thread.start()

