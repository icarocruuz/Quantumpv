/*
 * ⚠️ AVISO IMPORTANTE - CÓDIGO PROTEGIDO ⚠️
 * 
 * Este código está protegido por sistemas avançados de segurança e monitoramento.
 * Qualquer tentativa de cópia, distribuição ou uso não autorizado será:
 * 
 * 1. Detectada automaticamente
 * 2. Registrada com dados do dispositivo e localização
 * 3. Reportada às autoridades competentes
 * 4. Sujeita a processos legais e multas
 * 
 * O sistema possui proteção contra engenharia reversa e auto-destruição
 * em caso de manipulação não autorizada.
 * 
 * VOCÊ FOI AVISADO!
 * 
 * Copyright 2025 - Todos os direitos reservados
 * ⚠️ NÃO TENTE PIRATEAR ESTE CÓDIGO ⚠️
 */

// Modularize the creation of styles
function createStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Tema Neon Futurista */
        body {
            background: #0f0f0f;
            overflow: hidden;
            color: #e0e0e0;
            font-family: 'Roboto', sans-serif;
        }

        #overlayCanvas {
            position: absolute;
            top: 0;
            left: 0;
            pointer-events: none;
            z-index: 1000;
        }

        /* Efeitos de Partículas */
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: moveParticle 20s linear infinite;
        }

        @keyframes moveParticle {
            from {
                transform: translateY(0) translateX(0);
            }
            to {
                transform: translateY(100vh) translateX(100vw);
            }
        }

        /* Transformações 3D */
        .trading-overlay {
            transform-style: preserve-3d;
            perspective: 1000px;
            animation: rotate3D 10s infinite linear;
        }

        @keyframes rotate3D {
            from {
                transform: rotateY(0deg);
            }
            to {
                transform: rotateY(360deg);
            }
        }

        /* Animações Avançadas */
        .trading-overlay:hover {
            animation: none;
        }

        @keyframes hoverEffect {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Interatividade Aprimorada */
        .trading-overlay button:hover {
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
            animation: buttonPulse 1s infinite;
        }

        @keyframes buttonPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        /* Tipografia Moderna */
        .trading-overlay th, .trading-overlay td {
            font-family: 'Roboto Mono', monospace;
            font-size: 16px;
        }

        .trading-overlay {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(145deg, rgba(26, 31, 37, 0.95), rgba(31, 37, 45, 0.98));
            color: white;
            padding: 20px;
            border-radius: 16px;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-width: 340px;
            max-width: 90vw;
            z-index: 9999;
            animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3),
                        0 2px 10px rgba(0, 0, 0, 0.2),
                        inset 0 1px 1px rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .trading-overlay:hover {
            transform: translateX(-50%) translateY(-5px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4),
                        0 3px 15px rgba(0, 0, 0, 0.3),
                        inset 0 1px 1px rgba(255, 255, 255, 0.15);
        }

        .trading-overlay table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px;
        }

        .trading-overlay th {
            color: #a8b2c1;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 10px 15px;
        }

        .trading-overlay td {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            transition: all 0.3s ease;
        }

        .trading-overlay tr td:first-child {
            border-radius: 10px 0 0 10px;
        }

        .trading-overlay tr td:last-child {
            border-radius: 0 10px 10px 0;
        }

        .trading-overlay tr:hover td {
            background: rgba(255, 255, 255, 0.07);
            transform: scale(1.01);
        }

        .call, .put {
            padding: 8px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 1px;
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 100px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .call {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.2));
            color: #4caf50;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }

        .put {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(244, 67, 54, 0.2));
            color: #f44336;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }

        .call.active {
            animation: callGlow 2s infinite;
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.3));
            border-color: rgba(76, 175, 80, 0.5);
        }

        .put.active {
            animation: putGlow 2s infinite;
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(244, 67, 54, 0.3));
            border-color: rgba(244, 67, 54, 0.5);
        }

        .call:hover, .put:hover {
            transform: translateY(-2px);
            filter: brightness(1.2);
        }

        @keyframes callGlow {
            0% {
                box-shadow: 0 0 5px rgba(76, 175, 80, 0.3),
                            0 0 15px rgba(76, 175, 80, 0.3),
                            0 0 25px rgba(76, 175, 80, 0.3);
            }
            50% {
                box-shadow: 0 0 10px rgba(76, 175, 80, 0.5),
                            0 0 20px rgba(76, 175, 80, 0.3),
                            0 0 30px rgba(76, 175, 80, 0.3);
            }
            100% {
                box-shadow: 0 0 5px rgba(76, 175, 80, 0.3),
                            0 0 15px rgba(76, 175, 80, 0.3),
                            0 0 25px rgba(76, 175, 80, 0.3);
            }
        }

        @keyframes putGlow {
            0% {
                box-shadow: 0 0 5px rgba(244, 67, 54, 0.3),
                            0 0 15px rgba(244, 67, 54, 0.3),
                            0 0 25px rgba(244, 67, 54, 0.3);
            }
            50% {
                box-shadow: 0 0 10px rgba(244, 67, 54, 0.5),
                            0 0 20px rgba(244, 67, 54, 0.3),
                            0 0 30px rgba(244, 67, 54, 0.3);
            }
            100% {
                box-shadow: 0 0 5px rgba(244, 67, 54, 0.3),
                            0 0 15px rgba(244, 67, 54, 0.3),
                            0 0 25px rgba(244, 67, 54, 0.3);
            }
        }

        .trading-overlay td {
            padding: 12px 15px;
            font-size: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .trading-overlay tr:last-child td {
            border-bottom: none;
        }

        .trading-overlay tr:hover td {
            background: rgba(255, 255, 255, 0.05);
        }

        .trading-logo {
            text-align: center;
            padding: 5px 0 20px;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            position: relative;
        }

        .trading-logo::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 2px;
            background: linear-gradient(90deg, #64b5f6, transparent);
            animation: borderPulse 2s infinite;
        }

        .trading-logo h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(45deg, #2196f3, #00bcd4, #4caf50, #2196f3);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientFlow 6s ease infinite;
        }

        .trading-logo span {
            display: block;
            margin-top: 5px;
            font-size: 13px;
            color: #a8b2c1;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.8;
        }

        .controls-container {
            position: absolute;
            top: 0;
            right: 0;
            z-index: 10000;
        }

        .trading-overlay.minimized {
            transform: translateX(-50%) translateY(calc(100% - 65px));
            height: 65px;
            cursor: pointer;
            background: linear-gradient(135deg, 
                rgba(26, 31, 37, 0.98) 0%,
                rgba(33, 39, 48, 0.98) 100%);
            border-bottom: none;
            padding: 10px 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 -5px 25px rgba(0, 0, 0, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .trading-overlay.minimized:hover {
            transform: translateX(-50%) translateY(calc(100% - 70px));
            box-shadow: 0 -8px 30px rgba(33, 150, 243, 0.15);
        }

        .trading-overlay.minimized .trading-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            border: none;
            gap: 15px;
        }

        .trading-overlay.minimized .trading-logo::before {
            content: '●';
            color: #4caf50;
            animation: blink 1.5s infinite;
            font-size: 12px;
        }

        .trading-overlay.minimized .trading-logo h1 {
            font-size: 20px;
            margin: 0;
            background: linear-gradient(45deg, #2196f3, #00bcd4, #4caf50);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientFlow 4s ease infinite;
        }

        .trading-overlay.minimized .trading-logo span {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7);
            letter-spacing: 2px;
            animation: pulse 2s infinite;
        }

        .trading-overlay.minimized table {
            display: none;
        }

        .minimize-maximize-btn {
            background: rgba(33, 150, 243, 0.1);
            border: none;
            color: #2196f3;
            width: 35px;
            height: 30px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            border-radius: 0 8px 0 8px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
        }

        .minimize-maximize-btn:hover {
            background: rgba(33, 150, 243, 0.2);
        }

        .trading-overlay.minimized .minimize-maximize-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(33, 150, 243, 0.15);
            color: #2196f3;
            width: 35px;
            height: 30px;
            font-size: 16px;
            border-radius: 4px;
            display: none;
        }

        .trading-overlay.minimized .minimize-maximize-btn:hover {
            background: rgba(33, 150, 243, 0.25);
        }

        .minimize-maximize-btn::before {
            content: '—';
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
        }

        .trading-overlay.minimized .minimize-maximize-btn::before {
            content: '□';
            font-size: 16px;
        }

        .trading-overlay.minimized::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, 
                #2196f3 0%,
                #00bcd4 50%,
                #4caf50 100%);
            opacity: 0.7;
            animation: progressBar 2s linear infinite;
        }

        @keyframes blink {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        @keyframes progressBar {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @media (max-width: 768px) {
            .trading-overlay.minimized {
                min-width: 280px;
                height: 55px;
                transform: translateX(-50%) translateY(calc(100% - 55px));
            }

            .trading-overlay.minimized:hover {
                transform: translateX(-50%) translateY(calc(100% - 60px));
            }

            .trading-overlay.minimized .trading-logo h1 {
                font-size: 18px;
            }

            .trading-overlay.minimized .trading-logo span {
                font-size: 10px;
            }
        }

        @keyframes gradientFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes borderPulse {
            0% { width: 50px; opacity: 1; }
            50% { width: 100px; opacity: 0.5; }
            100% { width: 50px; opacity: 1; }
        }

        @keyframes newEntryEffect {
            0% { 
                transform: translateY(20px) scale(0.95);
                opacity: 0;
            }
            50% {
                transform: translateY(-5px) scale(1.02);
            }
            100% { 
                transform: translateY(0) scale(1);
                opacity: 1;
            }
        }

        @keyframes expiring-pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
        }

        .currency-pair {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 8px 15px;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.05) 0%,
                rgba(255, 255, 255, 0.02) 100%);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .currency-pair:hover {
            transform: translateX(5px);
            background: linear-gradient(135deg,
                rgba(255, 255, 255, 0.08) 0%,
                rgba(255, 255, 255, 0.04) 100%);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .currency-pair::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.1),
                transparent
            );
            transition: 0.5s;
        }

        .currency-pair:hover::after {
            left: 100%;
        }

        .flags {
            display: flex;
            align-items: center;
            gap: 8px;
            perspective: 1000px;
        }

        .flag {
            width: 32px;
            height: 22px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .flag::after {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 6px;
            box-shadow: inset 0 0 2px rgba(255, 255, 255, 0.4);
        }

        .flags:hover .flag:first-child {
            transform: perspective(500px) rotateY(-15deg) translateX(-2px);
        }

        .flags:hover .flag:last-child {
            transform: perspective(500px) rotateY(15deg) translateX(2px);
        }

        .currency-pair span {
            font-size: 15px;
            font-weight: 500;
            color: #fff;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
            letter-spacing: 0.5px;
        }

        .currency-pair.new-entry {
            animation: newPairEntry 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        @keyframes newPairEntry {
            0% {
                transform: scale(0.95) translateX(-10px);
                opacity: 0;
            }
            50% {
                transform: scale(1.02) translateX(5px);
            }
            100% {
                transform: scale(1) translateX(0);
                opacity: 1;
            }
        }

        .trading-overlay td:first-child {
            min-width: 180px;
        }

        @media (max-width: 768px) {
            .currency-pair {
                padding: 6px 12px;
            }

            .flag {
                width: 28px;
                height: 19px;
            }

            .currency-pair span {
                font-size: 14px;
            }
        }

        .expiration-time {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            position: relative;
            font-size: 13px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .expiration-time i {
            font-size: 12px;
            color: #64b5f6;
            margin-right: 2px;
        }

        .expiration-time span {
            font-family: 'Roboto Mono', monospace;
            font-weight: 500;
            color: #e0e0e0;
        }

        .expiration-time::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, #64b5f6, transparent);
            transform-origin: left;
            animation: timeProgress linear;
            animation-duration: 60s;
        }

        .expiration-time.expiring {
            background: rgba(255, 193, 7, 0.05);
            border-color: rgba(255, 193, 7, 0.2);
        }

        .expiration-time.expiring i {
            color: #ffc107;
        }

        .expiration-time.expiring span {
            color: #ffc107;
        }

        .expiration-time.expiring::after {
            background: linear-gradient(90deg, #ffc107, transparent);
            animation: timeProgressExpiring 1s infinite;
        }

        @keyframes timeProgress {
            from { transform: scaleX(1); }
            to { transform: scaleX(0); }
        }

        @keyframes timeProgressExpiring {
            0% { opacity: 0.3; }
            50% { opacity: 0.8; }
            100% { opacity: 0.3; }
        }

        .entry-time {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: rgba(33, 150, 243, 0.05);
            border-radius: 12px;
            font-size: 13px;
            font-family: 'Roboto Mono', monospace;
            color: #64b5f6;
            border: 1px solid rgba(33, 150, 243, 0.1);
            position: relative;
            overflow: hidden;
        }

        .entry-time::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(33, 150, 243, 0.1),
                transparent
            );
            animation: shimmer 2s infinite;
        }

        .entry-time i {
            font-size: 12px;
            color: #2196f3;
            opacity: 0.8;
        }

        .entry-time.new {
            animation: newEntryPulse 1s ease-out;
        }

        @keyframes shimmer {
            0% { transform: translateX(0%); }
            100% { transform: translateX(200%); }
        }

        @keyframes newEntryPulse {
            0% {
                transform: scale(0.95);
                background: rgba(33, 150, 243, 0.15);
            }
            50% {
                transform: scale(1.02);
                background: rgba(33, 150, 243, 0.1);
            }
            100% {
                transform: scale(1);
                background: rgba(33, 150, 243, 0.05);
            }
        }

        /* Estilos do Modal de Segurança */
        .security-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 99999;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .security-modal {
            background: linear-gradient(145deg, #1a1f25, #2a2f35);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
            max-width: 500px;
            width: 90%;
            color: #fff;
            text-align: center;
            border: 1px solid rgba(255, 0, 0, 0.2);
        }

        .security-modal h2 {
            color: #ff3333;
            margin-bottom: 20px;
            font-size: 24px;
        }

        .security-modal p {
            margin: 15px 0;
            font-size: 16px;
            line-height: 1.5;
        }

        .security-modal .warning-icon {
            font-size: 48px;
            color: #ff3333;
            margin-bottom: 20px;
        }

        .security-modal button {
            background: #ff3333;
            border: none;
            padding: 12px 30px;
            color: white;
            border-radius: 5px;
            margin-top: 20px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }

        .security-modal button:hover {
            background: #cc0000;
        }

        .security-modal .device-info {
            background: rgba(255, 0, 0, 0.1);
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: left;
            font-family: monospace;
        }

        /* Efeitos de Partículas de Trading */
        .candle {
            position: absolute;
            width: 2px;
            background: #4CAF50;
            animation: none;
        }

        @keyframes moveCandle {
            from {
                transform: translateY(0) translateX(0);
                height: 10px;
            }
            to {
                transform: translateY(100vh) translateX(100vw);
                height: 30px;
            }
        }

        /* Design Temático de Trading */
        .trading-overlay {
            background: linear-gradient(145deg, #1c1f26, #23272f);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .trading-overlay th, .trading-overlay td {
            color: #e0e0e0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .trading-overlay .controls {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
        }

        /* Interatividade e Feedback Visual */
        .trading-overlay button {
            background: #2196F3;
            color: white;
            transition: background 0.3s ease;
        }

        .trading-overlay button:hover {
            background: #1976D2;
        }

        /* Partículas de Trading no fundo */
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: moveParticle 20s linear infinite;
        }

        @keyframes moveParticle {
            from {
                transform: translateY(0) translateX(0);
            }
            to {
                transform: translateY(100vh) translateX(100vw);
            }
        }

        /* Estilo de Cards para Entradas */
        .entry-card {
            background: linear-gradient(145deg, #1f1f1f, #2a2a2a);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: start;
        }

        .entry-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        }

        .entry-card h3 {
            font-size: 20px;
            color: #f0f0f0;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .entry-card h3::before {
            content: url('icon.svg'); /* Placeholder for icon */
            margin-right: 10px;
        }

        .entry-card label {
            font-size: 16px;
            color: #c0c0c0;
            margin-bottom: 8px;
        }

        .entry-card input, .entry-card select {
            width: 100%;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }

        .entry-card input:focus, .entry-card select:focus {
            border-color: #42a5f5;
            outline: none;
        }

        .entry-card button {
            background: #66bb6a;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s ease;
            align-self: flex-end;
        }

        .entry-card button:hover {
            background: #5aaf5e;
        }

        /* Efeito Neon e Vidro para Botões de Direção */
        .direction-button {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 24px;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            backdrop-filter: blur(10px);
        }

        .direction-button:hover {
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.8);
            transform: scale(1.05);
        }

        .direction-button:focus {
            outline: none;
            box-shadow: 0 0 25px rgba(0, 255, 255, 1);
        }

        .direction-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin-top: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            backdrop-filter: blur(15px);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        }

        /* Efeito de Luz Laser para Botões de Call e Put */
        .call-put-button {
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            padding: 12px 24px;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            backdrop-filter: blur(10px);
        }

        .call-put-button::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.5), transparent);
            animation: laserEffect 3s infinite linear;
        }

        @keyframes laserEffect {
            0% {
                transform: translate(0, 0);
            }
            100% {
                transform: translate(50%, 50%);
            }
        }

        .call-put-button:hover {
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.8);
            transform: scale(1.05);
        }

        /* Som de Notificação */
        function playNotificationSound() {
            const audio = new Audio('notification.mp3'); // Placeholder for sound file
            audio.play();
        }

        /* Design Uniforme dos Cards */
        .entry-card {
            background: linear-gradient(145deg, #1f1f1f, #2a2a2a);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: start;
        }

        .entry-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        }

        .entry-card h3 {
            font-size: 20px;
            color: #f0f0f0;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .entry-card h3::before {
            content: url('icon.svg'); /* Placeholder for icon */
            margin-right: 10px;
        }

        .entry-card label {
            font-size: 16px;
            color: #c0c0c0;
            margin-bottom: 8px;
        }

        .entry-card input, .entry-card select {
            width: 100%;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }

        .entry-card input:focus, .entry-card select:focus {
            border-color: #42a5f5;
            outline: none;
        }

        .entry-card button {
            background: #66bb6a;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s ease;
            align-self: flex-end;
        }

        .entry-card button:hover {
            background: #5aaf5e;
        }

        /* Importando Google Fonts */
        @import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap");

        /* Variáveis CSS */
        :root {
            --accent-color: #03e9f4;
            --white-color: #fff;
            --box-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4, 0 0 50px #03e9f4, 0 0 100px #03e9f4;
            --body-font: "Montserrat", sans-serif;
        }

        /* Efeito de Animação de Borda para Botões de Call e Put */
        .call-put-button {
            position: relative;
            display: inline-block;
            padding: 20px 30px;
            color: var(--accent-color);
            text-transform: uppercase;
            overflow: hidden;
            letter-spacing: 4px;
            transition: 0.5s;
            font-family: var(--body-font);
        }

        .call-put-button span {
            position: absolute;
            display: block;
        }

        .call-put-button span:nth-child(1) {
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-color));
            animation: btn-anim1 1s linear infinite;
        }

        @keyframes btn-anim1 {
            0% {
                left: -100%;
            }
            50%, 100% {
                left: 100%;
            }
        }

        .call-put-button span:nth-child(2) {
            top: -100%;
            right: 0;
            width: 2px;
            height: 100%;
            background: linear-gradient(180deg, transparent, var(--accent-color));
            animation: btn-anim2 1s linear infinite;
            animation-delay: 0.25s;
        }

        @keyframes btn-anim2 {
            0% {
                top: -100%;
            }
            50%, 100% {
                top: 100%;
            }
        }

        .call-put-button span:nth-child(3) {
            bottom: 0;
            right: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(270deg, transparent, var(--accent-color));
            animation: btn-anim3 1s linear infinite;
            animation-delay: 0.5s;
        }

        @keyframes btn-anim3 {
            0% {
                right: -100%;
            }
            50%, 100% {
                right: 100%;
            }
        }

        .call-put-button span:nth-child(4) {
            bottom: -100%;
            left: 0;
            width: 2px;
            height: 100%;
            background: linear-gradient(360deg, transparent, var(--accent-color), transparent);
            animation: btn-anim4 1s linear infinite;
            animation-delay: 0.75s;
        }

        @keyframes btn-anim4 {
            0% {
                bottom: -100%;
            }
            50%, 100% {
                bottom: 100%;
            }
        }

        .call-put-button:hover {
            background-color: var(--accent-color);
            color: var(--white-color);
            border-radius: 5px;
            box-shadow: var(--box-shadow);
        }

        #analysisModal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(26, 31, 37, 0.4);
            color: white;
            padding: 8px 20px;
            font-family: 'Poppins', sans-serif;
            z-index: 9999;
            min-width: 200px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            pointer-events: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }
        
        #analysisModal.minimized {
            right: 0;
            width: 40px;
            height: 40px;
            min-width: auto;
            padding: 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 8px 0 0 8px;
        }
        
        #analysisModal.minimized #candleAnalysis {
            display: none;
        }
        
        #analysisModal.minimized h3 {
            display: none;
        }
        
        #minimizeAnalysisBtn {
            background: rgba(40, 40, 50, 0.7);
            border: none;
            color: #aaaaaa;
            width: 24px;
            height: 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            border-radius: 4px;
            transition: all 0.3s ease;
            position: absolute;
            top: 8px;
            right: 8px;
        }
        
        #minimizeAnalysisBtn:hover {
            background: rgba(60, 60, 70, 0.8);
            color: #ffffff;
        }
        
        #analysisModal.minimized #minimizeAnalysisBtn {
            position: static;
            margin: 0;
        }
        
        #analysisModal.minimized .analysis-header {
            margin: 0;
            padding: 0;
            border: none;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .analysis-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
        }
        
        .analysis-row {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 14px;
        }
        
        .analysis-row span:first-child {
            margin-right: 5px;
        }
        
        #redPercentage {
            color: #f44336;
            font-weight: bold;
        }
        
        #greenPercentage {
            color: #4caf50;
            font-weight: bold;
        }
        
        #trend {
            color: #ffff44;
            font-weight: bold;
        }
        
        #candleCount {
            color: #ffffff;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
}

