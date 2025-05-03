import flet as ft
import base64
import threading
import time
import json
import logging
from Proflet5 import quantum_theme, state
from Proflet5 import log_console, enable_buttons, stop_bot

# Assumindo que API é importado ou passado como argumento
# from Proflet4 import API  # Exemplo, depende de onde API é gerenciado
# Assumindo que os controles UI são importados
# from Proflet5 import progress_ring, timer_text, result_label, win_label, loss_label, balance_label, total_profit_label
# Assumindo que stop_bot é importado
# from Profler2 import stop_bot

# Variáveis para cache de pares (Movidas de proflet.py)
pares_cache = {}
ultimo_update_pares = 0
cache_timeout = 300  # 5 minutos

# Adicionar no início do arquivo, após os imports
_api_cache = {
    'all_open_time': None,
    'all_open_time_timestamp': 0,
    'profit': None,
    'profit_timestamp': 0
}

def get_cached_all_open_time(API):
    """Obtém all_open_time com cache para evitar atrasos de API."""
    global _api_cache
    current_time = time.time()
    
    # Se o cache for válido (menos de 60 segundos), retorne-o
    if _api_cache['all_open_time'] and current_time - _api_cache['all_open_time_timestamp'] < 60:
        logging.debug("Usando cache para all_open_time")
        return _api_cache['all_open_time']
    
    # Se não tiver cache ou estiver expirado, busque novos dados
    try:
        all_asset = API.get_all_open_time()
        if all_asset and isinstance(all_asset, dict):
            _api_cache['all_open_time'] = all_asset
            _api_cache['all_open_time_timestamp'] = current_time
            return all_asset
        else:
            logging.error("API retornou dados inválidos para all_open_time")
            # Se tiver cache expirado, use-o como fallback
            if _api_cache['all_open_time']:
                logging.warning("Usando cache expirado como fallback")
                return _api_cache['all_open_time']
            return {'binary': {}, 'turbo': {}, 'digital': {}}
    except Exception as e:
        logging.error(f"Erro ao obter all_open_time: {str(e)}")
        # Se tiver cache expirado, use-o como fallback
        if _api_cache['all_open_time']:
            logging.warning("Usando cache expirado como fallback após erro")
            return _api_cache['all_open_time']
        return {'binary': {}, 'turbo': {}, 'digital': {}}

def get_cached_profit(API):
    """Obtém all_profit com cache para evitar atrasos de API."""
    global _api_cache
    current_time = time.time()
    
    # Se o cache for válido (menos de 60 segundos), retorne-o
    if _api_cache['profit'] and current_time - _api_cache['profit_timestamp'] < 60:
        logging.debug("Usando cache para profit")
        return _api_cache['profit']
    
    # Se não tiver cache ou estiver expirado, busque novos dados
    try:
        profit = API.get_all_profit()
        if profit and isinstance(profit, dict):
            _api_cache['profit'] = profit
            _api_cache['profit_timestamp'] = current_time
            return profit
        else:
            logging.error("API retornou dados inválidos para profit")
            # Se tiver cache expirado, use-o como fallback
            if _api_cache['profit']:
                logging.warning("Usando cache expirado como fallback")
                return _api_cache['profit']
            return {}
    except Exception as e:
        logging.error(f"Erro ao obter profit: {str(e)}")
        # Se tiver cache expirado, use-o como fallback
        if _api_cache['profit']:
            logging.warning("Usando cache expirado como fallback após erro")
            return _api_cache['profit']
        return {}

