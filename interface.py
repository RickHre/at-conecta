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

# 2. Inicializa o estado de login e navegação
if "logado" not in st.session_state:
    st.session_state.logado = False
if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "Dashboard"

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
    
    opcoes_menu = ["Dashboard", "Cadastrar Paciente", "Listar Pacientes", "Agendar Atendimento", "Lista de Atendimentos"]
    
    # Sincroniza o selectbox com o estado do menu
    menu = st.sidebar.selectbox(
        "Menu", 
        opcoes_menu,
        index=opcoes_menu.index(st.session_state.menu_atual)
    )
    st.session_state.menu_atual = menu

    # --- DASHBOARD DINÂMICO ---
    if menu == "Dashboard":
        st.title(f"👋 Bem-vindo(a), {st.session_state.nome_usuario}!")

        # Atualiza métricas (Opcional: Verifique se criou a rota /metricas no main.py)
        try:
            r = requests.get(f"{BASE_URL}/metricas/{st.session_state.usuario_id}")
            if r.status_code == 200:
                m = r.json()
                st.session_state.pacientes = m['pacientes']
                st.session_state.atendimentos = m['atendimentos']
                st.session_state.alertas = m['alertas']
        except:
            pass

        c1, c2, c3, c4 = st.columns(4)
        card_style = "padding: 20px; border-radius: 15px; color: white; text-align: center; height: 120px; margin-bottom: 10px;"

        with c1:
            st.markdown(f'<div style="background-color: #4CAF50; {card_style}"><h4>Atendimentos</h4><h2>👥 {st.session_state.atendimentos}</h2></div>', unsafe_allow_html=True)
            if st.button("📅 Ver Agenda", use_container_width=True):
                st.session_state.menu_atual = "Lista de Atendimentos"
                st.rerun()

        with c2:
            st.markdown(f'<div style="background-color: #FFB300; {card_style}"><h4>Pacientes</h4><h2>👦 {st.session_state.pacientes}</h2></div>', unsafe_allow_html=True)
            if st.button("📋 Ver Prontuários", use_container_width=True):
                st.session_state.menu_atual = "Listar Pacientes"
                st.rerun()

        # Cards 3 e 4 mantêm o visual, mas botões ficam desabilitados por enquanto
        with c3:
            st.markdown(f'<div style="background-color: #FF5722; {card_style}"><h4>Alertas</h4><h2>⚠️ {st.session_state.alertas}</h2></div>', unsafe_allow_html=True)
            st.button("⚠️ Ver Alertas", use_container_width=True, disabled=True)

        with c4:
            st.markdown(f'<div style="background-color: #2196F3; {card_style}"><h4>Registros</h4><h2>📝 4</h2></div>', unsafe_allow_html=True)
            st.button("📝 Ver Logs", use_container_width=True, disabled=True)
            
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

    # --- Listar Pacientes ---
    elif menu == "Listar Pacientes":
        st.header("📋 Prontuários dos Pacientes")
        
        # Montando a URL com o ID do usuário logado
        url_completa = f"{API_PACIENTES}{st.session_state.usuario_id}"
        
        try:
            res = requests.get(url_completa)
            if res.status_code == 200:
                pacientes = res.json()
                if not pacientes:
                    st.info("Você ainda não tem pacientes cadastrados.")
                else:
                    for p in pacientes:
                        with st.expander(f"👤 {p['nome']}"):
                            st.write(f"**Responsável:** {p['responsavel']}")
                            st.write(f"**Nascimento:** {p['data_nascimento']}")
                            if p.get('ponto_alerta'):
                                st.warning("⚠️ Ponto de Alerta Ativo")
            else:
                st.error(f"Erro ao buscar dados: {res.status_code}")
        except Exception as e:
            st.error(f"Falha na conexão: {e}")

    # --- AGENDAR ATENDIMENTO ---
    elif menu == "Agendar Atendimento":
        st.header("🗓️ Novo Agendamento")
        
        # Busca lista de pacientes
        res = requests.get(f"{API_PACIENTES}{st.session_state.usuario_id}")
        
        if res.status_code == 200:
            lista_p = res.json()
            
            with st.form("form_atend"):
                paciente = st.selectbox("Selecione o Paciente", lista_p, format_func=lambda x: x['nome'])
                
                # Campos separados e validados
                data_col, hora_col = st.columns(2)
                with data_col:
                    data_sel = st.date_input("Data do Atendimento")
                with hora_col:
                    hora_sel = st.time_input("Horário")
                
                if st.form_submit_button("Confirmar Agendamento"):
                    # Combinamos a data e hora no formato que o Backend espera
                    data_formatada = f"{data_sel.strftime('%d/%m/%Y')} {hora_sel.strftime('%H:%M')}"
                    
                    dados = {
                        "usuario_id": st.session_state.usuario_id,
                        "paciente_id": paciente['id'],
                        "data": data_formatada
                    }
                    
                    res_post = requests.post(API_ATENDIMENTOS, json=dados)
                    if res_post.status_code == 200:
                        st.success(f"Agendado: {paciente['nome']} em {data_formatada}")
                        st.balloons() # Um toque de comemoração pelo sucesso!
                    else:
                        st.error("Erro ao salvar no banco de dados.")

    # --- LISTA DE ATENDIMENTOS ---
    elif menu == "Lista de Atendimentos":
        st.header("📅 Agenda de Atendimentos")
        
        url_atendimentos = f"{API_ATENDIMENTOS}{st.session_state.usuario_id}"
        
        try:
            res = requests.get(url_atendimentos)
            if res.status_code == 200:
                atendimentos = res.json()
                
                if not atendimentos:
                    st.info("Sua agenda está vazia para os próximos dias.")
                else:
                    # Ordenar por data (opcional, mas recomendado para engenharia)
                    for a in atendimentos:
                        with st.container():
                            # Criamos um layout de linha para cada atendimento
                            col_data, col_nome, col_status = st.columns([1, 2, 1])
                            
                            with col_data:
                                st.write(f"🗓️ **{a['data']}**")
                            
                            with col_nome:
                                st.write(f"👤 {a['paciente_nome']}")
                            
                            with col_status:
                                # Um botão de excluir para cada atendimento
                                if st.button("Cancelar", key=f"del_at_{a['id']}"):
                                    requests.delete(f"{API_ATENDIMENTOS}{a['id']}")
                                    st.toast(f"Atendimento de {a['paciente_nome']} cancelado.")
                                    st.rerun()
                            st.divider()
            else:
                st.error("Não foi possível carregar a agenda.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")                    