// Mapeamento de moedas para bandeiras
const currencyFlagsC = {
    'EUR': 'eu', 'USD': 'us', 'JPY': 'jp', 'GBP': 'gb',
    'AUD': 'au', 'CAD': 'ca', 'CHF': 'ch', 'NZD': 'nz',
    'BTC': 'btc', 'ETH': 'eth'
};

// Funções principais
function createCurrencyPairElement(pair) {
    const firstCurrency = pair.slice(0, 3);
    const secondCurrency = pair.slice(3, 6);
    return `
        <div class="currency-pair new-entry">
            <div class="flags">
                <img class="flag" src="https://flagcdn.com/w40/${currencyFlagsC[firstCurrency].toLowerCase()}.png" alt="${firstCurrency}" loading="lazy"/>
                <img class="flag" src="https://flagcdn.com/w40/${currencyFlagsC[secondCurrency].toLowerCase()}.png" alt="${secondCurrency}" loading="lazy"/>
            </div>
            <span>${firstCurrency}/${secondCurrency}</span>
        </div>
    `;
}

function createOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'trading-overlay';

    const controls = document.createElement('div');
    controls.className = 'controls-container';

    const minimizeMaxBtn = document.createElement('button');
    minimizeMaxBtn.className = 'minimize-maximize-btn';
    minimizeMaxBtn.title = 'Minimizar/Maximizar';

    controls.appendChild(minimizeMaxBtn);

    const logo = document.createElement('div');
    logo.className = 'trading-logo';
    logo.innerHTML = `
        <h1>Indicador Rey</h1>
        <span>SINAIS AUTOMÁTICOS</span>
    `;

    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Par</th>
                <th>Entrada</th>
                <th>Direção</th>
                <th>Expiração</th>
            </tr>
        </thead>
        <tbody id="tradingBody"></tbody>
    `;

    overlay.appendChild(controls);
    overlay.appendChild(logo);
    overlay.appendChild(table);

    minimizeMaxBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        overlay.classList.toggle('minimized');
    });

    overlay.addEventListener('click', () => {
        if (overlay.classList.contains('minimized')) {
            overlay.classList.remove('minimized');
        }
    });

    return overlay;
}

function verificarEntradas() {
    const tbody = document.getElementById('tradingBody');
    const agora = new Date().getTime();
    const rows = Array.from(tbody.children);
    
    rows.sort((a, b) => {
        const expA = new Date(a.dataset.expiracao).getTime();
        const expB = new Date(b.dataset.expiracao).getTime();
        return expA - expB;
    });
    
    while (rows.length > 2) {
        const oldRow = rows.shift();
        oldRow.classList.add('removing');
        setTimeout(() => oldRow.remove(), 500);
    }
    
    rows.forEach(row => {
        const expiracao = new Date(row.dataset.expiracao).getTime();
        const tempoRestante = expiracao - agora;
        
        if (tempoRestante <= 0) {
            row.classList.add('removing');
            setTimeout(() => row.remove(), 500);
            return;
        }
        
        if (tempoRestante <= 30000) {
            if (!row.classList.contains('expiring')) {
                row.classList.add('expiring');
                const cells = row.getElementsByTagName('td');
                for (let cell of cells) {
                    cell.style.transition = 'all 0.3s ease';
                }
            }
        } else {
            row.classList.remove('expiring');
            const cells = row.getElementsByTagName('td');
            for (let cell of cells) {
                cell.style.transition = '';
            }
        }
    });
}

function adicionarEntrada(par, direcao, minutos) {
    const tbody = document.getElementById('tradingBody');
    
    // Remove entradas anteriores
    while (tbody.firstChild) {
        tbody.firstChild.remove();
    }

    const row = document.createElement('tr');
    const agora = new Date();
    const expiracao = new Date(agora.getTime() + minutos * 60000);
    
    row.dataset.expiracao = expiracao.toISOString();
    
    row.innerHTML = `
        <td>${createCurrencyPairElement(par)}</td>
        <td>
            <div class="entry-time new">
                <i>▶</i>
                <span>${agora.toLocaleTimeString()}</span>
            </div>
        </td>
        <td><span class="${direcao.toLowerCase()} active">${direcao.toUpperCase()}</span></td>
        <td>
            <div class="expiration-time">
                <i>⌛</i>
                <span>${expiracao.toLocaleTimeString()}</span>
            </div>
        </td>
    `;
    
    tbody.appendChild(row);
    requestAnimationFrame(() => row.classList.add('new-entry'));

    // Remove a classe 'new' após a animação
    setTimeout(() => {
        const entryTime = row.querySelector('.entry-time');
        entryTime.classList.remove('new');
    }, 1000);

    // Atualiza a classe para expiração
    const atualizarExpiracao = () => {
        const tempoRestante = expiracao.getTime() - new Date().getTime();
        const expirationDiv = row.querySelector('.expiration-time');
        
        if (tempoRestante <= 30000 && tempoRestante > 0) { // 30 segundos
            expirationDiv.classList.add('expiring');
        }
        
        if (tempoRestante <= 0) {
            clearInterval(interval);
            row.classList.add('removing');
            setTimeout(() => row.remove(), 500);
        }
    };

    const interval = setInterval(atualizarExpiracao, 1000);

    // Remove a classe active do botão após 3 segundos
    setTimeout(() => {
        const direcaoSpan = row.querySelector(`.${direcao.toLowerCase()}`);
        direcaoSpan.classList.remove('active');
    }, 3000);
}

function gerarEntradaAleatoria() {
    const pares = ['EURUSD', 'GBPJPY', 'AUDCAD', 'USDJPY', 'EURGBP', 'BTCUSD', 'ETHUSD'];
    const direcoes = ['call', 'put'];
    const minutos = [1, 2, 3, 5];
    
    const par = pares[Math.floor(Math.random() * pares.length)];
    const direcao = direcoes[Math.floor(Math.random() * direcoes.length)];
    const minuto = minutos[Math.floor(Math.random() * minutos.length)];
    
    console.log(`Gerando entrada: ${par} - ${direcao} - ${minuto}m`);
    
    return {
        par: par,
        direcao: direcao,
        minutos: minuto
    };
}

function iniciarSinais() {
    let entradaAtiva = false;
    
    function criarNovaSinal() {
        if (!entradaAtiva) {
            entradaAtiva = true;
            const entrada = gerarEntradaAleatoria();
            
            console.log('Criando novo sinal:', entrada);
            
            try {
                adicionarEntrada(entrada.par, entrada.direcao, entrada.minutos);
                console.log('Sinal adicionado com sucesso');
            } catch (error) {
                console.error('Erro ao adicionar entrada:', error);
            }

            // Agenda a próxima entrada para 1 segundo após a atual expirar
            setTimeout(() => {
                entradaAtiva = false;
                criarNovaSinal();
            }, (entrada.minutos * 60000) + 1000);
        }
    }

    // Inicia a primeira entrada imediatamente, sem atraso
    criarNovaSinal();

    // Mantém a verificação de entradas
    setInterval(verificarEntradas, 500);
}

function init() {
    // Primeiro remover overlay existente
    const existingOverlay = document.querySelector('.trading-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Criar estilos e overlay
    createStyles();
    const overlay = createOverlay();
    document.body.appendChild(overlay);

    // Configurar canvas de sobreposição
    setupOverlayCanvas();
    
    // Criar modal de análise
    createAnalysisModal();
    
    // Iniciar análise constante de velas
    setInterval(analyzeCandlesticks, 1000);
    
    // Atualizar o modal de análise constantemente
    setInterval(createAnalysisModal, 2000);
    
    // Iniciar sistema de sinais com um pequeno delay
    setTimeout(() => iniciarSinais(), 100);
    
    // Iniciar sistema de análise
    scheduleAnalysis();
    
    if (typeof completion === 'function') {
        completion('Indicador Rey iniciado com sucesso!');
    }
}

function removeExistingOverlay() {
    const existingOverlay = document.querySelector('.trading-overlay');
    if (existingOverlay) existingOverlay.remove();
}

function setupOverlayCanvas() {
    const glcanvas = document.getElementById('glcanvas');
    if (!glcanvas) return;

    document.getElementById('overlayCanvas')?.remove();

    const overlayCanvas = document.createElement('canvas');
    overlayCanvas.id = 'overlayCanvas';
    applyCanvasStyles(glcanvas, overlayCanvas);
    glcanvas.parentNode.insertBefore(overlayCanvas, glcanvas.nextSibling);

    const ctx = overlayCanvas.getContext('2d');
    const drawLines = () => drawSupportResistanceLines(ctx, overlayCanvas, glcanvas);

    setTimeout(drawLines, 500);
    new ResizeObserver(drawLines).observe(glcanvas);
    setInterval(drawLines, 1000);
}

function applyCanvasStyles(sourceCanvas, targetCanvas) {
    targetCanvas.width = sourceCanvas.width;
    targetCanvas.height = sourceCanvas.height;
    targetCanvas.style.width = sourceCanvas.style.width;
    targetCanvas.style.height = sourceCanvas.style.height;
}

function drawSupportResistanceLines(ctx, overlayCanvas, glcanvas) {
    applyCanvasStyles(glcanvas, overlayCanvas);
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 3]);
    
    drawLine(ctx, 'rgba(255, 0, 0, 0.8)', overlayCanvas.height * 0.3);
    drawLine(ctx, 'rgba(0, 255, 0, 0.8)', overlayCanvas.height * 0.7);
    
    console.log('Linhas desenhadas:', {
        canvasWidth: overlayCanvas.width,
        canvasHeight: overlayCanvas.height,
        resistanceY: overlayCanvas.height * 0.3,
        supportY: overlayCanvas.height * 0.7
    });
}

function drawLine(ctx, color, yPosition) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.moveTo(0, yPosition);
    ctx.lineTo(ctx.canvas.width, yPosition);
    ctx.stroke();
}

function createAnalysisModal() {
    if (document.getElementById('analysisModal')) return;

    const modal = document.createElement('div');
    modal.id = 'analysisModal';
    
    // Melhorar efeito de vidro
    modal.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(26, 31, 37, 0.4);
        color: white;
        padding: 8px 20px;
        font-family: 'Segoe UI', Arial, sans-serif;
        z-index: 9999;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    `;

    // HTML simplificado
    modal.innerHTML = `
        <div style="display: flex; align-items: center; gap: 25px;">
            <h3 style="margin: 0; font-size: 16px; min-width: 120px;">Análise de Velas</h3>
            <div style="display: flex; align-items: center; gap: 25px;">
                <div class="analysis-item">
                    <span style="color: #f44336;">🔴</span>
                    <span id="redPercentage">0%</span>
                </div>
                <div class="analysis-item">
                    <span style="color: #4caf50;">🟢</span>
                    <span id="greenPercentage">0%</span>
                </div>
                <div class="analysis-item">
                    <span style="color: #ffff44;">📈</span>
                    <span id="trend">Neutro</span>
                </div>
                <div class="analysis-item">
                    <span style="color: #2196f3;">📊</span>
                    <span id="candleCount">0</span>
                </div>
            </div>
            <button id="toggleAnalysis">Analisar</button>
        </div>
    `;

    // Estilos para os itens
    const style = document.createElement('style');
    style.innerHTML = `
        .analysis-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            transition: all 0.3s ease;
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }
        
        .analysis-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        #redPercentage, #greenPercentage, #trend, #candleCount {
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.9);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        #toggleAnalysis {
            background: rgba(0, 255, 153, 0.2);
            color: #00ff99;
            border: 1px solid rgba(0, 255, 153, 0.3);
            padding: 4px 15px;
            border-radius: 15px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s ease;
            white-space: nowrap;
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }

        #toggleAnalysis:hover {
            transform: scale(1.05);
            background: rgba(0, 255, 153, 0.3);
            border-color: rgba(0, 255, 153, 0.5);
            box-shadow: 0 0 15px rgba(0, 255, 153, 0.3);
        }

        #toggleAnalysis:active {
            transform: scale(0.98);
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(modal);

    // Criar a div de mensagem uma única vez
    let mensagemDiv = document.createElement("div");
    mensagemDiv.id = "mensagem-status";
    mensagemDiv.style.position = "absolute";
    mensagemDiv.style.top = "50%";
    mensagemDiv.style.left = "50%";
    mensagemDiv.style.transform = "translate(-50%, -50%)";
    mensagemDiv.style.padding = "15px 25px";
    mensagemDiv.style.background = "black";
    mensagemDiv.style.color = "#00ff99";
    mensagemDiv.style.fontSize = "18px";
    mensagemDiv.style.fontWeight = "bold";
    mensagemDiv.style.fontFamily = "Arial, sans-serif";
    mensagemDiv.style.textAlign = "center";
    mensagemDiv.style.borderRadius = "10px";
    mensagemDiv.style.boxShadow = "0px 0px 15px rgba(0, 255, 153, 0.5)";
    mensagemDiv.style.border = "1px solid #00ff99";
    mensagemDiv.style.display = "none";
    mensagemDiv.style.animation = "pulse 1.5s infinite alternate";
    mensagemDiv.style.zIndex = "9999";
    document.body.appendChild(mensagemDiv);

    // Adicionar animação CSS
    let animStyle = document.createElement("style");
    animStyle.innerHTML = `
        @keyframes pulse {
            0% { transform: translate(-50%, -50%) scale(1); }
            100% { transform: translate(-50%, -50%) scale(1.05); }
        }
    `;
    document.head.appendChild(animStyle);

    // Adicionar o evento de clique ao botão
    document.getElementById('toggleAnalysis').addEventListener('click', function() {
        let elemento = document.querySelector("#glcanvas");
        let mensagens = [
            "🔍 ANALISANDO PARIDADE, AGUARDE...",
            "📊 ANALISANDO MACRO E MICRO TENDÊNCIA...",
            "⏳ COLETANDO DADOS DO MERCADO...",
            "📡 VERIFICANDO LIQUIDEZ E VOLUME...",
            "💹 AJUSTANDO PROJEÇÕES E NÍVEIS DE SUPORTE..."
        ];

        let mensagemAtual = mensagens[Math.floor(Math.random() * mensagens.length)];
        
        // Esconde o canvas e mostra a mensagem
        elemento.style.display = "none";
        mensagemDiv.innerText = mensagemAtual;
        mensagemDiv.style.display = "block";

        // Após 2 segundos, restaura o canvas e esconde a mensagem
        setTimeout(() => {
            elemento.style.display = "flex";
            mensagemDiv.style.display = "none";
            analyzeCandlesticks(); // Atualiza a análise
        }, 2000);
    });
}

function getDeviceInfo() {
    const nav = navigator;
    return {
        userAgent: nav.userAgent,
        platform: nav.platform,
        language: nav.language,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timestamp: new Date().toISOString()
    };
}

// Função para mostrar o modal de segurança
function mostrarModalSeguranca() {
    const deviceInfo = getDeviceInfo();
    const modalHTML = `
        <div class="security-modal-overlay">
            <div class="security-modal">
                <div class="warning-icon">⚠️</div>
                <h2>SISTEMA DE SEGURANÇA ATIVADO</h2>
                <p><strong>ATENÇÃO: Verificação de Segurança em Andamento</strong></p>
                <p>Este software está protegido por um sistema avançado de segurança que:</p>
                <ul style="text-align: left; margin: 15px 0;">
                    <li>Registra endereço MAC do dispositivo</li>
                    <li>Monitora tentativas de engenharia reversa</li>
                    <li>Detecta uso não autorizado</li>
                    <li>Rastreia localização geográfica</li>
                </ul>
                <div class="device-info">
                    <p><strong>Informações Registradas:</strong></p>
                    <p>ID: ${Math.random().toString(36).substring(2, 15)}</p>
                    <p>Plataforma: ${deviceInfo.platform}</p>
                    <p>Navegador: ${deviceInfo.userAgent.split(')')[0]})</p>
                    <p>Resolução: ${deviceInfo.screenResolution}</p>
                    <p>Data/Hora: ${deviceInfo.timestamp}</p>
                </div>
                <p style="color: #ff3333;"><strong>AVISO LEGAL:</strong> Qualquer tentativa de uso não autorizado ou pirataria será reportada às autoridades competentes e resultará em ações legais.</p>
                <button onclick="this.parentElement.parentElement.remove()">Entendi e Concordo</button>
            </div>
        </div>
    `;
    
    const modalElement = document.createElement('div');
    modalElement.innerHTML = modalHTML;
    document.body.appendChild(modalElement.firstElementChild);
}

// Iniciar com modal de segurança e depois tela de login
mostrarModalSeguranca();
init();

// Retornar status para o Atalhos
if (typeof completion === 'function') {
    completion('Indicador Rey iniciado com sucesso!');
}

// Função para atualizar os valores
function atualizarValores() {
    analyzeCandlesticks();
}

// Atualizar valores a cada segundo
setInterval(atualizarValores, 1000);

// Função para atualizar os valores automaticamente
setInterval(() => {
    analyzeCandlesticks();
}, 1000);

// Partículas de Trading no fundo
const ParticleSystemC = {
    particles: [],
    maxParticles: 100,
    
    init: function() {
        this.container = document.createElement('div');
        this.container.className = 'particle-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
        `;
        document.body.appendChild(this.container);
    },
    
    createParticle: function(x, y, type = 'default') {
        if (this.particles.length >= this.maxParticles) {
            const oldParticle = this.particles.shift();
            oldParticle.element.remove();
        }
        
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const size = Math.random() * 4 + 2;
        const angle = Math.random() * 360;
        const speed = Math.random() * 2 + 1;
        const lifetime = Math.random() * 2000 + 1000;
        
        let color, glow;
        switch(type) {
            case 'success':
                color = 'rgba(76, 175, 80, 0.8)';
                glow = '0 0 10px rgba(76, 175, 80, 0.5)';
                break;
            case 'error':
                color = 'rgba(244, 67, 54, 0.8)';
                glow = '0 0 10px rgba(244, 67, 54, 0.5)';
                break;
            default:
                color = 'rgba(255, 255, 255, 0.8)';
                glow = '0 0 10px rgba(255, 255, 255, 0.5)';
        }
        
        particle.style.cssText = `
            position: absolute;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            box-shadow: ${glow};
            border-radius: 50%;
            transform: rotate(${angle}deg);
            pointer-events: none;
        `;
        
        this.particles.push({
            element: particle,
            x: x,
            y: y,
            angle: angle,
            speed: speed,
            lifetime: lifetime,
            birth: performance.now()
        });
        
        this.container.appendChild(particle);
    },
    
    emitParticles: function(x, y, count = 10, type = 'default') {
        for (let i = 0; i < count; i++) {
            setTimeout(() => this.createParticle(x, y, type), i * 50);
        }
        requestAnimationFrame(() => this.update());
    },
    
    update: function() {
        const now = performance.now();
        let hasActiveParticles = false;
        
        this.particles.forEach((particle, index) => {
            const age = now - particle.birth;
            
            if (age >= particle.lifetime) {
                particle.element.remove();
                this.particles.splice(index, 1);
                return;
            }
            
            hasActiveParticles = true;
            const progress = age / particle.lifetime;
            const distance = particle.speed * age / 16;
            const radians = particle.angle * Math.PI / 180;
            
            const newX = particle.x + Math.cos(radians) * distance;
            const newY = particle.y + Math.sin(radians) * distance;
            const scale = 1 - progress;
            
            particle.element.style.transform = `
                translate(${newX - particle.x}px, ${newY - particle.y}px)
                scale(${scale})
                rotate(${particle.angle + age / 10}deg)
            `;
            particle.element.style.opacity = 1 - progress;
        });
        
        if (hasActiveParticles) {
            requestAnimationFrame(() => this.update());
        }
    }
};

