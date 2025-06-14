from untils import DOWNLOAD, HELP, login_menu, UPLOAD, socket
import threading

HOST = '192.168.14.129'
PORT = 5000

lock = threading.Lock()

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

    elif command == "LIST":
        s.sendall(f"{command}\n".encode())
        resposta = receber_mensagem(s)
        if resposta: print(resposta)
        else: return True

    elif command == "DELETE":
        s.sendall(f'{command} {content}\n'.encode())
        resposta = receber_mensagem(s)
        if resposta: print(resposta)
        else: return True

    elif command == "DELETE_ACCOUNT":
        s.sendall(f'{command}\n'.encode())
        resposta = receber_mensagem(s)
   
    elif command == "QUIT":
        s.sendall(f'{command}\n'.encode())
        resposta = receber_mensagem(s)
        if resposta: print(resposta)
        return True

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
                comando, nome, senha = login_menu()
                s.sendall(f"{comando} {nome} {senha}\n".encode())
                print(comando.upper())
                response = s.recv(1024)
                if not response:
                    print("Servidor desconectou após login.")
                    break
                response = response.decode()
                print(response)

                if comando == "REGISTRAR":

                    continue

                if "Login bem-sucedido" not in response:
                    print("Usuário não encontrado!")
                    continue

                stop = False
                while not stop:
                    print("Use comandos: UPLOAD, DOWNLOAD, LIST, DELETE, DELETE_ACCOUNT, QUIT, HELP")
                    command = input(">>command:").upper().strip()
                    if command == 'HELP':
                        HELP()
                        continue
                    

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
