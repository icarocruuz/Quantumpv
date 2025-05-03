import flet as ft
import time
import threading
from datetime import datetime
from Proflet5 import quantum_theme, UserSession, state
import numpy as np
from collections import Counter
import json
from Profler1 import purchase, payout, check_stop, get_digital_assets_only
from Proflet5 import log_console, _create_log_control
import traceback

# Imports de outros módulos do projeto (Exemplos)
# from catalogador import catag # Precisa existir
# from Profler1 import averages, show_modal, update_balance_and_profit # averages está aqui agora
# from Proflet4 import API, winning_patterns # API e estado
# from Proflet5 import UserSession, quantum_theme, ui_elements, state # Classes, config, UI, estado

def time_filter(user_session):
    """Verifica se a hora atual está dentro do período agendado."""
    if not user_session.use_schedule_var:
        return True
    now = datetime.now().time()
    start_time = datetime.strptime(user_session.start_time_var, '%H:%M').time()
    end_time = datetime.strptime(user_session.end_time_var, '%H:%M').time()
    return start_time <= now <= end_time

def averages(candles, average_candles_count):
    """Calcula a média das velas.
    Adaptado de 'medias' em bot.py.
    """
    if not candles or len(candles) < average_candles_count:
        return None # Não há velas suficientes
        
    total = 0
    # Usar as últimas 'average_candles_count' velas
    relevant_candles = candles[-average_candles_count:]
    for i in relevant_candles:
        total += i['close']
    average = total / average_candles_count

    # Determina tendência baseada na média vs última vela
    if average > candles[-1]['close']:
        trend = 'put'
    else:
        trend = 'call'

    return trend

def calcular_RSI(candles, period=14):
    """
    Calcula o Índice de Força Relativa (RSI)
    Portado de bot.py.
    Retorna: valor do RSI (0-100)
    """
    try:
        if not isinstance(candles, list) or len(candles) < period + 1:
            return 50  # Valor neutro se não houver dados suficientes
        
        if not all(isinstance(vela, dict) and 'close' in vela for vela in candles):
            return 50  
        
        closes = [vela['close'] for vela in candles] # Apenas preços de fechamento
        deltas = np.diff(closes)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up / down if down != 0 else 0 # Evitar divisão por zero
        rsi = np.zeros_like(closes)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(closes)):
            delta = deltas[i-1] 
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
        
        return rsi[-1] # Retorna o último valor RSI calculado

    except Exception as e:
        return 50 

def analisar_padrao_candlestick(page, vela, vela_anterior):
    """Analisa padrões de candlestick. Adaptado de bot.py.
    Retorna (direcao, nome_padrao) ou (None, '')
    """
    # Não chama mais log_console aqui para evitar poluição, a estratégia principal loga
    corpo = abs(vela['close'] - vela['open'])
    sombra_superior = vela['max'] - max(vela['open'], vela['close'])
    sombra_inferior = min(vela['open'], vela['close']) - vela['min']
    tendencia_anterior = 'alta' if vela_anterior['close'] > vela_anterior['open'] else 'baixa'
    
    # Reversão de Alta (Shooting Star / Gravestone Doji similar)
    if sombra_superior > corpo * 1.5 and tendencia_anterior == 'alta':
        # log_console(page, "⭐ Reversão de Alta identificada")
        return ('put', '⭐ Reversão de Alta')

    # Estrela Cadente (Confirmação mais forte de Reversão de Alta)
    if sombra_superior > corpo * 1.5 and sombra_inferior < corpo * 0.5 and tendencia_anterior == 'alta':
        # log_console(page, "⭐ Estrela Cadente identificada")
        return ('put', '⭐ Estrela Cadente')

    # Martelo (Hammer / Dragonfly Doji similar)
    if sombra_inferior > corpo * 1.5 and tendencia_anterior == 'baixa':
        # log_console(page, "🔨 Reversão de Baixa identificada")
        return ('call', '🔨 Reversão de Baixa')

    # Martelo Invertido (Confirmação mais forte de Reversão de Baixa)
    if sombra_inferior > corpo * 1.5 and sombra_superior < corpo * 0.5 and tendencia_anterior == 'baixa':
        # log_console(page, "🔨 Martelo Invertido identificado")
        return ('call', '🔨 Martelo Invertido')

    # Continuação de Alta (Marubozu de Alta / Vela de Força)
    # Condição simplificada: corpo grande, sombra superior pequena
    if vela['open'] < vela['close'] and corpo > 0 and sombra_superior < corpo * 0.3: # Corpo significativo e sombra pequena
        # log_console(page, "🟢 Continuação de Alta identificada")
        return ('call', '🟢 Continuação de Alta')

    # Continuação de Baixa (Marubozu de Baixa / Vela de Força)
    # Condição simplificada: corpo grande, sombra inferior pequena
    if vela['open'] > vela['close'] and corpo > 0 and sombra_inferior < corpo * 0.3: # Corpo significativo e sombra pequena
        # log_console(page, "🔴 Continuação de Baixa identificada")
        return ('put', '🔴 Continuação de Baixa')

    return (None, '')

def verificar_ativo_operacional(page, api_instance, ativo_atual, user_session):
    """
    Verifica se o ativo selecionado está operacional e recomenda alternativas se necessário.
    Retorna uma tupla (operacional, ativo_recomendado, mensagem)
    """
    if not api_instance or not api_instance.check_connect():
        log_console(page, "API não está conectada para verificar ativo", "error")
        return False, None, "API não conectada"
    
    # Verificar payout do ativo atual
    try:
        binary_p, turbo_p, digital_p = payout(api_instance, ativo_atual)
        
        # Verificar se o ativo tem payout digital (opções digitais disponíveis)
        if digital_p <= 0:
            log_console(page, f"⚠️ ATENÇÃO: {ativo_atual} sem payout digital ou fechado (payout = {digital_p})", "warning")
            
            # Obter alternativas com payout digital positivo
            ativos_disponiveis = get_digital_assets_only(api_instance)
            
            if not ativos_disponiveis:
                return False, None, "Nenhum ativo digital disponível no momento"
            
            # Ordenar pelo payout (maior primeiro)
            ativos_ordenados = sorted(ativos_disponiveis.items(), key=lambda x: x[1], reverse=True)
            
            # Verificar se há alternativas do mesmo tipo (OTC ou não)
            alternativas_mesmo_tipo = []
            alternativas_gerais = []
            
            for nome, payout_valor in ativos_ordenados:
                # Guardar 5 melhores alternativas gerais
                if len(alternativas_gerais) < 5:
                    alternativas_gerais.append((nome, payout_valor))
                
                # Verificar se é do mesmo tipo (OTC ou não)
                if ("-OTC" in ativo_atual and "-OTC" in nome) or ("-OTC" not in ativo_atual and "-OTC" not in nome):
                    if len(alternativas_mesmo_tipo) < 3:
                        alternativas_mesmo_tipo.append((nome, payout_valor))
            
            # Preparar lista de recomendações
            if alternativas_mesmo_tipo:
                recomendacoes = alternativas_mesmo_tipo
                tipo_msg = "do mesmo tipo"
            else:
                recomendacoes = alternativas_gerais
                tipo_msg = "disponíveis"
            
            # Formatar mensagem de recomendação
            recomendacoes_str = ", ".join([f"{nome} ({payout:.1f}%)" for nome, payout in recomendacoes])
            mensagem = f"{ativo_atual} não está disponível para operações digitais. Alternativas {tipo_msg}: {recomendacoes_str}"
            
            # Retornar o primeiro ativo recomendado
            ativo_recomendado = recomendacoes[0][0] if recomendacoes else None
            
            return False, ativo_recomendado, mensagem
        
        # O ativo está operacional
        log_console(page, f"✅ {ativo_atual} verificado e operacional (payout = {digital_p:.1f}%)", "info")
        return True, ativo_atual, f"Ativo operacional com payout {digital_p:.1f}%"
        
    except Exception as e:
        log_console(page, f"❌ Erro ao verificar ativo {ativo_atual}: {str(e)}", "error")
        return False, None, f"Erro ao verificar ativo: {str(e)}"

def estrategia_PRO(page, user_session: UserSession):
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): 
        log_console(page, "API não conectada. Tentando reconectar...", "error")
        return

    # Obter todos os ativos digitais disponíveis com payout
    ativos_disponiveis = get_digital_assets_only(api_instance)
    if not ativos_disponiveis:
        log_console(page, "Nenhum ativo digital disponível no momento (Estratégia PRO)", "error")
        return
    
    # === AJUSTE MULTI-PAR -> SEMPRE ANALISAR OS 5 MELHORES ===
    # Ordenar os ativos pelo payout e pegar os 5 melhores
    melhores_ativos = sorted(ativos_disponiveis.items(), key=lambda x: x[1], reverse=True)[:5]

    if not melhores_ativos:
        log_console(page, "Nenhum ativo com payout positivo encontrado após filtragem (Estratégia PRO)", "error")
        return

    target_ativos = melhores_ativos
    log_console(page, f"Analisando os {len(target_ativos)} melhores ativos digitais (Estratégia PRO - Top 5 Payouts).", "info")
    # A lógica anterior de if user_session.analyze_all_pairs_var foi removida
    # ==========================================================
    
    # Verificar hora de entrada para a estratégia PRO
    try:
        timestamp = api_instance.get_server_timestamp()
        minutes = float(datetime.fromtimestamp(timestamp).strftime('%M.%S')[1:])
        enter = (minutes >= 4.58 and minutes <= 5.00) or \
                (minutes >= 9.58 and minutes <= 10.00) or \
                (minutes >= 14.58 and minutes <= 15.00) or \
                (minutes >= 19.58 and minutes <= 20.00) or \
                (minutes >= 24.58 and minutes <= 25.00) or \
                (minutes >= 29.58 and minutes <= 30.00) or \
                (minutes >= 34.58 and minutes <= 35.00) or \
                (minutes >= 39.58 and minutes <= 40.00) or \
                (minutes >= 44.58 and minutes <= 45.00) or \
                (minutes >= 49.58 and minutes <= 50.00) or \
                (minutes >= 54.58 and minutes <= 55.00) or \
                (minutes >= 59.58)

        if enter and time_filter(user_session):
            # === MODIFICADO: Loop sobre target_ativos ===
            for ativo, payout in target_ativos:
                # --- Adicionado: Verificação de parada no início do loop do ativo ---
                if state.get('stop', False):
                    log_console(page, "Parada solicitada durante análise de ativos (Estratégia PRO)", "info")
                    return # Sai da função se o stop foi solicitado
                # -----------------------------------------------------------------
                try:
                    # Verificar se o ativo ainda está operacional
                    operacional, _, _ = verificar_ativo_operacional(page, api_instance, ativo, user_session)
                    if not operacional:
                        log_console(page, f"Ativo {ativo} não está operacional, pulando...", "warning")
                        continue
                    
                    log_console(page, f"Analisando ativo {ativo} com payout {payout:.1f}%", "info")
                    
                    option_type = 'digital'  # Sempre digital pois estamos usando get_digital_assets_only
                    
                    # Buscar as velas para análise
                    direction = None
                    timeframe = 60
                    qnt_velas = 3
                    if user_session.analyze_averages_var == 'S':
                        qnt_velas = max(qnt_velas, user_session.average_candles_var)
                    if user_session.use_rsi_var:
                        qnt_velas = max(qnt_velas, user_session.periodo_rsi_var + 1)

                    candles = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)

                    if not candles or len(candles) < 3:
                        log_console(page, f"Dados insuficientes para {ativo}, pulando...", "warning")
                        continue

                    # Analisar padrão de cores
                    try:
                        cores = []
                        for v in candles[-3:]:
                            if v['open'] < v['close']: cores.append('Green')
                            elif v['open'] > v['close']: cores.append('Red')
                            else: cores.append('Doji')
                    except (IndexError, KeyError, TypeError) as e_candle_err:
                        log_console(page, f"Erro ao analisar velas para {ativo}: {e_candle_err}", "error")
                        continue

                    if cores.count('Doji') == 0:
                        if cores.count('Green') > cores.count('Red'):
                            direction = 'put'
                        elif cores.count('Red') > cores.count('Green'):
                            direction = 'call'
                    else:
                        direction = None

                    # Aplicar filtro de médias se configurado
                    trend = None
                    if direction and user_session.analyze_averages_var == 'S':
                        if len(candles) >= user_session.average_candles_var:
                            trend = averages(candles, user_session.average_candles_var)
                            if trend and direction != trend:
                                log_console(page, f"Direção {direction} conflita com tendência {trend}, cancelando entrada para {ativo}", "info")
                                direction = None

                    # Aplicar filtro RSI se configurado
                    if direction and user_session.use_rsi_var:
                        try:
                            rsi_valor = calcular_RSI(candles, user_session.periodo_rsi_var)
                            log_console(page, f"📊 RSI({user_session.periodo_rsi_var}) para {ativo}: {rsi_valor:.2f}", "info")

                            # Verificar condições de sobrecompra/sobrevenda
                            if direction == 'call' and rsi_valor >= 70:
                                log_console(page, f"⚠️ Entrada CALL cancelada para {ativo}. RSI {rsi_valor:.2f} indica sobrecompra (>=70).", "warn")
                                direction = None
                            elif direction == 'put' and rsi_valor <= 30:
                                log_console(page, f"⚠️ Entrada PUT cancelada para {ativo}. RSI {rsi_valor:.2f} indica sobrevenda (<=30).", "warn")
                                direction = None
                        except Exception as e_rsi:
                            log_console(page, f"Erro ao calcular RSI para {ativo}: {e_rsi}", "error")

                    # Se temos uma direção válida, realizar a entrada
                    if direction:
                        log_console(page, f"➡️ Entrada {direction.upper()} em {ativo} (Payout: {payout:.1f}%)", "info")
                        
                        # Atualizar o ativo atual na sessão do usuário (para que fique registrado)
                        user_session.asset_var = ativo
                        
                        # Enviar ordem de compra
                        purchase(page, ativo, user_session.entry_value_var, direction, 1, option_type,
                                 user_session.use_soros_var, user_session.soros_levels_var,
                                 user_session.martingale_levels_var, user_session.martingale_factor_var,
                                 user_session.reentry_win_var, user_session)
                        
                        # Verificar se atingiu stop após esta operação
                        if state.get('stop', False):
                            log_console(page, "Stop atingido, interrompendo análise de ativos (Estratégia PRO)", "warning")
                            return # Sai da função inteira
                        
                        # --- Adicionado: Interromper loop de ativos após a primeira entrada bem sucedida neste ciclo ---
                        log_console(page, f"Entrada realizada em {ativo}. Interrompendo análise de outros ativos neste ciclo.", "info")
                        break # Sai do loop 'for ativo in ...'
                        # -----------------------------------------------------------------------------------------------
                
                except Exception as e_ativo:
                    log_console(page, f"Erro ao processar {ativo} (Estratégia PRO): {e_ativo}", "error")
                    continue  # Continua para o próximo ativo no loop
                # === FIM DA MODIFICAÇÃO DO LOOP ===
                # Adicionar pequena pausa entre análises de ativos
                time.sleep(0.1) 

    except Exception as e:
        log_console(page, f"Erro geral na estrategia_PRO: {e}", "error")
        traceback.print_exc()

