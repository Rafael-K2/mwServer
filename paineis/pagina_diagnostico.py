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

    lbl_db, _ = _card_resumo(cards, 0, 0, "🗄️", AZUL_CLARO, VERDE_VIBRANTE, "Banco", "Verificando", "status do PostgreSQL")
    lbl_api, _ = _card_resumo(cards, 0, 1, "🌐", ROXO_CLARO, "#6A1B9A", "API", "Online", "servidor Flask")
    lbl_backups, _ = _card_resumo(cards, 0, 2, "💾", "#FFF3E0", "#EF6C00", "Backups", "0", "registros salvos")

    corpo = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    corpo.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
    corpo.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(corpo, text="Resumo operacional", font=("Segoe UI", 14, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))

    lista = ctk.CTkScrollableFrame(corpo, fg_color="transparent")
    lista.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
    lista.grid_columnconfigure(0, weight=1)

    def _renderizar():
        status = _status_sistema()
        lbl_db.configure(text=status.get("db_status", "Indefinido"))
        lbl_api.configure(text=status.get("api_status", "Online"))
        lbl_backups.configure(text=str(len(_ler_backups_db(10))))

        for w in lista.winfo_children():
            w.destroy()

        infos = [
            ("Servidor", status.get("api_status", "Online")),
            ("Banco", status.get("db_status", "Indefinido")),
            ("Última checagem", _agora_br().strftime("%d/%m/%Y %H:%M:%S")),
        ]
        for titulo, valor in infos:
            bloco = ctk.CTkFrame(lista, fg_color="#F9FAFB", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            ctk.CTkLabel(bloco, text=titulo, font=("Segoe UI", 12, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(bloco, text=valor, font=("Segoe UI", 10), text_color=TEXTO_CINZA).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        for backup in _ler_backups_db(6):
            bloco = ctk.CTkFrame(lista, fg_color="#F4F9F4", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            ctk.CTkLabel(bloco, text=f"{backup.get('tipo', 'backup')} · {backup.get('origem', '-')}", font=("Segoe UI", 11, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(bloco, text=f"{backup.get('criado_em', '-')} · {backup.get('resumo', {})}", font=("Segoe UI", 10), text_color=TEXTO_CINZA, wraplength=650).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    _renderizar()
    return page
