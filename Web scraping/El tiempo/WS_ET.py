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
import smtplib, ssl

# 'for' para cambiar el año, desde 'inicio' a 'fin',
# y buscar 'num_art_buscar' resultados de google

num_art_buscar = 50
inicio = 2016
fin = 2018
count = 0
start_time = time.time()
palabras = ['homic', 'muerte', 'asesinato']

# Creacion de vectores para llenar con la informacion del scraping
titles_tot = []
links_tot  = []
contents_tot  = []
dates_tot  = []
urls_tot  = []
pal_buscada_tot  = []
loop_anio_tot = []
link_err = []

# loop para iterar por distintas palabtas
for pal in palabras:
    
    # loop para buscar 'pal' dentro de los años 'inicio' y 'fin'
    for year in range(inicio, fin+1):
        
        # Se crean los vectores acá porque cada anio la búsqueda de urls cambia
        titles = []
        links = []
        contents = []
        dates = []
        urls = []
        pal_buscada = []
        loop_anio = []
        
        year = 2018
        a_buscar = "site:https://www.eltiempo.com/ homicidio before:" + str(year) + \
        "-12-31 after:" + str(year) + "-1-01"
        # Busqueda urls en google search
        for url in search(a_buscar, stop = num_art_buscar):
            # 'if' para eliminar duplicados respecto al url
            if url in urls_tot:
                next
            urls.append(url)
            urls_tot.append(url)
        
        print('Total urls: ', len(urls), 'Año: ', year)
        print('')
        requests = 0
            
        for url in urls:
            
            try:
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
                elapsed_time_1 = time.time() - start_time
                print('Articulo: {} de año {}; Total time: {} min'.format(requests, year, 
                      round(elapsed_time_1/60, 3)))
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
                loop_anio .append(year)
                test_df=pd.DataFrame({'Titulo':titles,
                              'Fecha':dates,
                              'Contenido':contents,
                              'Link':links,
                              'Palabra buscada':pal_buscada,
                              'Año buscado':loop_anio})
            
            except:
                link_err.append(url)

        ## Dataframe con toda la informacion
        titles_tot.extend(titles)
        dates_tot.extend(dates)
        contents_tot.extend(contents)
        links_tot.extend(links)
        pal_buscada_tot.extend(pal_buscada)
        loop_anio_tot.extend(loop_anio)
        test_df_tot=pd.DataFrame({'Titulo':titles_tot,
                      'Fecha':dates_tot,
                      'Contenido':contents_tot,
                      'Link':links_tot,
                      'Palabra buscada':pal_buscada_tot,
                      'Año buscado':loop_anio_tot})
    
        ## Dataframe de los errores
        errores = pd.DataFrame(
                {'Link error':link_err}
                )
        

# Guardar una base para todas las palabras        
test_df_tot.to_excel("Publimetro_" + str(inicio) + '_' + str(fin) + "_total.xlsx")
errores.to_excel("Publimetro_errores.xlsx")

elapsed_time = time.time() - start_time


print('\nTotal articulos: {} \nNumero de años: {} \nArticulos por año: {} \nTotal time: {} min'
      .format(len(links_tot),
              fin + 1 - inicio,
              round(len(links_tot)/(fin + 1 - inicio), 3),
              round(elapsed_time/60, 3)))

## Enviar correo
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "python.development.cerac@gmail.com"  # Enter your address
receiver_email = "juan.salgado@cerac.org.co"  # Enter receiver address
password = 'Cerac_2019'
message = """Subject: Finalizo WS de Publimetro


Tiempo total: """ + str(round(elapsed_time/60, 3)) + "min" \
\
"""\n\nTotal articulos: """ + str(len(links_tot)) + \
\
"""\n\nTotal errores: """ + str(len(errores))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
