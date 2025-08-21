# Banden Voorraad Beheer

Een Python Flask-applicatie voor het beheren van een bandenvoorraad met Supabase als database backend.

## Functies

- **Voorraad Beheer**: Toevoegen, wijzigen en verwijderen van banden
- **Twee Categorieën**: Nieuwe en tweedehands banden, apart zichtbaar
- **Reserveringen**: Banden reserveren op klantnaam en datum
- **Automatische Voorraad**: Voorraad wordt automatisch verminderd bij reservering
- **Klant Overzicht**: Bekijk alle reserveringen per klant
- **Moderne Interface**: Responsive web interface met Bootstrap

## Vereisten

- Python 3.8+
- Supabase account
- PostgreSQL database (via Supabase)

## Installatie

### 1. Clone de repository
```bash
git clone <repository-url>
cd bandenboer
```

### 2. Installeer dependencies
```bash
pip install -r requirements.txt
```

### 3. Supabase Setup

1. Ga naar [Supabase](https://supabase.com) en maak een nieuw project
2. Ga naar de SQL Editor in je Supabase dashboard
3. Voer het `database_setup.sql` script uit om de tabellen aan te maken
4. Ga naar Settings > API om je project URL en service role key te vinden

### 4. Environment Variables

Kopieer `env.example` naar `.env` en vul je Supabase gegevens in:

```bash
cp env.example .env
```

Bewerk `.env`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Start de applicatie
```bash
python app.py
```

De applicatie is nu beschikbaar op `http://localhost:5000`

## Database Schema

### Tires Table
- `id`: Primary key
- `brand`: Merk van de banden
- `size`: Maat (breedte/hoogte/velg)
- `tire_type`: Type (zomer/winter/all_season)
- `condition`: Conditie (new/used)
- `stock`: Aantal op voorraad
- `price`: Inkoopprijs (optioneel)
- `created_at`: Aanmaakdatum
- `updated_at`: Laatste wijziging

### Reservations Table
- `id`: Primary key
- `tire_id`: Foreign key naar tires
- `customer_name`: Naam van de klant
- `reservation_date`: Reserveringsdatum
- `notes`: Optionele opmerkingen
- `created_at`: Aanmaakdatum

## Gebruik

### Web Interface
Start de Flask applicatie:
```bash
python app.py
```

#### Voorraad Beheren
1. Ga naar "Banden Toevoegen" om nieuwe banden toe te voegen
2. Vul alle verplichte velden in (merk, maat, type, conditie, voorraad)
3. Gebruik het overzicht om banden te bewerken of verwijderen

#### Reserveringen
1. Ga naar "Reserveringen" om een nieuwe reservering te maken
2. Selecteer beschikbare banden, vul klantnaam en datum in
3. De voorraad wordt automatisch verminderd
4. Bekijk reserveringen per klant door op de klantnaam te klikken

#### Overzicht
- Het hoofdoverzicht toont nieuwe en tweedehands banden gescheiden
- Statistieken tonen totaal aantal banden en lage voorraad
- Kleurcodering: groen voor nieuwe, oranje voor tweedehands banden

### Console Interface
Voor gebruikers die liever een command-line interface willen:
```bash
python console_app.py
```

De console versie biedt dezelfde functionaliteit als de web interface, maar via een interactieve terminal interface.

## API Endpoints

- `GET /`: Hoofdpagina met voorraad overzicht
- `GET/POST /tires/add`: Nieuwe banden toevoegen
- `GET/POST /tires/edit/<id>`: Banden bewerken
- `POST /tires/delete/<id>`: Banden verwijderen
- `GET/POST /reservations`: Reserveringen beheren
- `GET /reservations/customer/<name>`: Reserveringen per klant

## Uitbreidingen

De applicatie is modulair opgezet en eenvoudig uit te breiden:

- **Gebruikersbeheer**: Toevoegen van authenticatie
- **Facturering**: Integratie met facturatie systeem
- **Leveranciers**: Beheer van leveranciers en bestellingen
- **Rapporten**: Uitgebreide rapportage functionaliteit
- **API**: REST API voor externe integraties

## Troubleshooting

### Database Connectie Problemen
- Controleer of je Supabase URL en key correct zijn
- Zorg dat je service role key gebruikt (niet anon key)
- Controleer of de tabellen correct zijn aangemaakt

### Flask Errors
- Controleer of alle dependencies zijn geïnstalleerd
- Zorg dat je `.env` bestand correct is ingesteld
- Controleer de Flask logs voor specifieke foutmeldingen

## Licentie

Dit project is open source en beschikbaar onder de MIT licentie.

## Support

Voor vragen of problemen, maak een issue aan in de repository. 