import mysql.connector
import os
import sys

def criar_banco_dados():
    try:
        # Conectar ao MySQL sem especificar um banco de dados
        conexao = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password="raf167725"
        )
        
        cursor = conexao.cursor()
        
        # Criar o banco de dados se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS acervo_digital")
        print("Banco de dados 'acervo_digital' criado ou já existente.")
        
        # Fechar a conexão
        cursor.close()
        conexao.close()
        
        print("Inicialização do banco de dados concluída com sucesso!")
        return True
        
    except mysql.connector.Error as erro:
        print(f"Erro ao criar o banco de dados: {erro}")
        return False

def executar_script_sql():
    try:
        # Caminho para o arquivo SQL
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_setup.sql')
        
        # Verificar se o arquivo existe
        if not os.path.exists(script_path):
            print(f"Arquivo SQL não encontrado: {script_path}")
            return False
        
        # Ler o conteúdo do arquivo SQL
        with open(script_path, 'r') as arquivo:
            script_sql = arquivo.read()
        
        # Conectar ao MySQL com o banco de dados acervo_digital
        conexao = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password="raf167725",
            database="acervo_digital"
        )
        
        cursor = conexao.cursor()
        
        # Executar cada comando SQL separadamente
        comandos = script_sql.split(';')
        for comando in comandos:
            if comando.strip():
                cursor.execute(comando + ';')
        
        # Commit das alterações
        conexao.commit()
        
        # Fechar a conexão
        cursor.close()
        conexao.close()
        
        print("Script SQL executado com sucesso!")
        return True
        
    except mysql.connector.Error as erro:
        print(f"Erro ao executar o script SQL: {erro}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Inicializando o banco de dados...")
    
    # Criar o banco de dados
    if criar_banco_dados():
        # Executar o script SQL
        if executar_script_sql():
            print("Banco de dados inicializado com sucesso!")
            sys.exit(0)
        else:
            print("Falha ao executar o script SQL.")
            sys.exit(1)
    else:
        print("Falha ao criar o banco de dados.")
        sys.exit(1)