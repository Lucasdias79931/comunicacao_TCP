from untils import DOWNLOAD, HELP,login_menu, UPLOAD, socket
import threading


HOST = '192.168.1.137'
PORT = 5000

lock = threading.Lock()
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
                while True:
                    print("Use comandos: UPLOAD, DOWNLOAD, LIST, DELETE, DELETE_ACCOUNT, QUIT")
                    command = input(">>command:").upper().strip()

                    if command in ('DOWNLOAD', 'DELETE', 'UPLOAD'):
                        content = input(">>content:").strip()
                        if not content:
                            print("Conteúdo não pode ser vazio.")
                            continue

                    if command == "UPLOAD":
                        thread = threading.Thread(target=UPLOAD, args=(f'{command} {content}', s, lock))
                        thread.start()

                    elif command == "DOWNLOAD":
                        s.sendall(f'{command} {content}\n'.encode())
                        DOWNLOAD(f'{command} {content}', s)

                    elif command == "QUIT":
                        s.sendall(f'{command}\n'.encode())
                        try:
                            resposta = s.recv(1024)
                            if not resposta:
                                print("Servidor desconectou.")
                            else:
                                print(resposta.decode())
                        except Exception as e:
                            print(f"[ERRO - QUIT] {e}")
                        stop = True
                        break

                    elif command == "LIST":
                        s.sendall(f"{command}\n".encode())
                        try:
                            resposta = s.recv(1024)
                            if not resposta:
                                print("Servidor desconectou.")
                                stop = True
                                break
                            print(resposta.decode())
                        except Exception as e:
                            print(f"[ERRO - LIST] {e}")
                            stop = True
                            break

                    elif command == 'DELETE':
                        s.sendall(f'{command} {content}\n'.encode())
                        try:
                            resposta = s.recv(1024)
                            if not resposta:
                                print("Servidor desconectou.")
                                stop = True
                                break
                            print(resposta.decode())
                        except Exception as e:
                            print(f"[ERRO - DELETE] {e}")
                            stop = True
                            break

                    elif command == 'DELETE_ACCOUNT':
                        s.sendall(f'{command}\n'.encode())
                    else:
                        print('Opção inválida.')

                if stop:
                    break

            except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[ERRO - CONEXÃO PERDIDA] {e}")
                break

except Exception as e:
    print(f"[FALHA FATAL] {e}")
    exit(1)
