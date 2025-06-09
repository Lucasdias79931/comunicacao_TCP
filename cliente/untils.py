import os
import socket
from tqdm import tqdm
import zipfile

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
    if not os.path.isfile(filepath) and not os.path.isdir(filepath):
        print(f"Arquivo <{filepath}> não encontrado.")
        return

    
    try:
        
        

        if os.path.isdir(filepath):
            compactar_diretorio(filepath, f'{filepath}.zip')
            filepath = f'{filepath}.zip'
        
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
        else:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
        sock.sendall(f"UPLOAD {filename}\n".encode())
        sock.sendall(f"{filesize}\n".encode())
        with open(filepath, 'rb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Enviando {filename}") as barra:

         
            while True:

                dado = f.read(1024*64)
                
                if not dado:
                    break
                sock.sendall(dado)
                
                barra.update(len(dado)) 

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



def compactar_diretorio(diretorio_origem, nome_arquivo_zip):
    
    with zipfile.ZipFile(nome_arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for raiz, _, arquivos in os.walk(diretorio_origem):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                caminho_relativo = os.path.relpath(caminho_completo, diretorio_origem)
                zipf.write(caminho_completo, caminho_relativo)