def get_pares_disponiveis(API):
    """Busca os pares digitais disponíveis, priorizando e categorizando como em bot.py."""
    pares_disponiveis = {}
    try:
        if not API or not API.check_connect():
            logging.error("API não conectada para buscar pares!")
            return {}

        # Lista de ativos prioritários (copiada de bot.py, ajustar se necessário)
        ativos_prioritarios = [
            "EURUSD", "EURUSD-OTC", 
            "GBPUSD", "GBPUSD-OTC", 
            "USDJPY", "USDJPY-OTC",
            "EURJPY", "EURJPY-OTC", 
            "AUDUSD", "AUDUSD-OTC", 
            "USDCAD", "USDCAD-OTC", 
            "USDCHF", "USDCHF-OTC", 
            "EURGBP", "EURGBP-OTC", 
            "GBPJPY", "GBPJPY-OTC", 
            "AUDCAD", "AUDCAD-OTC"
        ]
        # Adicionar versões -OTC e -op (se aplicável à sua corretora via API)
        ativos_prioritarios_completos = []
        for par in ativos_prioritarios:
             ativos_prioritarios_completos.append(par)
             ativos_prioritarios_completos.append(par + "-OTC")
             # ativos_prioritarios_completos.append(par + "-op") # Descomentar se -op for relevante

        # Obter todos os ativos digitais abertos
        all_digital_assets = get_cached_all_open_time(API).get('digital', {})
        if not all_digital_assets:
             logging.debug("Nenhum ativo digital encontrado ou retornado pela API.")
             return {}

        logging.debug("--- Iniciando busca de payouts individuais ---")
        # Processar ativos prioritários primeiro
        pares_processados = set()
        for ativo_nome in ativos_prioritarios_completos:
            if ativo_nome in all_digital_assets and all_digital_assets[ativo_nome].get('open', False):
                try:
                    payout = API.get_digital_payout(ativo_nome)
                    logging.debug(f"DEBUG [get_pares_disponiveis]: Ativo: {ativo_nome}, Payout retornado: {payout}")
                    # Filtrar apenas ativos com payout digital > 0
                    if payout and payout > 0:
                        categoria = "outros"
                        if "-OTC" in ativo_nome: categoria = "otc"
                        # Adapte a lista de populares conforme necessário
                        elif ativo_nome in ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "USDCHF", "EURGBP", "GBPJPY", "AUDCAD"]: categoria = "populares"
                        
                        pares_disponiveis[ativo_nome] = {
                            'nome': ativo_nome,
                            'payout': payout,
                            'categoria': categoria
                        }
                        pares_processados.add(ativo_nome)
                except Exception as e_payout:
                    logging.warning(f"AVISO [get_pares_disponiveis]: Não foi possível obter payout para {ativo_nome}: {e_payout}")
                    continue
        
        # Processar os demais ativos abertos
        for ativo_nome, info in all_digital_assets.items():
            if ativo_nome not in pares_processados and info.get('open', False):
                 try:
                    payout = API.get_digital_payout(ativo_nome)
                    logging.debug(f"DEBUG [get_pares_disponiveis]: Ativo: {ativo_nome}, Payout retornado: {payout}")
                    # Filtrar apenas ativos com payout digital > 0
                    if payout and payout > 0:
                        categoria = "outros"
                        if "-OTC" in ativo_nome: categoria = "otc"
                        elif ativo_nome in ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "USDCHF", "EURGBP", "GBPJPY", "AUDCAD"]: categoria = "populares"
                        
                        pares_disponiveis[ativo_nome] = {
                            'nome': ativo_nome,
                            'payout': payout,
                            'categoria': categoria
                        }
                 except Exception as e_payout:
                     logging.warning(f"AVISO [get_pares_disponiveis]: Não foi possível obter payout para {ativo_nome}: {e_payout}")
                     continue

        logging.debug("--- Fim da busca de payouts individuais ---")
        # Ordenar: Populares primeiro, depois OTC, depois Outros. Dentro de cada categoria, maior payout primeiro.
        def sort_key(item):
            nome, info = item
            categoria = info['categoria']
            payout = info['payout']
            if categoria == 'populares': return (0, -payout) # 0 para populares
            if categoria == 'otc': return (1, -payout)       # 1 para otc
            return (2, -payout)                              # 2 para outros

        pares_ordenados = dict(sorted(pares_disponiveis.items(), key=sort_key))

        logging.debug(f"Total de pares digitais com payout encontrados e ordenados: {len(pares_ordenados)}")
        return pares_ordenados

    except Exception as e:
        logging.error(f"Erro GERAL ao buscar pares disponíveis: {str(e)}")
        import traceback
        traceback.print_exc() # Imprime o traceback completo para depuração
        return {}

def update_balance_and_profit(page, user_session, balance_label, total_profit_label):
    """Atualiza os labels de saldo e lucro total."""
    if balance_label and total_profit_label:
        balance_label.value = f"Saldo: {user_session.currency} {user_session.account_balance:.2f}"
        total_profit_label.value = f"Lucro Total: {user_session.currency} {user_session.total_profit:.2f}"
    else:
        logging.warning("Erro: Labels de saldo/lucro não encontrados para atualização.")

