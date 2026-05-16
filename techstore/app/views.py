from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Doctor, Tratamiento
from . import appbuilder


class DoctorView(ModelView):
    datamodel = SQLAInterface(Doctor)
    list_columns = ["nombre_completo", "especialidad", "telefono", "correo", "estado"]
    add_columns = ["nombre_completo", "especialidad", "telefono", "correo", "imagen", "estado"]
    edit_columns = add_columns
    show_columns = add_columns


class TratamientoView(ModelView):
    datamodel = SQLAInterface(Tratamiento)
    list_columns = ["nombre", "descripcion", "precio", "duracion_minutos", "doctor", "estado"]
    add_columns = ["nombre", "descripcion", "precio", "duracion_minutos", "doctor", "estado"]
    edit_columns = list_columns
    show_columns = list_columns


# Registrar las vistas en el menú
appbuilder.add_view(
    DoctorView,
    "Doctores",
    icon="fa-user-md",
    category="Gestión Médica"
)

appbuilder.add_view(
    TratamientoView,
    "Tratamientos",
    icon="fa-medkit",
    category="Gestión Médica"
)
import os
from flask import url_for
from markupsafe import Markup
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.filemanager import ImageManager

from .models import Paciente
from . import appbuilder

class PacienteModelView(ModelView):
    datamodel = SQLAInterface(Paciente)
    list_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado", "creado_en", "actualizado_en"]
    add_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado"]
    edit_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado"]
    show_columns = ["nombre_completo", "ci", "telefono", "edad", "direccion", "correo", "estado", "creado_en", "actualizado_en"]

appbuilder.add_view(
    PacienteModelView,
    "Pacientes",
    icon="wheelchair-alt",
    category="Configuraciones",
    category_icon="fa-cogs"
)    



