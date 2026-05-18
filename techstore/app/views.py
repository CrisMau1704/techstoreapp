from flask_appbuilder import ModelView, BaseView, expose
from app.extensions import db
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Doctor, Tratamiento, Cita, Pago
from . import appbuilder
from flask_appbuilder.fieldwidgets import Select2Widget
from wtforms import SelectField
from sqlalchemy import func, extract
from datetime import datetime
from flask import request
from sqlalchemy import and_


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
# =========================
# CITAS - VERSIÓN CORREGIDAssss
# =========================

def obtener_horarios_disponibles():
    """
    Función que retorna los horarios disponibles
    """
    horarios_base = [
        ("08:00", "08:00 AM"),
        ("09:00", "09:00 AM"),
        ("10:00", "10:00 AM"),
        ("11:00", "11:00 AM"),
        ("12:00", "12:00 PM"),
        ("14:00", "02:00 PM"),
        ("15:00", "03:00 PM"),
        ("16:00", "04:00 PM"),
        ("17:00", "05:00 PM"),
    ]
    
    return horarios_base


class CitaView(ModelView):

    datamodel = SQLAInterface(Cita)

    list_columns = [
        "id",
        "paciente",
        "doctor",
        "tratamiento",
        "fecha",
        "hora",
        "estado"
    ]

    # ✅ INCLUIR "hora" en add_columns
    add_columns = [
        "paciente",
        "doctor",
        "tratamiento",
        "fecha",
        "hora",          # 👈 IMPORTANTE: hora debe estar aquí
        "observacion",
        "estado"
    ]

    edit_columns = add_columns

    # Personalizar el widget de hora
    add_form_extra_fields = {
        "hora": SelectField(
            "Horario",
            choices=obtener_horarios_disponibles(),
            widget=Select2Widget(),
            description="Seleccione un horario para la cita"
        )
    }

    def pre_add(self, item):
        """Validar que el horario no esté ocupado"""
        from sqlalchemy import and_
        
        if not item.hora:
            raise Exception("❌ Debe seleccionar un horario")
        
        # Verificar si ya existe una cita con el mismo doctor, fecha y hora
        cita_existente = self.datamodel.session.query(Cita).filter(
            and_(
                Cita.doctor_id == item.doctor_id,
                Cita.fecha == item.fecha,
                Cita.hora == item.hora,
                Cita.estado.in_(['Pendiente', 'Confirmada'])
            )
        ).first()
        
        if cita_existente:
            raise Exception(f"❌ El horario {item.hora} ya está OCUPADO para este doctor en la fecha {item.fecha}")
        
        # Verificar que el paciente no tenga otra cita el mismo día
        cita_paciente = self.datamodel.session.query(Cita).filter(
            and_(
                Cita.paciente_id == item.paciente_id,
                Cita.fecha == item.fecha
            )
        ).first()
        
        if cita_paciente:
            raise Exception("❌ El paciente ya tiene una cita programada para esta fecha")
        
        return item

    def pre_update(self, item):
        """Misma validación al editar"""
        return self.pre_add(item)


# =========================
# PAGOS
# =========================

class PagoView(ModelView):

    datamodel = SQLAInterface(Pago)

    list_columns = [
        "cita.paciente.nombre_completo",
        "monto",
        "metodo_pago",
        "estado"
    ]

    add_columns = [
        "cita",
        "metodo_pago",
        "observacion",
        "estado"
    ]

    edit_columns = add_columns

    add_form_extra_fields = {

        "metodo_pago": SelectField(
            "Método de Pago",
            choices=[
                ("Efectivo", "Efectivo"),
                ("Tarjeta", "Tarjeta"),
                ("Transferencia", "Transferencia")
            ],
            widget=Select2Widget()
        )
    }

    
    def pre_add(self, item):

        if not item.cita:
            raise Exception("Debe seleccionar una cita")

            # Verificar si la cita tiene tratamiento
        if not item.cita.tratamiento:
            raise Exception("La cita no tiene tratamiento asociado")

            # Asignar automáticamente el monto
        item.monto = item.cita.tratamiento.precio



    def post_add(self, item):

        if item.monto:
            self.datamodel.edit(item)


# =========================
# DASHBOARD / REPORTES
# =========================

