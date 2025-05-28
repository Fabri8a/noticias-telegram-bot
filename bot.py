import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import random

# CONFIGURA AQUÍ TUS DATOS:
TOKEN = '7705552210:AAGcKtoRlsTMOxUYjhFSS5OQ8I0eTza2OAU'
CHAT_ID = '8160370113'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

DIARIOS = {
    "El País": "https://www.elpais.com.uy",
    "El Observador": "https://www.elobservador.com.uy",
    "Subrayado": "https://www.subrayado.com.uy",
    "Montevideo Portal": "https://www.montevideo.com.uy"
}

RADIOS = [
    "https://www.carve850.com.uy",
    "https://www.sarandi690.com.uy"
]

def obtener_noticias_diarios():
    noticias = []
    for nombre, url in DIARIOS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                titulares = soup.find_all(['h2', 'h3'])
                count = 0
                for t in titulares:
                    link_tag = t.find('a')
                    if link_tag and link_tag.get('href'):
                        link = link_tag.get('href')
                        if not link.startswith('http'):
                            link = url + link
                        titulo = t.get_text(strip=True)
                        noticias.append(f"📰 {titulo} ({nombre})\n🔗 {link}")
                        count += 1
                        if count >= 2:
                            break
            else:
                noticias.append(f"❌ Error en {url}: HTTP {resp.status_code}")
        except Exception as e:
            noticias.append(f"❌ Error en {url}: {str(e)}")
    return noticias

def obtener_noticias_radios():
    noticias = []
    for url in RADIOS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            titulos = soup.find_all(['h2', 'h3'])
            if titulos:
                for titulo in titulos[:2]:
                    texto = titulo.get_text(strip=True)
                    if texto:
                        noticias.append(f"📻 {texto} ({url})")
            else:
                noticias.append(f"📻 No se encontraron titulares ({url})")
        except Exception as e:
            noticias.append(f"❌ Error en {url}: {str(e)}")
    return noticias

async def enviar_noticias_a_telegram(noticias):
    bot = Bot(token=TOKEN)
    mensaje = "📰 Noticias destacadas de Uruguay:\n\n" + "\n\n".join(noticias)
    await bot.send_message(chat_id=CHAT_ID, text=mensaje)

if __name__ == "__main__":
    noticias_diarios = obtener_noticias_diarios()
    noticias_radios = obtener_noticias_radios()
    noticias_totales = noticias_diarios + noticias_radios
    noticias_validas = [n for n in noticias_totales if not n.startswith('❌')]
    noticias_finales = random.sample(noticias_validas, min(len(noticias_validas), 7))
    if len(noticias_finales) < 7:
        faltantes = 7 - len(noticias_finales)
        errores = [n for n in noticias_totales if n.startswith('❌')]
        noticias_finales += errores[:faltantes]
    asyncio.run(enviar_noticias_a_telegram(noticias_finales))
