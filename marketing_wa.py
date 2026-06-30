import os
import time
import random
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# ================= CONFIGURAÇÕES GERAIS DA OPERAÇÃO =================
CONFIG = {
    "NICHO_ATIVO": "NEGOCIO_LOCAL",  # Opções: 'AFILIADOS', 'NEGOCIO_LOCAL', 'STORYTELLING'
    "EXCECOES": [
        "Adoradores", "DESAFIO BIBLICO", "Anotações", "Você", "Suporte", "Admin"
    ],
    "LINK_RODAPE": "https://seu-link-rastreado.com/utm_source=wa_bot",
    "INTERVALO_CICLOS": 1200,  # Tempo de espera em segundos entre varreduras completas
}

# ================= BANCO DE DADOS DE SPINTAX (MULTINICHO) =================
NICHOS_CONFIG = {
    "AFILIADOS": {
        "SAUDACOES": ["Gente,", "Olá pessoal,", "Opa, desculpa incomodar,", "Fala galera!"],
        "INTRODUCOES": [
            "vcs viram que abriu um canal aqui no Whats que tá mandando cupons de até 80% pra Amazon e Magalu?",
            "acabei de achar um grupo de promoções que tá vazando uns bugs de desconto muito insanos.",
            "achei esse canal de ofertas aqui e já economizei uma grana hoje kkkk."
        ],
        "CHAMADAS": [
            "Tô deixando o acesso aqui antes que o link expire ou apaguem 👇",
            "Quem curte economizar e pegar promoção de verdade, vale a pena entrar 👇",
            "Vou mandar o link aqui embaixo para ajudar vcs 👇"
        ],
        "CORPO": "Como esse grupo aqui é bem movimentado, achei que vcs iam curtir a dica para não perder os descontos do mês."
    },
    
    "NEGOCIO_LOCAL": {
        "SAUDACOES": ["Fala pessoal, beleza?", "Olá a todos,", "Opa gente! Tudo bem?", "Boa galera,"],
        "INTRODUCOES": [
            "Passando rápido pra avisar quem mora na região que liberaram uma ação exclusiva essa semana.",
            "Tenho uma novidade excelente para quem é daqui do bairro e quer aproveitar uma oportunidade única.",
            "Olha que bacana o que estão fazendo para os moradores da nossa cidade nos próximos dias:"
        ],
        "CHAMADAS": [
            "Eles liberaram poucos vouchers com desconto especial, então clica aí pra garantir o seu antes que acabe 👇",
            "Basta chamar o atendimento deles no link oficial e pedir o seu benefício 👇",
            "Vou deixar o link direto deles bem aqui embaixo 👇"
        ],
        "CORPO": "Estão distribuindo vouchers promocionais de até 40% para os primeiros que entrarem em contato pelo WhatsApp comercial."
    },
    
    "STORYTELLING": {
        "SAUDACOES": ["Caramba galera,", "Gente, vcs viram isso?", "Olha que bizarro,", "Rapaz, inacreditável..."],
        "INTRODUCOES": [
            "vcs ficaram sabendo daquela história da profissional daqui da área que pediu demissão após descobrir uma brecha?",
            "vi um relato de uma pessoa comum que conseguiu mudar de vida usando apenas o celular e uma estratégia simples.",
            "acabei de ver um caso real de um negócio que faturou alto aplicando uma técnica simples sem investir em anúncios."
        ],
        "CHAMADAS": [
            "Ela gravou um vídeo curto explicando exatamente a lógica, o link tá aqui 👇",
            "Se vc quiser entender como funciona esse modelo, dá uma olhada na página oficial 👇",
            "Assiste o vídeo antes que tirem do ar, explica tudo direitinho 👇"
        ],
        "CORPO": "No começo achei que era mentira, mas depois que vi a explicação técnica e os resultados práticos, fez total sentido."
    }
}

def gerar_mensagem_dinamica(nicho):
    """
    Gera uma mensagem em Spintax baseada no nicho selecionado,
    garantindo quebras de padrões de hash no WhatsApp.
    """
    dados = NICHOS_CONFIG.get(nicho, NICHOS_CONFIG["AFILIADOS"])
    
    saudacao = random.choice(dados["SAUDACOES"])
    introducao = random.choice(dados["INTRODUCOES"])
    chamada = random.choice(dados["CHAMADAS"])
    corpo = dados["CORPO"]
    
    mensagem = f"""{saudacao} {introducao}

{corpo}

{chamada}"""
    return mensaje

