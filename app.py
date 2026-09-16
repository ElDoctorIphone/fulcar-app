from datetime import datetime
import os
import pandas as pd
import pytz
from streamlit_gsheets import GSheetsConnection
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
LOGO_FILE = "fulcar_logo.png"

st.set_page_config(
    page_title="Control de Vehículos - Fulcar AUTO",
    page_icon="🚗",
    layout="centered",
)

# --- ESTILOS CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    h1, h3 {
        color: #1a1a1a;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ENCABEZADO CON LOGO ---
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
  if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)
  else:
    st.warning(f"⚠️ Falta el archivo '{LOGO_FILE}'")

st.markdown(
    "<h3 style='text-align: center; color: #444; margin-top: -10px;"
    " margin-bottom: 25px; font-size: 1.2rem;'>Control de Vehículos e"
    " Inventario (Nube Permanente)</h3>",
    unsafe_allow_html=True,
)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)


def obtener_tiempo_rd():
  """Obtiene la fecha y hora actual en zona horaria de Santo Domingo (RD)

  en formato DD/MM/YYYY hh:mm a.m./p.m.
  """
  try:
    tz_rd = pytz.timezone("America/Santo_Domingo")
    ahora_rd = datetime.now(tz_rd)
    return (
        ahora_rd.strftime("%d/%m/%Y %I:%M %p")
        .lower()
        .replace("am", "a. m.")
        .replace("pm", "p. m.")
    )
  except Exception:
    return (
        datetime.now()
        .strftime("%d/%m/%Y %I:%M %p")
        .lower()
        .replace("am", "a. m.")
        .replace("pm", "p. m.")
    )


def cargar_datos():
  try:
    # Leemos la hoja de Google Sheets (ttl=0 para datos en tiempo real)
    df = conn.read(ttl=0)
    if df is not None and not df.empty:
      df = df.dropna(how="all")
      return df
  except Exception as e:
    st.error(f"⚠️ Error al leer Google Sheets: {e}")

  return pd.DataFrame(
      columns=[
          "ID",
          "Fecha/Hora",
          "Registrado Por",
          "Cliente",
          "Teléfono",
          "Vehículo",
          "Nota",
      ]
  )


def guardar_datos(df):
  # Método seguro compatible con GSheetsConnection para evitar UnsupportedOperationError
  try:
    conn.update(worksheet="Hoja 1", data=df)
  except Exception:
    # Si requiere sobreescritura general de la hoja principal
    conn.update(data=df)


# Cargar datos desde Google Sheets
df_registros = cargar_datos()

# Asegurar columna ID única
if not df_registros.empty and "ID" not in df_registros.columns:
  df_registros.insert(0, "ID", [str(i) for i in range(1, len(df_registros) + 1)])
elif not df_registros.empty:
  df_registros["ID"] = df_registros["ID"].astype(str)


# --- INTERFAZ SUPERIOR (Desplegable de Vehículos) ---
with st.expander("🚙 Ver Vehículos Registrados en el Sistema"):
  if not df_registros.empty and "Vehículo" in df_registros.columns:
    vehiculos_unicos = df_registros["Vehículo"].dropna().unique()
    if len(vehiculos_unicos) > 0:
      st.write("Lista de vehículos en inventario:")
      for v in vehiculos_unicos:
        st.markdown(f"- 🚗 **{v}**")
    else:
      st.info("No hay vehículos registrados todavía.")
  else:
    st.info("Base de datos en la nube vacía.")

st.markdown("")

# --- FORMULARIO DE REGISTRO ---
st.markdown("### 📝 Registrar Nuevo Cliente / Vehículo")

