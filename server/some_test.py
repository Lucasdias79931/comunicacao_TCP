import os 
import sys

file = sys.argv[1]

if os.path.exists(file):
    print(f'Pacotes: <{os.path.getsize(file) // 1024}>')
else:
    print(f'<{file}> não encontrado!\nverifique o caminho correto')