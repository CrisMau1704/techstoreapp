from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Paciente, Doctor, Tratamiento, Cita, Pago, EstadoCita
from . import appbuilder
from flask_appbuilder.fieldwidgets import Select2Widget
from wtforms import SelectField
from flask_appbuilder.actions import action
from flask import flash, redirect, url_for
from sqlalchemy import and_

from wtforms import SelectField
from flask_appbuilder.fieldwidgets import Select2Widget


class PacienteModelView(ModelView):
    datamodel = SQLAInterface(Paciente)
    list_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado", "creado_en", "actualizado_en"]
    add_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado"]
    edit_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado"]
    show_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado", "creado_en", "actualizado_en"]

class DoctorView(ModelView):
    datamodel = SQLAInterface(Doctor)
    list_columns = ["nombre_completo", "especialidad", "telefono", "correo", "estado"]
    add_columns = ["nombre_completo", "especialidad", "telefono", "correo", "estado"]
    edit_columns = add_columns
    show_columns = add_columns


class TratamientoView(ModelView):
    datamodel = SQLAInterface(Tratamiento)
    list_columns = ["nombre", "descripcion", "precio", "duracion_minutos", "doctor", "estado"]
    add_columns = ["nombre", "descripcion", "precio", "duracion_minutos", "doctor", "estado"]
    edit_columns = list_columns
    show_columns = list_columns


class CitaView(ModelView):
    datamodel = SQLAInterface(Cita)
    list_columns = ["id", "paciente", "doctor", "tratamiento", "fecha", "hora", "estado"]
    add_columns = ["paciente", "doctor", "tratamiento", "fecha", "hora", "observacion", "estado"]
    edit_columns = add_columns

class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    
    list_columns = ["cita.paciente.nombre_completo", "monto", "metodo_pago", "estado"]
    add_columns = ["cita", "monto", "metodo_pago", "observacion", "estado"]
    edit_columns = add_columns
    
    add_form_extra_fields = {
        "metodo_pago": SelectField(
            "Método de Pago",
            choices=[("Efectivo", "Efectivo"), ("Tarjeta", "Tarjeta"), ("Transferencia", "Transferencia")],
            widget=Select2Widget()
        )
    }
    
    def pre_add(self, item):
        # Forzar la carga de la relación
        if item.cita_id:
            cita = self.datamodel.session.query(Cita).filter(Cita.id == item.cita_id).first()
            if cita and cita.tratamiento:
                item.monto = cita.tratamiento.precio
        elif item.cita:
            item.monto = item.cita.tratamiento.precio
    
    def post_add(self, item):
        # Guardar nuevamente para asegurar el monto
        if item.monto:
            self.datamodel.edit(item)


appbuilder.add_view(
    PacienteModelView,
    "Pacientes",
    icon="fa-users",  # 👈 Cambié a "fa-users" que es más representativo (grupo de personas)
    category="Configuraciones",
    category_icon="fa-cogs"  # Engranaje para la categoría
)    

# Categoría: GESTIÓN MÉDICA
appbuilder.add_view(
    DoctorView,
    "Doctores",
    icon="fa-user-md",  # Doctor con estetoscopio
    category="Gestión Médica"
)

appbuilder.add_view(
    TratamientoView,
    "Tratamientos",
    icon="fa-medkit",  # Maletín médico
    category="Gestión Médica"
)

appbuilder.add_view(
    CitaView,
    "Citas",
    icon="fa-calendar",  # Calendario
    category="Gestión Médica"
)

appbuilder.add_view(
    PagoView,
    "Pagos",
    icon="fa-money",  # Dinero / factura
    category="Gestión Médica"
)