def estrategia_twin_towers(page, user_session: UserSession):
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): return

    option_type = 'digital'
    try:
        binary_p, turbo_p, digital_p = payout(api_instance, user_session.asset_var)
        if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
        elif max(binary_p, turbo_p) > 0: option_type = 'binary'
        else: return
    except Exception as e_payout: return

    try:
        timestamp = api_instance.get_server_timestamp()
        minutes = float(datetime.fromtimestamp(timestamp).strftime('%M.%S')[1:])
        enter = (minutes >= 3.58 and minutes <= 4.00) or (minutes >= 8.58 and minutes <= 9.00)

        if enter and time_filter(user_session):
            direction = None
            timeframe = 60
            qnt_velas = 4
            if user_session.analyze_averages_var == 'S':
                qnt_velas = max(qnt_velas, user_session.average_candles_var)

            candles = api_instance.get_candles(user_session.asset_var, timeframe, qnt_velas, timestamp)

            if not candles or len(candles) < 4:
                return

            try:
                vela_analise = candles[-4]
                cor_vela4 = 'Green' if vela_analise['open'] < vela_analise['close'] else 'Red' if vela_analise['open'] > vela_analise['close'] else 'Doji'
            except (IndexError, KeyError, TypeError) as e_candle_err:
                return

            if cor_vela4 == 'Green':
                direction = 'call'
            elif cor_vela4 == 'Red':
                direction = 'put'
            else:
                direction = None

            trend = None
            if direction and user_session.analyze_averages_var == 'S':
                if len(candles) >= user_session.average_candles_var:
                    trend = averages(candles, user_session.average_candles_var)
                    if trend and direction != trend: direction = None

            if direction:
                log_console(page, f"➡️ Entrada {direction.upper()} (TwinTowers)", "info")
                purchase(page, user_session.asset_var, user_session.entry_value_var, direction, 1, option_type,
                         user_session.use_soros_var, user_session.soros_levels_var,
                         user_session.martingale_levels_var, user_session.martingale_factor_var,
                         user_session.reentry_win_var, user_session)

    except Exception as e:
        log_console(page, f"Erro na estrategia_twin_towers: {e}", "error")

def estrategia_PRO_m5(page, user_session: UserSession):
    api_instance = state.get('API')
    # A verificação inicial da API pode ficar fora do loop principal
    if not api_instance or not api_instance.check_connect():
        log_console(page, "API não conectada. Tentando reconectar...", "error")
        time.sleep(5)  # Esperar 5 segundos antes de retornar
        return  # Retorna para tentar novamente no próximo ciclo

    # Verificar se o ativo selecionado está operacional
    ativo_atual = user_session.asset_var
    operacional, ativo_recomendado, mensagem = verificar_ativo_operacional(page, api_instance, ativo_atual, user_session)
    
    if not operacional:
        # Exibir mensagem de erro e recomendação
        log_console(page, mensagem, "warning")
        
        # Se temos um ativo recomendado, perguntar ao usuário se deseja usar
        if ativo_recomendado:
            # No ambiente Flet, precisamos mostrar um diálogo para o usuário escolher
            # Como não podemos interromper o fluxo aqui, vamos apenas recomendar no log
            log_console(page, f"Recomendação: Use {ativo_recomendado} em vez de {ativo_atual}", "info")
            
            # Alternativamente, poderíamos trocar automaticamente
            # user_session.asset_var = ativo_recomendado
            # log_console(page, f"Ativo alterado automaticamente para {ativo_recomendado}", "info")
            
            # Para esta implementação, vamos apenas alertar sem trocar
            # O usuário precisará mudar manualmente
        
        # Verificar se devemos continuar mesmo assim (para depuração ou se usuário deseja)
        # Na implementação atual, vamos continuar, mas alertando sobre possíveis falhas
        log_console(page, "Continuando a operação, mas podem ocorrer falhas nas entradas", "warning")
    
    log_console(page, "Iniciando loop da estratégia PRO M5...", "info")
    
    # Definir contadores para tentativas
    consecutive_api_errors = 0
    max_consecutive_errors = 3

    while not state.get('stop', False): # Loop principal da estratégia - Modificado para verificar stop=False
        # --- Adicionado: Verificação de parada no início do loop while ---
        # if state.get('stop', False): # Esta verificação já está na condição do while
        #     log_console(page, "Parada solicitada (Estratégia PRO M5)", "info")
        #     break # Sai do loop while
        # ----------------------------------------------------------------
        try:
            # Verificar conexão dentro do loop é uma boa prática
            if not api_instance.check_connect():
                 log_console(page, "API desconectada durante execução (PRO M5). Tentando reconectar...", "warn")
                 consecutive_api_errors += 1
                 if consecutive_api_errors > max_consecutive_errors:
                     log_console(page, f"Falha após {max_consecutive_errors} tentativas consecutivas. Esperando 60 segundos...", "error")
                     time.sleep(60)  # Pausa longa após muitas falhas
                     consecutive_api_errors = 0  # Resetar contador
                 else:
                     time.sleep(5)  # Pausa curta entre tentativas
                 continue  # Pula para a próxima iteração

            option_type = 'digital'
            try:
                binary_p, turbo_p, digital_p = payout(api_instance, user_session.asset_var)
                if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
                elif max(binary_p, turbo_p) > 0: option_type = 'binary'
                else: 
                    log_console(page, f"Par {user_session.asset_var} fechado ou sem payout (PRO M5). Aguardando...", "warn")
                    time.sleep(30)  # Espera 30 segundos se o par estiver fechado
                    continue
            except Exception as e_payout:
                log_console(page, f"Erro ao obter payout (PRO M5): {e_payout}. Tentando novamente...", "error")
                consecutive_api_errors += 1
                time.sleep(5)
                continue

            # Resetar contador de erros API se chegou aqui com sucesso
            consecutive_api_errors = 0
            
            # Obter timestamp - abordagem direta como no bot.py
            try:
                timestamp = api_instance.get_server_timestamp()
                if not timestamp:
                    log_console(page, "Timestamp inválido. Tentando novamente...", "error")
                    time.sleep(3)
                    continue
            except Exception as e:
                log_console(page, f"Erro ao obter timestamp: {str(e)}. Tentando novamente...", "error")
                time.sleep(3)
                continue
                
            dt_object = datetime.fromtimestamp(timestamp)
            minutes = int(dt_object.strftime('%M'))
            seconds = int(dt_object.strftime('%S'))
            # Condição de entrada original
            enter = (minutes % 5 == 4) and (seconds >= 58)

            if enter and time_filter(user_session):
                log_console(page, f"Condição de entrada PRO M5 atendida ({minutes}:{seconds}). Analisando velas...", "info") # Log quando a condição é atendida
                direction = None
                timeframe = 300 # 5 minutos
                qnt_velas = 3 # Velas para análise MHI
                
                # Ajustar quantidade de velas se médias ou RSI estiverem ativados
                if user_session.analyze_averages_var == 'S':
                    qnt_velas = max(qnt_velas, user_session.average_candles_var)
                if user_session.use_rsi_var:
                     qnt_velas = max(qnt_velas, user_session.periodo_rsi_var + 1) # RSI precisa de período + 1

                # Obter velas - abordagem direta como no bot.py
                try:
                    candles = api_instance.get_candles(user_session.asset_var, timeframe, qnt_velas, timestamp)
                except Exception as e:
                    log_console(page, f"Erro ao obter velas: {str(e)}", "error")
                    time.sleep(2)
                    continue

                if not candles or len(candles) < 3:
                    log_console(page, "Não foi possível obter velas suficientes para análise (PRO M5).", "warn")
                    time.sleep(1) # Pequena pausa antes de tentar de novo
                    continue # Pula para próxima iteração do loop

                try:
                    cores = []
                    # Analisar as últimas 3 velas de M5
                    for v in candles[-3:]:
                        if not all(key in v for key in ['open', 'close']):
                            raise KeyError(f"Dados incompletos na vela: {v}")
                        if v['open'] < v['close']: cores.append('Green')
                        elif v['open'] > v['close']: cores.append('Red')
                        else: cores.append('Doji')
                except (IndexError, KeyError, TypeError) as e_candle_err:
                    log_console(page, f"Erro ao analisar cores das velas (PRO M5): {e_candle_err}", "error")
                    time.sleep(1)
                    continue

                # Lógica MHI (Maioria de 3 velas)
                if cores.count('Doji') == 0:
                    if cores.count('Green') > cores.count('Red'):
                        direction = 'put' # Minoria
                    elif cores.count('Red') > cores.count('Green'):
                        direction = 'call' # Minoria
                else:
                    direction = None # Não opera se houver Doji

                # Filtro de Média Móvel (se ativado)
                trend = None
                if direction and user_session.analyze_averages_var == 'S':
                    if len(candles) >= user_session.average_candles_var:
                        trend = averages(candles, user_session.average_candles_var)
                        if trend and direction != trend:
                            log_console(page, f"Entrada {direction.upper()} (PRO M5) cancelada. Contra tendência da média ({trend.upper()}).", "warn")
                            direction = None
                    else:
                        log_console(page, "Velas insuficientes para cálculo da média móvel (PRO M5).", "warn")
                        # Decide-se não cancelar a entrada se a média não puder ser calculada
                
                # Filtro RSI (se ativado) - Adicionado como no bot.py
                if direction and user_session.use_rsi_var:
                    try:
                        rsi_valor = calcular_RSI(candles, user_session.periodo_rsi_var)
                        log_console(page, f"📊 RSI({user_session.periodo_rsi_var}) calculado: {rsi_valor:.2f}", "info")
                        if direction == 'call' and rsi_valor >= 70:
                             log_console(page, f"⚠️ Entrada CALL (PRO M5) cancelada. RSI {rsi_valor:.2f} indica sobrecompra (>=70).", "warn")
                             direction = None
                        elif direction == 'put' and rsi_valor <= 30:
                             log_console(page, f"⚠️ Entrada PUT (PRO M5) cancelada. RSI {rsi_valor:.2f} indica sobrevenda (<=30).", "warn")
                             direction = None
                    except Exception as e_rsi:
                         log_console(page, f"Erro ao calcular ou aplicar filtro RSI (PRO M5): {e_rsi}", "error")
                         # Considerar cancelar a entrada se RSI falhar? direction = None

                # Executar a compra se a direção for válida
                if direction:
                    log_console(page, f"➡️ Entrada {direction.upper()} (PRO M5) identificada. Executando compra...", "info")
                    purchase(page, user_session.asset_var, user_session.entry_value_var, direction, 1, option_type,
                             user_session.use_soros_var, user_session.soros_levels_var,
                             user_session.martingale_levels_var, user_session.martingale_factor_var,
                             user_session.reentry_win_var, user_session)
                    # Após a compra, talvez esperar um pouco mais para não tentar entrar no mesmo segundo
                    time.sleep(5) 
                # else: # Log opcional se não entrou
                    # log_console(page, "Nenhuma entrada válida encontrada nesta verificação (PRO M5).", "info")
            
            # else: # Log opcional quando a condição de tempo não é atendida
                # print(f"DEBUG: Condição de tempo não atendida ({minutes}:{seconds})")

        except Exception as e:
            log_console(page, f"Erro inesperado no loop da estrategia_PRO_m5: {e}", "error")
            traceback.print_exc() # Imprime traceback para depuração
            consecutive_api_errors += 1
            time.sleep(5) # Pausa maior em caso de erro inesperado

        # Pausa curta no final de cada ciclo do loop para evitar uso excessivo de CPU/API
        time.sleep(0.2)

    log_console(page, "Loop da estratégia PRO M5 finalizado (stop solicitado).", "info")