def payout(API, pair):
    """Calcula os payouts para binário, turbo e digital."""
    # Verifica se API está conectado antes de usar
    if not API or not API.check_connect():
        logging.error("API não conectada para verificar payout.")
        return 0, 0, 0

    # Inicializar valores padrão
    binary = 0
    turbo = 0
    digital = 0

    # Usar abordagem simples como no bot.py original
    try:
        # Obter profit e assets usando cache
        profit = get_cached_profit(API)
        all_asset = get_cached_all_open_time(API)
        
        # Verificar binário sem timeouts extras
        try:
            if 'binary' in all_asset and pair in all_asset['binary'] and all_asset['binary'][pair].get('open', False):
                if pair in profit and 'binary' in profit[pair] and profit[pair]['binary'] > 0:
                    binary = round(profit[pair]['binary'], 2) * 100
        except Exception as e_binary:
            logging.debug(f"Erro ao calcular payout binário para {pair}: {str(e_binary)}")

        # Verificar turbo sem timeouts extras
        try:
            if 'turbo' in all_asset and pair in all_asset['turbo'] and all_asset['turbo'][pair].get('open', False):
                if pair in profit and 'turbo' in profit[pair] and profit[pair]['turbo'] > 0:
                    turbo = round(profit[pair]['turbo'], 2) * 100
        except Exception as e_turbo:
            logging.debug(f"Erro ao calcular payout turbo para {pair}: {str(e_turbo)}")

        # Verificar digital sem timeouts extras
        try:
            if 'digital' in all_asset and pair in all_asset['digital'] and all_asset['digital'][pair].get('open', False):
                # Verificar se já temos cache do payout digital específico
                # Isso poderia ser estendido com um sistema de cache mais complexo
                digital = API.get_digital_payout(pair)
        except Exception as e_digital:
            logging.debug(f"Erro ao calcular payout digital para {pair}: {str(e_digital)}")
    
    except Exception as e_general:
        logging.error(f"Erro geral ao calcular payouts para {pair}: {str(e_general)}")
    
    return binary, turbo, digital

def load_image_base64(file_path):
    """Carrega uma imagem e retorna em base64."""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def get_pares_disponiveis_cached(API):
    """Versão com cache que agora chama get_digital_assets_only."""
    global pares_cache, ultimo_update_pares
    
    agora = time.time()
    
    # Se o cache ainda é válido, retornar
    if (agora - ultimo_update_pares) < cache_timeout and pares_cache:
        logging.debug("DEBUG: Retornando pares digitais do cache.")
        return pares_cache
    
    # Atualizar cache chamando a nova função
    logging.debug("DEBUG: Cache de pares digitais expirado ou vazio. Buscando novos...")
    pares_cache = get_digital_assets_only(API)
    ultimo_update_pares = agora
    return pares_cache

def get_digital_assets_only(API):
    """Busca apenas os pares digitais disponíveis e seus payouts."""
    digital_assets_payouts = {}
    try:
        if not API or not API.check_connect():
            logging.error("API não conectada para buscar pares digitais!")
            return {}

        # Abordagem usando o cache
        all_digital_assets = get_cached_all_open_time(API).get('digital', {})
            
        if not all_digital_assets:
             logging.warning("Nenhum ativo digital encontrado ou retornado pela API.")
             return {}

        logging.debug("--- Iniciando busca de payouts APENAS para Digitais --- ")
        for ativo_nome, info in all_digital_assets.items():
            if info and isinstance(info, dict) and info.get('open', False):
                 try:
                    # Chamada direta sem timeout
                    payout = API.get_digital_payout(ativo_nome)
                    logging.debug(f"DEBUG [get_digital_assets_only]: Ativo: {ativo_nome}, Payout retornado: {payout}")
                    # Garantir que apenas ativos com payout > 0 sejam incluídos
                    if payout and payout > 0:
                        digital_assets_payouts[ativo_nome] = payout
                 except Exception as e_payout:
                     logging.warning(f"AVISO [get_digital_assets_only]: Não foi possível obter payout para {ativo_nome}: {e_payout}")
                     continue
        
        logging.debug(f"--- Fim da busca de payouts Digitais. Encontrados: {len(digital_assets_payouts)} ---")
        # Ordenar pelo payout (maior primeiro)
        pares_ordenados = dict(sorted(digital_assets_payouts.items(), key=lambda item: item[1], reverse=True))
        return pares_ordenados

    except Exception as e:
        logging.error(f"Erro GERAL ao buscar pares digitais: {str(e)}")
        import traceback
        traceback.print_exc() 
        return {}

