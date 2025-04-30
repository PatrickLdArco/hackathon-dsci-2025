import os
from pathlib import Path
import csv

def listar_pdfs(diretorio):
    """Lista todos os arquivos PDF no diretório especificado."""
    return [f for f in os.listdir(diretorio) if f.endswith('.pdf')]

def ler_csv(caminho):
    """Lê um arquivo CSV e retorna seu conteúdo como uma lista de dicionários."""
    try:
        with open(caminho, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho} não foi encontrado.")
        return []

def main():
    print("=" * 50)
    print("Bem-vindo ao Sistema de Recomendação de Atualizações Educacionais!")
    print("=" * 50)
    
    # Listar arquivos PDF na pasta data/
    data_dir = Path("data")
    pdfs = listar_pdfs(data_dir)
    
    if not pdfs:
        print("Nenhum arquivo PDF encontrado na pasta 'data/'.")
        return
    
    print("\nArquivos disponíveis:")
    for i, pdf in enumerate(pdfs, start=1):
        print(f"{i}. {pdf}")
    
    # Perguntar ao usuário qual arquivo deseja utilizar
    while True:
        try:
            escolha = int(input("\nDigite o número do arquivo que deseja utilizar: "))
            if 1 <= escolha <= len(pdfs):
                arquivo_escolhido = pdfs[escolha - 1]
                break
            else:
                print("Por favor, escolha um número válido.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
    
    print(f"\nVocê escolheu o arquivo: {arquivo_escolhido}")
    
    # Confirmar preenchimento dos CSVs
    print("\nCertifique-se de que os seguintes arquivos foram preenchidos corretamente:")
    print("- data/feedbacks/ajustes.csv")
    print("- data/feedbacks/feedbacks.csv")
    
    confirmacao = input("\nOs arquivos foram preenchidos corretamente? (s/n): ").strip().lower()
    if confirmacao != 's':
        print("Por favor, preencha os arquivos antes de continuar.")
        return
    
    # Ler e printar os ajustes e feedbacks
    print("\nLendo os ajustes e feedbacks...")
    ajustes = ler_csv("data/feedbacks/ajustes.csv")
    feedbacks = ler_csv("data/feedbacks/feedbacks.csv")
    
    print("\nAjustes encontrados:")
    if ajustes:
        for ajuste in ajustes:
            print(ajuste)
    else:
        print("Nenhum ajuste encontrado.")
    
    print("\nFeedbacks encontrados:")
    if feedbacks:
        for feedback in feedbacks:
            print(feedback)
    else:
        print("Nenhum feedback encontrado.")
    
    # Executar o comando (atualmente apenas um print)
    print("\nExecutando o sistema...")
    print("Hello World")  # Substitua este comando pelo que será especificado futuramente

if __name__ == "__main__":
    main()