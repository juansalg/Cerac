# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:00:34 2019

@author: JCSR
"""

from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
import re
from IPython.core.display import clear_output
from random import randint

## %reset

keyword = input("What is the keyword you wanna look up?(e.g 'paro' o 'huelga de maestros')\n")


titles = []
links = []
contents = []
dates = []


start_time = time.time()
requests = 0
count = 0
pages = [str(i) for i in range(32,500)]


for page in pages:

    url = "https://noticias.caracoltv.com/busqueda/" + keyword + "?page=" + page
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
    
    articles = htmlsoup.find_all('div', attrs = {'class':'field__item even', 'property':'dc:title'})
    
    
    if len(articles) != 0:
        
        #if str(articles).find('https:') != -1:
            
            for oneArticle in articles:
                
                link = "https://noticias.caracoltv.com/" + oneArticle.h2.a['href']
                if 'bogota' not in link:
                    continue
                
                title = oneArticle.h2.a.text
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
                   
                
                date =  noodles.find("span", class_="date")
                
        
                if  date == None:
                    date = "**Unspecified**"
                else:
                    ## Modificando fecha
                    date1 = str(date)
                    date = re.search("- (.*)<", date1).group(1)
                
                
                content = noodles.find('div', attrs = {'class':'field field-name-body'})
                
                if not content:
                    ## Modificando fecha
                    date =  noodles.find_all("div", class_="field__item even")
                    date2 = date
                    date = date2[len(date) - 1]
                    date = str(date)
                    date = re.search(">(.*)<", date).group(1)
                    
                    titles.append(title)
                    dates.append(date)
                    texto="**Especial**"
                    contents.append(texto)
                    links.append(link)
                    test_df=pd.DataFrame({'Titulo':titles,
                                  'Fecha':dates,
                                  'Contenido':contents,
                                  'Link':links})
                
                else:
                    texto = ''
                    content_text = content.find_all('p')
                    for i in range(len(content_text)):
                        if i < len(content_text) - 1:
                            if content_text[i+1].getText() == "\n" or content_text[i].getText() == "\n":
                                continue
                        else:
                            if content_text[i].getText() == "\n":
                                continue
                        texto = texto + " " + content_text[i].getText()
                    
                    if not texto:
                        titles.append(title)
                        dates.append(date)
                        texto="**Texto vacio**"
                        contents.append(texto)
                        links.append(link)
                        test_df=pd.DataFrame({'Titulo':titles,
                                  'Fecha':dates,
                                  'Contenido':contents,
                                  'Link':links})
                    else:
                        
                        titles.append(title)
                        contents.append(texto)
                        dates.append(date)
                        links.append(link) 
                        test_df=pd.DataFrame({'Titulo':titles,
                                  'Fecha':dates,
                                  'Contenido':contents,
                                  'Link':links})
    
    
        #else:
         #   test_df=pd.DataFrame({'Titulo':titles,
         #                         'Fecha':dates,
         #                         'Contenido':contents,
         #                         'Link':links})
         #   print("There were no more articles found with your keyword")
         #   break
            
           
    else:
        test_df=pd.DataFrame({'Titulo':titles,
                                  'Fecha':dates,
                                  'Contenido':contents,
                                  'Link':links})
        print("There were no more articles found with your keyword")
        break
    
print('¿Guardar base en excel? ("si o no")')
respuesta = input()
if respuesta == "si":
    test_df.to_excel("Caracoltv.xlsx") 
