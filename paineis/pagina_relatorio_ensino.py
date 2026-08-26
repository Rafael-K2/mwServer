import threading
import unicodedata
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from paineis.helpers import card_resumo, iniciar_polling, classificar_nota


def _norm(texto):
    return unicodedata.normalize("NFD", str(texto).lower()).encode("ascii", "ignore").decode("ascii")


def _nota_numerica(valor):
    try:
        n = int(float(str(valor).strip().replace(",", ".")))
        if 1 <= n <= 5:
            return n
    except (TypeError, ValueError):
        pass
    return None


def processar_avaliacoes_ensino(registros):
    itens = {}
    boa = media = ruim = 0
    alunos = set()
    anonimas = set()
    registros_ensino = []

    for r in registros:
        try:
            estagio = int(str(r.get("Estagio", "")).strip())
        except (TypeError, ValueError):
            continue
        if estagio != 3:
            continue

        registros_ensino.append(r)
        item = str(r.get("Item", "")).strip() or "Sem item"
        nome_aluno = str(r.get("Aluno", "")).strip()
        if not nome_aluno or _norm(nome_aluno) == "anonimo":
            anonimas.add(str(r.get("Data", "")))
        else:
            alunos.add(nome_aluno.lower())

        nota = _nota_numerica(r.get("Nota"))
        if nota is None:
            continue

        dados = itens.setdefault(item, {"media": 0.0, "quantidade": 0, "soma": 0, "notas": []})
        dados["soma"] += nota
        dados["quantidade"] += 1
        dados["notas"].append(nota)

        classe = classificar_nota(nota)
        if classe == "Bom":
            boa += 1
        elif classe == "Medio":
            media += 1
        else:
            ruim += 1

    for item, dados in itens.items():
        dados["media"] = dados["soma"] / dados["quantidade"]
        dados["maior"] = max(dados["notas"])
        dados["menor"] = min(dados["notas"])

    total_estrelas = boa + media + ruim
    media_geral = 0.0
    if total_estrelas:
        soma_total = sum(d["soma"] for d in itens.values())
        media_geral = soma_total / total_estrelas

    return {
        "total_registros": len(registros_ensino),
        "total_estrelas": total_estrelas,
        "media_geral": media_geral,
        "boa": boa,
        "media": media,
        "ruim": ruim,
        "itens": itens,
        "alunos_identificados": len(alunos),
        "avaliacoes_anonimas": len(anonimas),
        "alunos_avaliaram": len(alunos) + len(anonimas),
    }


