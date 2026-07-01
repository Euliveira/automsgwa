import os
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

# ================= CONFIGURAÇÕES PRINCIPAIS =================
CONFIG = {
    # 🚫 LISTA DE EXCEÇÕES: O bot vai ignorar estes grupos automaticamente
    "EXCECOES": [
        "Adoradores",
        "DESAFIO BIBLICO",
        "📖 DESAFIO BIBLICO",
        "Enquete Biblica",
        "Anotações",
        "Você" # Evita mandar no seu próprio chat privado
    ],
    
    # O link do canal fixado no rodapé do texto
    "LINK_RODAPE": "https://whatsapp.com/channel/0029VaI00LD8PgsByJRPLi0D",
    
    # Intervalo de envio entre os ciclos gerais: 20 minutos (1200 segundos)
    "INTERVALO_ENVIO": 1200,

    # 📸 CONFIGURAÇÃO DE MÍDIA: A imagem PRECISA estar na mesma pasta com este nome exato
    "CAMINHO_IMAGEM": os.path.abspath("adoradores2.png")
}

MENSAGENS_BASE = [
    """
╒ ╓ ╔ ╕╖ ╗ ╘ ╙ ╚ ╛ ╜ ╝ ╒ ╓ ╔ ╕╖ ╗  


*"𝙊 𝙎𝙚𝙣𝙝𝙤𝙧 𝙚́ 𝙢𝙚𝙪 𝙥𝙖𝙨𝙩𝙤𝙧, 𝙚 𝙣𝙖𝙙𝙖 𝙢𝙚 𝙛𝙖𝙡𝙩𝙖𝙧𝙖́."*

      *(📖Salmos Salmos 23:1)*

*A dependency total do bom Pastor transforma a escassez do caminho em plena suficiência de alma.
Sob o cuidado de Deus, o amanhã deixa de ser uma incerteza e passa a ser um porto seguro.
Confie os seus passos à liderança do Altíssimo, pois quem caminha com Ele jamais ficará desamparado.*

*Deseja receber mais mensagens como essa? Siga nosso canal.*


*Não perca mais tempo, entre agora mesmo e vamos adorar ao Senhor.*

╒ ╓ ╔ ╕╖ ╗ ╘ ╙ ╚ ╛ ╜ ╝ ╒ ╓ ╔ ╕╖ ╗

"""
]

def digitar_como_humano(page, seletor, texto):
    """Simula a digitação real e trata o Shift+Enter para pular linha."""
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
            page.goto(url, timeout=120000, wait_until="commit")
            page.wait_for_timeout(10000)  # Estabilização inicial da página
            return True
        except Exception as e:
            print(f"[Aviso] Falha ao carregar página: {e}")
            if i < tentativas - 1:
                time.sleep(5)
            else:
                raise e

