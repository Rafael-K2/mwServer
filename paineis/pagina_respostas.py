"""
Aba "Respostas da Gestão" do Painel Administrativo.

Antes a comunicação entre gestão e alunos era só de mão única: toda sexta
o aluno avalia (Comida, Limpeza, Ensino, Acolhimento), e ninguém respondia
nada — a informação ficava só nos relatórios que a gestão via. Esta aba
permite escrever um recado sobre um setor (ou geral) que fica visível pra
todos os alunos dentro do app, fechando o ciclo.

Como a maioria das avaliações é anônima ou agregada por setor (não há uma
"conversa" individual rastreável com cada aluno), a resposta também é
agregada: não responde a UMA avaliação específica, e sim ao que a gestão
quer comunicar sobre um setor numa semana.
"""
import customtkinter as ctk
from tkinter import messagebox

from paineis.helpers import card_resumo
from paineis.helpers import confirmar_exclusao


SETORES = ["Geral", "Comida", "Limpeza", "Ensino", "Acolhimento"]
SETOR_ICONE = {"Geral": "📢", "Comida": "🍽️", "Limpeza": "🧹", "Ensino": "📚", "Acolhimento": "✨"}


def criar_pagina_respostas(_scroll_inner, cores, _agora_br, _inserir_resposta_gestao_db,
                            _ler_respostas_gestao_db, _apagar_resposta_gestao_db,
                            autor_padrao=None):
    """Cria e retorna o frame da página "Respostas da Gestão".

    Parâmetros
    ----------
    _scroll_inner : CTkFrame
        Frame pai (área rolável) onde a página é desenhada.
    cores : dict
        Constantes de cor: CINZA_BG, BRANCO, TEXTO_CINZA, TEXTO_ESCURO,
        VERDE_VIBRANTE, VERDE_ESCURO, AZUL_CLARO, ROXO_CLARO.
    _agora_br : callable
        Devolve datetime atual no fuso do Brasil.
    _inserir_resposta_gestao_db, _ler_respostas_gestao_db, _apagar_resposta_gestao_db : callables
        Funções de banco (Neon) para a tabela respostas_gestao.
    autor_padrao : str opcional
        Nome do perfil logado (ex.: "Coordenação"), preenchido automaticamente
        como autor de cada resposta nova.
    """
    CINZA_BG       = cores["CINZA_BG"]
    BRANCO         = cores["BRANCO"]
    TEXTO_CINZA    = cores["TEXTO_CINZA"]
    TEXTO_ESCURO   = cores["TEXTO_ESCURO"]
    VERDE_VIBRANTE = cores["VERDE_VIBRANTE"]
    VERDE_ESCURO   = cores["VERDE_ESCURO"]

    page = ctk.CTkFrame(_scroll_inner, fg_color=CINZA_BG)
    page.grid_columnconfigure(0, weight=0)
    page.grid_columnconfigure(1, weight=1)
    page.grid_rowconfigure(1, weight=1)

    # ── Cabeçalho ─────────────────────────────────────────────────────────
    cab = ctk.CTkFrame(page, fg_color="transparent")
    cab.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 16))
    ctk.CTkLabel(cab, text="Respostas da Gestão 📢",
                 font=("Segoe UI", 22, "bold"), text_color=TEXTO_ESCURO).pack(anchor="w")
    ctk.CTkLabel(cab, text="Escreva um recado visível para todos os alunos no app sobre "
                           "as avaliações da semana — fecha o ciclo do aluno avaliar e "
                           "a gestão responder.",
                 font=("Segoe UI", 12), text_color=TEXTO_CINZA, wraplength=760,
                 justify="left").pack(anchor="w")

    # ── Coluna esquerda: formulário de nova resposta ────────────────────────
    form_card = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12, width=320)
    form_card.grid(row=1, column=0, sticky="ns", padx=(0, 16))
    form_card.grid_propagate(False)

    ctk.CTkLabel(form_card, text="Nova resposta", font=("Segoe UI", 15, "bold"),
                 text_color=TEXTO_ESCURO).pack(anchor="w", padx=20, pady=(20, 12))

    ctk.CTkLabel(form_card, text="Setor", font=("Segoe UI", 11, "bold"),
                 text_color=TEXTO_ESCURO).pack(anchor="w", padx=20)
    cb_setor = ctk.CTkOptionMenu(form_card, values=SETORES, width=280,
                                  fg_color=VERDE_VIBRANTE, button_color=VERDE_ESCURO,
                                  button_hover_color=VERDE_ESCURO)
    cb_setor.set("Geral")
    cb_setor.pack(padx=20, pady=(4, 14))

    ctk.CTkLabel(form_card, text="Título", font=("Segoe UI", 11, "bold"),
                 text_color=TEXTO_ESCURO).pack(anchor="w", padx=20)
    ent_titulo = ctk.CTkEntry(form_card, font=("Segoe UI", 13), height=38,
                               border_color=VERDE_VIBRANTE, border_width=2,
                               placeholder_text="Ex: Cardápio de quinta foi ajustado")
    ent_titulo.pack(fill="x", padx=20, pady=(4, 14))

    ctk.CTkLabel(form_card, text="Mensagem", font=("Segoe UI", 11, "bold"),
                 text_color=TEXTO_ESCURO).pack(anchor="w", padx=20)
    txt_mensagem = ctk.CTkTextbox(form_card, font=("Segoe UI", 12), height=140)
    txt_mensagem.pack(fill="x", padx=20, pady=(4, 8))

    lbl_form_status = ctk.CTkLabel(form_card, text="", font=("Segoe UI", 10),
                                    text_color=VERDE_VIBRANTE, wraplength=280, justify="left")
    lbl_form_status.pack(padx=20, pady=(0, 4))

    # ── Coluna direita: histórico de respostas já publicadas ────────────────
    lista_card = ctk.CTkFrame(page, fg_color=BRANCO, corner_radius=12)
    lista_card.grid(row=1, column=1, sticky="nsew")
    lista_card.grid_rowconfigure(1, weight=1)
    lista_card.grid_columnconfigure(0, weight=1)

    topo_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
    topo_lista.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 4))
    ctk.CTkLabel(topo_lista, text="Já publicadas", font=("Segoe UI", 14, "bold"),
                 text_color=TEXTO_ESCURO).pack(side="left")
    lbl_total = ctk.CTkLabel(topo_lista, text="", font=("Segoe UI", 10), text_color=TEXTO_CINZA)
    lbl_total.pack(side="right")

    lista = ctk.CTkScrollableFrame(lista_card, fg_color="transparent")
    lista.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
    lista.grid_columnconfigure(0, weight=1)

    def carregar_respostas():
        for w in lista.winfo_children():
            w.destroy()
        try:
            respostas = _ler_respostas_gestao_db(50)
        except Exception as e:
            ctk.CTkLabel(lista, text=f"⚠ Falha ao carregar: {e}", font=("Segoe UI", 11),
                         text_color="#C62828").pack(anchor="w", pady=8)
            return

        lbl_total.configure(text=f"{len(respostas)} publicada(s)")

        if not respostas:
            ctk.CTkLabel(lista, text="Nenhuma resposta publicada ainda.",
                         font=("Segoe UI", 12), text_color=TEXTO_CINZA).pack(anchor="w", pady=24)
            return

        for r in respostas:
            bloco = ctk.CTkFrame(lista, fg_color="#F9FAFB", corner_radius=10)
            bloco.pack(fill="x", pady=6)
            bloco.grid_columnconfigure(0, weight=1)

            cab_bloco = ctk.CTkFrame(bloco, fg_color="transparent")
            cab_bloco.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 2))
            icone = SETOR_ICONE.get(r.get("setor"), "📢")
            ctk.CTkLabel(cab_bloco, text=f"{icone} {r.get('titulo', '')}",
                         font=("Segoe UI", 12, "bold"), text_color=TEXTO_ESCURO,
                         anchor="w").pack(side="left")

            def _remover(resposta_id=r.get("id"), titulo=r.get("titulo", "")):
                if confirmar_exclusao(
                    page.winfo_toplevel(),
                    "Apagar resposta",
                    f'Isso remove permanentemente a resposta "{titulo}" — ela some do '
                    "app de todos os alunos.",
                    cores, palavra="APAGAR",
                ):
                    try:
                        _apagar_resposta_gestao_db(resposta_id)
                        carregar_respostas()
                    except Exception as e:
                        messagebox.showerror("Erro", f"Falha ao apagar:\n{e}")

            ctk.CTkButton(cab_bloco, text="🗑", width=32, height=26,
                          fg_color="#FEE2E2", hover_color="#FCA5A5",
                          text_color="#C62828", font=("Segoe UI", 11),
                          command=_remover).pack(side="right")

            meta = f"{r.get('setor', 'Geral')} · {r.get('criado_em', '')}"
            if r.get("autor"):
                meta += f" · {r['autor']}"
            ctk.CTkLabel(bloco, text=meta, font=("Segoe UI", 9), text_color=TEXTO_CINZA,
                         anchor="w").grid(row=1, column=0, sticky="w", padx=14)
            ctk.CTkLabel(bloco, text=r.get("mensagem", ""), font=("Segoe UI", 11),
                         text_color="#374151", anchor="w", justify="left",
                         wraplength=560).grid(row=2, column=0, sticky="w", padx=14, pady=(4, 12))

    def publicar():
        titulo = ent_titulo.get().strip()
        mensagem = txt_mensagem.get("0.0", "end").strip()
        setor = cb_setor.get()

        if not titulo or not mensagem:
            lbl_form_status.configure(text="⚠ Preencha título e mensagem.", text_color="#C62828")
            return

        try:
            _inserir_resposta_gestao_db(setor, titulo, mensagem, autor_padrao)
        except Exception as e:
            lbl_form_status.configure(text=f"⚠ Falha ao publicar: {e}", text_color="#C62828")
            return

        lbl_form_status.configure(text="✔ Resposta publicada! Já está visível no app.",
                                   text_color=VERDE_VIBRANTE)
        ent_titulo.delete(0, "end")
        txt_mensagem.delete("0.0", "end")
        cb_setor.set("Geral")
        carregar_respostas()
        page.after(3500, lambda: lbl_form_status.configure(text=""))

    ctk.CTkButton(form_card, text="📢  Publicar para os alunos",
                  fg_color=VERDE_VIBRANTE, hover_color=VERDE_ESCURO,
                  font=("Segoe UI", 12, "bold"), height=40,
                  command=publicar).pack(fill="x", padx=20, pady=(4, 20))

    carregar_respostas()
    return page
