import os
import sys
import threading
import time
import flet as ft
import time
import threading
from datetime import datetime
import requests
import json
import base64
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image as PILImage
from iqoptionapi.stable_api import IQ_Option
from exnova.stable_api import ExNova
from bullex.stable_api import BulleX
from optinary.stable_api import OptinarY
from broker10.stable_api import Broker10
import numpy as np
from collections import Counter
import flet as ft
import mysql.connector
from mysql.connector import Error
import hashlib
import bcrypt
from Proflet4 import show_initial_screen, show_main_screen, show_login_screen
from Proflet5 import (
    show_loading_overlay, hide_loading_overlay, state,
    UserSession, get_user_session, quantum_theme, initialize_ui_elements,
    log_console, show_splash_screen, show_welcome_screen, show_choice_screen, show_register_screen
)
from Profler1 import get_pares_disponiveis, get_digital_assets_only
from Proflet5 import _create_log_control # Importar helper

# Definições globais de tema Quantum
quantum_theme = {
    "primary": "#6C5CE7",      # Roxo mais suave
    "secondary": "#00D2D3",    # Ciano mais elegante
    "background": "#0F1729",   # Azul escuro mais profissional
    "card_bg": ft.Colors.with_opacity(0.12, "#1A2234"),
    "surface": ft.Colors.with_opacity(0.15, "#1E2738"),
    "success": "#00B894",      # Verde mais suave
    "error": "#FF6B6B",        # Vermelho mais suave
    "text": "#FFFFFF",
    "text_secondary": "#A4B0BE"
}

# Estilos globais
card_style = {
    "bgcolor": quantum_theme["card_bg"],
    "border_radius": 30,
    "padding": ft.padding.all(20),
    "shadow": None,
    "border": None
}

# Estilo dos campos de texto
text_field_style = {
    "border_radius": 15,
    "focused_border_color": quantum_theme["secondary"],
    "bgcolor": ft.Colors.with_opacity(0.05, quantum_theme["surface"]),
    "border_color": ft.Colors.with_opacity(0.2, quantum_theme["secondary"]),
    "color": quantum_theme["text"]
}

# Estilo dos checkboxes
checkbox_style = {
    "fill_color": quantum_theme["secondary"],
    "check_color": quantum_theme["text"],
    "label_style": ft.TextStyle(color=quantum_theme["text"])
}

# Estilo dos dropdowns
dropdown_style = {
    "border_radius": 15,
    "focused_border_color": quantum_theme["secondary"],
    "bgcolor": "#1E2738",
    "border_color": ft.Colors.with_opacity(0.2, quantum_theme["secondary"]),
    "color": quantum_theme["text"]
}


