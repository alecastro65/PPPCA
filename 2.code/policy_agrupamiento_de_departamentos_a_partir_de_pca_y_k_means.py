# -*- coding: utf-8 -*-
"""Policy - Agrupamiento de departamentos a partir de PCA y K-means

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xTsGyvoh2TqP-tEuExK0X65m49koAH2i

# **Métodos de Machine Learning no supervisado: Análisis de Política Pública usando PCA y k-means clustering.**

---

##**Contexto:**

En este proyecto, voy a intentar conducir un análisis de política pública utilizando Análisis de Componentes Principales (PCA) y k-means clustering, con el objetivo de tener un mejor entendimiento de las principales brechas en el desarrollo socio-económico de los 32 departamentos de Colombia. 

Mediante la aplicación de PCA en 15 indicadores socio-económicos, espero reducir redundancias y eliminar problemas de correlación y multicolinealidad para destacar patrones que no son aparentes en un análisis tradicional. 


Una vez aplicada la reducción a los componentes principales, el objetivo es determinar si existen clusters de departamentos que requieran mayor atención en cuanto a la asignación de recursos y ayudas estatales, y en que areas se necesita más dicha asignación.

Estos resultados podrían dar luz sobre una mejora en la distribución de recursos para el desarrollo de la salud, educación y bienestar en las regiones.

##Importación de dependencias
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import plotly.express as px
from sklearn.metrics import silhouette_score        
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objs as pgo
import os
from pyhere import here

print("hola")
print(here())

"""
Adquisición y exploración de los Datos

