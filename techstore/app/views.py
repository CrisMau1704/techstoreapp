
from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fieldwidgets import Select2Widget
from wtforms import SelectField
from sqlalchemy import func, extract
from datetime import datetime

from .models import Paciente, Doctor, Tratamiento, Cita, Pago, EstadoCita
from . import appbuilder, db


# =========================
# PACIENTES
# =========================

class PacienteModelView(ModelView):

    datamodel = SQLAInterface(Paciente)

    list_columns = [
        "nombre_completo",
        "ci",
        "telefono",
        "edad",
        "direccion",
        "correo",
        "estado",
        "creado_en",
        "actualizado_en"
    ]

    add_columns = [
        "nombre_completo",
        "ci",
        "telefono",
        "edad",
        "direccion",
        "correo",
        "estado"
    ]

    edit_columns = add_columns

    show_columns = list_columns


# =========================
# DOCTORES
# =========================

class DoctorView(ModelView):

    datamodel = SQLAInterface(Doctor)

    list_columns = [
        "nombre_completo",
        "especialidad",
        "telefono",
        "correo",
        "estado"
    ]

    add_columns = list_columns

    edit_columns = list_columns

    show_columns = list_columns


# =========================
# TRATAMIENTOS
# =========================

class TratamientoView(ModelView):

    datamodel = SQLAInterface(Tratamiento)

    list_columns = [
        "nombre",
        "descripcion",
        "precio",
        "duracion_minutos",
        "doctor",
        "estado"
    ]

    add_columns = list_columns

    edit_columns = list_columns

    show_columns = list_columns


# =========================
# CITAS
# =========================

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

    add_columns = [
        "paciente",
        "doctor",
        "tratamiento",
        "fecha",
        "hora",
        "observacion",
        "estado"
    ]

    edit_columns = add_columns


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
        "monto",
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

        if item.cita_id:

            cita = self.datamodel.session.query(Cita).filter(
                Cita.id == item.cita_id
            ).first()

            if cita and cita.tratamiento:
                item.monto = cita.tratamiento.precio

        elif item.cita:

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


# =========================
# GESTIÓN MÉDICA
# =========================

appbuilder.add_view(
    PacienteModelView,
    "Pacientes",
    icon="fa-users",
    category="Gestión Médica",
    category_icon="fa-hospital-o"
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
    icon="fa-stethoscope",
    category="Gestión Médica"
)

appbuilder.add_view(
    CitaView,
    "Citas",
    icon="fa-calendar-check-o",
    category="Gestión Médica"
)

# =========================
# ADMINISTRACIÓN
# =========================

appbuilder.add_view(
    PagoView,
    "Pagos",
    icon="fa-credit-card",
    category="Administración",
    category_icon="fa-money"
)

# =========================
# REPORTES
# =========================

appbuilder.add_view(
    DashboardView,
    "Reportes",
    icon="fa-bar-chart",
    category="Administración"
)



