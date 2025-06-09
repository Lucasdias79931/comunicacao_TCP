import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from untils import DOWNLOAD, UPLOAD, socket
import threading
from time import time
from tqdm import tqdm

HOST = '192.168.1.166'
PORT = 5001

lock = threading.Lock()
here = os.path.abspath(os.path.dirname(__name__))

files_to_test = os.listdir(os.path.join(here, 'files_to_test'))
logs = os.path.join(here, "logs")
uploadLog = os.path.join(logs,'uploads.csv')
downloadLog = os.path.join(logs,'downloads.csv')
os.makedirs(logs, exist_ok=True)

def log(filename, size, time_trans, output):
    size_mb = size / (1024 * 1024)  
    linha = f"{filename},{size_mb:.2f},{time_trans:.4f}\n"
    header = "filename,size_MB,transfer_time_sec\n"

    if not os.path.exists(output):
        with open(output, 'w') as f:
            f.write(header)

    with open(output, 'a') as f:
        f.write(linha)



def UPLOAD(command, sock):
    parts = command.strip().split(maxsplit=1)
    if len(parts) != 2:
        print("Formato correto: UPLOAD caminho_arquivo")
        return

    filepath = parts[1]
    if not os.path.isfile(filepath):
        print(f"Arquivo <{filepath}> não encontrado.")
        return

    
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        

        sock.sendall(f"UPLOAD {filename}\n".encode())
        sock.sendall(f"{filesize}\n".encode())
        start = time()
        with open(filepath, 'rb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Enviando {filename}") as barra:

         
            while True:

                dado = f.read(1024*64)
                
                if not dado:
                    break
                sock.sendall(dado)
                
                barra.update(len(dado)) 
        end = time() - start
        resposta = sock.recv(1024)
        if not resposta:
            print("Servidor desconectou durante o upload.")
            return
        
        print(resposta.decode())


        log(filename,filesize,end,uploadLog)
    except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[ERRO - UPLOAD] {e}")


def DOWNLOAD(command, sock):
    parts = command.strip().split(maxsplit=1)
    if len(parts) != 2:
        print("Formato correto: DOWNLOAD nome_arquivo")
        return
    filename = parts[1]

    try:
      
        response = sock.recv(1024)
        if not response:
            print("Servidor desconectou durante o download.")
            return
        response = response.decode()

        if response.strip().isdigit():
            size = int(response.strip())
            with open(filename, 'wb') as f, tqdm(total=size, unit='B', unit_scale=True, desc=f"Enviando {filename}") as barra:
                dado = 0
                while dado < size:
                    data = sock.recv(4096)
                    if not data:
                        print("Conexão perdida durante o download.")
                        return
                    f.write(data)
                    
                    dado += len(data)
                    barra.update(dado)
            print("Arquivo baixado com sucesso.")
        else:
            print(response)
    except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[ERRO - DOWNLOAD] {e}")

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
                    print("Use comandos: UPLOAD, DOWNLOAD, LIST")
                    command = input(">>command:").upper().strip()

                    

                    print(command)
                    if command == 'UPLOAD':
                        for file in files_to_test:
                            full_file = os.path.join(here, f'files_to_test/{file}')
                            

                            
                            stop = tratar_comando(command, full_file, s)
                            
                    elif command == 'DOWNLOAD':
                        stop = tratar_comando(command, full_file, s)
                    elif command == "QUIT":
                        stop = tratar_comando(command, full_file, s)
                        break

            except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERRO - CONEXÃO PERDIDA] {e}")
                break

except Exception as e:
    print(f"[FALHA FATAL] {e}")
    exit(1)