class UserSession:
    def __init__(self, email):
        self.email = email
        self.password = ""
        self.name_var = ""
        self.access_key = ""
        self.account_type_var = "PRACTICE"
        self.entry_value_var = 5.0
        self.stop_win_var = 50.0
        self.stop_loss_var = 50.0
        self.analyze_averages_var = "N"
        self.average_candles_var = 60
        self.use_martingale_var = True
        self.martingale_levels_var = 2
        self.martingale_factor_var = 2.0
        self.use_soros_var = True
        self.soros_levels_var = 1
        self.asset_var = "EURUSD"
        self.strategy_var = 1
        self.start_time_var = "00:00"
        self.end_time_var = "23:59"
        self.use_schedule_var = False
        self.reentry_win_var = False
        self.use_ai_var = False
        self.reverse_direction_var = False
        self.use_stop_loss_var = True
        self.use_stop_win_var = True
        self.use_winning_patterns_var = False
        self.profile_pic = ""
        self.currency = "R$"
        self.account_balance = 0.0
        self.total_profit = 0.0
        # Novos atributos
        self.id = None
        self.username = email
        self.last_access = None
        self.last_ip = None
        self.is_blocked = False
        self.mentorship_key = None
        self.mentoria_approved = False
        # Atributos RSI
        self.use_rsi_var = False
        self.periodo_rsi_var = 14

    def load_configurations(self):
        try:
            connection = mysql.connector.connect(
                host='srv901.hstgr.io',
                user='u676638560_icaro',
                password='jWbtQ:7NR6|u',
                database='u676638560_trader'
            )
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (self.email,))
                row = cursor.fetchone()
                
                if row:
                    # Primeiro, vamos verificar quantas colunas temos
                    columns = [desc[0] for desc in cursor.description]
                    print(f"Colunas disponíveis: {columns}")
                    
                    # Criar um dicionário com os dados
                    data = dict(zip(columns, row))
                    
                    # Atribuir valores usando o dicionário
                    self.id = data.get('id')
                    self.username = data.get('username')
                    self.password = data.get('password')
                    self.last_access = data.get('last_access')
                    self.last_ip = data.get('last_ip')
                    self.access_key = data.get('access_key')
                    self.is_blocked = data.get('is_blocked', False)
                    self.mentorship_key = data.get('mentorship_key')
                    self.mentoria_approved = data.get('mentoria_approved', False)
                    self.account_type_var = data.get('account_type_var', 'PRACTICE')
                    self.entry_value_var = float(data.get('entry_value_var', 5.0))
                    self.stop_win_var = float(data.get('stop_win_var', 50.0))
                    self.stop_loss_var = float(data.get('stop_loss_var', 50.0))
                    self.analyze_averages_var = data.get('analyze_averages_var', 'N')
                    self.average_candles_var = int(data.get('average_candles_var', 60))
                    self.use_martingale_var = bool(data.get('use_martingale_var', True))
                    self.martingale_levels_var = int(data.get('martingale_levels_var', 2))
                    self.martingale_factor_var = float(data.get('martingale_factor_var', 2.0))
                    self.use_soros_var = bool(data.get('use_soros_var', True))
                    self.soros_levels_var = int(data.get('soros_levels_var', 1))
                    self.asset_var = data.get('asset_var', 'EURUSD')
                    self.strategy_var = int(data.get('strategy_var', 1))
                    self.start_time_var = data.get('start_time_var', '00:00')
                    self.end_time_var = data.get('end_time_var', '23:59')
                    self.use_schedule_var = bool(data.get('use_schedule_var', False))
                    self.reentry_win_var = bool(data.get('reentry_win_var', False))
                    self.use_ai_var = bool(data.get('use_ai_var', False))
                    self.reverse_direction_var = bool(data.get('reverse_direction_var', False))
                    self.use_stop_loss_var = bool(data.get('use_stop_loss_var', True))
                    self.use_stop_win_var = bool(data.get('use_stop_win_var', True))
                    self.use_winning_patterns_var = bool(data.get('use_winning_patterns_var', False))
                    self.profile_pic = data.get('profile_pic', '')
                    self.currency = data.get('currency', 'R$')
                    self.account_balance = float(data.get('account_balance', 0.0))
                    self.total_profit = float(data.get('total_profit', 0.0))
                    self.name_var = data.get('name_var', '')
                    # Carregar RSI
                    self.use_rsi_var = bool(data.get('use_rsi_var', False))
                    self.periodo_rsi_var = int(data.get('periodo_rsi_var', 14))

                    cursor.close()
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
        finally:
            if connection.is_connected():
                connection.close()

    def save_configurations(self):
        try:
            connection = mysql.connector.connect(
                host='srv901.hstgr.io',
                user='u676638560_icaro',
                password='jWbtQ:7NR6|u',
                database='u676638560_trader'
            )
            if connection.is_connected():
                cursor = connection.cursor()
                # Atenção: Adicione os novos campos à query SQL
                query = """
                UPDATE users SET
                account_type_var = %s, entry_value_var = %s, stop_win_var = %s, stop_loss_var = %s,
                analyze_averages_var = %s, average_candles_var = %s, use_martingale_var = %s,
                martingale_levels_var = %s, martingale_factor_var = %s, use_soros_var = %s,
                soros_levels_var = %s, asset_var = %s, strategy_var = %s, start_time_var = %s,
                end_time_var = %s, use_schedule_var = %s, reentry_win_var = %s, use_ai_var = %s,
                reverse_direction_var = %s, use_stop_loss_var = %s, use_stop_win_var = %s, use_winning_patterns_var = %s,
                profile_pic = %s,
                use_rsi_var = %s, periodo_rsi_var = %s
                WHERE username = %s
                """
                values = (
                    self.account_type_var, self.entry_value_var, self.stop_win_var, self.stop_loss_var,
                    self.analyze_averages_var, self.average_candles_var, self.use_martingale_var,
                    self.martingale_levels_var, self.martingale_factor_var, self.use_soros_var,
                    self.soros_levels_var, self.asset_var, self.strategy_var, self.start_time_var,
                    self.end_time_var, self.use_schedule_var, self.reentry_win_var, self.use_ai_var,
                    self.reverse_direction_var, self.use_stop_loss_var, self.use_stop_win_var, self.use_winning_patterns_var,
                    self.profile_pic,
                    self.use_rsi_var, self.periodo_rsi_var, # Adicionar valores RSI
                    self.email
                )

                print("Executando consulta SQL:")
                print(query)
                print("Com valores:")
                print(values)

                cursor.execute(query, values)
                connection.commit()
                cursor.close()
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
        finally:
            if connection.is_connected():
                connection.close()

