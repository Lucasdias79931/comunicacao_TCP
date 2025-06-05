import socket
import sys
import os

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
        print(f"file <{filepath}> not foud!.")
        return

    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        content = f.read()
    sock.sendall(f"UPLOAD {filename}\n".encode())
    sock.sendall(f"{len(content)}\n".encode())
    sock.sendall(content)
    print(sock.recv(1024).decode())

def DOWNLOAD(command, sock, lock=None):
    response= sock.recv(1024).decode()
    if response.strip().isdigit():
        size = int(response.strip())
        filename = command.strip().split(maxsplit=1)[1]
        with open("baixado_" + filename, 'wb') as f:
            responsed = 0
            while responsed < size:
                data = sock.recv(4096)
                if not data:
                    break
                f.write(data)
                responsed += len(data)
        print("files donwloaded with sucess.")
    else:
        print(response)


HOST = '127.0.0.1'
PORT = 5000

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
                print("User not found!")
                continue  

            
            
            stop = False
            while True:
                print("Use comandos: UPLOAD, DOWNLOAD, LIST, DELETE, DELETE_ACCOUNT, QUIT")
                command = input(">> ").upper()
                if command.startswith("UPLOAD"):
                    UPLOAD(command,s)
                elif command.strip().startswith("DOWNLOAD"):
                    s.sendall(f"{command}\n".encode())
                    DOWNLOAD(command,s)
                
                elif command.strip() == "QUIT":
                    print("Desconectando!!!")
                    s.sendall(f"{command.strip()}\n".encode())  
                    print(s.recv(1024).decode()) 
                    stop = True
                    break

                elif command.strip() == "LIST":
                    s.sendall(f"{command}\n".encode())
                    response = s.recv(1024).decode()
                    print(response)
                else:
                    response = s.recv(4096).decode()
                    print(response)
            if stop:
                break
        
except Exception as e:
    print(e)
    exit(1)


