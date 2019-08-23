# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
import re
from IPython.core.display import clear_output
from random import randint

## %reset

keywords = ['homicidios', 'muerte']


titles = []
links = []
contents = []
dates = []
pal_buscada_tot  = []
loop_page_tot = []


start_time = time.time()
requests = 0
count = 0
pages = [str(i) for i in range(0,5)]

for keyword in keywords:
    for page in pages:
    
        url = "http://www.qhubo.com/page/" + page + "/?s=" + keyword
        html = get(url)
        htmlsoup = soup(html.content,'html5lib')
        time.sleep(randint(2,4))
        requests += 1
        elapsed_time = time.time() - start_time
        print('Request: {}; Total time: {} min; Frequency: {} requests/s'.format(requests,
              round(elapsed_time/60, 3), round(requests/elapsed_time, 3)))
        print("")
        clear_output(wait = True)
       
       
        print(url)
        print("")
       
        articles = htmlsoup.find_all('div', attrs = {'class':'titulo'})
       
       
        if len(articles) != 0:
               
            for oneArticle in articles:
               
                link = oneArticle.a['href']
                #if 'bogota' not in link:
                 #   continue
               
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
                test_df=pd.DataFrame({'Titulo':titles,
                              'Fecha':dates,
                              'Contenido':contents,
                              'Link':links,
                              'Palabra buscada':pal_buscada_tot,
                              'Pagina buscada':loop_page_tot})
               
        ## Este Else hace parte del if: len(articles) != 0. Significa que en el url [var] no se 
        ## encontraron secciones con la categoria: 'div', attrs = {'class':'titulo'}
            ## Se vuelve a llenar el DF con los vectores llenos del contenido de los articulos
               
        else:
            test_df=pd.DataFrame({'Titulo':titles,
                          'Fecha':dates,
                          'Contenido':contents,
                          'Link':links,
                          'Palabra buscada':pal_buscada_tot,
                          'Pagina buscada':loop_page_tot})
            print("There were no more articles found with your keyword")
            break
    

test_df.to_excel("Qhubo_total.xlsx")

elapsed_time_2 = time.time() - start_time


print('\nTotal articulos: {} \nNumero de paginas: {} \nArticulos por pagina: {} \nTotal time: {} min'
      .format(len(links),
              len(pages),
              round(len(links)/len(pages), 3),
              round(elapsed_time_2/60, 3)))
    