# Funções auxiliares
def save_user_configurations(page, user_session):
    # Atualize os valores da sessão com os valores dos campos de texto e dropdowns
    user_session.account_type_var = account_type_dropdown.value
    user_session.entry_value_var = float(entry_value_texttextfield.value)
    user_session.stop_win_var = float(stop_win_texttextfield.value)
    user_session.stop_loss_var = float(stop_loss_texttextfield.value)
    user_session.analyze_averages_var = analyze_averages_checkbox.value
    user_session.average_candles_var = int(average_candles_texttextfield.value)
    user_session.use_martingale_var = use_martingale_checkbox.value
    user_session.martingale_levels_var = int(martingale_levels_texttextfield.value)
    user_session.martingale_factor_var = float(martingale_factor_texttextfield.value)
    user_session.use_soros_var = use_soros_checkbox.value
    user_session.soros_levels_var = int(soros_levels_texttextfield.value)
    user_session.asset_var = asset_dropdown.value
    user_session.strategy_var = int(strategy_dropdown.value)
    user_session.start_time_var = start_time_texttextfield.value
    user_session.end_time_var = end_time_texttextfield.value
    user_session.use_schedule_var = use_schedule_checkbox.value
    user_session.reentry_win_var = reentry_win_checkbox.value
    user_session.use_ai_var = use_ai_checkbox.value
    user_session.reverse_direction_var = reverse_direction_checkbox.value
    user_session.use_stop_loss_var = use_stop_loss_checkbox.value
    user_session.use_winning_patterns_var = use_winning_patterns_checkbox.value

    # Salve as configurações no banco de dados
    user_session.save_configurations()

    page.snack_bar = ft.SnackBar(
        content=ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=quantum_theme["success"]),
                ft.Text("Configurações salvas com sucesso", color=quantum_theme["text"])
            ]),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.8, quantum_theme["card_bg"])
        ),
        bgcolor=ft.Colors.TRANSPARENT,
        action_color=quantum_theme["secondary"]
    )
    page.snack_bar.open = True
    page.update()

    # Volte para a tela inicial
    show_initial_screen(page, user_session)

def load_user_configurations(page, user_session):
    user_session.load_configurations()

    account_type_dropdown.value = user_session.account_type_var
    email_textfield.value = user_session.email
    password_textfield.value = user_session.password
    name_texttextfield.value = user_session.name_var
    entry_value_texttextfield.value = str(user_session.entry_value_var)
    stop_win_texttextfield.value = str(user_session.stop_win_var)
    stop_loss_texttextfield.value = str(user_session.stop_loss_var)
    analyze_averages_checkbox.value = user_session.analyze_averages_var
    average_candles_texttextfield.value = str(user_session.average_candles_var)
    use_martingale_checkbox.value = user_session.use_martingale_var
    martingale_levels_texttextfield.value = str(user_session.martingale_levels_var)
    martingale_factor_texttextfield.value = str(user_session.martingale_factor_var)
    use_soros_checkbox.value = user_session.use_soros_var
    soros_levels_texttextfield.value = str(user_session.soros_levels_var)
    asset_dropdown.value = user_session.asset_var
    strategy_dropdown.value = str(user_session.strategy_var)
    start_time_texttextfield.value = user_session.start_time_var
    end_time_texttextfield.value = user_session.end_time_var
    use_schedule_checkbox.value = user_session.use_schedule_var
    reentry_win_checkbox.value = user_session.reentry_win_var
    use_ai_checkbox.value = user_session.use_ai_var
    reverse_direction_checkbox.value = user_session.reverse_direction_var
    use_stop_loss_checkbox.value = user_session.use_stop_loss_var
    use_winning_patterns_checkbox.value = user_session.use_winning_patterns_var

    page.update()

# Global variables
access_token = "APP_USR-242081477508554-021215-7da844e2e7da95fc845aef5e9361ce4c-147973828"
payment_id = None
currency = ""
account_balance = 0
total_profit = 0
stop = True
bot_thread = None
API = None
pix_login_time = None
sessions = {}
session_configurations = {}

# Inicialização dos controles globais
balance_label = ft.Text(
    value=f"Saldo: {currency} {account_balance}", 
    size=16, 
    weight="bold",
    color=quantum_theme["text"]
)
total_profit_label = ft.Text(
    value=f"Lucro Total: {currency} {total_profit}", 
    size=16, 
    weight="bold",
    color=quantum_theme["success"]
)
status_label = ft.Text(
    value="Não Conectado", 
    size=16, 
    weight="bold",
    color=quantum_theme["error"]
)
win_label = ft.Text(
    value=f"Vitórias: {0}", 
    size=16,
    color=quantum_theme["success"]
)
loss_label = ft.Text(
    value=f"Derrotas: {0}", 
    size=16,
    color=quantum_theme["error"]
)
result_label = ft.Text(
    value="", 
    size=16, 
    weight="bold",
    color=quantum_theme["text"]
)
connected = False

email_textfield = ft.TextField(
    label="Email", 
    width=300,
    **text_field_style
)
password_textfield = ft.TextField(
    label="Senha", 
    password=True, 
    width=300,
    **text_field_style
)
name_texttextfield = ft.TextField(
    label="Nome", 
    width=300,
    **text_field_style
)
access_key_texttextfield = ft.TextField(
    label="Chave de Acesso", 
    width=300,
    **text_field_style
)
entry_value_texttextfield = ft.TextField(
    value="5.0", 
    width=200, 
    label="Valor de Entrada",
    **text_field_style
)
stop_win_texttextfield = ft.TextField(
    value="50.0", 
    width=200, 
    label="Stop Win",
    **text_field_style
)
stop_loss_texttextfield = ft.TextField(
    value="50.0", 
    width=200, 
    label="Stop Loss",
    **text_field_style
)
average_candles_texttextfield = ft.TextField(
    value="60", 
    width=200, 
    label="Média de Velas",
    **text_field_style
)
martingale_levels_texttextfield = ft.TextField(
    value="2", 
    width=200, 
    label="Níveis de Martingale",
    **text_field_style
)
martingale_factor_texttextfield = ft.TextField(
    value="2.0", 
    width=200, 
    label="Fator de Martingale",
    **text_field_style
)
soros_levels_texttextfield = ft.TextField(
    value="1", 
    width=200, 
    label="Níveis de Soros",
    **text_field_style
)
asset_dropdown = ft.Dropdown(
    width=200,
    options=[],  # Lista vazia, será preenchida após a conexão
    value=None,  # Sem valor inicial
    label="Par de Moedas",
    **dropdown_style
)