def estrategia_QUARTA(page, user_session: UserSession):
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): return

    option_type = 'digital'
    try:
        binary_p, turbo_p, digital_p = payout(api_instance, user_session.asset_var)
        if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
        elif max(binary_p, turbo_p) > 0: option_type = 'binary'
        else: return
    except Exception as e_payout: return

    try:
        timestamp = api_instance.get_server_timestamp()
        minutes = float(datetime.fromtimestamp(timestamp).strftime('%M.%S'))
        enter = (minutes >= 4.58 and minutes <= 5.00) or \
                 (minutes >= 9.58 and minutes <= 10.00) or \
                 (minutes >= 14.58 and minutes <= 15.00) or \
                 (minutes >= 19.58 and minutes <= 20.00) or \
                 (minutes >= 24.58 and minutes <= 25.00) or \
                 (minutes >= 29.58 and minutes <= 30.00) or \
                 (minutes >= 34.58 and minutes <= 35.00) or \
                 (minutes >= 39.58 and minutes <= 40.00) or \
                 (minutes >= 44.58 and minutes <= 45.00) or \
                 (minutes >= 49.58 and minutes <= 50.00) or \
                 (minutes >= 54.58 and minutes <= 55.00) or \
                 (minutes >= 59.58)

        if enter and time_filter(user_session):
            direction = None
            timeframe = 60
            num_candles = 3

            candles_raw = api_instance.get_candles(user_session.asset_var, timeframe, num_candles, timestamp)

            if not candles_raw or len(candles_raw) < 3:
                return

            try:
                cores = []
                cores_str_list = []
                for v in candles_raw[-3:]:
                    if v['open'] < v['close']: cores.append('g'); cores_str_list.append('g')
                    elif v['open'] > v['close']: cores.append('r'); cores_str_list.append('r')
                    else: cores.append('d'); cores_str_list.append('d')
                cores_str = "".join(cores_str_list)
            except (IndexError, KeyError, TypeError) as e_candle_err:
                return

            if cores.count('d') == 0:
                if cores.count('g') > cores.count('r'):
                    direction = 'call'
                elif cores.count('r') > cores.count('g'):
                    direction = 'put'
            else:
                direction = None

            if direction:
                log_console(page, f"➡️ Entrada {direction.upper()} (QUARTA)", "info")
                purchase(page, user_session.asset_var, user_session.entry_value_var, direction, 1, option_type,
                         user_session.use_soros_var, user_session.soros_levels_var,
                         user_session.martingale_levels_var, user_session.martingale_factor_var,
                         user_session.reentry_win_var, user_session)

    except Exception as e:
        log_console(page, f"Erro na estrategia_QUARTA: {e}", "error")

def estrategia_cinco_velas(page: ft.Page, user_session: UserSession):
    """Estratégia 5 Velas - ADICIONADO loop interno e lógica Multi-Ativos restaurada."""
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect():
        log_console(page, "API não conectada (5 Velas)", "error")
        return

    log_console(page, f"Iniciando loop interno da Estratégia Cinco Velas.", "info")

    valor_entrada = user_session.entry_value_var
    timeframe = 60
    qnt_velas = 6
    option_type = 'digital' # Default

    while not state.get('stop', True): # <<<< LOOP INTERNO
        try:
            # Verificar conexão e API a cada ciclo
            if not api_instance.check_connect():
                log_console(page, "API desconectada durante loop (5 Velas)", "error")
                state['stop'] = True # Forçar parada
                break

            # === Definir ativos para analisar DENTRO do loop ===
            ativos_para_analisar = []
            if user_session.analyze_all_pairs_var:
                # log_console(page, "Modo Multi-Ativo (5 Velas): Buscando Top 5...", "debug") # Log opcional
                try:
                    ativos_disponiveis = get_digital_assets_only(api_instance)
                    if ativos_disponiveis:
                        melhores_ativos = sorted(ativos_disponiveis.items(), key=lambda x: x[1], reverse=True)[:5]
                        ativos_para_analisar = [ativo for ativo, _ in melhores_ativos]
                        # log_console(page, f"Analisando Top 5 (5 Velas): {ativos_para_analisar}", "debug") # Log opcional
                    else:
                        log_console(page, "Nenhum ativo digital disponível (5 Velas Multi).", "warn")
                        # Espera um pouco antes de tentar buscar ativos novamente
                        time.sleep(10)
                        continue # Pula para o próximo ciclo do WHILE
                except Exception as e_fetch_assets:
                    log_console(page, f"Erro ao buscar ativos (5 Velas Multi): {e_fetch_assets}", "error")
                    time.sleep(5)
                    continue # Pula para o próximo ciclo do WHILE
            else:
                # Modo Ativo Único
                ativos_para_analisar = [user_session.asset_var]
            # ====================================================

            # --- Loop sobre os ativos definidos (seja 1 ou 5) --- 
            entrada_realizada_neste_ciclo = False # Flag para sair do loop de ativos após trade
            for ativo in ativos_para_analisar:
                # Verificar parada dentro do loop de ativos
                if state.get('stop', True):
                    log_console(page, "Parada solicitada durante análise de ativos (5 Velas)", "info")
                    break # Sai do loop FOR
                
                # log_console(page, f"Analisando {ativo}...", "debug") # Log detalhado

                try:
                    # --- Verificação de Payout (dentro do loop FOR) --- 
                    try:
                        binary_p, turbo_p, digital_p = payout(api_instance, ativo)
                        if digital_p > max(binary_p, turbo_p, 0):
                            option_type = 'digital'
                        elif max(binary_p, turbo_p) > 0:
                            option_type = 'binary'
                        else:
                            # log_console(page, f"Par {ativo} fechado (5 Velas). Pulando ativo...", "warn")
                            continue # Pula para o PRÓXIMO ATIVO no FOR
                    except Exception as e_payout:
                         log_console(page, f"Erro payout {ativo} (5 Velas): {e_payout}. Pulando ativo...", "error")
                         continue # Pula para o PRÓXIMO ATIVO no FOR
                    # -----------------------------------------------------

                    timestamp = api_instance.get_server_timestamp()
                    agora = datetime.fromtimestamp(timestamp)

                    # --- Lógica de Análise (somente no segundo 59) --- 
                    if agora.second == 59 and time_filter(user_session):
                        # log_console(page, f"[{agora.strftime('%H:%M:%S')}] Verificando {ativo}...", "debug")

                        velas = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)
                        if not velas or len(velas) < qnt_velas:
                            # log_console(page, f"Velas insuficientes {ativo} (5 Velas).", "warn")
                            continue # Pula para o PRÓXIMO ATIVO
                        
                        ultimas_5_velas = velas[-6:-1]
                        if len(ultimas_5_velas) != 5:
                            # log_console(page, f"Não obteve 5 velas {ativo} (5 Velas).", "warn")
                            continue # Pula para o PRÓXIMO ATIVO
                        
                        try:
                            todas_verdes = True
                            todas_vermelhas = True
                            for i, vela in enumerate(ultimas_5_velas):
                                if not all(k in vela for k in ('open', 'close')): raise ValueError("Dados inválidos")
                                if vela['close'] >= vela['open']: todas_vermelhas = False
                                if vela['close'] <= vela['open']: todas_verdes = False
                        except Exception as e_candle_err:
                            log_console(page, f"Erro velas {ativo} (5 Velas): {e_candle_err}", "error")
                            continue # Pula para o PRÓXIMO ATIVO
                        
                        # Se não houve erro na análise:
                        direcao = None
                        if todas_verdes:
                            log_console(page, f"🟢 5 Verdes: {ativo}", "info")
                            direcao = 'call'
                        elif todas_vermelhas:
                            log_console(page, f"🔴 5 Vermelhas: {ativo}", "info")
                            direcao = 'put'

                        if direcao:
                            log_console(page, f"➡️ Entrada {direcao.upper()} em {ativo} (5 Velas)", "info")
                            purchase(page, ativo, valor_entrada, direcao, 1, option_type,
                                     user_session.use_soros_var, user_session.soros_levels_var,
                                     user_session.martingale_levels_var, user_session.martingale_factor_var,
                                     user_session.reentry_win_var, user_session)
                            entrada_realizada_neste_ciclo = True # Sinaliza que houve trade
                            break # Sai do loop FOR (para de analisar outros ativos neste ciclo)
                    # else: # Fora do segundo 59 ou filtro de tempo
                        # pass

                except Exception as e_ativo_loop:
                     log_console(page, f"Erro ao analisar ativo {ativo} (5 Velas): {e_ativo_loop}", "error")
                     # Continua para o próximo ativo

            # --- Fim do loop FOR sobre os ativos ---
            if state.get('stop', True): # Verifica stop após o loop FOR
                break # Sai do loop WHILE
            if entrada_realizada_neste_ciclo:
                time.sleep(1) # Pequena pausa após trade antes do próximo ciclo WHILE

        except Exception as e_while_loop:
            log_console(page, f"Erro inesperado no loop WHILE estrategia_cinco_velas: {e_while_loop}", "error")
            traceback.print_exc()
            time.sleep(5) # Pausa maior em caso de erro inesperado

        # Pausa curta entre os ciclos do WHILE
        time.sleep(0.5)

    log_console(page, f"Loop interno da Estratégia Cinco Velas finalizado.", "info")

