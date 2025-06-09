import zipfile
import os
import sys

diretorio = sys.argv[1]

def compactar_diretorio(diretorio_origem, nome_arquivo_zip):
    
    with zipfile.ZipFile(nome_arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for raiz, _, arquivos in os.walk(diretorio_origem):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                caminho_relativo = os.path.relpath(caminho_completo, diretorio_origem)
                zipf.write(caminho_completo, caminho_relativo)


compactar_diretorio(diretorio,'dados.zip')