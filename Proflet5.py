import flet as ft
import time
import threading
from datetime import datetime
import os
import sys
import threading
import time
import requests
import json
import base64
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image as PILImage
import numpy as np
from collections import Counter
import mysql.connector
from mysql.connector import Error
import hashlib
import bcrypt
# Imports para animação de cor
import colorsys
import math

# --- Funções Auxiliares de Cor ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"

def interpolate_color(color1_rgb, color2_rgb, factor):
    r1, g1, b1 = color1_rgb
    r2, g2, b2 = color2_rgb
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return (r, g, b)
# --- Fim Funções Auxiliares de Cor ---

# Imports das APIs das corretoras
from iqoptionapi.stable_api import IQ_Option
from exnova.stable_api import ExNova
from bullex.stable_api import BulleX
from optinary.stable_api import OptinarY
from broker10.stable_api import Broker10

# Imports de outros módulos do projeto (Exemplos)
# Supondo uma estrutura mais organizada:
# from config import quantum_theme, card_style, text_field_style, checkbox_style, dropdown_style
# from session import UserSession, sessions, get_user_session
# from ui_elements import create_ui_elements # Função que cria e retorna o dict de elementos
# from auth import show_login_screen, validate_login, on_login_click # Passar ui_elements para eles
# from screens import show_initial_screen, show_main_screen
# from user_profile import on_file_picked, file_picker_handler, save_profile_picture
# from api_utils import start_connection, atualizar_ativos_disponiveis, identificar_plataforma, API # Gerenciar API aqui
# from utils import show_loading_overlay, hide_loading_overlay, animate_page_transition
# from state import state # Dicionário para estado global

# --- Definições Globais (Mover para arquivos dedicados seria melhor) --- #

# 1. Configuração de Tema e Estilo (Mover para config.py)
quantum_theme = {
    "primary": "#4A7BFE",      # Azul vibrante
    "secondary": "#00D2D3",    # Manter Ciano/Turquesa
    "background": "#0A0F1A",   # Fundo bem escuro
    "card_bg": "#161C2D",      # Fundo sólido escuro para cards
    "surface": "#1D2A4C",      # Superfície ligeiramente mais clara
    "success": "#00B894",      # Manter Verde
    "error": "#FF6B6B",        # Manter Vermelho
    "text": "#FFFFFF",         # Manter Branco
    "text_secondary": "#B0B8D1" # Cinza-azulado claro
}

card_style = {
    "bgcolor": quantum_theme["card_bg"], # Usar cor sólida do tema
    "border_radius": 15, # Manter bordas arredondadas (ou ajustar se necessário)
    "padding": ft.padding.all(15), # Ajustar padding se necessário
    "shadow": None, # Sem sombra explícita na imagem
    # Manter a borda sutil, usando a cor 'surface' que é ligeiramente mais clara que 'card_bg'
    "border": ft.border.all(1, ft.colors.with_opacity(0.5, quantum_theme["surface"])) 
}

text_field_style = {
    "border_radius": 15,
    "focused_border_color": quantum_theme["secondary"],
    "bgcolor": ft.Colors.with_opacity(0.05, quantum_theme["surface"]),
    "border_color": ft.Colors.with_opacity(0.2, quantum_theme["secondary"]),
    "color": quantum_theme["text"]
}

checkbox_style = {
    "fill_color": quantum_theme["secondary"],
    "check_color": quantum_theme["text"],
    "label_style": ft.TextStyle(color=quantum_theme["text"])
}

dropdown_style = {
    "border_radius": 15,
    "focused_border_color": quantum_theme["secondary"],
    "bgcolor": "#1E2738",
    "border_color": ft.Colors.with_opacity(0.2, quantum_theme["secondary"]),
    "color": quantum_theme["text"]
}

