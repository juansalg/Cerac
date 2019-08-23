
from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
from IPython.core.display import clear_output
from random import randint
import datetime
import smtplib, ssl



now=datetime.datetime.now()
dia=str(now)
dia=dia[2:10]

keywords = ['Seguridad','Homicidio','Hurto','Vandalismo','Violencia sexual','Lesiones personales',
            'Policía de Bogotá','Inseguridad','Percepción de seguridad','Percepción de inseguridad',
            'Seguridad ciudadana','Orden público','Violencia','Asesinato','Matar','Robo',
            'Atraco','Fleteo','Orden público','Disturbio','Riña','Abuso sexual','Acoso sexual',
            'Acoso infantil','Golpiza','Linchamiento','Policía Nacional','Dar de baja']
titles = []
links = []
contents = []
dates = []
pal_buscada = []
paginas = []
link_err = []
inicio = 2010
fin = 2018
years = range(inicio,fin+1)

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
                        
                    try:
                            
                        print(url2)
                        
                        ## Descartar noticias repetidas o que no tienen 'bogo' en el link
                        if url2 in links or 'bogo' not in url2:
                            continue
                        
                        noodles=soup(link.content,'html.parser')
                        especial=noodles.find('p',class_="contenido")
                        if especial != None :
                            content=noodles.find('p',class_="contenido").text
                            if content != None:
                                date = noodles.find('span',class_="fecha").text.strip()
                                date = date[:-13]
                                
                                ## While para descartar fechas fuera del rango
                                fecha_en_rango = False
                                i = 0
                                while fecha_en_rango == False and i < len(years):
                                    if str(years[i]) in date:
                                        fecha_en_rango = True
                                    i += 1 
                                if fecha_en_rango == False:
                                    continue
                                
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
                    except:
                        link_err.append(url2)
            
errores = pd.DataFrame(
                {'Link error':link_err}
                )
            
                
      
test_df.to_excel("eltiempo_total.xlsx")
errores.to_excel("El_tiempo_errores.xlsx")


elapsed_time_2 = time.time() - start_time

print("")
print('\nTotal articulos: {} \nNumero de paginas: {} \nArticulos por pagina: {} \nTotal time: {} min'
      .format(len(links),
              len(pages),
              round(len(links)/len(pages), 3),
              round(elapsed_time_2/60, 3)))

## Enviar correo
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "python.development.cerac@gmail.com"  # Enter your address
receiver_email = "helena.hernandez@cerac.org.co"  # Enter receiver address
password = 'Cerac_2019'
message = """Subject: Finalizo WS de El tiempo


Tiempo total: """ + str(round(elapsed_time_2/60, 3)) + "min" \
\
"""\n\nTotal articulos: """ + str(len(links)) + \
\
"""\n\nTotal errores: """ + str(len(errores))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
