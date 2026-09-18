import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import urllib.parse
import altair as alt
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Gestão Pingo D'água", layout="wide", page_icon="🏊‍♂️")

# -------------------------------------------------------------------
# 1. FUNÇÃO DA JANELA POP-UP DO RECIBO
# -------------------------------------------------------------------
@st.dialog("🧾 Comprovante de Pagamento")
def abrir_janela_recibo(nome_aluno, modalidade, valor_pago, telefone):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    nome_seguro = str(nome_aluno) if pd.notna(nome_aluno) else "Aluno_Desconhecido"
    
    img_base64 = ""
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
            
    numero_zap = str(telefone).replace(' ', '').replace('-', '')
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; align-items: center; background: white; margin: 0; padding: 15px; }}
            
            #recibo-digital {{ border: 2px dashed #aaa; padding: 25px; width: 320px; background: #fff; color: #222; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }}
            .cabecalho {{ text-align: center; }}
            .cabecalho img {{ max-height: 80px; margin-bottom: 10px; }}
            .cabecalho h3 {{ margin: 0; color: #005A9C; font-size: 19px; }}
            .cabecalho p {{ margin: 2px 0 10px 0; font-size: 12px; color: #777; }}
            .divisor {{ border-top: 1px dashed #ccc; margin: 15px 0; }}
            .linha {{ margin: 8px 0; font-size: 14px; text-align: left; }}
            .linha strong {{ color: #666; display: block; font-size: 12px; text-transform: uppercase; }}
            .linha span {{ font-weight: bold; color: #000; font-size: 16px; }}
            .confirmado {{ text-align: center; color: #28a745; font-weight: bold; font-size: 16px; padding: 10px; background: #e6f9e6; border-radius: 5px; margin-top: 20px; border: 1px solid #c3e6cb; }}
            
            #recibo-impresso {{ display: none; }} 
            
            .btn {{ width: 320px; padding: 14px; margin: 5px 0; border: none; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .btn-zap {{ background-color: #25D366; color: white; }}
            .btn-down {{ background-color: #f8f9fa; color: #333; border: 1px solid #ddd; }}
            
            @media print {{
                body > *:not(#recibo-impresso) {{ display: none !important; }} 
                #recibo-impresso {{
                    display: flex !important; flex-direction: column; justify-content: space-between;
                    position: absolute; left: 0; top: 0; width: 100%; height: 140mm; 
                    font-family: 'Times New Roman', Times, serif; color: black; padding: 10mm 15mm; box-sizing: border-box;
                }}
                .print-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid black; padding-bottom: 15px; }}
                .print-logo {{ max-height: 70px; }}
                .print-empresa {{ text-align: center; flex-grow: 1; }}
                .print-empresa h2 {{ margin: 0; font-size: 22px; }}
                .print-empresa p {{ margin: 3px 0 0 0; font-size: 14px; color: #333; }}
                .print-valor {{ text-align: right; width: 25%; }}
                .print-valor h2 {{ margin: 0; font-size: 20px; font-weight: normal; text-transform: uppercase; }}
                .print-valor h3 {{ margin: 5px 0 0 0; font-size: 24px; }}
                .print-body {{ font-size: 18px; line-height: 1.6; text-align: justify; margin-top: 25px; }}
                .print-footer {{ text-align: center; margin-top: auto; }}
                .print-linha-ass {{ border-top: 1px solid black; width: 60%; margin: 35px auto 5px auto; }}
                .print-footer p {{ margin: 3px 0; font-size: 16px; }}
                .print-tesoura {{ border-top: 1px dashed #666; text-align: center; color: #666; padding-top: 5px; font-family: Arial, sans-serif; font-size: 12px; margin-top: 15px; }}
            }}
        </style>
    </head>
    <body>
    <div id="recibo-digital">
        <div class="cabecalho"><img src="data:image/png;base64,{img_base64}"><h3>PINGO D'ÁGUA NATAÇÃO</h3><p>RECIBO DIGITAL</p></div>
        <div class="divisor"></div>
        <div class="linha"><strong>ALUNO(A):</strong><span>{nome_seguro}</span></div>
        <div class="linha"><strong>REFERÊNCIA:</strong><span>{modalidade}</span></div>
        <div class="linha"><strong>VALOR:</strong><span>R$ {valor_pago}</span></div>
        <div class="linha"><strong>DATA:</strong><span>{data_hoje}</span></div>
        <div class="divisor"></div>
        <div class="confirmado">✅ PAGAMENTO CONFIRMADO</div>
    </div>
    <div id="recibo-impresso">
        <div class="print-header">
            <div style="width: 25%;"><img src="data:image/png;base64,{img_base64}" class="print-logo"></div>
            <div class="print-empresa"><h2>PINGO D'ÁGUA NATAÇÃO</h2><p>CNPJ: 00.000.000/0001-00</p><p>Jaboatão dos Guararapes - PE</p></div>
            <div class="print-valor"><h2>RECIBO</h2><h3>R$ {valor_pago}</h3></div>
        </div>
        <div class="print-body">
            Recebemos de <strong>{nome_seguro}</strong> a quantia de <strong>R$ {valor_pago}</strong>, referente ao pagamento da mensalidade da modalidade de <strong>{modalidade}</strong>.<br><br>
            Para maior clareza e validade, firmamos o presente recibo.
        </div>
        <div class="print-footer">
            <p>Jaboatão dos Guararapes, {data_hoje}</p><div class="print-linha-ass"></div>
            <p><strong>Assinatura do Responsável</strong></p><p>Pingo D'água Natação</p>
        </div>
        <div class="print-tesoura">
            ✂️ ---------------------------- Corte aqui para reaproveitar o papel ---------------------------- ✂️
        </div>
    </div>
    <button class="btn btn-zap" onclick="copiarEEnviar()">💬 Copiar e Abrir WhatsApp</button>
    <button class="btn btn-down" onclick="window.print()">🖨️ Imprimir Recibo Formal</button>
    <script>
        function copiarEEnviar() {{
            var btn = document.querySelector(".btn-zap"); var textoOriginal = btn.innerHTML; btn.innerHTML = "⏳ Copiando para memória...";
            html2canvas(document.querySelector("#recibo-digital"), {{scale: 3}}).then(canvas => {{
                canvas.toBlob(blob => {{
                    try {{
                        navigator.clipboard.write([new ClipboardItem({{ "image/png": blob }})]).then(() => {{
                            btn.innerHTML = "✅ Copiado! Cole no WhatsApp (Ctrl+V)";
                            setTimeout(() => {{ window.open("https://wa.me/55{numero_zap}?text=Ol%C3%A1!%20Tudo%20bem%3F%20Segue%20o%20seu%20comprovante%20de%20pagamento.%20%28Pressione%20'Colar'%20aqui%20na%20mensagem%20para%20receber%20a%20imagem%29%20%F0%9F%8F%8A%E2%80%8D%E2%99%82%EF%B8%8F%F0%9F%92%A6", "_blank"); btn.innerHTML = textoOriginal; }}, 1500);
                        }}).catch(e => alert("Erro ao copiar."));
                    }} catch(e) {{ alert("Erro ao copiar."); }}
                }});
            }});
        }}
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=650)

# -------------------------------------------------------------------
# 2. MARCA D'ÁGUA DE FUNDO
# -------------------------------------------------------------------
imagem_espaco = "logo.png"
if os.path.exists(imagem_espaco):
    with open(imagem_espaco, "rb") as arquivo_img:
        img_codificada = base64.b64encode(arquivo_img.read()).decode()
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]::before {{
        content: ""; background-image: url("data:image/png;base64,{img_codificada}");
        background-size: 500px; background-position: center; background-repeat: no-repeat;
        background-attachment: fixed; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        opacity: 0.12; pointer-events: none; z-index: 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. SEGURANÇA E ARQUIVOS BASE
# -------------------------------------------------------------------
arquivo_textos = "config_textos.json"
if not os.path.exists(arquivo_textos):
    json.dump({"senha_acesso": "pingo123", "chave_pix": "81999999999", "nome_recebedor": "Pingo D'água Natação", "msg_vencendo": "Seu vencimento está próximo.", "msg_atrasado": "Sua mensalidade está pendente.", "msg_aniversario": "Feliz Aniversário! 🎂🏊‍♂️"}, open(arquivo_textos, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
config_textos = json.load(open(arquivo_textos, "r", encoding="utf-8"))
SENHA_ACESSO = config_textos.get("senha_acesso", "pingo123")

if "logado" not in st.session_state: st.session_state["logado"] = False
if not st.session_state["logado"]:
    st.title("🔒 Acesso Restrito - Pingo D'água")
    senha_digitada = st.text_input("Senha:", type="password")
    if st.button("Entrar", use_container_width=True):
        if senha_digitada == SENHA_ACESSO: st.session_state["logado"] = True; st.rerun()
        else: st.error("Senha incorreta!")
    st.stop() 

# -------------------------------------------------------------------
# 4. CARREGAMENTO DE DADOS E MEMÓRIA
# -------------------------------------------------------------------
if "transacoes_feitas" not in st.session_state: st.session_state["transacoes_feitas"] = set()
if "pagamentos_recentes" not in st.session_state: st.session_state["pagamentos_recentes"] = set()
if "recibos_ocultos" not in st.session_state: st.session_state["recibos_ocultos"] = set()

hoje = datetime.now().date()

arquivo_precos = "banco_precos.csv"
if not os.path.exists(arquivo_precos):
    pd.DataFrame({"Modalidade": ["Natação Infantil", "Natação Adulto", "Hidroginástica"], "Valor (R$)": [79.99, 79.99, 70.99]}).to_csv(arquivo_precos, index=False)
df_precos = pd.read_csv(arquivo_precos)
TABELA_PRECOS = dict(zip(df_precos["Modalidade"], df_precos["Valor (R$)"]))

arquivo_turmas = "banco_turmas.csv"
if not os.path.exists(arquivo_turmas):
    pd.DataFrame({
        "Nome da Turma": ["Natação Infantil (Seg/Qua/Sex às 08:00)", "Natação Adulto (Ter/Qui às 19:00)"],
        "Capacidade Máxima": [10, 15]
    }).to_csv(arquivo_turmas, index=False)
df_turmas = pd.read_csv(arquivo_turmas)
lista_turmas = ["Sem Turma"] + df_turmas["Nome da Turma"].tolist()

arquivo_dados = "banco_alunos.csv"
arquivo_historico = "historico_caixa.csv"

if not os.path.exists(arquivo_dados):
    pd.DataFrame({
        "Nome do Aluno": ["Miguel Santos"], "Matrícula": ["Ativo"], "Data de Nascimento": ["2015-05-10"],
        "Modalidade": ["Natação Infantil"], "Turma": ["Natação Infantil (Seg/Qua/Sex às 08:00)"], 
        "Telefone": ["81988882222"], "Data de Vencimento": ["2026-09-10"], "Status": ["Atrasado"], "Ano_Ultimo_Parabens": [0]
    }).to_csv(arquivo_dados, index=False)

if not os.path.exists(arquivo_historico):
    pd.DataFrame(columns=["Data do Pagamento", "Aluno", "Modalidade", "Valor Recebido (R$)"]).to_csv(arquivo_historico, index=False)

df = pd.read_csv(arquivo_dados, dtype={"Telefone": str})
if "Turma" not in df.columns: df["Turma"] = "Sem Turma"
if "Matrícula" not in df.columns: df["Matrícula"] = "Ativo"
df["Data de Nascimento"] = pd.to_datetime(df["Data de Nascimento"], errors='coerce').dt.date
df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], errors='coerce').dt.date
if "Ano_Ultimo_Parabens" not in df.columns: df["Ano_Ultimo_Parabens"] = 0
df["Mensalidade (R$)"] = df["Modalidade"].map(TABELA_PRECOS).fillna(0.0)

def calcular_status(data_vencimento):
    if pd.isna(data_vencimento): return "Em dia" 
    dias = (data_vencimento - hoje).days
    if dias < 0: return "Atrasado"
    elif 0 <= dias <= 5: return "Perto de vencer"
    else: return "Em dia"
df["Status"] = df["Data de Vencimento"].apply(calcular_status)

def processar_pagamento(index_aluno, nome_aluno, modalidade_aluno, data_venc_atual, valor_pago):
    id_cob = f"{nome_aluno}_{data_venc_atual}"
    if id_cob in st.session_state["transacoes_feitas"]: return
    st.session_state["transacoes_feitas"].add(id_cob)
    st.session_state["pagamentos_recentes"].add(nome_aluno)
    
    df_hist = pd.read_csv(arquivo_historico)
    df_hist = pd.concat([df_hist, pd.DataFrame([{"Data do Pagamento": hoje.strftime("%d/%m/%Y"), "Aluno": nome_aluno, "Modalidade": modalidade_aluno, "Valor Recebido (R$)": valor_pago}])], ignore_index=True)
    df_hist.to_csv(arquivo_historico, index=False)

    df_atualiza = pd.read_csv(arquivo_dados)
    nova_data = pd.to_datetime(df_atualiza.at[index_aluno, "Data de Vencimento"], errors='coerce') + pd.DateOffset(months=1)
    df_atualiza.at[index_aluno, "Data de Vencimento"] = nova_data.strftime("%Y-%m-%d")
    df_atualiza.to_csv(arquivo_dados, index=False)
    if "tabela_alunos" in st.session_state: del st.session_state["tabela_alunos"]

with st.sidebar:
    st.title("🏊‍♂️ Pingo D'água")
    st.write("---")
    busca_nome = st.text_input("🔍 Buscar Aluno:")
    filtro_status = st.selectbox("📌 Filtrar Status:", ["Todos", "Atrasado", "Perto de vencer", "Em dia"])
    st.write("---")
    if st.button("🚪 Sair do Sistema"): st.session_state["logado"] = False; st.rerun()

# -------------------------------------------------------------------
# 5. ESTRUTURA DE ABAS 
# -------------------------------------------------------------------
aba1, aba2, aba3, aba4 = st.tabs(["🏊‍♂️ Gestão de Alunos", "💰 Histórico de Caixa", "📅 Grade de Aulas", "⚙️ Configurações"])

with aba1:
    df_ativos = df[df["Matrícula"] == "Ativo"]
    
    st.header("📈 Visão Geral do Espaço")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos Ativos", f"{len(df_ativos)} alunos")
    col2.metric("Receita Mensal Esperada", f"R$ {df_ativos['Mensalidade (R$)'].sum():.2f}".replace(".", ","))
    col3.metric("🔴 Valor em Atraso Base", f"R$ {df_ativos[df_ativos['Status'] == 'Atrasado']['Mensalidade (R$)'].sum():.2f}".replace(".", ","))
    
    st.write("---")
    st.subheader("📝 Painel de Cadastro e Edição")
    
    colunas_config = {
        "Status": st.column_config.TextColumn("Status", disabled=True),
        "Mensalidade (R$)": st.column_config.NumberColumn("Mensalidade (R$)", format="R$ %.2f", disabled=True),
        "Matrícula": st.column_config.SelectboxColumn("Matrícula", options=["Ativo", "Inativo"]),
        "Modalidade": st.column_config.SelectboxColumn("Modalidade", options=list(TABELA_PRECOS.keys())),
        "Turma": st.column_config.SelectboxColumn("Turma (Horário)", options=lista_turmas),
        "Data de Nascimento": st.column_config.DateColumn("Nascimento", format="DD/MM/YYYY"),
        "Data de Vencimento": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY"),
        "Telefone": st.column_config.TextColumn("Telefone"),
        "Ano_Ultimo_Parabens": None
    }

    df_editado = st.data_editor(df, num_rows="dynamic", column_config=colunas_config, use_container_width=True, hide_index=True, key="tabela_alunos")

    if st.button("💾 Salvar Modificações na Tabela", use_container_width=True):
        df_salvar = df_editado.copy()
        def formatar_data(val): return pd.to_datetime(val).strftime("%Y-%m-%d") if pd.notna(val) and str(val) not in ["", "None", "NaT", "nan"] else ""
        df_salvar["Data de Nascimento"] = df_salvar["Data de Nascimento"].apply(formatar_data)
        df_salvar["Data de Vencimento"] = df_salvar["Data de Vencimento"].apply(formatar_data)
        df_salvar["Matrícula"] = df_salvar["Matrícula"].fillna("Ativo")
        df_salvar["Turma"] = df_salvar["Turma"].fillna("Sem Turma")
        df_salvar.to_csv(arquivo_dados, index=False)
        if "tabela_alunos" in st.session_state: del st.session_state["tabela_alunos"]
        st.success("Tabela atualizada!"); st.rerun()

    st.write("---")
    st.subheader("📋 Painel de Cobrança Automática e Recibos")
    
    df_visualizacao = df_editado[df_editado["Matrícula"] == "Ativo"].copy()
    if busca_nome: df_visualizacao = df_visualizacao[df_visualizacao["Nome do Aluno"].str.contains(busca_nome, case=False, na=False)]
    if filtro_status != "Todos": df_visualizacao = df_visualizacao[df_visualizacao["Status"] == filtro_status]
    df_visualizacao["Prioridade"] = df_visualizacao["Status"].map({"Atrasado": 1, "Perto de vencer": 2, "Em dia": 3})
    df_visualizacao = df_visualizacao.sort_values(by="Prioridade").drop(columns=["Prioridade", "Ano_Ultimo_Parabens"])

    def colorir_linhas(row):
        cores = {'Em dia': '#c3e6cb', 'Atrasado': '#f5c6cb', 'Perto de vencer': '#ffeeba'}
        cor_fundo = cores.get(row['Status'], 'white')
        return [f"background-color: {cor_fundo}; color: black"] * len(row)

    st.dataframe(
        df_visualizacao.style
        .apply(colorir_linhas, axis=1)
        .format({
            "Mensalidade (R$)": lambda x: f"R$ {x:.2f}".replace(".", ",") if pd.notnull(x) else "R$ 0,00",
            "Data de Nascimento": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else "",
            "Data de Vencimento": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
        }), 
        use_container_width=True, hide_index=True
    )

    for index, row in df_visualizacao.iterrows():
        id_cob = f"{row['Nome do Aluno']}_{row['Data de Vencimento']}"
        v_br = f"{row['Mensalidade (R$)']:.2f}".replace(".", ",")
        
        if row["Status"] in ["Atrasado", "Perto de vencer"] and id_cob not in st.session_state["transacoes_feitas"]:
            col_wpp, col_pago = st.columns([3, 1])
            with col_wpp:
                dias_atraso = (hoje - row['Data de Vencimento']).days if row['Status'] == 'Atrasado' else 0
                v_final = row['Mensalidade (R$)'] + 10.00 if dias_atraso > 0 else row['Mensalidade (R$)']
                msg_base = config_textos["msg_atrasado"] if row["Status"] == "Atrasado" else config_textos["msg_vencendo"]
                link_wpp = f"https://wa.me/55{str(row['Telefone']).replace(' ', '')}?text={urllib.parse.quote(f'Olá! {msg_base} Valor: R$ {v_final:.2f}'.replace('.', ','))}"
                st.link_button(f"{'🔴' if row['Status'] == 'Atrasado' else '🟡'} Cobrar {row['Nome do Aluno']} (R$ {v_final:.2f})".replace('.', ','), link_wpp, use_container_width=True)
            with col_pago:
                st.button("✅ Confirmar Pagamento", key=f"btn_pago_{index}_{row['Data de Vencimento']}", on_click=processar_pagamento, args=(index, row['Nome do Aluno'], row['Modalidade'], row['Data de Vencimento'], v_final), use_container_width=True)
        else:
            if row['Nome do Aluno'] in st.session_state["pagamentos_recentes"] and row['Nome do Aluno'] not in st.session_state["recibos_ocultos"]:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.success(f"✅ Pagamento de {row['Nome do Aluno']} confirmado!")
                if c2.button(f"🧾 Emitir Recibo", key=f"btn_r_{index}", use_container_width=True): abrir_janela_recibo(row['Nome do Aluno'], row['Modalidade'], v_br, row['Telefone'])
                if c3.button("🧹 Concluir", key=f"btn_o_{index}", use_container_width=True): st.session_state["recibos_ocultos"].add(row['Nome do Aluno']); st.rerun()

with aba2:
    st.header("💰 Histórico de Entradas")
    df_historico = pd.read_csv(arquivo_historico)
    if not df_historico.empty:
        st.dataframe(df_historico.style.format({"Valor Recebido (R$)": lambda x: f"R$ {x:.2f}".replace(".", ",")}), use_container_width=True, hide_index=True)

# -------------------------------------------------------------------
# ABA 3 TOTALMENTE REFORMULADA: GRADE DE AULAS CATEGORIZADA
# -------------------------------------------------------------------
with aba3:
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.header("📅 Grade de Aulas e Lotação")
        st.write("Acompanhe a lotação separada por modalidade.")
    with col_t2:
        # Busca rápida para quando houver muitas turmas
        busca_turma = st.text_input("🔍 Buscar Turma (Ex: Ter/Qui ou 18:00):", "")
    
    df_ativos_aba3 = df[df["Matrícula"] == "Ativo"]
    
    if df_turmas.empty:
        st.info("Nenhuma turma cadastrada. Vá na aba de 'Configurações' para criar os horários.")
    else:
        turmas_exibidas = df_turmas.copy()
        if busca_turma:
            turmas_exibidas = turmas_exibidas[turmas_exibidas["Nome da Turma"].str.contains(busca_turma, case=False, na=False)]
            
        # Agrupa as turmas automaticamente baseadas na Tabela de Preços (Modalidades)
        modalidades_existentes = list(TABELA_PRECOS.keys())
        
        for modalidade in modalidades_existentes:
            # Pega as turmas que o nome começa com a modalidade
            turmas_da_mod = turmas_exibidas[turmas_exibidas["Nome da Turma"].str.startswith(modalidade, na=False)]
            
            if not turmas_da_mod.empty:
                st.write("---")
                st.subheader(f"🏊‍♂️ {modalidade}")
                
                colunas_grade = st.columns(3) # Organiza em 3 colunas
                
                for index, row in turmas_da_mod.reset_index().iterrows():
                    nome_completo = row["Nome da Turma"]
                    # Tira a palavra da modalidade para o cartão não ficar com texto gigante
                    nome_curto = nome_completo.replace(f"{modalidade} ", "") 
                    cap_max = int(row["Capacidade Máxima"])
                    
                    alunos_na_turma = df_ativos_aba3[df_ativos_aba3["Turma"] == nome_completo]
                    qtd_atual = len(alunos_na_turma)
                    vagas_livres = cap_max - qtd_atual
                    
                    if vagas_livres > 2: cor, status = "🟢", f"{vagas_livres} vagas livres"
                    elif vagas_livres > 0: cor, status = "🟡", f"Atenção: Só {vagas_livres} vagas"
                    else: cor, status = "🔴", "TURMA LOTADA"
                    
                    with colunas_grade[index % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{cor} {nome_curto}**")
                            st.write(f"Ocupação: **{qtd_atual} / {cap_max}**")
                            st.write(f"*{status}*")
                            
                            percentual = min(qtd_atual / cap_max, 1.0) if cap_max > 0 else 1.0
                            st.progress(percentual)
                            
                            with st.expander("Ver lista de alunos"):
                                if qtd_atual > 0:
                                    for aluno in alunos_na_turma["Nome do Aluno"].tolist(): 
                                        st.write(f"👤 {aluno}")
                                else:
                                    st.write("Vazio.")

with aba4:
    st.header("⚙️ Configurações do Sistema")
    
    # ---------------------------------------------------------
    # GESTÃO RÁPIDA E EXCLUSÃO INTUITIVA DE TURMAS
    # ---------------------------------------------------------
    st.subheader("📅 Gestão de Turmas e Horários")
    st.write("Crie novas turmas ou apague as existentes sem complicação.")
    
    with st.container(border=True):
        st.write("**➕ Criar Nova Turma**")
        with st.form("form_criar_turma"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: f_mod = st.selectbox("Modalidade", list(TABELA_PRECOS.keys()))
            with c2: f_dias = st.selectbox("Dias da Aula", ["Seg/Qua/Sex", "Ter/Qui", "Seg a Sex", "Sábado", "Domingo", "Livre"])
            with c3: f_hora = st.time_input("Horário", value=datetime.strptime("08:00", "%H:%M").time())
            with c4: f_cap = st.number_input("Capacidade", min_value=1, max_value=100, value=10)
                
            if st.form_submit_button("✅ Adicionar à Grade", use_container_width=True):
                nome_final = f"{f_mod} ({f_dias} às {f_hora.strftime('%H:%M')})"
                if nome_final in df_turmas["Nome da Turma"].values:
                    st.error(f"⚠️ A turma '{nome_final}' já existe!")
                else:
                    df_turmas = pd.concat([df_turmas, pd.DataFrame([{"Nome da Turma": nome_final, "Capacidade Máxima": f_cap}])], ignore_index=True)
                    df_turmas.to_csv(arquivo_turmas, index=False)
                    st.success(f"Turma '{nome_final}' criada!")
                    st.rerun()

    st.write("---")
    st.write("**📝 Editar ou Apagar Turmas Ativas**")
    st.info("Para **apagar** uma turma, basta marcar a caixinha '🗑️ Excluir' e clicar no botão de Salvar abaixo.")
    
    # Adicionando a caixinha de excluir de forma limpa
    df_turmas_ui = df_turmas.copy()
    df_turmas_ui["Excluir"] = False 
    
    colunas_turma_conf = {
        "Nome da Turma": st.column_config.TextColumn("Nome da Turma", disabled=True), # Protege o nome para não quebrar a lógica
        "Capacidade Máxima": st.column_config.NumberColumn("Vagas", min_value=1, step=1),
        "Excluir": st.column_config.CheckboxColumn("🗑️ Excluir?")
    }
    
    df_turmas_editado = st.data_editor(df_turmas_ui, num_rows="fixed", column_config=colunas_turma_conf, use_container_width=True, hide_index=True, key="tab_turmas")
    
    if st.button("💾 Salvar Alterações nas Turmas", use_container_width=True):
        # Filtra mantendo apenas quem NÃO foi marcado para excluir
        df_turmas_salvar = df_turmas_editado[df_turmas_editado["Excluir"] == False].drop(columns=["Excluir"])
        df_turmas_salvar.to_csv(arquivo_turmas, index=False)
        
        # Se alguma turma foi excluída, avisa e limpa as referências no cadastro de alunos
        if len(df_turmas_salvar) < len(df_turmas_editado):
            turmas_excluidas = set(df_turmas_editado["Nome da Turma"]) - set(df_turmas_salvar["Nome da Turma"])
            for turma_excluida in turmas_excluidas:
                df.loc[df["Turma"] == turma_excluida, "Turma"] = "Sem Turma"
            df.to_csv(arquivo_dados, index=False)
            
        st.success("Tabela de turmas atualizada com sucesso!")
        st.rerun()
        
    st.write("---")
    
    st.subheader("🏊‍♂️ Tabela de Preços")
    df_precos_editado = st.data_editor(df_precos, num_rows="dynamic", use_container_width=True, hide_index=True, key="tab_precos")
    if st.button("💾 Salvar Tabela de Preços", use_container_width=True):
        df_precos_editado.to_csv(arquivo_precos, index=False); st.rerun()
    st.write("---")
    
    st.subheader("📱 Textos e PIX")
    with st.form("form_textos"):
        novo_pix = st.text_input("🔑 PIX", value=config_textos["chave_pix"])
        novo_recebedor = st.text_input("👤 Recebedor", value=config_textos["nome_recebedor"])
        if st.form_submit_button("💾 Salvar Textos e PIX", use_container_width=True):
            config_textos["chave_pix"] = novo_pix; config_textos["nome_recebedor"] = novo_recebedor
            json.dump(config_textos, open(arquivo_textos, "w", encoding="utf-8"), ensure_ascii=False, indent=4); st.rerun()