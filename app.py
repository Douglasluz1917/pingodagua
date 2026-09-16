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

# -------------------------------------------------------------------
# ESTRUTURA DE ABAS
# -------------------------------------------------------------------
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
                st.link_button(f"🎁 Mandar Parabéns para {aluno['Nome do Aluno']}", f"https://wa.me/55{tel}?text={msg}")
            with col_btn2:
                if st.button(f"✅ Ocultar aviso ({aluno['Nome do Aluno']})", key=f"niver_{index}"):
                    df_atualiza = pd.read_csv(arquivo_dados)
                    df_atualiza.at[index, "Ano_Ultimo_Parabens"] = hoje.year
                    df_atualiza.to_csv(arquivo_dados, index=False)
                    st.rerun()

    st.write("---")
    st.header("📈 Visão Geral do Espaço")
    col1, col2, col3 = st.columns(3)
    
    total_ativos = len(df_ativos)
    receita_esperada = df_ativos['Mensalidade (R$)'].sum()
    valor_atrasado = df_ativos[df_ativos['Status'] == 'Atrasado']['Mensalidade (R$)'].sum()
    
    col1.metric("Total de Alunos Ativos", f"{total_ativos} alunos")
    col2.metric("Receita Mensal Esperada", f"R$ {receita_esperada:.2f}".replace(".", ","))
    col3.metric("🔴 Valor em Atraso Base", f"R$ {valor_atrasado:.2f}".replace(".", ","))
    
    st.write("---")
    
    st.subheader("📝 Painel de Cadastro e Edição (Todos os Alunos)")
    st.warning("⚠️ **IMPORTANTE:** Ao editar uma data, aperte **ENTER** ou clique fora da tabela para confirmar a data ANTES de clicar no botão de Salvar.")
    
    colunas_config = {
        "Status": st.column_config.TextColumn("Status", disabled=True),
        "Mensalidade (R$)": st.column_config.NumberColumn("Mensalidade (R$)", format="R$ %.2f", disabled=True),
        "Matrícula": st.column_config.SelectboxColumn("Matrícula", options=["Ativo", "Inativo"]),
        "Modalidade": st.column_config.SelectboxColumn("Modalidade", options=list(TABELA_PRECOS.keys())),
        "Data de Nascimento": st.column_config.DateColumn("Data de Nascimento", format="DD/MM/YYYY"),
        "Data de Vencimento": st.column_config.DateColumn("Data de Vencimento", format="DD/MM/YYYY"),
        "Telefone": st.column_config.TextColumn("Telefone (DDD + número)"),
        "Ano_Ultimo_Parabens": None
    }

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        column_config=colunas_config, 
        use_container_width=True, 
        hide_index=True,
        key="tabela_alunos"
    )

    if st.button("💾 Salvar Modificações na Tabela", use_container_width=True):
        df_salvar = df_editado.copy()
        
        def formatar_data_segura(val):
            if pd.isna(val) or val == "" or str(val) == "None" or str(val) == "NaT" or str(val) == "nan":
                return ""
            try:
                return pd.to_datetime(val).strftime("%Y-%m-%d")
            except:
                return ""

        df_salvar["Data de Nascimento"] = df_salvar["Data de Nascimento"].apply(formatar_data_segura)
        df_salvar["Data de Vencimento"] = df_salvar["Data de Vencimento"].apply(formatar_data_segura)
        df_salvar["Matrícula"] = df_salvar["Matrícula"].fillna("Ativo")
        
        df_salvar.to_csv(arquivo_dados, index=False)
        
        if "tabela_alunos" in st.session_state:
            del st.session_state["tabela_alunos"]
            
        st.success("Tabela de alunos atualizada com sucesso!")
        st.rerun()

    st.write("---")
    st.subheader("📋 Painel de Cobrança Automática")
    
    df_visualizacao = df_editado[df_editado["Matrícula"] == "Ativo"].copy()
    
    if busca_nome: 
        df_visualizacao = df_visualizacao[df_visualizacao["Nome do Aluno"].str.contains(busca_nome, case=False, na=False)]
    if filtro_status != "Todos": 
        df_visualizacao = df_visualizacao[df_visualizacao["Status"] == filtro_status]
        
    df_visualizacao["Prioridade"] = df_visualizacao["Status"].map({"Atrasado": 1, "Perto de vencer": 2, "Em dia": 3})
    df_visualizacao = df_visualizacao.sort_values(by="Prioridade").drop(columns=["Prioridade", "Ano_Ultimo_Parabens"])

    def colorir_linhas(row):
        cores = {'Em dia': '#c3e6cb', 'Atrasado': '#f5c6cb', 'Perto de vencer': '#ffeeba'}
        return [f"background-color: {cores.get(row['Status'], 'white')}; color: black"] * len(row)

    st.dataframe(
        df_visualizacao.style
        .apply(colorir_linhas, axis=1)
        .format({
            "Mensalidade (R$)": lambda x: f"R$ {x:.2f}".replace(".", ",") if pd.notnull(x) else "R$ 0,00",
            "Data de Nascimento": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else "",
            "Data de Vencimento": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
        }), 
        use_container_width=True, 
        hide_index=True
    )

    def calcular_idade(nascimento):
        if pd.isna(nascimento): return 18
        return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

    for index, row in df_visualizacao.iterrows():
        if row["Status"] in ["Atrasado", "Perto de vencer"]:
            col_wpp, col_pago = st.columns([3, 1])
            
            with col_wpp:
                idade = calcular_idade(row['Data de Nascimento'])
                saudacao = f"Olá, responsável por {row['Nome do Aluno']}" if idade < 18 else f"Olá, {row['Nome do Aluno']}"
                
                valor_base = row['Mensalidade (R$)']
                dias_atraso = (hoje - row['Data de Vencimento']).days if row['Status'] == 'Atrasado' else 0
                
                valor_final = valor_base + 10.00 if dias_atraso > 0 else valor_base
                txt_valor = f"O valor atualizado (com taxa)" if dias_atraso > 0 else "O valor da sua mensalidade"
                valor_formatado_br = f"{valor_final:.2f}".replace(".", ",")
                
                icone = "🔴" if row["Status"] == "Atrasado" else "🟡"
                texto_base = txt_atrasado if row["Status"] == "Atrasado" else txt_vencendo
                
                texto_cobranca = f"{saudacao}! 🏊‍♂️\n\nAqui é do Pingo D'água. {texto_base}\n\n{txt_valor} é de *R$ {valor_formatado_br}*.\n\nPara facilitar, segue nossa chave PIX:\n🔑 {txt_pix}\n👤 {txt_recebedor}\n\nQualquer dúvida, estamos à disposição!"
                
                link_wpp = f"https://wa.me/55{str(row['Telefone']).replace(' ', '')}?text={urllib.parse.quote(texto_cobranca)}"
                st.link_button(f"{icone} Cobrar {row['Nome do Aluno']} (R$ {valor_formatado_br})", link_wpp, use_container_width=True)
                
            with col_pago:
                id_cobranca = f"{row['Nome do Aluno']}_{row['Data de Vencimento']}"
                
                if id_cobranca in st.session_state["transacoes_feitas"]:
                    st.success("✅ Pago!")
                else:
                    st.button(
                        "✅ Confirmar", 
                        key=f"btn_pago_{index}_{row['Data de Vencimento']}", 
                        on_click=processar_pagamento, 
                        args=(index, row['Nome do Aluno'], row['Modalidade'], row['Data de Vencimento'], valor_final),
                        use_container_width=True
                    )
                    
    st.write("---")
    st.subheader("📊 Gráfico: Aulas Mais Procuradas")
    if total_ativos > 0:
        df_grafico_turmas = df_ativos["Modalidade"].value_counts().reset_index()
        df_grafico_turmas.columns = ["Turma", "Quantidade de Alunos"]
        
        # O comando axis=alt.Axis(tickMinStep=1, format="d") trava o gráfico apenas em números inteiros (1, 2, 3)
        grafico_turmas = alt.Chart(df_grafico_turmas).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X("Turma:N", sort="-y", title="Modalidade", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Quantidade de Alunos:Q", title="Alunos Matriculados", axis=alt.Axis(tickMinStep=1, format="d")),
            color=alt.Color("Turma:N", scale=alt.Scale(scheme='category10'), legend=None),
            tooltip=["Turma", "Quantidade de Alunos"]
        ).properties(height=400)
        
        st.altair_chart(grafico_turmas, use_container_width=True)
    else:
        st.info("Cadastre alunos para visualizar o gráfico de turmas.")

