
from bokeh.io import output_file, show
import pandas as pd
import numpy as np
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.plotting import figure
from os.path import dirname, join

#output_file("stacked2.html")
data = pd.read_excel(join(dirname(__file__), "Listado.xls"),sheet_name=None)


data.keys()

dfinal1= pd.concat(data, ignore_index=True)

dfinal = dfinal1.groupby(['Provincia', 'Número de docentes','Número de estudiantes','Acceso (terrestre/ aéreo/fluvial)','Sostenimiento', 'Modalidad','Régimen Escolar','Nombre de la Institución Educativa']).size().reset_index()

dfinal["color"] = np.where(dfinal["Régimen Escolar"] == 'SIERRA', "orange", "grey")
dfinal["color"] = np.where(dfinal["Régimen Escolar"] == 'COSTA', "purple", "grey")



provincias = dfinal1['Provincia'].value_counts()
profesores = dfinal1['Número de docentes'].value_counts()
estudiantes = dfinal1['Número de estudiantes'].value_counts()
modalidades = dfinal1['Modalidad'].value_counts()
acceso = dfinal1['Acceso (terrestre/ aéreo/fluvial)'].value_counts()
sostenimiento = dfinal1['Sostenimiento'].value_counts()





axis_map = {
    "Número de profesores": "Número de docentes",
    "Número de estudiantes": "Número de estudiantes",
 
}

docentes = dfinal['Número de docentes'].value_counts().keys().tolist()

docentes_slider = Slider(title="Número de profesores", value=80, start=min(docentes), end=max(docentes), step=10)
estudiantes_slider = Slider(title="Número de estudiantes", value=80, start=estudiantes.min(), end=estudiantes.max(), step=10)
provincias_select = Select(title="Provincias", options=sorted(provincias.keys()), value="AZUAY")
modalidades_select = Select(title="Modalidades", options=sorted(modalidades.keys()), value="A Distancia")
acceso_select = Select(title="Acceso", options=sorted(acceso.keys()), value="Aérea")
sostenimiento_select = Select(title="Sostenimiento", options=sorted(sostenimiento.keys()), value="Fiscal")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Número de profesores")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Número de estudiantes")





controls = [docentes_slider, estudiantes_slider,provincias_select, modalidades_select, acceso_select, sostenimiento_select, x_axis, y_axis]
inputs = column(*controls, width=320)

#
source = ColumnDataSource(data=dict(x=[], y=[], color=[], escuela=[], provincia=[], nestudiantes=[]))

TOOLTIPS=[
    ("Escuela", "@escuela"),
    ("Provincia", "@provincia"),
    ("Número de Estudiantes", "@nestudiantes")
]

p = figure(height=400, width=500, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None)


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

for control in controls:
    control.on_change('value', lambda attr, old, new: update())



#l = row(inputs, p)

l = row(inputs, p)

update()  # initial load of the data


curdoc().add_root(l)