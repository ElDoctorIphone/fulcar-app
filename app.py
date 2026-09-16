import calendar
import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de la página en modo ancho (wide)
st.set_page_config(
    page_title="FULCAR AUTO IMPORT SRL", page_icon="🚗", layout="wide"
)

# --- CLAVE SECRETA DE ACCESO ---
CLAVE_SECRETA = "Fulcar0131"  # Puedes cambiar esta clave cuando quieras

# Inicializar el estado de autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            ruta_logo = (
                r"C:\Users\FRANK VENTURA\OneDrive\Desktop\Base de datos fulcar autos\fulcar_logo.png"
            )
            if os.path.exists(ruta_logo):
                st.image(ruta_logo, width=250)
            else:
                st.image("fulcar_logo.png", width=250)
        except:
            st.markdown("## 🏎️ **FULCAR AUTO IMPORT SRL**")

        st.subheader("Acceso Restringido al Sistema")
        
        with st.form("form_login"):
            password_ingresada = st.text_input(
                "Ingresa la Clave de Seguridad", type="password"
            )
            btn_login = st.form_submit_button("Entrar al Sistema")

            if btn_login:
                if password_ingresada == CLAVE_SECRETA:
                    st.session_state.autenticado = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
        
        st.stop()  # Detiene la ejecución aquí hasta que coloquen la clave correcta

# ==========================================
# CÓDIGO PRINCIPAL DEL SISTEMA (Solo entra si está autenticado)
# ==========================================

# --- CREAR CARPETA LOCAL DE RESPALDO DE FOTOS ---
CARPETA_FOTOS = "uploads_vehiculos"
if not os.path.exists(CARPETA_FOTOS):
    os.makedirs(CARPETA_FOTOS)

# --- ESTILOS CSS PARA ADAPTABILIDAD MÓVIL (IPHONE) Y TAMAÑO AMPLIADO ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 16px;
    }
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column !important;
        }
        .stMetric {
            margin-bottom: 15px;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
    }
    .fulcar-texto-linea {
        font-family: inherit; 
        font-size: 1.05rem; 
        color: inherit; 
        margin-bottom: 10px;
        font-weight: 400;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicialización de bases de datos en session_state
if "propio" not in st.session_state:
    st.session_state.propio = []
if "colegas" not in st.session_state:
    st.session_state.colegas = []
if "cuentas" not in st.session_state:
    st.session_state.cuentas = []
if "gastos_dealer" not in st.session_state:
    st.session_state.gastos_dealer = []
if "traspasos" not in st.session_state:
    st.session_state.traspasos = []

# Meses y días en español
MESES_ES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}
DIAS_ES = {
    0: "lunes",
    1: "martes",
    2: "miércoles",
    3: "jueves",
    4: "viernes",
    5: "sábado",
    6: "domingo",
}


def fecha_formato_rd(fecha_obj):
    if not fecha_obj:
        return ""
    if isinstance(fecha_obj, str):
        try:
            fecha_obj = datetime.date.fromisoformat(fecha_obj)
        except:
            return fecha_obj
    dia_sem = DIAS_ES[fecha_obj.weekday()]
    mes_nom = MESES_ES[fecha_obj.month]
    return f"{dia_sem}, {fecha_obj.day} de {mes_nom} de {fecha_obj.year}"


def validar_y_parsear_monto(texto):
    """Valida obligatoriamente que el texto contenga comas y lo convierte a número."""
    if not texto:
        return 0.0, "El campo de monto está vacío."

    texto_limpio = str(texto).strip()

    sin_comas_ni_moneda = (
        texto_limpio.replace("RD$", "").replace("$", "").replace(",", "").strip()
    )
    try:
        val_num = float(sin_comas_ni_moneda)
    except:
        return 0.0, "El valor ingresado no es un número válido."

    if val_num >= 1000 and "," not in texto_limpio:
        return (
            0.0,
            f"❌ Formato incorrecto. Debe incluir las comas de miles (Ej: 250,000 en lugar de 250000).",
        )

    return val_num, None


# --- ENCABEZADO Y LOGO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        ruta_logo = (
            r"C:\Users\FRANK VENTURA\OneDrive\Desktop\Base de datos fulcar autos\fulcar_logo.png"
        )
        if os.path.exists(ruta_logo):
            st.image(ruta_logo, width=200)
        else:
            st.image("fulcar_logo.png", width=200)
    except:
        st.markdown("### 🏎️ **FULCAR AUTO IMPORT**")

with col_titulo:
    st.title("Sistema de Control Operativo y Financiero")
    hoy_str = fecha_formato_rd(datetime.date.today())
    st.caption(f"Fecha actual: {hoy_str.capitalize()}")

st.markdown("---")

opciones_menu = [
    "📊 Historial y Ganancias por Mes",
    "🚗 Mi Inventario Propio",
    "🤝 Vehículos de Colegas",
    "💰 Cuentas por Cobrar",
    "🏢 Gastos Operativos del Dealer",
    "📋 Traspasos Pendientes",
]

