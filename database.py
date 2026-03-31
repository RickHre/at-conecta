from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean

# 1. Cria o arquivo do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./at_database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Definição da Tabela de Pacientes (O "Modelo" do Banco)
class PacienteDB(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    data_nascimento = Column(String)
    responsavel = Column(String, nullable=True)
    ponto_alerta = Column(Boolean, default=False)

# 3. Novo Modelo para Usuários
class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    senha_hash = Column(String)  # Nunca guardamos a senha real!

# Cria as tabelas no arquivo .db
Base.metadata.create_all(bind=engine)