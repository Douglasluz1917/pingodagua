import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import urllib.parse
import altair as alt

st.set_page_config(page_title="Gestão Pingo D'água", layout="wide", page_icon="🏊‍♂️")

# -------------------------------------------------------------------
# 1. CARREGAMENTO DO COFRE (SENHAS E TEXTOS)
# -------------------------------------------------------------------
arquivo_textos = "config_textos.json"

if not os.path.exists(arquivo_textos):
    config_padrao = {
        "senha_acesso": "pingo123",
        "chave_pix": "81999999999",
        "nome_recebedor": "Pingo D'água Natação",
        "msg_vencendo": "Passando para lembrar que o vencimento da sua mensalidade está próximo.",
        "msg_atrasado": "Notamos que sua mensalidade consta como pendente em nosso sistema.",
        "msg_aniversario": "Toda a equipe do Pingo D'água deseja um Feliz Aniversário! 🎂🏊‍♂️"
    }
    with open(arquivo_textos, "w", encoding="utf-8") as f:
        json.dump(config_padrao, f, ensure_ascii=False, indent=4)

with open(arquivo_textos, "r", encoding="utf-8") as f:
    config_textos = json.load(f)

# Variáveis carregadas do cofre
SENHA_ACESSO = config_textos.get("senha_acesso", "pingo123")
txt_pix = config_textos.get("chave_pix", "81999999999")
txt_recebedor = config_textos.get("nome_recebedor", "Pingo D'água Natação")
txt_vencendo = config_textos.get("msg_vencendo", "Passando para lembrar que o vencimento da sua mensalidade está próximo.")
txt_atrasado = config_textos.get("msg_atrasado", "Notamos que sua mensalidade consta como pendente em nosso sistema.")
txt_niver = config_textos.get("msg_aniversario", "Toda a equipe do Pingo D'água deseja um Feliz Aniversário! 🎂🏊‍♂️")