class DashboardView(BaseView):

    route_base = "/dashboard"
    default_view = "index"

    @expose("/")
    def index(self):
        print("🚀 DASHBOARD VIEW ESTÁ FUNCIONANDO")
        from sqlalchemy import func, extract
        from datetime import datetime
        
        # =========================
        # CONTEOS PRINCIPALES
        # =========================
        total_pacientes = db.session.query(Paciente).filter(Paciente.estado == True).count()
        total_doctores = db.session.query(Doctor).filter(Doctor.estado == True).count()
        total_citas = db.session.query(Cita).count()
        total_pagos = db.session.query(Pago).filter(Pago.estado == True).count()

        # =========================
        # INGRESOS TOTALES
        # =========================
        total_ingresos = db.session.query(func.sum(Pago.monto)).filter(Pago.estado == True).scalar()
        if total_ingresos is None:
            total_ingresos = 0

        # =========================
        # CITAS POR DOCTOR (Para gráfica de barras)
        # =========================
        datos = db.session.query(
            Doctor.nombre_completo,
            func.count(Cita.id)
        ).join(Cita).group_by(Doctor.nombre_completo).all()

        doctores = [d[0] for d in datos]
        cantidades = [d[1] for d in datos]

        # =========================
        # PAGOS POR MÉTODO (Para gráfica de pastel)
        # =========================
        pagos_por_metodo = db.session.query(
            Pago.metodo_pago,
            func.sum(Pago.monto).label('total')
        ).filter(Pago.estado == True).group_by(Pago.metodo_pago).all()
        
        metodos_pago = [item[0] for item in pagos_por_metodo]
        montos_por_metodo = [float(item[1]) for item in pagos_por_metodo]

        # =========================
        # EVOLUCIÓN DE CITAS (Últimos 6 meses)
        # =========================
        meses = []
        citas_por_mes = []
        fecha_actual = datetime.now()
        
        for i in range(5, -1, -1):
            mes = fecha_actual.month - i
            año = fecha_actual.year
            if mes <= 0:
                mes += 12
                año -= 1
            
            nombre_mes = datetime(año, mes, 1).strftime('%B')
            meses.append(nombre_mes)
            
            count = db.session.query(Cita).filter(
                extract('month', Cita.fecha) == mes,
                extract('year', Cita.fecha) == año
            ).count()
            citas_por_mes.append(count)

        # =========================
        # TRATAMIENTOS MÁS SOLICITADOS
        # =========================
        tratamientos_populares = db.session.query(
            Tratamiento.nombre,
            func.count(Cita.id).label('total')
        ).join(Cita, Tratamiento.id == Cita.tratamiento_id).group_by(Tratamiento.id).order_by(func.count(Cita.id).desc()).limit(5).all()
        
        tratamientos_nombres = [item[0] for item in tratamientos_populares]
        tratamientos_cantidades = [item[1] for item in tratamientos_populares]

        # =========================
        # CITAS POR ESTADO
        # =========================
        citas_por_estado = db.session.query(
            Cita.estado,
            func.count(Cita.id).label('total')
        ).group_by(Cita.estado).all()
        
        estados_cita = [item[0] for item in citas_por_estado]
        cantidades_estado = [item[1] for item in citas_por_estado]

        # =========================
        # INGRESOS POR MES (Últimos 6 meses)
        # =========================
        ingresos_por_mes = []
        for i in range(5, -1, -1):
            mes = fecha_actual.month - i
            año = fecha_actual.year
            if mes <= 0:
                mes += 12
                año -= 1
            
            ingreso = db.session.query(func.sum(Pago.monto)).filter(
                extract('month', Pago.creado_en) == mes,
                extract('year', Pago.creado_en) == año,
                Pago.estado == True
            ).scalar() or 0
            ingresos_por_mes.append(float(ingreso))

        # =========================
        # PRÓXIMAS CITAS (Para tabla)
        # =========================
        proximas_citas = db.session.query(Cita).filter(
            Cita.fecha >= datetime.now().date()
        ).order_by(Cita.fecha.asc(), Cita.hora.asc()).limit(10).all()

        # =========================
        # KPIs ADICIONALES
        # =========================
        citas_completadas = db.session.query(Cita).filter(Cita.estado == 'Completada').count()
        tasa_ocupacion = (citas_completadas / total_citas * 100) if total_citas > 0 else 0
        promedio_por_cita = total_ingresos / total_citas if total_citas > 0 else 0
        citas_pendientes = db.session.query(Cita).filter(Cita.estado == 'Pendiente').count()
        tasa_exito = (citas_completadas / total_citas * 100) if total_citas > 0 else 0

        return self.render_template(
            "dashboard.html",
            # Conteos principales
            total_pacientes=total_pacientes,
            total_doctores=total_doctores,
            total_citas=total_citas,
            total_pagos=total_pagos,
            total_ingresos=total_ingresos,
            
            # Datos para gráficas
            doctores=doctores,
            cantidades=cantidades,
            metodos_pago=metodos_pago,
            montos_por_metodo=montos_por_metodo,
            meses=meses,
            citas_por_mes=citas_por_mes,
            tratamientos_nombres=tratamientos_nombres,
            tratamientos_cantidades=tratamientos_cantidades,
            estados_cita=estados_cita,
            cantidades_estado=cantidades_estado,
            ingresos_por_mes=ingresos_por_mes,
            
            # Próximas citas
            proximas_citas=proximas_citas,
            
            # KPIs
            tasa_ocupacion=round(tasa_ocupacion, 1),
            promedio_por_cita=round(promedio_por_cita, 2),
            citas_pendientes=citas_pendientes,
            tasa_exito=round(tasa_exito, 1)
        )


