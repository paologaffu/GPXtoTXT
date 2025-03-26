import os
import time
import gpxpy
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Inserisci il token del tuo bot
TELEGRAM_BOT_TOKEN = "7391567508:AAG5Ydf502b9MnG0WwX8dVhCBUBBjNv71C4"

async def start(update: Update, context) -> None:
    await update.message.reply_text("Ciao! Inviami un file GPX e ti dirò le strade che attraversa.")

def reverse_geocode(lat, lon):
    """Ottiene il nome della strada da OpenStreetMap Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
    headers = {"User-Agent": "GPX-Analyzer"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("address", {}).get("road", "Sconosciuto")
    except requests.RequestException:
        return "Errore di geocodifica"

def extract_street_names(gpx_file):
    """Legge il file GPX ed estrae l'elenco delle strade attraversate."""
    with open(gpx_file, "r", encoding="utf-8") as file:
        gpx = gpxpy.parse(file)

    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))

    street_names = []
    seen_streets = set()
    
    for lat, lon in coordinates[::2]:  # Prendiamo un punto ogni due
        street_name = reverse_geocode(lat, lon)
        if street_name not in seen_streets:  # Evitiamo duplicati consecutivi
            street_names.append(street_name)
            seen_streets.add(street_name)
        time.sleep(1)  # Ritardo per rispettare i limiti di Nominatim

    return street_names

async def handle_gpx(update: Update, context) -> None:
    """Gestisce il file GPX inviato dall'utente."""
    file = update.message.document

    # Debug: Mostra informazioni sul file ricevuto
    await update.message.reply_text(f"Ho ricevuto un file: {file.file_name} (MIME type: {file.mime_type})")

    if not file.file_name.endswith(".gpx"):
        await update.message.reply_text("Per favore, inviami un file GPX valido.")
        return

    file_path = f"./{file.file_name}"
    telegram_file = await file.get_file()
    await telegram_file.download(file_path)  # Scarica il file correttamente
    
    await update.message.reply_text("Sto analizzando il file, un attimo...")

    street_names = extract_street_names(file_path)
    os.remove(file_path)  # Rimuove il file dopo l'elaborazione

    if street_names:
        await update.message.reply_text("Strade attraversate:\n" + "\n".join(street_names))
    else:
        await update.message.reply_text("Non sono riuscito a trovare strade nel file GPX.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/gpx+xml"), handle_gpx))

    app.run_polling()

if __name__ == "__main__":
    main()
