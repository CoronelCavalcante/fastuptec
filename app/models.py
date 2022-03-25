from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


#esse arquivo lida com as tabelas no Banco de Dados

#tabela de funcionarios, password ja é encriptado ao ser armazenado
class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable= False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    manager = Column(Boolean,default=False, nullable=False)



#tabela de ordem distribuida associado o id e um funcionario com o id de uma ordem que ele deva tratar
class OrdemDistribuida(Base):
        __tablename__ = "ordemdistribuida"        
        id_employee = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"), primary_key=True)
        id_ordem_servico = Column(Integer, primary_key=True, nullable=False)
        id_poster = Column(Integer,ForeignKey("employee.id", ondelete="CASCADE") ,nullable=False)
        completed = Column(Boolean,default=False, nullable=False)
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))








