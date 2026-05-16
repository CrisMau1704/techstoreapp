import datetime
import pytz
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import ImageColumn
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from markupsafe import Markup
from flask import url_for

def get_bolivia_time():
    bolivia_tz = pytz.timezone('America/La_Paz')
    return datetime.datetime.now(bolivia_tz)

class Paciente(Model):
    __tablename__ = "paciente"
    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(150), nullable=False)
    ci = Column(String(20), nullable=False)
    telefono = Column(String(20), nullable=False)
    edad = Column(Integer, nullable=False)
    direccion = Column(String(255), nullable=False)
    correo = Column(String(150), nullable=False)
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)

    def __repr__(self):
        return self.nombre_completo

class Doctor(Model):
    __tablename__ = "doctor"  # 🔹 Nombre de la tabla en la BD
    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(150), nullable=False)
    especialidad = Column(String(100), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    imagen = Column(ImageColumn(size=(300, 300, True)))
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)

    def __repr__(self):
        return self.nombre_completo


# from sqlalchemy import Float, Text

class Tratamiento(Model):
    __tablename__ = "tratamiento"  # 🔹 Nombre de la tabla en la BD

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio = Column(Float)
    duracion_minutos = Column(Integer)
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)

    # 🔹 Relación con Doctor
    doctor_id = Column(Integer, ForeignKey("doctor.id"), nullable=False)
    doctor = relationship("Doctor")

    def __repr__(self):
        return self.nombre



