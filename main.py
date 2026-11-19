import os
import sys
import json
import time
import unicodedata
import requests
import config

TELEGRAM_TOKEN = os.environ["TELEGRAMTKN"]
BUFFER_KEY = os.environ["BUFFER_APY_KEY"]
BUFFER_CANALE = os.environ["BUFFER_CHANNEL_ID"]
REPO = os.environ["GITHUB_REPOSITORY"]

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE_OFFSET = "stato/ultimo_update.txt"
FILE_ATTESA = "stato/in_attesa.json"
CARTELLA_MEDIA = "mediawt"
GIORNI_CONSERVAZIONE = 7


def leggi_offset():
    try:
        with open(FILE_OFFSET) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def salva_offset(numero):
    with open(FILE_OFFSET, "w") as f:
        f.write(str(numero))


def leggi_attesa():
    try:
        with open(FILE_ATTESA) as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return []


def salva_attesa(lista):
    with open(FILE_ATTESA, "w") as f:
        json.dump(lista, f, ensure_ascii=False, indent=1)


def normalizza(testo):
    testo = unicodedata.normalize("NFKC", testo).lower()
    return "".join(c for c in testo if c.isalnum())


def da_eliminare(riga, frasi):
    r = normalizza(riga)
    if not r:
        return False
    for f in frasi:
        if f and (f in r or (len(r) >= 6 and r in f)):
            return True
    return False


def componi_testo(didascalia):
    frasi = [normalizza(f) for f in config.RIGHE_DA_TOGLIERE]
    righe = [r for r in didascalia.splitlines() if not da_eliminare(r, frasi)]
    pulito = "\n".join(righe).strip()
    parti = [pulito, config.LINK_STORE, config.HASHTAG, config.MENZIONE]
    testo = "\n\n".join(p for p in parti if p)
    lunghezza_x = len(testo) - len(config.LINK_STORE) + 23
    return testo, lunghezza_x


def scarica_video(video, nome_file):
    info = requests.get(f"{API}/getFile", params={"file_id": video["file_id"]}, timeout=30).json()
    if not info.get("ok"):
        print("Errore getFile:", info.get("description"))
        return False
    url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{info['result']['file_path']}"
    with open(os.path.join(CARTELLA_MEDIA, nome_file), "wb") as f:
        f.write(requests.get(url, timeout=120).content)
    return True


def pulisci_media(attesa):
    in_uso = {voce["file"] for voce in attesa}
    limite = time.time() - GIORNI_CONSERVAZIONE * 86400
    for nome in os.listdir(CARTELLA_MEDIA):
        if not nome.endswith(".mp4") or nome in in_uso:
            continue
        try:
            creato = int(nome.split("_")[0])
        except ValueError:
            continue
        if creato