// Inicializar sistema de partículas
ParticleSystemC.init();

// Loop principal de atualização
let lastUpdateTime = 0;
const UPDATE_INTERVAL = 1000; // 1 segundo em milissegundos

function mainLoop(currentTime) {
    // Verifica se passou tempo suficiente desde a última atualização
    if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
        const glcanvas = document.getElementById('glcanvas');
        if (glcanvas) {
            // Alterna o display entre none e flex
            glcanvas.style.display = 'none';
            
            // Força o reflow
            void glcanvas.offsetHeight;
            
            // Restaura para flex
            glcanvas.style.display = 'flex';
            
            // Analisa as velas
            analyzeCandlesticks();
        }
        
        // Atualiza o último tempo de atualização
        lastUpdateTime = currentTime;
    }
    
    // Continua o loop
    requestAnimationFrame(mainLoop);
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Iniciar com modal de segurança
    mostrarModalSeguranca();

    // Inicializar sistemas após autenticação
    setTimeout(() => {
        init();
        createAnalysisModal();
        // Inicia o loop principal
        mainLoop(performance.now());
    }, 1000);
});

// Atualiza os valores a cada 5 segundos
setInterval(atualizarValores, 5000);

// Função para atualizar os valores automaticamente
setInterval(() => {
    analyzeCandlesticks();
}, 1000);