class ReporteView(BaseView):

    route_base = "/reportes"
    default_view = "index"

    @expose("/", methods=["GET", "POST"])
    def index(self):

        pagos = []
        total_ingresos = 0

        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")
        metodo_pago = request.form.get("metodo_pago")
        tratamiento_id = request.form.get("tratamiento_id")

        query = db.session.query(Pago).join(Cita).join(Tratamiento)

        # =========================
        # FILTRO POR FECHAS
        # =========================

        if fecha_inicio and fecha_fin:
            query = query.filter(
                Cita.fecha.between(fecha_inicio, fecha_fin)
            )

        # =========================
        # FILTRO POR MÉTODO DE PAGO
        # =========================

        if metodo_pago and metodo_pago != "":
            query = query.filter(
                Pago.metodo_pago == metodo_pago
            )

        # =========================
        # FILTRO POR TRATAMIENTO
        # =========================

        if tratamiento_id and tratamiento_id != "":
            query = query.filter(
                Tratamiento.id == tratamiento_id
            )

        pagos = query.all()

        # =========================
        # TOTAL INGRESOS
        # =========================

        total_ingresos = sum(pago.monto for pago in pagos)

        tratamientos = db.session.query(Tratamiento).all()

        return self.render_template(
            "reportes.html",
            pagos=pagos,
            total_ingresos=total_ingresos,
            tratamientos=tratamientos
        )

# =========================
# GESTIÓN MÉDICA
# =========================

appbuilder.add_view(
    DashboardView,
    "Dashboard",
    icon="fa-bar-chart",
    category="Dashboard"
)


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
    icon="fa-users",
    category="Gestión Médica",
    category_icon="fa-hospital-o"
)

from .models import Cita, Pago

class CitaView(ModelView):
    datamodel = SQLAInterface(Cita)
    list_columns = ["fecha", "hora", "paciente", "doctor", "tratamiento", "estado"]
    add_columns = ["fecha", "hora", "paciente", "doctor", "tratamiento", "observacion", "estado"]
    edit_columns = add_columns
    show_columns = ["fecha", "hora", "paciente", "doctor", "tratamiento", "observacion", "estado", "creado_en", "actualizado_en"]

  
class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    list_columns = ["monto", "metodo_pago", "cita", "estado"]
    add_columns = ["monto", "metodo_pago", "cita", "observacion", "estado"]
    edit_columns = add_columns
    show_columns = ["monto", "metodo_pago", "cita", "observacion", "estado", "creado_en", "actualizado_en"]


appbuilder.add_view(
    CitaView,
    "Citas",
    icon="fa-calendar",
    category="Gestión"
)

appbuilder.add_view(
    PagoView,
    "Pagos",
    icon="fa-money",
    # icon="fa-credit-card",
    category="Administración",
    category_icon="fa-money"
)

# =========================
# REPORTES
# =========================

appbuilder.add_view(
    ReporteView,
    "Reportes",
    icon="fa-file-text",
    category="Reportes",
    category_icon="fa-bar-chart"
)


from flask_appbuilder import BaseView, expose

class DashboardView(BaseView):
    route_base = "/dashboard"

    @expose("/")
    def index(self):
        return self.render_template("dashboard.html")

