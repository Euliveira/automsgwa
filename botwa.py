import os
import time
import random
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# ================= CONFIGURAÇÕES PRINCIPAIS =================
CONFIG = {
    "EXCECOES": [
        "Adoradores", "DESAFIO BIBLICO", "DESAFIO BIBLICO 📖", 
        "Enquete Biblica", "Anotações", "Você"
    ],
    "LINK_RODAPE": "https://whatsapp.com/channel/0029VaI00LD8PgsByJRPLi0D",
    "INTERVALO_ENVIO": 1200
}

# Sua nova mensagem base com formatação especial e emoticons de moldura
MENSAGENS_BASE = [
    """┏╮╭┓           ┏╮╭┓  
   🌹  ◇◇◇◇  🌻      
┗╯╰┛           ┗╯╰┛   

*𝔸𝕕𝕠𝕣𝕒𝕕𝕠𝕣𝕖𝕤*

*Ainda que mil pessoas sejam mortas ao seu lado e dez mil, ao seu redor, você não sofrerá nada.*
*Você olhará e verá como os maus são castigados.*

      *(📖Salmos 91:7-8)*

*Deseja receber mais mensagens como essa? Siga nosso canal.*
*Aqui vocês encontram:*

➡️ Devocionais
➡️ Pedido de oração
➡️ Louvores
➡️ Testemunhos
➡️ Mensagens motivacionais


*Não perca mais tempo, entre agora mesmo e vamos adorar ao Senhor.*

           ┏╮╭┓          ┏╮╭┓  
              🌹 ◇◇◇◇  🌻
           ┗╯╰┛          ┗╯╰┛"""
]

def digitar_como_humano(page, seletor, texto):
    page.focus(seletor)
    for caractere in texto:
        if caractere == '\n':
            page.keyboard.down("Shift")
            page.keyboard.press("Enter")
            page.keyboard.up("Shift")
        else:
            page.keyboard.type(caractere)
        time.sleep(random.uniform(0.01, 0.03))

def carregar_pagina_com_retry(page, url, tentativas=3):
    for i in range(tentativas):
        try:
            print(f"[WhatsApp] Acessando a plataforma (Tentativa {i+1}/{tentativas})...")
            page.goto(url, timeout=120000, wait_until="networkidle")
            return True
        except Exception as e:
            print(f"[Aviso] Falha ao carregar página: {e}")
            if i < tentativas - 1:
                time.sleep(5)
            else:
                raise e

def disparar_rotina_automatica():
    print(f"\n--- Iniciando ciclo automático de varredura (Texto): {datetime.now().strftime('%H:%M:%S')} ---")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            './minha_sessao_robotica',
            headless=False,  
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            args=[
                '--start-maximized',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        page = context.new_page()
        
        # ESCUDO ANTI-DIALOGO: Fecha e descarta qualquer alerta/pop-up nativo do WhatsApp automaticamente
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        try:
            carregar_pagina_com_retry(page, "https://web.whatsapp.com")
        except Exception:
            context.close()
            return
        
        print("[WhatsApp] Aguardando a página gerar o QR Code ou os chats (Limite de 5 min)...")
        try:
            page.wait_for_selector('canvas, div[data-testid="chat-list"], div[id="pane-side"]', timeout=300000)
            print("⚡ Tela inicial carregada com sucesso!")
        except Exception:
            print("\n[Erro] O WhatsApp não exibiu o QR Code nem os chats a tempo.")
            context.close()
            return

        if page.is_visible('canvas'):
            print("\n📸 [Atenção] O QR Code está na tela do ROBÔ! Pegue seu celular e escaneie AGORA nesta janela.")
            print("[Status] Aguardando você escanear e o WhatsApp sincronizar as mensagens...")
            try:
                page.wait_for_selector('div[data-testid="chat-list"], div[id="pane-side"]', timeout=180000)
                print("⚡ Perfeito! QR Code lido e conta conectada.")
            except:
                print("\n[Erro] Tempo limite esgotado para a leitura do QR Code.")
                context.close()
                return
        else:
            print("⚡ Sessão existente detectada! Entrando direto...")

        time.sleep(5) 
        
        grupos_processados = set()
        seletor_titulo_chat = 'span[title][dir="auto"]'
        seletor_caixa_texto = 'div[contenteditable="true"][data-testid="conversation-compose-box-input"]'
        
        for scroll in range(5):
            if page.is_closed():
                break
                
            page.wait_for_timeout(1500)
            try:
                elementos_chats = page.query_selector_all(seletor_titulo_chat)
            except:
                break
            
            for elemento in elementos_chats:
                try:
                    if page.is_closed() or not elemento.is_visible():
                        continue
                        
                    nome_chat = elemento.get_attribute("title")
                    
                    if not nome_chat or nome_chat in grupos_processados:
                        continue
                        
                    if any(excecao.lower() in nome_chat.lower() for excecao in CONFIG["EXCECOES"]):
                        print(f"[Ignorado] O chat '{nome_chat}' está na lista de exceções.")
                        grupos_processados.add(nome_chat)
                        continue
                    
                    print(f"\n[Bot] Grupo descoberto: {nome_chat}")
                    grupos_processados.add(nome_chat)
                    
                    elemento.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    
                    elemento.click(force=True)
                    
                    try:
                        page.wait_for_selector(seletor_caixa_texto, timeout=5000)
                    except:
                        print(f"[Aviso] O grupo '{nome_chat}' parece restrito a admins ou travou. Pulando...")
                        continue
                    
                    mensagem_aleatoria = random.choice(MENSAGENS_BASE)
                    texto_final = f"{mensagem_aleatoria}\n\n👉 {CONFIG['LINK_RODAPE']}"
                    
                    print("[Texto] Digitando a mensagem...")
                    digitar_como_humano(page, seletor_caixa_texto, texto_final)
                        
                    time.sleep(1.5)
                    page.keyboard.press("Enter")
                    print(f"[Sucesso] Enviado para: {nome_chat}")
                    
                    tempo_espera = random.uniform(35.0, 65.0)
                    print(f"Aguardando {int(tempo_espera)} segundos antes do próximo alvo...")
                    time.sleep(tempo_espera)
                    
                except Exception as e:
                    print(f"[Aviso] Erro rápido ignorado no chat: {e}")
                    try:
                        page.keyboard.press("Escape")
                    except:
                        pass
            
            if not page.is_closed():
                print("[Sistema] Rolando barra lateral...")
                try:
                    page.evaluate('document.querySelector("#pane-side").scrollBy(0, 500)')
                    time.sleep(4)
                except:
                    pass
        
        print(f"\n[Concluído] Ciclo encerrado. Total de chats validados: {len(grupos_processados)}")
        try:
            context.close()
        except:
            pass

if __name__ == "__main__":
    print("Robô de Varredura Automática (Apenas Texto) Inicializado.")
    while True:
        disparar_rotina_automatica()
        print("Aguardando intervalo de 20 minutos para o próximo ciclo...")
        time.sleep(CONFIG["INTERVALO_ENVIO"])