# -------------------------------------------------------------------
# 2. TELA DE LOGIN E SEGURANÇA
# -------------------------------------------------------------------
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔒 Acesso Restrito - Pingo D'água")
    st.write("Por favor, insira a senha do administrador para acessar o sistema.")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        senha_digitada = st.text_input("Senha:", type="password")
        if st.button("Entrar", use_container_width=True):
            if senha_digitada == SENHA_ACESSO:
                st.session_state["logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    st.stop() 

# -------------------------------------------------------------------
# MEMÓRIA ANTI-CLIQUE DUPLO E DATAS
# -------------------------------------------------------------------
if "transacoes_feitas" not in st.session_state:
    st.session_state["transacoes_feitas"] = set()

hoje = datetime.now().date()

# -------------------------------------------------------------------
# 3. BANCO DE PREÇOS DINÂMICO
# -------------------------------------------------------------------
arquivo_precos = "banco_precos.csv"

if not os.path.exists(arquivo_precos):
    pd.DataFrame({
        "Modalidade": ["Natação Infantil", "Natação Adulto", "Natação Baby", "Hidroginástica (2 dias)", "Hidroginástica (3 dias)", "Hidroterapia"],
        "Valor (R$)": [79.99, 79.99, 79.99, 70.99, 99.99, 120.0]
    }).to_csv(arquivo_precos, index=False)

df_precos = pd.read_csv(arquivo_precos)
TABELA_PRECOS = dict(zip(df_precos["Modalidade"], df_precos["Valor (R$)"]))

with st.sidebar:
    st.title("🏊‍♂️ Pingo D'água")
    st.write("---")
    st.info("Filtros para o Painel de Cobrança:")
    busca_nome = st.text_input("🔍 Buscar Aluno (Cobrança):")
    filtro_status = st.selectbox("📌 Filtrar Status:", ["Todos", "Atrasado", "Perto de vencer", "Em dia"])
    st.write("---")
    if st.button("🚪 Sair do Sistema"):
        st.session_state["logado"] = False
        st.rerun()

arquivo_dados = "banco_alunos.csv"
arquivo_historico = "historico_caixa.csv"

if not os.path.exists(arquivo_dados):
    pd.DataFrame({
        "Nome do Aluno": ["Miguel Santos"],
        "Matrícula": ["Ativo"],
        "Data de Nascimento": ["2015-05-10"],
        "Modalidade": ["Natação Infantil"],
        "Telefone": ["81988882222"],
        "Data de Vencimento": ["2026-09-10"],
        "Status": ["Atrasado"],
        "Ano_Ultimo_Parabens": [0]
    }).to_csv(arquivo_dados, index=False)

if not os.path.exists(arquivo_historico):
    pd.DataFrame(columns=["Data do Pagamento", "Aluno", "Modalidade", "Valor Recebido (R$)"]).to_csv(arquivo_historico, index=False)

def processar_pagamento(index_aluno, nome_aluno, modalidade_aluno, data_venc_atual, valor_pago):
    id_cobranca = f"{nome_aluno}_{data_venc_atual}"
    if id_cobranca in st.session_state["transacoes_feitas"]:
        return
        
    st.session_state["transacoes_feitas"].add(id_cobranca)
    
    df_hist = pd.read_csv(arquivo_historico)
    novo_pagamento = pd.DataFrame([{
        "Data do Pagamento": hoje.strftime("%d/%m/%Y"),
        "Aluno": nome_aluno,
        "Modalidade": modalidade_aluno,
        "Valor Recebido (R$)": valor_pago
    }])
    df_hist = pd.concat([df_hist, novo_pagamento], ignore_index=True)
    df_hist.to_csv(arquivo_historico, index=False)

    df_atualiza = pd.read_csv(arquivo_dados)
    data_formatada = pd.to_datetime(df_atualiza.at[index_aluno, "Data de Vencimento"], errors='coerce')
    nova_data = data_formatada + pd.DateOffset(months=1)
    df_atualiza.at[index_aluno, "Data de Vencimento"] = nova_data.strftime("%Y-%m-%d")
    df_atualiza.to_csv(arquivo_dados, index=False)
    
    if "tabela_alunos" in st.session_state:
        del st.session_state["tabela_alunos"]

df = pd.read_csv(arquivo_dados, dtype={"Telefone": str})

if "Matrícula" not in df.columns:
    df["Matrícula"] = "Ativo"

df["Data de Nascimento"] = pd.to_datetime(df["Data de Nascimento"], errors='coerce').dt.date
df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], errors='coerce').dt.date

if "Ano_Ultimo_Parabens" not in df.columns:
    df["Ano_Ultimo_Parabens"] = 0

df["Mensalidade (R$)"] = df["Modalidade"].map(TABELA_PRECOS).fillna(0.0)

def calcular_status(data_vencimento):
    if pd.isna(data_vencimento): return "Em dia" 
    dias = (data_vencimento - hoje).days
    if dias < 0: return "Atrasado"
    elif 0 <= dias <= 5: return "Perto de vencer"
    else: return "Em dia"

df["Status"] = df["Data de Vencimento"].apply(calcular_status)

aba1, aba2, aba3 = st.tabs(["🏊‍♂️ Gestão de Alunos", "💰 Histórico de Caixa", "⚙️ Configurações"])

with aba1:
    df_ativos = df[df["Matrícula"] == "Ativo"]
    aniversariantes = df_ativos[
        (pd.to_datetime(df_ativos['Data de Nascimento'], errors='coerce').dt.month == hoje.month) &
        (pd.to_datetime(df_ativos['Data de Nascimento'], errors='coerce').dt.day == hoje.day) &
        (df_ativos['Ano_Ultimo_Parabens'] != hoje.year)
    ]

    if not aniversariantes.empty:
        st.balloons()
        st.success("🎉 **TEMOS ANIVERSARIANTES HOJE!**")
        for index, aluno in aniversariantes.iterrows():
            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                tel = str(aluno['Telefone']).replace(" ", "").replace("-", "")
                msg = urllib.parse.quote(f"Olá {aluno['Nome do Aluno']}! {txt_niver}")
                st.link_button(f"🎁 Mandar Parabéns para {aluno['Nome do Aluno']}", f"