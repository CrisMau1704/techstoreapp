import datetime
import pytz
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import ImageColumn
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from markupsafe import Markup
from flask import url_for
from sqlalchemy import Time, Date, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
import enum


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
    precio = Column(Float, default=0.0)
    duracion_minutos = Column(Integer)
    estado = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)

    # 🔹 Relación con Doctor
    doctor_id = Column(Integer, ForeignKey("doctor.id"), nullable=False)
    doctor = relationship("Doctor")

    def __repr__(self):
        return self.nombre


class EstadoCita(enum.Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    NO_ASISTIO = "No Asistió"

class Cita(Model):
    __tablename__ = "cita"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    hora = Column(String(10), nullable=False)  # String: "14:30"
    observacion = Column(Text, nullable=True)
    estado = Column(String(50), default="Pendiente", nullable=False)  # Pendiente, Confirmada, Completada, Cancelada
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)
    paciente_id = Column(Integer, ForeignKey("paciente.id"), nullable=False)
    paciente = relationship("Paciente", backref="citas")
    doctor_id = Column(Integer, ForeignKey("doctor.id"), nullable=False)
    doctor = relationship("Doctor", backref="citas")
    tratamiento_id = Column(Integer, ForeignKey("tratamiento.id"), nullable=False)
    tratamiento = relationship("Tratamiento", backref="citas")
    
    __table_args__ = (
        UniqueConstraint('doctor_id', 'fecha', 'hora', name='uq_doctor_fecha_hora'),
    )
    
    def __repr__(self):
        return f"{self.paciente.nombre_completo} - {self.fecha} {self.hora}"


class Pago(Model):
    __tablename__ = "pago"
    
    id = Column(Integer, primary_key=True)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50), nullable=False)  # Efectivo, Tarjeta, Transferencia
    observacion = Column(Text, nullable=True)
    estado = Column(Boolean, default=True)  # True = Pagado, False = Anulado
    creado_en = Column(DateTime, default=get_bolivia_time, nullable=False)
    actualizado_en = Column(DateTime, default=get_bolivia_time, onupdate=get_bolivia_time, nullable=False)
    
    cita_id = Column(Integer, ForeignKey("cita.id"), nullable=False, unique=True)
    cita = relationship("Cita", backref="pago", uselist=False)
    
    def __repr__(self):
        return f"Pago {self.id} - {self.monto} Bs."
    
# views.py - Actualiza tu DashboardView