pestana = st.radio(
    "Navegación del Sistema",
    opciones_menu,
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")

# ==========================================
# 1. HISTORIAL Y GANANCIAS POR MES
# ==========================================
if pestana == "📊 Historial y Ganancias por Mes":
    st.subheader("Panel Financiero y Rendimiento Mensual (DOP)")

    meses_disponibles = set()
    mes_actual_str = datetime.date.today().strftime("%Y-%m")
    meses_disponibles.add(mes_actual_str)

    for v in st.session_state.propio:
        if v.get("mes_venta"):
            meses_disponibles.add(v["mes_venta"])
    for g in st.session_state.gastos_dealer:
        if g.get("mes"):
            meses_disponibles.add(g["mes"])

    meses_lista = sorted(list(meses_disponibles), reverse=True)


    def formatear_mes_opcion(m_str):
        a, m = m_str.split("-")
        return f"{MESES_ES[int(m)].capitalize()} {a}"


    col_m1, col_m2 = st.columns([2, 2])
    with col_m1:
        mes_seleccionado = st.selectbox(
            "Seleccionar Mes a Consultar",
            meses_lista,
            format_func=formatear_mes_opcion,
        )

    anio_sel, mes_sel = map(int, mes_seleccionado.split("-"))
    dias_en_mes = calendar.monthrange(anio_sel, mes_sel)[1]

    with col_m2:
        st.info(
            f"📅 El mes seleccionado tiene **{dias_en_mes} días** en total."
        )

    ganancia_mes = 0
    valor_ventas_mes = 0
    vendidos_mes_count = 0
    vehiculos_vendidos_detalles = []

    for v in st.session_state.propio:
        if v["estado"] == "Vendido" and v.get("mes_venta") == mes_seleccionado:
            vendidos_mes_count += 1
            ganancia_mes += v["ganancia_neta"]
            valor_ventas_mes += v["precio_venta"]

            total_g_vehiculo = sum(g["monto"] for g in v.get("lista_gastos", []))
            costo_total = v["costo"] + total_g_vehiculo

            vehiculos_vendidos_detalles.append(
                {
                    "Vehículo": v["nombre"],
                    "Fecha Venta": fecha_formato_rd(v["fecha_venta"]),
                    "Inversión Total": f"RD$ {costo_total:,.2f}",
                    "Precio Venta": f"RD$ {v['precio_venta']:,.2f}",
                    "Ganancia Neta (Total)": f"RD$ {v['ganancia_neta']:,.2f}",
                    "Retorno Inversión Oscar": f"RD$ {v['retorno_oscar']:,.2f}",
                    "Retorno Inversión Doctor": f"RD$ {v['retorno_doctor']:,.2f}",
                    "Ganancia Oscar": f"RD$ {v['ganancia_oscar']:,.2f}",
                    "Ganancia Doctor": f"RD$ {v['ganancia_doctor']:,.2f}",
                }
            )

    gastos_dealer_mes = sum(
        g["monto"]
        for g in st.session_state.gastos_dealer
        if g.get("mes") == mes_seleccionado
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ganancia Neta del Mes", f"RD$ {ganancia_mes:,.2f}")
    kpi2.metric("Vehículos Vendidos", vendidos_mes_count)
    kpi3.metric("Valor Total Ventas", f"RD$ {valor_ventas_mes:,.2f}")
    kpi4.metric("Gastos Dealer (Mes)", f"RD$ {gastos_dealer_mes:,.2f}")

    st.markdown("### Detalle de Vehículos Vendidos en el Periodo")
    if vehiculos_vendidos_detalles:
        st.dataframe(
            pd.DataFrame(vehiculos_vendidos_detalles), use_container_width=True
        )
    else:
        st.info("No hay vehículos vendidos registrados en este mes.")

# ==========================================
# 2. MI INVENTARIO PROPIO
# ==========================================
elif pestana == "🚗 Mi Inventario Propio":
    st.subheader("Gestión de Mi Inventario (Vehículos Propios)")

    st.markdown("**Registrar Nuevo Vehículo (Compra)**")

    nombre_inv = st.text_input(
        "Marca, Modelo, Año",
        placeholder="Ej: Toyota RAV4 XLE 2025",
        key="input_nombre_nuevo",
    )
    costo_str = st.text_input(
        "Costo de Compra (RD$)",
        placeholder="Ej: 500,000",
        key="input_costo_nuevo",
    )

    c_est, c_pag = st.columns(2)
    with c_est:
        estado_inv = st.selectbox(
            "Estado Inicial",
            ["Disponible", "En Taller / Reparación", "Vendido"],
            key="select_estado_nuevo",
        )
    with c_pag:
        pagado_por_compra = st.selectbox(
            "Compra Pagada por:",
            ["Oscar", "El Doctor", "Ambos (Compartido)"],
            key="select_pagado_nuevo_2",
        )

    mo_str = ""
    md_str = ""
    if pagado_por_compra == "Ambos (Compartido)":
        st.markdown(
            "<small style='color: #2563eb;'><b>Especificar aportes de la compra:</b></small>",
            unsafe_allow_html=True,
        )
        col_apo1, col_apo2 = st.columns(2)
        with col_apo1:
            mo_str = st.text_input(
                "Parte que puso Oscar (RD$)",
                placeholder="Ej: 250,000",
                key="mo_nuevo_str",
            )
        with col_apo2:
            md_str = st.text_input(
                "Parte que puso El Doctor (RD$)",
                placeholder="Ej: 250,000",
                key="md_nuevo_str",
            )

    fotos_subidas = st.file_uploader(
        "Fotografías del Vehículo (Opcional - Puedes agregarlas después)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="fotos_nuevo_vehiculo",
    )

    if st.button("Guardar en Inventario", key="btn_guardar_vehiculo_new"):
        mo_compra = 0.0
        md_compra = 0.0
        costo_inv, err_costo = validar_y_parsear_monto(costo_str)

        err_mo, err_md = None, None
        if pagado_por_compra == "Ambos (Compartido)":
            mo_compra, err_mo = validar_y_parsear_monto(mo_str)
            md_compra, err_md = validar_y_parsear_monto(md_str)
        elif pagado_por_compra == "Oscar":
            mo_compra = costo_inv
        else:
            md_compra = costo_inv

        if not nombre_inv:
            st.error("Por favor ingresa el nombre del vehículo.")
        elif costo_str and err_costo:
            st.error(err_costo)
        elif costo_inv <= 0:
            st.error("Por favor ingresa un costo de compra válido.")
        elif pagado_por_compra == "Ambos (Compartido)":
            if err_mo:
                st.error(f"Error en monto de Oscar: {err_mo}")
            elif err_md:
                st.error(f"Error en monto de Doctor: {err_md}")
            elif (mo_compra + md_compra) != costo_inv:
                st.error(
                    f"❌ La suma de aportes no concuerda con el costo total."
                )
            else:
                rutas_fotos = []
                if fotos_subidas:
                    for f_item in fotos_subidas:
                        timestamp = datetime.datetime.now().strftime(
                            "%Y%m%d_%H%M%S_%f"
                        )
                        nombre_archivo = f"{timestamp}_{f_item.name}"
                        ruta_completa = os.path.join(
                            CARPETA_FOTOS, nombre_archivo
                        )
                        with open(ruta_completa, "wb") as f:
                            f.write(f_item.getbuffer())
                        rutas_fotos.append(ruta_completa)

                nuevo_vehiculo = {
                    "id": len(st.session_state.propio) + 1,
                    "nombre": nombre_inv,
                    "costo": costo_inv,
                    "pagado_por_compra": pagado_por_compra,
                    "monto_oscar_compra": mo_compra,
                    "monto_doctor_compra": md_compra,
                    "estado": estado_inv,
                    "fotos": rutas_fotos,
                    "lista_gastos": [],
                    "precio_venta": None,
                    "ganancia_neta": None,
                    "retorno_oscar": 0.0,
                    "retorno_doctor": 0.0,
                    "ganancia_oscar": 0.0,
                    "ganancia_doctor": 0.0,
                    "fecha_venta": None,
                    "mes_venta": None,
                }
                st.session_state.propio.append(nuevo_vehiculo)
                
                for k in ["input_nombre_nuevo", "input_costo_nuevo", "mo_nuevo_str", "md_nuevo_str"]:
                    if k in st.session_state:
                        del st.session_state[k]

                st.success(f"Vehículo {nombre_inv} agregado exitosamente.")
                st.rerun()
        else:
            rutas_fotos = []
            if fotos_subidas:
                for f_item in fotos_subidas:
                    timestamp = datetime.datetime.now().strftime(
                        "%Y%m%d_%H%M%S_%f"
                    )
                    nombre_archivo = f"{timestamp}_{f_item.name}"
                    ruta_completa = os.path.join(CARPETA_FOTOS, nombre_archivo)
                    with open(ruta_completa, "wb") as f:
                        f.write(f_item.getbuffer())
                    rutas_fotos.append(ruta_completa)

            nuevo_vehiculo = {
                "id": len(st.session_state.propio) + 1,
                "nombre": nombre_inv,
                "costo": costo_inv,
                "pagado_por_compra": pagado_por_compra,
                "monto_oscar_compra": mo_compra,
                "monto_doctor_compra": md_compra,
                "estado": estado_inv,
                "fotos": rutas_fotos,
                "lista_gastos": [],
                "precio_venta": None,
                "ganancia_neta": None,
                "retorno_oscar": 0.0,
                "retorno_doctor": 0.0,
                "ganancia_oscar": 0.0,
                "ganancia_doctor": 0.0,
                "fecha_venta": None,
                "mes_venta": None,
            }
            st.session_state.propio.append(nuevo_vehiculo)
            
            for k in ["input_nombre_nuevo", "input_costo_nuevo"]:
                if k in st.session_state:
                    del st.session_state[k]

            st.success(f"Vehículo {nombre_inv} agregado exitosamente.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Inventario Actual, Gastos y Edición")

    if st.session_state.propio:
        for i, v in enumerate(st.session_state.propio):
            total_g_vehiculo = sum(g["monto"] for g in v.get("lista_gastos", []))
            inversion_actual = v["costo"] + total_g_vehiculo

            with st.expander(
                f"🚗 {v['nombre']} — Estado: **{v['estado']}** | Inversión Total: RD$ {inversion_actual:,.2f}"
            ):
                st.markdown(f"**Vehículo:** {v['nombre']}")
                st.markdown(f"**Costo de Compra Fijo:** RD$ {v['costo']:,.2f}")
                st.markdown(f"**Gastos del Vehículo:** RD$ {total_g_vehiculo:,.2f}")

                if v["estado"] == "Vendido" and v["precio_venta"]:
                    st.markdown(
                        f"**Monto de la Venta:** RD$ {v['precio_venta']:,.2f}"
                    )
                    st.markdown(
                        f"**Ganancia Neta Total:** RD$ {v['ganancia_neta']:,.2f}"
                    )

                st.markdown("---")
                nuevo_estado = st.selectbox(
                    "Estado Actual",
                    ["Disponible", "En Taller / Reparación", "Vendido"],
                    index=["Disponible", "En Taller / Reparación", "Vendido"].index(
                        v["estado"]
                    )
                    if v["estado"]
                    in ["Disponible", "En Taller / Reparación", "Vendido"]
                    else 0,
                    key=f"est_{i}",
                )

                precio_v_str = "0"
                fecha_v = datetime.date.today()

                if nuevo_estado == "Vendido":
                    precio_v_str = st.text_input(
                        "Monto de la Venta (RD$)",
                        value=f"{v['precio_venta'] or 0:,.0f}",
                        key=f"pv_str_{i}",
                    )
                    fecha_v = st.date_input(
                        "Fecha de Venta",
                        value=(
                            datetime.date.fromisoformat(v["fecha_venta"])
                            if v["fecha_venta"]
                            else datetime.date.today()
                        ),
                        key=f"fv_{i}",
                    )

                if st.button("Guardar Estado / Venta", key=f"btn_act_{i}"):
                    v["estado"] = nuevo_estado

                    if nuevo_estado == "Vendido":
                        pv_val, err_pv = validar_y_parsear_monto(precio_v_str)
                        if err_pv:
                            st.error(f"Error en monto de venta: {err_pv}")
                        else:
                            v["precio_venta"] = pv_val
                            v["fecha_venta"] = str(fecha_v)
                            v["mes_venta"] = str(fecha_v)[:7]

                            total_g = sum(
                                gg["monto"] for gg in v.get("lista_gastos", [])
                            )
                            inversion_total_calc = v["costo"] + total_g
                            ganancia_calc = v["precio_venta"] - inversion_total_calc

                            total_oscar_inv = v["monto_oscar_compra"] + sum(
                                gg["monto_oscar"]
                                for gg in v.get("lista_gastos", [])
                            )
                            total_doctor_inv = v["monto_doctor_compra"] + sum(
                                gg["monto_doctor"]
                                for gg in v.get("lista_gastos", [])
                            )

                            v["ganancia_neta"] = ganancia_calc
                            v["retorno_oscar"] = total_oscar_inv
                            v["retorno_doctor"] = total_doctor_inv
                            v["ganancia_oscar"] = ganancia_calc / 2.0
                            v["ganancia_doctor"] = ganancia_calc / 2.0
                            st.success("¡Venta registrada con éxito!")
                            st.rerun()
                    else:
                        v["precio_venta"] = None
                        v["ganancia_neta"] = None
                        v["retorno_oscar"] = 0.0
                        v["retorno_doctor"] = 0.0
                        v["ganancia_oscar"] = 0.0
                        v["ganancia_doctor"] = 0.0
                        v["fecha_venta"] = None
                        v["mes_venta"] = None
                        st.success("¡Estado actualizado!")
                        st.rerun()

                if v["estado"] == "Vendido" and v["ganancia_neta"] is not None:
                    st.markdown("---")
                    st.markdown("#### 💰 Reporte de Liquidación de Venta")
                    st.info(
                        f"• **Ganancia Neta Total:** RD$ {v['ganancia_neta']:,.2f}\n\n"
                        f"• **A Oscar hay que entregarle:** RD$ {(v['retorno_oscar'] + v['ganancia_oscar']):,.2f} "
                        f"(Inversión: RD$ {v['retorno_oscar']:,.2f} + Ganancia: RD$ {v['ganancia_oscar']:,.2f})\n\n"
                        f"• **Al Doctor hay que entregarle:** RD$ {(v['retorno_doctor'] + v['ganancia_doctor']):,.2f} "
                        f"(Inversión: RD$ {v['retorno_doctor']:,.2f} + Ganancia: RD$ {v['ganancia_doctor']:,.2f})"
                    )

                st.markdown("---")
                st.markdown(
                    "##### 🛠️ Historial de Inversión y Gastos de este Vehículo"
                )

                if v["pagado_por_compra"] == "Ambos (Compartido)":
                    detalle_compra = f"(Pagado por: Oscar RD$ {v['monto_oscar_compra']:,.2f} / Doctor RD$ {v['monto_doctor_compra']:,.2f})"
                else:
                    detalle_compra = f"(Pagado por: {v['pagado_por_compra']})"

                st.markdown(
                    f'<div class="fulcar-texto-linea">🟢 <b>Compra:</b> — RD$ {v["costo"]:,.2f} {detalle_compra}</div>',
                    unsafe_allow_html=True,
                )

                if v.get("lista_gastos"):
                    for idx_g, mg in enumerate(v["lista_gastos"]):
                        col_mg1, col_mg2 = st.columns([5, 1])
                        with col_mg1:
                            if mg["pagado_por"] == "Ambos (Compartido)":
                                det_g = f"(Pagado por: Oscar RD$ {mg['monto_oscar']:,.2f} / Doctor RD$ {mg['monto_doctor']:,.2f})"
                            else:
                                det_g = f"(Pagado por: {mg['pagado_por']})"
                            st.markdown(
                                f'<div class="fulcar-texto-linea">🔹 <b>Gasto ({mg["concepto"]}):</b> — RD$ {mg["monto"]:,.2f} {det_g}</div>',
                                unsafe_allow_html=True,
                            )
                        with col_mg2:
                            if st.button(
                                "Borrar", key=f"del_gv_{i}_{idx_g}"
                            ):
                                v["lista_gastos"].pop(idx_g)
                                if v["estado"] == "Vendido" and v["precio_venta"]:
                                    total_g = sum(
                                        gg["monto"] for gg in v["lista_gastos"]
                                    )
                                    inversion_total_calc = v["costo"] + total_g
                                    ganancia_calc = v["precio_venta"] - inversion_total_calc

                                    total_oscar_inv = v["monto_oscar_compra"] + sum(
                                        gg["monto_oscar"] for gg in v["lista_gastos"]
                                    )
                                    total_doctor_inv = v["monto_doctor_compra"] + sum(
                                        gg["monto_doctor"] for gg in v["lista_gastos"]
                                    )

                                    v["ganancia_neta"] = ganancia_calc
                                    v["retorno_oscar"] = total_oscar_inv
                                    v["retorno_doctor"] = total_doctor_inv
                                    v["ganancia_oscar"] = ganancia_calc / 2.0
                                    v["ganancia_doctor"] = ganancia_calc / 2.0
                                st.rerun()

                st.markdown("---")
                st.markdown("##### ➕ Agregar Nuevo Gasto a este Vehículo")

                with st.form(f"form_gasto_vehiculo_{i}"):
                    gc1, gc2 = st.columns(2)
                    with gc1:
                        g_concepto = st.text_input(
                            "Concepto del Gasto",
                            placeholder="Ej: Pintura o Gasto de Cierre",
                            key=f"gc_con_{i}",
                        )
                        g_monto_str = st.text_input(
                            "Monto (RD$)",
                            placeholder="Ej: 24,000",
                            key=f"gc_mon_str_{i}",
                        )
                    with gc2:
                        g_resp = st.selectbox(
                            "Pagado por:",
                            ["Oscar", "El Doctor", "Ambos (Compartido)"],
                            key=f"gc_resp_{i}",
                        )

                    g_mo = 0.0
                    g_md = 0.0
                    g_monto_val, err_gm = validar_y_parsear_monto(g_monto_str)

                    if g_resp == "Ambos (Compartido)":
                        st.markdown(
                            "<small style='color: #2563eb;'><b>Oscar arriba / El Doctor abajo:</b></small>",
                            unsafe_allow_html=True,
                        )
                        g_mo_str = st.text_input(
                            "Parte Oscar (RD$)",
                            placeholder="Ej: 12,000",
                            key=f"gc_mo_str_{i}",
                        )
                        g_md_str = st.text_input(
                            "Parte Doctor (RD$)",
                            placeholder="Ej: 12,000",
                            key=f"gc_md_str_{i}",
                        )
                        g_mo, err_gmo = validar_y_parsear_monto(g_mo_str)
                        g_md, err_gmd = validar_y_parsear_monto(g_md_str)
                    elif g_resp == "Oscar":
                        g_mo = g_monto_val
                        err_gmo, err_gmd = None, None
                    else:
                        g_md = g_monto_val
                        err_gmo, err_gmd = None, None

                    if st.form_submit_button(
                        "Registrar Gasto a este Vehículo"
                    ):
                        if not g_concepto:
                            st.error("Ingresa el concepto del gasto.")
                        elif err_gm:
                            st.error(f"Error en monto: {err_gm}")
                        elif g_resp == "Ambos (Compartido)" and (
                            err_gmo or err_gmd
                        ):
                            st.error("Error en formato de aportes de los socios.")
                        elif g_resp == "Ambos (Compartido)" and (
                            g_mo + g_md
                        ) != g_monto_val:
                            st.error(
                                f"❌ La suma de aportes no concuerda con el total del gasto."
                            )
                        else:
                            nuevo_gasto = {
                                "concepto": g_concepto,
                                "monto": g_monto_val,
                                "pagado_por": g_resp,
                                "monto_oscar": g_mo,
                                "monto_doctor": g_md,
                                "fecha": str(datetime.date.today()),
                            }
                            v["lista_gastos"].append(nuevo_gasto)

                            if v["estado"] == "Vendido" and v["precio_venta"]:
                                total_g = sum(
                                    gg["monto"] for gg in v["lista_gastos"]
                                )
                                inversion_total_calc = v["costo"] + total_g
                                ganancia_calc = v["precio_venta"] - inversion_total_calc

                                total_oscar_inv = v["monto_oscar_compra"] + sum(
                                    gg["monto_oscar"]
                                    for gg in v["lista_gastos"]
                                )
                                total_doctor_inv = v["monto_doctor_compra"] + sum(
                                    gg["monto_doctor"]
                                    for gg in v["lista_gastos"]
                                )

                                v["ganancia_neta"] = ganancia_calc
                                v["retorno_oscar"] = total_oscar_inv
                                v["retorno_doctor"] = total_doctor_inv
                                v["ganancia_oscar"] = ganancia_calc / 2.0
                                v["ganancia_doctor"] = ganancia_calc / 2.0

                            st.success("¡Gasto agregado al vehículo!")
                            st.rerun()

                # --- SECCIÓN GALERÍA Y ADICIÓN DE FOTOS ---
                st.markdown("---")
                st.markdown("### 📸 Galería")
                if v.get("fotos"):
                    cols_fotos = st.columns(3)
                    for f_idx, ruta_f in enumerate(v["fotos"]):
                        if os.path.exists(ruta_f):
                            with cols_fotos[f_idx % 3]:
                                st.image(ruta_f, use_container_width=True)
                                col_d_btn, col_del_btn = st.columns(2)
                                with col_d_btn:
                                    with open(ruta_f, "rb") as archivo_img:
                                        st.download_button(
                                            label=f"📥 #{f_idx+1}",
                                            data=archivo_img,
                                            file_name=os.path.basename(ruta_f),
                                            mime="image/jpeg",
                                            key=f"dl_f_{i}_{f_idx}",
                                        )
                                with col_del_btn:
                                    if st.button("🗑️", key=f"del_img_prop_{i}_{f_idx}", help="Borrar esta foto"):
                                        v["fotos"].pop(f_idx)
                                        st.rerun()
                else:
                    st.info("Este vehículo no tiene fotografías registradas.")

                nuevas_fotos_propio = st.file_uploader(
                    "Agregar más fotografías a este vehículo",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"add_fotos_prop_{i}"
                )
                if nuevas_fotos_propio:
                    if st.button("Subir fotos seleccionadas", key=f"btn_subir_prop_{i}"):
                        for f_item in nuevas_fotos_propio:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            nombre_archivo = f"{timestamp}_{f_item.name}"
                            ruta_completa = os.path.join(CARPETA_FOTOS, nombre_archivo)
                            with open(ruta_completa, "wb") as f:
                                f.write(f_item.getbuffer())
                            v["fotos"].append(ruta_completa)
                        st.success("¡Fotografías agregadas exitosamente!")
                        st.rerun()

                st.markdown("---")
                if st.button("🗑️ Eliminar Vehículo Completo", key=f"del_{i}"):
                    st.session_state.propio.pop(i)
                    st.rerun()

        st.markdown("---")
        vehiculos_activos = [
            v for v in st.session_state.propio if v["estado"] != "Vendido"
        ]
        total_vehiculos = len(vehiculos_activos)
        valor_total_inv = sum(
            v["costo"] + sum(g["monto"] for g in v.get("lista_gastos", []))
            for v in vehiculos_activos
        )

        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Cantidad de Vehículos en Inventario", total_vehiculos)
        c_m2.metric(
            "Valor Total del Inventario (Costo + Gastos)",
            f"RD$ {valor_total_inv:,.2f}",
        )
    else:
        st.info("No hay vehículos registrados en tu inventario.")

# ==========================================
# 3. VEHÍCULOS DE COLEGAS
# ==========================================
elif pestana == "🤝 Vehículos de Colegas":
    st.subheader("Inventario Externo (Vehículos de Colegas)")

    col_nombre = st.text_input("Vehículo", placeholder="Ej: Honda CR-V", key="col_n")
    col_dueno = st.text_input("Dueño / Colega", placeholder="Ej: Juan Pérez", key="col_d")
    
    col_moneda = st.radio(
        "Moneda del Precio de Acuerdo",
        ["Pesos (RD$)", "Dólares (USD)"],
        horizontal=True,
        key="col_moneda_radio"
    )

    col_precio_str = st.text_input(
        "Precio Acuerdo (" + ("RD$" if col_moneda == "Pesos (RD$)" else "USD$") + ")",
        placeholder="Ej: 1,200,000" if col_moneda == "Pesos (RD$)" else "Ej: 20,000",
        key="col_p"
    )

    tasa_str = ""
    if col_moneda == "Dólares (USD)":
        tasa_str = st.text_input(
            "Tasa del Dólar (Opcional)",
            placeholder="Ej: 60.00 (Si no la pones, se guarda solo el monto)",
            key="col_tasa"
        )

    col_estado = st.selectbox(
        "Estado", ["Disponible para Venta", "Vendido"], key="col_e"
    )
    fotos_colega = st.file_uploader(
        "Fotografías del Vehículo de Colega (Opcional)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="fotos_colega_nuevo",
    )

    if st.button("Registrar Vehículo Colega", key="btn_reg_colega"):
        p_val, err_cp = validar_y_parsear_monto(col_precio_str)
        tasa_val = 0.0
        err_tasa = None

        if col_moneda == "Dólares (USD)" and tasa_str.strip():
            tasa_val, err_tasa = validar_y_parsear_monto(tasa_str)

        if not col_nombre:
            st.error("Ingresa el nombre del vehículo.")
        elif err_cp:
            st.error(f"Error en precio: {err_cp}")
        elif err_tasa:
            st.error(f"Error en tasa: {err_tasa}")
        else:
            if col_moneda == "Dólares (USD)" and tasa_val > 0:
                precio_final = p_val * tasa_val
            else:
                precio_final = p_val

            rutas_fotos_colega = []
            if fotos_colega:
                for f_item in fotos_colega:
                    timestamp = datetime.datetime.now().strftime(
                        "%Y%m%d_%H%M%S_%f"
                    )
                    nombre_archivo = f"colega_{timestamp}_{f_item.name}"
                    ruta_completa = os.path.join(
                        CARPETA_FOTOS, nombre_archivo
                    )
                    with open(ruta_completa, "wb") as f:
                        f.write(f_item.getbuffer())
                    rutas_fotos_colega.append(ruta_completa)

            st.session_state.colegas.append(
                {
                    "nombre": col_nombre,
                    "dueno": col_dueno,
                    "precio": precio_final,
                    "moneda_original": col_moneda,
                    "precio_original": p_val,
                    "tasa": tasa_val if (col_moneda == "Dólares (USD)" and tasa_val > 0) else None,
                    "estado": col_estado,
                    "fotos": rutas_fotos_colega,
                }
            )
            st.success("Registrado con éxito.")
            st.rerun()

    st.markdown("---")
    if st.session_state.colegas:
        for idx, c in enumerate(st.session_state.colegas):
            if c.get("moneda_original") == "Dólares (USD)":
                if c.get("tasa") and c["tasa"] > 0:
                    detalle_precio = f"US$ {c['precio_original']:,.2f} (Tasa: {c['tasa']:,.2f}) ➔ RD$ {c['precio']:,.2f}"
                else:
                    detalle_precio = f"US$ {c['precio_original']:,.2f} (Sin tasa aplicada)"
            else:
                detalle_precio = f"RD$ {c['precio']:,.2f}"

            with st.expander(
                f"🤝 {c['nombre']} (Dueño: {c['dueno']}) — Estado: **{c['estado']}** | Precio: {detalle_precio}"
            ):
                st.markdown(f"**Vehículo:** {c['nombre']}")
                st.markdown(f"**Dueño / Colega:** {c['dueno']}")
                st.markdown(f"**Precio de Acuerdo:** {detalle_precio}")

                st.markdown("---")
                st.markdown("##### ⚙️ Modificar Datos del Colega (Moneda, Precio o Tasa)")

                with st.form(f"form_edit_colega_{idx}"):
                    ed_c_moneda = st.selectbox(
                        "Moneda",
                        ["Pesos (RD$)", "Dólares (USD)"],
                        index=0 if c.get("moneda_original", "Pesos (RD$)") == "Pesos (RD$)" else 1,
                        key=f"ed_cm_{idx}"
                    )
                    ed_c_precio_str = st.text_input(
                        "Precio Original",
                        value=f"{c['precio_original']:,.0f}",
                        key=f"ed_cp_{idx}"
                    )
                    ed_c_tasa_str = st.text_input(
                        "Tasa del Dólar (Opcional)",
                        value=f"{c['tasa']:,.2f}" if c.get("tasa") else "",
                        key=f"ed_ct_{idx}"
                    )
                    ed_c_est = st.selectbox(
                        "Estado",
                        ["Disponible para Venta", "Vendido"],
                        index=["Disponible para Venta", "Vendido"].index(c["estado"]),
                        key=f"ed_ce_{idx}"
                    )

                    val_ed_p, err_edp = validar_y_parsear_monto(ed_c_precio_str)
                    val_ed_t, err_edt = 0.0, None
                    if ed_c_tasa_str.strip():
                        val_ed_t, err_edt = validar_y_parsear_monto(ed_c_tasa_str)

                    if st.form_submit_button("Guardar Cambios de Colega"):
                        if err_edp:
                            st.error(f"Error en precio: {err_edp}")
                        elif err_edt:
                            st.error(f"Error en tasa: {err_edt}")
                        else:
                            if ed_c_moneda == "Dólares (USD)" and val_ed_t > 0:
                                nuevo_precio_final = val_ed_p * val_ed_t
                            else:
                                nuevo_precio_final = val_ed_p

                            c["moneda_original"] = ed_c_moneda
                            c["precio_original"] = val_ed_p
                            c["tasa"] = val_ed_t if (ed_c_moneda == "Dólares (USD)" and val_ed_t > 0) else None
                            c["precio"] = nuevo_precio_final
                            c["estado"] = ed_c_est

                            st.success("¡Vehículo de colega actualizado con éxito!")
                            st.rerun()

                st.markdown("---")
                st.markdown("### 📸 Galería")
                if c.get("fotos"):
                    cols_c_fotos = st.columns(3)
                    for f_idx, ruta_fc in enumerate(c["fotos"]):
                        if os.path.exists(ruta_fc):
                            with cols_c_fotos[f_idx % 3]:
                                st.image(ruta_fc, use_container_width=True)
                                col_dc_btn, col_delc_btn = st.columns(2)
                                with col_dc_btn:
                                    with open(ruta_fc, "rb") as archivo_img_c:
                                        st.download_button(
                                            label=f"📥 #{f_idx+1}",
                                            data=archivo_img_c,
                                            file_name=os.path.basename(ruta_fc),
                                            mime="image/jpeg",
                                            key=f"dl_c_{idx}_{f_idx}",
                                        )
                                with col_delc_btn:
                                    if st.button("🗑️", key=f"del_img_col_{idx}_{f_idx}", help="Borrar esta foto"):
                                        c["fotos"].pop(f_idx)
                                        st.rerun()
                else:
                    st.info("Este vehículo de colega no tiene fotografías.")

                nuevas_fotos_colega = st.file_uploader(
                    "Agregar más fotografías a este vehículo de colega",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"add_fotos_col_{idx}"
                )
                if nuevas_fotos_colega:
                    if st.button("Subir fotos seleccionadas", key=f"btn_subir_col_{idx}"):
                        for f_item in nuevas_fotos_colega:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            nombre_archivo = f"colega_{timestamp}_{f_item.name}"
                            ruta_completa = os.path.join(CARPETA_FOTOS, nombre_archivo)
                            with open(ruta_completa, "wb") as f:
                                f.write(f_item.getbuffer())
                            c["fotos"].append(ruta_completa)
                        st.success("¡Fotografías agregadas exitosamente!")
                        st.rerun()

                st.markdown("---")
                if st.button("Eliminar Vehículo de Colega", key=f"col_del_{idx}"):
                    st.session_state.colegas.pop(idx)
                    st.rerun()
    else:
        st.info("No hay vehículos de colegas registrados.")

# ==========================================
# 4. CUENTAS POR COBRAR
# ==========================================
elif pestana == "💰 Cuentas por Cobrar":
    st.subheader("Control de Cuentas por Cobrar a Clientes")

    cta_cliente = st.text_input("Cliente", placeholder="Carlos Santana", key="cta_c")
    cta_concepto = st.text_input(
        "Concepto", placeholder="Inicial pendiente Suzuki SX4", key="cta_con"
    )
    cta_monto_str = st.text_input(
        "Monto Pendiente (RD$)", placeholder="Ej: 50,000", key="cta_m"
    )
    cta_fecha = st.text_input("Fecha Límite / Nota", placeholder="30 Sept", key="cta_f")

    if st.button("Registrar Deuda", key="btn_reg_deuda"):
        m_val, err_ct = validar_y_parsear_monto(cta_monto_str)
        if not cta_cliente:
            st.error("Ingresa el nombre del cliente.")
        elif err_ct:
            st.error(f"Error en monto: {err_ct}")
        else:
            st.session_state.cuentas.append(
                {
                    "cliente": cta_cliente,
                    "concepto": cta_concepto,
                    "monto": m_val,
                    "fecha": cta_fecha,
                }
            )
            st.success("Deuda registrada.")
            st.rerun()

    st.markdown("---")
    if st.session_state.cuentas:
        for idx, ct in enumerate(st.session_state.cuentas):
            col_c1, col_c2 = st.columns([4, 1])
            with col_c1:
                st.markdown(
                    f"👤 **{ct['cliente']}** | Concepto: {ct['concepto']} | Monto: **RD$ {ct['monto']:,.2f}** (Vence: {ct['fecha']})"
                )
            with col_c2:
                if st.button("Cobrado / Cerrar", key=f"ct_del_{idx}"):
                    st.session_state.cuentas.pop(idx)
                    st.rerun()
    else:
        st.info("No hay cuentas por cobrar pendientes.")

# ==========================================
# 5. GASTOS OPERATIVOS DEL DEALER
# ==========================================
elif pestana == "🏢 Gastos Operativos del Dealer":
    st.subheader(
        "Gastos Generales del Negocio (Oscar / El Doctor / Ambos Compartido)"
    )

    gd_concepto = st.text_input(
        "Concepto del Gasto", placeholder="Ej: Alquiler, Luz, Nómina", key="gd_c"
    )
    gd_monto_str = st.text_input(
        "Monto Total (RD$)", placeholder="Ej: 35,000", key="gd_m"
    )
    gd_desc = st.text_area(
        "Descripción detallada del gasto", placeholder="Detalle...", key="gd_d"
    )
    gd_fecha = st.date_input("Fecha del Gasto", value=datetime.date.today(), key="gd_f")

    st.markdown("**Pagado por:**")
    gd_responsable = st.radio(
        "Seleccionar Responsable:",
        ["Oscar", "El Doctor", "Ambos (Compartido)"],
        horizontal=True,
        key="resp_dealer_nuevo",
    )

    monto_oscar = 0.0
    monto_doctor = 0.0
    gd_monto_val, err_gdm = validar_y_parsear_monto(gd_monto_str)

    if gd_responsable == "Ambos (Compartido)":
        st.markdown(
            "<small style='color: #2563eb;'><b>Oscar arriba / El Doctor abajo:</b></small>",
            unsafe_allow_html=True,
        )
        mo_d_str = st.text_input(
            "Parte que asume Oscar (RD$)", placeholder="Ej: 17,500", key="mod_s"
        )
        md_d_str = st.text_input(
            "Parte que asume El Doctor (RD$)", placeholder="Ej: 17,500", key="mdd_s"
        )
        monto_oscar, err_gmo = validar_y_parsear_monto(mo_d_str)
        monto_doctor, err_gmd = validar_y_parsear_monto(md_d_str)
    elif gd_responsable == "Oscar":
        monto_oscar = gd_monto_val
        err_gmo, err_gmd = None, None
    else:
        monto_doctor = gd_monto_val
        err_gmo, err_gmd = None, None

    if st.button("Registrar Gasto del Dealer", key="btn_reg_gd"):
        if not gd_concepto:
            st.error("Ingresa el concepto del gasto.")
        elif err_gdm:
            st.error(f"Error en monto: {err_gdm}")
        elif gd_responsable == "Ambos (Compartido)" and (err_gmo or err_gmd):
            st.error("Error en formato de aportes de los socios.")
        elif gd_responsable == "Ambos (Compartido)" and (
            monto_oscar + monto_doctor
        ) != gd_monto_val:
            st.error(
                f"❌ La suma de aportes no concuerda con el monto total del gasto."
            )
        else:
            st.session_state.gastos_dealer.append(
                {
                    "id": len(st.session_state.gastos_dealer) + 1,
                    "concepto": gd_concepto,
                    "descripcion": gd_desc,
                    "monto": gd_monto_val,
                    "pagado_por": gd_responsable,
                    "monto_oscar": monto_oscar,
                    "monto_doctor": monto_doctor,
                    "fecha": str(gd_fecha),
                    "mes": str(gd_fecha)[:7],
                }
            )
            st.success("Gasto registrado exitosamente.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Historial y Edición de Gastos Operativos")

    if st.session_state.gastos_dealer:
        for idx, gd in enumerate(st.session_state.gastos_dealer):
            if gd["pagado_por"] == "Ambos (Compartido)":
                det_dealer = f"(Pagado por: Oscar RD$ {gd['monto_oscar']:,.2f} / Doctor RD$ {gd['monto_doctor']:,.2f})"
            else:
                det_dealer = f"(Pagado por: {gd['pagado_por']})"

            with st.expander(
                f"📌 {gd['concepto']} — RD$ {gd['monto']:,.2f} ({fecha_formato_rd(gd['fecha'])}) {det_dealer}"
            ):
                with st.form(f"form_edit_gasto_{idx}"):
                    ed_concepto = st.text_input(
                        "Concepto", value=gd["concepto"], key=f"ed_c_{idx}"
                    )
                    ed_desc = st.text_area(
                        "Descripción",
                        value=gd.get("descripcion", ""),
                        key=f"ed_d_{idx}",
                    )
                    ed_monto_str = st.text_input(
                        "Monto Total (RD$)",
                        value=f"{gd['monto']:,.0f}",
                        key=f"ed_m_str_{idx}",
                    )
                    ed_fecha = st.date_input(
                        "Fecha",
                        value=datetime.date.fromisoformat(gd["fecha"]),
                        key=f"ed_f_{idx}",
                    )
                    ed_resp = st.selectbox(
                        "Pagado por:",
                        ["Oscar", "El Doctor", "Ambos (Compartido)"],
                        index=["Oscar", "El Doctor", "Ambos (Compartido)"].index(
                            gd["pagado_por"]
                        ),
                        key=f"ed_r_{idx}",
                    )

                    ed_mo = gd.get("monto_oscar", 0.0)
                    ed_md = gd.get("monto_doctor", 0.0)
                    ed_monto_val, err_edm = validar_y_parsear_monto(
                        ed_monto_str
                    )

                    if ed_resp == "Ambos (Compartido)":
                        st.markdown(
                            "<small style='color: #2563eb;'><b>Oscar arriba / El Doctor abajo:</b></small>",
                            unsafe_allow_html=True,
                        )
                        c_es1, c_es2 = st.columns(2)
                        with c_es1:
                            ed_mo_str = st.text_input(
                                "Monto Oscar",
                                value=f"{ed_mo:,.0f}",
                                key=f"ed_mo_str_{idx}",
                            )
                            ed_mo, err_edmo = validar_y_parsear_monto(ed_mo_str)
                        with c_es2:
                            ed_md_str = st.text_input(
                                "Monto Doctor",
                                value=f"{ed_md:,.0f}",
                                key=f"ed_md_str_{idx}",
                            )
                            ed_md, err_edmd = validar_y_parsear_monto(ed_md_str)
                    elif ed_resp == "Oscar":
                        ed_mo = ed_monto_val
                        ed_md = 0.0
                        err_edmo, err_edmd = None, None
                    else:
                        ed_mo = 0.0
                        ed_md = ed_monto_val
                        err_edmo, err_edmd = None, None

                    col_ba1, col_ba2 = st.columns(2)
                    with col_ba1:
                        if st.form_submit_button("Guardar Cambios"):
                            if err_edm:
                                st.error(f"Error en monto: {err_edm}")
                            elif ed_resp == "Ambos (Compartido)" and (
                                err_edmo or err_edmd
                            ):
                                st.error(
                                    "Error en formato de aportes de socios."
                                )
                            elif ed_resp == "Ambos (Compartido)" and (
                                ed_mo + ed_md
                            ) != ed_monto_val:
                                st.error(
                                    f"❌ La suma de aportes no concuerda con el monto total."
                                )
                            else:
                                gd["concepto"] = ed_concepto
                                gd["descripcion"] = ed_desc
                                gd["monto"] = ed_monto_val
                                gd["fecha"] = str(ed_fecha)
                                gd["mes"] = str(ed_fecha)[:7]
                                gd["pagado_por"] = ed_resp
                                gd["monto_oscar"] = ed_mo
                                gd["monto_doctor"] = ed_md
                                st.success("¡Gasto actualizado!")
                                st.rerun()
                    with col_ba2:
                        if st.form_submit_button("🗑️ Borrar Gasto"):
                            st.session_state.gastos_dealer.pop(idx)
                            st.rerun()
    else:
        st.info("No hay gastos operativos registrados.")

# ==========================================
# 6. TRASPASOS PENDIENTES
# ==========================================
elif pestana == "📋 Traspasos Pendientes":
    st.subheader("Gestión y Control de Traspasos")

    st.markdown("**Registrar Nuevo Traspaso**")
    t_vehiculo = st.text_input(
        "Marca, Modelo y Año del Vehículo",
        placeholder="Ej: Toyota Corolla 2020",
        key="traspaso_vehiculo",
    )
    t_cliente = st.text_input(
        "Nombre del Cliente",
        placeholder="Ej: Juan Pérez",
        key="traspaso_cliente",
    )
    t_valor_dgii_str = st.text_input(
        "Valor en DGII (RD$)",
        placeholder="Ej: 500,000",
        key="traspaso_dgii",
    )

    t_plan_piloto = st.radio(
        "¿La persona irá a Plan Piloto?", ["Sí", "No"], horizontal=True, key="t_pp"
    )

    val_dgii, err_dgii = validar_y_parsear_monto(t_valor_dgii_str)

    if st.button("Calcular y Registrar Traspaso", key="btn_guardar_traspaso"):
        if not t_vehiculo:
            st.error("Por favor ingresa la marca, modelo y año del vehículo.")
        elif not t_cliente:
            st.error("Por favor ingresa el nombre del cliente.")
        elif t_valor_dgii_str and err_dgii:
            st.error(err_dgii)
        elif val_dgii <= 0:
            st.error("Por favor ingresa un valor en DGII válido.")
        else:
            monto_2_pct = val_dgii * 0.02
            cheque_admin = 350.0 if monto_2_pct > 15000 else 0.0
            notarizacion = 800.0
            legalizacion = 800.0
            gestion = 3500.0
            plan_piloto_costo = 2500.0 if t_plan_piloto == "No" else 0.0

            total_traspaso = (
                monto_2_pct
                + cheque_admin
                + notarizacion
                + legalizacion
                + gestion
                + plan_piloto_costo
            )

            nuevo_traspaso = {
                "vehiculo": t_vehiculo,
                "cliente": t_cliente,
                "valor_dgii": val_dgii,
                "monto_2_pct": monto_2_pct,
                "cheque_admin": cheque_admin,
                "notarizacion": notarizacion,
                "legalizacion": legalizacion,
                "gestion": gestion,
                "plan_piloto": t_plan_piloto,
                "plan_piloto_costo": plan_piloto_costo,
                "total": total_traspaso,
                "estado": "Pendiente",
            }

            st.session_state.traspasos.append(nuevo_traspaso)
            st.success("¡Traspaso registrado exitosamente!")
            st.rerun()

    st.markdown("---")
    st.markdown("### Listado de Traspasos Registrados")

    if st.session_state.traspasos:
        for idx, t in enumerate(st.session_state.traspasos):
            with st.expander(
                f"🚗 {t['vehiculo']} | Cliente: {t['cliente']} — Estatus: **{t['estado']}** | Total: RD$ {t['total']:,.2f}"
            ):
                st.markdown(f"**Vehículo:** {t['vehiculo']}")
                st.markdown(f"**Cliente:** {t['cliente']}")
                st.markdown(f"**Valor en DGII:** RD$ {t['valor_dgii']:,.2f}")
                st.markdown("---")
                st.markdown("##### 📊 Desglose de Gastos del Traspaso:")
                st.markdown(
                    f"• **Impuesto 2% DGII:** RD$ {t['monto_2_pct']:,.2f}"
                )
                if t["cheque_admin"] > 0:
                    st.markdown(
                        f"• **Cheque Administrativo:** RD$ {t['cheque_admin']:,.2f}"
                    )
                st.markdown(
                    f"• **Notarización de Acto de Venta:** RD$ {t['notarizacion']:,.2f}"
                )
                st.markdown(
                    f"• **Legalización en Procuraduría:** RD$ {t['legalizacion']:,.2f}"
                )
                st.markdown(f"• **Gastos de Gestión:** RD$ {t['gestion']:,.2f}")
                st.markdown(
                    f"• **Va a Plan Piloto:** {t['plan_piloto']}"
                    + (
                        f" (RD$ {t['plan_piloto_costo']:,.2f})"
                        if t["plan_piloto_costo"] > 0
                        else ""
                    )
                )
                st.markdown(
                    f"### **Costo Total del Traspaso:** RD$ {t['total']:,.2f}"
                )

                st.markdown("---")
                st.markdown("##### ⚙️ Modificar Gastos de Gestión o Estatus")

                with st.form(f"form_edit_traspaso_{idx}"):
                    edit_gestion_str = st.text_input(
                        "Modificar Gastos de Gestión (RD$)",
                        value=f"{t['gestion']:,.0f}",
                        key=f"edit_gestion_{idx}",
                    )
                    nuevo_est_traspaso = st.selectbox(
                        "Cambiar Estatus",
                        ["Pendiente", "Realizado"],
                        index=["Pendiente", "Realizado"].index(t["estado"]),
                        key=f"est_trasp_{idx}",
                    )

                    nueva_gestion_val, err_eg = validar_y_parsear_monto(
                        edit_gestion_str
                    )

                    if st.form_submit_button("Guardar Cambios de Traspaso"):
                        if err_eg:
                            st.error(f"Error en monto de gestión: {err_eg}")
                        else:
                            t["gestion"] = nueva_gestion_val
                            t["estado"] = nuevo_est_traspaso
                            t["total"] = (
                                t["monto_2_pct"]
                                + t["cheque_admin"]
                                + t["notarizacion"]
                                + t["legalizacion"]
                                + t["gestion"]
                                + t["plan_piloto_costo"]
                            )
                            st.success("¡Traspaso actualizado con éxito!")
                            st.rerun()

                st.markdown("---")
                if st.button("🗑️ Eliminar Traspaso", key=f"del_t_{idx}"):
                    st.session_state.traspasos.pop(idx)
                    st.rerun()
    else:
        st.info("No hay traspasos registrados.")