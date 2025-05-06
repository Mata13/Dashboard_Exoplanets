import streamlit as st
import pandas as pd
import time
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title = 'Dashboard Exoplanetas', page_icon = "🪐", layout = "wide")
st.title('Dashboard: Exoplanetas Confirmados 🪐')
#st.markdown("##")
st.markdown("##")


# Cargar datos
df = pd.read_csv('Exoplanets_confirmed.csv')

# Muestra el dataset en streamlit
#st.dataframe(df)


############################# Transformación de la columna de 'año' al formato correcto ########################

# Convertimos la columna 'discovered' al formato correcto de fecha
df['discovered'] = pd.to_datetime(df['discovered'], errors='coerce')

# Extraemos sólo el año
df['year'] = df['discovered'].dt.year


#################################### Indicadores ####################################

# Creamos diferentes indicadores para mostrar
total_exoplanetas = df["planet_status"].shape[0]
#st.write(f"Número de Confirmados con Datos Disponibles: {total_exoplanetas}")
avg_mass = df["mass"].mean()
#st.write(f"Masa Promedio (M Júpiter): {avg_mass}")
avg_radius = df["radius"].mean()
#st.write(f"Radio Promedio (R Júpiter): {avg_radius}")
avg_star_metallicity = df["star_metallicity"].mean()
#st.write(f"Metalicidad Estelar Promedio: {avg_star_metallicity}")
common_method = df["detection_type"].mode()[0]
#st.write(f"Método de Detección Más Común: {common_method}")

# Columnas para mostrar los indicadores
one_column, two_column, three_column, four_column, five_column = st.columns(5)
with one_column:
	st.subheader("Planetas con Datos Disponibles:")
	st.subheader(f"{total_exoplanetas}")

with two_column:
	st.subheader("Masa Promedio (M Júpiter):")
	st.subheader(f"{avg_mass:.2f}")

with three_column:
	st.subheader("Radio Promedio (R Júpiter):")
	st.subheader(f"{avg_radius:.2f}")

with four_column:
	st.subheader("Metalicidad Estelar Promedio:")
	st.subheader(f"{avg_star_metallicity:.2f}")

with five_column:
	st.subheader("Método de Detección Más Común:")
	st.subheader(f"{common_method}")

st.markdown("""---""")


# Configuración de columnas
col1, col2 = st.columns(2, gap = "large")  # 'gap' controla el espacio entre columnas

with col1:
  # Creamos la línea temporal de los exoplanetas descubiertos por año
	timeline = (
		df.groupby("year").size().reset_index(name = "planets")  # DataFrame con columnas year y Planetas
	)
	timeline = timeline.sort_values("year") # ordenar por año

	fig1 = px.line(
		timeline,
    x = "year",
    y = "planets",
    title = "Número de exoplanetas descubiertos por año",
    markers = True,  # añade puntos en cada año
	)

	fig1.update_layout(xaxis_title = "Año", yaxis_title = "Planetas", legend_title_text = "Método de detección")
	fig1.update_traces(line = dict(color = "gold", width =4))

	st.plotly_chart(fig1, use_container_width=True)

with col2:
  # Creamos el histograma
  fig2 = px.histogram(
    df,
    x = 'detection_type',
    title = "<b>Distribución por Método de Detección</b>",
    labels = {'detection_type': ''},  # Eliminar etiqueta redundante
    color = 'detection_type',  # Color por categoría
    color_discrete_sequence = px.colors.qualitative.Prism  # Paleta profesional
  )
  fig2.update_traces(marker_line_width=1.5, marker_line_color="white")
  st.plotly_chart(fig2, use_container_width=True)


st.markdown("""---""")


############################ Filtro por año ###########################

# Extraemos los datos por año de descubrimiento para ver los registros
st.sidebar.header('Selecciona los filtros:')
years = sorted(df['year'].unique()) # obtenemos una lista ordenada de los años
selected_years = st.sidebar.multiselect(
	"Selecciona el año:",
	options = years,
	default = None,
)

df = df.drop(columns = ['discovered'])