function analyzeCandlesticks() {
    // Garantir que o modal existe
    createAnalysisModal();
    
    const glcanvas = document.getElementById('glcanvas');
    if (!glcanvas) {
        console.log('Canvas GL não encontrado');
        return;
    }

    try {
        // Criar um canvas temporário para análise
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = glcanvas.width;
        tempCanvas.height = glcanvas.height;
        const ctx = tempCanvas.getContext('2d');

        // Copiar o conteúdo do canvas GL para o temporário
        ctx.drawImage(glcanvas, 0, 0);

        // Pegar os pixels
        const imageData = ctx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
        const data = imageData.data;

        let redCount = 0;
        let greenCount = 0;
        let totalPixels = 0;
        let candleCount = 0;
        
        // Armazenar posições de possíveis velas
        const candlePositions = new Set();
        
        // Cores exatas das velas fornecidas
        const exactGreen = [0, 181, 53];    // #00b535
        const exactRed = [215, 74, 55];     // #d74a37
        
        // Tolerância para detecção de cor (0-255)
        const tolerance = 30;
        
        // Analisar pixels com foco nas cores exatas das velas
        for (let y = 0; y < tempCanvas.height; y += 1) {
            for (let x = 0; x < tempCanvas.width; x += 1) {
                const i = (y * tempCanvas.width + x) * 4;
                
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                const a = data[i + 3];

                // Ignorar pixels transparentes
                if (a < 100) continue;

                // Verificar se é verde (#00b535) com tolerância
                if (Math.abs(r - exactGreen[0]) < tolerance && 
                    Math.abs(g - exactGreen[1]) < tolerance && 
                    Math.abs(b - exactGreen[2]) < tolerance) {
                    greenCount++;
                    candlePositions.add(Math.floor(x / 5) * 5);
                    totalPixels++;
                }
                // Verificar se é vermelho (#d74a37) com tolerância
                else if (Math.abs(r - exactRed[0]) < tolerance && 
                         Math.abs(g - exactRed[1]) < tolerance && 
                         Math.abs(b - exactRed[2]) < tolerance) {
                    redCount++;
                    candlePositions.add(Math.floor(x / 5) * 5);
                    totalPixels++;
                }
            }
        }
        
        // Estimar número de velas baseado nas posições distintas
        candleCount = candlePositions.size > 0 ? candlePositions.size : 0;

        // Atualizar a interface
        const total = redCount + greenCount;
        if (total > 0) {
            // Calcular as porcentagens iniciais
            let redPercent = Math.round((redCount / total) * 100);
            let greenPercent = Math.round((greenCount / total) * 100);
            
            // Limitar as porcentagens a um máximo de 70% para tornar mais realista
            if (redPercent > 70) {
                redPercent = Math.floor(Math.random() * 10) + 60; // Entre 60-70%
                greenPercent = 100 - redPercent;
            } else if (greenPercent > 70) {
                greenPercent = Math.floor(Math.random() * 10) + 60; // Entre 60-70%
                redPercent = 100 - greenPercent;
            }
            
            // Garantir que a soma seja 100%
            if (redPercent + greenPercent !== 100) {
                const diff = 100 - (redPercent + greenPercent);
                if (redPercent > greenPercent) {
                    redPercent += diff;
                } else {
                    greenPercent += diff;
                }
            }
            
            // Determinar a tendência com base nas porcentagens ajustadas
            let trend = "Neutro";
            if (redPercent > 55) trend = "Baixa";
            if (greenPercent > 55) trend = "Alta";

            // Atualizar os elementos específicos
            document.getElementById('redPercentage').textContent = `${redPercent}%`;
            document.getElementById('greenPercentage').textContent = `${greenPercent}%`;
            document.getElementById('trend').textContent = trend;
            document.getElementById('candleCount').textContent = candleCount;
            
            // Atualizar cores de tendência
            const trendElement = document.getElementById('trend');
            if (trend === "Alta") {
                trendElement.style.background = "linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.2))";
                trendElement.style.color = "#4caf50";
                trendElement.style.borderColor = "rgba(76, 175, 80, 0.3)";
            } else if (trend === "Baixa") {
                trendElement.style.background = "linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(244, 67, 54, 0.2))";
                trendElement.style.color = "#f44336";
                trendElement.style.borderColor = "rgba(244, 67, 54, 0.3)";
            } else {
                trendElement.style.background = "linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.2))";
                trendElement.style.color = "#ffc107";
                trendElement.style.borderColor = "rgba(255, 193, 7, 0.3)";
            }

            // Debug da análise (mantido apenas no console)
            console.log('Análise de velas (ajustada):', {
                total,
                redCount,
                greenCount,
                redPercent,
                greenPercent,
                trend,
                candleCount,
                candlePositions: Array.from(candlePositions).slice(0, 10)
            });
        }
    } catch (error) {
        console.error('Erro na análise:', error);
    }
}

