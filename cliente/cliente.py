from untils import DOWNLOAD, HELP, login_menu, UPLOAD, socket
import threading

HOST = '192.168.1.137'
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

def tratar_comando(command, content, s, lock):
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
            welcome = s.recv(1024)
            if not welcome:
                raise ConnectionResetError("Servidor não respondeu.")
            print(welcome.decode())
        except Exception as e:
            print(f"[ERRO INICIAL] {e}")
            exit(1)

        while True:
            try:
                comando, nome, senha = login_menu()
                s.sendall(f"{comando} {nome} {senha}\n".encode())

                response = s.recv(1024)
                if not response:
                    print("Servidor desconectou após login.")
                    break
                response = response.decode()
                print(response)

                if comando == "REGISTER":
                    continue

                if "Login bem-sucedido" not in response:
                    print("Usuário não encontrado!")
                    continue

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

                    stop = tratar_comando(command, content, s, lock)

                if stop:
                    break

            except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERRO - CONEXÃO PERDIDA] {e}")
                break

except Exception as e:
    print(f"[FALHA FATAL] {e}")
    exit(1)
