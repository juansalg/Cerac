# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:00:34 2019

@author: JCSR
"""

from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
from IPython.core.display import clear_output
from random import randint


""" qt = *palabra clave*
"""
url = "https://caracol.com.co/tag/homicidios/a/1"
html = get(url)
htmlsoup = soup(html.content,'html5lib')
time.sleep(randint(2,4))


print(url)
articles = htmlsoup.find_all('div', class_="module-item-content")
count = 0

if len(articles) != 0:
        for oneArticle in articles:
            
            link = oneArticle.h2.a['href']
            if link.find('https:',0) == -1:
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
            noodles = soup(html2.content,'html5lib')
            date_prueba =  noodles.find("span")
            count = count + 1
            
            """## Modificar class_
            if  == None:
                date noodles.find('abbr', "span")= "Unspecified"
            else:
                date = noodles.find('span', class_="published-at").text.strip()[:-12]           
            content = noodles.find('div', attrs = {'class':'article-content'}) 
            if content == None :
                content = noodles.find('div', attrs = {'class':'content-modules'})
            if content == None:
                titles.append(title)
                dates.append(date)
                texto="Especial"
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
  """      