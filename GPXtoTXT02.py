import os
import time
import gpxpy
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# === Funzione per ottenere il nome della strada dalle coordinate ===
def reverse_geocode(lat, lon):
    """Ottiene il nome della strada per una coppia di coordinate usando OpenStreetMap Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
    headers = {"User-Agent": "GPX-Analyzer"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("address", {}).get("road", "Sconosciuto")
    except requests.RequestException:
        return "Errore di geocodifica"

# === Funzione per estrarre le strade da un file GPX ===
def extract_street_names(gpx_file):
    """Legge il file GPX ed estrae l'elenco delle strade attraversate in ordine di percorrenza."""
    print(f"Apro il file GPX: {gpx_file}")  # 🔹 Debug

    with open(gpx_file, "r", encoding="utf-8") as file:
        gpx = gpxpy.parse(file)

    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))

    print(f"Trovate {len(coordinates)} coordinate")  # 🔹 Debug

    street_names = []
    seen_streets = set()

    for lat, lon in coordinates[::2]:  # Prendiamo un punto ogni due
        street_name = reverse_geocode(lat, lon)
        if street_name not in seen_streets:  # Evitiamo duplicati consecutivi
            street_names.append(street_name)
            seen_streets.add(street_name)
        time.sleep(1)  # Rispettiamo i limiti di Nominatim

    print("Elenco strade:", street_names)  # 🔹 Debug
    return street_names

# === Gestisce il comando /start ===
async def start(update: Update, context) -> None:
    """Risponde al comando /start."""
    await update.message.reply_text("Ciao! Inviami un file GPX e ti dirò le strade che attraversa.")

# === Gestisce il file GPX inviato dall'utente ===
async def handle_gpx(update: Update, context) -> None:
    """Gestisce il file GPX inviato dall'utente."""
    file = update.message.document

    await update.message.reply_text(f"Ho ricevuto un file: {file.file_name} (MIME type: {file.mime_type})")

    if not file.file_name.endswith(".gpx"):
        await update.message.reply_text("Per favore, inviami un file GPX valido.")
        return

    file_path = f"./{file.file_name}"
    telegram_file = await file.get_file()

    # 🔹 Debug: Messaggio prima di scaricare
    await update.message.reply_text("Sto scaricando il file...")

    try:
        await telegram_file.download_to_drive(file_path)

    except Exception as e:
        await update.message.reply_text(f"Errore nel download del file: {e}")
        return

    # 🔹 Debug: Verifica se il file esiste
    if os.path.exists(file_path):
        await update.message.reply_text(f"File scaricato correttamente: {file_path}")
    else:
        await update.message.reply_text("Errore: il file non è stato scaricato.")
        return

    await update.message.reply_text("Sto analizzando il file, un attimo...")

    try:
        street_names = extract_street_names(file_path)
    except Exception as e:
        await update.message.reply_text(f"Errore durante l'analisi del file: {e}")
        return

    os.remove(file_path)  # Rimuove il file dopo l'elaborazione

    if street_names:
        await update.message.reply_text("Strade attraversate:\n" + "\n".join(street_names))
    else:
        await update.message.reply_text("Non sono riuscito a trovare strade nel file GPX.")

# === Funzione principale per avviare il bot ===
def main():
    """Avvia il bot di Telegram."""
    TOKEN = "7391567508:AAG5Ydf502b9MnG0WwX8dVhCBUBBjNv71C4"

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_gpx))

    print("Bot avviato. In attesa di messaggi...")
    app.run_polling()

# === Avvia il bot ===
if __name__ == "__main__":
    main()