# =====================
# **show_modal**
# =====================
def show_modal(page, message, asset, direction, entry_value, strategy_name, user_session, quantum_theme, stop_bot, ui_elements, state, stop_flag, currency):
    """Mostra o modal de operação do robô com labels próprios.
       O timer agora é controlado pelo 'state' global.
    """
    # --- Buscar valores consistentemente do state, usando user_session ou parâmetro como fallback ---
    win_count = state.get('win_count', 0)
    loss_count = state.get('loss_count', 0)
    total_profit = state.get('total_profit', 0.0)
    account_balance = state.get('account_balance', user_session.account_balance) # Usa state, fallback user_session
    safe_currency = state.get('currency', currency) # Usa state, fallback parâmetro 'currency'
    # ------------------------------------------------------------------------------------------

    # Controles de UI GERAIS passados (para timer/progresso)
    progress_ring = ui_elements.get('progress_ring')
    timer_text = ui_elements.get('timer_text')
    result_label = ui_elements.get('result_label') # Este pode ser reutilizado se for só texto informativo
    status_label = ui_elements.get('status_label') # Obter referência para o status label da UI principal

    # --- VERIFICAÇÃO ROBUSTA DOS CONTROLES --- 
    if page is None:
        print("ERRO [show_modal]: Objeto 'page' é None.")
        return
    if None in [progress_ring, timer_text, result_label]:
        print(f"ERRO [show_modal]: Controles essenciais não encontrados em ui_elements. Progress: {progress_ring}, Timer: {timer_text}, Result: {result_label}")
        return
    # -------------------------------------------

    # Resetar controles gerais - Timer inicializado como 'Aguardando...'
    progress_ring.value = 0
    timer_text.value = "Aguardando..." # Modificado: Não usa mais 'exp'
    result_label.value = ""

    # --- CRIAR LABELS ESPECÍFICOS PARA O MODAL ---
    modal_status_label = ft.Text("Aguardando operação...", size=12, color=quantum_theme["text_secondary"], weight="bold") # Modificado
    modal_win_label = ft.Text(f"Vitórias: {win_count}", size=12, color=quantum_theme["success"])
    modal_loss_label = ft.Text(f"Derrotas: {loss_count}", size=12, color=quantum_theme["error"])
    modal_total_profit_label = ft.Text(f"Lucro Total: {safe_currency} {total_profit:.2f}", size=14, weight="bold", color=quantum_theme["success"])
    modal_balance_label = ft.Text(f"{safe_currency}{account_balance:.2f}", size=14, weight="bold", color=quantum_theme["success"])
    # --------------------------------------------

    # Atualizar status na interface principal
    if status_label:
        status_label.value = "Operando..." # Ou "Aguardando"?
        status_label.color = quantum_theme["success"]
        try:
            status_label.update()
        except Exception as e_status:
            print(f"Erro ao atualizar status_label na UI principal: {e_status}")

    show_balance = True # Define o estado inicial de visibilidade
    def toggle_balance(e):
        nonlocal show_balance, account_balance, safe_currency # Precisa acessar essas vars
        show_balance = not show_balance
        # Atualizar com o valor mais recente do state se possível
        current_balance_modal = state.get('account_balance', account_balance)
        modal_balance_label.value = f"{safe_currency}{current_balance_modal:.2f}" if show_balance else "*******"
        modal_balance_label.update()

    # Ícone e cor da direção serão atualizados dinamicamente pela thread update_modal_real_time
    direction_icon_control = ft.Icon(name=ft.icons.HOURGLASS_EMPTY, size=24, color=quantum_theme["text_secondary"]) # Placeholder
    direction_value_label = ft.Text(f" {safe_currency}{entry_value:.2f}", size=14, weight="bold", color=quantum_theme["text_secondary"]) # Placeholder

    modal_container = None

    # --- Função para o callback do PubSub de logs DENTRO do modal ---
    def on_log_update_modal(log_entry: dict):
        if not isinstance(log_entry, dict) or 'message' not in log_entry:
            return
        print(f"[Modal Log] Recebido: {log_entry}")
        try:
            log_control = _create_log_control(log_entry)
            max_log_display_modal = 100
            if len(log_list_view_modal.controls) >= max_log_display_modal:
                log_list_view_modal.controls.pop(0)
            log_list_view_modal.controls.append(log_control)
            if log_list_view_modal.page:
                log_list_view_modal.scroll_to(offset=-1, duration=300)
                log_list_view_modal.update()
        except Exception as e_log_modal:
            print(f"ERRO ao adicionar log no modal: {e_log_modal}")
    # ===============================================================

    # --- REMOVIDO: Handler PubSub para exibir o resultado da operação --- 
    # (A lógica foi movida para update_progress)
    # --- FIM DO HANDLER REMOVIDO ---

    def close_and_stop(e):
        nonlocal modal_container, stop_flag # <--- Adicionado stop_flag
        print("Botão fechar/parar do modal clicado.")
        stop_bot(e.page) # Chama stop_bot que define state['stop']=True e habilita botões
        stop_flag['active'] = False # <--- ADICIONADO: Sinaliza para as threads pararem
        print("[close_and_stop] stop_flag['active'] definido como False.") # Debug Log
        
        # --- Modificado: Desinscrever APENAS dos handlers relevantes --- 
        if hasattr(page, 'pubsub'):
            try:
                # Desinscrever de todos os handlers do modal
                page.pubsub.unsubscribe(on_stats_update_modal) 
                page.pubsub.unsubscribe(on_new_operation_started)
                # === DESINSCREVER DO LOG ===
                page.pubsub.unsubscribe(on_log_update_modal) 
                # --- NÃO HÁ MAIS HANDLER DE RESULTADO PARA DESINSCREVER ---
                print("Modal desinscrito dos eventos PubSub (stats, new_op, log).")
            except Exception as e_unsub:
                print(f"Erro ao desinscrever do PubSub: {e_unsub}")

        # Remover da overlay
        if modal_container and hasattr(e.page, 'overlay') and modal_container in e.page.overlay:
            e.page.overlay.remove(modal_container)
        else: 
            print("Erro: Modal não encontrado para remover do overlay.")
            # Tentar fechar via page.dialog como fallback?
            if e.page.dialog == modal_container: # Verificar se é o dialog atual
                 e.page.dialog.open = False
                 e.page.dialog = None
                 print("Fechado via page.dialog como fallback.")

        # Atualizar status na UI principal
        # ... (código para atualizar status_label)
        if status_label:
            status_label.value = "Não Operando"
            status_label.color = quantum_theme["error"]
            try:
                status_label.update()
            except:
                pass

        # Atualizar a página principal para refletir status parado e stats finais
        # (Isso já deve ser feito pelo on_stats_update após o stop)
        e.page.update()

    # Função para atualizar labels do modal em resposta ao evento pubsub
    def on_stats_update_modal(message, page, user_session):
        # Verificar se a mensagem é para este handler
        if message != "update_stats":
            # print(f"[Modal] Ignorando mensagem PubSub (não é update_stats): {message}") # Debug opcional
            return
            
        try:
            # Atualizar com os valores mais recentes do state
            current_win_count = state.get('win_count', 0)
            current_loss_count = state.get('loss_count', 0)
            current_profit = state.get('total_profit', 0.0)
            current_currency = state.get('currency', safe_currency)

            # Atualizar os labels do modal
            modal_win_label.value = f"Vitórias: {current_win_count}"
            modal_loss_label.value = f"Derrotas: {current_loss_count}"
            modal_total_profit_label.value = f"Lucro Total: {current_currency} {current_profit:.2f}"

            # Atualizar cor baseado no lucro
            if current_profit >= 0:
                modal_total_profit_label.color = quantum_theme["success"]
            else:
                modal_total_profit_label.color = quantum_theme["error"]

            # Atualizar saldo se não estiver oculto
            if show_balance:
                current_balance = state.get('account_balance', account_balance)
                modal_balance_label.value = f"{current_currency}{current_balance:.2f}"

            # Atualizar os controles
            modal_win_label.update()
            modal_loss_label.update()
            modal_total_profit_label.update()
            modal_balance_label.update()

        except Exception as e:
            print(f"Erro ao atualizar estatísticas no modal via pubsub: {e}")
            traceback.print_exc()

    # --- Função para lidar com o início de uma nova operação --- 
    def on_new_operation_started(message):
        # Verificar se a mensagem é para este handler
        if message != "new_operation_started":
            # print(f"[Modal] Ignorando mensagem PubSub (não é new_operation_started): {message}") # Debug opcional
            return

        print("Callback 'on_new_operation_started' acionado no modal.") # Debug
        # A thread update_progress vai pegar os detalhes do state
        # Atualiza o status visual do modal
        try: # Adicionado try-except para segurança
            if modal_status_label and modal_status_label.page:
                modal_status_label.value = "Operando..."
            # Atualiza informações da operação (direção, valor)
            op_direction = state.get('current_operation_direction', '...') # Assumindo que 'purchase' salva a direção
            op_entry_value = state.get('current_operation_entry_value', entry_value) # Assumindo que 'purchase' salva o valor
            if direction_icon_control and direction_icon_control.page:
                direction_icon_control.name = ft.icons.ARROW_UPWARD if op_direction == 'call' else ft.icons.ARROW_DOWNWARD if op_direction == 'put' else ft.icons.HOURGLASS_EMPTY
                direction_icon_control.color = quantum_theme["success"] if op_direction == 'call' else quantum_theme["error"] if op_direction == 'put' else quantum_theme["text_secondary"]
                direction_icon_control.update()
            if direction_value_label and direction_value_label.page:
                 direction_value_label.value = f" {safe_currency}{op_entry_value:.2f}"
                 direction_value_label.color = direction_icon_control.color
                 direction_value_label.update()
                 print(f"[on_new_operation_started] Controles do modal atualizados: dir={op_direction}, valor={op_entry_value}") # Debug Log
        except Exception as e_on_new_op:
            print(f"ERRO em on_new_operation_started: {e_on_new_op}")

    close_button = ft.IconButton(icon=ft.icons.CLOSE, icon_color=quantum_theme["text_secondary"], on_click=close_and_stop, tooltip="Fechar")

    # === DEFINIR O LISTVIEW DE LOGS AQUI (ANTES DE SER USADO) ===
    log_list_view_modal = ft.ListView(
        expand=True,
        spacing=5,
        auto_scroll=True,
        height=150, # Altura fixa ou adaptativa
        reverse=False,
        controls=[] # Inicia vazio
    )
    # ==========================================================
    
    # --- Criação do Conteúdo do Modal --- #
    # Determinar texto do ativo (MULTI-ATIVOS ou nome)
    asset_display_text = "MULTI-ATIVOS" if user_session.analyze_all_pairs_var else asset
    
    modal_content = ft.Column([
        # Título e Estratégia
        ft.Text(strategy_name, size=18, weight="w900", color=quantum_theme["primary"]),
        ft.Divider(height=5, color=ft.colors.with_opacity(0.2, quantum_theme["text_secondary"])),

        # === Informações da Conta ===
        ft.Text("Informações da Conta", size=14, weight="w600", color=quantum_theme["text_secondary"]),
        ft.Row([
            ft.Text("Investimento Base:", size=12, color=quantum_theme["text"]),
            ft.Text(f"{safe_currency}{entry_value:.2f}", size=12, weight="bold", color=quantum_theme["text"])
        ]),
        ft.Row([
            ft.Text("Saldo da conta:", size=12, color=quantum_theme["text"]),
            modal_balance_label, # Label atualizado dinamicamente
            ft.Switch(
                value=show_balance, 
                on_change=toggle_balance, 
                active_color=quantum_theme["secondary"]
            ),
            ft.Text("Mostrar Saldo", size=12, color=quantum_theme["text"])
        ]),
        # --- Bloco de Ativo/Status/Valor (Layout Restaurado da versão funcional) ---
        ft.Container(
             content=ft.Row([
                 ft.Stack([
                     progress_ring, 
                     ft.Container(content=timer_text, alignment=ft.alignment.center)
                 ], alignment=ft.alignment.center), # Stack contém anel e texto
                 ft.Column([ # Coluna ao lado do Stack
                     # Container para o nome do ativo (mantendo estilo)
                     ft.Container(
                        content=ft.Text(asset_display_text, weight="bold", size=12, color=quantum_theme["secondary"]),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        bgcolor=ft.colors.with_opacity(0.1, quantum_theme["secondary"]),
                        border_radius=10
                     ),
                     ft.Row([direction_icon_control, direction_value_label]) # Ícone/valor da direção
                 ], spacing=5)
             ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), # Row contém Stack e Coluna
             padding=ft.Padding(left=15, right=15, top=10, bottom=10), 
             bgcolor=ft.colors.with_opacity(0.05, quantum_theme["surface"]), 
             border_radius=15, 
             margin=ft.margin.only(top=5, bottom=5)
        ),
        # -------------------------------------------------------------------------
        ft.Divider(height=5, color=ft.colors.with_opacity(0.2, quantum_theme["text_secondary"])),

        # === Desempenho ===
        ft.Text("Desempenho", size=14, weight="w600", color=quantum_theme["text_secondary"]),
        ft.Row([
            modal_win_label,
            ft.Container(width=10),
            modal_loss_label,
        ]),
        modal_total_profit_label,
        ft.Divider(height=5, color=ft.colors.with_opacity(0.2, quantum_theme["text_secondary"])),

        # === Área de Log ===
        ft.Text("Logs de Operação", size=14, weight="w600", color=quantum_theme["text_secondary"]),
        ft.Container(
             log_list_view_modal, # Agora a variável existe
             height=150, # Altura fixa para a área de log
             border=ft.border.all(1, ft.colors.with_opacity(0.1, quantum_theme["text_secondary"])),
             border_radius=5,
             padding=5,
             expand=True # Tentar expandir para preencher espaço restante
        ),
        
        # === Botão Parar Robô ===
        ft.Container(height=10), # Espaçamento antes do botão
        # --- Correção: Aplicar gradiente ao Container, não ao botão ---
        ft.Container(
            # Conteúdo do botão movido para dentro do container
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.STOP, color=quantum_theme["text"]),
                    ft.Text("PARAR ROBÔ", color=quantum_theme["text"], weight=ft.FontWeight.BOLD)
                ]),
                on_click=close_and_stop,
                # Estilo do botão para ficar transparente e sem sombra
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.TRANSPARENT,
                    shadow_color=ft.colors.TRANSPARENT,
                    shape=ft.RoundedRectangleBorder(radius=10), # Manter borda arredondada
                    padding=10 # Padding interno do botão
                ),
                expand=True # Fazer o botão interno expandir
            ),
            # Estilo do Container (gradiente, forma, etc.)
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    quantum_theme["error"], # Cor principal (vermelho)
                    ft.colors.with_opacity(0.7, quantum_theme["error"]), # Tom mais escuro/transparente
                ]
            ),
            border_radius=10, # Borda do container
            # Remover padding do container se o botão já tiver, ou ajustar conforme necessário
            # padding=10, 
            expand=True # Fazer o container expandir
        )
        # --- Fim da Correção ---
        # ========================
        
    ], 
    scroll=ft.ScrollMode.ADAPTIVE, # Garantir que a coluna possa rolar
    expand=True # Fazer a coluna tentar expandir dentro do container pai
    )
    # --- Fim da Criação do Conteúdo --- #

    modal_container = ft.Container(
        content=modal_content, 
        padding=20, 
        bgcolor=ft.Colors.with_opacity(0.95, quantum_theme["background"]), 
        border_radius=20, 
        border=ft.border.all(1, ft.colors.with_opacity(0.2, quantum_theme["secondary"])), 
        width=450, # Largura fixa do modal
        height=700, # Adicionar uma altura sugerida para garantir visibilidade do botão
        alignment=ft.alignment.top_center 
    )

    # Adicionar ao overlay
    if hasattr(page, 'overlay'):
        page.overlay.append(modal_container)
        page.update() # Update inicial para mostrar o modal
    else:
        print("ERRO [show_modal]: page.overlay não existe.")
        return

    # --- INSCREVER O MODAL NO PUBSUB (APENAS LOGS, STATS E NEW_OP) ---
    if hasattr(page, 'pubsub'):
        # Se on_stats_update_modal existir e for necessário, reinscrever:
        page.pubsub.subscribe(lambda msg: on_stats_update_modal(msg, page, user_session))
        page.pubsub.subscribe(on_new_operation_started)
        # === INSCREVER NO LOG ===
        page.pubsub.subscribe(on_log_update_modal)
        # --- NÃO HÁ MAIS INSCRIÇÃO PARA RESULTADO AQUI ---
        print("Modal registrado para eventos PubSub (stats, new_op, log)")
    else:
        print("AVISO: Sistema pubsub não disponível para o modal")
    # -----------------------------------------------------

    # --- INICIAR THREADS --- 
    threading.Thread(target=update_progress, args=(state, progress_ring, timer_text, stop_flag, modal_status_label), daemon=True).start()
    # --- RESTAURADO: Thread 'update_modal_real_time' como fallback --- 
    threading.Thread(target=update_modal_real_time, args=(stop_flag, state, modal_win_label, modal_loss_label, modal_total_profit_label, modal_balance_label, currency, modal_status_label, status_label), daemon=True).start()
    # --- FIM RESTAURAÇÃO ---
    # --- RESTAURADO: Chamada para 'start_modal_update_thread' como na versão ok --- 
    start_modal_update_thread(modal_win_label, modal_loss_label, modal_total_profit_label, modal_balance_label, stop_flag, state, currency, quantum_theme)
    # --- FIM RESTAURAÇÃO ---
    print("Threads do modal iniciadas.")

