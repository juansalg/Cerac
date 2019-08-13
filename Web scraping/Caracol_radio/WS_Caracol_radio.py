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

keywords = []
mas_palabras = "si"
while mas_palabras == "si":
    i = 0
    keywords[i] = input("Ingrese palabra a buscar\n")
    i += 1
    mas_palabras = input("¿Seguir buscando palabras (si o no)\n")


titles = []
links = []
contents = []
dates = []


start_time = time.time()
requests = 0
count = 0
pages = [str(i) for i in range(57,2000)]

for keyword in keywords:
    for page in pages:
    
        url = "https://caracol.com.co/tag/" + keyword + "/a/" + page
        html = get(url)
        htmlsoup = soup(html.content,'html5lib')
        time.sleep(randint(2,4))
        requests += 1
        elapsed_time = time.time() - start_time
        print('Request: {}; Total time: {} min; Frequency: {} requests/s'.format(requests, 
              round(elapsed_time/60, 3), round(requests/elapsed_time, 3)))
        clear_output(wait = True)
        
        
        print(url)
        print("")
        
        articles = htmlsoup.find_all('div', class_="module-item-content")
        
        
        if len(articles) != 0:
            
            if str(articles).find('https:') != -1:
                
                for oneArticle in articles:
                    
                    link = oneArticle.h2.a['href']
                    if link.find('https:',0) == -1 or 'bogota' not in link:
                        continue
                    
                    title = oneArticle.h2.a.text
                    content = ''
                    html2 = ''
                    print(link)
                    while html2 == '':
                        try:
                            html2 = get(link)
                            break
                        except:
                            print("Connection refused by the server")
                            time.sleep(3)
                            print("Let's try again...")
                            continue
                        
                    count = count + 1
                    print(count)
                    print("")
                        
                    noodles = soup(html2.content,'html5lib')
                    
                    ## Modificando fecha
                    date_0 =  noodles.find("div", class_="cnt-metas")
                    date_1 =  date_0.find_all("span")
                    date_1 =  date_0.find_all("span") [len(date_1) - 1]
                    date = str(date_1)
                    date = re.search("\n(.*) -", date).group(1)
                    
            
                    if  date == None:
                        date = "**Unspecified**"
                    ##else:
                      ##  date = noodles.find('span', class_="published-at").text.strip()[:-12]
                        
                    content = noodles.find('div', attrs = {'class':'cuerpo'})
                    
                    if content == None:
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
                        for textos in content.find_all('p'):
                            texto += textos.getText()
                        
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
        
        
            else:
                test_df=pd.DataFrame({'Titulo':titles,
                                      'Fecha':dates,
                                      'Contenido':contents,
                                      'Link':links})
                print("There were no more articles found with your keyword")
                break
                
               
        else:
            test_df=pd.DataFrame({'Titulo':titles,
                                      'Fecha':dates,
                                      'Contenido':contents,
                                      'Link':links})
            print("There were no more articles found with your keyword")
            break
        
    test_df.to_excel("Caracol_radio" + keyword + ".xlsx")