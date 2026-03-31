import streamlit as st
import requests

# 1. Configurações da página (Sempre no topo)
st.set_page_config(page_title="Gestão AT - Univesp", layout="wide")
API_URL = "http://127.0.0.1:8080/pacientes/"

# 2. Inicializa o estado de login se não existir
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.nome_usuario = ""

# --- FLUXO DE ACESSO (LOGIN/CADASTRO) ---
if not st.session_state.logado:
    st.title("🔐 AT Conecta - Acesso")
    
    aba_login, aba_cadastro = st.tabs(["Login", "Criar Conta"])
    
    with aba_login:
        email_l = st.text_input("Email", key="l_email")
        senha_l = st.text_input("Senha", type="password", key="l_senha")
        if st.button("Entrar"):
            try:
                res = requests.post("http://127.0.0.1:8080/login", json={"email": email_l, "senha": senha_l})
                if res.status_code == 200:
                    st.session_state.logado = True
                    st.session_state.nome_usuario = res.json()['nome']
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
            except:
                st.error("Erro: O servidor Backend está desligado.")

    with aba_cadastro:
        nome_c = st.text_input("Nome Completo")
        email_c = st.text_input("Email", key="c_email")
        senha_c = st.text_input("Senha", type="password", key="c_senha")
        if st.button("Cadastrar"):
            payload = {"nome": nome_c, "email": email_c, "senha": senha_c}
            requests.post("http://127.0.0.1:8080/usuarios/", json=payload)
            st.success("Cadastro realizado! Agora faça o login.")

# --- SISTEMA LOGADO (DASHBOARD E GESTÃO) ---
else:
    # Sidebar - Identificação e Navegação
    st.sidebar.title("📌 Navegação")
    st.sidebar.write(f"Logado como: **{st.session_state.nome_usuario}**")
    
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Cadastrar Paciente", "Listar Pacientes"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # --- TELA: DASHBOARD ---
    if menu == "Dashboard":
        st.title(f"👋 Bem-vindo (a), {st.session_state.nome_usuario}!")
        st.write("Aqui está o seu resumo de hoje:")
        
        # 1. LINHA DE CARDS COLORIDOS (Métricas)
        # 4 colunas para os 4 cards principais
        c1, c2, c3, c4 = st.columns(4)
        
        # Estilo padrão para os cards (CSS)
        card_style = "padding: 20px; border-radius: 15px; color: white; text-align: center; height: 120px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);"

        with c1:
            st.markdown(f'<div style="background-color: #4CAF50; {card_style}">'
                        f'<p style="margin:0; font-size:14px;">Atendimentos Hoje</p>'
                        f'<h2 style="margin:10px 0;">👥 3</h2></div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown(f'<div style="background-color: #FFB300; {card_style}">'
                        f'<p style="margin:0; font-size:14px;">Crianças Acompanhadas</p>'
                        f'<h2 style="margin:10px 0;">👦 5</h2></div>', unsafe_allow_html=True)

        with c3:
            st.markdown(f'<div style="background-color: #FF5722; {card_style}">'
                        f'<p style="margin:0; font-size:14px;">Alertas Ativos</p>'
                        f'<h2 style="margin:10px 0;">⚠️ 2</h2></div>', unsafe_allow_html=True)

        with c4:
            st.markdown(f'<div style="background-color: #2196F3; {card_style}">'
                        f'<p style="margin:0; font-size:14px;">Últimos Registros</p>'
                        f'<h2 style="margin:10px 0;">📝 4</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
        st.divider()

        # 2. SEÇÃO DE AGENDA E NOTAS (2 colunas)
        col_esq, col_dir = st.columns([2, 1]) # A esquerda é o dobro da direita

        with col_esq:
            st.subheader("🗓️ Próximos Atendimentos")
            # Criando a lista de atendimentos como na imagem
            with st.container(border=True):
                st.write("**10:00** - João Santos - Escola ABC")
                st.write("**11:30** - Mariana Alves - Escola XYZ")
                st.write("**14:00** - Lucas Pereira - Visita no Parque")
                st.button("Ver Agenda Completa ➔", use_container_width=True)

        with col_dir:
            st.subheader("📌 Notas Rápidas")
            # Post-its coloridos usando as mensagens nativas do Streamlit
            st.warning("📝 Levar material de jogos sociais")
            st.error("🚨 Reunião com a Psicóloga às 16h")

        # 3. GRÁFICO DE EVOLUÇÃO (Simulação)
        st.divider()
        st.subheader("📈 Tendências de Atendimento")
        # Criando dados fictícios para o gráfico
        import pandas as pd
        dados_grafico = pd.DataFrame({
            'Meses': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
            'Sessões': [10, 15, 8, 22, 18]
        }).set_index('Meses')
        
        st.line_chart(dados_grafico)

    # --- TELA: CADASTRAR ---
    elif menu == "Cadastrar Paciente":
        st.header("🏥 Novo Cadastro de Paciente")
        with st.form("form_paciente"):
            nome = st.text_input("Nome do Paciente")
            nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
            responsavel = st.text_input("Responsável")
            alerta = st.checkbox("Ponto de Alerta?")
            enviar = st.form_submit_button("Salvar no Banco de Dados")

            if enviar:
                dados = {"nome": nome, "data_nascimento": nascimento, "responsavel": responsavel, "ponto_alerta": alerta}
                res = requests.post(API_URL, json=dados)
                if res.status_code == 200:
                    st.success(f"Paciente {nome} cadastrado com sucesso!")
                else:
                    st.error("Erro ao cadastrar.")

    # --- TELA: LISTAR ---
    elif menu == "Listar Pacientes":
        st.header("📋 Prontuários dos Pacientes")
        res = requests.get(API_URL)
        
        if res.status_code == 200:
            pacientes = res.json()
            if not pacientes:
                st.info("Nenhum paciente cadastrado.")
            else:
                for p in pacientes:
                    with st.expander(f"{'⚠️ ' if p.get('ponto_alerta') else '✅ '} {p['nome']}", expanded=True):
                        col_info, col_btn = st.columns([4, 1])
                        with col_info:
                            st.write(f"**Responsável:** {p['responsavel']}")
                            st.write(f"**Nascimento:** {p['data_nascimento']}")
                            if p.get('ponto_alerta'):
                                st.warning("🚨 ESTE PACIENTE POSSUI PONTO DE ALERTA ATIVO")
                        
                        with col_btn:
                            if st.button("🗑️ Excluir", key=f"del_{p['id']}"):
                                st.session_state[f"confirm_del_{p['id']}"] = True

                        if st.session_state.get(f"confirm_del_{p['id']}"):
                            st.error(f"Confirma a exclusão de {p['nome']}?")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ SIM", key=f"sim_{p['id']}", use_container_width=True):
                                requests.delete(f"{API_URL}{p['id']}")
                                del st.session_state[f"confirm_del_{p['id']}"]
                                st.rerun()
                            if c2.button("❌ NÃO", key=f"nao_{p['id']}", use_container_width=True):
                                del st.session_state[f"confirm_del_{p['id']}"]
                                st.rerun()