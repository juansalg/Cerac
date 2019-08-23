from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
from IPython.core.display import clear_output
from random import randint
import datetime


now=datetime.datetime.now()
dia=str(now)
dia=dia[2:10]

keywords = ['homicidios','muerte']
titles = []
links = []
contents = []
dates = []
pal_buscada = []
paginas = []

start_time = time.time()
requests = 0
pages = [str(i) for i in range(1,5)]
count = 0

for keyword in keywords:
    
    for page in pages:
        
        url = "https://www.eltiempo.com/buscar/" + page + "?q=" + keyword + "&publishedAt%5Bfrom%5D=00-01-01&publishedAt%5Buntil%5D=" + dia + "&contentTypes%5B0%5D=article"
        html = get(url)
        htmlsoup = soup(html.content,'html.parser')
        error=htmlsoup.find('div', class_="error-404")
        time.sleep(randint(2,4))
        requests += 1
        count += 1
        elapsed_time = time.time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        clear_output(wait = True)
        
        if (error != None):
            print("There were no more articles found with your keyword")
            test_df=pd.DataFrame({'Titulo':titles,
                                      'Fecha':dates,
                                      'Contenido':contents,
                                      'Link':links,
                                      'Palabra buscada':pal_buscada,
                                      'Pagina':paginas})
            break
        else:   
            articles = htmlsoup.find_all('h3', class_="title-container")
            
            for oneArticle in articles:
                    
                title = oneArticle.a.text.strip()
                link = oneArticle.a['href']
                content = ''
                url2 = "http://www.eltiempo.com" + link
                link = ''
                while link == '':
                    try:
                        link = get(url2)
                        break
                    except:
                        print("Connection refused by the server")
                        time.sleep(3)
                        print("Let's try again...")
                        continue
                print(url2)
                noodles=soup(link.content,'html.parser')
                especial=noodles.find('p',class_="contenido")
                if especial != None :
                    content=noodles.find('p',class_="contenido").text
                    if content != None:
                        date = noodles.find('span',class_="fecha").text.strip()
                        date = date[:-13]
                        titles.append(title)
                        contents.append(content)
                        dates.append(date)
                        links.append(url2)
                        pal_buscada.append(keyword)
                        paginas.append(page)   
                       
                            
                        test_df=pd.DataFrame({'Titulo':titles,
                                      'Fecha':dates,
                                      'Contenido':contents,
                                      'Link':links,
                                      'Palabra buscada':pal_buscada,
                                      'Pagina':paginas})
                
                else :
                        date = 0
                        titles.append(title)
                        content="Especial"
                        contents.append(content)
                        dates.append(date)
                        links.append(url2)
                        pal_buscada.append(keyword)
                        paginas.append(page)                        
                        
                        test_df=pd.DataFrame({'Titulo':titles,
                                      'Fecha':dates,
                                      'Contenido':contents,
                                      'Link':links,
                                      'Palabra buscada':pal_buscada,
                                      'Pagina':paginas})
                
      
test_df.to_excel("eltiempo_total.xlsx")

elapsed_time_2 = time.time() - start_time

print("")
print('\nTotal articulos: {} \nNumero de paginas: {} \nArticulos por pagina: {} \nTotal time: {} min'
      .format(len(links),
              len(pages),
              round(len(links)/len(pages), 3),
              round(elapsed_time_2/60, 3)))