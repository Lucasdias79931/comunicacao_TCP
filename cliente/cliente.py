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

def menu_principal():
    print("Comandos disponíveis:")
    print("UPLOAD caminho_arquivo")
    print("DOWNLOAD nome_arquivo")
    print("LIST")
    print("DELETE nome_arquivo")
    print("DELETE_ACCOUNT")
    print("QUIT")

def main():
    HOST = '127.0.0.1'
    PORT = 5000

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(s.recv(1024).decode())

            opcao, nome, senha = login_menu()
            comando = "LOGIN" if opcao == '1' else "REGISTER"
            s.sendall(f"{comando} {nome} {senha}\n".encode())
            resposta = s.recv(1024).decode()
            print(resposta)

            if comando == "REGISTER":
                continue  

            if "Login bem-sucedido" not in resposta:
                continue  

            menu_principal()
            
            while True:
                entrada = input(">> ")
                if entrada.strip().startswith("UPLOAD"):
                    partes = entrada.strip().split(maxsplit=1)
                    if len(partes) != 2:
                        print("Formato correto: UPLOAD caminho_arquivo")
                        continue
                    caminho_arquivo = partes[1]
                    if not os.path.isfile(caminho_arquivo):
                        print("Arquivo não encontrado.")
                        continue

                    nome_arquivo = os.path.basename(caminho_arquivo)
                    with open(caminho_arquivo, 'rb') as f:
                        conteudo = f.read()
                    s.sendall(f"UPLOAD {nome_arquivo}\n".encode())
                    s.sendall(f"{len(conteudo)}\n".encode())
                    s.sendall(conteudo)
                    print(s.recv(1024).decode())
                else:
                    s.sendall(f"{entrada}\n".encode())
                    if entrada.strip().startswith("DOWNLOAD"):
                        resposta = s.recv(1024).decode()
                        if resposta.strip().isdigit():
                            tamanho = int(resposta.strip())
                            nome_arquivo = entrada.strip().split(maxsplit=1)[1]
                            with open("baixado_" + nome_arquivo, 'wb') as f:
                                recebido = 0
                                while recebido < tamanho:
                                    data = s.recv(4096)
                                    if not data:
                                        break
                                    f.write(data)
                                    recebido += len(data)
                            print("Arquivo baixado com sucesso.")
                        else:
                            print(resposta)
                    elif entrada.strip() == "QUIT":
                        break
                    else:
                        resposta = s.recv(4096).decode()
                        print(resposta)
            break

if __name__ == "__main__":
    main()
