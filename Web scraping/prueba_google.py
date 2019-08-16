# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 11:23:45 2019

@author: juan.salgado
"""

from requests import get
from googlesearch import search
from bs4 import BeautifulSoup as soup
# import requests
import pandas as pd
import time
import re
from IPython.core.display import clear_output
from random import randint

# 'for' para cambiar el año, desde 'inicio' a 'fin',
# y buscar 'num_art_buscar' resultados de google

num_art_buscar = 1
inicio = 2010
fin = 2018
count = 0
start_time = time.time()
palabras = ['homicidios', 'muerte']

# Creacion de vectores para llenar con la informacion del scraping
titles = []
links = []
contents = []
dates = []
urls = []
pal_buscada = []
urls_concat = []


# loop para iterar por distintas palabtas
for pal in palabras:
    # loop para buscar 'pal' dentro de los años 'inicio' y 'fin'
    for year in range(inicio, fin+1):
        a_buscar = "site:https://www.publimetro.co/co/ " + pal + " before:" + str(year) + \
        "-12-31 after:" + str(year) + "-1-01"
        # Busqueda urls en google search
        for url in search(a_buscar, stop = num_art_buscar):
            # 'if' para eliminar duplicados respecto al url
            if url in urls:
                next
            urls.append(url)
            urls_concat.append(url + pal + str(year))
        
        print('Total urls: ', len(urls), 'Año: ', year)
        print('')
        requests = 0
            
        for url in urls:
        
            # Extraccion del codigo html de cada url
            link = ''
            while link == '':
                try:
                    link = get(url)
                    break
                except:
                    print("Connection refused by the server")
                    time.sleep(3)
                    print("Let's try again...")
                    continue
            linksoup = soup(link.content,'html5lib')
            time.sleep(randint(2,4))
            requests += 1
            elapsed_time = time.time() - start_time
            print('Articulo: {} de año {}; Total time: {} min'.format(requests, year, 
                  round(elapsed_time/60, 3)))
            print("")
            clear_output(wait = True) 
            print(url)
            print("")
            count += 1
            print('Total articulos', count)
            print("")
            
            # Extraccion del titulo
            titulo = linksoup.find_all('h1', attrs = {'class':'article-title'})
            for tit in titulo:
                title = tit.text
                
            # Extraccion de fecha
            # Se hace de dos formas: 'try': la extrae desde el link; 'except' desde el articulo mismo
            try:
                date = re.search("[0-9]+/[0-9]+/[0-9]+", url).group(0)
                
            except:
                fecha = linksoup.find_all('time', attrs = {'class':''})
                # Este 'if': Hay pags que tienen varias categorias 'time'. Segun el caso, se extrae la fecha
                # de dos formas. De lo contrario, se llena con '**Especial**'
                if len(fecha) == 1:
                    for fe in fecha:
                        date = fe.text
                    # 'if' porque hay fechas que no están registradas
                    if 'none' in date:
                        date = '**Especial**'
                    else:
                        # Extrayendo la fecha correcta [sin la hora]
                        date = re.search("\n(.*),", date).group(1)
                else:
                    date = fecha[0].getText()
                    if 'none' in date:
                        date = '**Especial**'
                    else:
                        date = re.search("\n(.*),", date).group(1)
                
            # Extracción del texto del articulo
            articulo_total = linksoup.find('div', attrs = {'class':'resumen'})
            articulo_txt = articulo_total.find_all('p')
            texto = ''
            for i in range(len(articulo_txt)):
                texto = texto + " " + articulo_txt[i].getText()
            
            # Si no encontro titulo, fecha, o texto: poner 'especial'
            if not title:
                title = '**Especial**'
            if not date:
                date = '**Especial**'
            if not texto:
                texto = '**Especial**'
                
            # Llenar vectores de variables
            
            titles.append(title)
            dates.append(date)
            contents.append(texto)
            links.append(url)
            pal_buscada.append(pal)
            test_df=pd.DataFrame({'Titulo':titles,
                          'Fecha':dates,
                          'Contenido':contents,
                          'Link':links,
                          'Palabra buscada':pal_buscada})

# Guardar una base para todas las palabras        
test_df.to_excel("Publimetro_" + str(inicio) + '-' + str(fin) + "total.xlsx")

print('\nTotal articulos: {} \nNumero de años: {} \nArticulos por año: {} \nTotal time: {} min'
      .format(count,
              fin + 1 - inicio,
              round(count/(fin + 1 - inicio), 3),
              round(elapsed_time/60, 3),
              round(requests/elapsed_time, 3)))