# Lógica para manejar selección vacía en caso de que el user no la haga y si la hace se haga el filtrado de los datos
if not selected_years:
  filtered_df = df.copy() # muestra todos los datos
else:
  filtered_df = df[df['year'].isin(selected_years)] # filtra usando la selección del user

# Muestra el dataset filtrado
st.write(f"Datos para los años: {selected_years if selected_years else 'TODOS'}")
st.dataframe(filtered_df)

st.markdown("""---""")


############################ Filtro por Método de Detección ###########################

# Extraemos el método de detección
detection_type = df['detection_type'].unique()
selected_detection_type = st.sidebar.multiselect(
	"Selecciona el método de detección:",
	options = detection_type,
	default = None,
)

# Filtra el dataset
filtered_df = df[df['detection_type'].isin(selected_detection_type)]
st.write(f"Datos para el método de detección seleccionado: {selected_detection_type}")
st.dataframe(filtered_df)


############################ Gráfica de dispersión: Masa vs Radio ###########################

# Creamos la gráfica
fig3 = px.scatter(
	filtered_df, # usamos los datos filtrados por el user
	x = "mass",
	y = "radius",
	color = "detection_type",
	#size = "semi_major_axis",
	hover_data = ["name", "year"],
	title = "Radio vs Masa",
)

fig3.update_layout(xaxis_type = "log", xaxis_title = "Masa [M Júpiter]", yaxis_title = "Radio [R Júpiter]", legend_title_text = "Método de detección")
fig3.update_traces(marker = dict(opacity = 0.7, line_width = 0.5))


################## Gráfica de dispersión: Excentricidad vs Periodo Orbital ###################
fig4 = px.scatter(
	filtered_df, # usamos los datos filtrados
	x = "orbital_period",
	y = "eccentricity",
	color = "detection_type",
	hover_data = ["name", "year"],
	title = "Excentricidad vs Periodo Orbital",
)

fig4.update_layout(xaxis_type = "log", xaxis_title = "Periodo Orbital [días]", yaxis_title = "Excentricidad", legend_title_text = "Método de detección")
fig4.update_traces(marker = dict(opacity = 0.7, line_width = 0.5))

######################## Ajuste Gráficas #####################
one_column, two_column = st.columns(2)
one_column.plotly_chart(fig3, use_container_width = True)
two_column.plotly_chart(fig4, use_container_width = True)


####################### Gráfica de dispersión: Masa vs Periodo Orbital ###################

####################### Gráfica de dispersión: Radio vs Periodo Orbital ###################

# Configuración de columnas
c1, c2 = st.columns(2, gap = "large")  # 'gap' controla el espacio entre columnas

with c1:
  # Creamos la gráfica
	fig5 = px.scatter(
		filtered_df, # usamos los datos filtrados por el user
		x = "orbital_period",
		y = "mass",
		color = "detection_type",
		#size = "semi_major_axis",
		hover_data = ["name", "year"],
		title = "Masa vs Periodo Orbital",
	)

	fig5.update_layout(xaxis_type = "log", yaxis_type = "log", xaxis_title = "Periodo Orbital [días]", yaxis_title = "Masa [M Júpiter]", legend_title_text = "Método de detección")
	fig5.update_traces(marker = dict(opacity = 0.7, line_width = 0.5))
	st.plotly_chart(fig5, use_container_width=True, key="scatter_mass")

with c2:
  # Creamos la gráfica
	fig6 = px.scatter(
		filtered_df, # usamos los datos filtrados por el user
		x = "orbital_period",
		y = "radius",
		color = "detection_type",
		hover_data = ["name", "year"],
		title = "Radio vs Periodo Orbital"
	)

	fig6.update_layout(xaxis_type = "log", yaxis_type = "log", xaxis_title = "Periodo Orbital [días]", yaxis_title = "Radio [R Júpiter]", legend_title_text = "Método de detección")
	fig6.update_traces(marker = dict(opacity = 0.7, line_width = 0.5))
	st.plotly_chart(fig6, use_container_width=True, key="scatter_radius")

st.markdown("""---""")