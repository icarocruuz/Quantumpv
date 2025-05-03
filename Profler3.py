import flet as ft
import time
import threading
from datetime import datetime
import base64
import os
import time
from Proflet5 import quantum_theme, UserSession # Adiciona UserSession

# Imports de outros módulos (Exemplos)
# from Profler1 import load_image_base64
# from Profler2 import show_catalog_modal
# from Proflet4 import start_strategy, show_main_screen, show_initial_screen # Funções de tela/estratégia
# from Proflet5 import sessions, API, validate_online_login, ui_elements # Globais, config, auth, UI

def on_file_picked(e, page, user_session, save_profile_picture_func, update_profile_avatar_func, show_main_screen_func):
    """Callback para quando um arquivo de imagem de perfil é selecionado."""
    if e.files:
        file = e.files[0]
        if file.path:
            try:
                with open(file.path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode()
                save_profile_picture_func(image_data, user_session) # Salva no BD
                update_profile_avatar_func(page, image_data)      # Atualiza UI
                # Opcional: voltar para tela principal ou só atualizar avatar?
                # show_main_screen_func(page, user_session)
                page.update() # Apenas atualiza a página atual
                # Mostrar confirmação
                page.snack_bar = ft.SnackBar(ft.Text("Foto de perfil atualizada!"), bgcolor=quantum_theme["success"])
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                print(f"Erro ao processar imagem: {ex}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao atualizar foto: {ex}"), bgcolor=quantum_theme["error"])
                page.snack_bar.open = True
                page.update()

def upload_profile_picture(e, file_picker):
    """Inicia a seleção de arquivo para a foto de perfil."""
    # file_picker deve ser uma instância de ft.FilePicker adicionada à página
    if file_picker:
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])
    else:
        print("Erro: FilePicker não encontrado.")

def load_profile_picture(user_session):
    """Carrega a imagem de perfil da sessão do usuário (que já foi carregada do BD)."""
    # A imagem já deve estar em user_session.profile_pic após load_configurations
    # Esta função pode não ser mais necessária se a sessão já carrega a pic.
    # Manter por enquanto, mas pode ser refatorada.
    return user_session.profile_pic if user_session else ""

# Removido: get_user_session (Definido em Proflet5/session.py)
# Removido: show_initial_screen (Definido em Proflet4/screens.py)

def on_login_success(page, user_session, show_initial_screen_func):
    """Chamado após o login ser validado com sucesso."""
    # Carregar as configurações do usuário (isso já deve ter acontecido na validação/criação da sessão)
    # user_session.load_configurations() # Verificar se é redundante
    # Mostrar a tela inicial do usuário
    show_initial_screen_func(page, user_session)

# Removido: on_login_click (Movido/Refatorado para Proflet5/auth.py onde validação ocorre)
# Removido: verify_login (Redundante com on_login_click/validate_online_login)

