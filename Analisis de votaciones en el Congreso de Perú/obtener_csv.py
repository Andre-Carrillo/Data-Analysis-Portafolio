# Haremos un análisis de las votaciones de los congresistas, el objetivo es este: 
# tener una base de datos con los congresistas, su distrito electoral, su agrupación 
# política y su bancada y las comisiones en las que está 
#
# |NOMBRE            |DISTRITO ELECTORAL     |BANCADA            |AGRUPACIÓN POLÍTICA    |COMISIONES         |
#
# Luego haremos una tabla con los votos de cada congresista
# |ID CONGRESISTA    | VOTO 1       | VOTO 2        | VOTO 3        | ...

import requests
import lxml.html as html
import numpy as np
import pandas as pd


from pdfinterpreter import pdf_to_vote_df

XPATH_LIST_CONGRESSMEN = '//a[@class="conginfo"]/text()'
XPATH_LIST_URLCONGINFO = '//a[@class="conginfo"]/@href'


URLCONGRESSMEN = 'https://www.congreso.gob.pe/pleno/congresistas/'

def parse_home():
    try:
       response = requests.get(URLCONGRESSMEN, verify=False)
       if response.status_code == 200:
          home = response.content.decode('utf-8')
          parsed = html.fromstring(home)
          LIST_CONGRESSMEN = parsed.xpath(XPATH_LIST_CONGRESSMEN)
          LIST_URLCONGINFO = parsed.xpath(XPATH_LIST_URLCONGINFO)
       else:
          raise ValueError
    except ValueError as ve:
        print(ve)
        pass
parse_home()
#LIST_CONGRESSMEN

response = requests.get(URLCONGRESSMEN, verify=False)

response.status_code
home = response.content.decode('utf-8')
parsed = html.fromstring(home)
LIST_CONGRESSMEN = parsed.xpath(XPATH_LIST_CONGRESSMEN)
LIST_URLCONGINFO = parsed.xpath(XPATH_LIST_URLCONGINFO)
print(LIST_CONGRESSMEN)
print(LIST_URLCONGINFO)

LIST_REGIONES = []
XPATH_REPRESENT = '//p[@class="representa"]/span[@class="value"]/text()'

LIST_BANCADAS = []
XPATH_BANCADA = '//p[@class="bancada"]/span[@class="value"]/text()'

LIST_GRUPO_POLITICO = []
XPATH_GRUPO_POLITICO = '//p[@class="grupo"]/span[@class="value"]/text()'

LIST_VOTACION = []
XPATH_VOTACION = '//p[@class="votacion"]/span[@class="value"]/text()'

for i in LIST_URLCONGINFO:
  temp_response = requests.get(URLCONGRESSMEN+i, verify=False)
  temp_home = temp_response.content.decode('utf-8')
  temp_parsed = html.fromstring(temp_home)
  LIST_REGIONES.append(temp_parsed.xpath(XPATH_REPRESENT))
  LIST_BANCADAS.append(temp_parsed.xpath(XPATH_BANCADA))
  LIST_GRUPO_POLITICO.append(temp_parsed.xpath(XPATH_GRUPO_POLITICO))
  LIST_VOTACION.append(temp_parsed.xpath(XPATH_VOTACION))

Congress = pd.DataFrame({"Congresista":LIST_CONGRESSMEN, 
                            "Región":[i[0] for i in LIST_REGIONES],
                            "Bancada":[i[0] for i in LIST_BANCADAS],
                            "Grupo":[i[0] for i in LIST_GRUPO_POLITICO],
                            "Votacion":[i[0] for i in LIST_VOTACION]})

Congress.to_csv("Congreso.csv")