strategy_dropdown = ft.Dropdown(
    width=200,
    options=[
        # Mapeamento baseado nos nomes e ordem original + novas funções
        # Valores numéricos são mantidos se o código de execução depender deles
        ft.dropdown.Option("1", text="PRO Invicto | Médio"),         # Mapeado para estrategia_PRO
        ft.dropdown.Option("2", text="Pro Old (TwinT) | Lento"),     # Mapeado para estrategia_twin_towers
        ft.dropdown.Option("3", text="PRO M5 | Lento"),             # Mapeado para estrategia_PRO_m5
        ft.dropdown.Option("4", text="Pro Agressivo (Q) | Lento"), # Mapeado para estrategia_QUARTA
        ft.dropdown.Option("5", text="5 Velas | Médio"),           # Mapeado para estrategia_cinco_velas
        ft.dropdown.Option("6", text="MACD Cross | Rápido"),       # Mapeado para estrategia_macd_crossover
        ft.dropdown.Option("7", text="RSI Reversal | Rápido"),     # Mapeado para estrategia_rsi_reversal
        ft.dropdown.Option("8", text="Origin RSI | Rápido"),       # Mapeado para estrategia_origin_rsi_reversal
        ft.dropdown.Option("9", text="Pattern+Trend | Médio"),    # Mapeado para estrategia_pattern_trend
    ],
    value="1", # Manter valor padrão ou ajustar se necessário
    label="Estratégia",
    **dropdown_style
)

start_time_texttextfield = ft.TextField(
    value="00:00", 
    width=200, 
    label="Hora de Início (HH:MM)",
    **text_field_style
)

end_time_texttextfield = ft.TextField(
    value="23:59", 
    width=200, 
    label="Hora de Término (HH:MM)",
    **text_field_style
)

use_schedule_checkbox = ft.Checkbox(
    label="Usar Agendamento", 
    value=False,
    **checkbox_style
)

reentry_win_checkbox = ft.Checkbox(
    label="Reentrada após Vitória", 
    value=False,
    **checkbox_style
)

use_ai_checkbox = ft.Checkbox(
    label="Usar IA", 
    value=False,
    **checkbox_style
)

reverse_direction_checkbox = ft.Checkbox(
    label="Inverter Direção", 
    value=False,
    **checkbox_style
)

use_stop_loss_checkbox = ft.Checkbox(
    label="Usar Stop Loss", 
    value=True,
    **checkbox_style
)

use_winning_patterns_checkbox = ft.Checkbox(
    label="Usar Padrões Vencedores", 
    value=False,
    **checkbox_style
)

account_type_dropdown = ft.Dropdown(
    width=200,
    options=[
        ft.dropdown.Option("PRACTICE", text="Prática"), 
        ft.dropdown.Option("REAL", text="Real")
    ],
    value="PRACTICE",
    label="Tipo de Conta",
    **dropdown_style
)

analyze_averages_checkbox = ft.Checkbox(
    label="Analisar Médias", 
    value=False,
    **checkbox_style
)

use_martingale_checkbox = ft.Checkbox(
    label="Usar Martingale", 
    value=True,
    **checkbox_style
)

use_soros_checkbox = ft.Checkbox(
    label="Usar Soros", 
    value=True,
    **checkbox_style
)

# Helper functions

