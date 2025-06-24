# TimeTracker - Persönliche Zeiterfassung
Dies ist eine moderne, persönliche Zeiterfassungsanwendung, die entwickelt wurde, um die Arbeitszeit schnell und unkompliziert von unterwegs zu erfassen. Die Anwendung besteht aus einem Python-Backend mit FastAPI und einem React-Frontend, das als mobile-first Progressive Web App (PWA) konzipiert ist.

## ✨ Features
- **Einfache Zeiterfassung**: Starten und Stoppen der Zeitmessung mit großen, benutzerfreundlichen Buttons.

- **Persönliches Dashboard**: Die App ist auf einen festen Benutzer zugeschnitten und begrüßt diesen namentlich.

- **Detaillierte Übersicht**: Alle Zeiteinträge werden in einer chronologischen Liste mit exakten Start- und Endzeiten angezeigt.

- **Progressive Web App (PWA)**: Kann wie eine native App direkt auf dem Startbildschirm von iOS und Android "installiert" werden.

- **Offline-Fähigkeit**: Die Benutzeroberfläche lädt auch ohne aktive Internetverbindung sofort.

- **Live Deployment**: Die gesamte Anwendung ist auf der Cloud-Plattform Render deployt und über das Internet erreichbar.

## 🛠️ Tech Stack
Die Anwendung ist als Monorepo strukturiert und nutzt folgende Technologien:

### Backend (`/backend`)

- Framework: [FastAPI](https://fastapi.tiangolo.com/)

- Sprache: Python

- Datenbank: [PostgreSQL](https://www.postgresql.org/) (gehostet auf [Supabase](https://supabase.com/))

- Datenbank-Treiber: `psycopg2-binary`

- Server: `uvicorn`

### Frontend (`/frontend`)

- Framework: [React](https://reactjs.org/)

- Build-Tool: [Vite](https://vitejs.dev/)

- Styling: [Tailwind CSS](https://tailwindcss.com/)
- Mobile App: Progressive Web App (PWA) Features (Manifest & Service Worker)

## 📁 Projektstruktur
Das Repository ist als Monorepo aufgebaut, um Backend und Frontend zentral zu verwalten.
```
/
├── backend/
│   ├── .venv/
│   ├── main.py         # Hauptlogik der FastAPI-Anwendung
│   ├── requirements.txt  # Python-Abhängigkeiten
│   └── .env.example    # Beispiel für Umgebungsvariablen
│
└── frontend/
    ├── public/
    │   ├── icons/        # App-Icons
    │   ├── manifest.json # PWA-Manifest
    │   └── sw.js         # Service Worker für Offline-Fähigkeit
    ├── src/
    │   ├── App.jsx       # Hauptkomponente der React-App
    │   └── ...
    ├── package.json      # Node.js-Abhängigkeiten
    └── vite.config.js    # Vite-Konfiguration
```
## 🚀 Lokale Einrichtung & Installation
Um das Projekt lokal auszuführen, benötigen Sie Git, Node.js (mit npm) und Python.

### 1. Backend
```sh # 1. In den Backend-Ordner wechseln
cd backend

# 2. Eine virtuelle Umgebung erstellen und aktivieren
python -m venv .venv
source .venv/bin/activate  # Auf Windows: .venv\Scripts\activate

# 3. Python-Abhängigkeiten installieren
pip install -r requirements.txt

# 4. .env-Datei erstellen
# Kopieren Sie die .env.example zu .env und tragen Sie Ihre Daten ein.
cp .env.example .env

# 5. Datenbank-Schema anwenden
# Stellen Sie sicher, dass die Tabellen (users, time_entries) und die View (v_time_summary)
# in Ihrer Supabase-Datenbank existieren. Fügen Sie Ihren Test-Benutzer ein.

# 6. Backend-Server starten
uvicorn main:app --reload --port 10000
```
Das Backend ist nun unter `http://localhost:10000` erreichbar.


### 2. Frontend
```sh
# 1. In den Frontend-Ordner wechseln
cd frontend

# 2. Node.js-Abhängigkeiten installieren
npm install

# 3. Frontend-Entwicklungsserver starten
npm run dev
```

Das Frontend ist nun unter `http://localhost:5173` erreichbar und verbindet sich mit dem lokal laufenden Backend.

☁️ Deployment
Die Anwendung ist live auf [Render](https://render.com/) deployt und nutzt eine [Supabase](https://supabase.com/)-Datenbank.

- Backend: Als "Web Service" auf Render deployt. Das "Root Directory" ist auf /backend gesetzt.

- Frontend: Als "Static Site" auf Render deployt. Das "Root Directory" ist auf /frontend gesetzt.

- Datenbank: Die DATABASE_URL für den Supabase Connection Pooler ist als Umgebungsvariable im Backend-Dienst hinterlegt.

- CORS: Die Live-URL des Frontends ist in der origins-Liste der FastAPI-Anwendung freigegeben, um die Kommunikation zu ermöglichen.

🔮 Zukünftige Features
Dieses Projekt hat das Potenzial für viele Erweiterungen:

- [ ] Einträge bearbeiten & löschen: Eine UI, um fehlerhafte Zeiterfassungen zu korrigieren.

- [ ] Notizen hinzufügen: Zu jedem Zeiteintrag eine kurze Notiz speichern.

- [ ] Wochen-/Monatsübersicht: Eine Ansicht, die die Gesamtstunden pro Woche oder Monat zusammenfasst.

- [ ] Export-Funktion: Die Möglichkeit, die erfassten Zeiten als CSV-Datei herunterzuladen.

- [ ] Multi-User-Fähigkeit: Eine richtige Benutzerauthentifizierung, damit sich mehrere Benutzer anmelden können.

Erstellt von **Joshua Phu**.