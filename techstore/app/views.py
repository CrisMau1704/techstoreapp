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



