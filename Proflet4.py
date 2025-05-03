from Proflet5 import UserSession, state, quantum_theme, initialize_ui_elements, create_modal
from Proflet5 import show_choice_screen
import flet as ft
import time
import threading
from datetime import datetime
import json
import numpy as np
from collections import Counter
from Profler2 import show_modal
from Profler1 import update_balance_and_profit, payout, get_pares_disponiveis_cached, check_stop
from Proflet5 import show_loading_overlay, hide_loading_overlay
from Proflet5 import _create_log_control, log_console, stop_bot, enable_buttons, disable_buttons
from Proflet5 import estrategias_descricao
from Proflet5 import animate_appbar_title, animate_text_color
# from utils import validate_online_login, get_user_session # Comentado ou removido

def show_initial_screen(page: ft.Page, user_session: UserSession):
    # --- IMPORTAR FUNÇÕES DE ANIMAÇÃO AQUI ---
    from Proflet5 import animate_appbar_title, animate_text_color
    # -----------------------------------------

    # === 1. DEFINIR Refs PRIMEIRO ===
    appbar_title1_ref = ft.Ref[ft.Text]()
    appbar_title2_ref = ft.Ref[ft.Text]()
    fab_icon_ref = ft.Ref[ft.Icon]()
    # ================================

    print(f"DEBUG [show_initial_screen]: Recriando labels e atualizando page.ui")
    # Recriar labels e atualizar page.ui CADA VEZ que a tela é exibida
    status_label = ft.Text("", size=14, weight="bold")
    balance_label = ft.Text("", size=14, color=quantum_theme["text"])
    total_profit_label = ft.Text("", size=14, color=quantum_theme["success"])
    win_label = ft.Text("", size=14, color=quantum_theme["success"])
    loss_label = ft.Text("", size=14, color=quantum_theme["error"])
    
    page.ui['status_label'] = status_label
    page.ui['balance_label'] = balance_label
    page.ui['total_profit_label'] = total_profit_label
    page.ui['win_label'] = win_label
    page.ui['loss_label'] = loss_label
    
    print(f"DEBUG [show_initial_screen]: NOVOS IDs -> balance_label ID = {id(balance_label)}, total_profit_label ID = {id(total_profit_label)}")

    # Garante que o log_list_view está inicializado (pode manter a lógica atual)
    if 'log_list_view' not in page.ui:
        page.ui['log_list_view'] = ft.ListView(expand=True, spacing=5, auto_scroll=True)

    # profile_pic e user_name (mantém como antes)
    profile_pic = user_session.profile_pic
    user_name = user_session.name_var if user_session.name_var else user_session.email

    # --- Verificar Status da Conexão (mantém como antes) --- #
    api_instance = state.get('API')
    is_connected = api_instance is not None and api_instance.check_connect()
    status_text = "Conectado" if is_connected else "Não Conectado"
    status_color = quantum_theme["success"] if is_connected else quantum_theme["error"]
    # ------------------------------------------------------------ #

    # --- Definir valores dos NOVOS labels a partir do state --- 
    current_currency = state.get('currency', user_session.currency)
    current_balance = state.get('account_balance', user_session.account_balance)
    current_profit = state.get('total_profit', 0.0)
    current_wins = state.get('win_count', 0)
    current_losses = state.get('loss_count', 0)

    status_label.value = status_text
    status_label.color = status_color
    balance_label.value = f"Saldo: {current_currency} {current_balance:.2f}"
    total_profit_label.value = f"Lucro Total: {current_currency} {current_profit:.2f}"
    win_label.value = f"Vitórias: {current_wins}"
    loss_label.value = f"Derrotas: {current_losses}"
    # ------------------------------------------------------

    # Configurar tema da página
    page.bgcolor = quantum_theme["background"]
    page.theme_mode = "dark"

    # --- LÓGICA PARA POPULAR O LOG LIST VIEW (mantém como antes) ---
    log_list_view = page.ui.get('log_list_view')
    if not log_list_view:
        print("ERRO CRÍTICO [show_initial_screen]: log_list_view não encontrado em page.ui!")
        log_list_view = ft.Text("Erro crítico: log_list_view não inicializado.", color="red")
    else:
        print(f"DEBUG [show_initial_screen]: Exibindo log_list_view com ID: {id(log_list_view)}")

    # --- Conteúdo Principal da Tela (Usa os NOVOS labels) --- #
    main_content_column = ft.Column([
        # Status do usuário
        ft.Container(
            content=ft.Column([
                ft.Divider(height=2, color=quantum_theme["surface"]),
                # Informações da conta (Card 1)
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, color=quantum_theme["secondary"]),
                            # Título da Seção em Negrito
                            ft.Text("Informações da Conta", size=18, weight=ft.FontWeight.BOLD, color=quantum_theme["secondary"]),
                        ], spacing=10),
                        ft.Divider(height=1, color=quantum_theme["surface"]),
                        # Métricas Destacadas
                        ft.Row([
                            # Status (Rótulo e Valor em Negrito)
                            ft.Column([
                                ft.Text("Status", size=13, weight=ft.FontWeight.BOLD, color=quantum_theme["text_secondary"]),
                                status_label,  # Usa o NOVO objeto (estilo aplicado na inicialização abaixo)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            # Saldo (Rótulo e Valor em Negrito)
                            ft.Column([
                                ft.Text("Saldo", size=13, weight=ft.FontWeight.BOLD, color=quantum_theme["text_secondary"]),
                                balance_label,  # Usa o NOVO objeto (estilo aplicado na inicialização abaixo)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            # Lucro Total (Rótulo e Valor em Negrito)
                            ft.Column([
                                ft.Text("Lucro Total", size=13, weight=ft.FontWeight.BOLD, color=quantum_theme["text_secondary"]),
                                total_profit_label,  # Usa o NOVO objeto (estilo aplicado na inicialização abaixo)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=15),
                    ], spacing=10),
                    # Aplicar novo estilo ao card de informações com MAIS transparência
                    bgcolor=ft.colors.with_opacity(0.70, quantum_theme["card_bg"]), # Opacidade 0.70
                    border_radius=15,
                    padding=15,
                    border=ft.border.all(1, ft.colors.with_opacity(0.5, quantum_theme["surface"])), # Borda sutil
                    margin=ft.margin.only(top=10, bottom=20),
                ),
                # Estatísticas rápidas (Card 2)
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.ANALYTICS, color=quantum_theme["secondary"]),
                             # Título da Seção em Negrito
                            ft.Text("Desempenho", size=18, weight=ft.FontWeight.BOLD, color=quantum_theme["secondary"]),
                        ], spacing=10),
                        ft.Divider(height=1, color=quantum_theme["surface"]),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                     # Rótulo e Valor em Negrito
                                    ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, color=quantum_theme["success"], size=16), ft.Text("Vitórias", size=13, weight=ft.FontWeight.BOLD, color=quantum_theme["text_secondary"])], spacing=5),
                                    win_label,  # Usa o NOVO objeto (estilo aplicado na inicialização abaixo)
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=10, # Padding ajustado
                                # Usar cor sólida com opacidade para destaque sutil
                                bgcolor=ft.Colors.with_opacity(0.1, quantum_theme["success"]),
                                border_radius=10,
                                expand=True,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column([
                                     # Rótulo e Valor em Negrito
                                    ft.Row([ft.Icon(ft.icons.HIGHLIGHT_OFF, color=quantum_theme["error"], size=16), ft.Text("Derrotas", size=13, weight=ft.FontWeight.BOLD, color=quantum_theme["text_secondary"])], spacing=5),
                                    loss_label,  # Usa o NOVO objeto (estilo aplicado na inicialização abaixo)
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=10, # Padding ajustado
                                # Usar cor sólida com opacidade para destaque sutil
                                bgcolor=ft.Colors.with_opacity(0.1, quantum_theme["error"]),
                                border_radius=10,
                                expand=True,
                                alignment=ft.alignment.center
                            ),
                        ], spacing=10),
                    ], spacing=10), # Espaçamento interno da coluna
                    # Aplicar novo estilo ao card de desempenho com MAIS transparência
                    bgcolor=ft.colors.with_opacity(0.70, quantum_theme["card_bg"]), # Opacidade 0.70
                    border_radius=15,
                    padding=15,
                    border=ft.border.all(1, ft.colors.with_opacity(0.5, quantum_theme["surface"])), # Borda sutil
                    margin=ft.margin.only(top=10, bottom=20), # Remover margem esquerda, manter top/bottom
                ),
            ]), # Fim da Column principal do conteúdo
            padding=20,
            # Remover bgcolor e border_radius do container externo
            # bgcolor=quantum_theme["card_bg"],
            # border_radius=20,
            margin=ft.margin.only(top=0, left=0, right=0, bottom=0), # Remover margens
            expand=True # Permitir que o card principal expanda
        )
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE) # Adicionar scroll à coluna principal
    # --- Fim do Conteúdo Principal --- #

    # --- Inicialização dos Labels (Garantir Negrito nos Valores) --- #
    if status_label:
        # ... (lógica do status)
        status_label.weight = ft.FontWeight.BOLD # Garantir negrito
    if balance_label:
        # ... (lógica do saldo)
        balance_label.weight = ft.FontWeight.BOLD # Garantir negrito
    if total_profit_label:
        # ... (lógica do lucro)
        total_profit_label.weight = ft.FontWeight.BOLD # Garantir negrito
    if win_label:
        win_label.weight = ft.FontWeight.BOLD # Garantir negrito
    if loss_label:
        loss_label.weight = ft.FontWeight.BOLD # Garantir negrito
    # ------------------------------------------------------------ #

    # --- Construir a View (Usa main_content_column com os NOVOS labels) --- #
    initial_view = ft.View(
        route="/initial_screen",
        controls=[
            main_content_column # Adicionar a coluna principal aqui
        ],
        appbar=ft.AppBar(
             title=ft.Container(
                content=ft.Row([
                    ft.Text( # Texto 1
                        # === 2. Associar Ref AQUI ===
                        ref=appbar_title1_ref,
                        value="QUANTUM",
                        size=28,
                        weight="bold",
                        color=quantum_theme["primary"], # Cor inicial
                    ),
                    ft.Text( # Texto 2
                         # === 2. Associar Ref AQUI ===
                        ref=appbar_title2_ref,
                        value="PRO",
                        size=28,
                        weight="bold",
                        color=quantum_theme["secondary"], # Cor inicial
                    ),
                ]),
                padding=10,
            ),
            center_title=True,
            bgcolor=quantum_theme["card_bg"], # Usar cor de card para AppBar
            actions=[
                # --- Botão de Minimizar --- #
                ft.IconButton(
                    icon=ft.icons.KEYBOARD_ARROW_DOWN,
                    icon_color=quantum_theme["text_secondary"],
                    tooltip="Minimizar",
                    on_click=lambda _: setattr(page, 'window_minimized', True) or page.update()
                ),
                # -------------------------
                ft.Stack(
                    [
                        ft.CircleAvatar(
                            foreground_image_src=f"data:image/png;base64,{profile_pic}" if profile_pic else None,
                            bgcolor=quantum_theme["primary"] if not profile_pic else None,
                            content=ft.Text(
                                user_name[0].upper() if user_name else "U",
                                color=quantum_theme["text"],
                                size=20,
                                weight="bold"
                            ) if not profile_pic else None,
                        ),
                        ft.Container(
                            content=ft.CircleAvatar(bgcolor=quantum_theme["success"], radius=5),
                            alignment=ft.alignment.bottom_left,
                        ),
                    ],
                    width=40,
                    height=40,
                ),
                ft.Text(user_name, size=14, weight="w500", color=quantum_theme["text"])
            ]
        ),
        bottom_appbar=ft.BottomAppBar(
            bgcolor=quantum_theme["card_bg"], # Usar cor de card para BottomAppBar
            shape=ft.NotchShape.CIRCULAR,
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            icon_color=quantum_theme["text"],
                            tooltip="Configurações",
                            on_click=lambda e: show_main_screen(e.page, user_session) # Apenas navegar
                        ),
                         # Remover gradiente do botão de configurações para um look mais flat
                        # gradient=ft.LinearGradient(...),
                        bgcolor=quantum_theme["surface"], # Usar cor surface
                        border_radius=35,
                        width=70,
                        height=70,
                        alignment=ft.alignment.center,
                    ),
                    # --- Comentando o botão Insights/Catalogador ---
                    # ft.IconButton(
                    #     icon=ft.icons.INSIGHTS,
                    #     icon_color=quantum_theme["text"],
                    #     tooltip="Catalogador", # Adicionado tooltip
                    #     on_click=lambda _: (
                    #         __import__('Profler2').show_catalog_modal(state.get('API'), page)
                    #         if state.get('API') 
                    #         else print("API não conectada para catalogador.")
                    #     ),
                    # ),
                    # -----------------------------------------------
                    ft.Container(expand=True),
                ]
            ),
        ),
        floating_action_button=ft.FloatingActionButton(
            content=ft.Container(
                content=ft.Icon(
                    # === 2. Associar Ref AQUI ===
                    ref=fab_icon_ref,
                    name=ft.Icons.BOLT_ROUNDED,
                    size=32,
                    color=quantum_theme["text"] # Cor inicial
                ),
                # --- GRADIENTE IGUAL AO BOTÃO CONECTAR --- 
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        quantum_theme["primary"], # Cor 1 do botão CONECTAR
                        ft.Colors.with_opacity(0.8, quantum_theme["secondary"]) # Cor 2 do botão CONECTAR
                    ],
                    rotation=45, # Manter rotação se desejar
                ),
                # ----------------------------------------
                animate=ft.animation.Animation(1000, "easeInOut"),
                border_radius=50,
                padding=15,
            ),
            bgcolor=ft.Colors.TRANSPARENT,
            tooltip="Iniciar Robô",
            on_click=lambda _: start_strategy(page, user_session),
            scale=1.4,
            height=70,
            width=70,
            elevation=10, # Reduzir elevação
            shape=ft.RoundedRectangleBorder(radius=35),
        ),
        floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
        bgcolor=quantum_theme["background"],
        padding=0 # Remover padding da View se houver
    )
    # --- Fim da Construção da View --- #

    page.views.clear()
    page.views.append(initial_view) # Adicionar a View
    page.update() # Atualizar a página após montar a view
    
    # === 3. Iniciar animações com as Refs DEFINIDAS ===
    state['animating_appbar_title'] = True
    page.run_thread(animate_appbar_title, page, appbar_title1_ref, appbar_title2_ref, 'animating_appbar_title')
    state['animating_fab_icon'] = True
    page.run_thread(animate_text_color, page, fab_icon_ref, 'animating_fab_icon')
    # ====================================================

    # --- Inscrever handler de atualização do fundo no pubsub ---
    def on_stats_update_main(message, page, user_session):
        if message != "update_stats":
            return
            
        try:
            # Atualizar com os valores mais recentes do state
            status_label = page.ui.get('status_label')
            balance_label = page.ui.get('balance_label')
            total_profit_label = page.ui.get('total_profit_label')
            win_label = page.ui.get('win_label')
            loss_label = page.ui.get('loss_label')
            
            current_currency = state.get('currency', user_session.currency)
            current_balance = state.get('account_balance', user_session.account_balance)
            current_profit = state.get('total_profit', 0.0)
            current_wins = state.get('win_count', 0)
            current_losses = state.get('loss_count', 0)
            api_instance = state.get('API')
            is_connected = api_instance is not None and api_instance.check_connect()
            status_text = "Conectado" if is_connected else "Não Conectado"
            status_color = quantum_theme["success"] if is_connected else quantum_theme["error"]
            
            # Atualizar os elementos individualmente
            if status_label and status_label.page:
                status_label.value = status_text
                status_label.color = status_color
                status_label.update()
                
            if balance_label and balance_label.page:
                balance_label.value = f"Saldo: {current_currency} {current_balance:.2f}"
                balance_label.update()
                
            if total_profit_label and total_profit_label.page:
                total_profit_label.value = f"Lucro Total: {current_currency} {current_profit:.2f}"
                total_profit_label.color = quantum_theme["success"] if current_profit >= 0 else quantum_theme["error"]
                total_profit_label.update()
                
            if win_label and win_label.page:
                win_label.value = f"Vitórias: {current_wins}"
                win_label.update()
                
            if loss_label and loss_label.page:
                loss_label.value = f"Derrotas: {current_losses}"
                loss_label.update()
                
            # Forçar atualização da página para garantir que tudo seja redesenhado
            print("Atualizando interface principal com novos dados!")
            page.update()
            
        except Exception as e:
            print(f"[on_stats_update_main] Erro ao atualizar interface principal: {e}")
            
    if hasattr(page, 'pubsub'):
        page.pubsub.subscribe(lambda msg: on_stats_update_main(msg, page, user_session))
        
    # Iniciar a thread de atualização em tempo real da tela principal
    stop_flag_main = {'active': True}
    threading.Thread(
        target=update_main_screen_real_time,
        args=(stop_flag_main, state, page, user_session),
        daemon=True
    ).start()
    print("DEBUG: Thread update_main_screen_real_time iniciada com NOVOS labels.")

