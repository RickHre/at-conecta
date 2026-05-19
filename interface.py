import streamlit as st
import requests
import time
from requests import RequestException

st.set_page_config(page_title="AT Conecta - Univesp", layout="wide")

BASE_URL = "https://at-conecta.onrender.com"
ENDPOINTS = {
    "usuarios": "/usuarios/",
    "login": "/login",
    "pacientes": "/pacientes/",
    "atendimentos": "/atendimentos/",
    "notas": "/notas/",
    "dashboard": "/dashboard/stats/",
}

MENU_DASHBOARD = "Dashboard"
MENU_CADASTRAR_PACIENTE = "Cadastrar Paciente"
MENU_LISTAR_PACIENTES = "Listar Pacientes"
MENU_AGENDAR_ATENDIMENTO = "Agendar Atendimento"
MENU_LISTA_ATENDIMENTOS = "Lista de Atendimentos"
MENU_LOGS = "Logs do Sistema"
MENU_NOTAS = "Gerenciar Notas"
MENU_OPTIONS = [
    MENU_DASHBOARD,
    MENU_CADASTRAR_PACIENTE,
    MENU_LISTAR_PACIENTES,
    MENU_AGENDAR_ATENDIMENTO,
    MENU_LISTA_ATENDIMENTOS,
    MENU_LOGS,
    MENU_NOTAS,
]


def api_url(key: str, extra: str = "") -> str:
    return f"{BASE_URL}{ENDPOINTS[key]}{extra}"


def api_call(method: str, key: str, extra: str = "", **kwargs):
    try:
        return requests.request(method, api_url(key, extra), timeout=10, **kwargs)
    except RequestException as exc:
        st.error("Falha ao conectar com o servidor. Verifique sua rede ou URL.")
        st.session_state.last_error = str(exc)
        return None


def get_json(key: str, extra: str = ""):
    res = api_call("get", key, extra)
    return res.json() if res and res.ok else None


def post_json(key: str, payload: dict):
    return api_call("post", key, json=payload)


def delete_resource(key: str, extra: str):
    return api_call("delete", key, extra)


def init_state():
    st.session_state.setdefault("logado", False)
    st.session_state.setdefault("menu_atual", MENU_DASHBOARD)
    st.session_state.setdefault("filtro_alerta", False)
    st.session_state.setdefault("atendimentos", 0)
    st.session_state.setdefault("pacientes", 0)
    st.session_state.setdefault("alertas", 0)
    st.session_state.setdefault("total_registros", 0)


def goto(menu: str, **kwargs):
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.session_state.menu_atual = menu


def render_top_sidebar():
    st.sidebar.title("📌 Navegação")
    st.sidebar.write(f"Logado como: **{st.session_state.nome_usuario}**")
    menu = st.sidebar.selectbox(
        "Menu",
        MENU_OPTIONS,
        index=MENU_OPTIONS.index(st.session_state.menu_atual),
    )
    st.session_state.menu_atual = menu


