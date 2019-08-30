from bs4 import BeautifulSoup as soup
from requests import get
import pandas as pd
import time
from IPython.core.display import clear_output
from random import randint
import smtplib, ssl


titles = []

keywords = ['Seguridad bogotá','Homicidio bogotá','Hurto bogotá','Vandalismo bogotá',
            'Policía de Bogotá','Inseguridad bogotá','Percepción de seguridad bogotá',
            'Percepción de inseguridad bogotá','Seguridad ciudadana bogotá',
            'Orden público bogotá','Violencia bogotá','Asesinato bogotá','Matar bogotá',
            'Robo bogotá','Atraco bogotá','Fleteo bogotá','Orden público bogotá',
            'Disturbio bogotá','Riña bogotá','Abuso sexual bogotá','Acoso sexual bogotá',
         'Acoso infantil bogotá','Golpiza bogotá','Linchamiento bogotá',
         'Policía Nacional bogotá','Dar de baja bogotá',
         'Violencia sexual bogotá', 'Lesiones personales bogotá']

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
pages = [str(i) for i in range(1,100000)]
count = 0

for keyword in keywords:
    
    for page in pages:
        
        url = "https://www.elespectador.com/search/" + keyword + "?page=" + page
        print(url)
        html = get(url)
        htmlsoup = soup(html.content,'html.parser')
        time.sleep(randint(2,4))
        requests += 1
        count += 1
        elapsed_time = time.time() - start_time
        print("")
        print('Palabra: {}; Página: {}; Tiempo: {} min'.format(keyword, page,
                                                                  round(elapsed_time/60,3)))
        print("")
        clear_output(wait = True)
        articles = htmlsoup.find_all('div', class_="node-title field field--name-title field--type-ds field--label-hidden")
        if not articles:
            print("There were no more articles found with your keyword")
            break
        
        else:   
            for oneArticle in articles:
                title = oneArticle.a.text.strip()
                link = oneArticle.a['href']
                content = ''
                url2 = "http://www.elespectador.com" + link
                
                ## Descartar noticias repetidas o que no tienen 'bogo' en el link
                if url2 in links:
                        continue
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
                    
                    
                    
                    noodles=soup(link.content,'html.parser')
                    especial=noodles.find('div',class_="node-body content_nota field field--name-body field--type-text-with-summary field--label-hidden")
                    if especial:
                        content=especial.find_all('p')
                        texto=''
                        for textos in content:
                            texto=texto+textos.getText()
                        texto=texto.replace('\n','')
                        
                        ## Eliminar artículos que no tengan la palabra 'bogot' ni en el url, 
                        ## título o texto
                        if 'bogot' not in url2 and 'bogot' not in title \
                            and 'bogot' not in content:
                            continue
                        
                        date = noodles.find('div',class_="node-post-date field field--name-post-date field--type-ds field--label-hidden").text
                        date = date[0:12].strip()
                        date = date.replace("-","")
                        
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
                        contents.append(texto)
                        dates.append(date)
                        links.append(url2)
                        pal_buscada.append(keyword)
                        paginas.append(page)
                
                    
                    else :
                            date = 0
                            titles.append(title)
                            content="Especial"
                            contents.append(content)
                            dates.append(date)
                            links.append(url2)
                            pal_buscada.append(keyword)
                            paginas.append(page)
        
    
                except:
                    link_err.append(url2)
                    

test_df=pd.DataFrame({'Titulo':titles,
          'Fecha':dates,
          'Contenido':contents,
          'Link':links,
          'Palabra buscada':pal_buscada,
          'Pagina':paginas})
                
errores = pd.DataFrame(
                {'Link error':link_err}
                )
      
test_df.to_excel("elespectador_total.xlsx")
errores.to_excel("El_espectador_errores.xlsx")

elapsed_time_2 = time.time() - start_time

print("")
print('\nTotal articulos: {} \nNumero de paginas: {} \nArticulos por pagina: {} \nTotal time: {} min'
      .format(len(links),
              requests,
              round(len(links)/requests, 3),
              round(elapsed_time_2/60, 3)))
    
## Enviar correo
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "python.development.cerac@gmail.com"  # Enter your address
receiver_email = "helena.hernandez@cerac.org.co"  # Enter receiver address
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