def digitar_como_humano(page, seletor, texto):
    page.focus(seletor)
    for caractere in texto:
        if caractere == '\n':
            page.keyboard.down("Shift")
            page.keyboard.press("Enter")
            page.keyboard.up("Shift")
        else:
            page.keyboard.type(caractere)
        time.sleep(random.uniform(0.01, 0.04))  # Humanização do tempo de clique por tecla

def carregar_pagina_com_retry(page, url, tentativas=3):
    for i in range(tentativas):
        try:
            print(f"[WhatsApp] Acessando a plataforma (Tentativa {i+1}/{tentativas})...")
            page.goto(url, timeout=120000, wait_until="networkidle")
            return True
        except Exception as e:
            print(f"[Aviso] Falha ao carregar página: {e}")
            if i < tentatives - 1:
                time.sleep(5)
            else:
                raise e

def disparar_rotina_automatica():
    nicho_atual = CONFIG["NICHO_ATIVO"]
    print(f"\n--- Iniciando ciclo automático de varredura [{nicho_atual}]: {datetime.now().strftime('%H:%M:%S')} ---")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            './sessao_comercial_robotica',
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
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        try:
            carregar_pagina_com_retry(page, "https://web.whatsapp.com")
        except Exception:
            context.close()
            return
        
        print("[WhatsApp] Aguardando autenticação ou carregamento dos chats...")
        try:
            page.wait_for_selector('canvas, div[data-testid="chat-list"], div[id="pane-side"]', timeout=300000)
            print("⚡ Tela inicial detectada!")
        except Exception:
            print("\n[Erro] Tempo limite de carregamento excedido.")
            context.close()
            return

        if page.is_visible('canvas'):
            print("\n📸 [Atenção] Realize o escaneamento do QR Code no navegador aberto.")
            try:
                page.wait_for_selector('div[data-testid="chat-list"], div[id="pane-side"]', timeout=180000)
                print("⚡ Conta conectada com sucesso!")
            except:
                print("\n[Erro] Autenticação expirada.")
                context.close()
                return
        else:
            print("⚡ Sessão ativa recuperada com sucesso.")

        time.sleep(5) 
        
        grupos_processados = set()
        seletor_titulo_chat = 'span[title][dir="auto"]'
        seletor_caixa_texto = 'div[contenteditable="true"][data-testid="conversation-compose-box-input"]'
        
        # Realiza varredura vertical simulando scroll contínuo
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
                        print(f"[Ignorado] Alvo em exceção: '{nome_chat}'")
                        grupos_processados.add(nome_chat)
                        continue
                    
                    print(f"\n[Bot] Alvo elegível encontrado: {nome_chat}")
                    grupos_processados.add(nome_chat)
                    
                    elemento.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    elemento.click(force=True)
                    
                    try:
                        page.wait_for_selector(seletor_caixa_texto, timeout=5000)
                    except:
                        print(f"[Aviso] Chat '{nome_chat}' fechado para interações de membros. Pulando...")
                        continue
                    
                    # Geração do bloco dinâmico baseado na parametrização do nicho
                    corpo_dinamico = gerar_mensagem_dinamica(nicho_atual)
                    texto_final = f"{corpo_dinamico}\n\n👉 {CONFIG['LINK_RODAPE']}"
                    
                    print("[Mensagem] Injetando conteúdo dinâmico humanizado...")
                    digitar_como_humano(page, seletor_caixa_texto, texto_final)
                        
                    time.sleep(1.5)
                    page.keyboard.press("Enter")
                    print(f"[Sucesso] Conteúdo distribuído em: {nome_chat}")
                    
                    # Janela de descanso dinâmica entre disparos diretos
                    tempo_espera = random.uniform(45.0, 90.0)
                    print(f"Pausa estratégica: aguardando {int(tempo_espera)} segundos...")
                    time.sleep(tempo_espera)
                    
                except Exception as e:
                    print(f"[Aviso] Tratamento de exceção em loop de chat: {e}")
                    try:
                        page.keyboard.press("Escape")
                    except:
                        pass
            
            if not page.is_closed():
                try:
                    page.evaluate('document.querySelector("#pane-side").scrollBy(0, 500)')
                    time.sleep(4)
                except:
                    pass
        
        print(f"\n[Concluído] Ciclo encerrado. Total mapeado nesta rodada: {len(grupos_processados)}")
        try:
            context.close()
        except:
            pass

if __name__ == "__main__":
    print("Módulo de Prospecção Ativa Multicopo Inicializado.")
    while True:
        disparar_rotina_automatica()
        print(f"Descanso global da operação. Próximo ciclo em {CONFIG['INTERVALO_CICLOS']} segundos...")
        time.sleep(CONFIG["INTERVALO_CICLOS"])
