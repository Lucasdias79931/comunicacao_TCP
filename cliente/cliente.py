import socket
import sys
import os
import threading
def login_menu():
    while True:
        opcao = input("1: Entrar\n2: Registrar\nEscolha: ")
        if opcao in ('1', '2'):
            nome = input("Nome: ")
            senha = input("Senha: ")
            return opcao, nome, senha
        else:
            print(f"Opcao inválida: {opcao}")

def UPLOAD(command, sock, lock=None):
    parts = command.strip().split(maxsplit=1)
    if len(parts) != 2:
        print("Formato correto: UPLOAD caminho_arquivo")
        return
    filepath = parts[1]
    if not os.path.isfile(filepath):
        print(f"Arquivo <{filepath}> não encontrado.")
        return

    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        content = f.read()
    sock.sendall(f"UPLOAD {filename}\n".encode())
    sock.sendall(f"{len(content)}\n".encode())
    sock.sendall(content)
    print(sock.recv(1024).decode())

def DOWNLOAD(command, sock, lock=None):
    parts = command.strip().split(maxsplit=1)
    if len(parts) != 2:
        print("Formato correto: DOWNLOAD nome_arquivo")
        return
    filename = parts[1]

    response = sock.recv(1024).decode()
    if response.strip().isdigit():
        size = int(response.strip())
        with open("baixado_" + filename, 'wb') as f:
            responsed = 0
            while responsed < size:
                data = sock.recv(4096)
                if not data:
                    break
                f.write(data)
                responsed += len(data)
        print("Arquivo baixado com sucesso.")
    else:
        print(response)

HOST = '127.0.0.1'
PORT = 5000

lock = threading.Lock()
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(s.recv(1024).decode())
        while True:
            opcao, nome, senha = login_menu()
            comando = "LOGIN" if opcao == '1' else "REGISTER"
            s.sendall(f"{comando} {nome} {senha}\n".encode())
            response = s.recv(1024).decode()
            print(response)

            if comando == "REGISTER":
                continue 

            if "Login bem-sucedido" not in response:
                print("Usuário não encontrado!")
                continue  

            stop = False
            while True:
                print("Use comandos: UPLOAD, DOWNLOAD, LIST, DELETE, DELETE_ACCOUNT, QUIT")
                command = input(">>command:").upper().strip()

                if command in ('DOWNLOAD', 'DELETE', 'UPLOAD'):
                    content = input(">>content:").strip()
                    if not content:
                        print("Conteúdo não pode ser vazio.")
                        continue

                if command == "UPLOAD":
                    thread = threading.Thread(target=UPLOAD, args=(f'{command} {content}', lock))
                    #UPLOAD(f'{command} {content}', s, lock=None)
                elif command == "DOWNLOAD":
                    s.sendall(f'{command} {content}\n'.encode())
                    DOWNLOAD(f'{command} {content}', s, lock=None)
                elif command == "QUIT":
                    s.sendall(f'{command}\n'.encode())  
                    print(s.recv(1024).decode()) 
                    stop = True
                    break
                elif command == "LIST":
                    s.sendall(f"{command}\n".encode())
                    response = s.recv(1024).decode()
                    print(response)
                elif command == 'DELETE':
                    s.sendall(f'{command} {content}\n'.encode())
                    response = s.recv(1024).decode()
                    print(response)
                elif command == 'DELETE_ACCOUNT':
                    ...
                else:
                    print('Opção inválida.')

            if stop:
                break

except Exception as e:
    print(e)
    exit(1)