def start_modal_update_thread(modal_win_label, modal_loss_label, modal_total_profit_label, modal_balance_label, stop_flag, state, currency, quantum_theme):
    def update_loop():
        while stop_flag['active']:
            try:
                win_count = state.get('win_count', 0)
                loss_count = state.get('loss_count', 0)
                total_profit = state.get('total_profit', 0.0)
                account_balance = state.get('account_balance', 0.0)
                # Atualizar os labels
                modal_win_label.value = f"Vitórias: {win_count}"
                modal_loss_label.value = f"Derrotas: {loss_count}"
                modal_total_profit_label.value = f"Lucro Total: {currency} {total_profit:.2f}"
                modal_total_profit_label.color = quantum_theme["success"] if total_profit >= 0 else quantum_theme["error"]
                modal_balance_label.value = f"{currency}{account_balance:.2f}"
                # Atualizar na interface
                modal_win_label.update()
                modal_loss_label.update()
                modal_total_profit_label.update()
                modal_balance_label.update()
            except Exception as e:
                print(f"[ModalUpdateThread] Erro ao atualizar labels: {e}")
            time.sleep(0.5)
    t = threading.Thread(target=update_loop, daemon=True)
    t.start()

def update_progress(state, progress_ring, timer_text, stop_flag, modal_status_label):
    """Atualiza o anel de progresso e o texto do timer baseado no 'state' global.
       Reinicia o contador quando uma nova operação começa.
       AGORA exibe o resultado WIN/LOSS diretamente.
    """
    print("[update_progress] Thread iniciada (Versão Revertida para teste).") # Debug
    last_result_displayed = False # Flag para controlar se o resultado já foi mostrado neste ciclo
    
    while stop_flag['active']:
        last_result_displayed = False # Resetar a flag no início de cada ciclo de espera
        # Espera até que uma operação esteja em progresso
        print("[update_progress] Aguardando operation_in_progress ser True...") # Debug
        while not state.get('operation_in_progress', False) and stop_flag['active']:
            # --- MOSTRAR RESULTADO DA OPERAÇÃO ANTERIOR (LÓGICA RESTAURADA) --- #
            if not last_result_displayed: # Só mostrar uma vez por ciclo
                last_result = state.pop('last_operation_result', None) # Lê e REMOVE o resultado do state
                if last_result:
                    print(f"[update_progress] Resultado detectado: {last_result}")
                    try:
                        if timer_text and timer_text.page:
                            if last_result == 'WIN':
                                timer_text.value = "WIN!"
                                timer_text.color = quantum_theme["success"]
                                timer_text.weight = ft.FontWeight.BOLD # Destacar
                                timer_text.size = 18 # Aumentar tamanho
                            elif last_result == 'LOSS':
                                timer_text.value = "LOSS!"
                                timer_text.color = quantum_theme["error"]
                                timer_text.weight = ft.FontWeight.BOLD # Destacar
                                timer_text.size = 18 # Aumentar tamanho
                            else: # EMPATE
                                timer_text.value = "EMPATE"
                                timer_text.color = quantum_theme["text_secondary"]
                                timer_text.weight = ft.FontWeight.NORMAL # Normal
                                timer_text.size = 16 # Tamanho normal
                            timer_text.update()
                            last_result_displayed = True # Marcar que foi exibido
                            
                            # Manter progresso em 100% durante a exibição do resultado
                            if progress_ring and progress_ring.page and progress_ring.value != 1.0:
                                progress_ring.value = 1.0
                                progress_ring.update()
                                
                            time.sleep(2.0) # Manter a mensagem por 2 segundos
                            
                            # Limpar texto para aguardar próxima operação (se não parar)
                            if stop_flag['active']:
                                timer_text.value = "Aguardando..."
                                timer_text.color = quantum_theme["text_secondary"] # Restaurar cor padrão
                                timer_text.weight = ft.FontWeight.NORMAL # Restaurar peso
                                timer_text.size = 16 # Restaurar tamanho
                                timer_text.update()
                    except Exception as e_show_res:
                        print(f"ERRO ao mostrar resultado no modal: {e_show_res}")
                        # Resetar flag mesmo se der erro
                        last_result_displayed = True 
            # ----------------------------------------------------------------- #
            
            # Define um estado de espera se os controles existirem (se o resultado não foi mostrado ou já foi limpo)
            if not last_result_displayed:
                try:
                    if timer_text and timer_text.page and timer_text.value != "Aguardando...":
                        timer_text.value = "Aguardando..."
                        timer_text.color = quantum_theme["text_secondary"] # Garantir cor padrão
                        timer_text.weight = ft.FontWeight.NORMAL # Garantir peso normal
                        timer_text.size = 16 # Garantir tamanho normal
                        timer_text.update()
                    if progress_ring and progress_ring.page:
                        if progress_ring.value != 0:
                            progress_ring.value = 0
                            progress_ring.update()
                    if modal_status_label and modal_status_label.page and modal_status_label.value != "Aguardando operação...":
                         modal_status_label.value = "Aguardando operação..."
                         modal_status_label.color = quantum_theme["text_secondary"]
                         modal_status_label.update()
                except ValueError as e_val:
                     # Log específico para ValueError
                     print(f"VALUE_ERROR [update_progress > wait_update]: {e_val}")
                     traceback.print_exc() # Imprimir stack trace para ValueErrors
                except Exception as e_wait_update:
                     print(f"ERRO GERAL [update_progress > wait_update]: {e_wait_update}")
            time.sleep(0.2) # Verifica o estado frequentemente

        # Sai se o robô foi parado
        if not stop_flag['active']:
            print("Thread update_progress terminando (stop_flag não ativa).") # Debug
            break

        # Operação começou, obter detalhes do state
        total_duration_seconds = state.get('current_operation_expiration_seconds', 0)
        start_time = state.get('current_operation_start_time', time.time())
        print(f"[update_progress] Nova operação detectada! Duração: {total_duration_seconds}s, StartTime: {start_time}") # DEBUG
        
        # Restaurar cor/peso/tamanho padrão do timer_text no início da operação
        try:
             if timer_text and timer_text.page:
                 timer_text.color = quantum_theme["text_secondary"]
                 timer_text.weight = ft.FontWeight.NORMAL
                 timer_text.size = 16
                 timer_text.update()
        except Exception as e_reset_color:
             print(f"Erro ao resetar cor/peso/tamanho do timer: {e_reset_color}")

        # Loop da contagem regressiva para a operação atual
        while state.get('operation_in_progress', False) and stop_flag['active']:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, int(total_duration_seconds - elapsed_time))
            progress_value = min(1.0, elapsed_time / total_duration_seconds) if total_duration_seconds > 0 else 1.0

            try:
                # Atualizar controles diretamente, verificando se ainda estão montados
                if progress_ring and progress_ring.page:
                    progress_ring.value = progress_value
                    progress_ring.update()
                else:
                    print("AVISO [update_progress > countdown]: progress_ring não está mais na página. Parando thread.")
                    stop_flag['active'] = False; break

                if timer_text and timer_text.page:
                    timer_text.value = f"{remaining_time}s"
                    # Garantir que a cor/peso/tamanho estejam normais durante a contagem
                    if timer_text.color != quantum_theme["text_secondary"] or timer_text.weight != ft.FontWeight.NORMAL or timer_text.size != 16:
                        timer_text.color = quantum_theme["text_secondary"]
                        timer_text.weight = ft.FontWeight.NORMAL
                        timer_text.size = 16
                    timer_text.update()
                else:
                    print("AVISO [update_progress > countdown]: timer_text não está mais na página. Parando thread.")
                    stop_flag['active'] = False; break

                # Manter status do modal atualizado
                if modal_status_label and modal_status_label.page:
                    if remaining_time < 5:
                        modal_status_label.value = "Verificando resultado..."
                    elif modal_status_label.value != "Operando...": # Evita update desnecessário
                        modal_status_label.value = "Operando..."
                        modal_status_label.color = quantum_theme["success"]
                        modal_status_label.update()

            except Exception as e_update:
                print(f"ERRO [update_progress > countdown_loop]: {e_update}")
                stop_flag['active'] = False # Parar em caso de erro inesperado
                break

            if remaining_time <= 0:
                print("[update_progress] Contagem regressiva chegou a 0.") # Debug
                state['operation_in_progress'] = False # Sinaliza fim da operação
                break # Sai do loop de contagem

            time.sleep(1.0)
        # FIM do loop da contagem regressiva

        # --- MOVER A EXIBIÇÃO DO RESULTADO PARA CÁ --- #
        # Tenta exibir o resultado da operação que ACABOU de terminar
        last_result = state.pop('last_operation_result', None) # Lê e REMOVE o resultado
        if last_result:
            print(f"[update_progress] Resultado pós-operação detectado: {last_result}")
            try:
                if timer_text and timer_text.page:
                    # ... (lógica para definir texto, cor, peso, tamanho baseados em WIN/LOSS/EMPATE) ...
                    if last_result == 'WIN':
                        timer_text.value = "WIN!"
                        timer_text.color = quantum_theme["success"]
                        timer_text.weight = ft.FontWeight.BOLD
                        timer_text.size = 18
                    elif last_result == 'LOSS':
                        timer_text.value = "LOSS!"
                        timer_text.color = quantum_theme["error"]
                        timer_text.weight = ft.FontWeight.BOLD
                        timer_text.size = 18
                    else: # EMPATE
                        timer_text.value = "EMPATE"
                        timer_text.color = quantum_theme["text_secondary"]
                        timer_text.weight = ft.FontWeight.NORMAL
                        timer_text.size = 16
                    timer_text.update()

                    # Manter progresso em 100%
                    if progress_ring and progress_ring.page and progress_ring.value != 1.0:
                        progress_ring.value = 1.0
                        progress_ring.update()

                    print(f"[update_progress] Exibindo '{timer_text.value}' por 2 segundos...")
                    time.sleep(2.0) # PAUSA OBRIGATÓRIA

                    # Limpar após a pausa, ANTES de esperar a próxima operação
                    if stop_flag['active']:
                        timer_text.value = "Aguardando..."
                        timer_text.color = quantum_theme["text_secondary"]
                        timer_text.weight = ft.FontWeight.NORMAL
                        timer_text.size = 16
                        timer_text.update()

            except Exception as e_show_res:
                print(f"ERRO ao mostrar resultado no modal (pós-op): {e_show_res}")
        # --- FIM DA EXIBIÇÃO DO RESULTADO --- #

        # Se saiu do loop principal (stop_flag), sair da thread
        if not stop_flag['active']:
             print("[update_progress] Stop flag desativada após exibir resultado. Saindo.")
             break

        # Aguarda o INÍCIO da próxima operação (operation_in_progress == True)
        print("[update_progress] Aguardando PRÓXIMA operation_in_progress ser True...")
        while not state.get('operation_in_progress', False) and stop_flag['active']:
             # Resetar para Aguardando (caso não tenha sido limpo após exibição)
             try:
                 if timer_text and timer_text.page and timer_text.value != "Aguardando...":
                     timer_text.value = "Aguardando..."
                     timer_text.color = quantum_theme["text_secondary"]
                     timer_text.weight = ft.FontWeight.NORMAL
                     timer_text.size = 16
                     timer_text.update()
                 if progress_ring and progress_ring.page and progress_ring.value != 0:
                     progress_ring.value = 0 # Resetar progresso
                     progress_ring.update()
                 if modal_status_label and modal_status_label.page and modal_status_label.value != "Aguardando operação...":
                     modal_status_label.value = "Aguardando operação..."
                     modal_status_label.color = quantum_theme["text_secondary"]
                     modal_status_label.update()
             except Exception as e_wait_update:
                 print(f"ERRO GERAL [update_progress > wait_update_loop]: {e_wait_update}")
             time.sleep(0.2)
        # Fim do loop de espera pela próxima operação

    print("[update_progress] Thread finalizada.")
    # ... (Reset final dos controles permanece o mesmo) ...
    try:
        if progress_ring and progress_ring.page: progress_ring.value = None; progress_ring.update()
        if timer_text and timer_text.page:
            timer_text.value = "Parado"
            timer_text.weight = ft.FontWeight.NORMAL # Reset final
            timer_text.size = 16 # Reset final
            timer_text.color = quantum_theme["error"]
            timer_text.update()
        if modal_status_label and modal_status_label.page: modal_status_label.value = "Parado"; modal_status_label.color = quantum_theme["error"]; modal_status_label.update()
    except Exception as e_final: print(f"ERRO [update_progress > final_thread]: {e_final}")

