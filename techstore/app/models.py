from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
class Usuario(Model):
    __tablename__= "usuario"

    id = Column(Integer, primary_key=true)
    username = Column(String(150), nullable=False)
    password = Column(String(150), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(String(150))
    estado = Column(Boolean, default=True)

    def __repr__(self):
        return self.username

class Paciente(Model):
    __tablename__= "paciente"

    id = Column(Integer, primary_key=true)
    nombre_completo = Column(String(150), nullable=False)
    ci = Column(String(20), nullable=False)
    telefono = Column(String(20), nullable=False)
    edad = Column(Integer, nullable=False)
    direccion = Column(String(255), nullable=False)
    correo = Column(String(150), nullable=False)
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.now)
    actualizado_en = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return self.nombre_completo