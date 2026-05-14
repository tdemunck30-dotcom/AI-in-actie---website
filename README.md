# Steengroeve website

Losse webapp om het spel voor te stellen en tegelijk alle downloadbare bouwbestanden aan te bieden.

## Wat zit erin

- een landingspagina met uitleg over het spel
- een downloadsectie die automatisch de map `downloads/` uitleest
- een kleine FastAPI-server die de website en de downloadbestanden serveert
- een `render.yaml` zodat je dit later makkelijk kan deployen

## Lokaal starten

De makkelijkste manier op Windows:

```powershell
start_spel_website.cmd
```

Laat het geopende venster open en surf daarna naar:

```text
http://127.0.0.1:8040/
```

Of handmatig:

```powershell
cd spel-website
..\.venv\Scripts\python.exe -m uvicorn website_app:app --host 127.0.0.1 --port 8040
```

Als je geen gedeelde virtuele omgeving wil gebruiken, kan je ook in deze map zelf een nieuwe omgeving maken en `pip install -r requirements.txt` uitvoeren.

## Contactformulier instellen

Het contactformulier werkt pas echt als de mailserver-instellingen ingevuld zijn.

1. Maak een kopie van `contact.local.env.example`
2. Noem die kopie `contact.local.env`
3. Vul daarin je eigen SMTP-gegevens in
4. Herstart daarna de website

Benodigde velden:

- `CONTACT_SMTP_HOST`
- `CONTACT_SMTP_PORT`
- `CONTACT_SMTP_USERNAME`
- `CONTACT_SMTP_PASSWORD`

Optioneel:

- `CONTACT_SMTP_FROM`
- `CONTACT_SMTP_TO`
- `CONTACT_SMTP_SECURITY`
- `CONTACT_RATE_LIMIT_SECONDS`

`contact.local.env` wordt niet mee in git opgeslagen.

## Bestanden toevoegen

Zet je materiaal in `downloads/`.

Voorbeelden:

- `downloads/Steengroeve-volledig-pakket.zip`
- `downloads/print/kaartenset.pdf`
- `downloads/handleidingen/opbouw-gids.pdf`

De site toont die bestanden automatisch in de downloadsectie.
