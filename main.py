from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, PacienteDB, UsuarioDB  # Adicionei UsuarioDB aqui
from pydantic import BaseModel
from passlib.context import CryptContext
from database import engine, Base

Base.metadata.create_all(bind=engine)

# 1. Configuração do FastAPI
app = FastAPI(title="Sistema de Gestão AT")

# 2. Contexto para criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Função para abrir/fechar conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Modelos de dados (Pydantic)
class PacienteCreate(BaseModel):
    nome: str
    data_nascimento: str
    responsavel: str = None
    ponto_alerta: bool = False

# --- ROTAS DE USUÁRIO (LOGIN/CADASTRO) ---

@app.post("/usuarios/")
def criar_usuario(usuario: dict, db: Session = Depends(get_db)):
    hash_da_senha = pwd_context.hash(usuario['senha'])
    novo_user = UsuarioDB(
        email=usuario['email'],
        nome=usuario['nome'],
        senha_hash=hash_da_senha
    )
    db.add(novo_user)
    db.commit()
    return {"status": "Usuário criado com sucesso"}

@app.post("/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == dados['email']).first()
    if not user or not pwd_context.verify(dados['senha'], user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    return {"nome": user.nome, "email": user.email}

# --- ROTAS DE PACIENTES ---

@app.post("/pacientes/")
async def cadastrar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    novo_paciente = PacienteDB(
        nome=paciente.nome,
        data_nascimento=paciente.data_nascimento,
        responsavel=paciente.responsavel,
        ponto_alerta=paciente.ponto_alerta
    )
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)
    return {"status": "Sucesso", "id": novo_paciente.id}

@app.get("/pacientes/")
async def listar_pacientes(db: Session = Depends(get_db)):
    pacientes = db.query(PacienteDB).all()
    return pacientes

@app.delete("/pacientes/{paciente_id}")
async def excluir_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteDB).filter(PacienteDB.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    db.delete(paciente)
    db.commit()
    return {"status": "Sucesso", "mensagem": f"Paciente {paciente_id} removido."}