def check_pix_payment(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        payment_info = response.json()
        if payment_info["status"] == "approved":
            return True
    return False

def create_pix_charge(event):
    global payment_id
    amount = 50.0
    description = "Test Payment via PIX"
    payment_id, qr_code_base64 = create_pix_charge(amount, description)
    if payment_id:
        qr_img_data = base64.b64decode(qr_code_base64)
        qr_img = PILImage.open(BytesIO(qr_img_data))
        qr_img = qr_img.resize((250, 250))

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        img = ft.Image(src_base64=img_str)
        modal = ft.Container(content=img, padding=10, bgcolor=ft.colors.Color(0xFF001F3F))  # Dark blue
        event.page.overlay.append(modal)
        event.page.update()
    else:
        event.page.dialog = ft.AlertDialog(title=ft.Text("Error creating PIX charge"))
        event.page.dialog.open = True
        event.page.update()

def get_user_session(email):
    if email not in sessions:
        sessions[email] = UserSession(email)
    return sessions[email]

def check_pix_payment_and_login(event):
    global payment_id, pix_login_time
    if payment_id and check_pix_payment(payment_id):
        event.page.dialog = ft.AlertDialog(title=ft.Text("PIX payment confirmed!"))
        event.page.dialog.open = True
        pix_login_time = datetime.now() + timedelta(hours=1)
        show_main_screen(event.page, event.page.user_session)
    else:
        event.page.dialog = ft.AlertDialog(title=ft.Text("PIX payment not confirmed or expired"))
        event.page.dialog.open = True
    event.page.update()

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
        connection = mysql.connector.connect(
            host='srv901.hstgr.io',
            user='u676638560_icaro',
            password='jWbtQ:7NR6|u',
            database='u676638560_trader'
        )

        if connection.is_connected():
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
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False, "Erro no sistema. Tente novamente mais tarde."
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def connect_to_iqoption(email, password):
    API = IQ_Option(email, password)
    check, reason = API.connect()
    return API, check, reason

def init_variables():
    global account_type_var, email_var, password_var, name_var, entry_value_var, stop_win_var, stop_loss_var
    global analyze_averages_var, average_candles_var, use_martingale_var, martingale_levels_var
    global martingale_factor_var, use_soros_var, soros_levels_var, asset_var, strategy_var, type_var
    global start_time_var, end_time_var, use_schedule_var, reentry_win_var, use_ai_var
    global reverse_direction_var, use_stop_loss_var, interval_var, win_count, loss_count, consecutive_losses

    account_type_var = "PRACTICE"
    email_var = ""
    password_var = ""
    name_var = ""
    entry_value_var = 5.0
    stop_win_var = 50.0
    stop_loss_var = 50.0
    analyze_averages_var = "N"
    average_candles_var = 60
    use_martingale_var = True
    martingale_levels_var = 2
    martingale_factor_var = 2.0
    use_soros_var = True
    soros_levels_var = 1
    asset_var = "EURUSD"
    strategy_var = 1
    type_var = "automatic"
    start_time_var = "00:00"
    end_time_var = "23:59"
    use_schedule_var = False
    reentry_win_var = False
    use_ai_var = False
    reverse_direction_var = False
    use_stop_loss_var = True
    interval_var = 5
    win_count = 0
    loss_count = 0
    consecutive_losses = 0
    
init_variables()

def change_values():
    global entry_value, type, stop_win, stop_loss, analyze_averages, average_candles
    global use_martingale, martingale_levels, martingale_factor
    global use_soros, soros_levels, type, use_schedule, reentry_win, use_ai, reverse_direction, use_stop_loss

    entry_value = entry_value_var
    stop_win = stop_win_var
    stop_loss = stop_loss_var
    analyze_averages = analyze_averages_var
    type = type_var
    use_schedule = use_schedule_var
    reentry_win = reentry_win_var
    use_ai = use_ai_var
    reverse_direction = reverse_direction_var
    use_stop_loss = use_stop_loss_var
    if analyze_averages == 'S':
        average_candles = average_candles_var
    else:
        average_candles = 60
    use_martingale = use_martingale_var
    martingale_levels = martingale_levels_var
    martingale_factor = martingale_factor_var
    use_soros = use_soros_var
    soros_levels = soros_levels_var

def start_connection(event, user_session):
    page = event.page # Get page object
    loading_dialog = show_loading_overlay(page, "Conectando...")

    # --- Helper functions for UI updates (run directly from thread) ---
    def _update_status_label(value, color):
        status_label = page.ui.get('status_label')
        if status_label:
            status_label.value = value
            status_label.color = color
            # page.update() # Flet should handle update when called from run_thread target

    def _update_asset_dropdown(options, value):
        asset_dropdown = page.ui.get('asset_dropdown')
        if asset_dropdown:
            asset_dropdown.options = options
            asset_dropdown.value = value
            # page.update()

    def _update_balance_profit_labels(balance_text, profit_text):
        balance_label = page.ui.get('balance_label')
        total_profit_label = page.ui.get('total_profit_label')
        if balance_label:
            balance_label.value = balance_text
        if total_profit_label:
            total_profit_label.value = profit_text
        # page.update()

    def _show_snackbar(text, color):
        page.snack_bar = ft.SnackBar(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE if color == quantum_theme["success"] else ft.icons.ERROR, color=color),
                    ft.Text(text, color=quantum_theme["text"])
                ]),
                padding=10, border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.8, quantum_theme["card_bg"])
            ),
            bgcolor=ft.Colors.TRANSPARENT, action_color=quantum_theme["secondary"]
        )
        page.snack_bar.open = True
        # page.update()
    
    # Helper to hide overlay (needs page update)
    def _hide_loading_overlay_wrapper():
        hide_loading_overlay(page, loading_dialog)
        # page.update() # Flet should handle this
        
    # Função para atualizar a mensagem de carregamento
    def _update_loading_message(message):
        if loading_dialog and hasattr(loading_dialog, 'content') and hasattr(loading_dialog.content, 'content'):
            loading_dialog.content.content.value = message
            page.update()

    # --- Logic executed by page.run_thread --- 
    global API # Still need global here to assign the instance
    api_instance = None
    local_check = False
    local_reason = "Initialization error"

    try:
        # Get required UI elements (values)
        plataforma_dropdown = page.ui.get('plataforma_dropdown')
        email_textfield = page.ui.get('email_textfield')
        password_textfield = page.ui.get('password_textfield')

        if None in [plataforma_dropdown, email_textfield, password_textfield]:
            raise ValueError("Controles de UI essenciais não encontrados para conexão.")

        plataforma = plataforma_dropdown.value
        email = email_textfield.value
        password = password_textfield.value

        if not email or not password:
             # Chamar diretamente
             _show_snackbar("Email e Senha de conexão são obrigatórios!", quantum_theme["error"])
             return # Exit thread

        # Instantiate API
        if plataforma == "IQ Option": api_instance = IQ_Option(email, password)
        elif plataforma == "Exnova": api_instance = ExNova(email, password)
        elif plataforma == "Bullex": api_instance = BulleX(email, password)
        elif plataforma == "Optinary": api_instance = OptinarY(email, password)
        elif plataforma == "Broker10": api_instance = Broker10(email, password)
        else:
            raise ValueError(f"Plataforma não suportada: {plataforma}")

        # Connect with signal error handling
        try:
            local_check, local_reason = api_instance.connect()
        except ValueError as e_conn:
            if "signal only works in main thread" in str(e_conn):
                print(f"AVISO: IQOptionAPI tentou registrar signal handler em background: {e_conn}")
                if api_instance.check_connect():
                    local_check = True
                    local_reason = "Conectado (erro de signal ignorado)"
                    print("Conexão verificada após erro de signal.")
                else:
                    local_check = False
                    local_reason = "Falha na conexão após erro de signal"
                    print("Falha na verificação de conexão pós-signal.")
            else: raise # Re-raise other ValueErrors

        # --- Process connection result ---
        if local_check:
            API = api_instance # Assign to global API
            state['API'] = API # Store in shared state
            print(f"Conectado com sucesso: {local_reason}")
            _update_status_label("Conectado", quantum_theme["success"])

            # --- PRIMEIRO: Mudar o tipo de conta --- 
            _update_loading_message("Alterando tipo de conta...")
            try:
                account_type_to_set = user_session.account_type_var
                print(f"DEBUG: Tentando definir tipo de conta para: {account_type_to_set}")
                API.change_balance(account_type_to_set)
                print(f"DEBUG: Tipo de conta definido para {account_type_to_set}")
            except Exception as change_balance_error:
                 print(f"Erro ao mudar tipo de conta: {change_balance_error}")
                 # Considerar se deve parar aqui ou continuar com saldo padrão
            # ----------------------------------------

            # Fetch ONLY digital pairs with positive payout
            from Profler1 import get_digital_assets_only
            
            # Atualizar mensagem de carregamento
            _update_loading_message("Carregando ativos com payout digital...")
                
            # Buscar somente ativos digitais com payout positivo
            pares_digitais = get_digital_assets_only(API)
            options = []
            asset_value = None
            
            if pares_digitais:
                # Criar as opções para o dropdown com os payouts
                options = [
                    ft.dropdown.Option(par, text=f"{par.replace('-', '/')} | {payout:.1f}%")
                    for par, payout in pares_digitais.items()
                ]
                
                # Ordenar por payout (maior primeiro)
                options.sort(key=lambda x: float(x.text.split('|')[1].strip().replace('%', '')), reverse=True)
                
                # Priorizar valor existente se ainda disponível
                current_asset_value = page.ui.get('asset_dropdown').value if page.ui.get('asset_dropdown') else None
                if current_asset_value in pares_digitais:
                    asset_value = current_asset_value
                else:
                    # Se não, usar o primeiro ativo da lista ordenada
                    asset_value = options[0].key if options else None
            else:
                print("AVISO: Nenhum ativo digital com payout positivo encontrado!")
                
            _update_asset_dropdown(options, asset_value)

            # Fetch balance/currency (can also block)
            _update_loading_message("Obtendo saldo e informações da conta...")
            temp_currency = "$"
            temp_account_balance = 0.0
            try:
                if isinstance(API, IQ_Option): # Use API here (already assigned)
                    profile = json.loads(json.dumps(API.get_profile_ansyc()))
                    temp_currency = str(profile['currency_char'])
                    temp_account_balance = float(API.get_balance())
                elif isinstance(API, (ExNova, BulleX, OptinarY, Broker10)):
                    temp_currency = API.get_currency()
                    temp_account_balance = API.get_balance()

                # --- Corrigir símbolo da moeda ---
                if temp_currency == "BRL":
                    print(f"DEBUG: Moeda 'BRL' detectada, substituindo por 'R$'.") # DEBUG
                    temp_currency = "R$"
                # ----------------------------------

                # DEBUG: Imprimir a moeda retornada pela API (após correção)
                print(f"DEBUG: Moeda final a ser usada: {temp_currency}")
                print(f"DEBUG: Saldo retornado pela API (APÓS change_balance): {temp_account_balance:.2f}") # DEBUG adicional
            except Exception as balance_error:
                print(f"Erro ao obter saldo/moeda: {balance_error}")
            
            # --- Atualizar sessão e estado com a moeda correta ---
            user_session.currency = temp_currency
            state['currency'] = temp_currency # Atualizar estado global também
            # -----------------------------------------------------
            user_session.account_balance = temp_account_balance
            state['account_balance'] = temp_account_balance # Atualizar estado global
            
            # Formatar labels com a moeda correta
            balance_text = f"Saldo: {user_session.currency} {user_session.account_balance:.2f}"
            profit_text = f"Lucro Total: {user_session.currency} {user_session.total_profit:.2f}" # Assuming total_profit comes from session or state
            _update_balance_profit_labels(balance_text, profit_text)
            
            # Show success message com informação específica sobre ativos digitais
            _update_loading_message("Concluindo configuração...")
            msg = f"Conectado! {len(pares_digitais if pares_digitais else [])} paridades digitais com payout disponíveis."
            _show_snackbar(msg, quantum_theme["success"])
            
            # --- ADICIONADO: Atualizar conteúdo do botão para CONECTADO --- 
            connect_button = event.control
            if connect_button:
                connect_button.content = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.CLOUD_DONE, color=quantum_theme["success"]), # Ícone de sucesso
                        ft.Text("CONECTADO", size=16, weight="bold", color=quantum_theme["text"]) # Texto atualizado
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    # Reutilizar estilo (padding/gradient) do botão original para consistência
                    padding=10,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[
                            quantum_theme["primary"],
                            ft.Colors.with_opacity(0.8, quantum_theme["secondary"])
                        ],
                    ),
                )
                connect_button.disabled = False # Garantir que está habilitado
            # --- FIM ATUALIZAR BOTÃO --- 
            
            # Explicitly update page once after all changes
            page.update()

        else:
            # Handle connection failure
            print(f"Falha ao conectar: {local_reason}")
            _update_status_label("Não Conectado", quantum_theme["error"])
            _show_snackbar(f"Falha ao conectar: {local_reason}", quantum_theme["error"])
            page.update() # Update page after failure updates

    except Exception as e_thread:
        # Catch any other error within the thread
        print(f"Erro na thread de conexão: {e_thread}")
        _update_status_label("Erro Conexão", quantum_theme["error"])
        _show_snackbar(f"Erro de conexão: {str(e_thread)}", quantum_theme["error"])
        # Explicitly update page after error
        page.update()
    finally:
        # Sempre garantir que o overlay de loading será fechado
        try:
            _hide_loading_overlay_wrapper()
            page.update()
        except:
            pass

