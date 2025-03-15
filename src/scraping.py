import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import re
import random
from selenium import webdriver

from selenium.webdriver.edge.service import Service  
from selenium.webdriver.edge.options import Options  


URL_TEMPLATE = "https://autos.mercadolibre.com.ar/usados/_Desde_{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
} # Para simular ser un usuario

# Configuración de Edge para Selenium
edge_options = Options()  
edge_options.use_chromium = True  
edge_options.add_argument("--headless")  # Lo eejcuta sin interfaz gráfica
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")


# Ruta al edgeDriver
service = Service("D:\joaquin\Escritorio\car_price_predictor\drivers\msedgedriver.exe")  
driver = webdriver.Edge(service=service, options=edge_options)

def get_dollar_blue():
    """Obtiene la cotización del dólar blue desde una API."""
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/blue")
        if response.status_code == 200:
            return response.json()["venta"]  # Toma el valor de venta
    except Exception as e:
        print(f"Error obteniendo dólar blue: {e}")
    
    return 1220  # Valor por defecto si la API falla

DOLAR_BLUE = get_dollar_blue()  # Obtiene el valor del dólar blue

def get_html(url):
    """Realiza una solicitud GET y devuelve el HTML."""
    time.sleep(random.uniform(1, 3))  # Espera entre 1 y 3 segundos (para evitar bloqueos)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        print("HTML obtenido correctamente.")  
        return response.text # Retorna html
    elif response.status_code == 429:  # Demasiadas solicitudes
        print("Bloqueo detectado. Esperando 15 segundos...")
        time.sleep(15)  # Espera 15 segundos antes de reintentar
        return get_html(url)  # Reintenta
    else:
        print(f"Error al acceder a la página: {response.status_code}")
        return None

def get_html_with_selenium(url): # Hay veces qeu el request falla, por lo que usamos selenium
    """Obtiene el HTML renderizado con Selenium."""
    driver.get(url)
    time.sleep(5)  # Espera fija de 5 segundos para asegurar la carga completa
    return driver.page_source

def get_pesos(price_tag, currency_tag):
    """Convierte USD a ARS si es necesario."""
    if isinstance(price_tag, str) and isinstance(currency_tag, str):
        price = int(price_tag.replace(".", ""))
        currency = currency_tag.strip()

        if "US$" in currency:  # Si está en dólares, convierte a pesos
            price *= DOLAR_BLUE

        return price
    
    return "No disponible"

def scrape_details(url):
    """Extrae información detallada de la página de cada auto."""
    time.sleep(random.uniform(1, 3))  # Espera entre 1 y 3 segundos

    # Intenta primero con requests
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Verifica si el HTML contiene los detalles esperados
    rows = soup.find_all(["tr", "tbody"], class_=re.compile(r"andes-table__(row|body)"))
    if not rows:  # Si no se encontraron filas, usa Selenium
        print("Usando Selenium para renderizar la página...")
        html = get_html_with_selenium(url)
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all(["tr", "tbody"], class_=re.compile(r"andes-table__(row|body)"))

    details = {}
    for row in rows:
        key_element = row.find("div", class_="andes-table__header__container")  # Nombre del atributo
        value_element = row.find("span", class_="andes-table__column--value")  # Valor del atributo
        if key_element and value_element:
            key = key_element.text.strip().lower()  # Normaliza el nombre
            value = value_element.text.strip()
            details[key] = value

    return details

def parse_page(html):
    """Extrae datos de la página de listado."""
    soup = BeautifulSoup(html, "html.parser")
    cars = []

    listings = soup.find_all("li", class_="ui-search-layout__item")
    print(f"Se encontraron {len(listings)} listados.")  

    for listing in listings:
        try:
            print("Procesando un listado...")  
            # Obtener el enlace al detalle del auto
            link_tag = listing.find("a", class_="poly-component__title")
            if link_tag:
                car_url = link_tag["href"]
                print(f"Scrapeando detalles de: {car_url}")  
                details = scrape_details(car_url)
            else:
                details = {}

            # Precio
            price_tag = listing.find("span", class_="andes-money-amount__fraction")
            currency_tag = listing.find("span", class_="andes-money-amount__currency-symbol")

            if price_tag and currency_tag:
                price = get_pesos(price_tag.text.strip(), currency_tag.text.strip())
            else:
                price = "No disponible"

            # Ubicación
            location_tag = listing.find("span", class_="poly-component__location")
            location = location_tag.text.strip() if location_tag else "No especificado"

            # Datos del auto
            car_data = {
                "Precio (ARS)": price,
                "Marca": details.get("marca", "No disponible"),
                "Modelo": details.get("modelo", "No disponible"),
                "Versión": details.get("versión", "No disponible"),
                "Año": details.get("año", "No disponible"),
                "KM": re.sub(r"[^\d]", "", details.get("kilómetros", "No disponible")), #Dejo solo los numeros
                "Color": details.get("color", "No disponible"),
                "Combustible": details.get("tipo de combustible", "No disponible"),
                "Puertas": details.get("puertas", "No disponible"),
                "Transmisión": details.get("transmisión", "No disponible"),
                "Motor": details.get("motor", "No disponible"),
                "Carrocería": details.get("tipo de carrocería", "No disponible"),
                "Ubicación": location,
            }

            # Filtrar autos con datos incompletos
            campos_obligatorios = ["Precio (ARS)", "Marca", "Modelo", "Año", "KM"]
            if any(car_data[campo] == "No disponible" for campo in campos_obligatorios):
                print("Auto descartado por falta de información.")  
                continue  # No agregar este auto si falta info clave

            cars.append(car_data)
            print("Auto agregado:", car_data)  

            # Pausar para evitar bloqueos
            time.sleep(random.uniform(1, 3))  # Espera entre 1 y 3 segundos

        except Exception as e:
            print(f"Error procesando el listado: {e}")
            continue

    return cars

def append_to_csv(cars, filename="autos.csv"):
    """Guarda los datos en un archivo CSV, agregando nueva información sin sobrescribir."""
    keys = [
        "Precio (ARS)", "Marca", "Modelo", "Versión", "Año", "KM",
        "Color", "Combustible", "Puertas", "Transmisión", "Motor", "Carrocería", "Ubicación"
    ]
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not file_exists:
            writer.writeheader() #Si es la primera vez que se crea el archivo, se escriben los headers
        writer.writerows(cars)

def scrape_multiple_pages(max_pages=1): #Si no se envía ningún parametro, se scrapea 1 sola pagina
    """Scrapea múltiples páginas de Mercado Libre y guarda los datos en un CSV tras cada página."""
    for page in range(1, max_pages + 1):
        url = URL_TEMPLATE.format(page * 50 + 1)
        print(f"Scrapeando: {url}")
        html = get_html(url)
        if html:
            cars = parse_page(html)
            append_to_csv(cars)  # Guardar cada página procesada
        time.sleep(random.uniform(3, 6))

if __name__ == "__main__":
    scrape_multiple_pages(max_pages=70)
    driver.quit()