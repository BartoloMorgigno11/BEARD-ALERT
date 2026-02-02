# Beard Alert

Progetto Python che usa la webcam per rilevare quando la mano tocca la zona della barba e invia un alert sonoro.

## Requisiti
- Windows 10/11
- Python 3.10+ con accesso alla webcam

## Installazione
1. Crea un virtualenv e installa le dipendenze:
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
   - `pip install -r requirements.txt`

## Avvio
- `python src/main.py`

## Configurazione
Modifica i parametri in [config.yaml](config.yaml) per:
- Soglie di rilevamento
- Uso di YOLO per il box persona
- Audio e debug overlay

## Note
- L'audio usa un beep di Windows se `sound_path` è vuoto.
- La zona barba è stimata usando la parte bassa del viso.

## Pubblicazione su GitHub
1. Non includere la cartella `.venv/` (è già in `.gitignore`).
2. Inizializza un repository Git nella cartella del progetto.
3. Fai commit dei file (config, src, README, requirements).
4. Crea un repository vuoto su GitHub e fai push.