def main(page: ft.Page):
    page.title = "Quantum Trader v3.0"
    page.window_width = 450
    page.window_height = 850
    page.window_resizable = False
    page.window_maximizable = False
    page.theme_mode = "dark"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inicializar UI a partir de Proflet5 e atribuir
    page.ui = initialize_ui_elements()

    # Configurar PubSub (copiado/adaptado de onde estava)
    log_list_view_ref = ft.Ref[ft.ListView]()
    def on_log_update(message):
        """Callback do PubSub: Adiciona o novo log diretamente ao ListView (TESTE SIMPLIFICADO)."""
        print(f"DEBUG: PubSub 'update_log' recebido. Tentando adicionar log SIMPLES.") # DEBUG
        
        log_list_view = page.ui.get('log_list_view')
        if not log_list_view or not isinstance(log_list_view, ft.ListView):
            print("ERRO CRÍTICO [on_log_update]: log_list_view não encontrado ou não é ListView em page.ui!")
            return
        
        # Print do ID do objeto no callback
        print(f"DEBUG [on_log_update]: Atualizando log_list_view com ID: {id(log_list_view)}")

        try:
            # --- TESTE: Adicionar texto simples --- 
            timestamp = datetime.now().strftime("%H:%M:%S")
            simple_text_control = ft.Text(f"[{timestamp}] Log de TESTE!", color="yellow", size=14)
            
            # Limitar o número máximo de logs exibidos
            max_log_display = 200 
            if len(log_list_view.controls) >= max_log_display:
                log_list_view.controls.pop(0)

            # Adicionar o novo controle ao ListView
            log_list_view.controls.append(simple_text_control)
            print(f"DEBUG [on_log_update]: Controle de TESTE adicionado. Total: {len(log_list_view.controls)}")
            # --- FIM DO TESTE --- 

            # Tentar rolar para o final (essencial após adicionar)
            if hasattr(log_list_view, 'scroll_to'):
                log_list_view.scroll_to(offset=-1, duration=300)
            
            # Atualizar APENAS o ListView para refletir a mudança
            if log_list_view and hasattr(log_list_view, 'update'):
                 log_list_view.update()
                 print("DEBUG [on_log_update]: log_list_view.update() chamado.") # DEBUG
            else:
                 print("ERRO [on_log_update]: log_list_view ou log_list_view.update não disponível.")

        except Exception as e_log_update:
            print(f"ERRO [on_log_update]: Exceção ao processar/adicionar log de TESTE: {e_log_update}")

    # --- Função de Callback para Atualização de Estatísticas --- #
    def on_stats_update(message):
        print(f"Recebido PubSub: {message}") # DEBUG
        # Acessar labels da UI principal
        win_label = page.ui.get('win_label')
        loss_label = page.ui.get('loss_label')
        total_profit_label = page.ui.get('total_profit_label')
        balance_label = page.ui.get('balance_label')

        # Acessar dados do estado global
        win_count = state.get('win_count', 0)
        loss_count = state.get('loss_count', 0)
        total_profit = state.get('total_profit', 0.0)
        account_balance = state.get('account_balance', 0.0)
        currency = state.get('currency', 'R$') # Usar fallback se necessário

        # Atualizar valores dos labels se existirem
        updated_controls = []
        if win_label:
            win_label.value = f"Vitórias: {win_count}"
            updated_controls.append(win_label)
        if loss_label:
            loss_label.value = f"Derrotas: {loss_count}"
            updated_controls.append(loss_label)
        if total_profit_label:
            total_profit_label.value = f"Lucro Total: {currency} {total_profit:.2f}"
            updated_controls.append(total_profit_label)
        if balance_label:
            balance_label.value = f"Saldo: {currency} {account_balance:.2f}"
            updated_controls.append(balance_label)

        print(f"Atualizando stats na UI: W:{win_count} L:{loss_count} P:{total_profit:.2f} B:{account_balance:.2f}") # DEBUG
        
        # Atualizar apenas os controles modificados
        if updated_controls:
            page.update(*updated_controls) # Passa a lista de controles para atualizar
            print("DEBUG [on_stats_update]: page.update(controles_especificos) chamado.")
        # else: # Remover a chamada geral a page.update()
        #    page.update()
    # ------------------------------------------------------- #

    # --- Assinar os tópicos --- #
    page.pubsub.subscribe_topic("update_log", on_log_update)
    page.pubsub.subscribe_topic("update_stats", on_stats_update) # Assinar novo tópico
    print(f"Inscrito nos tópicos PubSub {'update_log'} e {'update_stats'}") # DEBUG
    # -------------------------- #

    # Configurar roteamento
    def route_change(route):
        print(f"Mudando rota de {page.route} para: {route}") # Log da rota atual e nova

        # --- Parar animações de telas anteriores --- #
        if page.route == "/splash": # Se estava no splash
            state['animating_splash'] = False
            print("Flag 'animating_splash' definida como False.")
        if page.route == "/choice": # Se estava na tela de escolha
            state['animating_choice_title'] = False
            state['animating_login_button'] = False 
            state['animating_register_button'] = False 
            print("Flags de animação da tela Choice definidas como False.")
        if page.route == "/initial_screen": # Se estava na tela inicial
            state['animating_appbar_title'] = False
            state['animating_fab_icon'] = False
            print("Flags de animação da tela Initial definidas como False.")
        # ------------------------------------------ #

        page.views.clear()
        
        # --- LÓGICA DE ROTEAMENTO ORIGINAL --- #
        # (Mantenha a lógica de autenticação como está)
        # ...

        # Mapeamento de rotas para funções
        route_map = {
            "/login": show_login_screen, # Função importada de Proflet4/3
            "/initial_screen": lambda p: show_initial_screen(p, get_user_session(state.get('current_user_email'))), # Usa lambda para passar a sessão
            "/main_screen": lambda p: show_main_screen(p, get_user_session(state.get('current_user_email'))), # Usa lambda
            "/welcome": show_welcome_screen, # Novas telas de Proflet5
            "/choice": show_choice_screen,
            "/register": show_register_screen,
        }

        # Tenta obter a função correspondente à rota atual (route = novo destino)
        view_function = route_map.get(route.route) # Usar route.route para obter a string da rota

        if view_function:
            try:
                view_function(page) # Chama a função para construir a view
            except Exception as e_view:
                print(f"Erro ao construir a view para {route}: {e_view}")
                # Fallback: Ir para uma tela de erro ou login?
                # Se der erro ao construir uma view, voltar para welcome pode ser mais seguro
                show_welcome_screen(page)
        else:
            # Se nenhuma rota corresponder, ir para Welcome como padrão inicial pós-splash
            print(f"Rota desconhecida: {route}. Exibindo Welcome Screen.")
            show_welcome_screen(page)

        page.update()

    page.on_route_change = route_change
    # Tirar go("/login") daqui para deixar o splash controlar
    # page.go("/login") 
    # Em vez disso, iniciar com o splash screen
    show_splash_screen(page) # Usar a função de Proflet5

# Função on_file_picked e outras auxiliares (verificar duplicação com Proflet5)
# ...

# Ponto de entrada
# if __name__ == "__main__":
#     ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=8550)

# Cria a instância da aplicação Flet que uvicorn pode usar
app = ft.app(target=main, view=ft.WEB_BROWSER)




