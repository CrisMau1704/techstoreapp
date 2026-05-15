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
    list_columns = ["nombre", "descripcion", "precio", "duracion_minutos", "estado"]
    add_columns = list_columns
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