def disparar_rotina_automatica():
    print(f"\n--- Iniciando ciclo automático de varredura (Imagem + Texto): {datetime.now().strftime('%H:%M:%S')} ---")

    # Garante que a imagem existe antes de abrir o navegador
    if not os.path.exists(CONFIG["CAMINHO_IMAGEM"]):
        print(f"\n[ERRO CRÍTICO] A imagem não foi encontrada em: {CONFIG['CAMINHO_IMAGEM']}")
        print("Por favor, certifique-se de colocar o arquivo 'adoradores2.png' na mesma pasta do script.")
        return

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            './minha_sessao_robotica',
            headless=False,
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            args=[
                '--start-maximized',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        page = context.new_page()
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        try:
            carregar_pagina_com_retry(page, "https://web.whatsapp.com")
        except Exception:
            context.close()
            return
        
        painel_lateral = 'div[id="pane-side"]'
        
        print("[WhatsApp] Verificando conexão...")
        try:
            page.wait_for_selector('canvas, div[data-testid="chat-list"], ' + painel_lateral, timeout=300000)
        except Exception:
            print("\n[Erro] Tempo limite de carregamento esgotado.")
            context.close()
            return

        if page.is_visible('canvas'):
            print("\n📸 [Atenção] O QR Code apareceu! Pegue o celular e escaneie agora (Limite de 3 minutos)...")
            try:
                page.wait_for_selector(painel_lateral, timeout=180000)
                print("⚡ Perfeito! Conectado e autenticado com sucesso.")
            except Exception:
                print("\n[Erro] Tempo esgotado para escanear o QR Code.")
                context.close()
                return
        else:
            print("⚡ Sessão existente detectada! Entrando direto...")

        time.sleep(5) 
        
        grupos_processados = set()
        seletor_titulo_chat = 'span[title][dir="auto"]'
        seletor_caixa_texto = 'div[contenteditable="true"][data-testid="conversation-compose-box-input"]'
        
        # Seletores dinâmicos e redundantes para maior estabilidade
        seletor_botao_anexo = 'div[aria-label="Anexar"], button[aria-label="Anexar"], div[role="button"][aria-label="Anexar"], button[data-testid="attach-menu-plus"]'
        seletor_input_arquivo = 'input[accept*="image"], input[accept*="video"], input[type="file"]'
        seletor_legenda_imagem = 'div[data-testid="media-editor-caption-input"], div[contenteditable="true"][placeholder*="legenda"], div[role="textbox"]'

        for scroll in range(5):
            if page.is_closed():
                break
                
            elementos_chats = page.query_selector_all(seletor_titulo_chat)
            
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
                    
                    print(f"\n[Bot] Grupo descobor: {nome_chat}")
                    grupos_processados.add(nome_chat)
                    
                    elemento.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    elemento.click(force=True)
                    
                    # Sincronização: garante que o chat abriu antes de disparar o fluxo de mídia
                    try:
                        page.wait_for_selector(seletor_caixa_texto, timeout=15000)
                    except Exception:
                        print(f"[Aviso] O grupo '{nome_chat}' demorou muito para carregar ou está restrito. Pulando...")
                        continue
                    
                    # --- INÍCIO DO FLUXO DE MÍDIA ---
                    print("[Mídia] Abrindo menu de anexos...")
                    page.wait_for_selector(seletor_botao_anexo, timeout=10000)
                    page.locator(seletor_botao_anexo).first.click()
                    time.sleep(1.5)

                    print("[Mídia] Injetando o arquivo de imagem...")
                    page.locator(seletor_input_arquivo).first.set_input_files(CONFIG["CAMINHO_IMAGEM"])
                    
                    print("[Mídia] Aguardando processamento e tela de legenda...")
                    try:
                        page.wait_for_selector(seletor_legenda_imagem, timeout=20000)
                    except Exception as erro_timeout:
                        # Se der timeout na legenda, gera o screenshot de diagnóstico
                        nome_print = "debug_erro_midia.png"
                        page.screenshot(path=nome_print)
                        print(f"[ERRO DE SINCRONIZAÇÃO] A tela de legenda não apareceu a tempo.")
                        print(f"👉 Captura de tela salva como '{nome_print}' para análise.")
                        raise erro_timeout
                    
                    mensagem_aleatoria = random.choice(MENSAGENS_BASE)
                    texto_final = f"{mensagem_aleatoria}\n\n👉 {CONFIG['LINK_RODAPE']}"
                    
                    print("[Texto] Digitando a mensagem na legenda da imagem...")
                    digitar_como_humano(page, seletor_legenda_imagem, texto_final)
                        
                    time.sleep(1.5)
                    page.keyboard.press("Enter")
                    print(f"[Sucesso] Imagem + Texto enviados para: {nome_chat}")
                    
                    tempo_espera = random.uniform(35.0, 65.0)
                    print(f"Aguardando {int(tempo_espera)} segundos antes do próximo alvo (Antiban)...")
                    time.sleep(tempo_espera)
                    
                except Exception as e:
                    print(f"[Aviso] Não foi possível interagir com o chat '{nome_chat}': {e}")
                    try:
                        page.keyboard.press("Escape")
                        time.sleep(1)
                        page.keyboard.press("Escape")
                    except:
                        pass
            
            if not page.is_closed():
                print("[Sistema] Rolando a barra lateral para buscar novos grupos...")
                try:
                    page.evaluate(f'document.querySelector("{painel_lateral}").scrollBy(0, 500)')
                    time.sleep(4)
                except:
                    pass
        
        print(f"\n[Concluído] Ciclo encerrado. Total de chats validados: {len(grupos_processados)}")
        context.close()

if __name__ == "__main__":
    print("Robô de Varredura Automática (Imagem + Texto) Inicializado.")
    while True:
        disparar_rotina_automatica()
        print("Aguardando intervalo de 20 minutos para o próximo ciclo completo...")
        time.sleep(CONFIG["INTERVALO_ENVIO"])