def criar_pagina_relatorio_ensino(_scroll_inner, cores, _agora_br, _ler_avaliacoes_semana_db):
    CINZA_BG = cores["CINZA_BG"]
    BRANCO = cores["BRANCO"]
    TEXTO_CINZA = cores["TEXTO_CINZA"]
    TEXTO_ESCURO = cores["TEXTO_ESCURO"]
    VERDE_VIBRANTE = cores["VERDE_VIBRANTE"]
    VERDE_ESCURO = cores["VERDE_ESCURO"]
    AZUL_CLARO = cores["AZUL_CLARO"]
    ROXO_CLARO = cores["ROXO_CLARO"]
    LARANJA = cores.get("LARANJA", "#EF6C00")

    def _card_resumo(parent, row, col, icone, cor_fundo, cor_icone, titulo, valor, subtitulo):
        return card_resumo(parent, row, col, icone, cor_fundo, cor_icone, titulo, valor,
                           subtitulo, {"BRANCO": BRANCO, "TEXTO_CINZA": TEXTO_CINZA, "TEXTO_ESCURO": TEXTO_ESCURO})

    page = ctk.CTkFrame(_scroll_inner, fg_color=CINZA_BG)
    page.grid_columnconfigure(0, weight=1)

    cab = ctk.CTkFrame(page, fg_color="transparent")
    cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
    ctk.CTkLabel(cab, text="📚 Relatório do Ensino", font=("Segoe UI", 20, "bold"), text_color=TEXTO_ESCURO).pack(anchor="w")
    ctk.CTkLabel(cab, text="Resumo das avaliações do setor de ensino.", font=("Segoe UI", 12), text_color=TEXTO_CINZA).pack(anchor="w")

    cards = ctk.CTkFrame(page, fg_color="transparent")
    cards.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
    cards.grid_columnconfigure((0, 1, 2), weight=1)

    lbl_total, _ = _card_resumo(cards, 0, 0, "👥", AZUL_CLARO, VERDE_VIBRANTE, "Alunos que avaliaram", "0", "respostas coletadas")
    lbl_media, _ = _card_resumo(cards, 0, 1, "⭐", ROXO_CLARO, "#6A1B9A", "Média geral", "0.00", "de 5 estrelas")
    lbl_itens, _ = _card_resumo(cards, 0, 2, "📝", "#FFF3E0", LARANJA, "Itens avaliados", "0", "categorias registradas")

    resumo_box = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    resumo_box.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
    resumo_box.grid_columnconfigure((0, 1), weight=1)

    lbl_preferida = ctk.CTkLabel(resumo_box, text="Matéria preferida: —", font=("Segoe UI", 15, "bold"), text_color=TEXTO_ESCURO)
    lbl_preferida.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))
    lbl_resumo_desc = ctk.CTkLabel(resumo_box, text="Acompanhe a percepção dos alunos por disciplina e os principais indicadores do setor de ensino.", font=("Segoe UI", 11), text_color=TEXTO_CINZA, wraplength=700)
    lbl_resumo_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

    graficos_area = ctk.CTkFrame(page, fg_color="transparent")
    graficos_area.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 12))
    graficos_area.grid_columnconfigure((0, 1), weight=1)

    chart_left = ctk.CTkFrame(graficos_area, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    chart_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
    chart_left.grid_columnconfigure(0, weight=1)
    chart_left.grid_rowconfigure(1, weight=1)

    chart_right = ctk.CTkFrame(graficos_area, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    chart_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
    chart_right.grid_columnconfigure(0, weight=1)
    chart_right.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(chart_left, text="📈 Comparação das matérias", font=("Segoe UI", 13, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
    ctk.CTkLabel(chart_right, text="📊 Distribuição das respostas", font=("Segoe UI", 13, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

    chart_left_body = ctk.CTkFrame(chart_left, fg_color="transparent")
    chart_left_body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    chart_left_body.grid_columnconfigure(0, weight=1)
    chart_left_body.grid_rowconfigure(0, weight=1)

    chart_right_body = ctk.CTkFrame(chart_right, fg_color="transparent")
    chart_right_body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    chart_right_body.grid_columnconfigure(0, weight=1)
    chart_right_body.grid_rowconfigure(0, weight=1)

    corpo = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12, border_width=1, border_color="#E5E7EB")
    corpo.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 20))
    corpo.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(corpo, text="Detalhes por matéria", font=("Segoe UI", 14, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))

    lista = ctk.CTkScrollableFrame(corpo, fg_color="transparent")
    lista.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
    lista.grid_columnconfigure(0, weight=1)

    _ativo = {"vivo": True}
    page.bind("<Destroy>", lambda e: _ativo.update({"vivo": False}))

    def _renderizar(stats):
        for w in lista.winfo_children():
            w.destroy()

        for w in chart_left_body.winfo_children():
            w.destroy()
        for w in chart_right_body.winfo_children():
            w.destroy()

        if not stats["itens"]:
            ctk.CTkLabel(lista, text="Ainda não há avaliações de ensino para mostrar.", font=("Segoe UI", 12), text_color=TEXTO_CINZA).pack(anchor="w", pady=8)
            lbl_total.configure(text="0")
            lbl_media.configure(text="0.00")
            lbl_itens.configure(text="0")
            lbl_preferida.configure(text="Matéria preferida: —")
            lbl_resumo_desc.configure(text="Acompanhe a percepção dos alunos por disciplina e os principais indicadores do setor de ensino.")
            return

        itens_ord = sorted(stats["itens"].items(), key=lambda kv: kv[0].lower())
        labels = [item for item, _ in itens_ord]
        medias = [dados["media"] for _, dados in itens_ord]
        quantidades = [dados["quantidade"] for _, dados in itens_ord]

        preferida = max(itens_ord, key=lambda kv: (kv[1]["media"], kv[1]["quantidade"]))
        lbl_preferida.configure(text=f"Matéria preferida: {preferida[0]} ({preferida[1]['media']:.2f} ★)")
        lbl_resumo_desc.configure(text=f"{preferida[0]} foi a disciplina com melhor percepção entre os alunos, com {preferida[1]['quantidade']} avaliação(ões) registrada(s).")

        fig1 = plt.Figure(figsize=(5.2, 3.1), dpi=100)
        ax1 = fig1.add_subplot(111)
        cores_barras = [VERDE_VIBRANTE if v == max(medias) else "#A7F3D0" for v in medias]
        ax1.bar(labels, medias, color=cores_barras, edgecolor="none")
        ax1.set_ylim(0, 5)
        ax1.set_ylabel("Média")
        ax1.set_title("Média por matéria")
        ax1.set_facecolor("white")
        fig1.patch.set_facecolor("white")
        for bar, valor in zip(ax1.patches, medias):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{valor:.1f}", ha="center", va="bottom", fontsize=8)
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=chart_left_body)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        valores_dist = [stats["boa"], stats["media"], stats["ruim"]]
        nomes_dist = ["Positivas", "Neutras", "Negativas"]
        cores_dist = ["#34D399", "#FBBF24", "#F87171"]
        fig2 = plt.Figure(figsize=(5.2, 3.1), dpi=100)
        ax2 = fig2.add_subplot(111)
        wedges, texts, autotexts = ax2.pie(
            valores_dist,
            labels=nomes_dist,
            autopct="%1.1f%%",
            startangle=90,
            colors=cores_dist,
            wedgeprops={"linewidth": 1, "edgecolor": "white"},
        )
        for t in texts + autotexts:
            t.set_fontsize(9)
        ax2.set_title("Distribuição das respostas")
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_right_body)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        for item, dados in sorted(stats["itens"].items()):
            bloco = ctk.CTkFrame(lista, fg_color="#F9FAFB", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            bloco.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(bloco, text=item, font=("Segoe UI", 12, "bold"), text_color=TEXTO_ESCURO).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(bloco, text=f"{dados['media']:.2f} ★ · {dados['quantidade']} avaliação(ões)", font=("Segoe UI", 10), text_color=TEXTO_CINZA).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
            ctk.CTkLabel(bloco, text=f"Maior: {dados['maior']} · Menor: {dados['menor']}", font=("Segoe UI", 10), text_color=TEXTO_CINZA).grid(row=0, column=1, sticky="e", padx=12, pady=(10, 4))

        lbl_total.configure(text=str(stats["alunos_avaliaram"]))
        lbl_media.configure(text=f"{stats['media_geral']:.2f}")
        lbl_itens.configure(text=str(len(stats['itens'])))

    def carregar_dados():
        # A consulta ao banco roda numa thread separada — antes rodava
        # direto aqui (na thread principal do Tkinter), e travava a janela
        # inteira até o Neon responder, toda vez que a aba abria ou o
        # polling detectava uma avaliação nova. Só o resultado já pronto
        # (stats) volta pra thread principal via page.after, porque widgets
        # do Tkinter só podem ser tocados dali.
        def _thread_body():
            try:
                registros = _ler_avaliacoes_semana_db()
            except Exception:
                registros = []
            stats = processar_avaliacoes_ensino(registros)
            if _ativo["vivo"] and page.winfo_exists():
                page.after(0, lambda: _renderizar(stats))

        threading.Thread(target=_thread_body, daemon=True).start()

    carregar_dados()
    iniciar_polling(page, carregar_dados)

    return page
