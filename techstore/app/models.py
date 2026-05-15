from flask_appbuilder import Model
from flask_appbuilder.models.mixins import ImageColumn
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class Doctor(Model):
    __tablename__ = "doctor"  # 🔹 Nombre de la tabla en la BD

    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(150), nullable=False)
    especialidad = Column(String(100), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    imagen = Column(ImageColumn(size=(300, 300, True)))
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.now)
    actualizado_en = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return self.nombre_completo


from sqlalchemy import Float, Text

class Tratamiento(Model):
    __tablename__ = "tratamiento"  # 🔹 Nombre de la tabla en la BD

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio = Column(Float)
    duracion_minutos = Column(Integer)
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.now)
    actualizado_en = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return self.nombre