with aba2:
    st.header("💰 Histórico de Entradas")
    df_historico = pd.read_csv(arquivo_historico)
    
    if df_historico.empty:
        st.info("Nenhum pagamento registrado ainda. Confirme um pagamento na aba de Gestão para ver o histórico.")
    else:
        df_historico["Data Real"] = pd.to_datetime(df_historico["Data do Pagamento"], format="%d/%m/%Y", errors="coerce")
        df_historico["Mês/Ano"] = df_historico["Data Real"].dt.strftime("%m/%Y")
        
        lista_meses = df_historico["Mês/Ano"].dropna().unique().tolist()
        lista_meses.sort(reverse=True)
        
        col_filtro, _ = st.columns([1, 3])
        with col_filtro:
            mes_selecionado = st.selectbox("📅 Filtrar Tabela por Mês:", ["Todos os Meses"] + lista_meses)
        
        if mes_selecionado != "Todos os Meses":
            df_mostrar = df_historico[df_historico["Mês/Ano"] == mes_selecionado]
        else:
            df_mostrar = df_historico
            
        df_mostrar = df_mostrar.drop(columns=["Data Real", "Mês/Ano"])
        
        st.dataframe(
            df_mostrar.style.format({"Valor Recebido (R$)": lambda x: f"R$ {x:.2f}".replace(".", ",")}), 
            use_container_width=True, 
            hide_index=True
        )
        
        total_caixa = df_mostrar["Valor Recebido (R$)"].sum()
        total_caixa_br = f"{total_caixa:.2f}".replace(".", ",")
        
        if mes_selecionado == "Todos os Meses":
            st.success(f"**Total Histórico Geral:** R$ {total_caixa_br}")
        else:
            st.success(f"**Total arrecadado em {mes_selecionado}:** R$ {total_caixa_br}")
            
        st.write("---")
        st.subheader("📈 Gráfico: Evolução Financeira")
        
        df_grafico_caixa = df_historico.groupby("Mês/Ano")["Valor Recebido (R$)"].sum().reset_index()
        df_grafico_caixa["Ordenacao"] = pd.to_datetime(df_grafico_caixa["Mês/Ano"], format="%m/%Y")
        df_grafico_caixa = df_grafico_caixa.sort_values("Ordenacao")
        
        grafico_financeiro = alt.Chart(df_grafico_caixa).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X("Mês/Ano:O", sort=None, title="Mês e Ano", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Valor Recebido (R$):Q", title="Total Arrecadado (R$)"),
            color=alt.Color("Mês/Ano:O", scale=alt.Scale(scheme='tableau10'), legend=None),
            tooltip=["Mês/Ano", "Valor Recebido (R$)"]
        ).properties(height=350)
        
        st.altair_chart(grafico_financeiro, use_container_width=True)

