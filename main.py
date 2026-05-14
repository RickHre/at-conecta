from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, PacienteDB, UsuarioDB, AtendimentoDB, engine, Base, NotaDB
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime

# Inicialização do Banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AT Conecta - Backend Otimizado")
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
    data: str 

class NotaCreate(BaseModel):
    conteudo: str
    tipo: str
    usuario_id: int

# --- ROTAS DE USUÁRIO & AUTENTICAÇÃO ---

@app.post("/usuarios/")
def criar_usuario(usuario: dict, db: Session = Depends(get_db)):
    # Slice de 72 bytes para compatibilidade com bcrypt [cite: 3]
    hash_da_senha = pwd_context.hash(usuario['senha'][:72])
    novo_user = UsuarioDB(email=usuario['email'], nome=usuario['nome'], senha_hash=hash_da_senha)
    db.add(novo_user)
    db.commit()
    return {"message": "Usuário criado com sucesso"}

@app.post("/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == dados['email'], UsuarioDB.deleted_at == None).first()
    if not user or not pwd_context.verify(dados['senha'][:72], user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Busca estatísticas iniciais para alimentar o session_state 
    stats = obter_estatisticas_base(user.id, db)
    
    return {
        "id": user.id,
        "nome": user.nome,
        **stats
    }

# --- FUNÇÃO AUXILIAR DE ESTATÍSTICAS ---
def obter_estatisticas_base(usuario_id: int, db: Session):
    atendimentos = db.query(AtendimentoDB).filter(AtendimentoDB.usuario_id == usuario_id, AtendimentoDB.deleted_at == None).count()
    pacientes = db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None).count()
    alertas = db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None, PacienteDB.ponto_alerta == True).count()
    
    return {
        "atendimentos": atendimentos,
        "pacientes": pacientes,
        "alertas": alertas,
        "total_registros": atendimentos + pacientes
    }

@app.get("/dashboard/stats/{usuario_id}")
def get_stats(usuario_id: int, db: Session = Depends(get_db)):
    return obter_estatisticas_base(usuario_id, db)

# --- ROTAS DE PACIENTES ---

@app.post("/pacientes/")
async def cadastrar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    novo = PacienteDB(**paciente.dict())
    db.add(novo)
    db.commit()
    return {"message": "Paciente cadastrado com sucesso"}

@app.get("/pacientes/{usuario_id}")
async def listar_pacientes(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(PacienteDB).filter(PacienteDB.usuario_id == usuario_id, PacienteDB.deleted_at == None).all()

@app.delete("/pacientes/{paciente_id}")
async def excluir_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteDB).filter(PacienteDB.id == paciente_id).first()
    if not paciente: 
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    paciente.deleted_at = datetime.utcnow() # Soft Delete de segurança
    db.commit()
    return {"message": "Paciente removido do sistema"}

# --- ROTAS DE ATENDIMENTOS ---

@app.post("/atendimentos/")
async def criar_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    dt_objeto = datetime.strptime(atendimento.data, "%d/%m/%Y %H:%M")
    novo = AtendimentoDB(
        usuario_id=atendimento.usuario_id,
        paciente_id=atendimento.paciente_id,
        data=dt_objeto
    )
    db.add(novo)
    db.commit()
    return {"message": "Atendimento agendado"}

@app.get("/atendimentos/{usuario_id}")
async def listar_atendimentos(usuario_id: int, db: Session = Depends(get_db)):
    resultado = db.query(AtendimentoDB, PacienteDB.nome).join(
        PacienteDB, PacienteDB.id == AtendimentoDB.paciente_id
    ).filter(AtendimentoDB.usuario_id == usuario_id, AtendimentoDB.deleted_at == None).all()
    
    return [
        {"id": a.id, "data": a.data.strftime("%d/%m/%Y %H:%M"), "paciente_nome": nome} 
        for a, nome in resultado
    ]

# --- ROTAS DE NOTAS ---

@app.post("/notas/")
def criar_nota(nota: NotaCreate, db: Session = Depends(get_db)):
    nova_nota = NotaDB(**nota.dict())
    db.add(nova_nota)
    db.commit()
    return {"message": "Nota salva"}

@app.get("/notas/{usuario_id}")
def listar_notas(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(NotaDB).filter(NotaDB.usuario_id == usuario_id, NotaDB.deleted_at == None).all()

@app.delete("/notas/{nota_id}")
def excluir_nota(nota_id: int, db: Session = Depends(get_db)):
    nota = db.query(NotaDB).filter(NotaDB.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    db.delete(nota)
    db.commit()
    return {"message": "Nota excluída definitivamente"}