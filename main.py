from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, PacienteDB, UsuarioDB, AtendimentoDB, engine, Base
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime

# Garante a criação das tabelas no Codespaces
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AT Conecta - Backend")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- DEPENDÊNCIA DO BANCO ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MODELOS DE VALIDAÇÃO (PYDANTIC) ---
class PacienteCreate(BaseModel):
    nome: str
    data_nascimento: str
    responsavel: str = None
    ponto_alerta: bool = False
    usuario_id: int

class AtendimentoCreate(BaseModel):
    usuario_id: int
    paciente_id: int
    data: str # Recebe como string "DD/MM/AAAA HH:MM"

class AtendimentoUpdate(BaseModel):
    data: str = None
    confirmado: str = None

# --- ROTAS DE USUÁRIO ---
@app.post("/usuarios/")
def criar_usuario(usuario: dict, db: Session = Depends(get_db)):
    # O bcrypt tem limite de 72 bytes, por isso o slice [:72]
    hash_da_senha = pwd_context.hash(usuario['senha'][:72])
    novo_user = UsuarioDB(email=usuario['email'], nome=usuario['nome'], senha_hash=hash_da_senha)
    db.add(novo_user)
    db.commit()
    return {"status": "Sucesso"}

@app.post("/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == dados['email'], UsuarioDB.deleted_at == None).first()
    if not user or not pwd_context.verify(dados['senha'][:72], user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Contadores dinâmicos para os Cards do Dashboard
    atendimentos = db.query(AtendimentoDB).filter(AtendimentoDB.usuario_id == user.id, AtendimentoDB.deleted_at == None).count()
    pacientes = db.query(PacienteDB).filter(PacienteDB.usuario_id == user.id, PacienteDB.deleted_at == None).count()
    alertas = db.query(PacienteDB).filter(PacienteDB.usuario_id == user.id, PacienteDB.deleted_at == None, PacienteDB.ponto_alerta == True).count()
    
    return {
        "nome": user.nome, 
        "id": user.id, 
        "atendimentos": atendimentos, 
        "pacientes": pacientes, 
        "alertas": alertas
    }

# DASHBOARD
@app.get("/metricas/{usuario_id}")
def obter_metricas(usuario_id: int, db: Session = Depends(get_db)):
    pacientes = db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None).count()
    atendimentos = db.query(AtendimentoDB).filter(AtendimentoDB.usuario_id == usuario_id, AtendimentoDB.deleted_at == None).count()
    alertas = db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None, PacienteDB.ponto_alerta == True).count()
    
    return {"pacientes": pacientes, "atendimentos": atendimentos, "alertas": alertas}

# --- ROTAS DE PACIENTES ---
@app.post("/pacientes/")
async def cadastrar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    novo = PacienteDB(**paciente.dict())
    db.add(novo)
    db.commit()
    return {"status": "Sucesso"}

@app.get("/pacientes/{usuario_id}")
async def listar_pacientes_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None).all()

@app.delete("/pacientes/{paciente_id}")
async def excluir_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteDB).filter(PacienteDB.id == paciente_id).first()
    if not paciente: raise HTTPException(status_code=404)
    paciente.deleted_at = datetime.utcnow() # Soft Delete
    db.commit()
    return {"status": "Removido"}

# --- ROTAS DE ATENDIMENTOS ---
@app.post("/atendimentos/")
async def criar_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    # Converte string para objeto datetime do Python
    dt_objeto = datetime.strptime(atendimento.data, "%d/%m/%Y %H:%M")
    novo = AtendimentoDB(
        usuario_id=atendimento.usuario_id,
        paciente_id=atendimento.paciente_id,
        data=dt_objeto
    )
    db.add(novo)
    db.commit()
    return {"status": "Sucesso"}

@app.get("/atendimentos/{usuario_id}")
async def listar_atendimentos(usuario_id: int, db: Session = Depends(get_db)):
    # Faz um JOIN para trazer o nome do paciente junto com o atendimento
    resultado = db.query(AtendimentoDB, PacienteDB.nome).join(
        PacienteDB, PacienteDB.id == AtendimentoDB.paciente_id
    ).filter(AtendimentoDB.usuario_id == usuario_id, AtendimentoDB.deleted_at == None).all()
    
    return [
        {"id": a.id, "data": a.data.strftime("%d/%m/%Y %H:%M"), "paciente_nome": nome} 
        for a, nome in resultado
    ]