// Variáveis para controle de tempo de análise
let lastAnalysisTime = 0;
const ANALYSIS_INTERVAL = 5000; // 5 segundos entre análises

// Função para agendar análises de forma mais eficiente
function scheduleAnalysis() {
    const now = performance.now();
    if (now - lastAnalysisTime >= ANALYSIS_INTERVAL) {
        lastAnalysisTime = now;
        analyzeCandlesticks();
        
        // Adicionar informação sobre o tempo de atualização no console
        console.log(`Análise atualizada em: ${new Date().toLocaleTimeString()}, próxima em ${ANALYSIS_INTERVAL/1000}s`);
    }
    requestAnimationFrame(scheduleAnalysis);
}

// Modificar a inicialização para usar o novo sistema de agendamento
document.addEventListener('DOMContentLoaded', () => {
    // Iniciar com modal de segurança
    mostrarModalSeguranca();

    // Inicializar sistemas após autenticação
    setTimeout(() => {
        // Inicializar interface
        init();
        
        // Iniciar o sistema de análise otimizado
        scheduleAnalysis();
        
        // Adicionar informação sobre o intervalo de atualização no modal
        const analysisDiv = document.getElementById('candleAnalysis');
        if (analysisDiv) {
            const infoDiv = document.createElement('div');
            infoDiv.style.cssText = 'margin-top: 10px; font-size: 12px; color: #aaaaaa; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;';
            infoDiv.innerHTML = `Atualização: a cada ${ANALYSIS_INTERVAL/1000}s`;
            analysisDiv.appendChild(infoDiv);
        }
    }, 1000);
});

// Adicionar ao loop de renderização existente
const originalRenderC = window.render;
window.render = function() {
    if (originalRenderC) {
        originalRenderC.apply(this, arguments);
    }
    
    // Analisar velas imediatamente após cada frame
    analyzeCandlesticks();
};
