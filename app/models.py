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
    manager = Column(Boolean,default=False, nullable=False)



#quaro ver se eu guardo id cliente e id login pq se nao vao ser 3 consultas no front end quero ve se reduso a sempre 1
#talvez criar um endpoint que so faz isso de pegar um id ordem de servico e ir buscar o resto....
class OrdemDistribuida(Base):
        __tablename__ = "ordemdistribuida"        
        id_employee = Column(Integer, ForeignKey("employee.id", ondelete="RESTRICT"), primary_key=True)
        id_ordem_servico = Column(Integer, primary_key=True, nullable=False)
        id_poster = Column(Integer,ForeignKey("employee.id", ondelete="RESTRICT") ,nullable=False)
        completed = Column(Boolean,default=False, nullable=False)
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))








