import pymysql

# Configurações do banco
host = "127.0.0.1"
port = 3307
usuario = "root"
senha = "raf167725"
banco = "acervo_digital"

try:
    # Conecta ao MySQL
    conexao = pymysql.connect(
        host=host,
        port=port,
        user=usuario,
        password=senha,
        database=banco
    )
    
    print("Conexão bem-sucedida!")
    
    # Fecha a conexão
    conexao.close()
    
except pymysql.MySQLError as e:
    print("Erro ao conectar ao banco de dados:")
    print(e)