with st.form("form_registro", clear_on_submit=True):
  nombre_cliente = st.text_input("👤 Nombre y Apellido del Cliente")
  telefono = st.text_input(
      "📱 Número de Teléfono", placeholder="Ej: 809-000-0000"
  )
  registrado_por = st.text_input(
      "✍️ Registrado por (Tu nombre o usuario)", placeholder="Ej: Frank"
  )

  vehiculos_existentes = (
      list(df_registros["Vehículo"].dropna().unique())
      if not df_registros.empty and "Vehículo" in df_registros.columns
      else []
  )

  if len(vehiculos_existentes) > 0:
    opciones_desplegable = ["-- Escribir nuevo vehículo --"] + (
        vehiculos_existentes
    )
    vehiculo_elegido = st.selectbox(
        "🚘 Seleccione o Escriba el Vehículo", options=opciones_desplegable
    )

    if vehiculo_elegido == "-- Escribir nuevo vehículo --":
      vehiculo = st.text_input(
          "🚗 Especifique el Nuevo Vehículo (Marca, Modelo, Año...)"
      )
    else:
      vehiculo = vehiculo_elegido
  else:
    vehiculo = st.text_input(
        "🚗 Vehículo (Escribe el primero: Marca, Modelo, Año...)"
    )

  nota = st.text_area(
      "📋 Nota u Observaciones",
      placeholder="Detalles de entrada, estado del vehículo, motivo...",
  )

  submitted = st.form_submit_button(
      "💾 Guardar en la Nube", use_container_width=True
  )

  if submitted:
    if not nombre_cliente or not telefono or not vehiculo or not registrado_por:
      st.error(
          "⚠️ Por favor completa los campos obligatorios: Cliente, Teléfono,"
          " Vehículo y Registrado Por."
      )
    else:
      max_id = 0
      if not df_registros.empty and "ID" in df_registros.columns:
        try:
          max_id = pd.to_numeric(df_registros["ID"], errors="coerce").max()
          if pd.isna(max_id):
            max_id = len(df_registros)
        except:
          max_id = len(df_registros)

      nuevo_id = str(int(max_id) + 1)
      fecha_hora_rd = obtener_tiempo_rd()

      nuevo_registro = pd.DataFrame(
          [{
              "ID": nuevo_id,
              "Fecha/Hora": fecha_hora_rd,
              "Registrado Por": registrado_por,
              "Cliente": nombre_cliente,
              "Teléfono": telefono,
              "Vehículo": vehiculo,
              "Nota": nota,
          }]
      )
      df_registros = pd.concat(
          [df_registros, nuevo_registro], ignore_index=True
      )
      guardar_datos(df_registros)
      st.success(
          f"✅ ¡Vehículo para {nombre_cliente} guardado en la nube con éxito!"
      )
      st.rerun()

st.markdown("---")

# --- VISTA GENERAL DE REGISTROS ---
st.markdown("### 📊 Base de Datos de Registros (En Vivo)")

if not df_registros.empty:
  busqueda = st.text_input(
      "🔍 Buscar cliente, teléfono o vehículo:", placeholder="Escribe para filtrar..."
  )
  if busqueda:
    df_filtrado = df_registros[
        df_registros.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    ]
  else:
    df_filtrado = df_registros

  st.dataframe(
      df_filtrado.drop(columns=["ID"])
      if "ID" in df_filtrado.columns
      else df_filtrado,
      use_container_width=True,
      hide_index=True,
  )

  csv_data = df_registros.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Respaldo en CSV",
      data=csv_data,
      file_name="respaldo_fulcar.csv",
      mime="text/csv",
      use_container_width=True,
  )
else:
  st.info("ℹ️ La base de datos en la nube está conectada y lista.")

# --- PANEL DE ADMINISTRADOR ---
st.markdown("---")
with st.expander("🔐 Panel de Administrador (Edición / Corrección de Datos)"):
  password_admin = st.text_input(
      "Contraseña de Administrador", type="password"
  )

  if password_admin == "Fulcar0131":
    st.success("✅ Acceso concedido.")

    if not df_registros.empty:
      st.warning(
          "⚠️ **INTERFAZ DE EDICIÓN REAL:** Haz doble clic en cualquier celda"
          " de la tabla de abajo para corregir datos directamente."
      )

      df_editado = st.data_editor(
          df_registros,
          num_rows="dynamic",
          use_container_width=True,
          key="editor",
          column_config={"ID": st.column_config.Column(disabled=True)},
      )

      if st.button("💾 Guardar Cambios en la Nube"):
        if df_editado["ID"].duplicated().any():
          st.error(
              "Error: Hay IDs duplicados. Por favor, corrige los IDs antes de"
              " guardar."
          )
        else:
          guardar_datos(df_editado)
          st.success("🎉 ¡Google Sheets actualizado con éxito!")
          st.rerun()

      st.markdown("### 🗑️ Eliminar un registro específico")
      ids_disponibles = list(df_registros["ID"].astype(str))
      id_a_borrar = st.selectbox(
          "Selecciona el ID del registro a eliminar permanentemente",
          options=ids_disponibles,
      )

      if st.button(
          "❌ Eliminar Registro Seleccionado (IRREVERSIBLE)", type="primary"
      ):
        df_registros = df_registros[
            df_registros["ID"].astype(str) != str(id_a_borrar)
        ]
        if not df_registros.empty:
          df_registros.reset_index(drop=True, inplace=True)
          df_registros.insert(
              0,
              "ID",
              [str(i) for i in range(1, len(df_registros) + 1)],
          )

        guardar_datos(df_registros)
        st.success("🗑️ Registro eliminado de la nube correctamente.")
        st.rerun()
    else:
      st.info("ℹ️ No hay datos para administrar.")
  elif password_admin != "":
    st.error("❌ Contraseña incorrecta.")
