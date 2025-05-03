(function() {
    'use strict';

    // --- Configurações ---
    const BASE_URL = "https://api-bullex.onrender.com"; // Endereço da sua API Python local

    // !!! AVISO DE SEGURANÇA !!!
    // Colocar chaves de API diretamente no código do lado do cliente (como este script)
    // é INSEGURO. Qualquer pessoa pode inspecionar o código e roubar sua chave.
    // Considere usar um servidor intermediário para proteger sua chave.
    const ELEVENLABS_API_KEY = "sk_c4ab105a60295efd010db35643db964144c66f5d087889c4"; // SUA CHAVE API AQUI
    const ELEVENLABS_VOICE_ID = "NOpBlnGInO9m6vDvFkFC"; // Exemplo: Rachel. Substitua pelo ID da voz desejada.

    // --- Variáveis Globais de Estado ---
    let email = '';
    let senha = '';
    let tipo = 'automatico'; // digital, binary, automatico
    let valor_entrada = 1;
    let stop_win = 10;
    let stop_loss = 10;
    let usar_martingale = false;
    let martingale = 0;
    let fator_mg = 2;
    let usar_soros = false;
    let niveis_soros = 0;
    let analise_medias = false;
    let velas_medias = 14;
    let ativo = 'EURUSD';
    let conta = 'PRACTICE'; // PRACTICE ou REAL
    let estrategia = 1; // 1: MHI

    let conectado = false;
    let stop = true;
    let lucro_total = 0;
    let nivel_soros = 0;
    let valor_soros = 0;
    let lucro_op_atual = 0;
    let operacao_em_andamento = false;
    let saldo_inicial = 0;
    let cifrao = '$';
    let checkStopInterval = null;
    let mhiInterval = null;
    let isMinimized = false; // Estado para controle de minimizar/maximizar
    let usar_voz = false; // Controle para feedback de voz
    let nome = 'Usuário'; // Nome do usuário (global)
    let consecutive_wins = 0;
    let consecutive_losses = 0;
    let usar_rsi = false; // Variável para controle do filtro RSI
    let periodo_rsi = 14; // Período padrão do RSI
    let estrategia_selecionada = 'mhi'; // Estratégia padrão ('mhi' ou 'pro')
    let timeframe_selecionado_segundos = 60; // Timeframe padrão M1 (60 segundos)

    // --- Funções da API Wrapper ---

    async function apiFetch(endpoint, method = 'GET', data = null, params = null) {
        const url = new URL(`${BASE_URL}${endpoint}`);
        if (params) {
            Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        }

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            // Comentado para reduzir verbosidade - Descomente se precisar depurar chamadas API
            // log(`API Call: ${method} ${url.pathname}${url.search}`, 'info');
            const response = await fetch(url.toString(), options);
            if (!response.ok) {
                const errorText = await response.text();
                log(`Erro na API ${response.status}: ${errorText}`, 'error');
                throw new Error(`Erro na API: ${response.status}`);
            }
            // Verifica se a resposta tem conteúdo antes de tentar parsear JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                 const responseData = await response.json();
                 // Comentado para reduzir verbosidade - Descomente se precisar depurar respostas API
                 // log(`API Response: ${JSON.stringify(responseData)}`, 'info');
                 return responseData;
            } else {
                 log(`API Response: (No JSON content)`, 'info');
                 return { success: true }; // Ou alguma resposta padrão para sucesso sem JSON
            }
        } catch (error) {
            log(`Erro de rede ou API: ${error.message}`, 'error');
            // Se for erro de conexão, pode ser que o servidor Python não esteja rodando
            if (error instanceof TypeError) { // Geralmente TypeError para falha de fetch
                log(`Falha ao conectar à API em ${BASE_URL}. Verifique se o servidor Python está rodando.`, 'error');
            }
            throw error; // Re-throw para que a função chamadora possa lidar
        }
    }

    // Funções espelhando a classe IQ_Option do Python
    async function apiConnect(email, senha) {
        try {
            const data = await apiFetch('/connect', 'POST', { email, senha });
            return { success: true, message: "success" }; // Assumindo que sucesso não retorna JSON específico na API original
        } catch (error) {
            // A função apiFetch já loga o erro, mas podemos adicionar contexto
            log(`Falha na conexão: ${error.message}`, 'error');
            // Tenta pegar a mensagem de erro específica, se disponível
             try {
                 // Se o erro original foi de resposta não-OK, pode ter uma mensagem no corpo
                 if (error.message.includes("Erro na API")) {
                     // Não temos acesso direto ao corpo do erro aqui, apiFetch já logou.
                     // Podemos retornar uma mensagem genérica ou específica baseada no status code se o capturarmos
                 }
             } catch (parseError) {
                 // Ignore erros ao tentar analisar a mensagem de erro
             }
             return { success: false, message: error.message || "Erro de conexão" };
        }
    }

    async function apiChangeBalance(account_type) {
        try {
            await apiFetch('/change_balance', 'POST', { account_type });
            return true;
        } catch (error) {
            return false;
        }
    }

    async function apiGetServerTimestamp() {
        try {
            const data = await apiFetch('/get_server_timestamp');
            // A API Python retorna { timestamp: ... }, então pegamos esse valor
            return data.timestamp || Math.floor(Date.now() / 1000);
        } catch (error) {
            return Math.floor(Date.now() / 1000);
        }
    }

    async function apiGetAllProfit() {
        try {
            return await apiFetch('/get_all_profit');
        } catch (error) {
            return {};
        }
    }

    async function apiGetAllOpenTime() {
        try {
            return await apiFetch('/get_all_open_time');
        } catch (error) {
            return { binary: {}, turbo: {}, digital: {} };
        }
    }

     async function apiGetDigitalPayout(par) {
        try {
            const data = await apiFetch('/get_digital_payout', 'GET', null, { par });
            return data.payout || 0;
        } catch (error) {
            return 0;
        }
    }

    async function apiGetCandles(ativo, timeframe, qnt_velas, timestamp) {
        try {
            return await apiFetch('/get_candles', 'GET', null, { ativo, timeframe, qnt_velas, timestamp });
        } catch (error) {
            return [];
        }
    }

    async function apiBuyDigitalSpotV2(ativo, entrada, direcao, exp) {
        try {
            const data = await apiFetch('/buy_digital', 'POST', { ativo, entrada, direcao, exp });
            return { success: data.success || false, id: data.id || 'error' };
        } catch (error) {
            return { success: false, id: 'error' };
        }
    }

    async function apiBuy(entrada, ativo, direcao, exp) {
         try {
            const data = await apiFetch('/buy', 'POST', { entrada, ativo, direcao, exp });
            return { success: data.success || false, id: data.id || 'error' };
        } catch (error) {
            return { success: false, id: 'error' };
        }
    }

    // check_win não é usado diretamente no Python, usa-se diferença de saldo
    // async function apiCheckWinDigitalV2(id) { ... }
    // async function apiCheckWinV4(id) { ... }

    async function apiGetProfileAsync() {
        try {
            return await apiFetch('/get_profile');
        } catch (error) {
            return { currency_char: '$', name: 'Usuario' };
        }
    }

    async function apiGetBalance() {
        try {
            const data = await apiFetch('/get_balance');
            return data.balance || 0;
        } catch (error) {
            return 0; // Retornar 0 em caso de erro pode ser problemático para stops
        }
    }

     // Função para buscar ativos (não presente no original, mas útil)
     async function apiGetActives() {
        try {
            const data = await apiFetch('/get_actives');
            return data || {};
        } catch (error) {
            log("Erro ao buscar lista de ativos da API.", 'error');
            return {};
        }
    }

    // --- Funções Auxiliares (Tradução do Python) ---

    function formatCurrency(value) {
        // Verifica se o valor é um número válido
        if (typeof value !== 'number' || isNaN(value)) {
            log(`Erro: Tentativa de formatar valor não numérico: ${value}`, 'warning');
            return `${cifrao}---`; // Retorna um placeholder
        }
        return `${cifrao}${value.toFixed(2)}`;
    }

    // --- Função de Fala (Text-to-Speech) usando ElevenLabs ---
    async function speak(text) {
        if (!usar_voz || !ELEVENLABS_API_KEY) {
            // log('ElevenLabs: Voz desativada ou chave API não configurada.', 'warning');
            return;
        }

        // Cancela áudios anteriores (se houver uma maneira de gerenciar isso)
        // Com a API, cada chamada é independente, então cancelar a API do navegador não adianta.
        // Poderíamos armazenar o objeto Audio atual e pará-lo, mas pode ser complexo.

        const url = `https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}`;
        const headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
        };
        const data = {
            text: text,
            model_id: "eleven_multilingual_v2", // Modelo recomendado para Português
            voice_settings: {
                stability: 0.5,
                similarity_boost: 0.75,
                // style: 0.3, // Descomente para testar exagero de estilo
                // use_speaker_boost: true // Descomente para testar boost
            }
        };

        try {
            log(`ElevenLabs: Solicitando fala para: "${text}"`, 'info'); // Adicionado log para confirmar chamada
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                let errorDetails = response.statusText;
                try {
                     const errorData = await response.json();
                     errorDetails = errorData.detail ? (typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)) : errorDetails;
                } catch (e) {
                    // Ignora se o corpo do erro não for JSON
                }
                log(`Erro na API ElevenLabs (${response.status}): ${errorDetails}`, 'error');
                return;
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            log(`ElevenLabs: Áudio recebido, tocando...`, 'info'); // Adicionado log antes de tocar
            
            audio.play().catch(e => log(`Erro ao tocar áudio ElevenLabs: ${e.message}`, 'error'));
            
            // Limpa a URL do Blob após o áudio terminar de tocar para liberar memória
            audio.onended = () => {
                log(`ElevenLabs: Áudio finalizado.`, 'info'); // Adicionado log no fim
                URL.revokeObjectURL(audioUrl);
            };
            // Adiciona tratamento de erro para o play()
             audio.onerror = (e) => {
                 log(`Erro no objeto Audio do ElevenLabs: ${e.target.error.message}`, 'error');
                 URL.revokeObjectURL(audioUrl); // Limpa mesmo em caso de erro
             };


        } catch (error) {
            log(`Erro ao chamar API ElevenLabs: ${error.message}`, 'error');
        }
    }

    // Remove a necessidade de carregar vozes do navegador
    // if (typeof speechSynthesis !== 'undefined' && speechSynthesis.onvoiceschanged !== undefined) {
    //     speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
    // }

    async function checkStop() {
        if (!conectado || !stop) return; // Só checa se estiver conectado e rodando

        try {
            const saldo_atual = await apiGetBalance();
            if (saldo_atual === 0 && saldo_inicial !== 0) { // Evita stop loss imediato se falhar ao pegar saldo inicial
                 log(`Não foi possível obter o saldo atual para verificar stops. Tentando novamente...`, 'warning');
                 return; // Tenta novamente na próxima verificação
            }
            
            // Log detalhado para depuração
            // log(`CheckStop: Saldo Atual=${formatCurrency(saldo_atual)}, Saldo Inicial=${formatCurrency(saldo_inicial)}, StopWin=${formatCurrency(stop_win)}, StopLoss=${formatCurrency(stop_loss)}`, 'info');

            updateStatus(`Saldo: ${formatCurrency(saldo_atual)} | Lucro: ${formatCurrency(lucro_total)}`);

            // Stop Loss
            if (saldo_atual <= saldo_inicial - stop_loss) {
                log(`CheckStop: Stop Loss condition met (${formatCurrency(saldo_atual)} <= ${formatCurrency(saldo_inicial)} - ${formatCurrency(stop_loss)})`, 'error'); // Log antes de parar
                stop = false;
                log('#########################', 'error');
                log(`STOP LOSS BATIDO ${formatCurrency(saldo_inicial - saldo_atual)}`, 'error');
                log(`SALDO INICIAL: ${formatCurrency(saldo_inicial)}`, 'error');
                log(`SALDO ATUAL: ${formatCurrency(saldo_atual)}`, 'error');
                log('#########################', 'error');
                usar_voz = document.getElementById('iqbot-usar-voz').checked;
                speak("Stop Loss atingido!");
                stopBot(); // Para os loops
            }

            // Stop Win
            if (saldo_atual >= saldo_inicial + stop_win) {
                log(`CheckStop: Stop Win condition met (${formatCurrency(saldo_atual)} >= ${formatCurrency(saldo_inicial)} + ${formatCurrency(stop_win)})`, 'success'); // Log antes de parar
                stop = false;
                log('#########################', 'success');
                log(`STOP WIN BATIDO ${formatCurrency(saldo_atual - saldo_inicial)}`, 'success');
                log(`SALDO INICIAL: ${formatCurrency(saldo_inicial)}`, 'success');
                log(`SALDO ATUAL: ${formatCurrency(saldo_atual)}`, 'success');
                log('#########################', 'success');
                usar_voz = document.getElementById('iqbot-usar-voz').checked;
                speak("Stop Win atingido!");
                stopBot(); // Para os loops
            }
        } catch (error) {
            log(`Erro ao verificar stops: ${error.message}`, 'error');
        }
    }

    async function payout(par) {
        // Esta função no Python depende de dados que podem não estar sempre atualizados
        // via chamadas individuais. A API /get_actives pode ser mais adequada se retornar payouts.
        // Por simplicidade, vamos focar no payout digital que é usado na MHI automática.
        // A API web pode precisar ser ajustada para fornecer payouts de forma mais confiável.
        try {
            // ---> REVERSÃO: Remove a lógica de tratar sufixos <---
            // let assetForPayoutCheck = par;
            // if (par && par.endsWith('-op')) { 
            //     assetForPayoutCheck = par.replace('-op', ''); 
            //     log(`Payout: Verificando payout para ${par} usando o ativo base ${assetForPayoutCheck}`, 'info');
            // }
            // const digital_payout = await apiGetDigitalPayout(assetForPayoutCheck); // Usa o ativo ajustado
            
            // ---> Linha Original Restaurada <---
            const digital_payout = await apiGetDigitalPayout(par); // Passa o parâmetro original diretamente

            // Simplificando: retornando apenas o digital por enquanto
            return { digital: digital_payout, binary: 0, turbo: 0 }; // Adapte se precisar dos outros
        } catch (error) {
            log(`Erro ao obter payout para ${par}: ${error.message}`, 'error');
            return { digital: 0, binary: 0, turbo: 0 };
        }
    }

    async function compra(ativo, valor_entrada_base, direcao, exp, tipo_operacao) {
        if (operacao_em_andamento) {
            log('Tentativa de iniciar nova operação enquanto uma já está em andamento.', 'warning');
            return;
        }
        if (!stop) {
            log('Operação bloqueada: Stop Loss/Win atingido.', 'warning');
            return;
        }

        operacao_em_andamento = true;
        log(`Iniciando operação: ${ativo} ${direcao} ${formatCurrency(valor_entrada_base)} Exp: ${exp}m Tipo: ${tipo_operacao}`, 'info');

        let entrada_atual = valor_entrada_base;
        let valor_soros_op = 0; // Controla o valor do soros para esta sequência

        // Lógica Soros para definir valor de entrada inicial
        if (usar_soros) {
            if (nivel_soros === 0) {
                entrada_atual = valor_entrada_base;
                valor_soros_op = 0;
            } else if (nivel_soros >= 1 && valor_soros > 0 && nivel_soros <= niveis_soros) {
                entrada_atual = valor_entrada_base + valor_soros; // Usa o lucro acumulado
                valor_soros_op = valor_soros; // Guarda quanto do lucro está sendo reinvestido
                log(`Soros Nível ${nivel_soros}: Entrada = Base (${formatCurrency(valor_entrada_base)}) + Lucro Anterior (${formatCurrency(valor_soros)}) = ${formatCurrency(entrada_atual)}`, 'info');
            } else { // Nível de soros excedido ou sem lucro anterior
                log(`Soros: Nível ${nivel_soros} inválido ou sem lucro acumulado. Voltando à entrada base.`, 'info');
                entrada_atual = valor_entrada_base;
                valor_soros_op = 0;
                nivel_soros = 0; // Reseta o nível
                valor_soros = 0;   // Reseta o lucro acumulado para soros
            }
        } else {
             entrada_atual = valor_entrada_base; // Sem soros, usa entrada base
        }

        // ... (declarações de variáveis em compra)
        const progressIndicator = document.getElementById('iqbot-progress-indicator');
        const progressText = document.getElementById('iqbot-progress-text');
        const progressCircle = progressIndicator ? progressIndicator.querySelector('.iqbot-progress-circle') : null;

        try {
            for (let i = 0; i <= martingale; i++) {
                if (!stop) {
                    log(`Martingale ${i} cancelado: Stop Loss/Win atingido.`, 'warning');
                    break;
                }

                const saldo_anterior = await apiGetBalance();
                const tempo_inicio_operacao_ts = await apiGetServerTimestamp();
                const tempo_expiracao_ts = tempo_inicio_operacao_ts + exp * 60; // Exp em segundos
                const tempo_expiracao = new Date(tempo_expiracao_ts * 1000);
                const total_duration_ms = exp * 60 * 1000;

                log(`Saldo antes: ${formatCurrency(saldo_anterior)}`, 'info');
                log(`Início: ${new Date(tempo_inicio_operacao_ts * 1000).toLocaleTimeString()} | Expiração: ${tempo_expiracao.toLocaleTimeString()}`, 'info');

                // MOSTRAR e RESETAR Indicador de Progresso
                if (progressIndicator && progressText && progressCircle) {
                    progressText.textContent = `00:${String(exp*60).padStart(2, '0')}`; // Tempo inicial total
                    progressCircle.style.setProperty('--progress-angle', '0deg'); // Reseta ângulo
                    progressIndicator.style.display = 'flex'; // Mostra o indicador
                }

                let check, id;
                if (i > 0) { // Se for martingale, recalcula entrada
                   entrada_atual = round(entrada_atual * fator_mg, 2);
                   log(`Martingale ${i}: Nova entrada = ${formatCurrency(entrada_atual)}`, 'info');
                }

                log(`${i === 0 ? 'Abrindo Ordem' : `Abrindo Gale ${i}`}: ${ativo} ${direcao} ${formatCurrency(entrada_atual)} Exp: ${exp}m`, 'info');

                if (tipo_operacao === 'digital') {
                    ({ success: check, id } = await apiBuyDigitalSpotV2(ativo, entrada_atual, direcao, exp));
                } else { // binary
                    ({ success: check, id } = await apiBuy(entrada_atual, ativo, direcao, exp));
                }

                if (check) {
                    log(`Ordem ${id} aberta com sucesso. Aguardando resultado...`, 'info');

                    const checkResultPromise = new Promise(async (resolve) => {
                        const delay = tempo_expiracao.getTime() - Date.now() + 5000; // 5 segundos de margem

                        let countdownInterval = setInterval(async () => {
                            const now_ts = await apiGetServerTimestamp();
                            const remaining_seconds = Math.max(0, Math.floor(tempo_expiracao_ts - now_ts));
                            updateStatus(`Aguardando resultado... ${remaining_seconds}s`);

                            // --- ATUALIZAÇÃO INDICADOR DE PROGRESSO ---
                            if (progressIndicator && progressText && progressCircle) {
                                const remaining_ms = Math.max(0, tempo_expiracao.getTime() - Date.now());
                                const elapsed_ms = total_duration_ms - remaining_ms;
                                const progress_percentage = Math.min(1, elapsed_ms / total_duration_ms);
                                const progress_angle = progress_percentage * 360;
                                
                                // Formata tempo 00:SS
                                const display_seconds = Math.floor(remaining_ms / 1000);
                                const formatted_time = `00:${String(display_seconds).padStart(2, '0')}`;
                                progressText.textContent = formatted_time;
                                
                                // Atualiza CSS
                                progressCircle.style.setProperty('--progress-angle', `${progress_angle}deg`);
                            }
                            // --- FIM ATUALIZAÇÃO INDICADOR ---

                            if (remaining_seconds === 0) clearInterval(countdownInterval);
                        }, 1000);

                        setTimeout(async () => {
                            clearInterval(countdownInterval);
                            log(`Verificando resultado da ordem ${id} (Exp: ${tempo_expiracao.toLocaleTimeString()})`, 'info');
                            try {
                                const saldo_atual = await apiGetBalance();
                                const resultado = round(saldo_atual - saldo_anterior, 2);
                                lucro_total += resultado;

                                log(`Saldo depois: ${formatCurrency(saldo_atual)} | Resultado Op: ${formatCurrency(resultado)}`, 'info');

                                if (resultado > 0) {
                                    log(`Resultado: WIN ${i > 0 ? `(Gale ${i})` : ''} | Lucro: ${formatCurrency(resultado)} | Lucro Total: ${formatCurrency(lucro_total)}`, 'success');
                                    if (usar_soros) {
                                         valor_soros += resultado; // Acumula lucro para próximo nível Soros
                                         nivel_soros++;
                                         log(`Soros: Lucro acumulado ${formatCurrency(valor_soros)}. Próximo nível: ${nivel_soros}`, 'info');
                                         if (nivel_soros > niveis_soros) {
                                              log(`Soros: Nível máximo ${niveis_soros} atingido. Resetando.`, 'info');
                                              valor_soros = 0;
                                              nivel_soros = 0;
                                         }
                                    }
                                    // Removido: Falas condicionais de Win
                                    // consecutive_wins++; // A contagem ainda pode ser útil, manter?
                                    // consecutive_losses = 0;
                                    // speak("Frase de Win Simples"); // Simplificar ou remover totalmente para teste
                                    resolve({ win: true }); // Indica vitória para sair do loop do martingale
                                    
                                    // Falas de Win APÓS resolve()
                                    consecutive_wins++;
                                    consecutive_losses = 0;
                                    if (consecutive_wins >= 3) {
                                        speak("Está na hora de parar, né? Acertamos muito já.");
                                    } else {
                                        const winPhrases = [
                                            "Minha análise estava correta!",
                                            "Essa foi muito fácil!",
                                            "WIN! Boa! Lucro no bolso."
                                            // Adicione mais frases se quiser
                                        ];
                                        speak(winPhrases[Math.floor(Math.random() * winPhrases.length)]);
                                    }
                                } else if (resultado === 0) {
                                    log(`Resultado: EMPATE ${i > 0 ? `(Gale ${i})` : ''} | Lucro: ${formatCurrency(resultado)} | Lucro Total: ${formatCurrency(lucro_total)}`, 'warning');
                                     if (usar_soros) {
                                        log(`Soros: Empate, mantendo nível ${nivel_soros} e lucro acumulado ${formatCurrency(valor_soros)}.`, 'info');
                                        // Mantém valor_soros e nivel_soros para tentar novamente com o mesmo valor base + lucro
                                    }
                                    // Não resolve como win, continua para martingale se houver
                                     if (i < martingale) {
                                        resolve({ win: false }); // Continua martingale
                                    } else {
                                        log('Empate no último nível de martingale.', 'warning');
                                        resolve({ win: false }); // Termina como 'loss' para fins de soros/reset
                                    }

                                } else { // Loss
                                    log(`Resultado: LOSS ${i > 0 ? `(Gale ${i})` : ''} | Prejuízo: ${formatCurrency(resultado)} | Lucro Total: ${formatCurrency(lucro_total)}`, 'error');
                                     if (usar_soros) {
                                        log(`Soros: Loss, resetando nível e lucro acumulado.`, 'info');
                                        valor_soros = 0;
                                        nivel_soros = 0;
                                    }
                                    // Verifica se ainda há gales a tentar
                                    if (martingale > 0 && i < martingale) {
                                        resolve({ win: false }); // Continua martingale
                                        // Fala de Loss para martingale (opcional, pode adicionar aqui se quiser)
                                    } else {
                                        // Loss final (sem mais gales ou sem martingale)
                                        if (i > 0) {
                                             log('Loss no último nível de martingale.', 'error');
                                        }
                                        resolve({ win: false }); // Termina como loss

                                        // Falas de Loss APÓS resolve()
                                        consecutive_losses++;
                                        consecutive_wins = 0;
                                        if (consecutive_losses >= 3) {
                                            speak("O mercado não está muito bom não, vamos parar...");
                                        } else {
                                            const lossPhrases = [
                                                "O padrão mudou bem nesse momento.",
                                                "LOSS... Está muito volátil hoje.",
                                                `Essa paridade não está respeitando, ${nome}.`,
                                                "Hum, essa não deu."
                                                // Adicione mais frases se quiser
                                            ];
                                            speak(lossPhrases[Math.floor(Math.random() * lossPhrases.length)]);
                                        }
                                    }
                                }
                                await checkStop(); // Verifica stops após cada operação/gale

                            } catch (err) {
                                log(`Erro ao verificar resultado da ordem ${id}: ${err.message}`, 'error');
                                if (usar_soros) { // Reseta soros em caso de erro na verificação
                                    log(`Soros: Resetando devido a erro na verificação.`, 'error');
                                    valor_soros = 0;
                                    nivel_soros = 0;
                                }
                                resolve({ win: false }); // Assume loss em caso de erro
                            }

                        }, Math.max(0, delay)); // Garante que o delay não seja negativo
                    });

                    const result = await checkResultPromise;
                    if (result.win) {
                        break; // Sai do loop do martingale em caso de WIN
                    }
                    // Se foi loss ou empate, continua para o próximo gale (o loop for continua)

                } else {
                    log(`Erro ao abrir ordem ${i > 0 ? `(Gale ${i})` : ''}: ${id}`, 'error');
                     if (usar_soros) { // Reseta soros se falhar ao abrir ordem
                        log(`Soros: Resetando devido a erro ao abrir ordem.`, 'error');
                        valor_soros = 0;
                        nivel_soros = 0;
                    }
                    // Se falhou em abrir a ordem, não adianta tentar gale, sai do loop
                    break;
                }
            } // Fim do loop for (martingale)
        } catch (error) {
             log(`Erro inesperado durante o ciclo de compra/martingale: ${error.message}`, 'error');
             if (usar_soros) {
                 log(`Soros: Resetando devido a erro inesperado.`, 'error');
                 valor_soros = 0;
                 nivel_soros = 0;
             }
             // Esconde o indicador em caso de erro
             if (progressIndicator) {
                progressIndicator.style.display = 'none';
             }
        } finally {
            operacao_em_andamento = false;
             updateStatus('Pronto.'); // Atualiza status final
            log('Tentativa de operação finalizada.', 'info');
             await checkStop(); // Última verificação de stop após a conclusão do ciclo
            // Garante que o indicador está escondido ao final de tudo
            if (progressIndicator) {
                progressIndicator.style.display = 'none';
            }
        }
    }


    function medias(velas) {
        if (!velas || velas.length < velas_medias) return null; // Não há velas suficientes

        const velasParaMedia = velas.slice(-velas_medias); // Pega as últimas X velas
        let soma = 0;
        for (const vela of velasParaMedia) {
            // Verifica se 'close' existe e é um número
            if (typeof vela.close !== 'number') {
                log('Erro: Vela inválida encontrada na análise de médias.', 'error');
                console.log(vela); // Loga a vela problemática
                return null; // Retorna null para indicar erro
            }
            soma += vela.close;
        }
        const media = soma / velas_medias;
        const ultimaVela = velas[velas.length - 1];

         // Verifica se 'close' da última vela existe e é um número
        if (typeof ultimaVela.close !== 'number') {
             log('Erro: Última vela inválida na análise de médias.', 'error');
             console.log(ultimaVela);
             return null;
        }

        log(`Média(${velas_medias}): ${media.toFixed(5)} | Último Fechamento: ${ultimaVela.close.toFixed(5)}`, 'info');
        return media > ultimaVela.close ? 'put' : 'call';
    }

    // Função para calcular RSI (Índice de Força Relativa)
    function calcularRSI(velas, periodo = 14) {
        if (!velas || velas.length < periodo + 1) {
            log('RSI: Velas insuficientes para cálculo.', 'warning');
            return 50; // Retorna valor neutro
        }

        const closes = velas.map(v => v.close);
        let gains = 0;
        let losses = 0;

        // Calcula a primeira média de ganhos/perdas
        for (let i = 1; i <= periodo; i++) {
            const difference = closes[i] - closes[i - 1];
            if (difference >= 0) {
                gains += difference;
            } else {
                losses += Math.abs(difference);
            }
        }

        let avgGain = gains / periodo;
        let avgLoss = losses / periodo;

        // Suaviza as médias para o restante dos dados
        for (let i = periodo + 1; i < closes.length; i++) {
            const difference = closes[i] - closes[i - 1];
            let currentGain = 0;
            let currentLoss = 0;
            if (difference >= 0) {
                currentGain = difference;
            } else {
                currentLoss = Math.abs(difference);
            }
            avgGain = (avgGain * (periodo - 1) + currentGain) / periodo;
            avgLoss = (avgLoss * (periodo - 1) + currentLoss) / periodo;
        }

        if (avgLoss === 0) {
            return 100; // Evita divisão por zero, RSI máximo
        }

        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));
        
        // log(`RSI(${periodo}) calculado: ${rsi.toFixed(2)}`, 'info'); // Log para depuração
        return rsi;
    }

    // Função para analisar padrões de candlestick (VERSÃO ANTIGA RESTAURADA)
    function analisarPadraoCandlestickJS(vela, vela_anterior) { // Apenas 2 velas
        if (!vela || !vela_anterior) return null;

        // Certifica que temos os dados necessários
        const requiredKeys = ['open', 'close', 'min', 'max'];
        if (!requiredKeys.every(k => typeof vela[k] === 'number') || 
            !requiredKeys.every(k => typeof vela_anterior[k] === 'number')) {
            log('Padrão CStick: Dados de vela inválidos.', 'warning');
            return null;
        }

        const corpo = Math.abs(vela.close - vela.open);
        const sombra_superior = vela.max - Math.max(vela.open, vela.close);
        const sombra_inferior = Math.min(vela.open, vela.close) - vela.min;
        const tendencia_anterior = vela_anterior.close > vela_anterior.open ? 'alta' : 'baixa';
        const direcao_atual = vela.close > vela.open ? 'alta' : 'baixa';

        // --- Lógica de Padrões (Adaptada do Python, RETORNANDO apenas o resultado) ---

        // REVERSÃO DE ALTA (Pinbar de baixa / Sombra superior longa)
        if (sombra_superior > corpo * 1.5 && tendencia_anterior === 'alta') {
            // log('⭐ Reversão de Alta (Pinbar) identificada', 'info');
            return { direcao: 'put', nome: '⭐ Reversão de Alta (Pinbar)' };
        }

        // ESTRELA CADENTE
        if (sombra_superior > corpo * 1.5 && sombra_inferior < corpo * 0.5 && tendencia_anterior === 'alta') {
            // log('⭐ Estrela Cadente identificada', 'info');
            return { direcao: 'put', nome: '⭐ Estrela Cadente' };
        }

        // MARTELO
        if (sombra_inferior > corpo * 1.5 && sombra_superior < corpo * 0.5 && tendencia_anterior === 'baixa') {
            // log('🔨 Martelo identificado', 'info');
            return { direcao: 'call', nome: '🔨 Martelo' };
        }

        // REVERSÃO DE BAIXA (Pinbar de alta / Sombra inferior longa)
        if (sombra_inferior > corpo * 1.5 && tendencia_anterior === 'baixa') {
            // log('🔨 Reversão de Baixa (Pinbar) identificada', 'info');
            return { direcao: 'call', nome: '🔨 Reversão de Baixa (Pinbar)' };
        }

        // CONTINUAÇÃO DE ALTA (Vela de alta com pouca sombra superior)
        if (direcao_atual === 'alta' && corpo > sombra_superior * 1.5) { 
            // log('🟢 Continuação de Alta identificada', 'info');
            return { direcao: 'call', nome: '🟢 Continuação de Alta' };
        }

        // CONTINUAÇÃO DE BAIXA (Vela de baixa com pouca sombra inferior)
        if (direcao_atual === 'baixa' && corpo > sombra_inferior * 1.5) { 
            // log('🔴 Continuação de Baixa identificada', 'info');
            return { direcao: 'put', nome: '🔴 Continuação de Baixa' };
        }

        // Se nenhum padrão foi identificado
        return null;
    }

    // async function estrategiaMhi() { ... } // Função seguinte para referência de localização

    // --- Nova Estratégia: PRO Adaptada ---
    async function estrategiaProAdaptada() {
        if (operacao_em_andamento || !stop) {
            if (!stop) { /* log('PRO Adaptada Skip: stop=false', 'warning'); */ } // Log menos verboso
            return;
        }

        try {
            const timestamp = await apiGetServerTimestamp();
            const agora = new Date(timestamp * 1000);
            const segundos = agora.getSeconds();

            // Gatilho de tempo (final do minuto M1)
            if (segundos === 59) {
                if (operacao_em_andamento) {
                     log('PRO Adaptada: Horário de entrada, mas operação em andamento.', 'warning');
                     return;
                }

                log(`--- [${agora.toLocaleTimeString()}] Iniciando análise PRO Adaptada ---`, 'info');
                let ativo_final = ativo;
                let tipo_final = tipo;

                // Seleção automática de tipo (Digital/Binária)
                if (tipo === 'automatico') {
                    log(`Modo automático: Verificando payouts para ${ativo_final}...`, 'info');
                    const payouts = await payout(ativo_final);
                    if (payouts.digital > 0) { // Simplificado: prioriza digital
                        log(`Payout Digital: ${payouts.digital}%. Usando Digital.`, 'info');
                        tipo_final = 'digital';
                    } else {
                         log(`Payouts indisponíveis ou zero para ${ativo_final}. Abortando operação.`, 'error');
                         await sleep(2000);
                         return;
                    }
                }

                const timeframe = 60; // M1
                // Qtd de velas: Suficiente para RSI (ex: 15 se periodo=14) e padrões (2-3)
                const velas_rsi = usar_rsi ? periodo_rsi + 1 : 0;
                const velas_media = analise_medias ? velas_medias + 1 : 0;
                // ---> AJUSTE AQUI: Garante que busca pelo menos 3 velas para padrões multi-candle
                // const qnt_velas_necessarias = Math.max(3, velas_rsi, velas_media); // Comentado
                // Ajuste para Versão Antiga: Mínimo de 2 velas é suficiente
                const qnt_velas_necessarias = Math.max(2, velas_rsi, velas_media); // Descomentado
                log(`Buscando ${qnt_velas_necessarias} velas para ${ativo_final} (Timeframe: ${timeframe}s)...`, 'info');
                const velas = await apiGetCandles(ativo_final, timeframe, qnt_velas_necessarias, timestamp); // Passa o timeframe selecionado

                // ---> CORREÇÃO: Verifica se o número de velas recebidas é menor que o NÚMERO SOLICITADO <---
                // if (!velas || velas.length < 3) { // Linha antiga com valor fixo 3
                if (!velas || velas.length < qnt_velas_necessarias) { // CORRIGIDO: Usa a variável
                    log(`Erro ou velas insuficientes (${velas ? velas.length : 0}/${qnt_velas_necessarias}) para ${ativo_final}.`, 'error'); // CORRIGIDO: Mostra o número solicitado
                    await sleep(2000);
                    return;
                }

                // ---> Pega as últimas velas necessárias (agora pode ser 2 ou mais) <---
                const velaAtual = velas[velas.length - 1];
                const velaAnterior = velas[velas.length - 2];
                // const velaAnterior2 = velas[velas.length - 3]; // Não é mais necessária para a versão restaurada
                
                // 1. Analisar Padrão de Candlestick (passando as 2 velas necessárias)
                const resultadoPadrao = analisarPadraoCandlestickJS(velaAtual, velaAnterior);
                let direcao = null;
                
                if (resultadoPadrao) {
                    log(`Padrão Identificado: ${resultadoPadrao.nome}`, 'info');
                    direcao = resultadoPadrao.direcao;
                    
                    // 2. Aplicar Filtros (se houver direção)
                    let filtro_abortou = false;
                    
                    // Filtro de Média Móvel
                    if (direcao && analise_medias) {
                         if (velas.length < velas_media + 1) {
                            log(`PRO Adaptada: Velas insuficientes para Média (${velas.length}/${velas_media + 1}). Filtro ignorado.`, 'warning');
                         } else {
                            const tendencia = medias(velas.slice(-(velas_media + 1))); // Pega velas suficientes para média
                            if (tendencia && direcao !== tendencia) {
                                log(`PRO Adaptada Abortada: Direção (${direcao}) contra tendência Média (${tendencia}).`, 'warning');
                                direcao = null;
                                filtro_abortou = true;
                            } else if (tendencia) {
                                log(`PRO Adaptada Confirmada: Tendência Média (${tendencia}) a favor.`, 'info');
                            }
                         }
                    }
                    
                    // Filtro RSI
                    if (direcao && usar_rsi && !filtro_abortou) {
                        // ---> CORREÇÃO: A verificação aqui estava errada <---
                        // if (velas.length < velas_rsi + 1) { // Condição anterior incorreta (ex: 15 < 15 + 1)
                        if (velas.length < velas_rsi) {      // CORRIGIDO: Compara com velas_rsi (que já é periodo+1)
                             log(`PRO Adaptada: Velas insuficientes para RSI (${velas.length}/${velas_rsi}). Filtro ignorado.`, 'warning'); // Log corrigido
                        } else {
                            const rsi_valor = calcularRSI(velas, periodo_rsi);
                            log(`PRO Adaptada: RSI(${periodo_rsi}) = ${rsi_valor.toFixed(2)}`, 'info');
                            
                            // ---> LÓGICA RSI MAIS RESTRITIVA <-----
                            if (direcao === 'call' && rsi_valor >= 65) { // CALL cancelado se RSI >= 65
                                log(`PRO Adaptada Abortada: CALL com RSI próximo a sobrecompra (${rsi_valor.toFixed(2)} >= 65).`, 'warning');
                                direcao = null;
                            } else if (direcao === 'put' && rsi_valor <= 35) { // PUT cancelado se RSI <= 35
                                log(`PRO Adaptada Abortada: PUT com RSI próximo a sobrevenda (${rsi_valor.toFixed(2)} <= 35).`, 'warning');
                                direcao = null;
                            } else {
                                 log(`PRO Adaptada Confirmada: RSI (${rsi_valor.toFixed(2)}) não contradiz (CALL < 65 ou PUT > 35).`, 'info');
                            }
                            // ---> FIM DA LÓGICA <-----
                        }
                    }
                }
                
                // 3. Executar Compra se houver direção válida após filtros
                if (direcao) {
                    log(`>>> INICIANDO COMPRA (PRO): ${ativo_final} | ${direcao} | ${formatCurrency(valor_entrada)} | Exp: 1m | Tipo: ${tipo_final}`, 'success');
                    // Adicionar fala de análise aqui?
                    // speak("Análise PRO indica entrada..."); // Exemplo, pode causar sobreposição
                    compra(ativo_final, valor_entrada, direcao, 1, tipo_final); // Expiração de 1 min para esta estratégia
                } else {
                    log('--- Análise PRO Adaptada concluída: Nenhuma entrada realizada (sem padrão ou filtro abortou) ---', 'info');
                }

                await sleep(1500); // Espera para não reanalisar imediatamente
            }
        } catch (error) {
             console.error("Erro detalhado na estrategiaProAdaptada:", error);
             log(`Erro CRÍTICO na Estratégia PRO Adaptada: ${error.message}.`, 'error');
             await sleep(5000);
        }
    }

    // --- Nova Estratégia: Cinco Velas Sequenciais ---
    async function estrategiaCincoVelas() {
        if (operacao_em_andamento || !stop) {
            if (!stop) { /* log('Cinco Velas Skip: stop=false', 'warning'); */ }
            return;
        }

        try {
            const timestamp = await apiGetServerTimestamp();
            const agora = new Date(timestamp * 1000);
            const segundos = agora.getSeconds();
            const timeframe = 60; // Estratégia M1

            // Gatilho de tempo (final do minuto M1 para analisar velas fechadas)
            if (segundos === 59) {
                if (operacao_em_andamento) {
                    log('Cinco Velas: Horário de entrada, mas operação em andamento.', 'warning');
                    return;
                }

                log(`--- [${agora.toLocaleTimeString()}] Iniciando análise Cinco Velas ---`, 'info');
                let ativo_final = ativo;
                let tipo_final = tipo;

                // Seleção automática de tipo (Digital/Binária) - Igual à PRO
                if (tipo === 'automatico') {
                    log(`Modo automático: Verificando payouts para ${ativo_final}...`, 'info');
                    const payouts = await payout(ativo_final);
                    if (payouts.digital > 0) { 
                        log(`Payout Digital: ${payouts.digital}%. Usando Digital.`, 'info');
                        tipo_final = 'digital';
                    } else {
                        log(`Payouts indisponíveis ou zero para ${ativo_final}. Abortando operação.`, 'error');
                        await sleep(2000);
                        return;
                    }
                }

                // Precisamos de 6 velas para analisar as 5 anteriores concluídas
                const qnt_velas = 6;
                log(`Buscando ${qnt_velas} velas para ${ativo_final} (Timeframe: ${timeframe}s)...`, 'info');
                const velas = await apiGetCandles(ativo_final, timeframe, qnt_velas, timestamp);

                if (!velas || velas.length < qnt_velas) {
                    log(`Erro ou velas insuficientes (${velas ? velas.length : 0}/${qnt_velas}) para ${ativo_final}.`, 'error');
                    await sleep(2000);
                    return;
                }

                // Analisa as 5 velas anteriores (índices length-2 a length-6)
                const ultimas_5_velas = velas.slice(velas.length - 6, velas.length - 1);
                let todas_verdes = true;
                let todas_vermelhas = true;

                for (const vela of ultimas_5_velas) {
                    if (vela.close >= vela.open) { // Se for verde ou doji
                        todas_vermelhas = false;
                    }
                    if (vela.close <= vela.open) { // Se for vermelha ou doji
                        todas_verdes = false;
                    }
                }

                let direcao = null;
                if (todas_verdes) {
                    log('🟢 Sequência de 5 velas verdes identificada.', 'info');
                    direcao = 'call';
                } else if (todas_vermelhas) {
                    log('🔴 Sequência de 5 velas vermelhas identificada.', 'info');
                    direcao = 'put';
                }

                // Executar Compra se uma sequência foi encontrada
                if (direcao) {
                    log(`>>> INICIANDO COMPRA (Cinco Velas): ${ativo_final} | ${direcao} | ${formatCurrency(valor_entrada)} | Exp: 1m | Tipo: ${tipo_final}`, 'success');
                    // A função compra lidará com a reentrada se Martingale (nível >= 1) estiver ativo globalmente
                    compra(ativo_final, valor_entrada, direcao, 1, tipo_final); // Expiração de 1 min
                } else {
                    log('--- Análise Cinco Velas concluída: Nenhuma sequência de 5 encontrada ---', 'info');
                }

                await sleep(1500); // Espera para não reanalisar imediatamente
            }
        } catch (error) {
             console.error("Erro detalhado na estrategiaCincoVelas:", error);
             log(`Erro CRÍTICO na Estratégia Cinco Velas: ${error.message}.`, 'error');
             await sleep(5000);
        }
    }

    // --- Funções da Interface Gráfica ---
    let uiContainer = null;
    let logContainer = null;
    let statusContainer = null;

    // Função auxiliar para adicionar estilos CSS -> REMOVIDA
    /*
    function addGlobalStyle(css) {
        const head = document.head || document.getElementsByTagName('head')[0];
        const style = document.createElement('style');
        style.type = 'text/css';
        style.appendChild(document.createTextNode(css));
        head.appendChild(style);
    }
    */

    function createUI() {
        if (document.getElementById('iqbot-console-ui')) {
             log('UI já existe.', 'warning');
             return;
        }

        // --- Estilos Globais Inspirados no Dashboard --- > CHAMADA REMOVIDA
        /*
        addGlobalStyle(`
            // ... todo o CSS que estava aqui ...
        `);
        */

        uiContainer = document.createElement('div');
        uiContainer.id = 'iqbot-console-ui';
        // ... (restante da função createUI) ...

        // Header com Título e Botão Minimizar
        const header = document.createElement('div');
        header.id = 'iqbot-header';

        const title = document.createElement('span');
        title.id = 'iqbot-title';
        title.textContent = 'TDF PRO BOT';
        header.appendChild(title);

        // --- Novo Span para Status no Header ---
        const headerStatusSpan = document.createElement('span');
        headerStatusSpan.id = 'iqbot-header-status';
        headerStatusSpan.textContent = 'Analisando...'; // Texto padrão
        header.appendChild(headerStatusSpan); // Adiciona ANTES do botão minimizar
        // --- Fim Novo Span ---

        const minimizeButton = document.createElement('button');
        minimizeButton.id = 'iqbot-minimize-btn';
        minimizeButton.textContent = '_';
        minimizeButton.onclick = toggleMinimize;
        header.appendChild(minimizeButton);

        uiContainer.appendChild(header);

        // Área de Conteúdo
        const contentArea = document.createElement('div');
        contentArea.id = 'iqbot-content-area';

        // --- Seção: Status e Conexão ---
        const statusSection = document.createElement('div');
        statusSection.className = 'iqbot-section';

        statusContainer = document.createElement('div');
        statusContainer.id = 'iqbot-status';
        statusSection.appendChild(statusContainer);
        // updateStatus('Desconectado'); // REMOVIDO: Não chama mais updateStatus aqui

        // Define estado inicial diretamente no HTML
        statusContainer.innerHTML = `
            <span class="status-dot offline"></span>
            <div class="status-text-container">
                <span class="status-main">DESCONECTADO</span>
                <span class="status-details"></span>
            </div>
        `;
        statusContainer.className = 'status-indicator'; // Garante a classe base

        // --- Novo Indicador Circular de Progresso ---
        const progressIndicator = document.createElement('div');
        progressIndicator.id = 'iqbot-progress-indicator';
        progressIndicator.style.display = 'none'; // Começa oculto
        progressIndicator.innerHTML = `
            <div class="iqbot-progress-circle">
                <span id="iqbot-progress-text">00:00</span>
            </div>
        `;
        statusSection.appendChild(progressIndicator); // Adiciona na seção de status
        // --- Fim Indicador ---

        statusSection.appendChild(createCheckboxGroup('Ativar Feedback por Voz?', 'iqbot-usar-voz', usar_voz, (e) => {
            // ... (lógica da voz) ...
        }));

        statusSection.appendChild(createInputGroup('Email', 'iqbot-email', 'email', email));
        statusSection.appendChild(createInputGroup('Senha', 'iqbot-senha', 'password', senha));

        statusSection.appendChild(createButton('Conectar', 'iqbot-connect-btn', connectBot));

        contentArea.appendChild(statusSection);
        // --- Fim Seção Status e Conexão ---

        // --- Seção: Configurações Gerais ---
        const configSection = document.createElement('div');
        configSection.className = 'iqbot-section';
        const configTitle = document.createElement('div');
        configTitle.className = 'iqbot-section-title';
        configTitle.textContent = 'Configurações Gerais';
        configSection.appendChild(configTitle);

        const configRow1 = document.createElement('div');
        configRow1.className = 'iqbot-flex-row'; // Linha flex para agrupar
        configRow1.appendChild(createSelectGroup('Conta:', 'iqbot-conta', conta, [{value: 'PRACTICE', text: 'Demo'}, {value: 'REAL', text: 'Real'}]));
        configRow1.appendChild(createSelectGroup('Ativo:', 'iqbot-ativo-select', ativo, []));
        configSection.appendChild(configRow1);

        const configRow2 = document.createElement('div');
        configRow2.className = 'iqbot-flex-row';
        const timeframeOptions = [
            { value: 60, text: 'M1' },
            { value: 300, text: 'M5' },
            { value: 900, text: 'M15' }
        ];
        configRow2.appendChild(createSelectGroup('Timeframe:', 'iqbot-timeframe', timeframe_selecionado_segundos, timeframeOptions, (e) => {
            // ... (lógica timeframe) ...
        }));
        configRow2.appendChild(createInputGroup('Entrada', 'iqbot-entrada', 'number', valor_entrada, null, null, 0.01));
        configSection.appendChild(configRow2);

        const configRow3 = document.createElement('div');
        configRow3.className = 'iqbot-flex-row';
        configRow3.appendChild(createInputGroup('Stop Win', 'iqbot-stopwin', 'number', stop_win, null, null, 0.01));
        configRow3.appendChild(createInputGroup('Stop Loss', 'iqbot-stoploss', 'number', stop_loss, null, null, 0.01));
        configSection.appendChild(configRow3);

        contentArea.appendChild(configSection);
        // --- Fim Seção Configurações Gerais ---

        // --- Seção: Gerenciamento e Filtros ---
        const managementSection = document.createElement('div');
        managementSection.className = 'iqbot-section';
        const managementTitle = document.createElement('div');
        managementTitle.className = 'iqbot-section-title';
        managementTitle.textContent = 'Gerenciamento e Filtros';
        managementSection.appendChild(managementTitle);

        // Opções MG e Soros lado a lado
        const optionsRow = document.createElement('div');
        optionsRow.className = 'iqbot-flex-row';
        
        // Container MG
        const mgContainer = document.createElement('div');
        mgContainer.className = 'iqbot-option-block'; // <-- Aplica a nova classe
        mgContainer.appendChild(createCheckboxGroup('Usar Martingale?', 'iqbot-usar-mg', usar_martingale, (e) => { /* ... */ }));
        const mgInputsContainer = document.createElement('div');
        mgInputsContainer.className = 'iqbot-flex-row'; 
        mgInputsContainer.appendChild(createInputGroup('Níveis MG', 'iqbot-mg-niveis', 'number', martingale, null, null, 1, !usar_martingale));
        mgInputsContainer.appendChild(createInputGroup('Fator', 'iqbot-mg-fator', 'number', fator_mg, null, null, 0.1, !usar_martingale)); 
        mgContainer.appendChild(mgInputsContainer);
        optionsRow.appendChild(mgContainer);

        // Container Soros
        const sorosContainer = document.createElement('div');
        sorosContainer.className = 'iqbot-option-block'; // <-- Aplica a nova classe
        sorosContainer.appendChild(createCheckboxGroup('Usar Soros?', 'iqbot-usar-soros', usar_soros, (e) => { /* ... */ }));
        sorosContainer.appendChild(createInputGroup('Níveis Soros', 'iqbot-soros-niveis', 'number', niveis_soros, null, null, 1, !usar_soros));
        optionsRow.appendChild(sorosContainer);
        managementSection.appendChild(optionsRow);

        // Filtros Média e RSI lado a lado
        const filtersRowContainer = document.createElement('div');
        filtersRowContainer.className = 'iqbot-flex-row';
        filtersRowContainer.style.marginTop = '15px'; // Espaço acima

        const filterContainer = document.createElement('div'); // Média
        filterContainer.className = 'iqbot-option-block'; // <-- Aplica a nova classe
        filterContainer.appendChild(createCheckboxGroup('Filtro Média?', 'iqbot-analise-medias', analise_medias, (e) => { /* ... */ }));
        filterContainer.appendChild(createInputGroup('Período', 'iqbot-velas-medias', 'number', velas_medias, null, null, 1, !analise_medias));
        filtersRowContainer.appendChild(filterContainer);

        const rsiContainer = document.createElement('div'); // RSI
        rsiContainer.className = 'iqbot-option-block'; // <-- Aplica a nova classe
        rsiContainer.appendChild(createCheckboxGroup('Filtro RSI?', 'iqbot-usar-rsi', usar_rsi, (e) => { /* ... */ }));
        rsiContainer.appendChild(createInputGroup('Período', 'iqbot-periodo-rsi', 'number', periodo_rsi, null, null, 1, !usar_rsi));
        filtersRowContainer.appendChild(rsiContainer);
        managementSection.appendChild(filtersRowContainer);

        contentArea.appendChild(managementSection);
        // --- Fim Seção Gerenciamento e Filtros ---

        // --- Seção: Seleção de Estratégia ---
        const strategySection = document.createElement('div');
        strategySection.className = 'iqbot-section';
        const strategyTitle = document.createElement('div');
        strategyTitle.className = 'iqbot-section-title';
        strategyTitle.textContent = 'Seleção de Estratégia';
        strategySection.appendChild(strategyTitle);

        const strategyOptionsContainer = document.createElement('div');
        strategyOptionsContainer.style.display = 'flex';
        strategyOptionsContainer.style.justifyContent = 'space-around';
        strategyOptionsContainer.style.marginTop = '10px';

        const strategies = {
            mhi: { 
                name: 'MHI Clássico', 
                premium: false,
                description: 'Busca reversão após padrão MHI em 3 velas.' 
            },
            pro: { 
                name: 'Tendência & Reversão PRO', 
                premium: true,
                description: 'Combina padrões de candle com filtros (Média/RSI).'
            },
            cinco_velas: { 
                name: 'Sequência de Velas', 
                premium: true,
                description: 'Opera a favor após 5 velas da mesma cor.' 
            }
        };

        Object.keys(strategies).forEach(key => {
            const stratInfo = strategies[key];
            const radioContainer = document.createElement('div');
            radioContainer.className = 'iqbot-radio-group'; // Usa nova classe
            // Adiciona um title (tooltip) com a descrição completa
            radioContainer.title = stratInfo.description; 

            const radioInput = document.createElement('input');
            radioInput.type = 'radio';
            radioInput.name = 'iqbot-strategy';
            radioInput.id = `iqbot-strategy-${key}`;
            radioInput.value = key;
            radioInput.checked = (estrategia_selecionada === key);
            radioInput.addEventListener('change', function() {
                estrategia_selecionada = this.value;
                log(`Estratégia selecionada: ${stratInfo.name}`, 'info');
            });

            const radioLabel = document.createElement('label');
            radioLabel.htmlFor = `iqbot-strategy-${key}`;
            radioLabel.textContent = stratInfo.name;

            // Adiciona indicador premium
            if (stratInfo.premium) {
                const premiumIcon = document.createElement('span');
                premiumIcon.className = 'premium-indicator';
                premiumIcon.textContent = '👑'; // Ícone de coroa
                radioLabel.appendChild(premiumIcon);
            }

            // Adiciona a descrição abaixo do label (visível)
            const descriptionSpan = document.createElement('span');
            descriptionSpan.textContent = stratInfo.description;
            descriptionSpan.style.display = 'block'; // Para ficar abaixo do label
            descriptionSpan.style.fontSize = '0.8em';
            descriptionSpan.style.color = '#aaa'; // Cor mais suave
            descriptionSpan.style.marginTop = '3px'; // Pequeno espaço

            radioContainer.appendChild(radioInput);
            radioContainer.appendChild(radioLabel);
            radioContainer.appendChild(descriptionSpan); // Adiciona descrição visível
            strategyOptionsContainer.appendChild(radioContainer);
        });

        strategySection.appendChild(strategyOptionsContainer);
        contentArea.appendChild(strategySection);
        // --- Fim Seção Seleção de Estratégia ---

        // --- Seção: Ações e Logs ---
        const actionSection = document.createElement('div');
        actionSection.className = 'iqbot-section';

        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'iqbot-button-group';
        // Botão Conectar foi movido para a seção de status
        buttonGroup.appendChild(createButton('Iniciar Bot', 'iqbot-start-btn', startBot, true));
        buttonGroup.appendChild(createButton('Parar Bot', 'iqbot-stop-btn', stopBot, true));
        buttonGroup.appendChild(createButton('Ocultar Logs', 'iqbot-toggle-logs-btn', toggleLogsVisibility, false));
        actionSection.appendChild(buttonGroup);

        logContainer = document.createElement('div');
        logContainer.id = 'iqbot-logs';
        actionSection.appendChild(logContainer);

        contentArea.appendChild(actionSection);
        // --- Fim Seção Ações e Logs ---

        uiContainer.appendChild(contentArea);
        document.body.appendChild(uiContainer);

        // Habilitar arrastar pelo header
        makeDraggable(uiContainer, header);

        // Popula o dropdown de ativos imediatamente após criar a UI
        populateActivesDropdown();

        log('Interface criada com novo design.', 'info');
    }

     // Modificada para usar placeholders e ícones, E ADICIONAR LABELS para numéricos
     function createInputGroup(label, id, type, value, onChange = null, icon = null, step = null, disabled = false) {
        const group = document.createElement('div');
        group.className = 'iqbot-input-group'; // Usa classe para estilo

        // Adiciona Label explicitamente SE NÃO for email ou senha (que usam placeholder)
        if (id !== 'iqbot-email' && id !== 'iqbot-senha' && type !== 'checkbox') {
            const lbl = document.createElement('label');
            lbl.htmlFor = id;
            lbl.textContent = label;
            group.appendChild(lbl);
        }

        const input = document.createElement('input');
        input.type = type === 'password' ? 'password' : type; // Mantém tipo original
        input.id = id;
        input.value = value;
        // Usa placeholder apenas para email e senha
        input.placeholder = (id === 'iqbot-email' || id === 'iqbot-senha') ? label : '';
        input.disabled = disabled;
        input.className = 'iqbot-input'; // Usa classe para estilo
        // Garante que nenhum listener do script interfira com a digitação/deleção
        input.addEventListener('keydown', (e) => {
            // Previne apenas se for uma tecla específica que QUEIRAMOS bloquear
            // No nosso caso, não queremos bloquear nada, então deixamos passar.
            // e.stopPropagation(); // Exemplo de como parar propagação se necessário
        });


        // Adiciona step se for number
        if (type === 'number' && step) input.step = step;

        // Handlers de mudança
         if (onChange) {
             input.onchange = onChange;
         } else if (id === 'iqbot-email') {
              input.onchange = (e) => email = e.target.value;
         } else if (id === 'iqbot-senha') {
              input.onchange = (e) => senha = e.target.value;
         } else if (id.startsWith('iqbot-')) { // Handlers padrão para estado global baseado no ID
             input.onchange = (e) => {
                 // Converte ID (ex: iqbot-stop-win) para nome de variável (ex: stop_win)
                 const key = id.replace('iqbot-', '').replace(/-/g, '_');
                 try {
                     if (type === 'number') window[key] = parseFloat(e.target.value);
                     else if (type === 'checkbox') window[key] = e.target.checked; // Embora checkbox não use essa fn agora
                     else window[key] = e.target.value;
                     // log(`${key} set to ${window[key]}`, 'info'); // Log pode ser verboso
                 } catch (err) {
                     console.error(`Erro ao definir variável ${key} a partir do input ${id}:`, err);
                 }
             };
         }

        group.appendChild(input);

        // Adiciona ícone se especificado
        if (icon) {
            const iconSpan = document.createElement('span');
            iconSpan.className = 'iqbot-input-icon';
            iconSpan.textContent = icon;
            group.appendChild(iconSpan);

             // Lógica para alternar visibilidade da senha
             if (type === 'password') {
                 iconSpan.classList.add('iqbot-password-toggle');
                 iconSpan.onclick = () => {
                     if (input.type === 'password') {
                         input.type = 'text';
                         iconSpan.textContent = '🙈'; // Ícone olho fechado
                     } else {
                         input.type = 'password';
                         iconSpan.textContent = '👁️'; // Ícone olho aberto
                     }
                 };
             }
        }

        return group;
    }

     // Modificado para usar classes
     function createSelectGroup(label, id, value, options, onChange = null) { // Adiciona parâmetro onChange
         const group = document.createElement('div');
         group.className = 'iqbot-select-group'; // Classe para estilo
         group.style.flexGrow = '1'; // Para ocupar espaço em flex containers

         const lbl = document.createElement('label');
         lbl.htmlFor = id;
         lbl.textContent = label;

         const select = document.createElement('select');
         select.id = id;
         select.value = value;
         options.forEach(opt => {
             const option = document.createElement('option');
             option.value = opt.value;
             option.textContent = opt.text;
             select.appendChild(option);
         });

         // Define o handler de mudança
         if (onChange) {
             select.onchange = onChange;
         } else if (id === 'iqbot-ativo-select') { // Handler específico para o select de ativo
            select.onchange = (e) => {
                ativo = e.target.value; // Atualiza a variável global 'ativo'
                if (ativo) { // Log apenas se um ativo real for selecionado
                    log(`Ativo selecionado: ${ativo}`, 'info');
                }
            };
         } else if (id === 'iqbot-conta') { // Mantém handler específico da conta se não houver genérico
             select.onchange = (e) => {
                 conta = e.target.value; // Atualiza a variável global 'conta'
                 log(`Conta selecionada: ${conta}`, 'info');
             };
         }

         group.appendChild(lbl);
         group.appendChild(select);
         return group;
    }

     // Modificado para usar classes
     function createCheckboxGroup(label, id, checked, onChange) {
        const group = document.createElement('div');
        group.className = 'iqbot-checkbox-group'; // Classe para estilo

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = id;
        input.checked = checked;
        input.style.marginRight = '8px'; // Espaço entre checkbox e label
        input.onchange = onChange;

        const lbl = document.createElement('label');
        lbl.htmlFor = id;
        lbl.textContent = label;

        group.appendChild(input);
        group.appendChild(lbl);
        return group;
    }

    // Modificado para usar classes e novo estilo
    function createButton(text, id, onClick, disabled = false) {
        const button = document.createElement('button');
        button.textContent = text;
        button.id = id;
        button.disabled = disabled;
        button.onclick = onClick;
        button.className = 'iqbot-button'; // Usa classe para estilo
        return button;
    }

     // Modificado para usar classes e novo estilo do log
     function log(message, type = 'info') {
        if (!logContainer) {
            console.log(`[${type.toUpperCase()}] ${message}`); // Fallback para console se UI não pronta
            return;
        }
        const p = document.createElement('p');
        const timestamp = new Date().toLocaleTimeString();
        p.textContent = `[${timestamp}] ${message}`;
        // Estilos aplicados via CSS global, mas a cor ainda é definida inline
        // para diferenciação fácil (poderia ser feito com classes)
        switch (type) {
            case 'error':   p.style.color = '#ff8a8a'; break;
            case 'success': p.style.color = '#8aff8a'; break;
            case 'warning': p.style.color = '#ffd700'; break;
            case 'info':
            default:        p.style.color = '#ccc'; break;
        }
        logContainer.appendChild(p);
        // Auto-scroll
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    function updateStatus(text) {
        if (statusContainer) {
            statusContainer.innerHTML = ''; // Limpa

            // 1. Determina a classe do ponto
            let dotClass = 'offline';
            const lowerText = text.toLowerCase();
            // Considera online se tiver conectado, rodando, parado ou mencionando saldo
            if (lowerText.includes('conectado') || lowerText.includes('rodando') || lowerText.includes('parado') || lowerText.includes('saldo:')) {
                dotClass = 'online';
            } else if (lowerText.includes('erro') || lowerText.includes('falha') || lowerText.includes('inválid') || lowerText.includes('desconectado')) {
                 dotClass = 'offline';
            } else if (lowerText.includes('conectando')) {
                dotClass = 'offline'; // Ou pode ser uma classe 'connecting' específica
            }

            const statusDot = document.createElement('span');
            statusDot.className = `status-dot ${dotClass}`;
            statusContainer.appendChild(statusDot);

            // 2. Tenta formatar a exibição baseada no conteúdo do texto
            // Regex simplificado para Saldo: ... | Lucro: ... (como na imagem)
            const saldoLucroRegex = /Saldo:\s*([R\$€£]?\s*-?\d+(?:[.,]\d+)?)\s*\|\s*Lucro:\s*([R\$€£]?\s*-?\d+(?:[.,]\d+)?)/i;
            // Regex para o status inicial: Conectado: Nome | Saldo Inicial: ...
            const conectadoNomeSaldoRegex = /Conectado:\s*(.+?)\s*\|\s*Saldo Inicial:\s*([R\$€£]?\s*-?\d+(?:[.,]\d+)?)/i;

            const saldoLucroMatch = text.match(saldoLucroRegex);
            const conectadoMatch = text.match(conectadoNomeSaldoRegex);

            const textContainer = document.createElement('div');
            textContainer.className = 'status-text-container'; // Classe para container do texto

            if (saldoLucroMatch) {
                // Formato Saldo | Lucro (durante operação)
                const saldoStr = saldoLucroMatch[1];
                const lucroStr = saldoLucroMatch[2];
                // Extrai valor numérico do lucro para aplicar cor
                const lucroValorMatch = lucroStr.match(/-?\d+(?:[.,]\d+)?/);
                const lucroValor = lucroValorMatch ? parseFloat(lucroValorMatch[0].replace(',', '.')) : 0;

                const details = document.createElement('span');
                details.className = 'status-details'; // Usa classe CSS para estilização
                details.innerHTML = `
                    <span class="status-label">Saldo:</span>
                    <span class="status-value status-saldo">${saldoStr}</span>
                    <span class="separator">|</span>
                    <span class="status-label">Lucro:</span>
                    <span class="status-value ${lucroValor > 0 ? 'positive' : (lucroValor < 0 ? 'negative' : 'neutral')}">${lucroStr}</span>
                `;
                textContainer.appendChild(details);

            } else if (conectadoMatch) {
                 // Formato Conectado: Nome | Saldo Inicial (após conexão)
                const nomeUsuario = conectadoMatch[1];
                const saldoInicialStr = conectadoMatch[2];

                const main = document.createElement('span');
                main.className = 'status-main';
                main.textContent = `CONECTADO`; // Status principal
                textContainer.appendChild(main);

                const details = document.createElement('span');
                details.className = 'status-details';
                details.innerHTML = `
                    <span class="status-user">${nomeUsuario}</span>
                    <span class="separator">|</span>
                    <span class="status-label">Saldo Inicial:</span>
                    <span class="status-value status-saldo">${saldoInicialStr}</span>
                `;
                textContainer.appendChild(details);

            } else {
                // Outros status (Conectando, Parado, Rodando, Erro, etc.) -> Exibe texto simples
                const main = document.createElement('span');
                main.className = 'status-main';
                 // Deixa o texto como está, mas em maiúsculas para consistência
                main.textContent = text.toUpperCase();
                textContainer.appendChild(main);
            }

            statusContainer.appendChild(textContainer);
            statusContainer.className = 'status-indicator'; // Garante a classe base no container principal
        }
    } // Fecha a nova função updateStatus()

    // Função para Minimizar/Maximizar
    function toggleMinimize() {
        isMinimized = !isMinimized;
        const btn = document.getElementById('iqbot-minimize-btn');
        const headerStatusSpan = document.getElementById('iqbot-header-status');

        if (isMinimized) {
            uiContainer.classList.add('minimized');
            if (btn) btn.textContent = '□';
            // Mostra status no header SÓ SE o bot estiver rodando
            if (headerStatusSpan) headerStatusSpan.style.display = !stop ? 'inline' : 'none';
        } else {
            uiContainer.classList.remove('minimized');
            if (btn) btn.textContent = '_';
            // Esconde status no header ao maximizar
            if (headerStatusSpan) headerStatusSpan.style.display = 'none';
        }
    }

     // Modificado para usar o elemento principal como handle
     function makeDraggable(element, handle) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        handle.onmousedown = dragMouseDown;

        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }

        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        }

        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }


    // --- Funções de Controle do Bot ---

    async function connectBot() {
        email = document.getElementById('iqbot-email').value;
        senha = document.getElementById('iqbot-senha').value;
        conta = document.getElementById('iqbot-conta').value; // Pega a conta selecionada

        if (!email || !senha) {
            log('Email e Senha são obrigatórios.', 'error');
            return;
        }

        log(`Tentando conectar como ${email} na conta ${conta}...`, 'info');
        updateStatus(`Conectando...`);
        document.getElementById('iqbot-connect-btn').disabled = true;

        try {
            // 1. Tenta conectar
             const check = await apiConnect(email, senha);

            if (check.success) {
                log('Conectado com sucesso à API!', 'success');

                // 2. Muda para a conta selecionada
                log(`Mudando para conta ${conta}...`, 'info');
                const balanceChanged = await apiChangeBalance(conta);

                if (balanceChanged) {
                    log(`Conta ${conta} selecionada.`, 'success');

                    // 3. Obtém perfil e saldo inicial
                     const perfil = await apiGetProfileAsync();
                     cifrao = perfil.currency_char || '$';
                     nome = perfil.name || 'Usuário';

                     // Mensagem de boas-vindas com voz (se ativa)
                     usar_voz = document.getElementById('iqbot-usar-voz').checked; // Garante que temos o valor atualizado
                     speak(`Olá ${nome}, eu sou o PRO BULLEX e irei operar por você!`);

                     saldo_inicial = await apiGetBalance();
                     // --- DEBUG: Logar saldo obtido --- 
                     console.log('[connectBot] Saldo obtido pela API:', saldo_inicial, '(Tipo:', typeof saldo_inicial, ')');
                     // ---> REMOVE VERIFICAÇÃO rigorosa introduzida anteriormente <---
                     // if (typeof saldo_inicial !== 'number' || isNaN(saldo_inicial)) { ... } // Bloco removido
                     
                     lucro_total = 0; // Reseta lucro ao conectar
                     nivel_soros = 0; // Reseta soros
                     valor_soros = 0;
                     consecutive_wins = 0; // Reseta contadores
                     consecutive_losses = 0;

                     log(`Olá, ${nome}!`, 'info');
                     // Passa nome e saldo para updateStatus
                     const statusString = `Conectado: ${nome} | Saldo Inicial: ${formatCurrency(saldo_inicial)}`; // Nova string sem (${conta})
                     console.log('[connectBot] String final para updateStatus:', statusString); // DEBUG
                     updateStatus(statusString); 
                     conectado = true;
                     stop = true; // Permite iniciar

                     // ---> Chama a função para popular os ativos <---
                     populateActivesDropdown(); // Removido await, pois a função agora é síncrona

                     // Habilita/desabilita botões
                     document.getElementById('iqbot-start-btn').disabled = false;
                     document.getElementById('iqbot-stop-btn').disabled = true; // Parar fica desabilitado até iniciar
                     document.getElementById('iqbot-connect-btn').disabled = true; // Manter conectar desabilitado
                     // Desabilita campos de config após conectar
 


                } else {
                     log(`Falha ao mudar para conta ${conta}.`, 'error');
                     updateStatus(`Erro ao mudar conta.`);
                     document.getElementById('iqbot-connect-btn').disabled = false; // Reabilita conectar
                }

            } else {
                 log(`Falha na conexão: ${check.message}`, 'error');
                 // Tentar interpretar a mensagem de erro comum
                 if (check.message && check.message.includes('invalid_credentials')) {
                     log('Email ou senha incorretos.', 'error');
                     updateStatus('Credenciais inválidas.');
                 } else if (check.message && (check.message.includes('Failed to fetch') || check.message.includes('NetworkError'))) {
                      log('Falha ao conectar à API. Verifique se o servidor Python está rodando.', 'error');
                       updateStatus('Erro de conexão com API.');
                 }
                 else {
                     updateStatus(`Falha na conexão.`);
                 }
                 conectado = false; // Garante que está desconectado
                 updateStatus('Desconectado: Falha na conexão'); // Atualiza status visualmente
                 document.getElementById('iqbot-connect-btn').disabled = false;
            }
        } catch (error) {
            log(`Erro inesperado durante a conexão: ${error.message}`, 'error');
            conectado = false; // Garante que está desconectado
            updateStatus(`Erro: ${error.message}`);
            document.getElementById('iqbot-connect-btn').disabled = false;
        }
    }

     function disableConfigInputs(disable) {
         const ids = [
             'iqbot-email', 'iqbot-senha', 'iqbot-conta',
-            'iqbot-ativo', // Restaurado input de ativo
+            // 'iqbot-ativo-select', // Removido anteriormente, mantido removido para deixar sempre habilitado
             'iqbot-entrada', 'iqbot-stopwin', 'iqbot-stoploss', 
             'iqbot-usar-mg', 'iqbot-mg-niveis', 'iqbot-mg-fator', 
             'iqbot-usar-soros', 'iqbot-soros-niveis'
         ];
         if (document.getElementById('iqbot-usar-voz')) ids.push('iqbot-usar-voz'); // Inclui o novo checkbox
         ids.forEach(id => {
             const el = document.getElementById(id);
             if (el) el.disabled = disable;
         });
         // Inclui os novos campos do filtro de média
         const idsFiltro = ['iqbot-analise-medias', 'iqbot-velas-medias'];
         idsFiltro.forEach(id => {
             const el = document.getElementById(id);
             if (el) el.disabled = disable;
         });
         // Re-habilita campos MG/Soros apenas se a checkbox correspondente estiver marcada
         if (!disable) { // Ao re-habilitar (ex: após parar)
              document.getElementById('iqbot-mg-niveis').disabled = !document.getElementById('iqbot-usar-mg').checked;
              document.getElementById('iqbot-mg-fator').disabled = !document.getElementById('iqbot-usar-mg').checked;
              document.getElementById('iqbot-soros-niveis').disabled = !document.getElementById('iqbot-usar-soros').checked;
              // Re-habilita campo de período da média se o filtro estiver marcado
              document.getElementById('iqbot-velas-medias').disabled = !document.getElementById('iqbot-analise-medias').checked;
         }
     }

    function startBot() {
        // Remove DEBUG INÍCIO

        if (!conectado) {
            log('Conecte primeiro!', 'error');
            return;
        }
         if (mhiInterval || checkStopInterval) {
             log('Bot já está rodando.', 'warning');
             return;
        }

        // Restaura verificação original de saldo_inicial (sem check === 0 e sem console.error)
        if (typeof saldo_inicial !== 'number' || isNaN(saldo_inicial)) {
            log('Erro crítico: Saldo inicial inválido. Não é possível iniciar o bot.', 'error');
            updateStatus('Erro: Saldo Inválido');
            document.getElementById('iqbot-connect-btn').disabled = false;
            document.getElementById('iqbot-start-btn').disabled = true;
            document.getElementById('iqbot-stop-btn').disabled = true;
            conectado = false;
            return;
        }

        log('Iniciando Bot...', 'success');
        stop = true; // Garante que o bot pode operar
        operacao_em_andamento = false; // Reseta estado de operação

        // Atualiza valores das configurações globais a partir da UI antes de iniciar (remove logs)
        ativo = document.getElementById('iqbot-ativo-select').value;
        valor_entrada = parseFloat(document.getElementById('iqbot-entrada').value);
        stop_win = parseFloat(document.getElementById('iqbot-stopwin').value);
        stop_loss = parseFloat(document.getElementById('iqbot-stoploss').value);
        usar_martingale = document.getElementById('iqbot-usar-mg').checked;
        martingale = usar_martingale ? parseInt(document.getElementById('iqbot-mg-niveis').value) : 0;
        fator_mg = usar_martingale ? parseFloat(document.getElementById('iqbot-mg-fator').value) : 0;
        usar_soros = document.getElementById('iqbot-usar-soros').checked;
        niveis_soros = usar_soros ? parseInt(document.getElementById('iqbot-soros-niveis').value) : 0;
        usar_voz = document.getElementById('iqbot-usar-voz').checked;
        analise_medias = document.getElementById('iqbot-analise-medias').checked;
        velas_medias = analise_medias ? parseInt(document.getElementById('iqbot-velas-medias').value) : 0;
        usar_rsi = document.getElementById('iqbot-usar-rsi').checked;
        periodo_rsi = usar_rsi ? parseInt(document.getElementById('iqbot-periodo-rsi').value) : 14;
        timeframe_selecionado_segundos = parseInt(document.getElementById('iqbot-timeframe').value);
        const timeframe_texto = document.getElementById('iqbot-timeframe').options[document.getElementById('iqbot-timeframe').selectedIndex].text;
        const selectedStrategyRadio = document.querySelector('input[name="iqbot-strategy"]:checked');
        if (selectedStrategyRadio) {
            estrategia_selecionada = selectedStrategyRadio.value;
        } else {
            estrategia_selecionada = 'mhi';
            document.getElementById('iqbot-strategy-mhi').checked = true;
        }
        // Log da estratégia é mantido pois estava em funcionav2
        log(`Iniciando com Estratégia: ${estrategia_selecionada === 'pro' ? 'PRO Adaptada' : (estrategia_selecionada === 'cinco_velas' ? 'Cinco Velas' : 'MHI Original')}`, 'info');
        
        // Resetar soros ao iniciar (mantido)
        nivel_soros = 0;
        valor_soros = 0;
        consecutive_wins = 0;
        consecutive_losses = 0;

        // Logs das configurações são mantidos pois estavam em funcionav2
        log(`Configurações: Ativo: ${ativo}, Entrada: ${formatCurrency(valor_entrada)}, SW: ${formatCurrency(stop_win)}, SL: ${formatCurrency(stop_loss)}`, 'info');
        log(`Martingale: ${usar_martingale ? `Sim (Níveis: ${martingale}, Fator: ${fator_mg})` : 'Não'}`, 'info');
        log(`Soros: ${usar_soros ? `Sim (Níveis: ${niveis_soros})` : 'Não'}`, 'info');
        log(`Timeframe: ${timeframe_texto}`, 'info');

        // Inicia loop de verificação de stop (remove logs)
        checkStopInterval = setInterval(checkStop, 5000);
        checkStop(); // <-- Chama imediatamente como em funcionav2

        // Inicia loop da estratégia SELECIONADA (remove logs e ajusta a forma de iniciar)
        log(`Iniciando loop da estratégia ${estrategia_selecionada}...`, 'info'); // Log mantido
        // Lógica de seleção de `funcionav2`
        if (estrategia_selecionada === 'pro') {
            mhiInterval = setInterval(estrategiaProAdaptada, 500);
        } else if (estrategia_selecionada === 'cinco_velas') { // Adiciona verificação para cinco_velas
            mhiInterval = setInterval(estrategiaCincoVelas, 500);
        } else {
            mhiInterval = setInterval(estrategiaMhi, 500); // MHI como padrão
        }

        // Atualiza UI (remove log)
        document.getElementById('iqbot-start-btn').disabled = true;
        document.getElementById('iqbot-stop-btn').disabled = false;
        disableConfigInputs(true);
        
        // Atualização de status final como em funcionav2
        // (Aqui está a diferença principal, funcionav2 usava uma string fixa ou baseada no MHI)
        // Vamos usar a versão mais genérica de funcionav2 que apenas menciona o saldo
        updateStatus(`Rodando | Saldo: ${formatCurrency(saldo_inicial)}`); 
    }

    function stopBot() {
        log('Parando Bot...', 'warning');
        stop = false; // Sinaliza para as operações pararem

        // Para os loops
        if (checkStopInterval) {
            clearInterval(checkStopInterval);
            checkStopInterval = null;
        }
        if (mhiInterval) {
            clearInterval(mhiInterval);
            mhiInterval = null;
        }

        // Atualiza UI
        if (conectado) { // Só reabilita start se ainda estiver conectado
             document.getElementById('iqbot-start-btn').disabled = false;
             document.getElementById('iqbot-stop-btn').disabled = true;
             disableConfigInputs(false); // Reabilita config
             updateStatus(`Parado | Saldo: ${formatCurrency(saldo_inicial)}`); // Atualiza status
        } else {
             document.getElementById('iqbot-start-btn').disabled = true;
             document.getElementById('iqbot-stop-btn').disabled = true;
             document.getElementById('iqbot-connect-btn').disabled = false;
             disableConfigInputs(false);
             updateStatus('Desconectado');
        }

        // Não reseta conectado, email, senha - pode querer reiniciar
        // operacao_em_andamento será resetado naturalmente ao final da op atual

        // Esconde status no header
        const headerStatusSpan = document.getElementById('iqbot-header-status');
        if (headerStatusSpan) {
            headerStatusSpan.style.display = 'none';
        }
    }

     // Utilitário sleep
     function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
     }

    // Utilitário round
    function round(value, decimals) {
        return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
    }


    // --- Inicialização ---
    function init() {
        console.log('Iniciando PRO BULLEX UI...');
        // Garante que o estado inicial seja sempre desconectado
        conectado = false;
        stop = true; // Reseta o stop também

        // Removido: Tentativa de carregar vozes cedo
        // if (typeof speechSynthesis !== 'undefined') {
        //     speechSynthesis.getVoices();
        // }
        createUI(); // Cria a UI
        log('PRO BULLEX UI v1.0 carregado. Insira suas credenciais e clique em Conectar.', 'info');
        toggleMinimize(); // <--- Adiciona esta linha para minimizar logo após criar
         // Tentar obter saldo inicial e perfil se já houver cookie de sessão válido na API?
         // Poderia tentar um /get_profile para ver se está conectado na API python
         // Mas a conexão inicial com email/senha é mais robusta.
    }

    // --- Executa a inicialização ---
    // Espera um pouco para a página carregar completamente
    // Em alguns casos, pode ser necessário esperar por elementos específicos da IQ Option
    // se a interação direta com a página fosse necessária (que não é o caso aqui).
    if (document.readyState === "complete" || document.readyState === "interactive") {
        setTimeout(init, 1000); // Espera 1 segundo
    } else {
        document.addEventListener("DOMContentLoaded", () => setTimeout(init, 1000));
    }

    // Adicionar após a definição da função speak (linha ~320)

    // Lista todas as vozes disponíveis no sistema
    function getAvailableVoices() {
        return speechSynthesis.getVoices().filter(voice => 
            voice.lang.includes('pt') || voice.name.toLowerCase().includes('brasil') || 
            voice.name.toLowerCase().includes('brazil'));
    }

    // Cria um dropdown com todas as vozes disponíveis
    function createVoiceSelector() {
        const voices = getAvailableVoices();
        if (!voices || voices.length === 0) return null;
        
        const container = document.createElement('div');
        container.className = 'iqbot-select-group';
        
        const label = document.createElement('label');
        label.textContent = 'Voz:';
        label.htmlFor = 'iqbot-voice-select';
        container.appendChild(label);
        
        const select = document.createElement('select');
        select.id = 'iqbot-voice-select';
        
        // Adiciona opção padrão
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Voz Padrão';
        select.appendChild(defaultOption);
        
        // Adiciona todas as vozes disponíveis
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.name} (${voice.lang})`;
            select.appendChild(option);
        });
        
        select.onchange = function() {
            // Teste a voz selecionada
            const selectedVoice = this.value;
            
            if (selectedVoice) {
                const voice = voices.find(v => v.name === selectedVoice);
                if (voice) {
                    speak(`Olá, ${nome}! Esta é a voz ${voice.name}.`);
                }
            }
        };
        
        container.appendChild(select);
        return container;
    }

    // Função para criar controles de ajuste de voz (velocidade e tom)
    function createVoiceControls() {
        const container = document.createElement('div');
        container.className = 'iqbot-inline-number-group';
        
        // Controle de velocidade
        const rateGroup = document.createElement('div');
        rateGroup.className = 'iqbot-input-group';
        const rateLabel = document.createElement('label');
        rateLabel.htmlFor = 'iqbot-voice-rate';
        rateLabel.textContent = 'Velocidade';
        rateGroup.appendChild(rateLabel);
        
        const rateInput = document.createElement('input');
        rateInput.type = 'range';
        rateInput.id = 'iqbot-voice-rate';
        rateInput.min = '0.5';
        rateInput.max = '2';
        rateInput.step = '0.1';
        rateInput.value = '1';
        rateInput.className = 'iqbot-input';
        rateInput.oninput = function() {
            document.getElementById('iqbot-rate-value').textContent = this.value;
        };
        rateInput.onchange = function() {
            speak(`Testando velocidade em ${this.value}.`);
        };
        rateGroup.appendChild(rateInput);
        
        const rateValue = document.createElement('span');
        rateValue.id = 'iqbot-rate-value';
        rateValue.textContent = '1';
        rateValue.style.marginLeft = '5px';
        rateGroup.appendChild(rateValue);
        
        container.appendChild(rateGroup);
        
        // Controle de tom
        const pitchGroup = document.createElement('div');
        pitchGroup.className = 'iqbot-input-group';
        const pitchLabel = document.createElement('label');
        pitchLabel.htmlFor = 'iqbot-voice-pitch';
        pitchLabel.textContent = 'Tom';
        pitchGroup.appendChild(pitchLabel);
        
        const pitchInput = document.createElement('input');
        pitchInput.type = 'range';
        pitchInput.id = 'iqbot-voice-pitch';
        pitchInput.min = '0.5';
        pitchInput.max = '2';
        pitchInput.step = '0.1';
        pitchInput.value = '1';
        pitchInput.className = 'iqbot-input';
        pitchInput.oninput = function() {
            document.getElementById('iqbot-pitch-value').textContent = this.value;
        };
        pitchInput.onchange = function() {
            speak(`Testando tom em ${this.value}.`);
        };
        pitchGroup.appendChild(pitchInput);
        
        const pitchValue = document.createElement('span');
        pitchValue.id = 'iqbot-pitch-value';
        pitchValue.textContent = '1';
        pitchValue.style.marginLeft = '5px';
        pitchGroup.appendChild(pitchValue);
        
        container.appendChild(pitchGroup);
        
        return container;
    }

    
    // --- Modificações na função createUI() ---
    // ... existing code ...

    // Agora, precisamos adicionar o seletor de vozes e os controles à UI
    // Na função createUI(), depois de adicionar o checkbox de usar voz:

    // ... existing code ...

    // --- Adicionar nova função para controlar visibilidade dos logs ---

    // Função para mostrar/ocultar o container de logs
    function toggleLogsVisibility() {
        if (!logContainer) return; // Garante que o container existe

        const button = document.getElementById('iqbot-toggle-logs-btn');
        const isHidden = logContainer.style.display === 'none';

        if (isHidden) {
            logContainer.style.display = ''; // Restaura para o display padrão (geralmente block ou herdado do CSS)
            if (button) button.textContent = 'Ocultar Logs';
        } else {
            logContainer.style.display = 'none';
            if (button) button.textContent = 'Mostrar Logs';
        }
    }

    // Função para preencher o dropdown de ativos (VERSÃO FIXA - PRIORITÁRIOS -op e -OTC)
    function populateActivesDropdown() { 
        const selectElement = document.getElementById('iqbot-ativo-select');
        if (!selectElement) {
            log('Erro: Elemento iqbot-ativo-select não encontrado', 'error');
            return;
        }

        selectElement.disabled = true; 
        selectElement.innerHTML = ''; 
        log('Populando dropdown com ativos prioritários fixos (-op e -OTC)...', 'info');

        try {
            // --- Definição dos 10 Ativos Base Prioritários ---
            const basePrioritarios = [
                "EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", 
                "USDCAD", "USDCHF", "EURGBP", "GBPJPY", "AUDCAD"
            ];
            const knownSuffixes = ['-OTC', '-op']; 
            
            // --- Lógica para gerar lista com AMBOS os sufixos ---
            let finalAssetList = []; // Construir a lista diretamente

            basePrioritarios.forEach(base => {
                const otcAsset = `${base}${knownSuffixes[0]}`;
                const opAsset = `${base}${knownSuffixes[1]}`;

                // Adiciona ambas as variantes à lista
                finalAssetList.push({ name: otcAsset });
                finalAssetList.push({ name: opAsset });
            });

            // Ordena a lista final alfabeticamente
            finalAssetList.sort((a, b) => a.name.localeCompare(b.name));
            // ---> FIM DA LÓGICA <---

            // Adiciona a opção "Selecione um Ativo" primeiro
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Selecione um Ativo';
            selectElement.appendChild(defaultOption);

            // Adiciona os ativos da lista
            finalAssetList.forEach(asset => {
                const option = document.createElement('option');
                option.value = asset.name;
                option.textContent = asset.name; // Sem payout
                if (asset.name === ativo) { // Verifica se é o ativo global atual
                    option.selected = true;
                } else if (!ativo && defaultOption.value === '') {
                     // Seleciona o "Selecione um ativo" se nenhum ativo global estiver definido
                     // (Evita que o primeiro item da lista seja selecionado automaticamente no carregamento inicial)
                    // Este check extra é importante pois 'ativo' pode ser 'EURUSD' por padrão
                }
                selectElement.appendChild(option);
            });
            
            // Seleciona o "Selecione um ativo" se o ativo padrão não estiver na lista
            // (Isso garante que "Selecione um ativo" seja o padrão se o 'ativo' global não corresponder a nada)
            if (!finalAssetList.some(asset => asset.name === ativo)) {
                 selectElement.value = ''; // Força a seleção do "Selecione um Ativo"
            }

            log(`Exibindo ${finalAssetList.length} ativos prioritários fixos (-op e -OTC).`, 'info');

        } catch (error) {
            log(`Erro ao popular dropdown fixo: ${error.message}`, 'error');
            console.error("Erro detalhado dropdown fixo:", error);
            selectElement.innerHTML = '<option value="">Erro</option>';
        } finally {
            // Habilita o select sempre ao final da função
            selectElement.disabled = false; 
        }
    }
})(); 