# 2. Classe UserSession (Mover para session.py)
class UserSession:
    def __init__(self, email):
        self.email = email
        self.password = "" # Não armazenar senha descriptografada idealmente
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
        self.use_winning_patterns_var = False
        self.profile_pic = "" # Base64 da imagem
        self.currency = "R$" # Pode ser atualizado após conexão
        self.account_balance = 0.0 # Pode ser atualizado após conexão
        self.id = None
        self.username = email
        self.last_access = None
        self.last_ip = None
        self.is_blocked = False
        self.mentorship_key = None
        self.mentoria_approved = False
        self.analyze_all_pairs_var: bool = False

    def load_configurations(self):
        """Carrega configurações do banco de dados para esta sessão."""
        connection = None # Definir connection como None inicialmente
        try:
            # Usar uma função helper para criar conexão seria melhor
            connection = mysql.connector.connect(
                host='srv901.hstgr.io',
                user='u676638560_icaro',
                password='jWbtQ:7NR6|u',
                database='u676638560_trader'
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True) # Usar dictionary=True
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (self.email,))
                data = cursor.fetchone()

                if data:
                    print(f"Dados carregados para {self.email}: {list(data.keys())}")
                    # Atribuir valores com .get() para evitar KeyErrors
                    self.id = data.get('id')
                    self.username = data.get('username', self.email)
                    # self.password = data.get('password') # Não carregar hash da senha aqui
                    self.last_access = data.get('last_access')
                    self.last_ip = data.get('last_ip')
                    self.access_key = data.get('access_key')
                    self.is_blocked = bool(data.get('is_blocked', 0))
                    self.mentorship_key = data.get('mentorship_key')
                    self.mentoria_approved = bool(data.get('mentoria_approved', 0))
                    self.account_type_var = data.get('account_type_var', 'PRACTICE')
                    self.entry_value_var = float(data.get('entry_value_var', 5.0))
                    self.stop_win_var = float(data.get('stop_win_var', 50.0))
                    self.stop_loss_var = float(data.get('stop_loss_var', 50.0))
                    self.analyze_averages_var = data.get('analyze_averages_var', 'N')
                    self.average_candles_var = int(data.get('average_candles_var', 60))
                    self.use_martingale_var = bool(data.get('use_martingale_var', 1))
                    self.martingale_levels_var = int(data.get('martingale_levels_var', 2))
                    self.martingale_factor_var = float(data.get('martingale_factor_var', 2.0))
                    self.use_soros_var = bool(data.get('use_soros_var', 1))
                    self.soros_levels_var = int(data.get('soros_levels_var', 1))
                    self.asset_var = data.get('asset_var', 'EURUSD')
                    self.strategy_var = int(data.get('strategy_var', 1))
                    self.start_time_var = data.get('start_time_var', '00:00')
                    self.end_time_var = data.get('end_time_var', '23:59')
                    self.use_schedule_var = bool(data.get('use_schedule_var', 0))
                    self.reentry_win_var = bool(data.get('reentry_win_var', 0))
                    self.use_ai_var = bool(data.get('use_ai_var', 0))
                    self.reverse_direction_var = bool(data.get('reverse_direction_var', 0))
                    self.use_stop_loss_var = bool(data.get('use_stop_loss_var', 1))
                    self.use_winning_patterns_var = bool(data.get('use_winning_patterns_var', 0))
                    self.profile_pic = data.get('profile_pic', '')
                    self.currency = data.get('currency', 'R$')
                    self.account_balance = float(data.get('account_balance', 0.0))
                    self.analyze_all_pairs_var = bool(data.get('analyze_all_pairs_var', 0))
                else:
                    print(f"Nenhuma configuração encontrada no BD para {self.email}. Usando padrões.")

                cursor.close()
        except Error as e:
            print(f"Erro ao conectar/ler MySQL em load_configurations: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()

    def save_configurations(self):
        """Salva as configurações atuais da sessão no banco de dados."""
        connection = None # Definir connection como None inicialmente
        try:
            # Usar uma função helper para criar conexão seria melhor
            connection = mysql.connector.connect(
                host='srv901.hstgr.io',
                user='u676638560_icaro',
                password='jWbtQ:7NR6|u',
                database='u676638560_trader'
            )
            if connection.is_connected():
                cursor = connection.cursor()
                # Query com todos os campos atualizáveis
                query = """
                UPDATE users SET
                    account_type_var = %s, entry_value_var = %s, stop_win_var = %s, stop_loss_var = %s,
                    analyze_averages_var = %s, average_candles_var = %s, use_martingale_var = %s,
                    martingale_levels_var = %s, martingale_factor_var = %s, use_soros_var = %s,
                    soros_levels_var = %s, asset_var = %s, strategy_var = %s, start_time_var = %s,
                    end_time_var = %s, use_schedule_var = %s, reentry_win_var = %s, use_ai_var = %s,
                    reverse_direction_var = %s, use_stop_loss_var = %s, use_winning_patterns_var = %s,
                    profile_pic = %s, currency = %s, account_balance = %s, analyze_all_pairs_var = %s
                WHERE username = %s
                """
                # Montar tupla de valores na ordem correta
                # Converter booleanos para 0/1 para o BD, se necessário
                values = (
                    self.account_type_var, self.entry_value_var, self.stop_win_var, self.stop_loss_var,
                    self.analyze_averages_var, self.average_candles_var, int(self.use_martingale_var),
                    self.martingale_levels_var, self.martingale_factor_var, int(self.use_soros_var),
                    self.soros_levels_var, self.asset_var, self.strategy_var, self.start_time_var,
                    self.end_time_var, int(self.use_schedule_var), int(self.reentry_win_var), int(self.use_ai_var),
                    int(self.reverse_direction_var), int(self.use_stop_loss_var), int(self.use_winning_patterns_var),
                    self.profile_pic, self.currency, self.account_balance, int(self.analyze_all_pairs_var),
                    self.email
                )

                print(f"Salvando configurações para {self.email}")
                # print(f"Valores: {values}") # Debug
                cursor.execute(query, values)
                connection.commit()
                print(f"Configurações salvas com sucesso para {self.email}")
                cursor.close()
            else:
                print("Não foi possível conectar ao BD para salvar configurações.")
        except Error as e:
            print(f"Erro ao conectar/salvar MySQL em save_configurations: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()

# 3. Gerenciamento de Sessão (Mover para session.py)
sessions = {} # Dicionário para armazenar sessões ativas

def get_user_session(email):
    """Obtém ou cria uma nova sessão de usuário."""
    if email not in sessions:
        print(f"Criando nova sessão para {email}")
        sessions[email] = UserSession(email)
        sessions[email].load_configurations() # Carrega config ao criar sessão
    else:
        print(f"Usando sessão existente para {email}")
    return sessions[email]

# 4. Estado Global da Aplicação (Mover para state.py)
state = {
    "stop": True, # Flag para parar/iniciar o bot
    "total_profit": 0.0,
    "win_count": 0,
    "loss_count": 0,
    "consecutive_losses": 0,
    "soros_level": 0,
    "soros_value": 0.0,
    "current_op_profit": 0.0, # Lucro da operação atual para Soros
    "type": "automatic", # Tipo de operação (binary/digital/automatic)
    "winning_patterns": {}, # Dicionário para padrões vencedores
    "status": "Desconectado", # Status da conexão com a corretora
    "api_instance": None, # Instância da API da corretora conectada
    'log_entries': [],
    'animating_splash': False, # Flag para controlar animação
}

# 5. Instância da API (Gerenciar em api_utils.py)
# API = None # Definir API como None inicialmente

# 6. Elementos da UI (Definir/Criar em ui_elements.py ou aqui temporariamente)
# É crucial que estes sejam definidos ANTES de serem usados nas funções de tela/lógica
# ui_elements = {} # REMOVED GLOBAL DICTIONARY

def initialize_ui_elements():
    """Cria as instâncias dos controles Flet e retorna o dicionário ui_elements."""
    # Estilos para TextFields de Login (inspirado em VaultCash)
    login_textfield_style = {
        # "filled": False, # Remover preenchimento
        # "bgcolor": ft.colors.with_opacity(0.04, quantum_theme["background"]),
        "border": ft.InputBorder.UNDERLINE, # Usar borda underline
        "border_radius": 5, # Menos arredondado que o botão
        "border_color": ft.colors.with_opacity(0.5, quantum_theme["text_secondary"]), # Cinza claro padrão
        "focused_border_color": quantum_theme["primary"], # Cor primária ao focar
        # "label_style": ft.TextStyle(color=quantum_theme["text_secondary"]),
        "text_style": ft.TextStyle(color=quantum_theme["text"]),
        "cursor_color": quantum_theme["secondary"],
        "content_padding": ft.padding.symmetric(vertical=10, horizontal=5) # Ajustar padding
    }
    
    # Usando um dicionário local para evitar problemas com estado global
    ui_elements = {
        # --- Tela de Login --- #
        # Labels serão criados separadamente na tela
        'email_textfield_login': ft.TextField(
            hint_text="Digite seu usuário",
            keyboard_type=ft.KeyboardType.EMAIL,
            # prefix_icon=ft.icons.PERSON_OUTLINE, # Remover ícone
            **login_textfield_style
        ),
        'password_textfield_login': ft.TextField(
            hint_text="Digite sua senha",
            password=True,
            can_reveal_password=True,
            # prefix_icon=ft.icons.LOCK_OUTLINE, # Remover ícone
            **login_textfield_style
        ),
        'access_key_texttextfield_login': ft.TextField(
            hint_text="Digite sua chave",
            # prefix_icon=ft.icons.KEY_OUTLINED, # Remover ícone
             **login_textfield_style
        ),

        # Tela Principal / Configurações
        "plataforma_dropdown": ft.Dropdown(width=300, options=[
                ft.dropdown.Option("IQ Option", text="IQ Option"), ft.dropdown.Option("Exnova", text="Exnova"),
                ft.dropdown.Option("Bullex", text="Bullex"), ft.dropdown.Option("Optinary", text="Optinary"),
                ft.dropdown.Option("Broker10", text="Broker10"),
            ], value="IQ Option", label="Plataforma", **dropdown_style),
        "email_textfield": ft.TextField(label="Email (Conexão)", width=300, prefix_icon=ft.icons.EMAIL, **text_field_style),
        "password_textfield": ft.TextField(label="Senha (Conexão)", password=True, width=300, prefix_icon=ft.icons.LOCK, **text_field_style),
        "account_type_dropdown": ft.Dropdown(width=300, options=[
                ft.dropdown.Option("PRACTICE", text="Prática"), ft.dropdown.Option("REAL", text="Real")
            ], value="PRACTICE", label="Tipo de Conta", **dropdown_style),
        "status_label": ft.Text("Desconectado", size=14, weight="bold", color=quantum_theme["error"]),
        "balance_label": ft.Text("Saldo: R$ 0.00", size=14, color=quantum_theme["text"]),
        "total_profit_label": ft.Text("Lucro Total: R$ 0.00", size=14, color=quantum_theme["success"]),
        "win_label": ft.Text("Vitórias: 0", size=14, color=quantum_theme["success"]),
        "loss_label": ft.Text("Derrotas: 0", size=14, color=quantum_theme["error"]),
        "asset_dropdown": ft.Dropdown(
            width=300, 
            # Começa com uma opção indicando carregamento
            options=[ft.dropdown.Option(key="loading", text="> Carregando ativos <", disabled=True)], 
            value="loading", # Define o valor inicial para a opção de carregamento
            label="Par de Moedas", 
            **dropdown_style
        ),
        "strategy_dropdown": ft.Dropdown(
            width=300,
            options=[
                # Restaurando emojis no texto e removendo 'leading'
                ft.dropdown.Option("1", text="🔹 QUANTUM EDGE M5"),
                ft.dropdown.Option("2", text="🔸 TWIN TOWERS REVERSAL"),
                ft.dropdown.Option("3", text="⚡ PRECISION ALPHA M5"),
                ft.dropdown.Option("4", text="🎯 MOMENTUM HUNTER"), # Emoji adicionado
                ft.dropdown.Option("5", text="🖐️ FIVE COLORS"),
                ft.dropdown.Option("6", text="📈 MACD CROSSOVER"),
                ft.dropdown.Option("7", text="🔄 RSI REVERSAL (30/70)"),
                ft.dropdown.Option("8", text="🧭 ORIGIN RSI REVERSAL"),
                ft.dropdown.Option("9", text="🔵 PRO SUPREMY")
            ],
            value="1",
            label="Estratégia",
            **dropdown_style
        ),
        "entry_value_texttextfield": ft.TextField(value="5.0", width=300, label="Valor de Entrada", prefix_text="R$", **text_field_style),
        "stop_win_texttextfield": ft.TextField(value="50.0", width=300, label="Stop Win", prefix_text="R$", **text_field_style),
        "stop_loss_texttextfield": ft.TextField(value="50.0", width=300, label="Stop Loss", prefix_text="R$", **text_field_style),
        "use_stop_loss_checkbox": ft.Checkbox(label="Usar Stop Loss", value=True, **checkbox_style),
        "analyze_averages_checkbox": ft.Checkbox(label="Analisar Médias", value=False, **checkbox_style),
        "average_candles_texttextfield": ft.TextField(value="60", width=300, label="Velas para Média", **text_field_style),
        "use_martingale_checkbox": ft.Checkbox(label="Usar Martingale", value=True, **checkbox_style),
        "martingale_levels_texttextfield": ft.TextField(value="2", width=300, label="Níveis de Martingale", **text_field_style),
        "martingale_factor_texttextfield": ft.TextField(value="2.0", width=300, label="Fator Martingale", **text_field_style),
        "use_soros_checkbox": ft.Checkbox(label="Usar Soros", value=True, **checkbox_style),
        "soros_levels_texttextfield": ft.TextField(value="1", width=300, label="Níveis de Soros", **text_field_style),
        "start_time_texttextfield": ft.TextField(value="00:00", width=300, label="Hora Início (HH:MM)", **text_field_style),
        "end_time_texttextfield": ft.TextField(value="23:59", width=300, label="Hora Fim (HH:MM)", **text_field_style),
        "use_schedule_checkbox": ft.Checkbox(label="Usar Agendamento", value=False, **checkbox_style),
        "reentry_win_checkbox": ft.Checkbox(label="Reentrada após Vitória", value=False, **checkbox_style),
        "use_ai_checkbox": ft.Checkbox(label="Usar IA (Não implementado)", value=False, disabled=True, **checkbox_style),
        "reverse_direction_checkbox": ft.Checkbox(label="Inverter Direção Após Loss", value=False, **checkbox_style),
        "use_winning_patterns_checkbox": ft.Checkbox(label="Usar Padrões Vencedores (QUARTA)", value=False, **checkbox_style),
        "analyze_all_pairs_checkbox": ft.Checkbox(label="Analisar Todos os Pares Disponíveis", value=False, **checkbox_style),

        # Modal de Operação (Elementos precisam ser criados dinamicamente ou placeholders)
        "progress_ring": ft.ProgressRing(width=60, height=60, color=quantum_theme["secondary"], bgcolor=ft.Colors.with_opacity(0.1, quantum_theme["surface"])),
        "timer_text": ft.Text("60s", size=16, weight="bold", color=quantum_theme["text"]),
        "result_label": ft.Text("", size=16, weight="bold", color=quantum_theme["text"]),

        # Adicionar controles RSI
        "use_rsi_checkbox": ft.Checkbox(
            label="Usar Filtro RSI",
            value=False,
            **checkbox_style
        ),
        "periodo_rsi_textfield": ft.TextField(
            label="Período RSI",
            value="14",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            **text_field_style
        ),

        # === ADICIONAR CONTROLE DE LOGS AQUI ===
        "log_list_view": ft.ListView(
            expand=True, 
            spacing=5, 
            auto_scroll=True, 
            reverse=False # Logs aparecem do mais antigo para o mais novo
        ),
        # ======================================

        # Adicionar outros elementos conforme necessário (ex: FilePicker)
        "file_picker": ft.FilePicker(on_result=lambda e: print(f"FilePicker result: {e.files}")) # Placeholder
    }
    print("Elementos da UI inicializados e retornados.")
    return ui_elements # Return the dictionary

# --- Funções Auxiliares (Mover para utils.py ou outros módulos) --- #

# Removido: load_configurations - Não usado diretamente, UserSession.load_configurations é chamado

# Removido: on_file_picked (Duplicado - usar versão de Profler3/user_profile.py)

# Removido: file_picker_handler (Redundante com on_file_picked)

# Removido: save_profile_picture (Duplicado - usar versão de Profler3/user_profile.py)

# Função de Splash Screen (Pode ficar aqui ou ir para screens.py)
def show_splash_screen(page: ft.Page):
    """Mostra a tela de splash inicial com visual atualizado e título animado."""
    print("--- Executing show_splash_screen ---") # DEBUG
    page.views.clear() # Limpar views anteriores
    page.bgcolor = ft.colors.BLACK # Definir fundo como preto

    # Referência para o texto do título
    title_text_ref = ft.Ref[ft.Text]()

    # Logo Quantum Pro (agora com Ref)
    title_text = ft.Text(
        ref=title_text_ref, # Atribuir a referência
        spans=[
            ft.TextSpan(
                "QUANTUM",
                ft.TextStyle(size=36, weight="bold", color=quantum_theme["primary"])
            ),
            ft.TextSpan(
                "PRO",
                ft.TextStyle(size=34, weight="bold", color=quantum_theme["secondary"])
            ),
        ],
        text_align=ft.TextAlign.CENTER
    )

    splash_view = ft.View(
        "/splash",
        [
            ft.Container(
                expand=True,
                bgcolor=ft.colors.BLACK, # Garantir que container também seja preto
                content=ft.Column(
                    [
                        ft.Container(height=150), # Espaço superior
                        title_text, # Logo
                        ft.Container(height=40),
                        ft.ProgressRing(width=32, height=32, stroke_width=4, color=quantum_theme["primary"]),
                        ft.Container(height=15),
                        ft.Text("Iniciando Quantum Pro...", size=16, color=quantum_theme["text_secondary"]),
                    ],
                    alignment=ft.MainAxisAlignment.START, # Alinhar ao topo para controlar espaçamento
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                )
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0 # Remover padding da view
    )
 
    page.views.append(splash_view)
    page.update()
 
    # Iniciar animação em thread separada
    state['animating_splash'] = True
    page.run_thread(animate_title_color, page, title_text_ref) # Passar page e ref

    # Simular carregamento e ir para a próxima tela (em outra thread)
    page.run_thread(navigate_after_splash, page)

def animate_title_color(page: ft.Page, text_ref: ft.Ref[ft.Text]):
    """Anima a cor do texto do título em um ciclo RGB suave (roda em thread)."""
    hue = 0
    while state.get('animating_splash', False): # Loop enquanto a flag estiver ativa
        # Calcular cor RGB a partir do HSL (Hue, Saturation, Lightness)
        # Mantemos Saturação e Luminosidade constantes para cores vivas
        rgb_float = colorsys.hls_to_rgb(hue / 360, 0.5, 1.0)
        # Converter para valores 0-255
        rgb_int = tuple(int(c * 255) for c in rgb_float)
        # Formatar como string hexadecimal #RRGGBB
        hex_color = f"#{rgb_int[0]:02x}{rgb_int[1]:02x}{rgb_int[2]:02x}"

        if text_ref.current: # Verificar se o controle existe
            text_ref.current.color = hex_color
            try:
                page.update(text_ref.current) # Atualizar apenas o controle de texto
            except Exception as e_update:
                # Se a página for fechada ou derro durante o update
                print(f"Erro ao atualizar cor do título (splash): {e_update}")
                state['animating_splash'] = False # Parar animação em caso de erro
                break

        # Incrementar o matiz para a próxima cor (velocidade da animação)
        hue = (hue + 2) % 360

        # Pequena pausa para controlar a velocidade
        time.sleep(0.02)
    print("--- Animação do título (splash) finalizada ---")

def navigate_after_splash(page):
    """Função auxiliar para rodar em thread e navegar após o splash."""
    time.sleep(2) # Manter tempo original do splash
    # Parar a animação ANTES de navegar
    state['animating_splash'] = False
    # Chamar diretamente a função que atualiza a view
    show_welcome_screen(page)

# Funções Utilitárias de UI (Exemplo)
def show_loading_overlay(page: ft.Page, message: str = "Carregando..."):
    """Mostra um diálogo de carregamento simples."""
    if page is None: return None
    loading_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(message, text_align=ft.TextAlign.CENTER),
        content=ft.Row(
            [ft.ProgressRing(color=quantum_theme.get("secondary", "#00D2D3")), ft.Text("Aguarde...")],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        actions_alignment=ft.MainAxisAlignment.CENTER,
        content_padding=ft.padding.symmetric(vertical=20, horizontal=20),
        shape=ft.RoundedRectangleBorder(radius=15),
        bgcolor=ft.colors.with_opacity(0.9, quantum_theme.get("background", "#0F1729")),
    )
    page.dialog = loading_dialog
    loading_dialog.open = True
    page.update()
    return loading_dialog # Retorna a instância para poder fechá-la

def hide_loading_overlay(page: ft.Page, dialog: ft.AlertDialog):
    """Fecha um diálogo de carregamento existente."""
    if page is None or dialog is None: return
    dialog.open = False
    page.update()

# Função de Validação de Login (Mover para auth.py)
def validate_login(username, password, access_key):
    """Valida as credenciais do usuário contra o banco de dados."""
    connection = None
    try:
        print(f"Validando login para: {username}")
        connection = mysql.connector.connect(
            host='srv901.hstgr.io',
            user='u676638560_icaro',
            password='jWbtQ:7NR6|u',
            database='u676638560_trader'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, password, access_key, is_blocked FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            cursor.close()

            if not user_data:
                print("Usuário não encontrado.")
                return False, "Usuário não encontrado."

            if user_data.get('is_blocked'):
                print("Conta bloqueada.")
                return False, "Conta bloqueada. Entre em contato com o suporte."

            stored_password_hash = user_data.get('password')
            stored_access_key = user_data.get('access_key')

            # Verificar chave de acesso primeiro
            if stored_access_key and stored_access_key != access_key:
                 print("Chave de acesso incorreta.")
                 return False, "Chave de acesso incorreta."
            elif not stored_access_key and access_key:
                 print("Chave de acesso fornecida, mas não esperada.")
                 # Decidir o comportamento: erro ou ignorar?
                 return False, "Chave de acesso não necessária/configurada para este usuário."
            elif not stored_access_key and not access_key:
                 pass # Ok, chave não é necessária e não foi fornecida
            # Caso onde a chave é necessária mas não foi fornecida é coberto pela validação anterior
            elif stored_access_key and not access_key:
                 print("Chave de acesso obrigatória não fornecida.")
                 return False, "Chave de acesso obrigatória."


            # Verificar senha com bcrypt
            if stored_password_hash and bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                print("Login validado com sucesso.")
                # Atualizar último acesso (opcional, pode ser feito após sucesso completo)
                # try:
                #     cursor = connection.cursor()
                #     cursor.execute("UPDATE users SET last_access = NOW() WHERE id = %s", (user_data['id'],))
                #     connection.commit()
                #     cursor.close()
                # except Error as update_err:
                #     print(f"Erro ao atualizar last_access: {update_err}")
                return True, None
            else:
                print("Senha incorreta.")
                return False, "Senha incorreta."
        else:
             print("Falha ao conectar ao BD para validação.")
             return False, "Erro de sistema ao validar (conexão BD)."

    except Error as e:
        print(f"Erro de MySQL em validate_login: {e}")
        return False, f"Erro de sistema ao validar (MySQL: {e})."
    except Exception as ex:
        print(f"Erro inesperado em validate_login: {ex}")
        return False, f"Erro inesperado no sistema: {ex}"
    finally:
        if connection and connection.is_connected():
            connection.close()

# Função de Callback de Login (Mover para auth.py)
def on_login_click_callback(e, page, email_field, password_field, access_key_field):
    """Callback executado quando o botão de login é clicado."""
    # Precisa das funções: validate_login, get_user_session, show_initial_screen, show_loading_overlay, hide_loading_overlay
    username = email_field.value
    password = password_field.value
    access_key = access_key_field.value

    if not username or not password:
        page.snack_bar = ft.SnackBar(ft.Text("Usuário e Senha são obrigatórios."), bgcolor=quantum_theme["error"])
        page.snack_bar.open = True
        page.update()
        return

    # Mostrar loading
    # loading_overlay = show_loading_overlay(page, "Validando...")

    # Validar login
    is_valid, error_message = validate_login(username, password, access_key)

    # Esconder loading
    # hide_loading_overlay(page, loading_overlay)

    if is_valid:
        user_session = get_user_session(username)
        user_session.password = password # Armazenar senha aqui é arriscado
        user_session.access_key = access_key

        # Navegar para a tela inicial
        # show_initial_screen(page, user_session) # Precisa da função importada
        print(f"Login bem-sucedido para {username}. Navegando para tela inicial...")
        _temp_show_initial(page, user_session) # Placeholder temporário

    else:
        page.snack_bar = ft.SnackBar(ft.Text(error_message or "Falha no login."), bgcolor=quantum_theme["error"])
        page.snack_bar.open = True
        page.update()

# Removido: atualizar_ativos_disponiveis (Mover para api_utils.py)
# Removido: plataforma_dropdown (Definido em initialize_ui_elements)
# Removido: identificar_plataforma (Mover para api_utils.py)

# --- Função Principal --- #

def main(page: ft.Page):
    """Função principal que inicializa a aplicação Flet."""
    page.title = "Quantum Trader v3.0"
    page.window_width = 450 # Ajustar largura
    page.window_height = 850 # Ajustar altura
    page.window_resizable = False
    page.window_maximizable = False
    page.theme_mode = "dark"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inicializar elementos da UI e atribuir a page.ui
    page.ui = initialize_ui_elements()
    print(f"DEBUG [main]: page.ui ID = {id(page.ui)}, balance_label ID = {id(page.ui.get('balance_label'))}, total_profit_label ID = {id(page.ui.get('total_profit_label'))}")

    # Adicionar FilePicker à página (necessário para upload de imagem)
    # Precisa da função file_picker_handler ou on_file_picked definida e passada
    # file_picker = ft.FilePicker(on_result=lambda e: file_picker_handler(e, page, current_user_session)) # Precisa da sessão atual
    # page.overlay.append(file_picker)

    # Iniciar com splash screen
    show_splash_screen(page)

# Placeholders temporários para navegação (substituir por imports reais)
def _temp_show_login(page):
    print("Placeholder: Mostrando tela de login...")
    # Aqui chamaria show_login_screen(page, quantum_theme, on_login_click_callback)
    login_view_placeholder = ft.View("/login", [ft.Text("Tela de Login Placeholder", size=20)])
    page.views.clear()
    page.views.append(login_view_placeholder)
    page.update()

def _temp_show_initial(page, user_session):
     print(f"Placeholder: Mostrando tela inicial para {user_session.email}...")
     # Aqui chamaria show_initial_screen(...)
     initial_view_placeholder = ft.View("/initial", [ft.Text(f"Tela Inicial Placeholder - Olá {user_session.email}", size=20)])
     page.views.clear()
     page.views.append(initial_view_placeholder)
     page.update()

# --- Ponto de Entrada --- #
if __name__ == "__main__":
    # Tentar carregar padrões vencedores uma vez na inicialização?
    # state['winning_patterns'] = load_winning_patterns()

    ft.app(
        target=main,
        assets_dir="static",
        view=ft.AppViewer.FLET_APP # Usar FLET_APP para desktop
        # view=ft.WEB_BROWSER # Para Web
    )

# --- Novas Telas (Welcome, Choice, Register) --- #

def show_welcome_screen(page: ft.Page):
    """Mostra a tela inicial de boas-vindas (inspirada em VaultCash Screen 1)."""
    print("--- Executing show_welcome_screen ---") # DEBUG
    page.views.clear()
    page.bgcolor = ft.colors.BLACK # Fundo preto
    
    # Ícone Original (INSIGHTS)
    main_icon = ft.Container(
        content=ft.Icon(name=ft.icons.INSIGHTS, size=120, color=quantum_theme["primary"]),
        border_radius=70, padding=20,
        border=ft.border.all(3, ft.colors.with_opacity(0.5, quantum_theme["primary"])),
        width=160, height=160, alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=30)
    )
    
    # Título da Aplicação (Unificado com Spans)
    title_text = ft.Text(
        spans=[
            ft.TextSpan(
                "QUANTUM",
                ft.TextStyle(size=42, weight="bold", color=quantum_theme["primary"])
            ),
            ft.TextSpan(
                "PRO",
                ft.TextStyle(size=40, weight="bold", color=quantum_theme["secondary"])
            ),
        ]
    )

    # Slogan
    slogan_text = ft.Text(
        "Professional trading simplified.", 
        size=18, 
        color=quantum_theme["text_secondary"], 
        weight="w500", 
        text_align=ft.TextAlign.CENTER
    )
    
    # Botão Começar
    get_started_button = ft.ElevatedButton(
         style=ft.ButtonStyle(
             shape=ft.RoundedRectangleBorder(radius=15),
             bgcolor=quantum_theme["primary"],
             elevation=2,
         ),
         content=ft.Container(
             content=ft.Text("COMEÇAR", weight="bold", color=quantum_theme["text"], size=16),
             padding=ft.padding.symmetric(vertical=14, horizontal=15),
             width=280,
             height=55,
             alignment=ft.alignment.center,
         ),
         on_click=lambda _: show_choice_screen(page) # Navega para tela de escolha
     )

    welcome_view = ft.View(
        "/welcome",
        controls=[
            ft.Container(
                 content=ft.Column([
                    ft.Container(height=80), # Espaço no topo
                    main_icon,
                    title_text, # Usar o Text único
                    ft.Container(height=10),
                    slogan_text,
                    ft.Container(height=60), # Espaço antes do botão
                    get_started_button,
                 ],
                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                 alignment=ft.MainAxisAlignment.START, # Alinha ao topo após espaçamento
                 expand=True
            ),
            padding=20,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.colors.BLACK # Garantir container preto
        )],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )

    page.views.append(welcome_view)
    page.update()

def animate_choice_title(page: ft.Page, text_ref: ft.Ref[ft.Text]):
    """Anima suavemente a cor das spans do título entre cores do tema."""
    print("--- Iniciando animação suave do título (choice) --- ")
    theme_colors_hex = [quantum_theme["primary"], quantum_theme["secondary"], "#7A77FF"]
    theme_colors_rgb = [hex_to_rgb(c) for c in theme_colors_hex]
    color_index = 0
    factor = 0.0
    steps = 50 # Mais passos

    while state.get('animating_choice_title', False):
        # ... (cálculo de cor interpolada)
        start_color = theme_colors_rgb[color_index]
        end_color = theme_colors_rgb[(color_index + 1) % len(theme_colors_rgb)]
        interpolated_rgb = interpolate_color(start_color, end_color, factor)
        hex_color = rgb_to_hex(interpolated_rgb)

        if text_ref.current and text_ref.current.spans:
            try:
                if len(text_ref.current.spans) >= 2:
                    text_ref.current.spans[0].style.color = hex_color
                    text_ref.current.spans[1].style.color = hex_color
                    page.update(text_ref.current)
            except Exception as e_update:
                # ... (tratamento de erro)
                print(f"Erro ao atualizar cor do título (choice): {e_update}")
                state['animating_choice_title'] = False
                break
        else:
            # ... (tratamento de erro)
            print("AVISO: Controle de título ou spans não encontrados (choice). Parando animação.")
            state['animating_choice_title'] = False # Parar se controle sumir
            break
            
        factor += 1.0 / steps
        if factor >= 1.0:
            factor = 0.0
            color_index = (color_index + 1) % len(theme_colors_rgb)
            time.sleep(0.2) 

        time.sleep(0.02) # Pausa menor entre passos
        
    print("--- Animação suave do título (choice) finalizada --- ")

def animate_container_bgcolor(page: ft.Page, container_ref: ft.Ref[ft.Container], state_flag_name: str):
    """Anima suavemente o bgcolor de um Container entre cores do tema."""
    print(f"--- Iniciando animação suave bgcolor para {state_flag_name} --- ")
    theme_colors_hex = [quantum_theme["primary"], quantum_theme["secondary"], "#7A77FF"]
    theme_colors_rgb = [hex_to_rgb(c) for c in theme_colors_hex]
    color_index = 0
    factor = 0.0
    steps = 50 # Mais passos

    while state.get(state_flag_name, False):
        # ... (cálculo de cor interpolada)
        start_color = theme_colors_rgb[color_index]
        end_color = theme_colors_rgb[(color_index + 1) % len(theme_colors_rgb)]
        interpolated_rgb = interpolate_color(start_color, end_color, factor)
        hex_color = rgb_to_hex(interpolated_rgb)

        if container_ref.current:
            try:
                container_ref.current.bgcolor = hex_color
                page.update(container_ref.current)
            except Exception as e_update:
                # ... (tratamento de erro)
                print(f"Erro ao atualizar bgcolor ({state_flag_name}): {e_update}")
                state[state_flag_name] = False
                break
        else:
             # ... (tratamento de erro)
             print(f"AVISO: Container não encontrado para animar bgcolor ({state_flag_name})")
             state[state_flag_name] = False
             break 

        factor += 1.0 / steps
        if factor >= 1.0:
            factor = 0.0
            color_index = (color_index + 1) % len(theme_colors_rgb)
            time.sleep(0.2)
            
        time.sleep(0.02) # Pausa menor entre passos
    print(f"--- Animação suave bgcolor para {state_flag_name} finalizada --- ")

def animate_text_color(page: ft.Page, text_ref: ft.Ref[ft.Text], state_flag_name: str):
    """Anima suavemente a cor de um Text entre cores do tema."""
    print(f"--- Iniciando animação suave text color para {state_flag_name} --- ")
    # === USAR CORES MAIS CLARAS AQUI ===
    theme_colors_hex = ["#87CEFA", "#AFEEEE", "#E6E6FA"] # LightSkyBlue, PaleTurquoise, Lavender
    # ===================================
    theme_colors_rgb = [hex_to_rgb(c) for c in theme_colors_hex]
    color_index = 0
    factor = 0.0
    steps = 50 # Mais passos

    while state.get(state_flag_name, False):
        # ... (cálculo de cor interpolada)
        start_color = theme_colors_rgb[color_index]
        end_color = theme_colors_rgb[(color_index + 1) % len(theme_colors_rgb)]
        interpolated_rgb = interpolate_color(start_color, end_color, factor)
        hex_color = rgb_to_hex(interpolated_rgb)

        if text_ref.current:
            try:
                text_ref.current.color = hex_color
                page.update(text_ref.current)
            except Exception as e_update:
                # ... (tratamento de erro)
                print(f"Erro ao atualizar text color ({state_flag_name}): {e_update}")
                state[state_flag_name] = False
                break
        else:
            # ... (tratamento de erro)
            print(f"AVISO: Text não encontrado para animar cor ({state_flag_name})")
            state[state_flag_name] = False
            break

        factor += 1.0 / steps
        if factor >= 1.0:
            factor = 0.0
            color_index = (color_index + 1) % len(theme_colors_rgb)
            time.sleep(0.2)
            
        time.sleep(0.02) # Pausa menor entre passos
    print(f"--- Animação suave text color para {state_flag_name} finalizada --- ")

def animate_appbar_title(page: ft.Page, text1_ref: ft.Ref[ft.Text], text2_ref: ft.Ref[ft.Text], state_flag_name: str):
    """Anima suavemente a cor dos dois textos do título da AppBar entre cores do tema."""
    print(f"--- Iniciando animação suave AppBar title para {state_flag_name} --- ")
    theme_colors_hex = [quantum_theme["primary"], quantum_theme["secondary"], "#7A77FF"]
    theme_colors_rgb = [hex_to_rgb(c) for c in theme_colors_hex]
    color_index = 0
    factor = 0.0
    steps = 50 # Usar os mesmos 50 passos

    while state.get(state_flag_name, False):
        start_color = theme_colors_rgb[color_index]
        end_color = theme_colors_rgb[(color_index + 1) % len(theme_colors_rgb)]
        
        interpolated_rgb = interpolate_color(start_color, end_color, factor)
        hex_color = rgb_to_hex(interpolated_rgb)

        if text1_ref.current and text2_ref.current: # Verificar ambos os refs
            try:
                text1_ref.current.color = hex_color
                text2_ref.current.color = hex_color # Aplicar mesma cor a ambos por simplicidade
                page.update(text1_ref.current, text2_ref.current) # Atualizar ambos
            except Exception as e_update:
                print(f"Erro ao atualizar cor AppBar title ({state_flag_name}): {e_update}")
                state[state_flag_name] = False
                break
        else:
             print(f"AVISO: Text refs não encontrados para animar AppBar title ({state_flag_name})")
             state[state_flag_name] = False
             break 

        factor += 1.0 / steps
        if factor >= 1.0:
            factor = 0.0
            color_index = (color_index + 1) % len(theme_colors_rgb)
            time.sleep(0.2)
            
        time.sleep(0.02) # Usar a mesma pausa dos outros
    print(f"--- Animação suave AppBar title para {state_flag_name} finalizada --- ")

def show_choice_screen(page: ft.Page):
    """Mostra a tela para escolher entre Login e Cadastro."""
    print("--- Executing show_choice_screen ---") # DEBUG
    page.views.clear()
    page.bgcolor = ft.colors.BLACK # Garantir fundo preto
    
    # Referências
    choice_title_ref = ft.Ref[ft.Text]()
    login_button_ref = ft.Ref[ft.Container]() # Ref para o Container do botão Login
    register_text_ref = ft.Ref[ft.Text]() # Ref para o Texto do botão Registrar
    
    # --- Reutilizar Elementos de Branding da Welcome Screen --- #
    main_icon = ft.Container(
        content=ft.Icon(name=ft.icons.INSIGHTS, size=80, color=quantum_theme["primary"]),
        border_radius=50, padding=15,
        border=ft.border.all(2, ft.colors.with_opacity(0.5, quantum_theme["primary"])),
        width=120, height=120, alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=20)
    )
    title_text = ft.Text(
        ref=choice_title_ref, # Atribuir a referência
        spans=[
            ft.TextSpan(
                "QUANTUM",
                ft.TextStyle(size=36, weight="bold", color=quantum_theme["primary"]) # Cor inicial
            ),
            ft.TextSpan(
                "PRO",
                ft.TextStyle(size=34, weight="bold", color=quantum_theme["secondary"]) # Cor inicial
            ),
        ]
    )
    # --- Fim Elementos de Branding --- #

    # Importar show_login_screen...
    try:
        # Tentar importar de Profler4 primeiro (onde parece estar definida)
        try:
            from Proflet4 import show_login_screen
        except ImportError:
            # Fallback para Profler3 se não encontrar em Proflet4
            from Profler3 import show_login_screen
            
    except ImportError:
        print("Erro: Não foi possível importar show_login_screen de Proflet4 ou Profler3")
        # Fallback ou tratamento de erro
        show_login_screen = lambda p: print("Função show_login_screen não encontrada!")
          
    # --- Botão LOGIN (Usando Container com borda arredondada e Ref) ---
    login_button = ft.Container(
        ref=login_button_ref, # Adicionar Ref
        content=ft.Text("LOGIN", weight="bold", color=quantum_theme["text"], size=16),
        width=280, # Largura original
        height=55, # Altura original
        alignment=ft.alignment.center,
        bgcolor=quantum_theme["primary"], # Cor de fundo inicial
        border_radius=15, # Garantir borda arredondada
        ink=True, # Efeito de clique (ripple)
        on_click=lambda _: show_login_screen(page) # Ação de clique original
    )

    # --- Botão CRIAR CONTA (OutlinedButton com Ref no Texto interno) ---
    register_button = ft.OutlinedButton(
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            side=ft.BorderSide(2, quantum_theme["primary"]), # Borda com cor primária
        ),
        content=ft.Container( # Container para alinhar e definir tamanho
            content=ft.Text(
                ref=register_text_ref, # Adicionar Ref ao Texto
                value="CRIAR CONTA", 
                weight="bold", 
                color=quantum_theme["primary"], # Cor inicial do texto
                size=16
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=15),
            width=280,
            height=55,
            alignment=ft.alignment.center,
        ),
        on_click=lambda _: show_register_screen(page)
    )
     
    choice_view = ft.View(
        "/choice",
        controls=[
            ft.Column([
                ft.Container(height=60), # Espaço superior
                main_icon, # Adicionado Ícone
                title_text, # Adicionado Título
                ft.Container(height=50),
                login_button,
                ft.Container(height=20),
                register_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=10
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
        bgcolor=ft.colors.BLACK # Garantir fundo preto para a view
    )
    page.views.append(choice_view)
    page.update()
    
    # Iniciar animações
    state['animating_choice_title'] = True
    page.run_thread(animate_choice_title, page, choice_title_ref)
    state['animating_login_button'] = True
    page.run_thread(animate_container_bgcolor, page, login_button_ref, 'animating_login_button')
    state['animating_register_button'] = True
    page.run_thread(animate_text_color, page, register_text_ref, 'animating_register_button')

def show_register_screen(page: ft.Page):
    """Mostra a tela de cadastro (inspirada em VaultCash Screen 2)."""
    print("--- Executing show_register_screen ---") # DEBUG
    page.views.clear()
    page.bgcolor = ft.colors.BLACK # Fundo preto

    # Acessar campos de UI (idealmente, teríamos campos específicos para registro)
    # Vamos reutilizar os de login por enquanto, mas o ideal seria criar novos
    # e talvez adicionar um campo 'Nome Completo'
    email_field = page.ui.get('email_textfield_login')
    password_field = page.ui.get('password_textfield_login')
    # Adicionar um campo para nome, se necessário:
    # name_field = ft.TextField(hint_text="Nome Completo", **login_textfield_style)
    # page.ui['name_textfield_register'] = name_field # Adicionar ao dict de UI
    
    # Recriar TextFields com estilo correto se a instância não for a desejada
    # (Isso é um workaround pela reutilização - idealmente seriam instâncias separadas)
    login_textfield_style = {
        "border": ft.InputBorder.UNDERLINE,
        "border_radius": 5,
        "border_color": ft.colors.with_opacity(0.5, quantum_theme["text_secondary"]),
        "focused_border_color": quantum_theme["primary"],
        "text_style": ft.TextStyle(color=quantum_theme["text"]),
        "cursor_color": quantum_theme["secondary"],
        "content_padding": ft.padding.symmetric(vertical=10, horizontal=5)
    }
    email_field = ft.TextField(hint_text="Digite seu email", keyboard_type=ft.KeyboardType.EMAIL, **login_textfield_style)
    password_field = ft.TextField(hint_text="Crie uma senha", password=True, can_reveal_password=True, **login_textfield_style)
    name_field = ft.TextField(hint_text="Nome Completo", **login_textfield_style) # Campo de nome

    register_button = ft.ElevatedButton(
         style=ft.ButtonStyle(
             shape=ft.RoundedRectangleBorder(radius=15),
             bgcolor=quantum_theme["primary"],
             elevation=2,
         ),
         content=ft.Container(
             content=ft.Text("REGISTRAR", weight="bold", color=quantum_theme["text"], size=16),
             padding=ft.padding.symmetric(vertical=14, horizontal=15),
             width=280, # Largura do botão
             height=55,
             alignment=ft.alignment.center,
         ),
         # Ação: Abrir URL externa
         on_click=lambda _: page.launch_url("https://www.tradersdofractal.cloud")
     )
     
    register_view = ft.View(
        "/register",
        appbar=ft.AppBar( # Adicionar AppBar com botão voltar
            leading=ft.IconButton(
                icon=ft.icons.ARROW_BACK_IOS_NEW,
                icon_color=quantum_theme["text_secondary"],
                tooltip="Voltar",
                on_click=lambda _: show_choice_screen(page)
            ),
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0
        ),
        controls=[
            ft.Column([
                ft.Text("Crie sua Conta", size=32, weight="bold", color=quantum_theme["text"]),
                ft.Container(height=30),
                ft.Text(" Nome Completo", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                name_field,
                ft.Container(height=15),
                ft.Text(" Email", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                email_field,
                ft.Container(height=15),
                ft.Text(" Senha", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                password_field,
                ft.Container(height=40),
                register_button,
                ft.Container(height=20),
                ft.Row([
                    ft.Text("Já tem uma conta?", color=quantum_theme["text_secondary"]),
                    ft.TextButton("Faça Login", on_click=lambda _: show_choice_screen(page)) # Volta para escolha ou direto login?
                ], alignment=ft.MainAxisAlignment.CENTER)

            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            alignment=ft.MainAxisAlignment.START,
            spacing=5
            )
        ],
        padding=ft.padding.symmetric(horizontal=30, vertical=10) # Padding da página
    )
    page.views.append(register_view)
    page.update()


# Removido código solto no final
# asset_dropdown.visible = True
# print(f"Dropdown atualizado com {len(asset_dropdown.options)} opções")
# print(f"Primeira opção: {asset_dropdown.options[0].text if asset_dropdown.options else 'Nenhuma opção'}")
# ft.app(target=main, assets_dir="static", view=ft.WEB_BROWSER)

# Dicionário de descrições
estrategias_descricao = {
    1: {
        "nome": "QUANTUM EDGE M5",
        "descricao": "Estratégia avançada para timeframe de 5 minutos que utiliza análise multidimensional de padrões de preço e volume. Incorpora algoritmos de reconhecimento de padrões e análise estatística para identificar pontos de entrada de alta probabilidade.",
        "risco": "Médio" # ADICIONADO
    },
    2: {
        "nome": "TWIN TOWERS REVERSAL",
        "descricao": "Estratégia especializada na identificação de padrões de velas gêmeas e reversões de tendência. Utiliza análise de força das velas e confirmação de padrões para entradas precisas em momentos de reversão de mercado.",
        "risco": "Alto" # ADICIONADO
    },
    3: {
        "nome": "PRECISION ALPHA M5",
        "descricao": "Estratégia de precisão para timeframe de 5 minutos com foco em alpha positivo. Combina análise técnica avançada com filtros de tendência e volatilidade para maximizar a relação risco-retorno.",
        "risco": "Médio" # ADICIONADO
    },
    4: {
        "nome": "MOMENTUM HUNTER",
        "descricao": "Sistema adaptativo multi-timeframe que captura movimentos de momentum no mercado. Utiliza machine learning para otimizar entradas e saídas em diferentes ambientes de mercado, com foco em movimentos rápidos e decisivos.",
        "risco": "Alto" # ADICIONADO
    },
    5: { 
        "nome": "FIVE COLORS",
        "descricao": "Estratégia baseada na análise das cores das últimas cinco velas consecutivas. Busca identificar sequências uniformes de alta ou baixa para prever a continuidade.",
        "risco": "Baixo" # ADICIONADO
    },
    6: { 
        "nome": "MACD CROSSOVER",
        "descricao": "Estratégia clássica que utiliza o cruzamento da linha MACD sobre a linha de sinal para indicar possíveis mudanças de tendência e pontos de entrada."
    },
    7: { # Adicionada descrição para ID 7
        "nome": "RSI REVERSAL (30/70)",
        "descricao": "Busca por oportunidades de reversão entrando contra a tendência quando o RSI indica condições de sobrecompra (acima de 70) ou sobrevenda (abaixo de 30)."
    },
    8: { # Adicionada descrição para ID 8
        "nome": "ORIGIN RSI REVERSAL",
        "descricao": "Inspirada na Pro Origin Analyzer. Entra na reversão do RSI (abaixo de 30 ou acima de 70) com filtros de confirmação de preço, tendência macro (SMA 100) e volatilidade (ATR)."
    },
    9: { 
        "nome": "PRO SUPREMY", # Renomeado
        "descricao": "Busca por padrões de Engolfo ou Sequência de Candles e confirma a entrada com a tendência de curto prazo (EMA 11). Corresponde às bandeiras/setas amarelas do script Pro Origin Analyzer."
    }
}

# Função para criar modais com estilo Quantum (Movida de proflet.py)
def create_modal(title, content, icon=None, page=None):
    """Função helper para criar modais responsivos"""
    is_mobile = page.width < 600 if page else False
    modal_width = page.width - 40 if is_mobile else 700 if page else 700
    modal_height = page.height - 100 if is_mobile else 500 if page else 500

    # Botão de fechar
    close_button = ft.IconButton(
        icon=ft.icons.CLOSE,
        icon_color=quantum_theme["text_secondary"],
        on_click=lambda e: close_modal(page),
        tooltip="Fechar",
    )

    return ft.AlertDialog(
        modal=True,
        content=ft.Container(
            content=ft.Column([
                # Cabeçalho com botão de fechar
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            name=icon or ft.Icons.DASHBOARD_ROUNDED,
                            size=28 if is_mobile else 32,
                            color=quantum_theme["secondary"]
                        ),
                        ft.Text(
                            title,
                            size=20 if is_mobile else 24,
                            weight="bold",
                            color=quantum_theme["text"]
                        ),
                        ft.Container(expand=True),  # Espaçador flexível
                        close_button,  # Botão de fechar
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[
                            ft.Colors.with_opacity(0.2, quantum_theme["primary"]),
                            ft.Colors.with_opacity(0.1, quantum_theme["secondary"])
                        ]
                    ),
                    padding=15 if is_mobile else 20,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15)
                ),
                
                # Conteúdo com scroll
                ft.Column(
                    controls=[
                        ft.Container(
                            content=content,
                            width=modal_width,
                            height=modal_height,
                            padding=15 if is_mobile else 20,
                            bgcolor=ft.Colors.with_opacity(0.05, quantum_theme["surface"])
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                
                # Botões
                ft.Container(
                    content=ft.Row([
                        ft.OutlinedButton(
                            text="FECHAR",
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: close_modal(page),
                            style=ft.ButtonStyle(
                                color=quantum_theme["text_secondary"]
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.END),
                    padding=10
                )
            ]),
            bgcolor=ft.Colors.with_opacity(0.95, quantum_theme["background"]),
            border_radius=15,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, quantum_theme["secondary"])),
        ),
        # Adicionar estas propriedades para remover a borda do AlertDialog
        bgcolor=ft.Colors.TRANSPARENT,
        shape=ft.RoundedRectangleBorder(radius=15),
        inset_padding=0,
        actions_padding=0,
        content_padding=0
    )

# Função para fechar o modal (Movida de proflet.py)
def close_modal(page):
    if page and page.dialog:
        page.dialog.open = False
        page.update()

# --- FUNÇÕES MOVIDAS DE Profler2.py ---

def _create_log_control(log_data: dict):
    """Cria um controle Flet visualmente agradável para uma entrada de log."""
    level_styles = {
        "info": {"icon": ft.icons.INFO_OUTLINE, "color": quantum_theme["text_secondary"]},
        "win": {"icon": ft.icons.CHECK_CIRCLE_OUTLINE, "color": quantum_theme["success"]},
        "loss": {"icon": ft.icons.ERROR_OUTLINE, "color": quantum_theme["error"]},
        "error": {"icon": ft.icons.ERROR, "color": quantum_theme["error"]},
        "warn": {"icon": ft.icons.WARNING_AMBER_ROUNDED, "color": "#FFA726"}, # Laranja para warning
        "draw": {"icon": ft.icons.REMOVE_CIRCLE_OUTLINE, "color": quantum_theme["text_secondary"]},
        # Adicione outros níveis se necessário
    }

    level = log_data.get('level', 'info').lower()
    style = level_styles.get(level, level_styles["info"])
    timestamp = log_data.get('timestamp', '')
    message = log_data.get('message', '')

    return ft.Row(
        controls=[
            ft.Icon(name=style["icon"], color=style["color"], size=16),
            ft.Text(f"[{timestamp}]", size=11, color=quantum_theme["text_secondary"], weight="normal"),
            ft.Text(message, size=12, color=style["color"], weight="normal", expand=True, no_wrap=False), # Permitir quebra de linha
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

def log_console(page, message, level="info"):
    """Adiciona uma mensagem ao log no estado global e dispara atualização da UI via PubSub."""
    if not isinstance(state.get('log_entries'), list):
        state['log_entries'] = []

    timestamp = datetime.now().strftime("%H:%M:%S")
    emoji_map = {
        "info": "ℹ️", "win": "✅", "loss": "❌", "warn": "⚠️", "error": "🆘", "debug": "🐞", "draw": "➖"
    }
    emoji = emoji_map.get(level, "")

    log_entry = {"timestamp": timestamp, "message": message, "level": level, "emoji": emoji}
    state['log_entries'].append(log_entry)

    # Limitar o tamanho da lista de logs no estado (opcional, mas bom para memória)
    max_log_state = 500
    if len(state['log_entries']) > max_log_state:
        state['log_entries'] = state['log_entries'][-max_log_state:] # Manter os últimos 500

    if page and hasattr(page, 'pubsub'):
        try:
             # === MODIFICADO: Enviar o dicionário log_entry ===
             page.pubsub.send_all(log_entry)
             # ===============================================
             print(f"DEBUG: Mensagem de log enviada para PubSub: {log_entry}") # DEBUG
        except Exception as e_pubsub:
             print(f"Erro ao enviar PubSub 'log_entry': {e_pubsub}")

def enable_buttons(page):
    """Reabilita botões na página (adaptado para funcionar com page.ui ou page.controls)."""
    buttons_to_update = []
    # Tentar com page.ui primeiro (estrutura preferida)
    if page and hasattr(page, 'ui') and isinstance(page.ui, dict):
        fab = page.ui.get('start_button') # Assumindo que o FAB tem essa chave
        settings_button = page.ui.get('settings_button') # Assumindo chave para botão de config
        catalog_button = page.ui.get('catalog_button') # Assumindo chave para botão de catalog
        connect_button = page.ui.get('connect_button') # Assumindo chave para botão conectar

        if fab and hasattr(fab, 'disabled'):
            fab.disabled = False
            buttons_to_update.append(fab)
        if settings_button and hasattr(settings_button, 'disabled'):
            settings_button.disabled = False
            buttons_to_update.append(settings_button)
        if catalog_button and hasattr(catalog_button, 'disabled'):
            catalog_button.disabled = False
            buttons_to_update.append(catalog_button)
        if connect_button and hasattr(connect_button, 'disabled'):
            connect_button.disabled = False
            buttons_to_update.append(connect_button)

    # Fallback: Iterar por page.controls se page.ui não for usado ou falhar
    elif page and hasattr(page, 'controls'):
        print("Aviso: Usando fallback page.controls para enable_buttons.")
        for control in page.controls:
             # Identificar botões relevantes por tipo ou outra propriedade
             if isinstance(control, (ft.FloatingActionButton, ft.IconButton, ft.ElevatedButton)):
                 if hasattr(control, 'disabled'):
                      control.disabled = False
                      buttons_to_update.append(control)

    if buttons_to_update and page:
        try:
            page.update(*buttons_to_update) # Atualizar apenas os botões modificados
        except Exception as e_update:
             print(f"Erro ao atualizar botões em enable_buttons: {e_update}")
    elif not buttons_to_update:
        print("enable_buttons: Nenhum botão encontrado/identificado para habilitar.")

def disable_buttons(page):
    """Desabilita botões na página (adaptado para funcionar com page.ui ou page.controls)."""
    buttons_to_update = []
    if page and hasattr(page, 'ui') and isinstance(page.ui, dict):
        fab = page.ui.get('start_button')
        settings_button = page.ui.get('settings_button')
        catalog_button = page.ui.get('catalog_button')
        connect_button = page.ui.get('connect_button') # Desabilitar conectar também?

        if fab and hasattr(fab, 'disabled'):
            fab.disabled = True
            buttons_to_update.append(fab)
        if settings_button and hasattr(settings_button, 'disabled'):
            settings_button.disabled = True
            buttons_to_update.append(settings_button)
        if catalog_button and hasattr(catalog_button, 'disabled'):
            catalog_button.disabled = True
            buttons_to_update.append(catalog_button)
        if connect_button and hasattr(connect_button, 'disabled'):
            connect_button.disabled = True # Desabilitar conectar durante operação
            buttons_to_update.append(connect_button)

    elif page and hasattr(page, 'controls'):
        print("Aviso: Usando fallback page.controls para disable_buttons.")
        for control in page.controls:
             if isinstance(control, (ft.FloatingActionButton, ft.IconButton, ft.ElevatedButton)):
                 if hasattr(control, 'disabled'):
                      control.disabled = True
                      buttons_to_update.append(control)

    if buttons_to_update and page:
        try:
            page.update(*buttons_to_update)
        except Exception as e_update:
            print(f"Erro ao atualizar botões em disable_buttons: {e_update}")
    elif not buttons_to_update:
        print("disable_buttons: Nenhum botão encontrado/identificado para desabilitar.")

def stop_bot(page):
    """Para o robô definindo a flag no estado e reabilita os botões."""
    print("Chamando stop_bot...") # Debug
    state['stop'] = True # <<< CORRIGIDO: Define True para PARAR >>>
    print(f"state['stop'] definido como {state['stop']}") # Debug

    # --- REATIVAR E RESTAURAR FAB ---
    fab = None
    try:
        # Acessar o FAB da view atual (que deve ser /initial_screen)
        if page.views and page.views[-1].route == "/initial_screen":
            fab = page.views[-1].floating_action_button
        
        if fab and hasattr(fab, 'content') and isinstance(fab.content, ft.Container):
            fab.disabled = False
            # Restaurar gradiente original com as NOVAS cores do tema
            fab.content.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    quantum_theme["primary"], # Usar nova cor primária
                    ft.Colors.with_opacity(0.8, quantum_theme["secondary"]) # Usar secundária
                ],
                rotation=45,
            )
            fab.update()
            fab.content.update() # Atualizar o container interno também
            print("[stop_bot] FAB reativado e aparência restaurada.") # DEBUG
        elif fab:
            # Se não for container, apenas reativar
            fab.disabled = False
            fab.update()
            print("[stop_bot] FAB reativado (sem mudança de aparência).") # DEBUG
        else:
             print("[stop_bot] AVISO: FAB não encontrado na view atual para reativar.") # DEBUG
    except Exception as e_fab_enable:
        print(f"ERRO ao tentar reativar/restaurar FAB: {e_fab_enable}")
    # --- FIM REATIVAR E RESTAURAR FAB ---

    # Tenta fechar o modal se ele existir no overlay
    # Esta lógica é melhor no callback do botão 'Parar' do modal
    # if page and hasattr(page, 'overlay') and len(page.overlay) > 0:
    #     print("Tentando limpar overlay em stop_bot...")
    #     page.overlay.clear()
    #     page.update() # Atualiza após limpar overlay

    enable_buttons(page)  # Reativar os botões após parar
    print("stop_bot finalizado (botões habilitados).")