from pickle import FALSE
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

#por boas praticas é melhor ter tabelas diferentes para tipos diferentes de funcionarios???? por enquanto sou vou de employee e manager
class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable= False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    manager = Column(Boolean,default=FALSE, nullable=False)



#deve existir uma maneira melhor de fazer isso aqui talvez separar funcionario e gerente
class OrdemDistribuida(Base):
        __tablename__ = "ordemdistribuida"        
        id_employee = Column(Integer, ForeignKey("employee.id", ondelete="RESTRICT"), primary_key=True)
        id_ordem_servico = Column(Integer, primary_key=True, nullable=False)
        id_poster = Column(Integer, nullable=False)
        completed = Column(Boolean,default=FALSE, nullable=False)
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))







