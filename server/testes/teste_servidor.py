import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import threading
from fileContoller import fileControle 
from until import recv_line

HOST = '0.0.0.0'
PORT = 5001

# Diretório base para diretórios dos usuários
BASE_DIR = os.path.abspath(os.path.dirname(__name__))
os.makedirs(BASE_DIR, exist_ok=True)

fc = fileControle(BASE_DIR)




##################################################
########## Função Principal ######################
def conexao_cliente(conn, addr):
    conn.settimeout(60)
    print(f"[+] Nova conexão de {addr}")
    try:
        conn.sendall("CONEXÃO INICIADA\n".encode())
        root = 'root_test'
        

        

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

