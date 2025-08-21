# Setup Instructies voor Bandenboer App

## 1. Supabase Configuratie

Je hebt een Supabase project nodig om deze applicatie te kunnen gebruiken. Volg deze stappen:

### Stap 1: Ga naar je Supabase Dashboard
- Ga naar [supabase.com](https://supabase.com)
- Log in en ga naar je project dashboard

### Stap 2: Vind je API Keys
- Ga naar **Settings** > **API** in je Supabase dashboard
- Kopieer de volgende waarden:
  - **Project URL** (bijv. `https://tfcgwmxiqgnlyjtpymzy.supabase.co`)
  - **service_role key** (begint met `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

### Stap 3: Maak een .env bestand aan
Maak een bestand aan genaamd `.env` in de root van je project met de volgende inhoud:

```env
# Supabase Configuration
SUPABASE_URL=https://tfcgwmxiqgnlyjtpymzy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=jouw-service-role-key-hier

# Flask Configuration
SECRET_KEY=bandenboer-secret-key-2024
FLASK_ENV=development
FLASK_DEBUG=True
```

**Vervang `jouw-service-role-key-hier` met je echte service role key uit Supabase.**

## 2. Database Setup

### Stap 1: Voer het database script uit
- Ga naar je Supabase dashboard
- Ga naar **SQL Editor**
- Kopieer de inhoud van `database_setup.sql`
- Voer het script uit om de tabellen aan te maken

### Stap 2: Controleer de tabellen
Na het uitvoeren van het script zou je de volgende tabellen moeten hebben:
- `tires` - voor banden voorraad
- `reservations` - voor klant reserveringen

## 3. Applicatie Starten

Nadat je de configuratie hebt ingesteld, kun je de applicatie starten:

```bash
python app.py
```

De applicatie draait dan op `http://localhost:5000`

## Troubleshooting

### Fout: "supabase_url is required"
- Controleer of je `.env` bestand bestaat
- Controleer of `SUPABASE_URL` correct is ingesteld

### Fout: "SUPABASE_SERVICE_ROLE_KEY is niet ingesteld"
- Controleer of je `.env` bestand bestaat
- Controleer of `SUPABASE_SERVICE_ROLE_KEY` correct is ingesteld
- Zorg ervoor dat je de **service_role** key gebruikt, niet de **anon** key

### Database connectie fout
- Controleer of je Supabase project actief is
- Controleer of je de juiste URL en key gebruikt
- Controleer of je het database setup script hebt uitgevoerd 