Las columnas 2-13 son tomadas del ‘Anexo de metadatos por departamentos’ de la Encuesta nacional de calidad de vida (ECV) 2019. 
*   “(...)Estas investigaciones cuantifican y caracterizan las condiciones de vida de los colombianos incluyendo variables relacionadas con la vivienda (tenencia, acceso a servicios públicos) , las personas (salud, educación, seguridad social) y los hogares (jefatura del hogar, hijos menores de edad, género). ”
La columna 14 se tomó del estudio de Pobreza Multidimensional en Colombia 2019 y 2018, y la columna 15 , del Informe de Cuentas Nacionales Departamentales 2019.
"""
"""
#**lista de variables:**
Departamento:```
 Nombre del departamento
```hog_acued:``` Número de hogares con acceso a acueducto
```hog_alcan:``` Número de hogares con acceso a alcantarillado
```hog_elect:``` Número de hogares con acceso a energía electrica
```afi_seg_soc:``` Población afiliada al Sistema general de Seg. Social en el régimen contributivo.
```asist_educacion```: Porcentaje de personas mayores de 6 años que asisten al sistema educativo.
```acc_internet```: Porcentaje de hogares con acceso a internet.
```jef_hogar_mujer```: Hogares con hijos menores de 18 años, con jefe de hogar mujer, sin conyuge.
```viv_propia```: Hogares con vivienda propia totalmente pagada
```porc_pens```: Porcentaje de población mayor de 60 años que cuenta con una pensión.
```elim_exc:``` Porcentaje de hogares que realizan Eliminación de excretas hacia la red de alcantarillado.
```perc_pob:``` Hogares en los que el jefe se considera pobre.
```ipm:``` Índice de pobreza multimodal (2019)
```var_pib_porc```: Porcentaje de variación del PIB departamental 2018-19.
"""

#dataset = pd.read_excel('/content/drive/My Drive/datasets/ecv_colombia.xlsx')
dataset_path = here("1.data\ecv_colombia.xlsx")
print(dataset_path)
dataset = pd.read_excel(dataset_path)


dataset.info()

"""## Tratamiento de índice y valores nulos

Utilizaremos la columna "Departamento" como índice del dataset. Adicional a ello, eliminaremos cualquier fila que contenga valores invalidos (Caracteres en blanco al final de los datos)
"""

dataset.set_index("Departamento", inplace=True)
dataset.dropna(inplace=True)

"""##Análisis de correlación"""

#generamos un mapa de calor de acuerdo a la matríz de correlaciones
sns.heatmap(dataset.corr())

"""Visualmente se aprecia una altísima correlación entre las variables de nuestro estudio. Por esta razón, vamos a aplicar la técnica de análisis de componentes principales (PCA). Esto nos permite "reducir" las variables que están correlacionadas mediante una transformación lineal, manteniendo una "cantidad" suficiente de la varianza explicativa de los datos originales.

##Normalización

Para correr PCA de una manera adecuada, tenemos que asegurarnos de que todas las mediciones se encuentren en la misma escala. Para esto usamos el método ```StandardScaler()``` de la librería **Scikitlearn**
"""

sc_x = StandardScaler()
sc_x.fit(dataset.values)
dataset_scaled = sc_x.transform(dataset.values)

"""# Reducción dimensional mediante PCA:

##Número de componentes

Inicialmente, aplicaremos PCA sobre los datos normalizados sin especificar la cantidad de componentes principales que vamos a utilizar. Esto con el objetivo de poder seleccionar un número óptimo de componentes.
"""

pca = PCA() 
components = pca.fit_transform(dataset_scaled)
components_df = pd.DataFrame(data = components)#Convierto 'components_df' a un dataframe de pandas
                                               #para facilitar el trabajo con plotly express

exp_var_cumul = np.cumsum(pca.explained_variance_ratio_)#Guardamos el acumulado de las varianzas explicativas para graficar.

fig0 = px.area(
    x=range(1, exp_var_cumul.shape[0] + 1),
    y=exp_var_cumul,
    labels={"x": "# Componentes", "y": "Varianza Explicada"},)
fig0.add_annotation(x=6, y=0.94,
            text="Componentes Óptimos",
            showarrow=True,
            arrowhead=2)
fig0

"""La gráfica de la varianza explicada acumulada nos muestra que a partir de 6 componentes, nuestros datos 'reducidos' explican el 94% de la varianza. De allí en adelante, los aumentos en la varianza explicada son marginales. Así que definirémos nuestro numero de componentes principales en 6"""

pca = PCA(n_components=6) #Volvemos a correr PCA con los componentes definidos arriba.
components = pca.fit_transform(dataset_scaled)
components_df = pd.DataFrame(data = components)

"""Al graficar nuevamente la matríz de correlación sobre los datos reducidos a sus principales componentes, podemos ver que la autocorrelación se ha reducido a su mínima expresión."""

sns.heatmap(components_df.corr())

"""##Ubicación de las observaciones en los principales componentes

Ahora procedemos a visualizar la dispersión de los distintos departamentos en un espacio bi-dimensional conformado por los 2 componentes principales.
"""

fig1 = px.scatter(components, x=0, y=1, text=dataset.index)
fig1.update_traces(textposition='top center')
fig1.update_layout(
    height=700,
    width=900,
    title_text='Ubicación de los Departamentos en el espacio de los dos componentes principales')
fig1.show()

"""Visualmente podemos identificar evidencias de agrupamiento. Vamos a correr el algoritmo K-Means para confirmar.

#Aplicación de K-means

##Determinación del numero de clusters para K-Means

Inicialmente vamos a correr K-means con valores de k desde 2 hasta 10. A la vez que guardamos los valores de la inercia, para luego determinar el valor adecuado de clusters.
"""

sum_of_squared_distances = []
K = range(2,10)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(components)
    sum_of_squared_distances.append(km.inertia_)

fig2 = px.line(x=K, y=sum_of_squared_distances, title= "K (# de Clusters) vs Inercia",                  
               labels={
                     "x": "K clusters",
                     "y": "Inercia",
                     
                 },)
fig2.show()

"""Siguiendo el método visual de 'codo', utilizaremos 4 clusters

# K-Means con 4 clusters
"""

km = KMeans(n_clusters = 4)
km.fit(components)
cluster = km.predict(components)
cluster_discret = cluster.astype(str) #facilita la visualización en plx

pd.Series(cluster).value_counts()

cluster.shape

fig3 = px.scatter(components, x=0, y=1, color=cluster_discret,  text=dataset.index)
fig3.update_traces(textposition='top center')
fig3.update_layout(
    height=700,
    width=900,
    title_text='Ubicación de los Departamentos en el espacio de los dos componentes principales'
)



fig3.show()

"""En la figura anterior podemos ver los distintos departamentos coloreados según el cluster en el que fueron clasificados. Una inferencia interesante es que los departamentos no están necesariamente agrupados de acuerdo a su ubicación geográfica.

#Análisis descriptivo de los clusters
"""

cluster_map = pd.DataFrame()
cluster_map['data_index'] = dataset.index.values
cluster_map['cluster'] = km.labels_
cluster_map[cluster_map.cluster == 0]

cluster_map[cluster_map.cluster == 1]

cluster_map[cluster_map.cluster == 2]

cluster_map[cluster_map.cluster == 3]

"""##Indice de pobreza multimodal por cluster"""

fig4 = px.scatter(dataset, x=cluster, y=dataset.ipm, color=cluster_discret,  hover_data=[dataset.index], size='ipm'
                  )

fig4.update_layout(
    height=800,
    width=1000,
    title_text='Indice de pobreza multimodal por cluster')
fig4.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    )
)

"""La Fig.5 muestra que el cluster 0 (azul) tiene -en general- los mayores valores en el índice de pobreza multimpodal, sin embargo, todos los clusters parecen ubicarse en su mayoría por debajo de 40 puntos, a excepción de Vichada y Vaupés, que tienen valores extremadamente altos.

##Acceso a acueducto público por cluster
"""

fig5 = px.scatter(dataset, x=cluster, y=dataset.hog_acued, color=cluster_discret,  hover_data=[dataset.index], size='hog_acued')


fig5.update_layout(
    height=850,
    width=1000,
    title_text='Acceso a acueducto público por cluster')
fig5.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    )
)

"""##Población con acceso a internet por cluster"""

fig6 = px.scatter(dataset, x=cluster, y=dataset.acc_internet, color=cluster_discret,  hover_data=[dataset.index], size='acc_internet')

fig6.update_layout(
    height=800,
    width=1000,
    title_text='Población con acceso a internet por cluster')
fig6.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    )
)

"""##Población que cursa o logró acceder a la educación superior"""

fig7 = px.scatter(dataset, x=cluster, y=dataset.edu_sup, color=cluster_discret,  hover_data=[dataset.index], size='edu_sup')

fig7.update_layout(
    height=800,
    width=1000,
    title_text='Acceso a educación superior')
fig7.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    )
)

"""##Población afiliada como cotizante a Seguridad social por cluster"""

fig8 = px.scatter(dataset, x=cluster, y=dataset.afi_seg_soc, color=cluster_discret,  hover_data=[dataset.index], size='afi_seg_soc')

fig8.update_layout(
    height=800,
    width=1000,
    title_text='Población afiliada como cotizante a S.S por cluster')
fig8.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    )
)
fig8

"""#Conclusiones

La teoría económica tradicional muestra debilidades en los análisis multivariados, en especial cuando se aplican sobre indicadores con altos niveles de correlación, como lo son los indicadores socioeconómicos (por ejemplo, un acceso deficiente al agua potable estará relacionado con una mala calidad alimenticia). En este sentido, el análisis por componentes principales se muestra especialmente útil para lidiar con series de datos con muchas dimensiones.
Con un mejor entendimiento sobre como los indicadores económicos utilizados varían entre los 32 departamentos, nos es posible identificar que cluster de departamentos demanda mayor asistencia gubernamental. Por ejemplo, si quisieramos identificar en que lugar es necesaria una política de inversión en infraestructura de comunicaciones, o acueducto y alcantarillado, nos centraríamos en el cluster 0. Este analisis es muy útil para identificar en que departamentos se deben priorizar las distintas políticas públicas de desarrollo socio-económico, e incluso, es posible utilizar el mísmo método sobre municipios y entidades territoriales de menor tamaño para lograr mayor especificidad en la identificación y corrección de deficiencias de orden socio-económico.
"""