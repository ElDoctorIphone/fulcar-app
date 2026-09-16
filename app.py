import calendar
import datetime
import io
import json
import os
import pandas as pd
import streamlit as st
import cloudinary
import cloudinary.uploader

# Configuración de la página en modo ancho (wide)
st.set_page_config(
    page_title="FULCAR AUTO IMPORT SRL", page_icon="🚗", layout="wide"
)

# --- CONFIGURACIÓN DE CLOUDINARY PARA FOTOS PERMANENTES ---
try:
    cloudinary.config(
        cloud_name=st.secrets["cloudinary"]["cloud_name"],
        api_key=st.secrets["cloudinary"]["api_key"],
        api_secret=st.secrets["cloudinary"]["api_secret"]
    )
except Exception:
    pass

def subir_imagen_a_cloudinary(f_item):
    """Sube la imagen a Cloudinary y devuelve la URL permanente en la nube"""
    try:
        resultado = cloudinary.uploader.upload(f_item)
        return resultado.get("secure_url")
    except Exception as e:
        CARPETA_FOTOS = "uploads_vehiculos"
        if not os.path.exists(CARPETA_FOTOS):
            os.makedirs(CARPETA_FOTOS)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nombre_archivo = f"{timestamp}_{f_item.name}"
        ruta_completa = os.path.join(CARPETA_FOTOS, nombre_archivo)
        with open(ruta_completa, "wb") as f:
            f.write(f_item.getbuffer())
        return ruta_completa

# --- ARCHIVO DE PERSISTENCIA PERMANENTE (BASE DE DATOS LOCAL) ---
DB_FILE = "fulcar_database.json"

def cargar_datos_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "propio": [],
        "colegas": [],
        "cuentas": [],
        "gastos_dealer": [],
        "traspasos": []
    }

def guardar_datos_db():
    datos = {
        "propio": st.session_state.propio,
        "colegas": st.session_state.colegas,
        "cuentas": st.session_state.cuentas,
        "gastos_dealer": st.session_state.gastos_dealer,
        "traspasos": st.session_state.traspasos
    }
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error al guardar en la base de datos: {e}")

# --- CLAVE SECRETA DE ACCESO ---
CLAVE_SECRETA = "fulcar2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            if os.path.exists("fulcar_logo.png"):
                st.image("fulcar_logo.png", width=250)
            else:
                st.markdown("## 🏎️ **FULCAR AUTO IMPORT SRL**")
        except:
            st.markdown("## 🏎️ **FULCAR AUTO IMPORT SRL**")

        st.subheader("Acceso Restringido al Sistema")
        
        with st.form("form_login"):
            password_ingresada = st.text_input("Ingresa la Clave de Seguridad", type="password")
            btn_login = st.form_submit_button("Entrar al Sistema")

            if btn_login:
                if password_ingresada == CLAVE_SECRETA:
                    st.session_state.autenticado = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
        
        st.stop()

