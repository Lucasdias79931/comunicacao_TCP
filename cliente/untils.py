import os
import socket
from tqdm import tqdm


def HELP():
    print("UPLOAD - Digite o comando, em seguida espere o campo 'content' para digitar o path completo do arquivo")
    print("DOWNLOAD - Digite o comando, em seguida espere o campo 'content' para digitar o nome do arquivo")
    print("DELETE - Digite o nome do arquivo que será deletado")
    print("DELETE_ALCCOUTT - Deleta conta e todos os arquivos vinculados")
    print("QUIT - Desconectar da conta e do servidor")
    print('Entrar - Digite para fazer login')
    print('Registrar - Digite para registrar conta')

def login_menu():
    while True:

        opcao = input("1: Entrar\n2: Registrar\nEscolha: ").upper()
        
        if opcao == 'HELP':
            HELP()
            continue

        if opcao in ('ENTRAR', 'REGISTRAR'):
            nome = input("NOME>> ")
            senha = input("SENHA>> ")
            return opcao, nome, senha
        else:
            print(f"Opcao inválida: {opcao}\ndigite 'HELP' parar ajuda!")

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
        #ith open(filepath, 'rb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Enviando {filename}") as barra:

        with open(filepath, 'rb') as f:
            enviado = 0
            while True:

                    dado = f.read(4096*1024)
                    if not dado:
                        break
                    sock.sendall(dado)
                    enviado += len(dado)
         #               barra.update(len(dado)) 

        resposta = sock.recv(1024)
        if not resposta:
            print("Servidor desconectou durante o upload.")
            return
        print(resposta.decode())

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
            with open("baixado_" + filename, 'wb') as f:
                dado = 0
                while dado < size:
                    data = sock.recv(4096)
                    if not data:
                        print("Conexão perdida durante o download.")
                        return
                    f.write(data)
                    dado += len(data)
            print("Arquivo baixado com sucesso.")
        else:
            print(response)
    except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[ERRO - DOWNLOAD] {e}")
    