def purchase(page, asset, entry_value, direction, exp, type, use_soros, soros_levels, martingale_levels, martingale_factor, reentry, user_session):
    # Obter api_instance de state
    api_instance = state.get('API')

    # Verificação da API
    if not api_instance or not api_instance.check_connect():
        log_console(page, "Erro: API não está conectada para realizar a compra.", level="error")
        return False

    # Variáveis locais para esta operação
    soros_level = state.get('soros_level', 0)
    soros_value = state.get('soros_value', 0)
    current_op_profit = 0
    consecutive_losses = state.get('consecutive_losses', 0)

    if use_soros and soros_level == 0:
        entry = entry_value
    elif use_soros and soros_level >= 1 and soros_value > 0 and soros_level <= soros_levels:
        entry = entry_value + soros_value
    else:
        entry = entry_value

    for i in range(martingale_levels + 1):
        # Verificar se o robô está parado
        if state.get('stop', True):
            log_console(page, "Compra cancelada, robô parado.", level="info")
            break

        # --- Adicionado: Atualizar state e sinalizar início da operação ---
        expiration_seconds = exp * 60
        state['current_operation_expiration_seconds'] = expiration_seconds
        state['current_operation_start_time'] = time.time() # Armazena o tempo de início
        state['current_operation_direction'] = direction
        state['current_operation_entry_value'] = entry
        state['operation_in_progress'] = True
        print(f"[Purchase] State atualizado para iniciar operação: direction={direction}, entry={entry}, exp_sec={expiration_seconds}") # Debug Log
        # Enviar sinal para o modal
        if hasattr(page, 'pubsub'):
            page.pubsub.send_all("new_operation_started")
            print("PubSub: Evento 'new_operation_started' enviado.") # Debug
        else:
            print("AVISO [purchase]: page.pubsub não disponível para sinalizar nova operação.")
        # ----------------------------------------------------------------

        # Realizar a compra
        if type == 'digital':
            check, id = api_instance.buy_digital_spot_v2(asset, entry, direction, exp)
        else:
            check, id = api_instance.buy(entry, asset, direction, exp)

        if check:
            log_console(page, f"Ordem aberta: Par: {asset} Timeframe: {exp} Entrada: {entry}", level="info")
            
            # Inicializar result para evitar erros
            result = None
            status = False
            
            # Loop de verificação SEM limite de tentativas (como em bot.py)
            while True: # Alterado de loop com max_retries
                try:
                    # Pausa ligeiramente maior, similar ao bot.py
                    time.sleep(0.5) 

                    if type == 'digital':
                        status, result = api_instance.check_win_digital_v2(id)
                    else:
                        status, result = api_instance.check_win_v4(id)
                    
                    # Registrar o status e resultado para depuração
                    logging.debug(f"check_win para ID {id}: status={status}, result={result}")
                    
                    if status:
                        # --- Adicionado: Sinalizar fim da operação no state ---
                        state['operation_in_progress'] = False
                        print(f"State: operation_in_progress definido como False para ID {id}") # Debug
                        # -------------------------------------------------------
                        break  # Saímos do loop se obtivemos status True
                    
                    # Não precisamos mais incrementar retry_count ou verificar max_retries
                    # A verificação de stop do robô pode ser feita aqui se necessário,
                    # mas a lógica atual já verifica antes de entrar no loop de martingale.
                    if state.get('stop', False):
                         log_console(page, f"Verificação de resultado interrompida (robô parado) para ID: {id}", level="info")
                         # --- Adicionado: Sinalizar fim da operação no state (mesmo se parado) ---
                         state['operation_in_progress'] = False
                         print(f"State: operation_in_progress definido como False (robô parado) para ID {id}") # Debug
                         # ------------------------------------------------------------------------
                         break # Sai do loop de verificação se o robô parou

                except Exception as e:
                    # Logar o erro mas continuar tentando
                    log_console(page, f"Erro ao verificar resultado (tentativa continuará): {str(e)}", level="error")
                    logging.error(f"Exception em check_win (ID: {id}): {str(e)}")
                    # Pausa extra em caso de erro para não sobrecarregar
                    time.sleep(1)

            # Se saiu do loop porque o robô parou, status pode ser False
            if not status and state.get('stop', False):
                 log_console(page, f"Não foi possível obter resultado final para ID {id} (robô parado).", level="warn")
                 # O estado 'operation_in_progress' já foi definido como False acima

            # Apenas processamos o resultado se status for True e result não for None
            elif status and result is not None:
                # O estado 'operation_in_progress' já foi definido como False acima
                # Atualizar lucro total
                state['total_profit'] = state.get('total_profit', 0.0) + round(result, 2)
                
                # --- SINALIZAR RESULTADO NO STATE --- 
                if result > 0:
                    state['last_operation_result'] = 'WIN'
                    log_console(page, f"Resultado final para ID {id}: WIN ({result:.2f})", level="win")
                elif result < 0:
                    state['last_operation_result'] = 'LOSS'
                    log_console(page, f"Resultado final para ID {id}: LOSS ({result:.2f})", level="loss")
                else:
                    state['last_operation_result'] = 'TIE'
                    log_console(page, f"Resultado final para ID {id}: EMPATE (0.00)", level="info")
                # ------------------------------------
                
                if use_soros:
                    soros_value += round(result, 2)
                current_op_profit += round(result, 2)

                if result > 0:  # WIN
                    state['win_count'] = state.get('win_count', 0) + 1
                    consecutive_losses = 0  # Reinicia perdas consecutivas
                    log_console(page, f"WIN! Lucro: {result} Par: {asset} Lucro Total: {state['total_profit']}", level="win")
                    
                    # --- ADICIONADO: Notificação de WIN --- 
                    if page:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINED, color=quantum_theme["success"]), 
                                    ft.Text(f"WIN! +{state.get('currency', '$')}{result:.2f}", color=quantum_theme["text"], weight="bold")
                                ]), 
                                padding=10, border_radius=10, 
                                bgcolor=ft.Colors.with_opacity(0.8, quantum_theme["success"])
                            ),
                            bgcolor=ft.Colors.TRANSPARENT, 
                            duration=2000 # Mostrar por 2 segundos
                        )
                        page.snack_bar.open = True
                        # A atualização da página será feita pelo pubsub ou pela próxima ação
                    # --- FIM Notificação de WIN --- 
                    
                    if page and hasattr(page, 'pubsub'):
                        page.pubsub.send_all("update_stats")
                    
                    # Lógica de reentrada após WIN
                    if reentry and user_session.reentry_win_var:
                        log_console(page, "Reentrada após WIN iniciada...", level="info")
                        # Chama purchase recursivamente. O state será atualizado novamente no início da próxima chamada.
                        purchase(page, asset, entry_value, direction, exp, type, use_soros, soros_levels, martingale_levels, martingale_factor, False, user_session)
                
                elif result == 0:  # EMPATE
                    log_console(page, f"EMPATE! Lucro: {result} Par: {asset} Lucro Total: {state['total_profit']}", level="draw")
                    
                    if page and hasattr(page, 'pubsub'):
                        page.pubsub.send_all("update_stats")
                    
                    # Se empatar no Martingale, mantém o valor da entrada atual
                    if user_session.use_martingale_var and i + 1 <= martingale_levels:
                        entry = round(abs(entry), 2)  # Mantém o valor
                    else:
                        break  # Sai do loop de martingale se não usar martingale
                
                else:  # LOSS
                    state['loss_count'] = state.get('loss_count', 0) + 1
                    consecutive_losses += 1
                    log_console(page, f"LOSS! Lucro: {result} Par: {asset} Lucro Total: {state['total_profit']}", level="loss")
                    
                    # --- ADICIONADO: Notificação de LOSS --- 
                    if page:
                        page.snack_bar = ft.SnackBar(
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.icons.ERROR_OUTLINE, color=quantum_theme["error"]), 
                                    # result já é negativo, então mostramos diretamente
                                    ft.Text(f"LOSS! {state.get('currency', '$')}{result:.2f}", color=quantum_theme["text"], weight="bold") 
                                ]), 
                                padding=10, border_radius=10, 
                                bgcolor=ft.Colors.with_opacity(0.8, quantum_theme["error"]) # Usar cor de erro
                            ),
                            bgcolor=ft.Colors.TRANSPARENT, 
                            duration=2000 # Mostrar por 2 segundos
                        )
                        page.snack_bar.open = True
                        # A atualização da página será feita pelo pubsub ou pela próxima ação
                    # --- FIM Notificação de LOSS --- 
                    
                    if page and hasattr(page, 'pubsub'):
                        page.pubsub.send_all("update_stats")

                    # Inversão de direção (se configurado)
                    if user_session.reverse_direction_var:
                        direction = 'call' if direction == 'put' else 'put'
                        log_console(page, f"Direção invertida para {direction} após LOSS.", level="warn")

                    # Martingale (se configurado e dentro do limite)
                    if user_session.use_martingale_var and i + 1 <= martingale_levels:
                        entry = round(entry * martingale_factor, 2)
                        log_console(page, f"Martingale Nível {i+1}. Novo valor: {entry}", level="info")
                        # O state será atualizado no início da próxima iteração do loop for
                    else:
                        log_console(page, "Martingale não aplicado ou limite atingido.", level="info")
                        break  # Sai do loop de martingale

                # Verificar condições de stop
                if check_stop(page, user_session):
                    log_console(page, "Stop atingido dentro do loop de compra.", level="info")
                    # --- Adicionado: Garantir que operation_in_progress é False se der stop ---
                    state['operation_in_progress'] = False
                    # ---------------------------------------------------------------------
                    break
                
                # Se chegou até aqui e foi WIN ou EMPATE (sem martingale), sair do loop de martingale
                if result >= 0 and not (result == 0 and user_session.use_martingale_var and i + 1 <= martingale_levels):
                    break
                
            else:  # Se falhou em verificar o resultado (e não foi por stop)
                log_console(page, f"Falha ao verificar resultado da ordem ID: {id}", level="error")
                 # --- Adicionado: Garantir que operation_in_progress é False se falhar a verificação ---
                state['operation_in_progress'] = False
                 # ----------------------------------------------------------------------------------
                break  # Sai do loop de martingale
                
        else:  # Se falhou em abrir a ordem
            log_console(page, f"Erro ao abrir ordem: {id} {asset}", level="error")
             # --- Adicionado: Garantir que operation_in_progress é False se falhar a abertura ---
            state['operation_in_progress'] = False
             # ------------------------------------------------------------------------------
            break  # Sai do loop de martingale

    # Atualizar estado do Soros/Perdas no final da sequência
    if use_soros:
        if current_op_profit > 0:
            state['soros_level'] = soros_level + 1
            state['soros_value'] = soros_value  # Salva o valor acumulado
        else:
            state['soros_level'] = 0
            state['soros_value'] = 0
    else:
        state['soros_level'] = 0
        state['soros_value'] = 0

    state['consecutive_losses'] = consecutive_losses  # Salva contagem de perdas

    if hasattr(page, 'pubsub'):
        try:
            # Forçar atualização de toda a interface
            page.pubsub.send_all("update_stats")
            print("Evento update_stats enviado após operação")
        except Exception as e_pubsub:
            print(f"Erro ao enviar evento pubsub: {e_pubsub}")

    return True  # Indica que a operação (ou sequência de martingale) foi concluída

def check_stop(page, user_session):
    # Importar dependências
    from Proflet5 import enable_buttons, stop_bot
    
    total_profit = state.get('total_profit', 0.0)

    if user_session.use_stop_loss_var and total_profit <= -abs(user_session.stop_loss_var):
        stop_bot(page)
        log_console(page, f"STOP LOSS ATINGIDO! Lucro Total: {total_profit}", level="loss")
        return True

    if user_session.use_stop_win_var and total_profit >= abs(user_session.stop_win_var):
        stop_bot(page)
        log_console(page, f"STOP WIN ATINGIDO! Lucro Total: {total_profit}", level="win")
        return True

    return False

