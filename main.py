import pandas as pd
import numpy as np
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.plotting import figure
from os.path import dirname, join

# Permite leer la data 
data = pd.read_excel(join(dirname(__file__), "data/Listado.xls"),sheet_name=None)


#Ignorar la división de las hojas
dfinal1= pd.concat(data, ignore_index=True)

#Agrupa las filas que necesitamos en un una nueva tabla.
dfinal = dfinal1.groupby(['Provincia', 'Número de docentes','Número de estudiantes','Acceso (terrestre/ aéreo/fluvial)',
'Sostenimiento', 'Modalidad','Régimen Escolar','Nombre de la Institución Educativa']).size().reset_index()


#Realiza una contabilización de cada uno de los parametros para los selects.
provincias = dfinal1['Provincia'].value_counts()
modalidades = dfinal1['Modalidad'].value_counts()
acceso = dfinal1['Acceso (terrestre/ aéreo/fluvial)'].value_counts()
sostenimiento = dfinal1['Sostenimiento'].value_counts()


# Asignación de ejes
axis_map = {
    "Número de profesores": "Número de docentes",
    "Número de estudiantes": "Número de estudiantes",
 
}

#lista para la creacion de los sliders
docentes = dfinal['Número de docentes'].value_counts().keys().tolist()
es = dfinal['Número de estudiantes'].value_counts().keys().tolist()


#Lista de valores de las regiones 
regimen = dfinal['Régimen Escolar'].value_counts().keys().tolist()
regimen_sierra = (dfinal['Régimen Escolar']== 'SIERRA').sum()
regimen_costa = (dfinal['Régimen Escolar']== 'COSTA').sum()
regimen_oriente = (dfinal['Régimen Escolar']== 'ORIENTE').sum()
regimen_insular = (dfinal['Régimen Escolar']== 'INSULAR').sum()

#arreglo de los valores 
regiones = [regimen_costa, regimen_sierra,regimen_oriente,regimen_insular]


#Son las opciones que se pondra en el select para el cabio de grafico
opciones = {
    "Grafico de barras": "Grafico de barras",
    "Grafico de dispersion": "Grafico de dispersion",
}

#Parametros de cambio
docentes_slider = Slider(title="Número de profesores", value=0, start=min(docentes), end=max(docentes), step=10,bar_color="blue", name='docentes_slider')
estudiantes_slider = Slider(title="Número de estudiantes", value=0, start=min(es), end=max(es), step=10, name='estudiantes_slider' )
provincias_select = Select(title="Provincias", options=sorted(provincias.keys()), value="AZUAY" , name ='provincias_select')
modalidades_select = Select(title="Modalidades", options=sorted(modalidades.keys()), value="Presencial", name='modalidades_select')
acceso_select = Select(title="Acceso", options=sorted(acceso.keys()), value="Terrestre", name='acceso_select')
sostenimiento_select = Select(title="Sostenimiento", options=sorted(sostenimiento.keys()), value="Particular", name='sostenimiento_select')
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Número de profesores", name='x_axis')
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Número de estudiantes",name = 'y_axis')
graficos_select = Select(title="Opciones de gráficos", options=sorted(opciones.keys()), value="Grafico de dispersion", name='graficos_select')


controls = [docentes_slider, estudiantes_slider,provincias_select, modalidades_select, acceso_select, sostenimiento_select, x_axis, y_axis, graficos_select]
inputs = column(*controls, width=320)

 
# se crea un objeto que tiene un diccionario donde se inicializa los valores
source = ColumnDataSource(data=dict(x=[], y=[], color=[], escuela=[], provincia=[], nestudiantes=[], nombres=[] ))

# Esta informacion se muestra al pasar por uno de los puntos que se marcan en la grafica
TOOLTIPS=[
    ("Escuela", "@escuela"),
    ("Provincia", "@provincia"),
    ("Número de Estudiantes", "@nestudiantes")
]
#Define los colores de los puntos del grafico
dfinal["color"] = np.where(dfinal["Régimen Escolar"] == 'COSTA', "orange", "blue")

#Creación de la figura
p = figure(height=200, width=400, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None)



#Función para que funcione los select.
def select_escuelas():
    
    provincias_val = provincias_select.value
    modalidades_val = modalidades_select.value
    acceso_val = acceso_select.value
    sostenimiento_val = sostenimiento_select.value
    
    
    selected = dfinal[
        (dfinal['Número de docentes'] >= docentes_slider.value) &
        (dfinal['Número de estudiantes'] >= estudiantes_slider.value) &
        (dfinal['Provincia'] == provincias_val) &
        (dfinal['Modalidad'] == modalidades_val) &
        (dfinal['Acceso (terrestre/ aéreo/fluvial)'] == acceso_val) &
        (dfinal['Sostenimiento'] == sostenimiento_val)
    
    ]
    return selected
    

def select_grafico():

    grafico_val = graficos_select.value
    curdoc().clear()
    if (grafico_val ==  "Grafico de barras"):
     print('barras')
     curdoc().add_root(m)
    else:
     print('dispersion')
     curdoc().add_root(l)


TOOLTIPS1=[
    ("Regimen", "@y"),
    ("Escuelas", "@rigth")
]

data_list = ColumnDataSource(data=dict(rigth=[], y=[]))

plats = (regimen)
values = (regiones)
platform = figure(height=250, toolbar_location=None, outline_line_color=None, tooltips=TOOLTIPS1,sizing_mode="scale_both", name="platform",
                  y_range=list(reversed(plats)), x_axis_location="above")
platform.x_range.start = 1
platform.ygrid.grid_line_color = None
platform.axis.minor_tick_line_color = None
platform.outline_line_color = None


platform.hbar(left=0, right= "rigth", y="y", height=0.8, source=data_list)



def update():
    df=select_escuelas()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d Escuelas seleccionadas" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        escuela=df["Nombre de la Institución Educativa"],
        provincia=df["Provincia"],
        nestudiantes=df["Número de estudiantes"],
    )
   
    regimen_sierra = (df['Régimen Escolar']== 'SIERRA').sum()
    regimen_costa = (df['Régimen Escolar']== 'COSTA').sum()
    regimen_oriente = (df['Régimen Escolar']== 'ORIENTE').sum()
    regimen_insular = (df['Régimen Escolar']== 'INSULAR').sum()  
    regiones = [regimen_costa, regimen_sierra,regimen_oriente,regimen_insular]
    data_list.data = {
         'rigth' :regiones,
         'y' :regimen
    

    }
# nuevo metodo
for control in controls:
    if (control.name == 'graficos_select'):
      control.on_change('value', lambda attr, old, new: select_grafico())
    else:
      control.on_change('value', lambda attr, old, new: update())
   

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

l = column(desc, row(inputs, p), sizing_mode="scale_both" )
m = column(desc, row(inputs, platform), sizing_mode="scale_both" )


update()  # initial load of the data

curdoc().add_root(l)