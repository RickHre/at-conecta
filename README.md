🚀 Como Rodar o Projeto no seu GitHub/Codespaces
Siga os passos abaixo para configurar o ambiente e iniciar a aplicação.

1. Preparação do Ambiente
Após clonar o repositório no seu GitHub Codespaces, certifique-se de que as dependências necessárias estão instaladas:

# Ativar o ambiente virtual (se necessário)
source .venv/bin/activate

# Instalar as bibliotecas fundamentais
pip install fastapi uvicorn streamlit sqlalchemy requests passlib bcrypt

2. Configuração do Endereço (IMPORTANTE)
Como o Codespaces gera um link único para cada usuário, você precisa atualizar a URL de conexão no arquivo interface.py:

Vá na aba Ports do seu VS Code/Codespaces.

Localize a porta 8080.

Copie o endereço (Local Address) e cole na variável BASE_URL dentro do arquivo interface.py

3. Iniciando o Backend (API)
Abra um terminal e execute os comandos para criar o banco de dados e subir o servidor FastAPI:

# Opcional: remover banco antigo para um reset limpo
rm at_database.db

# Iniciar o servidor
uvicorn main:app --reload --port 8080

Clique em "Tornar público" quando o pop-up aparecer no canto inferior direito.

4. Iniciando o Frontend (Interface)
Abra um segundo terminal (clicando no +) e execute o Streamlit:

streamlit run interface.py

Clique em "Tornar público" quando o pop-up aparecer no canto inferior direito.

Clique na aba "Portas", na porta do strealite, clique em "Abrir no Navegador".

🛠️ Tecnologias Utilizadas
Backend: FastAPI (Python) com persistência em SQLite via SQLAlchemy.

Frontend: Streamlit com navegação dinâmica e métricas em tempo real.

Segurança: Criptografia de senhas com BCrypt.

Arquitetura: Separação de responsabilidades entre API e Interface.

📋 Funcionalidades Principais

Dashboard: Visão geral de atendimentos, pacientes e alertas ativos.
Prontuários: Cadastro e listagem de crianças com filtro de Ponto de Alerta.  
Agenda: Agendamento de sessões integrado aos dados do paciente.
Gerenciador de Notas: Sistema de tarefas rápidas para o dia a dia do AT.