# ==========================================
# CÓDIGO PRINCIPAL DEL SISTEMA
# ==========================================
st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 16px; }
    @media (max-width: 768px) {
        .stColumns { flex-direction: column !important; }
        .stMetric { margin-bottom: 15px; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.2rem !important; }
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

# Cargar datos persistentes al iniciar la sesión
datos_guardados = cargar_datos_db()
if "propio" not in st.session_state:
    st.session_state.propio = datos_guardados["propio"]
if "colegas" not in st.session_state:
    st.session_state.colegas = datos_guardados["colegas"]
if "cuentas" not in st.session_state:
    st.session_state.cuentas = datos_guardados["cuentas"]
if "gastos_dealer" not in st.session_state:
    st.session_state.gastos_dealer = datos_guardados["gastos_dealer"]
if "traspasos" not in st.session_state:
    st.session_state.traspasos = datos_guardados["traspasos"]

MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}
DIAS_ES = {
    0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
    4: "viernes", 5: "sábado", 6: "domingo",
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
    if not texto:
        return 0.0, "El campo de monto está vacío."
    texto_limpio = str(texto).strip()
    sin_comas_ni_moneda = texto_limpio.replace("RD$", "").replace("$", "").replace(",", "").strip()
    try:
        val_num = float(sin_comas_ni_moneda)
    except:
        return 0.0, "El valor ingresado no es un número válido."
    if val_num >= 1000 and "," not in texto_limpio:
        return 0.0, f"❌ Formato incorrecto. Debe incluir las comas de miles (Ej: 250,000 en lugar de 250000)."
    return val_num, None

# --- ENCABEZADO, LOGO Y BOTÓN DE RESPALDO EXTERNO ---
col_logo, col_titulo, col_respaldo = st.columns([1, 3, 1])
with col_logo:
    try:
        if os.path.exists("fulcar_logo.png"):
            st.image("fulcar_logo.png", width=180)
        else:
            st.markdown("### 🏎️ **FULCAR AUTO IMPORT**")
    except:
        st.markdown("### 🏎️ **FULCAR AUTO IMPORT**")

with col_titulo:
    st.title("Sistema de Control Operativo")
    hoy_str = fecha_formato_rd(datetime.date.today())
    st.caption(f"Fecha actual: {hoy_str.capitalize()}")

with col_respaldo:
    st.markdown("<br>", unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(st.session_state.propio).to_excel(writer, sheet_name='Inventario_Propio', index=False)
        pd.DataFrame(st.session_state.colegas).to_excel(writer, sheet_name='Vehiculos_Colegas', index=False)
        pd.DataFrame(st.session_state.cuentas).to_excel(writer, sheet_name='Cuentas_Cobrar', index=False)
        pd.DataFrame(st.session_state.gastos_dealer).to_excel(writer, sheet_name='Gastos_Dealer', index=False)
        pd.DataFrame(st.session_state.traspasos).to_excel(writer, sheet_name='Traspasos', index=False)
    
    st.download_button(
        label="📥 Descargar Respaldo Excel",
        data=output.getvalue(),
        file_name=f"Respaldo_Fulcar_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Descarga una copia exacta de respaldo en tu dispositivo."
    )

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
        st.info(f"📅 El mes seleccionado tiene **{dias_en_mes} días** en total.")

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
        g["monto"] for g in st.session_state.gastos_dealer if g.get("mes") == mes_seleccionado
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ganancia Neta del Mes", f"RD$ {ganancia_mes:,.2f}")
    kpi2.metric("Vehículos Vendidos", vendidos_mes_count)
    kpi3.metric("Valor Total Ventas", f"RD$ {valor_ventas_mes:,.2f}")
    kpi4.metric("Gastos Dealer (Mes)", f"RD$ {gastos_dealer_mes:,.2f}")

    st.markdown("### Detalle de Vehículos Vendidos en el Periodo")
    if vehiculos_vendidos_detalles:
        st.dataframe(pd.DataFrame(vehiculos_vendidos_detalles), use_container_width=True)
    else:
        st.info("No hay vehículos vendidos registrados en este mes.")

# ==========================================
# 2. MI INVENTARIO PROPIO
# ==========================================
elif pestana == "🚗 Mi Inventario Propio":
    st.subheader("Gestión de Mi Inventario (Vehículos Propios)")

    st.markdown("**Registrar Nuevo Vehículo (Compra)**")

    nombre_inv = st.text_input("Marca, Modelo, Año", placeholder="Ej: Toyota RAV4 XLE 2025", key="input_nombre_nuevo")
    costo_str = st.text_input("Costo de Compra (RD$)", placeholder="Ej: 500,000", key="input_costo_nuevo")

    c_est, c_pag = st.columns(2)
    with c_est:
        estado_inv = st.selectbox("Estado Inicial", ["Disponible", "En Taller / Reparación", "Vendido"], key="select_estado_nuevo")
    with c_pag:
        pagado_por_compra = st.selectbox("Compra Pagada por:", ["Oscar", "El Doctor", "Ambos (Compartido)"], key="select_pagado_nuevo_2")

    mo_str = ""
    md_str = ""
    if pagado_por_compra == "Ambos (Compartido)":
        st.markdown("<small style='color: #2563eb;'><b>Especificar aportes de la compra:</b></small>", unsafe_allow_html=True)
        col_apo1, col_apo2 = st.columns(2)
        with col_apo1:
            mo_str = st.text_input("Parte que puso Oscar (RD$)", placeholder="Ej: 250,000", key="mo_nuevo_str")
        with col_apo2:
            md_str = st.text_input("Parte que puso El Doctor (RD$)", placeholder="Ej: 250,000", key="md_nuevo_str")

    fotos_subidas = st.file_uploader(
        "Fotografías del Vehículo (Opcional)",
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
                st.error(f"❌ La suma de aportes no concuerda con el costo total.")
            else:
                rutas_fotos = []
                if fotos_subidas:
                    for f_item in fotos_subidas:
                        url_img = subir_imagen_a_cloudinary(f_item)
                        if url_img:
                            rutas_fotos.append(url_img)

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
                guardar_datos_db()
                st.success(f"Vehículo {nombre_inv} agregado exitosamente.")
                st.rerun()
        else:
            rutas_fotos = []
            if fotos_subidas:
                for f_item in fotos_subidas:
                    url_img = subir_imagen_a_cloudinary(f_item)
                    if url_img:
                        rutas_fotos.append(url_img)

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
            guardar_datos_db()
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
                    st.markdown(f"**Monto de la Venta:** RD$ {v['precio_venta']:,.2f}")
                    st.markdown(f"**Ganancia Neta Total:** RD$ {v['ganancia_neta']:,.2f}")

                st.markdown("---")
                nuevo_estado = st.selectbox(
                    "Estado Actual",
                    ["Disponible", "En Taller / Reparación", "Vendido"],
                    index=["Disponible", "En Taller / Reparación", "Vendido"].index(v["estado"])
                    if v["estado"] in ["Disponible", "En Taller / Reparación", "Vendido"]
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
                        value=(datetime.date.fromisoformat(v["fecha_venta"]) if v["fecha_venta"] else datetime.date.today()),
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

                            total_g = sum(gg["monto"] for gg in v.get("lista_gastos", []))
                            inversion_total_calc = v["costo"] + total_g
                            ganancia_calc = v["precio_venta"] - inversion_total_calc

                            total_oscar_inv = v["monto_oscar_compra"] + sum(gg["monto_oscar"] for gg in v.get("lista_gastos", []))
                            total_doctor_inv = v["monto_doctor_compra"] + sum(gg["monto_doctor"] for gg in v.get("lista_gastos", []))

                            v["ganancia_neta"] = ganancia_calc
                            v["retorno_oscar"] = total_oscar_inv
                            v["retorno_doctor"] = total_doctor_inv
                            v["ganancia_oscar"] = ganancia_calc / 2.0
                            v["ganancia_doctor"] = ganancia_calc / 2.0
                            guardar_datos_db()
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
                        guardar_datos_db()
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
                st.markdown("##### 🛠️ Historial de Inversión y Gastos de este Vehículo")

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
                            if st.button("Borrar", key=f"del_gv_{i}_{idx_g}"):
                                v["lista_gastos"].pop(idx_g)
                                if v["estado"] == "Vendido" and v["precio_venta"]:
                                    total_g = sum(gg["monto"] for gg in v["lista_gastos"])
                                    inversion_total_calc = v["costo"] + total_g
                                    ganancia_calc = v["precio_venta"] - inversion_total_calc

                                    total_oscar_inv = v["monto_oscar_compra"] + sum(gg["monto_oscar"] for gg in v["lista_gastos"])
                                    total_doctor_inv = v["monto_doctor_compra"] + sum(gg["monto_doctor"] for gg in v["lista_gastos"])

                                    v["ganancia_neta"] = ganancia_calc
                                    v["retorno_oscar"] = total_oscar_inv
                                    v["retorno_doctor"] = total_doctor_inv
                                    v["ganancia_oscar"] = ganancia_calc / 2.0
                                    v["ganancia_doctor"] = ganancia_calc / 2.0
                                guardar_datos_db()
                                st.rerun()

                st.markdown("---")
                st.markdown("##### ➕ Agregar Nuevo Gasto a este Vehículo")

                with st.form(f"form_gasto_vehiculo_{i}"):
                    gc1, gc2 = st.columns(2)
                    with gc1:
                        g_concepto = st.text_input("Concepto del Gasto", placeholder="Ej: Pintura", key=f"gc_con_{i}")
                        g_monto_str = st.text_input("Monto (RD$)", placeholder="Ej: 24,000", key=f"gc_mon_str_{i}")
                    with gc2:
                        g_resp = st.selectbox("Pagado por:", ["Oscar", "El Doctor", "Ambos (Compartido)"], key=f"gc_resp_{i}")

                    g_mo = 0.0
                    g_md = 0.0
                    g_monto_val, err_gm = validar_y_parsear_monto(g_monto_str)

                    if g_resp == "Ambos (Compartido)":
                        st.markdown("<small style='color: #2563eb;'><b>Oscar arriba / El Doctor abajo:</b></small>", unsafe_allow_html=True)
                        g_mo_str = st.text_input("Parte Oscar (RD$)", placeholder="Ej: 12,000", key=f"gc_mo_str_{i}")
                        g_md_str = st.text_input("Parte Doctor (RD$)", placeholder="Ej: 12,000", key=f"gc_md_str_{i}")
                        g_mo, err_gmo = validar_y_parsear_monto(g_mo_str)
                        g_md, err_gmd = validar_y_parsear_monto(g_md_str)
                    elif g_resp == "Oscar":
                        g_mo = g_monto_val
                        err_gmo, err_gmd = None, None
                    else:
                        g_md = g_monto_val
                        err_gmo, err_gmd = None, None

                    if st.form_submit_button("Registrar Gasto a este Vehículo"):
                        if not g_concepto:
                            st.error("Ingresa el concepto del gasto.")
                        elif err_gm:
                            st.error(f"Error en monto: {err_gm}")
                        elif g_resp == "Ambos (Compartido)" and (err_gmo or err_gmd):
                            st.error("Error en formato de aportes.")
                        elif g_resp == "Ambos (Compartido)" and (g_mo + g_md) != g_monto_val:
                            st.error(f"❌ La suma de aportes no concuerda con el total.")
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
                                total_g = sum(gg["monto"] for gg in v["lista_gastos"])
                                inversion_total_calc = v["costo"] + total_g
                                ganancia_calc = v["precio_venta"] - inversion_total_calc

                                total_oscar_inv = v["monto_oscar_compra"] + sum(gg["monto_oscar"] for gg in v["lista_gastos"])
                                total_doctor_inv = v["monto_doctor_compra"] + sum(gg["monto_doctor"] for gg in v["lista_gastos"])

                                v["ganancia_neta"] = ganancia_calc
                                v["retorno_oscar"] = total_oscar_inv
                                v["retorno_doctor"] = total_doctor_inv
                                v["ganancia_oscar"] = ganancia_calc / 2.0
                                v["ganancia_doctor"] = ganancia_calc / 2.0

                            guardar_datos_db()
                            st.success("¡Gasto agregado!")
                            st.rerun()

                # --- SECCIÓN GALERÍA ---
                st.markdown("---")
                st.markdown("### 📸 Galería")
                if v.get("fotos"):
                    cols_fotos = st.columns(3)
                    for f_idx, ruta_f in enumerate(v["fotos"]):
                        with cols_fotos[f_idx % 3]:
                            st.image(ruta_f, use_container_width=True)
                            col_d_btn, col_del_btn = st.columns(2)
                            with col_d_btn:
                                st.markdown(f"[📥 Ver #{f_idx+1}]({ruta_f})")
                            with col_del_btn:
                                if st.button("🗑️", key=f"del_img_prop_{i}_{f_idx}", help="Borrar foto"):
                                    v["fotos"].pop(f_idx)
                                    guardar_datos_db()
                                    st.rerun()
                else:
                    st.info("Sin fotografías registradas.")

                nuevas_fotos_propio = st.file_uploader(
                    "Agregar más fotografías",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"add_fotos_prop_{i}"
                )
                if nuevas_fotos_propio:
                    if st.button("Subir fotos seleccionadas", key=f"btn_subir_prop_{i}"):
                        for f_item in nuevas_fotos_propio:
                            url_img = subir_imagen_a_cloudinary(f_item)
                            if url_img:
                                v["fotos"].append(url_img)
                        guardar_datos_db()
                        st.success("¡Fotos agregadas!")
                        st.rerun()

                st.markdown("---")
                if st.button("🗑️ Eliminar Vehículo Completo", key=f"del_{i}"):
                    st.session_state.propio.pop(i)
                    guardar_datos_db()
                    st.rerun()

        st.markdown("---")
        vehiculos_activos = [v for v in st.session_state.propio if v["estado"] != "Vendido"]
        total_vehiculos = len(vehiculos_activos)
        valor_total_inv = sum(
            v["costo"] + sum(g["monto"] for g in v.get("lista_gastos", [])) for v in vehiculos_activos
        )

        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Cantidad de Vehículos en Inventario", total_vehiculos)
        c_m2.metric("Valor Total del Inventario", f"RD$ {valor_total_inv:,.2f}")
    else:
        st.info("No hay vehículos registrados en tu inventario.")

# ==========================================
# 3. VEHÍCULOS DE COLEGAS
# ==========================================
elif pestana == "🤝 Vehículos de Colegas":
    st.subheader("Inventario Externo (Vehículos de Colegas)")

    col_nombre = st.text_input("Vehículo", placeholder="Ej: Honda CR-V", key="col_n")
    col_dueno = st.text_input("Dueño / Colega", placeholder="Ej: Juan Pérez", key="col_d")
    
    col_moneda = st.radio("Moneda", ["Pesos (RD$)", "Dólares (USD)"], horizontal=True, key="col_moneda_radio")
    col_precio_str = st.text_input("Precio Acuerdo", placeholder="Ej: 1,200,000", key="col_p")

    tasa_str = ""
    if col_moneda == "Dólares (USD)":
        tasa_str = st.text_input("Tasa del Dólar (Opcional)", placeholder="Ej: 60.00", key="col_tasa")

    col_estado = st.selectbox("Estado", ["Disponible para Venta", "Vendido"], key="col_e")
    fotos_colega = st.file_uploader("Fotografías", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="fotos_colega_nuevo")

    if st.button("Registrar Vehículo Colega", key="btn_reg_colega"):
        p_val, err_cp = validar_y_parsear_monto(col_precio_str)
        tasa_val = 0.0
        err_tasa = None

        if col_moneda == "Dólares (USD)" and tasa_str.strip():
            tasa_val, err_tasa = validar_y_parsear_monto(tasa_str)

        if not col_nombre:
            st.error("Ingresa el nombre.")
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
                    url_img = subir_imagen_a_cloudinary(f_item)
                    if url_img:
                        rutas_fotos_colega.append(url_img)

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
            guardar_datos_db()
            st.success("Registrado con éxito.")
            st.rerun()

    st.markdown("---")
    if st.session_state.colegas:
        for idx, c in enumerate(st.session_state.colegas):
            if c.get("moneda_original") == "Dólares (USD)":
                if c.get("tasa") and c["tasa"] > 0:
                    detalle_precio = f"US$ {c['precio_original']:,.2f} (Tasa: {c['tasa']:,.2f}) ➔ RD$ {c['precio']:,.2f}"
                else:
                    detalle_precio = f"US$ {c['precio_original']:,.2f}"
            else:
                detalle_precio = f"RD$ {c['precio']:,.2f}"

            with st.expander(f"🤝 {c['nombre']} ({c['dueno']}) — **{c['estado']}** | {detalle_precio}"):
                if c.get("fotos"):
                    cols_c_fotos = st.columns(3)
                    for f_idx, ruta_fc in enumerate(c["fotos"]):
                        with cols_c_fotos[f_idx % 3]:
                            st.image(ruta_fc, use_container_width=True)
                            st.markdown(f"[📥 Ver #{f_idx+1}]({ruta_fc})")
                if st.button("Eliminar", key=f"col_del_{idx}"):
                    st.session_state.colegas.pop(idx)
                    guardar_datos_db()
                    st.rerun()
    else:
        st.info("No hay vehículos de colegas registrados.")

# ==========================================
# 4. CUENTAS POR COBRAR
# ==========================================
elif pestana == "💰 Cuentas por Cobrar":
    st.subheader("Control de Cuentas por Cobrar a Clientes")

    cta_cliente = st.text_input("Cliente", placeholder="Carlos Santana", key="cta_c")
    cta_concepto = st.text_input("Concepto", placeholder="Inicial pendiente", key="cta_con")
    cta_monto_str = st.text_input("Monto Pendiente (RD$)", placeholder="Ej: 50,000", key="cta_m")
    cta_fecha = st.text_input("Fecha Límite / Nota", placeholder="30 Sept", key="cta_f")

    if st.button("Registrar Deuda", key="btn_reg_deuda"):
        m_val, err_ct = validar_y_parsear_monto(cta_monto_str)
        if not cta_cliente:
            st.error("Ingresa el cliente.")
        elif err_ct:
            st.error(err_ct)
        else:
            st.session_state.cuentas.append(
                {"cliente": cta_cliente, "concepto": cta_concepto, "monto": m_val, "fecha": cta_fecha}
            )
            guardar_datos_db()
            st.success("Registrado.")
            st.rerun()

    st.markdown("---")
    if st.session_state.cuentas:
        for idx, ct in enumerate(st.session_state.cuentas):
            col_c1, col_c2 = st.columns([4, 1])
            with col_c1:
                st.markdown(f"👤 **{ct['cliente']}** | {ct['concepto']} | **RD$ {ct['monto']:,.2f}** (Vence: {ct['fecha']})")
            with col_c2:
                if st.button("Cobrado", key=f"ct_del_{idx}"):
                    st.session_state.cuentas.pop(idx)
                    guardar_datos_db()
                    st.rerun()
    else:
        st.info("No hay cuentas pendientes.")

# ==========================================
# 5. GASTOS OPERATIVOS DEL DEALER
# ==========================================
elif pestana == "🏢 Gastos Operativos del Dealer":
    st.subheader("Gastos Generales del Negocio")

    gd_concepto = st.text_input("Concepto", placeholder="Ej: Alquiler, Luz", key="gd_c")
    gd_monto_str = st.text_input("Monto Total (RD$)", placeholder="Ej: 35,000", key="gd_m")
    gd_desc = st.text_area("Descripción", placeholder="Detalle...", key="gd_d")
    gd_fecha = st.date_input("Fecha", value=datetime.date.today(), key="gd_f")

    gd_responsable = st.radio("Pagado por:", ["Oscar", "El Doctor", "Ambos (Compartido)"], horizontal=True, key="resp_dealer_nuevo")

    monto_oscar = 0.0
    monto_doctor = 0.0
    gd_monto_val, err_gdm = validar_y_parsear_monto(gd_monto_str)

    if gd_responsable == "Ambos (Compartido)":
        mo_d_str = st.text_input("Parte Oscar (RD$)", placeholder="Ej: 17,500", key="mod_s")
        md_d_str = st.text_input("Parte Doctor (RD$)", placeholder="Ej: 17,500", key="mdd_s")
        monto_oscar, err_gmo = validar_y_parsear_monto(mo_d_str)
        monto_doctor, err_gmd = validar_y_parsear_monto(md_d_str)
    elif gd_responsable == "Oscar":
        monto_oscar = gd_monto_val
    else:
        monto_doctor = gd_monto_val

    if st.button("Registrar Gasto del Dealer", key="btn_reg_gd"):
        if not gd_concepto:
            st.error("Ingresa el concepto.")
        elif err_gdm:
            st.error(err_gdm)
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
            guardar_datos_db()
            st.success("Gasto registrado.")
            st.rerun()

    st.markdown("---")
    if st.session_state.gastos_dealer:
        for idx, gd in enumerate(st.session_state.gastos_dealer):
            with st.expander(f"📌 {gd['concepto']} — RD$ {gd['monto']:,.2f} ({gd['fecha']})"):
                if st.button("Borrar Gasto", key=f"del_gd_{idx}"):
                    st.session_state.gastos_dealer.pop(idx)
                    guardar_datos_db()
                    st.rerun()
    else:
        st.info("No hay gastos registrados.")

# ==========================================
# 6. TRASPASOS PENDIENTES
# ==========================================
elif pestana == "📋 Traspasos Pendientes":
    st.subheader("Gestión y Control de Traspasos")

    st.markdown("**Registrar Nuevo Traspaso**")
    t_vehiculo = st.text_input("Marca, Modelo y Año del Vehículo", placeholder="Ej: Toyota Corolla 2020", key="traspaso_vehiculo")
    t_cliente = st.text_input("Nombre del Cliente", placeholder="Ej: Juan Pérez", key="traspaso_cliente")
    t_valor_dgii_str = st.text_input("Valor en DGII (RD$)", placeholder="Ej: 500,000", key="traspaso_dgii")

    t_plan_piloto = st.radio("¿La persona irá a Plan Piloto?", ["Sí", "No"], horizontal=True, key="t_pp")

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
                monto_2_pct + cheque_admin + notarizacion + legalizacion + gestion + plan_piloto_costo
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
            guardar_datos_db()
            st.success("¡Traspaso registrado exitosamente!")
            st.rerun()

    st.markdown("---")
    st.markdown("### Listado de Traspasos Registrados")

    if st.session_state.traspasos:
        for idx, t in enumerate(st.session_state.traspasos):
            with st.expander(f"🚗 {t['vehiculo']} | Cliente: {t['cliente']} — Estatus: **{t['estado']}** | Total: RD$ {t['total']:,.2f}"):
                st.markdown(f"**Vehículo:** {t['vehiculo']}")
                st.markdown(f"**Cliente:** {t['cliente']}")
                st.markdown(f"**Valor en DGII:** RD$ {t['valor_dgii']:,.2f}")
                st.markdown("---")
                st.markdown("##### 📊 Desglose de Gastos del Traspaso:")
                st.markdown(f"• **Impuesto 2% DGII:** RD$ {t['monto_2_pct']:,.2f}")
                if t["cheque_admin"] > 0:
                    st.markdown(f"• **Cheque Administrativo:** RD$ {t['cheque_admin']:,.2f}")
                st.markdown(f"• **Notarización de Acto de Venta:** RD$ {t['notarizacion']:,.2f}")
                st.markdown(f"• **Legalización en Procuraduría:** RD$ {t['legalizacion']:,.2f}")
                st.markdown(f"• **Gastos de Gestión:** RD$ {t['gestion']:,.2f}")
                st.markdown(f"• **Va a Plan Piloto:** {t['plan_piloto']}" + (f" (RD$ {t['plan_piloto_costo']:,.2f})" if t["plan_piloto_costo"] > 0 else ""))
                st.markdown(f"### **Costo Total del Traspaso:** RD$ {t['total']:,.2f}")

                st.markdown("---")
                st.markdown("##### ⚙️ Modificar Gastos de Gestión o Estatus")

                with st.form(f"form_edit_traspaso_{idx}"):
                    edit_gestion_str = st.text_input("Modificar Gastos de Gestión (RD$)", value=f"{t['gestion']:,.0f}", key=f"edit_gestion_{idx}")
                    nuevo_est_traspaso = st.selectbox("Cambiar Estatus", ["Pendiente", "Realizado"], index=["Pendiente", "Realizado"].index(t["estado"]), key=f"est_trasp_{idx}")

                    nueva_gestion_val, err_eg = validar_y_parsear_monto(edit_gestion_str)

                    if st.form_submit_button("Guardar Cambios de Traspaso"):
                        if err_eg:
                            st.error(f"Error en monto de gestión: {err_eg}")
                        else:
                            t["gestion"] = nueva_gestion_val
                            t["estado"] = nuevo_est_traspaso
                            t["total"] = (
                                t["monto_2_pct"] + t["cheque_admin"] + t["notarizacion"] + t["legalizacion"] + t["gestion"] + t["plan_piloto_costo"]
                            )
                            guardar_datos_db()
                            st.success("¡Traspaso actualizado con éxito!")
                            st.rerun()

                st.markdown("---")
                if st.button("🗑️ Eliminar Traspaso", key=f"del_t_{idx}"):
                    st.session_state.traspasos.pop(idx)
                    guardar_datos_db()
                    st.success("¡Traspaso eliminado!")
                    st.rerun()
    else:
        st.info("No hay traspasos registrados.")