def update_modal_real_time(stop_flag, state, modal_win_label, modal_loss_label, modal_total_profit_label, modal_balance_label, currency, modal_status_label, status_label):
    """Atualiza W/L, Lucro e Saldo no modal complementando o sistema pubsub."""
    # ESTA FUNÇÃO PROVAVELMENTE NÃO É MAIS NECESSÁRIA SE O PUBSUB FUNCIONAR BEM
    # Considerar comentar ou remover a chamada a esta thread em show_modal
    # (RESTAURADA CONFORME VERSÃO FUNCIONAL FORNECIDA)
    print("[update_modal_real_time] Thread iniciada (Versão Revertida).") # Debug
    # Armazena valores anteriores para detectar mudanças
    prev_win_count = None 
    prev_loss_count = None
    prev_profit = None
    prev_balance = None
    force_update_counter = 0  # Contador para forçar atualizações periódicas
    
    while stop_flag['active']:
        print(f"[update_modal_real_time] Loop - stop_flag: {stop_flag['active']}") # Debug
        try:
            # Verificar se os controles ainda estão montados
            if not all(hasattr(label, 'page') and label.page for label in [modal_win_label, modal_loss_label, modal_total_profit_label, modal_balance_label] if label is not None):
                print("AVISO: Labels do modal inválidos/desmontados em update_modal_real_time. Parando thread.")
                stop_flag['active'] = False
                break

            # Usar uma cópia do state para evitar problemas de referência
            state_copy = state.copy() if isinstance(state, dict) else {}
            
            # Obter valores atuais do state 
            win_count_state = state_copy.get('win_count', 0)
            loss_count_state = state_copy.get('loss_count', 0)
            total_profit_state = state_copy.get('total_profit', 0.0)
            balance_state = state_copy.get('account_balance', 0.0)
            safe_currency = state_copy.get('currency', currency)
            
            # Debug: imprimir valores atuais
            print(f"[update_modal_real_time] Estado lido: W:{win_count_state} L:{loss_count_state} P:{total_profit_state:.2f} B:{balance_state:.2f}") # Debug
            
            # Incrementar contador para forçar atualização a cada ~5 segundos
            force_update_counter += 1
            force_update = (force_update_counter >= 5)  # Força update a cada 5 ciclos
            
            # Verificar mudanças nos valores
            win_changed = prev_win_count != win_count_state
            loss_changed = prev_loss_count != loss_count_state
            profit_changed = prev_profit != total_profit_state
            balance_changed = prev_balance != balance_state
            
            # SEMPRE atualizar os labels ao detectar mudanças ou periodicamente
            try:
                if win_changed or force_update:
                    print(f"[update_modal_real_time] Atualizando vitórias: {win_count_state}") # Debug
                    modal_win_label.value = f"Vitórias: {win_count_state}"
                    modal_win_label.update()
                    
                if loss_changed or force_update:
                    print(f"[update_modal_real_time] Atualizando derrotas: {loss_count_state}") # Debug
                    modal_loss_label.value = f"Derrotas: {loss_count_state}"
                    modal_loss_label.update()
                
                if profit_changed or force_update:
                    print(f"[update_modal_real_time] Atualizando lucro: {total_profit_state:.2f}") # Debug
                    profit_text = f"Lucro Total: {safe_currency} {total_profit_state:.2f}"
                    modal_total_profit_label.value = profit_text
                    # Atualizar cor com base no lucro
                    modal_total_profit_label.color = quantum_theme["success"] if total_profit_state >= 0 else quantum_theme["error"]
                    modal_total_profit_label.update()
                
                # Atualizar saldo somente se estiver visível
                if "*******" not in modal_balance_label.value and (balance_changed or force_update):
                    print(f"[update_modal_real_time] Atualizando saldo: {balance_state:.2f}") # Debug
                    balance_text = f"{safe_currency}{balance_state:.2f}"
                    modal_balance_label.value = balance_text
                    modal_balance_label.update()
                    
                # SEMPRE manter status_label da UI principal sincronizado
                if status_label and hasattr(status_label, 'page') and status_label.page and force_update:
                    if status_label.value != "Operando...":
                        status_label.value = "Operando..."
                        status_label.color = quantum_theme["success"]
                        status_label.update()
            except Exception as e_update_controls:
                print(f"ERRO ao atualizar controles: {e_update_controls}")

            # Armazenar valores atuais para comparação na próxima iteração
            prev_win_count = win_count_state
            prev_loss_count = loss_count_state
            prev_profit = total_profit_state
            prev_balance = balance_state
            
            # Resetar contador se foi uma atualização forçada
            if force_update:
                force_update_counter = 0

        except Exception as e_update_labels:
            print(f"ERRO [update_modal_real_time > loop]: {e_update_labels}")
            import traceback
            traceback.print_exc()
            # Não parar a thread por erros temporários
            time.sleep(1)  # Esperar um pouco mais em caso de erro

        time.sleep(0.5)  # Pausa entre atualizações

    # Se a thread foi finalizada (stop_flag['active'] = False), atualizar para não operando
    try:
        if status_label and hasattr(status_label, 'page') and status_label.page:
            status_label.value = "Não Operando"
            status_label.color = quantum_theme["error"]
            status_label.update()
            
        if modal_status_label and hasattr(modal_status_label, 'page') and modal_status_label.page:
            modal_status_label.value = "Operação finalizada"
            modal_status_label.color = quantum_theme["text_secondary"]
            modal_status_label.update()
    except Exception as e_final_update:
        print(f"ERRO [update_modal_real_time > final]: {e_final_update}")
        
    print("[update_modal_real_time] Thread finalizada.")

