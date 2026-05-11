import streamlit as st
import requests

# 1. Configurações da página
st.set_page_config(page_title="AT Conecta - Univesp", layout="wide")

# link da aba 'Ports' do Codespaces
BASE_URL = "https://fictional-bassoon-69rj7jrg9qppc49vj-8080.app.github.dev"

# URLs específicas
API_PACIENTES = f"{BASE_URL}/pacientes/"
API_ATENDIMENTOS = f"{BASE_URL}/atendimentos/"
API_LOGIN = f"{BASE_URL}/login"

# 2. Inicializa o estado de login
if "logado" not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Acesso ao Sistema")
    tab_login, tab_cadastro = st.tabs(["Login", "Novo Usuário"])

    with tab_login:
        email_l = st.text_input("Email")
        senha_l = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            res = requests.post(API_LOGIN, json={"email": email_l, "senha": senha_l})
            if res.status_code == 200:
                data = res.json()
                st.session_state.logado = True
                st.session_state.usuario_id = data['id']
                st.session_state.nome_usuario = data['nome']
                # Guardamos os contadores do banco para os cards
                st.session_state.atendimentos = data['atendimentos']
                st.session_state.pacientes = data['pacientes']
                st.session_state.alertas = data['alertas']
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with tab_cadastro:
        st.subheader("Criar conta de Especialista")
        
        # Certifique-se de que estes nomes (nome_novo, etc) são os mesmos no payload
        nome_novo = st.text_input("Nome Completo", key="reg_nome")
        email_novo = st.text_input("Novo Email", key="reg_email")
        senha_novo = st.text_input("Nova Senha", type="password", key="reg_senha")
        
        if st.button("Cadastrar Especialista"):
            # O payload usa as variáveis que acabamos de criar acima
            payload = {
                "nome": nome_novo, 
                "email": email_novo, 
                "senha": senha_novo
            }
            
            try:
                # Faz a chamada para o link do Codespaces
                res = requests.post(f"{BASE_URL}/usuarios/", json=payload)
                
                if res.status_code == 200:
                    st.success("Conta criada! Já pode fazer login na outra aba.")
                else:
                    st.error(f"Erro: {res.status_code}")
            except Exception as e:
                st.error(f"Erro de conexão com o servidor: {e}")

# --- SISTEMA LOGADO ---
else:
    st.sidebar.title("📌 Navegação")
    st.sidebar.write(f"Logado como: **{st.session_state.nome_usuario}**")
    
    menu = st.sidebar.selectbox("Menu", 
        ["Dashboard", "Cadastrar Paciente", "Listar Pacientes", "Agendar Atendimento", "Lista de Atendimentos"])

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # --- DASHBOARD DINÂMICO ---
    if menu == "Dashboard":
        st.title(f"👋 Bem-vinda, {st.session_state.nome_usuario}!")
        
        c1, c2, c3, c4 = st.columns(4)
        card_style = "padding: 20px; border-radius: 15px; color: white; text-align: center; height: 120px;"

        with c1:
            st.markdown(f'<div style="background-color: #4CAF50; {card_style}"><h4>Atendimentos</h4><h2>👥 {st.session_state.atendimentos}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="background-color: #FFB300; {card_style}"><h4>Pacientes</h4><h2>👦 {st.session_state.pacientes}</h2></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="background-color: #FF5722; {card_style}"><h4>Alertas</h4><h2>⚠️ {st.session_state.alertas}</h2></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="background-color: #2196F3; {card_style}"><h4>Registros</h4><h2>📝 4</h2></div>', unsafe_allow_html=True)

    # --- CADASTRAR PACIENTE ---
    elif menu == "Cadastrar Paciente":
        st.header("👶 Novo Prontuário")
        with st.form("form_paciente"):
            nome = st.text_input("Nome da Criança")
            nasc = st.text_input("Data Nascimento (DD/MM/AAAA)")
            resp = st.text_input("Responsável")
            alerta = st.checkbox("Ponto de Alerta Ativo?")
            if st.form_submit_button("Salvar"):
                dados = {
                    "nome": nome, "data_nascimento": nasc, "responsavel": resp, 
                    "ponto_alerta": alerta, "usuario_id": st.session_state.usuario_id
                }
                requests.post(API_PACIENTES, json=dados)
                st.success("Cadastrado! Relogue para atualizar o Dashboard.")

    # --- AGENDAR ATENDIMENTO ---
    elif menu == "Agendar Atendimento":
        st.header("🗓️ Novo Agendamento")
        # Busca lista de pacientes para o selectbox
        res = requests.get(f"{API_PACIENTES}{st.session_state.usuario_id}")
        if res.status_code == 200:
            lista_p = res.json()
            with st.form("form_atend"):
                paciente = st.selectbox("Selecione o Paciente", lista_p, format_func=lambda x: x['nome'])
                data_at = st.text_input("Data e Hora (DD/MM/AAAA HH:MM)")
                if st.form_submit_button("Confirmar Agendamento"):
                    dados = {
                        "usuario_id": st.session_state.usuario_id,
                        "paciente_id": paciente['id'],
                        "data": data_at
                    }
                    requests.post(API_ATENDIMENTOS, json=dados)
                    st.success("Agendado com sucesso!")