def update_name_var(e, user_session):
    user_session.name_var = e.control.value

def show_main_screen(page: ft.Page, user_session: UserSession):
    # Access UI elements via page.ui
    email_textfield = page.ui.get('email_textfield')
    password_textfield = page.ui.get('password_textfield')
    plataforma_dropdown = page.ui.get('plataforma_dropdown')
    account_type_dropdown = page.ui.get('account_type_dropdown')
    status_label = page.ui.get('status_label')
    balance_label = page.ui.get('balance_label')
    total_profit_label = page.ui.get('total_profit_label')
    asset_dropdown = page.ui.get('asset_dropdown')
    entry_value_texttextfield = page.ui.get('entry_value_texttextfield')
    stop_win_texttextfield = page.ui.get('stop_win_texttextfield')
    stop_loss_texttextfield = page.ui.get('stop_loss_texttextfield')
    use_stop_loss_checkbox = page.ui.get('use_stop_loss_checkbox')
    analyze_averages_checkbox = page.ui.get('analyze_averages_checkbox')
    average_candles_texttextfield = page.ui.get('average_candles_texttextfield')
    use_martingale_checkbox = page.ui.get('use_martingale_checkbox')
    martingale_levels_texttextfield = page.ui.get('martingale_levels_texttextfield')
    martingale_factor_texttextfield = page.ui.get('martingale_factor_texttextfield')
    use_soros_checkbox = page.ui.get('use_soros_checkbox')
    soros_levels_texttextfield = page.ui.get('soros_levels_texttextfield')
    strategy_dropdown = page.ui.get('strategy_dropdown')
    start_time_texttextfield = page.ui.get('start_time_texttextfield')
    end_time_texttextfield = page.ui.get('end_time_texttextfield')
    use_schedule_checkbox = page.ui.get('use_schedule_checkbox')
    reentry_win_checkbox = page.ui.get('reentry_win_checkbox')
    use_ai_checkbox = page.ui.get('use_ai_checkbox')
    reverse_direction_checkbox = page.ui.get('reverse_direction_checkbox')
    use_winning_patterns_checkbox = page.ui.get('use_winning_patterns_checkbox')
    use_rsi_checkbox = page.ui.get('use_rsi_checkbox')
    periodo_rsi_textfield = page.ui.get('periodo_rsi_textfield')
    win_label = page.ui.get('win_label')
    loss_label = page.ui.get('loss_label')
    # === ADICIONAR GETTER PARA NOVO CHECKBOX ===
    analyze_all_pairs_checkbox = page.ui.get('analyze_all_pairs_checkbox')
    # =========================================

    # Basic check for a few critical elements
    if None in [email_textfield, password_textfield, plataforma_dropdown, asset_dropdown]:
        print("ERRO em show_main_screen: Elementos críticos da UI não encontrados em page.ui")
        page.add(ft.Text("Erro ao carregar a tela principal."))
        page.update()
        return

    # Adicionar getters para os controles que faltavam na UI
    strategy_dropdown = page.ui.get('strategy_dropdown')
    start_time_texttextfield = page.ui.get('start_time_texttextfield')
    end_time_texttextfield = page.ui.get('end_time_texttextfield')
    use_schedule_checkbox = page.ui.get('use_schedule_checkbox')
    reentry_win_checkbox = page.ui.get('reentry_win_checkbox')
    use_ai_checkbox = page.ui.get('use_ai_checkbox')
    reverse_direction_checkbox = page.ui.get('reverse_direction_checkbox')
    use_winning_patterns_checkbox = page.ui.get('use_winning_patterns_checkbox')
    use_rsi_checkbox = page.ui.get('use_rsi_checkbox')
    periodo_rsi_textfield = page.ui.get('periodo_rsi_textfield')

    profile_pic = user_session.profile_pic
    user_name = user_session.name_var if user_session.name_var else user_session.email

    # Configurar tema da página
    page.bgcolor = quantum_theme["background"]
    page.theme_mode = "dark"

    # Carregar dados do login nos elementos da UI
    if email_textfield: email_textfield.value = user_session.email
    if password_textfield: password_textfield.value = user_session.password
    if account_type_dropdown: account_type_dropdown.value = user_session.account_type_var
    # Carregar valores para os novos campos (se existirem em user_session)
    if start_time_texttextfield: start_time_texttextfield.value = getattr(user_session, 'start_time_var', '00:00')
    if end_time_texttextfield: end_time_texttextfield.value = getattr(user_session, 'end_time_var', '23:59')
    if use_schedule_checkbox: use_schedule_checkbox.value = getattr(user_session, 'use_schedule_var', False)
    if reentry_win_checkbox: reentry_win_checkbox.value = getattr(user_session, 'reentry_win_var', False)
    if use_ai_checkbox: use_ai_checkbox.value = getattr(user_session, 'use_ai_var', False)
    if reverse_direction_checkbox: reverse_direction_checkbox.value = getattr(user_session, 'reverse_direction_var', False)
    if use_winning_patterns_checkbox: use_winning_patterns_checkbox.value = getattr(user_session, 'use_winning_patterns_var', False)
    # Carregar valores para campos existentes que foram movidos
    if entry_value_texttextfield: entry_value_texttextfield.value = str(getattr(user_session, 'entry_value_var', 5.0))
    if stop_win_texttextfield: stop_win_texttextfield.value = str(getattr(user_session, 'stop_win_var', 50.0))
    if stop_loss_texttextfield: stop_loss_texttextfield.value = str(getattr(user_session, 'stop_loss_var', 50.0))
    if use_stop_loss_checkbox: use_stop_loss_checkbox.value = getattr(user_session, 'use_stop_loss_var', False)
    if analyze_averages_checkbox: analyze_averages_checkbox.value = getattr(user_session, 'analyze_averages_var', False)
    if average_candles_texttextfield: average_candles_texttextfield.value = str(getattr(user_session, 'average_candles_var', 60))
    if use_martingale_checkbox: use_martingale_checkbox.value = getattr(user_session, 'use_martingale_var', False)
    if martingale_levels_texttextfield: martingale_levels_texttextfield.value = str(getattr(user_session, 'martingale_levels_var', 2))
    if martingale_factor_texttextfield: martingale_factor_texttextfield.value = str(getattr(user_session, 'martingale_factor_var', 2.0))
    if use_soros_checkbox: use_soros_checkbox.value = getattr(user_session, 'use_soros_var', False)
    if soros_levels_texttextfield: soros_levels_texttextfield.value = str(getattr(user_session, 'soros_levels_var', 1))
    if use_rsi_checkbox: use_rsi_checkbox.value = getattr(user_session, 'use_rsi_var', False)
    if periodo_rsi_textfield: periodo_rsi_textfield.value = str(getattr(user_session, 'periodo_rsi_var', 14))
    if strategy_dropdown: strategy_dropdown.value = str(getattr(user_session, 'strategy_var', 1))
    if asset_dropdown: asset_dropdown.value = getattr(user_session, 'asset_var', None)
    # === CARREGAR VALOR DO NOVO CHECKBOX ===
    if analyze_all_pairs_checkbox: analyze_all_pairs_checkbox.value = getattr(user_session, 'analyze_all_pairs_var', False)
    # =======================================

    # --- Adicionar Tooltips ---
    if email_textfield: email_textfield.tooltip = "Seu email de login na corretora"
    if password_textfield: password_textfield.tooltip = "Sua senha na corretora (armazenada localmente)"
    if plataforma_dropdown: plataforma_dropdown.tooltip = "Corretora desejada"
    if account_type_dropdown: account_type_dropdown.tooltip = "Tipo de conta (Real ou Treinamento)"
    if asset_dropdown: asset_dropdown.tooltip = "Par de moedas ou ativo para operar"
    if entry_value_texttextfield: entry_value_texttextfield.tooltip = "Valor inicial de cada operação"
    if stop_win_texttextfield: stop_win_texttextfield.tooltip = "Meta de lucro para parar o robô"
    if stop_loss_texttextfield: stop_loss_texttextfield.tooltip = "Limite de perda para parar o robô"
    if use_stop_loss_checkbox: use_stop_loss_checkbox.tooltip = "Ativar/Desativar o limite de Stop Loss"
    if analyze_averages_checkbox: analyze_averages_checkbox.tooltip = "Usar análise de médias móveis como confirmação de tendência"
    if average_candles_texttextfield: average_candles_texttextfield.tooltip = "Número de candles para cálculo da média móvel"
    if use_martingale_checkbox: use_martingale_checkbox.tooltip = "Aplicar Martingale após uma perda"
    if martingale_levels_texttextfield: martingale_levels_texttextfield.tooltip = "Número máximo de níveis de Martingale"
    if martingale_factor_texttextfield: martingale_factor_texttextfield.tooltip = "Fator de multiplicação para o valor da entrada no Martingale"
    if use_soros_checkbox: use_soros_checkbox.tooltip = "Aplicar Soros após uma vitória (reinvestir lucro)"
    if soros_levels_texttextfield: soros_levels_texttextfield.tooltip = "Número máximo de níveis de Soros"
    if strategy_dropdown: strategy_dropdown.tooltip = "Estratégia principal a ser utilizada pelo robô"
    if start_time_texttextfield: start_time_texttextfield.tooltip = "Horário de início das operações (HH:MM)"
    if end_time_texttextfield: end_time_texttextfield.tooltip = "Horário de término das operações (HH:MM)"
    if use_schedule_checkbox: use_schedule_checkbox.tooltip = "Ativar/Desativar operação por horário agendado"
    if reentry_win_checkbox: reentry_win_checkbox.tooltip = "Entrar novamente imediatamente após uma vitória (sem esperar novo sinal)"
    if use_ai_checkbox: use_ai_checkbox.tooltip = "Utilizar inteligência artificial para análise complementar (se disponível)"
    if reverse_direction_checkbox: reverse_direction_checkbox.tooltip = "Inverter a direção da entrada sugerida pela estratégia principal"
    if use_winning_patterns_checkbox: use_winning_patterns_checkbox.tooltip = "Priorizar operações baseadas em padrões de velas vencedores identificados"
    if use_rsi_checkbox: use_rsi_checkbox.tooltip = "Utilizar o indicador RSI como filtro ou confirmação"
    if periodo_rsi_textfield: periodo_rsi_textfield.tooltip = "Período de cálculo para o indicador RSI"
    # === ADICIONAR TOOLTIP PARA NOVO CHECKBOX ===
    if analyze_all_pairs_checkbox: analyze_all_pairs_checkbox.tooltip = "Se ativo, o robô analisará todos os pares digitais com payout em vez do par selecionado"
    # ==========================================
    # --- Fim Adicionar Tooltips ---

    # Botão de conectar
    connect_button = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CLOUD_SYNC, color=quantum_theme["text"]),
                ft.Text("CONECTAR", size=16, weight="bold", color=quantum_theme["text"])
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    quantum_theme["primary"],
                    ft.Colors.with_opacity(0.8, quantum_theme["secondary"])
                ],
            ),
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=lambda e: (
            # --- ATUALIZAR ESTADO DO BOTÃO --- 
            setattr(e.control, 'disabled', True),
            setattr(e.control, 'content', ft.Container( # Novo conteúdo
                content=ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color=quantum_theme["text"]),
                    ft.Text("CONECTANDO", size=16, weight="bold", color=quantum_theme["text"])
                ], alignment=ft.MainAxisAlignment.CENTER),
                # Copiar estilo do container original
                padding=10,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        quantum_theme["primary"],
                        ft.Colors.with_opacity(0.8, quantum_theme["secondary"])
                    ],
                ),
            )),
            e.page.update(e.control), # Atualiza apenas o botão
            # --- FIM ATUALIZAR ESTADO DO BOTÃO ---

            # --- ATUALIZAR user_session ANTES de conectar --- 
            setattr(user_session, 'account_type_var', e.page.ui.get('account_type_dropdown').value),
            print(f"DEBUG: account_type_var em user_session ANTES de conectar: {user_session.account_type_var}"), # DEBUG
            # ------------------------------------------------
            
            # Atualiza o status imediatamente antes de iniciar a thread
            setattr(e.page.ui['status_label'], 'value', "Conectando..."),
            setattr(e.page.ui['status_label'], 'color', quantum_theme["text_secondary"]),
            e.page.update(), # Atualiza o label de status
            # Inicia a conexão na thread
            e.page.run_thread(
                lambda: __import__('proflet').start_connection(e, user_session) # Lambda chama a função com args
            )
        )
    )

    # Função para atualizar paridades disponíveis
    def update_available_pairs():
        api_instance = state.get('API')
        if api_instance and api_instance.check_connect():
            try:
                # Buscar somente ativos digitais com payout positivo e categorias
                from Profler1 import get_pares_disponiveis
                pares_categorizados = get_pares_disponiveis('API')
                
                # Separar por categoria
                populares = []
                otc = []
                outros = []
                for nome, info in pares_categorizados.items():
                    if info['categoria'] == 'populares':
                        populares.append((nome, info['payout']))
                    elif info['categoria'] == 'otc':
                        otc.append((nome, info['payout']))
                    else:
                        outros.append((nome, info['payout']))
                
                options = []
                if populares:
                    options.append(ft.dropdown.Option("header_populares", text="=== ATIVOS POPULARES ===", disabled=True))
                    for nome, payout in populares:
                        options.append(ft.dropdown.Option(nome, text=f"{nome.replace('-', '/')} | {payout:.1f}%"))
                if otc:
                    options.append(ft.dropdown.Option("header_otc", text="=== ATIVOS OTC ===", disabled=True))
                    for nome, payout in otc:
                        options.append(ft.dropdown.Option(nome, text=f"{nome.replace('-', '/')} | {payout:.1f}%"))
                if outros:
                    options.append(ft.dropdown.Option("header_outros", text="=== OUTROS ATIVOS ===", disabled=True))
                    for nome, payout in outros:
                        options.append(ft.dropdown.Option(nome, text=f"{nome.replace('-', '/')} | {payout:.1f}%"))
                
                # Priorizar valor existente se ainda disponível
                current_asset_value = page.ui.get('asset_dropdown').value if page.ui.get('asset_dropdown') else None
                asset_value = None
                if current_asset_value and any(opt.key == current_asset_value for opt in options):
                    asset_value = current_asset_value
                else:
                    # Selecionar o primeiro ativo válido (ignorando headers)
                    for opt in options:
                        if not opt.disabled:
                            asset_value = opt.key
                            break
                _update_asset_dropdown(page, options, asset_value)
                
            except Exception as e:
                print(f"Erro ao atualizar paridades: {e}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Erro ao atualizar paridades: {str(e)}"),
                    bgcolor=quantum_theme["error"]
                )
                page.snack_bar.open = True
                page.update()

    def _update_asset_dropdown(page, options, value):
        asset_dropdown = page.ui.get('asset_dropdown')
        if asset_dropdown:
            asset_dropdown.options = options
            asset_dropdown.value = value
            asset_dropdown.update()

    # Botão para atualizar paridades
    refresh_pairs_button = ft.IconButton(
        icon=ft.icons.REFRESH,
        icon_color=quantum_theme["secondary"],
        tooltip="Atualizar Paridades",
        on_click=lambda _: update_available_pairs()
    )

    # --- Definir Conteúdo das Abas ---

    # Aba Conta
    account_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.ACCOUNT_CIRCLE, color=quantum_theme["secondary"], size=20),
                ft.Text("Dados da Conta", size=18, weight="w600", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            plataforma_dropdown,
            email_textfield,
            password_textfield,
            account_type_dropdown,
            connect_button,
            ft.Divider(color=quantum_theme["surface"], height=1),
            ft.Row([
                ft.Text("Status:", color=quantum_theme["text_secondary"]),
                status_label,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("Saldo:", color=quantum_theme["text_secondary"]),
                balance_label,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("Lucro Total:", color=quantum_theme["text_secondary"]),
                total_profit_label,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=15)
    )

    # Aba Estratégia
    strategy_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
             ft.Row([
                ft.Icon(ft.icons.TRENDING_UP, color=quantum_theme["secondary"], size=20),
                ft.Text("Configuração da Estratégia", size=18, weight="w500", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            ft.Row([
                ft.Text("Estratégia Principal", size=14, color=quantum_theme["text_secondary"]),
                ft.IconButton(
                    icon=ft.icons.INFO_OUTLINE,
                    icon_color=quantum_theme["secondary"],
                    tooltip="Ver descrição da estratégia selecionada",
                    # AJUSTAR on_click PARA CHAMAR A FUNÇÃO DO MODAL
                    on_click=lambda e: show_strategy_description_modal(
                        page=e.page, # Passar a página
                        strategy_id_str=page.ui.get('strategy_dropdown').value # Pegar valor atual do dropdown
                    )
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            strategy_dropdown,
            ft.Row([
                 ft.Text("Par de Moedas / Ativo", size=14, color=quantum_theme["text_secondary"]),
                 refresh_pairs_button, # Botão de atualizar aqui
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            asset_dropdown,
            entry_value_texttextfield,
            # === ADICIONAR CHECKBOX AQUI ===
            analyze_all_pairs_checkbox,
            # =============================
            reentry_win_checkbox,
            reverse_direction_checkbox,
        ], spacing=15)
    )

    # Aba Gerenciamento de Risco
    risk_management_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
             ft.Row([
                ft.Icon(ft.icons.SHIELD_OUTLINED, color=quantum_theme["secondary"], size=20),
                ft.Text("Gerenciamento de Risco", size=18, weight="w600", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            stop_win_texttextfield,
            stop_loss_texttextfield,
            use_stop_loss_checkbox,
        ], spacing=15)
    )

    # Aba Multiplicadores (Martingale/Soros)
    multipliers_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
             ft.Row([
                ft.Icon(ft.icons.MULTIPLE_STOP, color=quantum_theme["secondary"], size=20),
                ft.Text("Multiplicadores (Gale/Soros)", size=18, weight="w600", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            use_martingale_checkbox,
            martingale_levels_texttextfield,
            martingale_factor_texttextfield,
            ft.Divider(color=quantum_theme["surface"], height=1),
            use_soros_checkbox,
            soros_levels_texttextfield,
        ], spacing=15)
    )

    # Aba Análise Técnica
    technical_analysis_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
             ft.Row([
                ft.Icon(ft.icons.ANALYTICS_OUTLINED, color=quantum_theme["secondary"], size=20),
                ft.Text("Análise Técnica Auxiliar", size=18, weight="w600", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            analyze_averages_checkbox,
            average_candles_texttextfield,
            ft.Divider(color=quantum_theme["surface"], height=1),
            use_rsi_checkbox,
            periodo_rsi_textfield,
        ], spacing=15)
    )

    # Aba Avançado/Outros
    advanced_tab_content = ft.Container(
        padding=20,
        content=ft.Column([
             ft.Row([
                ft.Icon(ft.icons.SETTINGS_APPLICATIONS, color=quantum_theme["secondary"], size=20),
                ft.Text("Configurações Avançadas", size=18, weight="w600", color=quantum_theme["text"]),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=quantum_theme["surface"], height=1),
            use_winning_patterns_checkbox,
            use_ai_checkbox,
            ft.Divider(color=quantum_theme["surface"], height=1),
            use_schedule_checkbox,
            start_time_texttextfield,
            end_time_texttextfield,
        ], spacing=15)
    )

    # --- Fim Definir Conteúdo das Abas ---

    main_screen = ft.View(
        "/main_screen",
        [
            ft.AppBar(
                title=ft.Container(
                    content=ft.Row([
                        ft.Text(
                            "QUANTUM",
                            size=28,
                            weight="bold",
                            color=quantum_theme["primary"],
                        ),
                        ft.Text(
                            "PRO",
                            size=28,
                            weight="bold",
                            color=quantum_theme["secondary"],
                        ),
                    ]),
                    padding=10,
                ),
                bgcolor=ft.Colors.with_opacity(0.1, quantum_theme["surface"]),
                center_title=True,
            ),
            ft.ListView(
                expand=True,
                controls=[
                    # account_info_card, # REMOVIDO
                    # strategy_card, # REMOVIDO
                    # --- Adicionar Tabs ---
                    ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        tabs=[
                            ft.Tab(
                                text="Conta",
                                icon=ft.icons.ACCOUNT_CIRCLE_OUTLINED,
                                content=account_tab_content,
                            ),
                            ft.Tab(
                                text="Estratégia",
                                icon=ft.icons.TRENDING_UP,
                                content=strategy_tab_content,
                            ),
                             ft.Tab(
                                text="Gerenciamento",
                                icon=ft.icons.SHIELD_OUTLINED,
                                content=risk_management_tab_content,
                            ),
                             ft.Tab(
                                text="Multiplicadores",
                                icon=ft.icons.MULTIPLE_STOP_OUTLINED,
                                content=multipliers_tab_content,
                            ),
                             ft.Tab(
                                text="Análise Téc.", # Abreviação para caber
                                icon=ft.icons.ANALYTICS_OUTLINED,
                                content=technical_analysis_tab_content,
                            ),
                            ft.Tab(
                                text="Avançado",
                                icon=ft.icons.SETTINGS_APPLICATIONS_OUTLINED,
                                content=advanced_tab_content,
                            ),
                        ],
                        expand=1, # Para as abas preencherem o espaço
                        label_color=quantum_theme["primary"],
                        unselected_label_color=quantum_theme["text_secondary"],
                        indicator_color=quantum_theme["secondary"],
                        divider_color=quantum_theme["surface"],
                    ),
                    # --- Fim Adicionar Tabs ---
                ],
                padding=0, # Remover padding do ListView se houver
            ),
            # --- Adicionar Botões Salvar/Voltar AQUI ---
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.TRANSPARENT, # Para o gradiente funcionar
                            elevation=0, # Remover elevação padrão se usar gradiente
                        ),
                        content=ft.Container(
                            content=ft.Row([ # Conteúdo do botão
                                ft.Icon(ft.icons.SAVE, color=quantum_theme["text"]),
                                ft.Text("SALVAR", weight="bold", color=quantum_theme["text"])
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                            padding=10,
                            # Gradiente semelhante ao botão CONECTAR
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left,
                                end=ft.alignment.bottom_right,
                                colors=[
                                    quantum_theme["primary"],
                                    ft.Colors.with_opacity(0.8, quantum_theme["secondary"])
                                ],
                            ),
                            border_radius=10, # Manter raio
                        ),
                        on_click=lambda e: save_user_configurations(page, user_session),
                    ),
                    ft.OutlinedButton(
                        "VOLTAR",
                        icon=ft.icons.ARROW_BACK,
                        style=ft.ButtonStyle(
                            color=quantum_theme["text_secondary"],
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: show_initial_screen(page, user_session),
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                padding=ft.padding.only(top=10, bottom=20), # Ajustar padding conforme necessário
            ),
            # --- Fim Adicionar Botões ---
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    page.views.clear()
    page.views.append(main_screen)
    page.update()

def averages(candles, user_session):
    total = 0
    for i in candles:
        total += i['close']
    average = total / user_session.average_candles_var

    if average > candles[-1]['close']:
        trend = 'put'
    else:
        trend = 'call'

    return trend

def calculate_RSI(candles, period=14):
    gains = []
    losses = []

    for i in range(1, len(candles)):
        current_close = candles[i]['close']
        previous_close = candles[i - 1]['close']
        change = current_close - previous_close

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    average_gains = sum(gains[-period:]) / period
    average_losses = sum(losses[-period:]) / period

    if average_losses == 0:
        return 100
    else:
        rs = average_gains / average_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi

def load_winning_patterns(filepath="winning_patterns.json"):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_winning_patterns(patterns, filepath="winning_patterns.json"):
    with open(filepath, "w") as file:
        json.dump(patterns, file, indent=4)

def update_winning_patterns(winning_patterns, pattern):
    if pattern in winning_patterns:
        winning_patterns[pattern] += 1
    else:
        winning_patterns[pattern] = 1

def get_most_frequent_patterns(winning_patterns, top_n=5):
    return dict(Counter(winning_patterns).most_common(top_n))

winning_patterns = load_winning_patterns()

def calculate_MACD(candles, short_period=12, long_period=26, signal_period=9):
    """Calcula o Moving Average Convergence Divergence (MACD)."""
    try:
        if not isinstance(candles, list) or len(candles) < long_period:
            return None, None, None # Dados insuficientes

        closes = np.array([c['close'] for c in candles])
        
        # Calcular EMAs
        ema_short = np.convolve(closes, np.ones(short_period)/short_period, mode='valid')
        # Ajuste para EMA (forma simplificada, pode usar pandas ewm para mais precisão)
        weights_short = np.exp(np.linspace(-1., 0., short_period))
        weights_short /= weights_short.sum()
        ema_short = np.convolve(closes, weights_short, mode='full')[:len(closes)]
        ema_short[:short_period] = ema_short[short_period]
        
        weights_long = np.exp(np.linspace(-1., 0., long_period))
        weights_long /= weights_long.sum()
        ema_long = np.convolve(closes, weights_long, mode='full')[:len(closes)]
        ema_long[:long_period] = ema_long[long_period]

        # Linha MACD
        macd_line = ema_short - ema_long

        # Linha de Sinal (EMA da linha MACD)
        weights_signal = np.exp(np.linspace(-1., 0., signal_period))
        weights_signal /= weights_signal.sum()
        signal_line = np.convolve(macd_line, weights_signal, mode='full')[:len(macd_line)]
        signal_line[:signal_period] = signal_line[signal_period]

        # Histograma MACD
        histogram = macd_line - signal_line

        # Retornar os últimos valores
        return macd_line[-1], signal_line[-1], histogram[-1]
    except Exception as e:
        print(f"Erro ao calcular MACD: {e}")
        return None, None, None

def calculate_bollinger_bands(candles, period=20, num_std_dev=2):
    closes = np.array([candle['close'] for candle in candles])
    sma = np.mean(closes[-period:])
    std_dev = np.std(closes[-period:])
    upper_band = sma + (num_std_dev * std_dev)
    lower_band = sma - (num_std_dev * std_dev)
    return upper_band, lower_band

def process_log_queue(page):
    pass

def start_strategy(page, user_session):
    # Imports locais das ESTRATÉGIAS de Profler2
    from Profler2 import (
        estrategia_PRO, estrategia_twin_towers, estrategia_PRO_m5,
        estrategia_QUARTA, estrategia_cinco_velas,
        estrategia_rsi_reversal, estrategia_origin_rsi_reversal, estrategia_pattern_trend,
        estrategia_macd_crossover
    )
    # Imports locais das FUNÇÕES AUXILIARES de Proflet5
    from Proflet5 import log_console, stop_bot, disable_buttons, enable_buttons 

    # Importar estratégias DEPOIS de validar a API
    try:
        from Profler2 import (
            estrategia_PRO, estrategia_twin_towers, estrategia_PRO_m5,
            estrategia_QUARTA, estrategia_cinco_velas,
            estrategia_macd_crossover, estrategia_rsi_reversal,
            estrategia_origin_rsi_reversal, estrategia_pattern_trend
        )
    except ImportError as e_import:
        log_console(page, f"Erro ao importar módulo de estratégias: {e_import}", "error")
        # Adicionar tratamento de erro se necessário, como parar o bot ou mostrar mensagem
        stop_bot(page)
        return
    
    print("[start_strategy] Iniciando...") # DEBUG
    # global stop, total_profit # Remover ou ajustar se usar state

    # Acessar API e verificar conexão (mantido)
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect():
        log_console(page, "Erro: API não conectada para iniciar estratégia.", level="error")
        page.snack_bar = ft.SnackBar(ft.Text("Conecte a API antes de iniciar o robô."), bgcolor=quantum_theme["error"])
        page.snack_bar.open = True
        page.update()
        return

    # Acessar estratégia selecionada (mantido)
    strategy_dropdown = page.ui.get('strategy_dropdown')
    if not strategy_dropdown:
        print("ERRO [start_strategy]: strategy_dropdown não encontrado em page.ui") # DEBUG
        return
    selected_strategy = strategy_dropdown.value
    print(f"[start_strategy] Estratégia selecionada: {selected_strategy}") # DEBUG

    strategy_function = None
    # Mapear valor do dropdown para a função CORRETAMENTE
    strategy_map = {
        "1": estrategia_PRO,
        "2": estrategia_twin_towers,
        "3": estrategia_PRO_m5,
        "4": estrategia_QUARTA,
        "5": estrategia_cinco_velas,
        "6": estrategia_macd_crossover,      # Corrigido ID 6
        "7": estrategia_rsi_reversal,        # Corrigido ID 7
        "8": estrategia_origin_rsi_reversal, # Corrigido ID 8
        "9": estrategia_pattern_trend        # Adicionado ID 9 (PRO SUPREMY)
    }
    strategy_function = strategy_map.get(selected_strategy)

    if strategy_function:
        print(f"[start_strategy] Função da estratégia encontrada: {strategy_function.__name__}") # DEBUG

        # --- DESABILITAR E ALTERAR FAB ---
        fab = None
        try:
            # Acessar o FAB da view atual (que deve ser /initial_screen)
            if page.views and page.views[-1].route == "/initial_screen":
                fab = page.views[-1].floating_action_button
            
            if fab and hasattr(fab, 'content') and isinstance(fab.content, ft.Container):
                fab.disabled = True
                # Mudar gradiente para indicar atividade/inatividade
                fab.content.gradient = ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[ft.colors.with_opacity(0.5, ft.colors.GREY_700), ft.colors.with_opacity(0.4, ft.colors.GREY_800)], # Gradiente cinza
                )
                fab.update()
                fab.content.update() # Atualizar o container interno também
                print("[start_strategy] FAB desabilitado e aparência alterada.") # DEBUG
            elif fab:
                # Se não for container, apenas desabilitar
                fab.disabled = True
                fab.update()
                print("[start_strategy] FAB desabilitado (sem mudança de aparência).") # DEBUG
            else:
                 print("[start_strategy] AVISO: FAB não encontrado na view atual para desabilitar.") # DEBUG
        except Exception as e_fab_disable:
            print(f"ERRO ao tentar desabilitar/alterar FAB: {e_fab_disable}")
        # --- FIM DESABILITAR E ALTERAR FAB ---

        # Reverter estado e botões (disable_buttons pode ser redundante agora, mas mantemos por segurança)
        state['stop'] = False # <--- Corrigido para False para iniciar
        disable_buttons(page) 
        # stop_flag = {'active': True} # Remover stop_flag daqui? Ou será criada no show_modal?

        # --- Atualizar Status Principal para Operando --- (mantido, mas pode ser ajustado)
        try:
            status_label_main = page.ui.get('status_label')
            if status_label_main:
                status_label_main.value = "🚀 Operando..." # Ou "Iniciando..."?
                status_label_main.color = quantum_theme["secondary"]
            else:
                print("AVISO [start_strategy]: status_label não encontrado em page.ui para atualizar status.")
            page.update() 
        except Exception as e_status:
             print(f"ERRO [start_strategy]: Falha ao atualizar status para Operando: {e_status}")
        # --------------------------------------------- #
        
        # --- RE-ADICIONAR CHAMADA AO MODAL INICIAL --- #
        print("[start_strategy] Chamando show_modal...") # DEBUG
        stop_flag = {'active': True} 
        try:
            # Chamar a função show_modal original do Profler2.py
            from Profler2 import show_modal # Garantir que está importando corretamente
            show_modal(
                page=page,
                message="O Robô está operando",
                asset=user_session.asset_var,
                direction="call",
                entry_value=user_session.entry_value_var,
                strategy_name=strategy_dropdown.options[int(selected_strategy)-1].text,
                user_session=user_session,
                quantum_theme=quantum_theme, # Passar o tema quantum
                stop_bot=stop_bot,
                ui_elements=page.ui, # Passar os elementos da UI
                state=state, # Passar o estado global
                stop_flag=stop_flag, # Passar a flag de parada
                currency=state.get('currency', 'R$') # Passar moeda do estado
            )
            print("Modal aberto com sucesso!")
        except Exception as e_modal:
            print(f"ERRO ao abrir modal: {e_modal}")
            import traceback
            traceback.print_exc() # Imprimir o traceback completo para diagnóstico
        print(f"[start_strategy] show_modal chamado. Iniciando thread para {strategy_function.__name__}...") # DEBUG

        # --- INICIAR A THREAD DA ESTRATÉGIA SELECIONADA ---
        global bot_thread # Manter referência global se necessário parar externamente
        
        # IMPORTANTE: Registrar um listener para capturar e encaminhar mensagens de log para o modal
        def forward_stats_to_modal():
            """Thread dedicada para enviar atualizações de estatísticas para o modal a cada segundo."""
            while not state.get('stop', True):
                try:
                    # --- MODIFICADO: Remover verificação page.window_destroyed --- 
                    if page and page.pubsub: # Apenas verificar se page e pubsub existem
                        # Enviar evento de atualização para o modal
                        page.pubsub.send_all("update_stats")
                        # print("Evento update_stats enviado para o modal") # DEBUG opcional
                    else:
                        print("AVISO: Página ou PubSub não disponível, parando thread forward_stats_to_modal.")
                        break # Sai do loop se a página ou pubsub não estiverem ativos
                    # ---------------------------------------------------------------
                except Exception as e_pubsub:
                    # Verificar se o erro é específico do loop fechado (mantido)
                    if "Event loop is closed" in str(e_pubsub):
                        print("AVISO: Event loop fechado detectado em forward_stats_to_modal. Parando thread.")
                        break # Sai do loop
                    else:
                        print(f"ERRO ao enviar estatísticas via pubsub: {e_pubsub}")
                time.sleep(1.0)  # Enviar a cada 1 segundo
                
        # Iniciar a thread de encaminhamento de estatísticas
        stats_thread = threading.Thread(target=forward_stats_to_modal, daemon=True)
        stats_thread.start()
        
        # Iniciar a thread principal da estratégia
        bot_thread = threading.Thread(
            target=strategy_function,
            args=(page, user_session), # Argumentos necessários para a função da estratégia
            daemon=True
        )
        bot_thread.start()
        log_console(page, f"Thread para {strategy_function.__name__} (Multi-Ativo) iniciada.", "info")
        
        # Definir um callback global para receber atualizações de ordens abertas
        def monitor_open_orders():
            """Thread para monitorar ordens abertas e atualizar stats."""
            last_profit = state.get('total_profit', 0.0)
            while not state.get('stop', True):
                try:
                    # Verificar se o lucro total mudou
                    current_profit = state.get('total_profit', 0.0)
                    if current_profit != last_profit:
                        print(f"Lucro total mudou: {last_profit} -> {current_profit}")
                        # Atualizar estatísticas via pubsub
                        if hasattr(page, 'pubsub'):
                            page.pubsub.send_all("update_stats")
                            print("Atualização forçada de stats enviada devido mudança no lucro")
                        last_profit = current_profit
                except Exception as e_monitor:
                    print(f"ERRO no monitor de ordens: {e_monitor}")
                time.sleep(0.5)  # Verificar a cada 0.5 segundo
                
        # Iniciar thread de monitoramento de ordens
        monitor_thread = threading.Thread(target=monitor_open_orders, daemon=True)
        monitor_thread.start()
        # -------------------------------------------------
    else:
        log_console(page, f"Erro: Estratégia selecionada ({selected_strategy}) não encontrada ou inválida.", "error")
        stop_bot(page) # Parar se a estratégia for inválida

def run_strategy_loop(page, strategy_function, user_session):
    from Profler1 import check_stop
    from Proflet5 import enable_buttons, log_console

    while not state.get('stop', True):
        try:
            strategy_function(page, user_session)
            if check_stop(page, user_session): break
        except Exception as e_loop:
            log_console(page, f"ERRO no loop da estratégia ({strategy_function.__name__}): {e_loop}", level="error")
            break
        time.sleep(1) # Pausa de 1 segundo entre as chamadas da estratégia

    # Código quando o loop parar
    log_console(page, f"Loop da estratégia {strategy_function.__name__} finalizado.", level="info")
    enable_buttons(page) # Usar enable_buttons importado
    status_label = page.ui.get('status_label')
    if status_label:
        status_label.value = "Parado"
        status_label.color = quantum_theme["error"]
    page.update()

def save_user_configurations(page, user_session):
    # Helper para conversão segura para float
    def safe_float(value, default=0.0):
        try:
            return float(value) if value else default
        except (ValueError, TypeError):
            return default
            
    # Helper para conversão segura para int
    def safe_int(value, default=0):
        try:
            return int(value) if value else default
        except (ValueError, TypeError):
            return default

    # Atualize os valores da sessão com os valores dos campos via page.ui
    # Adicionar verificações para cada page.ui.get pode ser mais robusto
    user_session.account_type_var = page.ui.get('account_type_dropdown').value
    # Usar safe_float e safe_int
    user_session.entry_value_var = safe_float(page.ui.get('entry_value_texttextfield').value, 5.0) # Default 5.0
    user_session.stop_win_var = safe_float(page.ui.get('stop_win_texttextfield').value, 50.0) # Default 50.0
    user_session.stop_loss_var = safe_float(page.ui.get('stop_loss_texttextfield').value, 50.0) # Default 50.0
    user_session.analyze_averages_var = page.ui.get('analyze_averages_checkbox').value
    user_session.average_candles_var = safe_int(page.ui.get('average_candles_texttextfield').value, 60) # Default 60
    user_session.use_martingale_var = page.ui.get('use_martingale_checkbox').value
    user_session.martingale_levels_var = safe_int(page.ui.get('martingale_levels_texttextfield').value, 2) # Default 2
    user_session.martingale_factor_var = safe_float(page.ui.get('martingale_factor_texttextfield').value, 2.0) # Default 2.0
    user_session.use_soros_var = page.ui.get('use_soros_checkbox').value
    user_session.soros_levels_var = safe_int(page.ui.get('soros_levels_texttextfield').value, 1) # Default 1
    # Verificar se asset_dropdown existe e tem valor antes de acessar .value
    asset_dropdown = page.ui.get('asset_dropdown')
    user_session.asset_var = asset_dropdown.value if asset_dropdown and asset_dropdown.value is not None else user_session.asset_var # Manter valor antigo se não houver seleção
    user_session.strategy_var = safe_int(page.ui.get('strategy_dropdown').value, 1) # Default 1
    user_session.start_time_var = page.ui.get('start_time_texttextfield').value or "00:00" # Default "00:00"
    user_session.end_time_var = page.ui.get('end_time_texttextfield').value or "23:59" # Default "23:59"
    user_session.use_schedule_var = page.ui.get('use_schedule_checkbox').value
    user_session.reentry_win_var = page.ui.get('reentry_win_checkbox').value
    user_session.use_ai_var = page.ui.get('use_ai_checkbox').value
    user_session.reverse_direction_var = page.ui.get('reverse_direction_checkbox').value
    user_session.use_stop_loss_var = page.ui.get('use_stop_loss_checkbox').value
    user_session.use_winning_patterns_var = page.ui.get('use_winning_patterns_checkbox').value
    # Salvar configurações RSI
    user_session.use_rsi_var = page.ui.get('use_rsi_checkbox').value
    user_session.periodo_rsi_var = safe_int(page.ui.get('periodo_rsi_textfield').value, 14) # Default 14
    # === SALVAR VALOR DO NOVO CHECKBOX ===
    analyze_all_pairs_checkbox = page.ui.get('analyze_all_pairs_checkbox')
    user_session.analyze_all_pairs_var = analyze_all_pairs_checkbox.value if analyze_all_pairs_checkbox else False
    # ====================================

    # Imprima os valores antes de salvar
    print("Valores a serem salvos no banco de dados (após validação):")
    print(f"account_type_var: {user_session.account_type_var}")
    print(f"entry_value_var: {user_session.entry_value_var}")
    print(f"stop_win_var: {user_session.stop_win_var}")
    print(f"stop_loss_var: {user_session.stop_loss_var}")
    print(f"analyze_averages_var: {user_session.analyze_averages_var}")
    print(f"average_candles_var: {user_session.average_candles_var}")
    print(f"use_martingale_var: {user_session.use_martingale_var}")
    print(f"martingale_levels_var: {user_session.martingale_levels_var}")
    print(f"martingale_factor_var: {user_session.martingale_factor_var}")
    print(f"use_soros_var: {user_session.use_soros_var}")
    print(f"soros_levels_var: {user_session.soros_levels_var}")
    print(f"asset_var: {user_session.asset_var}")
    print(f"strategy_var: {user_session.strategy_var}")
    print(f"start_time_var: {user_session.start_time_var}")
    print(f"end_time_var: {user_session.end_time_var}")
    print(f"use_schedule_var: {user_session.use_schedule_var}")
    print(f"reentry_win_var: {user_session.reentry_win_var}")
    print(f"use_ai_var: {user_session.use_ai_var}")
    print(f"reverse_direction_var: {user_session.reverse_direction_var}")
    print(f"use_stop_loss_var: {user_session.use_stop_loss_var}")
    print(f"use_winning_patterns_var: {user_session.use_winning_patterns_var}")
    # Imprimir valores RSI
    print(f"use_rsi_var: {user_session.use_rsi_var}")
    print(f"periodo_rsi_var: {user_session.periodo_rsi_var}")
    # === IMPRIMIR NOVO VALOR ===
    print(f"analyze_all_pairs_var: {user_session.analyze_all_pairs_var}")
    # ===========================

    # Salve as configurações no banco de dados
    user_session.save_configurations()

    page.snack_bar = ft.SnackBar(ft.Text("Configurações salvas"))
    page.snack_bar.open = True
    page.update()

    # Volte para a tela inicial
    show_initial_screen(page, user_session)

def show_login_screen(page: ft.Page):
    print("--- Executing show_login_screen ---") # DEBUG
    # Acessar elementos da UI via page.ui
    email_field = page.ui.get('email_textfield_login')
    password_field = page.ui.get('password_textfield_login')
    access_key_field = page.ui.get('access_key_texttextfield_login')

    # Verificar se os elementos existem
    if not all([email_field, password_field, access_key_field]):
        print("ERRO CRÍTICO: Campos de login não encontrados em page.ui!")
        page.add(ft.Text("Erro ao carregar a tela de login."))
        page.update()
        return
        
    # Configurar tema da página
    page.bgcolor = quantum_theme["background"]
    page.theme_mode = "dark"

    def on_login_click_internal(e):
        """Callback interno para o botão de login."""
        button = e.control # Obter o botão que foi clicado
        page = e.page     # Obter a página do evento

        # Guardar conteúdo original para restaurar em caso de falha
        original_button_content = button.content

        # Adicionar import de proflet aqui dentro
        from proflet import validate_online_login, get_user_session

        username = email_field.value
        password = password_field.value
        # Capturar valor da chave de acesso novamente
        access_key = access_key_field.value

        if not username or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário e Senha são obrigatórios."), bgcolor=quantum_theme["error"])
            page.snack_bar.open = True
            page.update()
            return

        # --- ATUALIZAR ESTADO DO BOTÃO --- 
        button.disabled = True
        # Usar a aparência do botão sólido
        button.content = ft.Container( 
             content=ft.Row([
                 ft.ProgressRing(width=16, height=16, stroke_width=2, color=quantum_theme["text"]),
                 ft.Text("ENTRANDO...", weight="bold", color=quantum_theme["text"])
             ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
             padding=ft.padding.symmetric(vertical=12, horizontal=15),
             width=250, # Manter largura
             height=50, # Manter altura
             alignment=ft.alignment.center,
             # Não precisa de gradiente aqui, mas manter tamanho/padding
        )
        # A cor de fundo já está no style do botão, não precisa redefinir aqui
        button.update() # Atualiza apenas o botão
        # --- FIM ATUALIZAR ESTADO DO BOTÃO ---

        loading = show_loading_overlay(page, "Validando credenciais...")

        # Função para rodar validação em thread
        def validate_in_thread():
            print("Thread: Iniciando validação online...") # DEBUG
            # Passar access_key vazio para a validação
            is_valid, error_message = validate_online_login(username, password, access_key)
            print(f"Thread: Resultado da validação: is_valid={is_valid}, message='{error_message}'") # DEBUG
            
            # Atualizar UI na thread principal
            def update_ui_after_validation():
                print("UI Thread: Iniciando update_ui_after_validation...") # DEBUG
                hide_loading_overlay(page, loading)
                print(f"UI Thread: is_valid = {is_valid}") # DEBUG
                if is_valid:
                    print("UI Thread: Login VÁLIDO. Obtendo sessão...") # DEBUG
                    user_session = get_user_session(username)
                    user_session.password = password # Considerar não armazenar senha
                    user_session.access_key = access_key # Salvar chave vazia (ou remover)
                    print("UI Thread: Carregando configurações...") # DEBUG
                    try:
                        user_session.load_configurations() # Carregar config após login
                        print("UI Thread: Configurações carregadas. Navegando para /initial_screen...") # DEBUG
                        # --- Persistir email no client storage ---
                        page.client_storage.set("user_email", username) # <--- Usar username
                        # ---------------------------------------

                        # Atualizar estado global
                        state['current_user_email'] = username # <--- Usar username
                        # state['API'] = API # <--- REMOVER esta linha (API é conectada separadamente)

                        # Limpar campos sensíveis após uso? (opcional)
                        # password_field.value = ""

                        # Ir para a tela inicial
                        log_console(page, f"Login bem-sucedido para {username}. Navegando...", "success") # <--- Usar username
                        show_initial_screen(page, user_session)
                    except Exception as e_load:
                        print(f"UI Thread: ERRO ao carregar configurações: {e_load}") # DEBUG
                        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao carregar configs: {e_load}"), bgcolor=quantum_theme["error"])
                        page.snack_bar.open = True
                    # --- REVERTER BOTÃO --- # Restaurar botão com o conteúdo ORIGINAL
                    button.disabled = False
                    button.content = original_button_content # Restaurar conteúdo original
                    button.update()
                    # --- FIM REVERTER BOTÃO --- 
                else:
                    print(f"UI Thread: Login INVÁLIDO. Motivo: {error_message}") # DEBUG
                    page.snack_bar = ft.SnackBar(ft.Text(error_message or "Falha no login."), bgcolor=quantum_theme["error"])
                    page.snack_bar.open = True
                    # --- REVERTER BOTÃO EM CASO DE FALHA --- 
                    button.disabled = False
                    button.content = original_button_content # Restaurar conteúdo original
                    button.update()
                    # --- FIM REVERTER BOTÃO --- 
                
                print("UI Thread: Finalizando update_ui_after_validation.") # DEBUG
                page.update()
            
            update_ui_after_validation() # Chamar diretamente

        # Iniciar validação em thread
        threading.Thread(target=validate_in_thread, daemon=True).start()

    # Botão de login - Definido dentro do layout da view abaixo
    # login_button = ... 

    # --- Definição da View de Login (Reestruturada) --- #
    login_view = ft.View(
        "/login",
        appbar=ft.AppBar( # Adicionar AppBar com botão voltar
            leading=ft.IconButton(
                icon=ft.icons.ARROW_BACK_IOS_NEW,
                icon_color=quantum_theme["text_secondary"],
                tooltip="Voltar",
                on_click=lambda _: show_choice_screen(page) # Voltar para tela de escolha
            ),
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0
        ),
        controls=[
            ft.Column([
                ft.Container(height=40), # Espaço superior reduzido
                ft.Text("Login", size=32, weight="bold", color=quantum_theme["text"]),
                ft.Container(height=5), 
                ft.Text("Continue com seu usuário e senha.", size=16, color=quantum_theme["text_secondary"]),
                ft.Container(height=40), # Espaço antes dos campos
                
                # Campos com Labels Externas
                ft.Text(" Usuário", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                email_field, # Usar instância da UI
                ft.Container(height=15),
                ft.Text(" Senha", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                password_field, # Usar instância da UI
                # Readicionar Campo Chave de Acesso
                ft.Container(height=15),
                ft.Text(" Chave de Acesso", size=14, color=quantum_theme["text_secondary"], weight="w500"),
                # Envolver TextField e botão Colar em uma Row
                ft.Row(
                    [
                        # Usar Container para permitir que o TextField expanda
                        ft.Container(content=access_key_field, expand=True),
                        ft.IconButton(
                            icon=ft.icons.CONTENT_PASTE_GO,
                            icon_color=quantum_theme["secondary"],
                            tooltip="Colar da área de transferência",
                            icon_size=20,
                            on_click=lambda _: (
                                setattr(access_key_field, 'value', _.page.get_clipboard() or ""), # Restaura page.get_clipboard()
                                _.page.update(access_key_field) # Atualiza o campo na UI
                            )
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER # Alinha o botão verticalmente com o campo
                ),
                
                ft.Container(height=40),
                                
                # Botão Entrar (estilo VaultCash)
                ft.ElevatedButton(
                     style=ft.ButtonStyle(
                         shape=ft.RoundedRectangleBorder(radius=15),
                         bgcolor=quantum_theme["primary"],
                         elevation=2,
                     ),
                     content=ft.Container(
                         # Conteúdo guardado em original_button_content no início do callback
                         content=ft.Row([
                             ft.Icon(ft.icons.LOGIN_ROUNDED, color=quantum_theme["text"]),
                             ft.Text("ENTRAR", weight="bold", color=quantum_theme["text"])
                         ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                         padding=ft.padding.symmetric(vertical=12, horizontal=15),
                         width=250,
                         height=50,
                         alignment=ft.alignment.center,
                     ),
                     on_click=on_login_click_internal # Callback interno
                 ),
                 ft.Container(height=20),
                 ft.TextButton("Esqueceu a senha?", disabled=True) # Link desabilitado por enquanto

            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            alignment=ft.MainAxisAlignment.START,
            spacing=5
            )
        ],
        padding=ft.padding.symmetric(horizontal=30, vertical=10) # Padding da página
    )
    # --- Fim da Definição da View de Login --- #

    # Limpar views existentes e adicionar a nova view de login
    page.views.clear()
    page.views.append(login_view)
    page.update()

def show_strategy_description_modal(page: ft.Page, strategy_id_str: str):
    """Exibe um modal com a descrição da estratégia selecionada."""
    print(f"DEBUG: show_strategy_description_modal chamada com ID: {strategy_id_str}")
    dlg = None # Definir dlg fora do try para usar no finally
    try:
        # Restaurar código original que busca a descrição
        strategy_id = int(strategy_id_str)
        strategy_info = estrategias_descricao.get(strategy_id)

        if not strategy_info:
            error_content = ft.Text(f"Descrição não encontrada para a estratégia selecionada (ID: {strategy_id}).", color=quantum_theme["text_secondary"])
            # Usar create_modal para consistência de estilo no erro
            dlg = create_modal("Erro", error_content, icon=ft.icons.ERROR_OUTLINE, page=page)
            print("DEBUG: Modal de erro (via create_modal) criado.")
        else:
            # Criar o conteúdo do modal com a descrição
            modal_content = ft.Column([
                 ft.Text(
                    strategy_info["nome"],
                    size=18, 
                    weight="bold", 
                    color=quantum_theme["secondary"]
                 ),
                 ft.Divider(height=1, color=quantum_theme["surface"]),
                 ft.Text(
                    strategy_info["descricao"],
                    size=14, 
                    color=quantum_theme["text"], 
                 ),
                 ft.Divider(height=1, color=quantum_theme["surface"]),
                 ft.Text(
                    "Importante: O robô analisa continuamente e só opera ao identificar padrões favoráveis.", 
                    size=12, 
                    color=quantum_theme["text_secondary"], 
                    italic=True
                 )
            ], spacing=10)
            # Usar create_modal para exibir a descrição
            dlg = create_modal(
                "Descrição da Estratégia", 
                modal_content, 
                icon=ft.icons.INFO_OUTLINE,
                page=page
            )
            print("DEBUG: Modal de descrição (via create_modal) criado.")

        # === Abordagem do Exemplo: Adicionar ao Overlay ANTES ===
        if dlg: # Verificar se o diálogo foi criado
            if hasattr(page, 'overlay'):
                 # Limpar overlay anterior pode ajudar (opcional, mas seguro)
                 # page.overlay.clear() 
                 page.overlay.append(dlg)
                 print("DEBUG: Diálogo adicionado ao page.overlay.")
            else:
                 print("ERRO: page.overlay não existe!")
                 return # Não continuar se não puder adicionar ao overlay
            
            # Manter atribuição a page.dialog (padrão Flet)
            page.dialog = dlg
            
            # Definir open = True
            dlg.open = True
            
            print("DEBUG: Tentando abrir diálogo via overlay + page.dialog.")
            page.update()
            print("DEBUG: page.update() chamado após tentar abrir diálogo.")
        else:
             print("ERRO: Falha ao criar o diálogo (dlg é None).")
        # =======================================================

    except ValueError:
        print(f"ERRO: ID de estratégia inválido ao converter para int: {strategy_id_str}")
        log_console(page, f"ID de estratégia inválido: {strategy_id_str}", level="error")
        # Poderia mostrar um modal de erro aqui também
    except Exception as e:
        print(f"ERRO GERAL em show_strategy_description_modal: {e}")
        import traceback
        traceback.print_exc()
        log_console(page, f"Erro ao mostrar descrição da estratégia: {e}", level="error")

# Função auxiliar para fechar o modal (ajustada para remover do overlay)
def close_modal(page):
    # Fecha o diálogo atribuído a page.dialog
    if page and page.dialog:
        current_dialog = page.dialog
        current_dialog.open = False
        page.dialog = None # Desatribuir de page.dialog
        print("DEBUG: page.dialog fechado e desatribuído.")
        # Remove o diálogo específico do overlay se ele estiver lá
        if hasattr(page, 'overlay') and current_dialog in page.overlay:
            page.overlay.remove(current_dialog)
            print("DEBUG: Diálogo removido do page.overlay.")
        page.update() # Atualizar após fechar e remover
    else:
        print("DEBUG: Nenhum diálogo ativo para fechar.")

def update_main_screen_real_time(stop_flag, state, page, user_session):
    import time
    print("[update_main_screen_real_time] Thread iniciada.")
    initial_view_route = "/initial_screen" # Rota da tela que esta thread atualiza

    # Aguarda até todos os labels estarem prontos e adicionados à página
    while stop_flag['active']:
        # Verificar se a view atual é a tela inicial ANTES de buscar labels
        # Isso evita erros se a página mudar antes dos labels serem encontrados
        current_route = page.views[-1].route if page.views else None
        if current_route != initial_view_route:
            print(f"[update_main_screen_real_time] View mudou ({current_route}), parando thread.")
            stop_flag['active'] = False
            break 
            
        win_label = page.ui.get('win_label')
        loss_label = page.ui.get('loss_label')
        total_profit_label = page.ui.get('total_profit_label')
        balance_label = page.ui.get('balance_label')
        
        # Verificar se os labels existem E estão na página correta
        labels_exist = all([win_label, loss_label, total_profit_label, balance_label])
        labels_on_page = all([getattr(lbl, 'page', None) for lbl in [win_label, loss_label, total_profit_label, balance_label]])

        if labels_exist and labels_on_page:
            print("DEBUG LABELS:", win_label, loss_label, total_profit_label, balance_label)
            print("DEBUG LABELS .page:", getattr(win_label, 'page', None), getattr(loss_label, 'page', None), getattr(total_profit_label, 'page', None), getattr(balance_label, 'page', None))
            break # Sai do loop de espera se tudo estiver OK
            
        print("[update_main_screen_real_time] Aguardando labels serem adicionados à página correta...")
        time.sleep(0.2) # Aumentar um pouco a pausa

    prev_win = prev_loss = prev_profit = prev_balance = None
    force_update_counter = 0
    
    while stop_flag['active']:
        # Verificar se a view ainda é a tela inicial a cada ciclo
        current_route = page.views[-1].route if page.views else None
        if current_route != initial_view_route:
            print(f"[update_main_screen_real_time] View mudou ({current_route}), parando thread.")
            stop_flag['active'] = False
            break
            
        print(f"[update_main_screen_real_time] Loop - stop_flag: {stop_flag['active']}")
        try:
            # Labels já garantidos pelo loop acima
            # Rebuscar os labels caso a página tenha sido recriada (embora a verificação de rota deva impedir isso)
            win_label = page.ui.get('win_label') 
            loss_label = page.ui.get('loss_label')
            total_profit_label = page.ui.get('total_profit_label')
            balance_label = page.ui.get('balance_label')

            # Segurança extra: verificar se labels ainda existem na página
            if not all(getattr(lbl, 'page', None) for lbl in [win_label, loss_label, total_profit_label, balance_label]):
                print("[update_main_screen_real_time] Labels não estão mais na página, parando thread.")
                stop_flag['active'] = False
                break

            current_wins = state.get('win_count', 0)
            current_losses = state.get('loss_count', 0)
            current_profit = state.get('total_profit', 0.0)
            current_balance = state.get('account_balance', user_session.account_balance)
            current_currency = state.get('currency', user_session.currency)

            print(f"[update_main_screen_real_time] Estado lido: W:{current_wins} L:{current_losses} P:{current_profit:.2f} B:{current_balance:.2f}")

            force_update_counter += 1
            force_update = (force_update_counter >= 5)

            if win_label and (prev_win != current_wins or force_update):
                print(f"[update_main_screen_real_time] Atualizando win_label: {prev_win} -> {current_wins}")
                win_label.value = f"Vitórias: {current_wins}"
                win_label.update()
                prev_win = current_wins

            if loss_label and (prev_loss != current_losses or force_update):
                print(f"[update_main_screen_real_time] Atualizando loss_label: {prev_loss} -> {current_losses}")
                loss_label.value = f"Derrotas: {current_losses}"
                loss_label.update()
                prev_loss = current_losses

            if total_profit_label and (prev_profit != current_profit or force_update):
                print(f"[update_main_screen_real_time] Atualizando total_profit_label: {prev_profit} -> {current_profit}")
                total_profit_label.value = f"Lucro Total: {current_currency} {current_profit:.2f}"
                total_profit_label.color = quantum_theme["success"] if current_profit >= 0 else quantum_theme["error"]
                total_profit_label.update()
                prev_profit = current_profit

            if balance_label and (prev_balance != current_balance or force_update):
                print(f"[update_main_screen_real_time] Atualizando balance_label: {prev_balance} -> {current_balance}")
                balance_label.value = f"Saldo: {current_currency} {current_balance:.2f}"
                balance_label.update()
                prev_balance = current_balance

            if force_update:
                force_update_counter = 0

            page.update()
        except Exception as e:
            print(f"[update_main_screen_real_time] Erro: {e}")
            # Considerar parar a thread em caso de erro repetido?
        time.sleep(0.5)
        
    print("[update_main_screen_real_time] Thread finalizada.") # Log quando a thread realmente termina

def calculate_SMA(candles, period):
    """Calcula a Média Móvel Simples (SMA)."""
    try:
        if not isinstance(candles, list) or len(candles) < period:
            return None # Dados insuficientes
        closes = np.array([c['close'] for c in candles[-period:]])
        return np.mean(closes)
    except Exception as e:
        print(f"Erro ao calcular SMA: {e}")
        return None

def calculate_ATR(candles, period=14):
    """Calcula o Average True Range (ATR). Requer high, low, close."""
    try:
        if not isinstance(candles, list) or len(candles) < period + 1:
            return None # Dados insuficientes
            
        highs = np.array([c['max'] for c in candles]) # Usar 'max' conforme API
        lows = np.array([c['min'] for c in candles]) # Usar 'min' conforme API
        closes = np.array([c['close'] for c in candles])
        
        tr = np.maximum(highs[1:] - lows[1:], 
                      np.maximum(np.abs(highs[1:] - closes[:-1]), 
                                 np.abs(lows[1:] - closes[:-1])))
        
        # Usar SMA para ATR como simplificação (ideal seria EMA)
        atr = calculate_SMA(tr.tolist(), period) # Requer TR como lista de floats
        # Correção: calculate_SMA espera lista de dicionários, adaptar
        # Criar lista de dicionários "falsos" para SMA
        tr_dicts = [{'close': x} for x in tr]
        atr = calculate_SMA(tr_dicts[-period:], period)
        
        return atr
    except KeyError as e:
         print(f"Erro ao calcular ATR: Chave ausente nos dados da vela ({e}). Certifique-se que 'max', 'min', 'close' existem.")
         return None
    except Exception as e:
        print(f"Erro geral ao calcular ATR: {e}")
        return None

def highest(candles, period):
    """Encontra o valor mais alto (high) no período."""
    try:
        if not isinstance(candles, list) or len(candles) < period:
            return None
        return max(c['max'] for c in candles[-period:])
    except KeyError:
         print(f"Erro ao calcular highest: Chave 'max' ausente.")
         return None
    except Exception as e:
        print(f"Erro ao calcular highest: {e}")
        return None

def lowest(candles, period):
    """Encontra o valor mais baixo (low) no período."""
    try:
        if not isinstance(candles, list) or len(candles) < period:
            return None
        return min(c['min'] for c in candles[-period:])
    except KeyError:
        print(f"Erro ao calcular lowest: Chave 'min' ausente.")
        return None
    except Exception as e:
        print(f"Erro ao calcular lowest: {e}")
        return None

def calculate_EMA(candles, period):
    """Calcula a Média Móvel Exponencial (EMA) de forma simplificada."""
    try:
        if not isinstance(candles, list) or len(candles) < period:
            return None # Dados insuficientes
        closes = np.array([c['close'] for c in candles])
        # Usar pandas ewm seria mais preciso, mas para simplificar:
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        ema = np.convolve(closes, weights, mode='full')[:len(closes)]
        ema[:period] = ema[period] # Preencher valores iniciais
        return ema[-1] # Retornar o último valor EMA
    except Exception as e:
        print(f"Erro ao calcular EMA: {e}")
        return None