def show_catalog_modal(api, page):
     if not api or not api.check_connect():
         dlg = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text("API não conectada."))
         page.dialog = dlg
         dlg.open = True
         page.update()
         return

     print("Funcionalidade do catalogador a ser implementada.")
     dlg = ft.AlertDialog(title=ft.Text("Catalogador"), content=ft.Text("Catalogador em desenvolvimento."))
     page.dialog = dlg
     dlg.open = True
     page.update()

def get_digital_assets_only(api):
    """
    Obtém todos os ativos digitais disponíveis, ordenados por payout.
    
    Args:
        api: Instância da API IQ Option
        
    Returns:
        Um dicionário ordenado de {ativo: payout} com os ativos digitais disponíveis
    """
    try:
        # Obter todos os pares de ativos
        all_assets = api.get_all_open_time()
        
        # Filtrar apenas digitais disponíveis
        digital_assets = {}
        
        if 'digital' in all_assets:
            for asset, status in all_assets['digital'].items():
                if status['open']:
                    try:
                        # Obter o payout para este ativo
                        # Verificamos tanto call quanto put para garantir que ambos estão disponíveis
                        payout_call = api.get_digital_payout(asset)
                        payout_put = api.get_digital_payout(asset)
                        
                        # Usamos o menor payout entre call e put para segurança
                        payout = min(payout_call, payout_put)
                        
                        if payout > 0:  # Só incluímos ativos com payout positivo
                            digital_assets[asset] = payout
                    except:
                        continue  # Se não conseguir obter o payout, pular este ativo
        
        # Ordenar por payout (maior para menor)
        sorted_assets = dict(sorted(digital_assets.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_assets
        
    except Exception as e:
        print(f"Erro ao obter ativos digitais: {e}")
        traceback.print_exc()
        return {}

def on_stats_update_main(message, page, user_session):
    # use user_session normalmente aqui
    if message != "update_stats":
        return
    # Atualiza os labels do fundo com os valores do state
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

def register_main_update_handler(page, user_session):
    """Registra o handler de atualização da tela principal"""
    if hasattr(page, 'pubsub'):
        page.pubsub.subscribe(lambda msg: on_stats_update_main(msg, page, user_session))

# Inscreva o handler no pubsub
# Chame register_main_update_handler(page, user_session) onde você tiver acesso a page e user_session

# --- Novas Estratégias --- #

def estrategia_macd_crossover(page: ft.Page, user_session: UserSession):
    """Estratégia MACD Crossover - ADICIONADO loop interno para execução contínua."""
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect():
        log_console(page, "API não conectada (MACD)", "error")
        return

    log_console(page, f"Iniciando loop interno da Estratégia MACD Crossover para {user_session.asset_var}", "info")

    ativo = user_session.asset_var
    valor_entrada = user_session.entry_value_var
    timeframe = 60 
    qnt_velas = 50 
    option_type = 'digital'

    while not state.get('stop', True): # <<<< LOOP INTERNO ADICIONADO
        try:
            # Verificar conexão e API a cada ciclo
            if not api_instance.check_connect():
                log_console(page, "API desconectada durante loop (MACD)", "error")
                state['stop'] = True # Forçar parada
                break

            # --- Verificação de Payout --- 
            try:
                binary_p, turbo_p, digital_p = payout(api_instance, ativo)
                if digital_p > max(binary_p, turbo_p, 0):
                    option_type = 'digital'
                elif max(binary_p, turbo_p) > 0:
                    option_type = 'binary'
                else:
                    log_console(page, f"Par {ativo} fechado ou sem payout (MACD). Aguardando...", "warn")
                    time.sleep(5) 
                    continue 
            except Exception as e_payout:
                 log_console(page, f"Erro ao verificar payout {ativo} (MACD): {e_payout}", "error")
                 time.sleep(5) 
                 continue
            # --------------------------------

            timestamp = api_instance.get_server_timestamp()
            dt_object = datetime.fromtimestamp(timestamp)
            seconds = int(dt_object.strftime('%S'))
            
            # Verificar se NÃO está nos últimos segundos
            if seconds > 55:
                # time.sleep(0.5) # Espera pequena para não sobrecarregar
                continue 

            # A análise acontece se o filtro de tempo permitir
            if time_filter(user_session):
                # log_console(page, f"[{dt_object.strftime('%H:%M:%S')}] Verificando MACD para {ativo}...", "debug") # Log opcional
                velas = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)
                if not velas or len(velas) < qnt_velas:
                    # log_console(page, f"Velas insuficientes para {ativo} (MACD Crossover)", "warn")
                    # Continua no próximo ciclo
                    pass # Deixa a pausa no fim do loop while tratar disso
                else:
                    # Calcular MACD 
                    try:
                         from Proflet4 import calculate_MACD
                    except ImportError:
                         log_console(page, "Erro ao importar calculate_MACD", "error")
                         time.sleep(5); continue # Pausa maior se import falhar
                         
                    macd_line, signal_line, histogram = calculate_MACD(velas)
                    if macd_line is None or signal_line is None:
                        # log_console(page, f"Não foi possível calcular MACD para {ativo}", "warn")
                        pass # Continua no próximo ciclo
                    else:
                        # Calcular MACD da vela anterior
                        macd_line_prev, signal_line_prev, _ = calculate_MACD(velas[:-1])
                        if macd_line_prev is not None and signal_line_prev is not None:
                            direcao = None
                            # Cruzamento para Cima (CALL)
                            if macd_line_prev < signal_line_prev and macd_line > signal_line:
                                log_console(page, f"📈 MACD Crossover UP detectado em {ativo}", "info")
                                direcao = 'call'
                            # Cruzamento para Baixo (PUT)
                            elif macd_line_prev > signal_line_prev and macd_line < signal_line:
                                log_console(page, f"📉 MACD Crossover DOWN detectado em {ativo}", "info")
                                direcao = 'put'
                                
                            # Aplicar filtro de médias se configurado
                            if direcao and user_session.analyze_averages_var == 'S':
                                 if len(velas) >= user_session.average_candles_var:
                                     trend = averages(velas, user_session.average_candles_var)
                                     if trend and direcao != trend:
                                         log_console(page, f"Entrada {direcao.upper()} (MACD) cancelada. Contra tendência ({trend.upper()}).", "warn")
                                         direcao = None

                            if direcao:
                                log_console(page, f"➡️ Entrada {direcao.upper()} (MACD Crossover)", "info")
                                purchase(page, ativo, valor_entrada, direcao, 1, option_type,
                                         user_session.use_soros_var, user_session.soros_levels_var,
                                         user_session.martingale_levels_var, user_session.martingale_factor_var,
                                         user_session.reentry_win_var, user_session)
                                time.sleep(1) # Pausa após a compra
            # else: # Fora do filtro de tempo
                 # pass

        except Exception as e_loop:
            log_console(page, f"Erro inesperado no loop estrategia_macd_crossover: {e_loop}", "error")
            traceback.print_exc()
            time.sleep(5) # Pausa maior em caso de erro inesperado

        # Pausa curta entre os ciclos de verificação
        time.sleep(0.5) 

    log_console(page, f"Loop interno da Estratégia MACD Crossover para {ativo} finalizado.", "info")

def estrategia_rsi_reversal(page: ft.Page, user_session: UserSession):
    """Estratégia baseada em reversão de RSI (sobrecompra/sobrevenda)."""
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): return

    ativo = user_session.asset_var
    valor_entrada = user_session.entry_value_var
    timeframe = 60 # Usar M1 para RSI Reversal, pode ser ajustado
    periodo_rsi = user_session.periodo_rsi_var if user_session.use_rsi_var else 14 # Pega do user_session ou usa 14
    qnt_velas = periodo_rsi + 5 # Garantir velas suficientes

    option_type = 'digital'
    try:
        binary_p, turbo_p, digital_p = payout(api_instance, ativo)
        if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
        elif max(binary_p, turbo_p) > 0: option_type = 'binary'
        else: 
            log_console(page, f"Par {ativo} fechado (RSI Reversal).", "warn")
            return
    except Exception as e_payout: 
        log_console(page, f"Erro payout {ativo} (RSI Reversal): {e_payout}", "error")
        return

    try:
        timestamp = api_instance.get_server_timestamp()
        dt_object = datetime.fromtimestamp(timestamp)
        seconds = int(dt_object.strftime('%S'))
        
        # Restaurado: Verificar se NÃO está nos últimos segundos para evitar entrada ruim
        if seconds > 55:
            # log_console(page, f"Ignorando análise nos últimos segundos ({seconds}s) - RSI Reversal", "debug") # Log opcional
            return

        # A análise agora acontece se o filtro de tempo permitir
        if time_filter(user_session):
            velas = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)
            if not velas or len(velas) < qnt_velas:
                log_console(page, f"Velas insuficientes para {ativo} (RSI Reversal)", "warn")
                return

            rsi_valor = calcular_RSI(velas, periodo_rsi)
            log_console(page, f"📊 RSI({periodo_rsi}) para {ativo}: {rsi_valor:.2f}", "info")

            direcao = None
            # Condição de Sobrevenda (CALL)
            if rsi_valor <= 30: 
                log_console(page, f"🟢 RSI Sobrevenda ({rsi_valor:.2f} <= 30) detectada em {ativo}", "info")
                direcao = 'call'
            # Condição de Sobrecompra (PUT)
            elif rsi_valor >= 70:
                log_console(page, f"🔴 RSI Sobrecompra ({rsi_valor:.2f} >= 70) detectada em {ativo}", "info")
                direcao = 'put'
                
            # Aplicar filtro de médias se configurado (PODE SER CONTRA-INTUITIVO para reversão)
            # Considerar remover ou inverter a lógica do filtro de média para esta estratégia?
            # Por enquanto, mantém o filtro padrão:
            if direcao and user_session.analyze_averages_var == 'S':
                 if len(velas) >= user_session.average_candles_var:
                     trend = averages(velas, user_session.average_candles_var)
                     if trend and direcao != trend:
                         log_console(page, f"Entrada {direcao.upper()} (RSI Reversal) cancelada. Contra tendência ({trend.upper()}).", "warn")
                         direcao = None

            if direcao:
                log_console(page, f"➡️ Entrada {direcao.upper()} (RSI Reversal)", "info")
                purchase(page, ativo, valor_entrada, direcao, 1, option_type,
                         user_session.use_soros_var, user_session.soros_levels_var,
                         user_session.martingale_levels_var, user_session.martingale_factor_var,
                         user_session.reentry_win_var, user_session)

    except Exception as e:
        log_console(page, f"Erro na estrategia_rsi_reversal: {e}", "error")