def render_login_screen():
    st.title("🔐 Acesso ao Sistema")
    login_tab, signup_tab = st.tabs(["Login", "Novo Usuário"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                res = post_json("login", {"email": email, "senha": password})
                if res and res.ok:
                    data = res.json()
                    st.session_state.update(
                        logado=True,
                        usuario_id=data["id"],
                        nome_usuario=data["nome"],
                        atendimentos=data.get("atendimentos", 0),
                        pacientes=data.get("pacientes", 0),
                        alertas=data.get("alertas", 0),
                        total_registros=data.get("total_registros", 0),
                    )
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

    with signup_tab:
        st.subheader("Criar conta de Especialista")
        with st.form("signup_form"):
            nome = st.text_input("Nome Completo", key="reg_nome")
            email = st.text_input("Novo Email", key="reg_email")
            senha = st.text_input("Nova Senha", type="password", key="reg_senha")
            if st.form_submit_button("Cadastrar Especialista"):
                payload = {"nome": nome, "email": email, "senha": senha}
                res = post_json("usuarios", payload)
                if res and res.ok:
                    st.success("Conta criada! Já pode fazer login na outra aba.")
                else:
                    st.error(f"Erro ao criar usuário: {res.status_code if res else 'sem resposta'}")


def load_dashboard_stats():
    stats = get_json("dashboard", str(st.session_state.usuario_id))
    if stats:
        st.session_state.atendimentos = stats.get("atendimentos", st.session_state.atendimentos)
        st.session_state.pacientes = stats.get("pacientes", st.session_state.pacientes)
        st.session_state.alertas = stats.get("alertas", st.session_state.alertas)
        st.session_state.total_registros = stats.get("total_registros", st.session_state.total_registros)


def metric_card(label: str, value: str, color: str, button_label: str, target_menu: str, key_suffix: str, **kwargs):
    card_style = (
        "padding: 20px; border-radius: 15px; color: white; text-align: center;"
        " height: 130px; margin-bottom: 5px;"
    )
    st.markdown(
        f'<div style="background-color: {color}; {card_style}">'
        f"<h4>{label}</h4><h2>{value}</h2></div>",
        unsafe_allow_html=True,
    )
    st.button(
        button_label,
        use_container_width=True,
        key=f"card_{key_suffix}",
        on_click=goto,
        args=(target_menu,),
        kwargs=kwargs,
    )


def render_dashboard():
    load_dashboard_stats()
    st.title(f"👋 Olá, {st.session_state.nome_usuario}!")
    st.write("Aqui está o seu resumo de hoje:")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Atendimentos Hoje",
            f"👥 {st.session_state.atendimentos}",
            "#4CAF50",
            "📅 Ver Agenda",
            MENU_LISTA_ATENDIMENTOS,
            key_suffix="atendimentos"
        )
    with c2:
        metric_card(
            "Crianças Acompanhadas",
            f"👦 {st.session_state.pacientes}",
            "#FFB300",
            "📋 Ver Prontuários",
            MENU_LISTAR_PACIENTES,
            key_suffix="pacientes"
        )
    with c3:
        metric_card(
            "Alertas Ativos",
            f"⚠️ {st.session_state.alertas}",
            "#FF5722",
            "⚠️ Ver Alertas",
            MENU_LISTAR_PACIENTES,
            key_suffix="alertas",
            filtro_alerta=True,
        )
    with c4:
        metric_card(
            "Últimos Registros",
            f"📝 {st.session_state.total_registros}",
            "#2196F3",
            "📝 Ver Logs",
            MENU_LOGS,
            key_suffix="logs"
        )

    st.divider()
    col_agenda, col_notas = st.columns([2, 1])

    with col_agenda:
        st.subheader("🗓️ Próximos Atendimentos")
        agenda = get_json("atendimentos", str(st.session_state.usuario_id)) or []
        if not agenda:
            st.info("Nenhum atendimento agendado.")
        else:
            for atendimento in agenda[:3]:
                with st.container():
                    st.write(f"🕒 **{atendimento['data']}** - {atendimento['paciente_nome']}")
            st.button(
                "Ver Agenda Completa →",
                use_container_width=True,
                key="btn_dash_ver_agenda",
                on_click=goto,
                args=(MENU_LISTA_ATENDIMENTOS,),
            )

    with col_notas:
        st.subheader("📌 Notas Recentes")
        notas = get_json("notas", str(st.session_state.usuario_id)) or []
        notas_pendentes = [nota for nota in notas if not nota.get("concluida")][:3]
        if notas_pendentes:
            for nota in notas_pendentes:
                if nota.get("tipo") == "Urgente":
                    st.error(f"🚨 {nota['conteudo']}")
                else:
                    st.info(f"🔹 {nota['conteudo']}")
        else:
            st.write("Nenhuma tarefa pendente! 🙌")

        st.divider()
        st.button(
            "⚙️ Gerenciar Todas as Notas",
            use_container_width=True,
            type="primary",
            key="btn_dash_notas",
            on_click=goto,
            args=(MENU_NOTAS,),
        )


def render_notes():
    st.button(
        "⬅️ Voltar ao Dashboard",
        key="btn_notas_voltar",
        on_click=goto,
        args=(MENU_DASHBOARD,),
    )

    st.header("🗒️ Gerenciador de Notas")
    with st.expander("➕ Nova Tarefa", expanded=True):
        with st.form("form_nota"):
            texto = st.text_input("Descrição da tarefa")
            prioridade = st.selectbox("Prioridade", ["Normal", "Urgente"])
            if st.form_submit_button("Adicionar"):
                payload = {
                    "conteudo": texto,
                    "tipo": prioridade,
                    "usuario_id": st.session_state.usuario_id,
                }
                res = post_json("notas", payload)
                if res and res.ok:
                    st.toast("Nota criada com sucesso.", icon="✅")
                    st.rerun()
                else:
                    st.error("Falha ao criar nota.")

    st.divider()
    notas = get_json("notas", str(st.session_state.usuario_id)) or []
    if not notas:
        st.info("Nenhuma nota encontrada.")
        return

    for nota in notas:
        col_txt, col_del = st.columns([9, 1])
        with col_txt:
            if nota.get("tipo") == "Urgente":
                st.error(f"🚨 {nota['conteudo']}")
            else:
                st.info(f"🔹 {nota['conteudo']}")
        with col_del:
            if st.button("🗑️", key=f"del_nota_{nota['id']}"):
                res = delete_resource("notas", str(nota["id"]))
                if res and res.ok:
                    st.toast("Nota excluída.", icon="✅")
                    st.rerun()
                else:
                    st.error("Falha ao excluir nota.")


def render_register_patient():
    st.button(
        "⬅️ Voltar",
        key="btn_voltar_cad_paciente",
        on_click=goto,
        args=(MENU_LISTAR_PACIENTES,),
    )

    st.header("👶 Novo Prontuário")
    with st.form("form_paciente"):
        nome = st.text_input("Nome da Criança")
        nasc = st.text_input("Data Nascimento (DD/MM/AAAA)")
        resp = st.text_input("Responsável")
        alerta = st.checkbox("Ponto de Alerta Ativo?")
        
        if st.form_submit_button("Salvar"):
            payload = {
                "nome": nome,
                "data_nascimento": nasc,
                "responsavel": resp,
                "ponto_alerta": alerta,
                "usuario_id": st.session_state.usuario_id,
            }
            res = post_json("pacientes", payload)
            if res and res.ok:
                st.success("👶 Prontuário cadastrado com sucesso!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Erro ao cadastrar paciente.")


def render_patient_list():
    top_cols = st.columns([1, 2, 7])
    with top_cols[0]:
        st.button(
            "⬅️ Voltar ao Dashboard",
            key="btn_pacientes_voltar",
            on_click=goto,
            args=(MENU_DASHBOARD,),
        )
    with top_cols[1]:
        st.button(
            "➕ Novo Paciente",
            type="primary",
            use_container_width=True,
            key="btn_novo_paciente",
            on_click=goto,
            args=(MENU_CADASTRAR_PACIENTE,),
        )

    if st.session_state.filtro_alerta:
        st.warning("🚨 Exibindo apenas pacientes com Ponto de Alerta!")
        if st.button("Mostrar Todos os Pacientes", key="btn_mostrar_todos"):
            st.session_state.filtro_alerta = False
            st.rerun()

    st.header("📋 Prontuários dos Pacientes")
    pacientes = get_json("pacientes", str(st.session_state.usuario_id)) or []
    if not pacientes:
        st.info("Você ainda não tem pacientes cadastrados.")
        return

    for paciente in pacientes:
        if st.session_state.filtro_alerta and not paciente.get("ponto_alerta"):
            continue
        with st.expander(f"👤 {paciente['nome']}"):
            st.write(f"**Responsável:** {paciente.get('responsavel', '—')}")
            st.write(f"**Nascimento:** {paciente.get('data_nascimento', '—')}")
            if paciente.get("ponto_alerta"):
                st.warning("⚠️ Ponto de Alerta Ativo")


def render_schedule_form():
    st.button(
        "⬅️ Voltar",
        key="btn_voltar_agendamento",
        on_click=goto,
        args=(MENU_LISTA_ATENDIMENTOS,),
    )

    st.header("🗓️ Novo Agendamento")
    pacientes = get_json("pacientes", str(st.session_state.usuario_id)) or []
    if not pacientes:
        st.info("Cadastre um paciente antes de agendar.")
        return

    with st.form("form_atend"):
        paciente = st.selectbox("Selecione o Paciente", pacientes, format_func=lambda x: x["nome"])
        data_sel = st.date_input("Data do Atendimento")
        hora_sel = st.time_input("Horário")
        
        if st.form_submit_button("Confirmar Agendamento"):
            data_formatada = f"{data_sel.strftime('%d/%m/%Y')} {hora_sel.strftime('%H:%M')}"
            payload = {
                "usuario_id": st.session_state.usuario_id,
                "paciente_id": paciente["id"],
                "data": data_formatada,
            }
            res = post_json("atendimentos", payload)
            if res and res.ok:
                st.success(f"Agendado: {paciente['nome']} em {data_formatada}")
                st.balloons()
                time.sleep(2.5)
                st.rerun()
            else:
                st.error("Erro ao salvar no banco de dados.")


def render_appointments():
    cols = st.columns([1, 2, 7])
    with cols[0]:
        st.button(
            "⬅️ Voltar ao Dashboard",
            key="btn_agenda_voltar",
            on_click=goto,
            args=(MENU_DASHBOARD,),
        )
    with cols[1]:
        st.button(
            "📅 Novo Agendamento",
            type="primary",
            use_container_width=True,
            key="btn_novo_agendamento",
            on_click=goto,
            args=(MENU_AGENDAR_ATENDIMENTO,),
        )

    st.header("📅 Agenda de Atendimentos")
    atendimentos = get_json("atendimentos", str(st.session_state.usuario_id)) or []
    if not atendimentos:
        st.info("Sua agenda está vazia para os próximos dias.")
        return

    for atendimento in atendimentos:
        with st.container():
            cols = st.columns([1, 2, 1])
            cols[0].write(f"🗓️ **{atendimento['data']}**")
            cols[1].write(f"👤 {atendimento['paciente_nome']}")
            if cols[2].button("Cancelar", key=f"del_at_{atendimento['id']}"):
                res = delete_resource("atendimentos", str(atendimento["id"]))
                if res and res.ok:
                    st.toast("Atendimento cancelado.", icon="✅")
                    st.rerun()
                else:
                    st.error("Falha ao cancelar atendimento.")
            st.divider()


def render_logs():
    st.button(
        "⬅️ Voltar ao Dashboard",
        key="btn_logs_voltar",
        on_click=goto,
        args=(MENU_DASHBOARD,),
    )

    st.header("📝 Histórico de Registros")
    st.write("Estas são as atividades recentes no seu sistema:")

    pacientes = get_json("pacientes", str(st.session_state.usuario_id)) or []
    atendimentos = get_json("atendimentos", str(st.session_state.usuario_id)) or []
    logs = [f"🟢 **Paciente Cadastrado:** {p['nome']}" for p in pacientes]
    logs += [f"🔵 **Atendimento Agendado:** {a['paciente_nome']} para {a['data']}" for a in atendimentos]

    st.session_state.total_registros = len(logs)
    if not logs:
        st.info("Nenhuma atividade registrada ainda.")
        return

    for log in reversed(logs):
        st.info(log)


init_state()

if not st.session_state.logado:
    render_login_screen()
else:
    render_top_sidebar()
    page = st.session_state.menu_atual
    if page == MENU_DASHBOARD:
        render_dashboard()
    elif page == MENU_NOTAS:
        render_notes()
    elif page == MENU_CADASTRAR_PACIENTE:
        render_register_patient()
    elif page == MENU_LISTAR_PACIENTES:
        render_patient_list()
    elif page == MENU_AGENDAR_ATENDIMENTO:
        render_schedule_form()
    elif page == MENU_LISTA_ATENDIMENTOS:
        render_appointments()
    elif page == MENU_LOGS:
        render_logs()
    else:
        st.error("Menu desconhecido. Por favor, reinicie a página.")
