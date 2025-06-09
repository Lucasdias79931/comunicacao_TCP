from untils import DOWNLOAD, HELP, login_menu, UPLOAD, socket
from pandas import pd
from matplotlib import pyplot as plt
import threading
import os

HOST = '192.168.1.108'
PORT = 5001

lock = threading.Lock()
here = os.path.abspath(os.path.dirname(__name__))

files_to_test = os.path.join(here, 'files_to_test')
logs = os.path.join(here, "logs")
os.makedirs(logs, exist_ok=True)

def receber_mensagem(sock):
    try:
        resposta = sock.recv(1024)
        if not resposta:
            print("Servidor desconectou.")
            return None
        return resposta.decode()
    except Exception as e:
        print(f"[ERRO DE RECEBIMENTO] {e}")
        return None

def tratar_comando(command, content, s):
    if command == "UPLOAD":
        UPLOAD(f'{command} {content}', s)
    elif command == "DOWNLOAD":
        s.sendall(f'{command} {content}\n'.encode())
        DOWNLOAD(f'{command} {content}', s)
    else:
        print('Opção inválida.')
    return False

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.settimeout(80)
        try:
            resposta = s.recv(1024)
            if not resposta:
                raise ConnectionResetError("Servidor não respondeu.")
            print(resposta.decode())
        except Exception as e:
            print(f"[ERRO INICIAL] {e}")
            exit(1)

        while True:
            try:
               

                stop = False
                while not stop:
                    print("Use comandos: UPLOAD, DOWNLOAD, LIST, DELETE, DELETE_ACCOUNT, QUIT")
                    command = input(">>command:").upper().strip()

                    

                    content = ""
                    if command in ('DOWNLOAD', 'DELETE', 'UPLOAD'):
                        content = input(">>content:").strip()
                        if not content:
                            print("Conteúdo não pode ser vazio.")
                            continue

                    stop = tratar_comando(command, content, s)
            
                if stop:
                    
                    break

            except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERRO - CONEXÃO PERDIDA] {e}")
                break

except Exception as e:
    print(f"[FALHA FATAL] {e}")
    exit(1)
