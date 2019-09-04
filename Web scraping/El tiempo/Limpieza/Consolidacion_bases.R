# install.packages("readxl")
# install.packages("tidyverse")
library("readxl")
library('tidyverse')

path = "C:/Users/juan.salgado/Desktop/Proyecto CCB/GIT_Cerac/Web scraping/El tiempo"
el_tiempo_raw <- read_excel(paste(path,'/eltiempo_consolidado.xlsx', sep = ""))
el_tiempo_raw <- subset(el_tiempo_raw, select = -1)

# Seleccionar valores unicos segun el link
el_tiempo_uniq <- el_tiempo_raw %>% distinct(Link, .keep_all = TRUE)
  # Modificar palabra buscada
el_tiempo_uniq$`Palabra buscada`[el_tiempo_uniq$`Palabra buscada` == 'Seguridad'] <-
                      'Seguridad bogotá'
el_tiempo_uniq$`Palabra buscada`[el_tiempo_uniq$`Palabra buscada` == 'Homicidio'] <-
                      'Homicidio bogotá'

# Modificar fecha

  # Funcion que extrae el anio
year_extr <- function(y){
  year <- sub(".* de .* ", "", y)
  return(year)
}
  # Funcion que extrae el mes
mes_extr <- function(m){
  mes <- sub(".*de (.+) .*", "\\1",m)
  return(mes)
}

# Generar columna de mes y de anio
el_tiempo_uniq <- el_tiempo_uniq %>%
  mutate(mes = mes_extr(Fecha)) %>%
  mutate(anio = year_extr(Fecha))

# Collapse by year & palabra_buscada

  # Por Anio
year_count <- data.frame(table(el_tiempo_uniq$anio))
colnames(year_count) <- c('Anio', 'Cantidad de articulos')
tot_art <- sum(year_count$`Cantidad de articulos`)
year_count <- year_count %>%
              mutate(`Proporcion de articulos total (%)` = 
                       round((`Cantidad de articulos` / tot_art)*100, 2))

  # Por palabra buscada
pal_year_count <- count(el_tiempo_uniq, `Palabra buscada`, anio)
colnames(pal_year_count) <- c('Palabra buscada', 'Anio', 'Cantidad de articulos')
  
    # Total palabras por articulo
tot_art_pal <- sum(year_count$`Cantidad de articulos`)

pal_year_count <- pal_year_count %>%
  
    # Generar total articulos por palabra
  group_by(`Palabra buscada`) %>%
  mutate(`Articulos por palabra` = 
           sum(`Cantidad de articulos`)) %>% ungroup() %>%
  
    # Proporcion de articulos sobre el total de articulos por palabra
  mutate(`Proporcion de articulos palabra (%)` = 
           round((`Cantidad de articulos` / `Articulos por palabra`)*100, 2)) %>%
  
    # Proporcion de articulos sobre el total de articulos
  mutate(`Proporcion de articulos total (%)` = 
           round((`Cantidad de articulos` / tot_art)*100, 2)) 

# Grafico num articulos por anio
# ggplot(el_tiempo_uniq, aes(x = year))