with aba3:
    st.header("⚙️ Configurações do Sistema")
    
    st.subheader("🔒 Alterar Senha de Acesso")
    st.write("Altere a senha principal do sistema. Por segurança, você será deslogado após salvar.")
    with st.form("form_senha"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            nova_senha = st.text_input("Nova Senha:", type="password")
        with col_s2:
            confirma_senha = st.text_input("Confirme a Nova Senha:", type="password")
            
        if st.form_submit_button("💾 Salvar Nova Senha", use_container_width=True):
            if nova_senha and nova_senha == confirma_senha:
                config_textos["senha_acesso"] = nova_senha
                with open(arquivo_textos, "w", encoding="utf-8") as f:
                    json.dump(config_textos, f, ensure_ascii=False, indent=4)
                st.success("Senha alterada! Deslogando por segurança...")
                st.session_state["logado"] = False
                st.rerun()
            elif nova_senha != confirma_senha:
                st.error("As senhas não coincidem. Tente novamente.")
            else:
                st.warning("A senha não pode estar vazia.")
    st.write("---")

    st.subheader("🏊‍♂️ Tabela de Preços")
    st.write("Gerencie aqui as opções de aulas e os preços.")
    colunas_precos = {
        "Valor (R$)": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
    }
    df_precos_editado = st.data_editor(
        df_precos, 
        num_rows="dynamic", 
        column_config=colunas_precos, 
        use_container_width=True, 
        hide_index=True,
        key="tabela_precos"
    )
    if st.button("💾 Salvar Tabela de Preços", use_container_width=True):
        df_precos_editado.to_csv(arquivo_precos, index=False)
        st.success("Tabela de preços atualizada com sucesso!")
        st.rerun()

    st.write("---")
    
    st.subheader("📱 Personalização de Mensagens e PIX")
    st.write("Altere os textos que serão enviados automaticamente pelo WhatsApp.")
    with st.form("form_textos"):
        novo_pix = st.text_input("🔑 Chave PIX", value=txt_pix)
        novo_recebedor = st.text_input("👤 Nome do Recebedor (PIX)", value=txt_recebedor)
        nova_msg_vencendo = st.text_area("🟡 Mensagem de Vencimento (Perto de vencer)", value=txt_vencendo, height=80)
        nova_msg_atrasado = st.text_area("🔴 Mensagem de Atraso (Já venceu)", value=txt_atrasado, height=80)
        nova_msg_niver = st.text_area("🎁 Mensagem de Aniversário", value=txt_niver, height=80)
        
        if st.form_submit_button("💾 Salvar Textos e PIX", use_container_width=True):
            config_textos["chave_pix"] = novo_pix
            config_textos["nome_recebedor"] = novo_recebedor
            config_textos["msg_vencendo"] = nova_msg_vencendo
            config_textos["msg_atrasado"] = nova_msg_atrasado
            config_textos["msg_aniversario"] = nova_msg_niver
            
            with open(arquivo_textos, "w", encoding="utf-8") as f:
                json.dump(config_textos, f, ensure_ascii=False, indent=4)
            st.success("Mensagens e PIX atualizados com sucesso!")
            st.rerun()