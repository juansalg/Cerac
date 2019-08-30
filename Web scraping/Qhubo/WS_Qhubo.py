# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
import re
from IPython.core.display import clear_output
from random import randint
import smtplib, ssl

## %reset

keywords = ['Seguridad bogotá','Homicidio bogotá','Hurto bogotá','Vandalismo bogotá',
            'Policía de Bogotá','Inseguridad bogotá','Percepción de seguridad bogotá',
            'Percepción de inseguridad bogotá','Seguridad ciudadana bogotá',
            'Orden público bogotá','Violencia bogotá','Asesinato bogotá','Matar bogotá',
            'Robo bogotá','Atraco bogotá','Fleteo bogotá','Orden público bogotá',
            'Disturbio bogotá','Riña bogotá','Abuso sexual bogotá','Acoso sexual bogotá',
         'Acoso infantil bogotá','Golpiza bogotá','Linchamiento bogotá',
         'Policía Nacional bogotá','Dar de baja bogotá',
         'Violencia sexual bogotá', 'Lesiones personales bogotá']


titles = []
links = []
contents = []
dates = []
pal_buscada_tot  = []
loop_page_tot = []
link_err = []
inicio = 2010
fin = 2018
years = range(inicio,fin+1)


start_time = time.time()
requests = 0
count = 0
pages = [str(i) for i in range(1,5500)]

for keyword in keywords:
    
    for page in pages:
    
        url = "http://www.qhubo.com/page/" + page + "/?s=" + keyword
        html = get(url)
        htmlsoup = soup(html.content,'html5lib')
        time.sleep(randint(2,4))
        requests += 1
        elapsed_time = time.time() - start_time
        print("")
        print('Palabra: {}; Página: {}; Tiempo: {} min'.format(keyword, page,
                                                                  round(elapsed_time/60,3)))
        print("")
        clear_output(wait = True)
       
       
        print(url)
        print("")
       
        articles = htmlsoup.find_all('div', attrs = {'class':'titulo'})
       
       
        if articles:
               
            for oneArticle in articles:
               
                link = oneArticle.a['href']
                if link in links:
                    continue
               
                title = oneArticle.a.text
                content = ''
                html2 = ''
        
                while html2 == '':
                    try:
                        html2 = get(link)
                        break
                    except:
                        print("Connection refused by the server")
                        time.sleep(3)
                        print("Let's try again...")
                        continue
                    
                try:
                       
                    noodles = soup(html2.content,'html5lib')
                    #if 'field field-name-body' not in noodles:
                     #   print(link)
                      #  print("")
                       # continue
                    print(link)
                    count = count + 1
                    print(count)
                    print("")
                    
                    date =  noodles.find("div", class_="meta")
               
                    if  date == None:
                        date = "**Unspecified**"
                    else:
                        ## Modificando fecha
                        date1 = str(date)
                        date = re.search("\t(.*)<", date1).group(1)
                    
                    ## While para descartar fechas fuera del rango
                    fecha_en_rango = False
                    i = 0
                    while fecha_en_rango == False and i < len(years):
                        if str(years[i]) in date:
                            fecha_en_rango = True
                        i += 1 
                    if fecha_en_rango == False:
                        continue                    
                    
                    ## No se descartan palabras que no tengan 'bogot' porque en la mayoría de
                    ## artículos no sale 'bogot', asi sean de bogota.
                   
                    content = noodles.find_all(attrs = {'style':'text-align: justify;'})
                    texto = ''
                    i = 0
                    
                    ## Extraccion del texto. Diferentes casos:
                        
                        ## Caso 1: content vacio [no atributos en html > style = text-align: justify;]
                            ## El while es para buscar todos los parrafos, antes del primer pararfo con
                            ## espacio (el parrafo sin texto que separa el articulo de las etiquetas)
                            
                    """ Quizas modificar este if para que salgan los "p" que no tengan espacio en
                    "p+1", pero que si tengan etiqueta: http://www.qhubo.com/17470-2/
                    """
                    
                    if not content:
                        content2 = noodles.find_all("p")
                        while content2[i].getText() != '\xa0':
                            texto = texto + " " + content2[i].getText()
                            i = i+1
                            if i == len(content2):
                                break
                            
                          ## Caso 2: content no vacio [si atributos en html > style = text-align: justify;]
                              ## El while es para buscar todos los parrafos antes del primer pararfo con
                              ## espacio (el parrafo sin texto que separa el articulo de las etiquetas)
                            
                    else:
                        while content[i].getText() != '\xa0':
                            texto = texto + " " + content[i].getText()
                            i = i+1
                            if i == len(content):
                                break
                        
                    ## Si texto llega a quedar vacio: "**Texto especial**"
        
                    if not texto:
                        texto = "**Texto especial**"
                        
                    ## Relleno del dataframe con la info. extraida
                            
                    titles.append(title)
                    dates.append(date)
                    contents.append(texto)
                    links.append(link)
                    pal_buscada_tot.append(keyword)
                    loop_page_tot.append(page)


                except:
                    link_err.append(link)  
               
        ## Este Else hace parte del if: len(articles) != 0. Significa que en el url [var] no se 
        ## encontraron secciones con la categoria: 'div', attrs = {'class':'titulo'}
            ## Se vuelve a llenar el DF con los vectores llenos del contenido de los articulos
               
        else:
            print("There were no more articles found with your keyword")
            break


test_df=pd.DataFrame({'Titulo':titles,
          'Fecha':dates,
          'Contenido':contents,
          'Link':links,
          'Palabra buscada':pal_buscada_tot,
          'Pagina buscada':loop_page_tot})
    
errores = pd.DataFrame(
                {'Link error':link_err}
                )
    

test_df.to_excel("Qhubo_total.xlsx")
errores.to_excel("Qhubo_errores.xlsx")


elapsed_time_2 = time.time() - start_time


print('\nTotal articulos: {} \nNumero de paginas: {} \nArticulos por pagina: {} \nTotal time: {} min'
      .format(len(links),
              len(pages),
              round(len(links)/len(pages), 3),
              round(elapsed_time_2/60, 3)))

## Enviar correo
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "python.development.cerac@gmail.com"  # Enter your address
receiver_email = "juan.salgado@cerac.org.co"  # Enter receiver address
password = 'Cerac_2019'

message = """Subject: Finalizo WS de El espectador


Tiempo total: """ + str(round(elapsed_time_2/60, 3)) + "min" \
\
"""\n\nTotal articulos: """ + str(len(links)) + \
\
"""\n\nTotal paginas: """ + str(requests) + \
\
"""\n\nTotal errores: """ + str(len(errores))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)  