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
    
    opcoes_menu = ["Dashboard", "Cadastrar Paciente", "Listar Pacientes", "Agendar Atendimento", "Lista de Atendimentos","Logs do Sistema" ,"Gerenciar Notas"]
    
    # Sincroniza o selectbox com o estado do menu
    menu = st.sidebar.selectbox(
        "Menu", 
        opcoes_menu,
        index=opcoes_menu.index(st.session_state.menu_atual)
    )
    st.session_state.menu_atual = menu

    # --- DASHBOARD DINÂMICO ---
    if menu == "Dashboard":
        # ATUALIZAÇÃO AUTOMÁTICA DOS NÚMEROS
        try:
            # Fazemos uma chamada rápida para pegar os números reais
            res_stats = requests.get(f"{BASE_URL}/dashboard/stats/{st.session_state.usuario_id}")
            if res_stats.status_code == 200:
                stats = res_stats.json()
                st.session_state.atendimentos = stats['atendimentos']
                st.session_state.pacientes = stats['pacientes']
                st.session_state.alertas = stats['alertas']
                st.session_state.total_registros = stats['total_registros']
        except Exception as e:
            st.error(f"Erro ao sincronizar dados: {e}")

        st.title(f"👋 Olá, {st.session_state.nome_usuario}!")
        st.write("Aqui está o seu resumo de hoje:")

        # 1. LINHA DE CARDS (Métricas Dinâmicas)
        c1, c2, c3, c4 = st.columns(4)
        card_style = "padding: 20px; border-radius: 15px; color: white; text-align: center; height: 130px; margin-bottom: 5px;"

        #Card Atendimentos
        with c1:
            st.markdown(f'<div style="background-color: #4CAF50; {card_style}"><h4>Atendimentos Hoje</h4><h2>👥 {st.session_state.atendimentos}</h2></div>', unsafe_allow_html=True)
            if st.button("📅 Ver Agenda", use_container_width=True):
                st.session_state.menu_atual = "Lista de Atendimentos"
                st.rerun()

        #Card Pacientes
        with c2:
            st.markdown(f'<div style="background-color: #FFB300; {card_style}"><h4>Crianças Acompanhadas</h4><h2>👦 {st.session_state.pacientes}</h2></div>', unsafe_allow_html=True)
            if st.button("📋 Ver Prontuários", use_container_width=True):
                st.session_state.menu_atual = "Listar Pacientes"
                st.rerun()
        #Card Alertas
        with c3:
            st.markdown(f'<div style="background-color: #FF5722; {card_style}"><h4>Alertas Ativos</h4><h2>⚠️ {st.session_state.alertas}</h2></div>', unsafe_allow_html=True)
            if st.button("⚠️ Ver Alertas", use_container_width=True):
                st.session_state.menu_atual = "Listar Pacientes"
                st.session_state.filtro_alerta = True # Ativa o filtro
                st.rerun()

        #Card Logs
        with c4:
            st.markdown(f'<div style="background-color: #2196F3; {card_style}"><h4>Últimos Registros</h4><h2>📝 {st.session_state.get("total_registros", 0)}</h2></div>', unsafe_allow_html=True)
            if st.button("📝 Ver Logs", use_container_width=True):
                st.session_state.menu_atual = "Logs do Sistema"
                st.rerun()

        st.divider()

        # 2. SEÇÃO DE CONTEÚDO (Próximos Atendimentos vs Notas)
        col_agenda, col_notas = st.columns([2, 1])

        with col_agenda:
            st.subheader("🗓️ Próximos Atendimentos")
            
            # Buscamos os atendimentos reais do banco para listar aqui
            try:
                res = requests.get(f"{API_ATENDIMENTOS}{st.session_state.usuario_id}")
                if res.status_code == 200:
                    agenda = res.json()
                    if not agenda:
                        st.info("Nenhum atendimento agendado.")
                    else:
                        # Mostra apenas os 3 primeiros para o Dashboard não ficar gigante
                        for a in agenda[:3]:
                            with st.container(border=True):
                                st.write(f"🕒 **{a['data']}** - {a['paciente_nome']}")
                        
                        if st.button("Ver Agenda Completa →"):
                            st.session_state.menu_atual = "Lista de Atendimentos"
                            st.rerun()
            except:
                st.error("Erro ao carregar agenda rápida.")

        # Notas Rápidas
        with col_notas:
            st.subheader("📌 Notas Recentes")
            try:
                res_n = requests.get(f"{BASE_URL}/notas/{st.session_state.usuario_id}")
                if res_n.status_code == 200:
                    notas = res_n.json()
                    # Mostra apenas as 3 últimas notas não concluídas para não poluir
                    notas_pendentes = [n for n in notas if not n['concluida']][:3]
                    
                    for n in notas_pendentes:
                        if n['tipo'] == "Urgente":
                            st.error(f"🚨 {n['conteudo']}")
                        else:
                            st.info(f"🔹 {n['conteudo']}")
                    
                    if not notas_pendentes:
                        st.write("Nenhuma tarefa pendente! 🙌")
            except:
                st.write("Sem notas para exibir.")

            st.divider()
            # Botão principal para a nova página
            if st.button("⚙️ Gerenciar Todas as Notas", use_container_width=True, type="primary"):
                st.session_state.menu_atual = "Gerenciar Notas"
                st.rerun()

    elif menu == "Gerenciar Notas":
        if st.button("⬅️ Voltar ao Dashboard"):
            st.session_state.menu_atual = "Dashboard"
            st.rerun()

        st.header("🗒️ Gerenciador de Notas")
        
        with st.expander("➕ Nova Tarefa", expanded=True):
            with st.form("form_nota"):
                texto = st.text_input("Descrição da tarefa")
                prioridade = st.selectbox("Prioridade", ["Normal", "Urgente"])
                if st.form_submit_button("Adicionar"):
                    payload = {"conteudo": texto, "tipo": prioridade, "usuario_id": st.session_state.usuario_id}
                    requests.post(f"{BASE_URL}/notas/", json=payload)
                    st.rerun()

        st.divider()

        # Listagem simplificada apenas com texto e lixeira
        try:
            res = requests.get(f"{BASE_URL}/notas/{st.session_state.usuario_id}")
            if res.status_code == 200:
                for n in res.json():
                    # Usamos apenas 2 colunas agora: Texto e Lixeira
                    col_txt, col_del = st.columns([9, 1])
                    
                    with col_txt:
                        if n['tipo'] == "Urgente":
                            st.error(f"🚨 {n['conteudo']}")
                        else:
                            st.info(f"🔹 {n['conteudo']}")
                            
                    with col_del:
                        # Botão de exclusão único por ID
                        if st.button("🗑️", key=f"del_pag_{n['id']}"):
                            requests.delete(f"{BASE_URL}/notas/{n['id']}")
                            st.rerun()
            else:
                st.write("Nenhuma nota encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar notas: {e}")
                    
    # --- CADASTRAR PACIENTE ---
    elif menu == "Cadastrar Paciente":

        col_v_pac, _ = st.columns([1, 4])
        with col_v_pac:
            if st.button("⬅️ Voltar", key="v_cad_pac"):
                st.session_state.menu_atual = "Listar Pacientes" # Volta para a lista
                st.rerun()

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
        # Navegação no topo
        col_v1, col_v2, col_espaco = st.columns([1, 2, 7])
        with col_v1:
            if st.button("⬅️ Voltar ao Dashboard", key="v_dash_p"):
                st.session_state.filtro_alerta = False
                st.session_state.menu_atual = "Dashboard"
                st.rerun()
        with col_v2:
            # Botão que leva ao formulário de cadastro
            if st.button("➕ Novo Paciente", type="primary", use_container_width=True):
                st.session_state.menu_atual = "Cadastrar Paciente"
                st.rerun()

        # Aviso visual se o filtro estiver ligado
        if st.session_state.get('filtro_alerta'):
            st.warning("🚨 Exibindo apenas pacientes com Ponto de Alerta!")
            if st.button("Mostrar Todos os Pacientes"):
                st.session_state.filtro_alerta = False
                st.rerun()

        st.header("📋 Prontuários dos Pacientes")
            
        url_completa = f"{API_PACIENTES}{st.session_state.usuario_id}"
       
        try:
            res = requests.get(url_completa)
            if res.status_code == 200:
                pacientes = res.json()
                if not pacientes:
                    st.info("Você ainda não tem pacientes cadastrados.")
                else:
                    # O FOR COMEÇA AQUI: percorrendo a lista que veio do banco
                    for p in pacientes:
                        
                        # LÓGICA DO FILTRO: 
                        # Se o filtro está ativo e o paciente NÃO tem alerta, o código ignora ele
                        if st.session_state.get('filtro_alerta') and not p.get('ponto_alerta'):
                            continue
                            
                        # Só desenha o expander para quem passar pelo filtro acima
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

        # Botão de Voltar
        col_v_ag, _ = st.columns([1, 4])
        with col_v_ag:
            if st.button("⬅️ Voltar", key="v_cad_ag"):
                st.session_state.menu_atual = "Lista de Atendimentos" # Volta para a lista
                st.rerun()

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

        # Navegação no topo
        col_a1, col_a2, col_espaco_at = st.columns([1, 2, 7])
        with col_a1:
            if st.button("⬅️ Voltar ao Dashboard", key="v_dash_a"):
                st.session_state.menu_atual = "Dashboard"
                st.rerun()
        with col_a2:
            # Botão que leva ao formulário de agendamento
            if st.button("📅 Novo Agendamento", type="primary", use_container_width=True):
                st.session_state.menu_atual = "Agendar Atendimento"
                st.rerun()

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

    elif menu == "Logs do Sistema":
            if st.button("⬅️ Voltar ao Dashboard"):
                st.session_state.menu_atual = "Dashboard"
                st.rerun()

            st.header("📝 Histórico de Registros")
            st.write("Estas são as atividades recentes no seu sistema:")

            try:
                # Pegamos os pacientes e atendimentos para montar um log simples
                res_p = requests.get(f"{API_PACIENTES}{st.session_state.usuario_id}")
                res_a = requests.get(f"{API_ATENDIMENTOS}{st.session_state.usuario_id}")
                
                if res_p.status_code == 200 and res_a.status_code == 200:
                    pacientes = res_p.json()
                    atendimentos = res_a.json()
                    
                    # Criamos uma lista de mensagens de log
                    logs = []
                    for p in pacientes:
                        logs.append(f"🟢 **Paciente Cadastrado:** {p['nome']}")
                    for a in atendimentos:
                        logs.append(f"🔵 **Atendimento Agendado:** {a['paciente_nome']} para {a['data']}")
                    
                    # Atualizamos o contador do Dashboard
                    st.session_state.total_registros = len(logs)
                    
                    if not logs:
                        st.info("Nenhuma atividade registrada ainda.")
                    else:
                        # Mostra os logs do mais novo para o mais antigo
                        for log in reversed(logs):
                            st.info(log)
                else:
                    st.error("Erro ao carregar registros.")
            except Exception as e:
                st.error(f"Falha na conexão: {e}")