def estrategia_origin_rsi_reversal(page: ft.Page, user_session: UserSession):
    """Estratégia inspirada na Pro Origin Analyzer, focando em reversão de RSI com filtros."""
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): return

    ativo = user_session.asset_var
    valor_entrada = user_session.entry_value_var
    timeframe = 60 # M1 como no script original
    periodo_rsi = user_session.periodo_rsi_var if user_session.use_rsi_var else 14
    nivel_sobrecompra = 70 # Pode ser configurável no futuro
    nivel_sobrevenda = 30  # Pode ser configurável no futuro
    periodo_macro = 100     # Para filtro de tendência macro (SMA)
    periodo_volatilidade = 5 # Para filtro ATR/SMA
    qnt_velas = max(periodo_rsi + 3, periodo_macro + 1, periodo_volatilidade + 2) # Garantir velas suficientes

    # Parâmetros opcionais (adicionar checkboxes na UI depois)
    usar_filtro_tendencia_macro = True # Exemplo: Habilitar filtro SMA 100
    usar_filtro_volatilidade = True  # Exemplo: Habilitar filtro ATR

    option_type = 'digital'
    try:
        binary_p, turbo_p, digital_p = payout(api_instance, ativo)
        if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
        elif max(binary_p, turbo_p) > 0: option_type = 'binary'
        else: 
            log_console(page, f"Par {ativo} fechado (Origin RSI).", "warn")
            return
    except Exception as e_payout: 
        log_console(page, f"Erro payout {ativo} (Origin RSI): {e_payout}", "error")
        return

    try:
        timestamp = api_instance.get_server_timestamp()
        dt_object = datetime.fromtimestamp(timestamp)
        seconds = int(dt_object.strftime('%S'))
        
        # Restaurado: Verificar se NÃO está nos últimos segundos para evitar entrada ruim
        if seconds > 55:
             # log_console(page, f"Ignorando análise nos últimos segundos ({seconds}s) - Origin RSI", "debug") # Log opcional
             return 

        # A análise agora acontece se o filtro de tempo permitir
        if time_filter(user_session):
            # O resto da lógica da estratégia (cálculo indicadores, filtros, compra) permanece aqui dentro
            velas = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)
            if not velas or len(velas) < qnt_velas:
                log_console(page, f"Velas insuficientes para {ativo} (Origin RSI)", "warn")
                return

            # Importar funções necessárias
            try:
                from Proflet4 import calculate_SMA, calculate_ATR, highest, lowest, calculate_RSI
            except ImportError:
                log_console(page, "Erro ao importar funções de cálculo (Origin RSI)", "error")
                return

            # Calcular Indicadores
            rsi_valor = calculate_RSI(velas, periodo_rsi)
            rsi_anterior = calculate_RSI(velas[:-1], periodo_rsi)
            sma_macro = calculate_SMA(velas, periodo_macro) if usar_filtro_tendencia_macro else None
            atr_atual = calculate_ATR(velas, periodo_volatilidade) if usar_filtro_volatilidade else None
            sma_atr = calculate_SMA([{'close': calculate_ATR(velas[-(periodo_volatilidade+i):-i] if i>0 else velas[-periodo_volatilidade:], periodo_volatilidade)} for i in range(1, periodo_volatilidade + 1) if calculate_ATR(velas[-(periodo_volatilidade+i):-i] if i>0 else velas[-periodo_volatilidade:], periodo_volatilidade) is not None], periodo_volatilidade) if usar_filtro_volatilidade and atr_atual else None
            
            if rsi_valor is None or rsi_anterior is None:
                 log_console(page, f"Não foi possível calcular RSI para {ativo} (Origin RSI)", "warn")
                 return
            if usar_filtro_volatilidade and (atr_atual is None or sma_atr is None):
                 log_console(page, f"Não foi possível calcular Volatilidade/ATR para {ativo} (Origin RSI)", "warn")
                 # Poderia continuar sem o filtro ou retornar
                 # return 
            
            log_console(page, f"📊 Origin RSI - RSI({periodo_rsi}): {rsi_valor:.2f} (Ant: {rsi_anterior:.2f})", "info")
            if sma_macro: log_console(page, f"📊 Origin RSI - SMA({periodo_macro}): {sma_macro:.5f} | Preço: {velas[-1]['close']:.5f}", "info")
            if atr_atual and sma_atr: log_console(page, f"📊 Origin RSI - ATR({periodo_volatilidade}): {atr_atual:.5f} | SMA ATR: {sma_atr:.5f}", "info")

            direcao = None
            # Condição de Reversão Alta (CALL)
            if rsi_valor <= nivel_sobrevenda and rsi_valor > rsi_anterior: # RSI subindo de sobrevenda
                if velas[-1]['close'] > velas[-1]['open']: # Candle atual de alta
                     # Filtro Macro Tendência (Opcional)
                    if usar_filtro_tendencia_macro and sma_macro and velas[-1]['close'] < sma_macro: # Preço abaixo da SMA Lenta
                         log_console(page, f"CALL (Origin RSI) bloqueado por tendência macro de baixa (SMA {periodo_macro})", "warn")
                    # Filtro Volatilidade (Opcional)
                    elif usar_filtro_volatilidade and atr_atual and sma_atr and atr_atual < sma_atr:
                         log_console(page, f"CALL (Origin RSI) bloqueado por baixa volatilidade (ATR < SMA ATR)", "warn")
                    else:
                         log_console(page, f"🟢 Origin RSI Reversal UP detectado em {ativo} (RSI: {rsi_valor:.2f})", "info")
                         direcao = 'call'
            
            # Condição de Reversão Baixa (PUT)
            elif rsi_valor >= nivel_sobrecompra and rsi_valor < rsi_anterior: # RSI caindo de sobrecompra
                 if velas[-1]['close'] < velas[-1]['open']: # Candle atual de baixa
                     # Filtro Macro Tendência (Opcional)
                    if usar_filtro_tendencia_macro and sma_macro and velas[-1]['close'] > sma_macro: # Preço acima da SMA Lenta
                         log_console(page, f"PUT (Origin RSI) bloqueado por tendência macro de alta (SMA {periodo_macro})", "warn")
                    # Filtro Volatilidade (Opcional)
                    elif usar_filtro_volatilidade and atr_atual and sma_atr and atr_atual < sma_atr:
                         log_console(page, f"PUT (Origin RSI) bloqueado por baixa volatilidade (ATR < SMA ATR)", "warn")
                    else:
                         log_console(page, f"🔴 Origin RSI Reversal DOWN detectado em {ativo} (RSI: {rsi_valor:.2f})", "info")
                         direcao = 'put'

            if direcao:
                log_console(page, f"➡️ Entrada {direcao.upper()} (Origin RSI Reversal)", "info")
                purchase(page, ativo, valor_entrada, direcao, 1, option_type,
                         user_session.use_soros_var, user_session.soros_levels_var,
                         user_session.martingale_levels_var, user_session.martingale_factor_var,
                         user_session.reentry_win_var, user_session)

    except Exception as e:
        log_console(page, f"Erro na estrategia_origin_rsi_reversal: {e}", "error")
        import traceback
        traceback.print_exc()

def estrategia_pattern_trend(page: ft.Page, user_session: UserSession):
    api_instance = state.get('API')
    if not api_instance or not api_instance.check_connect(): return

    valor_entrada = user_session.entry_value_var
    timeframe = 60 # M1
    periodo_ema_curta = 11
    qnt_velas = max(periodo_ema_curta + 1, 5)
    option_type = 'digital' # Default

    # === AJUSTE MULTI-PAR -> SEMPRE ANALISAR OS 5 MELHORES ===
    ativos_disponiveis = get_digital_assets_only(api_instance)
    if not ativos_disponiveis:
        log_console(page, "Nenhum ativo digital disponível no momento (Pattern+Trend)", "error")
        return

    # Ordenar por payout e pegar os 5 melhores
    melhores_ativos = sorted(ativos_disponiveis.items(), key=lambda x: x[1], reverse=True)[:5]
    if not melhores_ativos:
        log_console(page, "Nenhum ativo com payout positivo encontrado após filtragem (Pattern+Trend)", "error")
        return

    # Extrair apenas os nomes dos ativos para o loop
    ativos_para_analisar = [ativo for ativo, _ in melhores_ativos]
    log_console(page, f"Analisando os {len(ativos_para_analisar)} melhores ativos digitais (Pattern+Trend - Top 5 Payouts).", "info")
    # A lógica anterior de if user_session.analyze_all_pairs_var foi removida
    # ==========================================================

    # === Loop sobre os ativos ===
    for ativo in ativos_para_analisar:
        # --- Adicionado: Verificação de parada no início do loop do ativo ---
        if state.get('stop', False):
            log_console(page, "Parada solicitada durante análise de ativos (Pattern+Trend)", "info")
            return # Sai da função se o stop foi solicitado
        # -----------------------------------------------------------------
        if user_session.analyze_all_pairs_var:
             log_console(page, f"--- Analisando {ativo} (Pattern+Trend) ---", "debug")
             
        try:
            # Verificar payout DENTRO do loop
            try:
                binary_p, turbo_p, digital_p = payout(api_instance, ativo)
                if digital_p > max(binary_p, turbo_p, 0): option_type = 'digital'
                elif max(binary_p, turbo_p) > 0: option_type = 'binary'
                else: continue # Pular ativo fechado
            except Exception as e_payout: continue # Pular ativo com erro

            timestamp = api_instance.get_server_timestamp()
            dt_object = datetime.fromtimestamp(timestamp)
            seconds = int(dt_object.strftime('%S'))

            # Restaurado: Verificar se NÃO está nos últimos segundos para evitar entrada ruim
            if seconds > 55:
                 # log_console(page, f"Ignorando análise nos últimos segundos ({seconds}s) - PatternTrend", "debug") # Log opcional
                 continue # Usar continue dentro do loop for

            # A análise agora acontece se o filtro de tempo permitir
            if time_filter(user_session):
                # O resto da lógica da estratégia (cálculo EMA, análise padrão, compra) permanece aqui dentro
                velas = api_instance.get_candles(ativo, timeframe, qnt_velas, timestamp)
                if not velas or len(velas) < 4: continue # Pular se velas insuficientes

                # Importar EMA DENTRO do loop ou garantir que já está importada
                try: from Proflet4 import calculate_EMA
                except ImportError: log_console(page, "Erro importar calculate_EMA", "error"); continue

                ema_curta = calculate_EMA(velas, periodo_ema_curta)
                if ema_curta is None: continue # Pular se EMA falhar

                # ... (Lógica de pegar velas v_atual, v_ant, etc. como estava) ...
                v_atual = velas[-1]; v_ant = velas[-2]; v_ant2 = velas[-3]; v_ant3 = velas[-4]
                close = v_atual['close']; open_ = v_atual['open']; high = v_atual['max']; low = v_atual['min']
                close1 = v_ant['close']; open1 = v_ant['open']; high1 = v_ant['max']; low1 = v_ant['min']
                close2 = v_ant2['close']; open2 = v_ant2['open']; close3 = v_ant3['close']

                tendencia_alta = close > ema_curta
                tendencia_baixa = close < ema_curta
                # ... (Log da tendência como estava) ...

                direcao = None
                padrao = ""
                # ... (Lógica de Engolfo como estava) ...
                if close1 < open1 and close > open_ and close > high1 and open_ < low1 and tendencia_alta:
                    direcao = 'call'; padrao = "Engolfo de Alta"
                elif close1 > open1 and close < open_ and close < low1 and open_ > high1 and tendencia_baixa:
                    direcao = 'put'; padrao = "Engolfo de Baixa"
                # ... (Lógica de Sequência como estava) ...
                if direcao is None:
                    if close > close1 and close1 > open2 and close3 > close2 and tendencia_alta:
                        direcao = 'call'; padrao = "Sequência de Alta"
                    elif close < close1 and close1 < open2 and close3 < close2 and tendencia_baixa:
                        direcao = 'put'; padrao = "Sequência de Baixa"

                if direcao:
                    log_console(page, f"⭐ {padrao} confirmado com tendência {('Alta' if tendencia_alta else 'Baixa')} em {ativo}", "info")
                    log_console(page, f"➡️ Entrada {direcao.upper()} em {ativo} (Pattern+Trend)", "info")
                    purchase(page, ativo, valor_entrada, direcao, 1, option_type, # Usar 'ativo' do loop
                             user_session.use_soros_var, user_session.soros_levels_var,
                             user_session.martingale_levels_var, user_session.martingale_factor_var,
                             user_session.reentry_win_var, user_session)
                    if state.get('stop', False): return # Parar tudo
                    # --- Adicionado: Interromper loop de ativos após a primeira entrada ---
                    log_console(page, f"Entrada realizada em {ativo}. Interrompendo análise de outros ativos neste ciclo.", "info")
                    break # Sai do loop 'for ativo in ...'
                    # --------------------------------------------------------------------------

        except KeyError as e_key:
             log_console(page, f"Erro chave {ativo} (Pattern+Trend): {e_key}", "error")
        except Exception as e:
            log_console(page, f"Erro na análise de {ativo} (Pattern+Trend): {e}", "error")
        
        # Pausa entre ativos no modo multi-par
        if user_session.analyze_all_pairs_var:
            time.sleep(0.1)

# --- Fim Novas Estratégias --- #