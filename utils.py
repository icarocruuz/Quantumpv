# utils.py

import mysql.connector
from mysql.connector import Error
import bcrypt

# Funções movidas de proflet.py

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='srv901.hstgr.io',
            user='u676638560_icaro',
            password='jWbtQ:7NR6|u',
            database='u676638560_trader'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def validate_online_login(username, password, access_key):
    connection = None
    try:
        # Usar a função create_connection definida aqui
        connection = create_connection()

        if connection and connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT password, access_key, is_blocked FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            row = cursor.fetchone()

            if row:
                storedHashedPassword, storedAccessKey, isBlocked = row
                print(f"Debug: storedAccessKey: {storedAccessKey}, enteredAccessKey: {access_key}")

                if isBlocked:
                    return False, "Conta está bloqueada. Entre em contato com o suporte."
                
                if not storedAccessKey:
                    return False, "Chave de acesso não encontrada. O login não é permitido sem uma chave de acesso."
                elif storedAccessKey != access_key:
                    return False, "Chave de acesso incorreta. Tente novamente."

                if bcrypt.checkpw(password.encode('utf-8'), storedHashedPassword.encode('utf-8')):
                    return True, None
                else:
                    return False, "Credenciais incorretas. Tente novamente."
            else:
                return False, "Usuário não encontrado."
        else:
            # Erro na conexão já foi logado por create_connection
            return False, "Erro no sistema (conexão DB). Tente novamente mais tarde."

    except Error as e:
        print(f"Erro durante a validação do login: {e}")
        return False, "Erro no sistema (validação). Tente novamente mais tarde."
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Ajustar get_user_session para não depender de variáveis globais de proflet se possível
# Por enquanto, manteremos a estrutura assumindo que UserSession está definido em outro lugar
# (Idealmente, UserSession também poderia ir para um arquivo de modelos/classes)
# Vamos assumir que UserSession será importado onde for necessário.
# sessions = {} # Manter um dict de sessões aqui ou passar como argumento?
# Por simplicidade agora, vamos remover a dependência do 'sessions' global daqui.
def get_user_session(email, sessions_dict):
    # Esta função agora PRECISA receber o dicionário de sessões
    if email not in sessions_dict:
        # Precisa importar UserSession de onde ela estiver definida
        # Exemplo: from Proflet5 import UserSession 
        # Esta importação deve estar no topo do utils.py ou ser passada
        from Proflet5 import UserSession # Tentativa de importação aqui
        sessions_dict[email] = UserSession(email)
    return sessions_dict[email] 