def show_login_screen(page, quantum_theme, on_login_callback): # Passar tema e callback
    """Mostra a tela de login."""
    # Precisa importar ou receber ui_elements (email_textfield, password_textfield, access_key_texttextfield)
    global email_textfield, password_textfield, access_key_texttextfield # Globais são problemáticos

    page.bgcolor = quantum_theme["background"]
    page.theme_mode = "dark"
    page.views.clear() # Limpar views anteriores

    # --- Definição dos campos e botão --- #
    # Idealmente, esses campos seriam definidos em ui_elements.py e importados
    email_textfield = ft.TextField(
        label="Usuário",
        width=300,
        prefix_icon=ft.icons.PERSON_ROUNDED,
        border=ft.InputBorder.UNDERLINE,
        cursor_color=quantum_theme["secondary"],
        focused_border_color=quantum_theme["secondary"],
        focused_color=quantum_theme["secondary"],
        bgcolor=ft.Colors.TRANSPARENT,
        color=quantum_theme["text"],
        text_size=16,
    )

    password_textfield = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        width=300,
        prefix_icon=ft.icons.LOCK_ROUNDED,
        border=ft.InputBorder.UNDERLINE,
        cursor_color=quantum_theme["secondary"],
        focused_border_color=quantum_theme["secondary"],
        focused_color=quantum_theme["secondary"],
        bgcolor=ft.Colors.TRANSPARENT,
        color=quantum_theme["text"],
        text_size=16,
    )

    access_key_texttextfield = ft.TextField(
        label="Chave de Acesso",
        width=300,
        prefix_icon=ft.icons.KEY_ROUNDED,
        border=ft.InputBorder.UNDERLINE,
        cursor_color=quantum_theme["secondary"],
        focused_border_color=quantum_theme["secondary"],
        focused_color=quantum_theme["secondary"],
        bgcolor=ft.Colors.TRANSPARENT,
        color=quantum_theme["text"],
        text_size=16,
    )

    # --- Botão Entrar (Usando Container com largura 300) ---
    login_button = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.LOGIN_ROUNDED, color=quantum_theme["text"], size=20),
            ft.Text(
                "ENTRAR",
                size=16,
                weight="bold",
                color=quantum_theme["text"]
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        width=300, # Definir largura explicitamente
        height=50, # Altura original
        alignment=ft.alignment.center,
        # Gradiente roxo/azul
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[
                "#7A77FF", # Roxo/Azul claro
                quantum_theme["primary"] # Azul vibrante atual
            ],
            rotation=45,
        ),
        border_radius=15,
        ink=True, # Efeito de clique
        on_click=lambda e: on_login_callback(e, page, email_textfield, password_textfield, access_key_texttextfield)
    )

    # --- Layout da tela --- #
    background = ft.Container(
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.alignment.center,
            radius=1.5,
            colors=[
                ft.Colors.with_opacity(0.2, quantum_theme["secondary"]),
                quantum_theme["background"],
                ft.Colors.with_opacity(0.1, quantum_theme["primary"]),
            ],
            stops=[0.0, 0.5, 1.0],
        ),
    )

    login_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                name=ft.icons.LOCK_ROUNDED,
                                size=30,
                                color=quantum_theme["secondary"]
                            ),
                            ft.Text(
                                "LOGIN",
                                size=24,
                                weight="bold",
                                color=quantum_theme["secondary"]
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    # Campos de entrada centralizados
                    ft.Container(
                        content=ft.Column([
                                email_textfield,
                            ft.Container(height=15),
                                password_textfield,
                            ft.Container(height=15),
                                access_key_texttextfield,
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        width=300,
                    ),
                    
                    ft.Container(height=30),
                    
                    # Botão de login diretamente na coluna (centralizado pela coluna pai)
                    login_button,
                    
                    ft.Container(height=20),
                    
                    # Links de ajuda
                    ft.Row([
                        ft.TextButton(
                            "Esqueceu a senha?",
                            icon=ft.icons.HELP_OUTLINE,
                            style=ft.ButtonStyle(
                                color=quantum_theme["text_secondary"],
                            ),
                        ),
                        ft.TextButton(
                            "Suporte",
                            icon=ft.icons.SUPPORT_AGENT,
                            style=ft.ButtonStyle(
                                color=quantum_theme["text_secondary"],
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(30),
        ),
        elevation=0,
    )

    # Indicadores de segurança
    security_indicators = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.SHIELD_ROUNDED, color=quantum_theme["success"], size=16),
            ft.Text(
                "Conexão Segura",
                size=12,
                color=quantum_theme["text_secondary"],
            ),
            ft.Container(width=10),
            ft.Icon(ft.icons.VERIFIED_USER_ROUNDED, color=quantum_theme["success"], size=16),
            ft.Text(
                "Criptografia Avançada",
                size=12,
                color=quantum_theme["text_secondary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),
        margin=ft.margin.only(top=10),
    )

    login_view = ft.View(
        "/login",
        padding=0, # Remover padding da view
        bgcolor=quantum_theme["background"], # Definir bgcolor da view
        controls=[
            ft.Stack(
                controls=[
                    background,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                # Logo e título
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            # Logo do robô
                                            ft.Container(
                                                content=ft.Icon(
                                                    name=ft.icons.SMART_TOY_ROUNDED,
                                                    size=80,
                                                    color=quantum_theme["secondary"]
                                                ),
                                                border_radius=60,
                                                padding=10,
                                                gradient=ft.SweepGradient(
                                                    center=ft.alignment.center,
                                                    colors=[
                                                        quantum_theme["primary"],
                                                        ft.Colors.with_opacity(0.5, quantum_theme["secondary"]),
                                                        quantum_theme["primary"],
                                                    ],
                                                ),
                                                width=100,
                                                height=100,
                                                alignment=ft.alignment.center,
                                            ),
                                            
                                            # Título QUANTUM TRADER
                                            ft.Row(
                                                controls=[
                                                    ft.Text("QUANTUM", size=40, weight="bold", color=quantum_theme["primary"], opacity=0.9),
                                                    ft.Text("TRADER", size=40, weight="bold", color=quantum_theme["secondary"], opacity=0.9),
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            
                                            # Subtítulo e versão
                                            ft.Text("PROFESSIONAL TRADING", size=16, color=quantum_theme["text_secondary"], weight="bold", text_align=ft.TextAlign.CENTER, opacity=0.8),
                                            ft.Text("v3.0", size=12, color=quantum_theme["text_secondary"], weight="bold", text_align=ft.TextAlign.CENTER, opacity=0.6),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    margin=ft.margin.only(bottom=30) # Espaço abaixo do logo/título
                                ),
                                # Card de login
                                login_card,
                                security_indicators,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER, # Centralizar verticalmente
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ]
            ),
        ]
    )

    page.views.append(login_view)
    page.update()

def update_profile_avatar(page, image_data):
    """Atualiza o CircleAvatar do perfil na AppBar (se existir)."""
    profile_pic_src = f"data:image/png;base64,{image_data}" if image_data else None

    # Tenta encontrar a AppBar e o CircleAvatar dentro dela
    if page.views:
        current_view = page.views[-1]
        if hasattr(current_view, 'appbar') and current_view.appbar and hasattr(current_view.appbar, 'actions'):
            for action_item in current_view.appbar.actions:
                if isinstance(action_item, ft.Stack):
                    # Encontra o CircleAvatar dentro do Stack
                    for stack_item in action_item.controls:
                        if isinstance(stack_item, ft.CircleAvatar) and hasattr(stack_item, 'foreground_image_src'):
                            stack_item.foreground_image_src = profile_pic_src
                            # Se não houver imagem, remover o conteúdo de texto padrão se houver
                            if profile_pic_src:
                                stack_item.content = None
                            stack_item.update()
                            print("Avatar UI atualizado.")
                            return # Sai após encontrar e atualizar
    print("Aviso: Não foi possível encontrar o CircleAvatar do perfil para atualizar.")
