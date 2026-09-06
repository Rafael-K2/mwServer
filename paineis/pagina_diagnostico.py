import threading
import customtkinter as ctk

from paineis.helpers import card_resumo


def criar_pagina_diagnostico(_scroll_inner, cores, _agora_br, _status_sistema, _ler_backups_db):
    CINZA_BG = cores["CINZA_BG"]
    BRANCO = cores["BRANCO"]
    TEXTO_CINZA = cores["TEXTO_CINZA"]
    TEXTO_ESCURO = cores["TEXTO_ESCURO"]
    VERDE_VIBRANTE = cores["VERDE_VIBRANTE"]
    VERDE_ESCURO = cores["VERDE_ESCURO"]
    AZUL_CLARO = cores["AZUL_CLARO"]
    ROXO_CLARO = cores["ROXO_CLARO"]

    def _card_resumo(parent, row, col, icone, cor_fundo, cor_icone, titulo, valor, subtitulo):
        return card_resumo(parent, row, col, icone, cor_fundo, cor_icone, titulo, valor,
                           subtitulo, {"BRANCO": BRANCO, "TEXTO_CINZA": TEXTO_CINZA, "TEXTO_ESCURO": TEXTO_ESCURO})

    page = ctk.CTkFrame(_scroll_inner, fg_color=CINZA_BG)
    page.grid_columnconfigure(0, weight=1)

    cab = ctk.CTkFrame(page, fg_color="transparent")
    cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
    ctk.CTkLabel(cab, text="🛠️ Diagnóstico do Sistema", font=("Segoe UI", 20, "bold"), text_color=TEXTO_ESCURO).pack(anchor="w")
    ctk.CTkLabel(cab, text="Status do banco, da API e dos backups salvos no banco.", font=("Segoe UI", 12), text_color=TEXTO_CINZA).pack(anchor="w")

    cards = ctk.CTkFrame(page, fg_color="transparent")
    cards.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
    cards.grid_columnconfigure((0, 1, 2), weight=1)

    lbl_db, _ = _card_resumo(cards, 0, 0, "🗄️", AZUL_CLARO, VERDE_VIBRANTE, "Banco", "Verificando...", "status do PostgreSQL")
    lbl_api, _ = _card_resumo(cards, 0, 1, "🌐", ROXO_CLARO, "#6A1B9A", "API", "Verificando...", "servidor Flask")
    lbl_backups, _ = _card_resumo(cards, 0, 2, "💾", "#FFF3E0", "#EF6C00", "Backups", "…", "registros salvos")

    corpo = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    corpo.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
    corpo.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(corpo, text="Resumo operacional", font=("Segoe UI", 14, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))

    lista = ctk.CTkScrollableFrame(corpo, fg_color="transparent")
    lista.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
    lista.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(lista, text="Carregando...", font=("Segoe UI", 12), text_color=TEXTO_CINZA).pack(anchor="w", pady=8)

    _ativo = {"vivo": True}
    page.bind("<Destroy>", lambda e: _ativo.update({"vivo": False}))

    def _renderizar(status, total_backups, backups_recentes, erro=None):
        lbl_db.configure(text=status.get("db_status", "Indefinido"))
        lbl_api.configure(text=status.get("api_status", "Indefinido"))
        lbl_backups.configure(text=str(total_backups))

        for w in lista.winfo_children():
            w.destroy()

        if erro:
            ctk.CTkLabel(lista, text=f"⚠ Falha ao consultar o banco: {erro}",
                         font=("Segoe UI", 11), text_color="#C62828",
                         wraplength=650, justify="left").pack(anchor="w", pady=8)

        # Explicação detalhada e em português simples de por que o banco não
        # está OK — pensada pra quem estiver na frente da tela conseguir
        # entender e mandar print, mesmo sem saber nada técnico.
        db_status = status.get("db_status", "Indefinido")
        db_detalhe = status.get("db_detalhe", "")
        if db_status != "Online" and db_detalhe:
            aviso = ctk.CTkFrame(lista, fg_color="#FEF3F2", corner_radius=10,
                                  border_width=1, border_color="#FCA5A5")
            aviso.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(aviso, text=f"🔴 Banco: {db_status}", font=("Segoe UI", 12, "bold"),
                         text_color="#C62828").pack(anchor="w", padx=14, pady=(12, 4))
            ctk.CTkLabel(aviso, text=db_detalhe, font=("Segoe UI", 11), text_color="#7F1D1D",
                         wraplength=650, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

        infos = [
            ("Servidor", status.get("api_status", "Indefinido")),
            ("Banco", db_status),
            ("Última checagem", _agora_br().strftime("%d/%m/%Y %H:%M:%S")),
        ]
        for titulo, valor in infos:
            bloco = ctk.CTkFrame(lista, fg_color="#F9FAFB", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            ctk.CTkLabel(bloco, text=titulo, font=("Segoe UI", 12, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(bloco, text=valor, font=("Segoe UI", 10), text_color=TEXTO_CINZA).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        for backup in backups_recentes:
            bloco = ctk.CTkFrame(lista, fg_color="#F4F9F4", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            ctk.CTkLabel(bloco, text=f"{backup.get('tipo', 'backup')} · {backup.get('origem', '-')}", font=("Segoe UI", 11, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(bloco, text=f"{backup.get('criado_em', '-')} · {backup.get('resumo', {})}", font=("Segoe UI", 10), text_color=TEXTO_CINZA, wraplength=650).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    def carregar_dados():
        # As duas chamadas abaixo (_status_sistema, _ler_backups_db) batem
        # no banco. Antes rodavam direto aqui, na thread principal do
        # Tkinter — travava a janela inteira até o Neon responder, toda
        # vez que essa aba era aberta. Agora rodam numa thread separada; só
        # o resultado pronto volta pra thread principal via page.after,
        # porque widgets do Tkinter só podem ser tocados dali.
        def _thread_body():
            erro = None
            try:
                status = _status_sistema()
            except Exception as e:
                status = {}
                erro = str(e)
            try:
                backups_recentes = _ler_backups_db(6)
                total_backups = len(_ler_backups_db(10))
            except Exception as e:
                backups_recentes = []
                total_backups = 0
                erro = erro or str(e)

            if _ativo["vivo"] and page.winfo_exists():
                page.after(0, lambda: _renderizar(status, total_backups, backups_recentes, erro))

        threading.Thread(target=_thread_body, daemon=True).start()

    carregar_dados()
    return page
