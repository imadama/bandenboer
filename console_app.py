#!/usr/bin/env python3
"""
Console versie van de Banden Voorraad Beheer applicatie
"""

from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Fout: SUPABASE_URL en SUPABASE_SERVICE_ROLE_KEY moeten ingesteld zijn in .env bestand")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

class ConsoleBandenVoorraad:
    def __init__(self):
        self.test_connection()
    
    def test_connection(self):
        """Test database connectie"""
        try:
            supabase.table('tires').select('*').limit(1).execute()
            print("✅ Database connectie succesvol!")
        except Exception as e:
            print(f"❌ Database connectie fout: {e}")
            print("Zorg ervoor dat je de database_setup.sql hebt uitgevoerd in Supabase")
            sys.exit(1)
    
    def show_menu(self):
        """Toon hoofdmenu"""
        print("\n" + "="*50)
        print("🚗 BANDEN VOORRAAD BEHEER - CONSOLE VERSIE")
        print("="*50)
        print("1. Voorraad bekijken")
        print("2. Banden toevoegen")
        print("3. Banden bewerken")
        print("4. Banden verwijderen")
        print("5. Reservering maken")
        print("6. Reserveringen bekijken")
        print("7. Reserveringen per klant")
        print("0. Afsluiten")
        print("-"*50)
    
    def show_inventory(self):
        """Toon voorraad overzicht"""
        print("\n📋 VOORRAAD OVERZICHT")
        print("-"*50)
        
        # Nieuwe banden
        new_tires = supabase.table('tires').select('*').eq('condition', 'new').execute()
        print(f"\n🆕 NIEUWE BANDEN ({len(new_tires.data)} items):")
        if new_tires.data:
            for tire in new_tires.data:
                stock_status = "🔴" if tire['stock'] < 5 else "🟢"
                print(f"  {stock_status} {tire['brand']} {tire['size']} ({tire['tire_type']}) - Voorraad: {tire['stock']}")
        else:
            print("  Geen nieuwe banden in voorraad")
        
        # Tweedehands banden
        used_tires = supabase.table('tires').select('*').eq('condition', 'used').execute()
        print(f"\n♻️  TWEEDEHANDS BANDEN ({len(used_tires.data)} items):")
        if used_tires.data:
            for tire in used_tires.data:
                stock_status = "🔴" if tire['stock'] < 5 else "🟢"
                print(f"  {stock_status} {tire['brand']} {tire['size']} ({tire['tire_type']}) - Voorraad: {tire['stock']}")
        else:
            print("  Geen tweedehands banden in voorraad")
        
        # Statistieken
        total_tires = len(new_tires.data) + len(used_tires.data)
        total_stock = sum(tire['stock'] for tire in new_tires.data + used_tires.data)
        low_stock = len([t for t in new_tires.data + used_tires.data if t['stock'] < 5])
        
        print(f"\n📊 STATISTIEKEN:")
        print(f"  Totaal banden: {total_tires}")
        print(f"  Totaal voorraad: {total_stock}")
        print(f"  Lage voorraad: {low_stock}")
    
    def add_tire(self):
        """Voeg nieuwe banden toe"""
        print("\n➕ NIEUWE BANDEN TOEVOEGEN")
        print("-"*50)
        
        try:
            print("\nMerk:")
            print("1. Michelin")
            print("2. Continental")
            print("3. Vredestein")
            print("4. Bridgestone")
            print("5. Goodyear")
            print("6. Dunlop")
            print("7. Pirelli")
            print("8. Hankook")
            print("9. Kumho Tyres")
            print("10. Hifly")
            brand_choice = input("Keuze (1-10): ").strip()
            brands = {
                '1': 'Michelin', '2': 'Continental', '3': 'Vredestein', '4': 'Bridgestone',
                '5': 'Goodyear', '6': 'Dunlop', '7': 'Pirelli', '8': 'Hankook',
                '9': 'Kumho Tyres', '10': 'Hifly'
            }
            brand = brands.get(brand_choice)
            if not brand:
                print("❌ Ongeldige keuze!")
                return
            
            print("Maat (formaat: xxx/xx/Rxx)")
            print("Bijvoorbeeld: 205/55R16, 225/45R17, 195/65R15")
            size = input("Voer maat in: ").strip()
            if not size:
                print("❌ Maat is verplicht!")
                return
            
            # Eenvoudige validatie voor formaat xxx/xx/Rxx
            import re
            if not re.match(r'^\d{3}/\d{2}R\d{2}$', size):
                print("❌ Ongeldig formaat! Gebruik formaat: xxx/xx/Rxx (bijv. 205/55R16)")
                return
            
            print("\nType:")
            print("1. Zomer")
            print("2. Winter")
            print("3. All Season")
            type_choice = input("Keuze (1-3): ").strip()
            tire_types = {'1': 'zomer', '2': 'winter', '3': 'all_season'}
            tire_type = tire_types.get(type_choice)
            if not tire_type:
                print("❌ Ongeldige keuze!")
                return
            
            print("\nConditie:")
            print("1. Nieuw")
            print("2. Tweedehands")
            condition_choice = input("Keuze (1-2): ").strip()
            conditions = {'1': 'new', '2': 'used'}
            condition = conditions.get(condition_choice)
            if not condition:
                print("❌ Ongeldige keuze!")
                return
            
            stock = input("Aantal op voorraad: ").strip()
            try:
                stock = int(stock)
                if stock < 0:
                    raise ValueError()
            except ValueError:
                print("❌ Ongeldig aantal!")
                return
            
            price = input("Inkoopprijs (€, optioneel): ").strip()
            try:
                price = float(price) if price else None
            except ValueError:
                print("❌ Ongeldige prijs!")
                return
            
            # Voeg toe aan database
            data = {
                'brand': brand,
                'size': size,
                'tire_type': tire_type,
                'condition': condition,
                'stock': stock,
                'price': price
            }
            
            result = supabase.table('tires').insert(data).execute()
            print("✅ Banden succesvol toegevoegd!")
            
        except Exception as e:
            print(f"❌ Fout bij toevoegen: {e}")
    
    def edit_tire(self):
        """Bewerk bestaande banden"""
        print("\n✏️  BANDEN BEWERKEN")
        print("-"*50)
        
        # Toon beschikbare banden
        tires = supabase.table('tires').select('*').execute()
        if not tires.data:
            print("❌ Geen banden gevonden!")
            return
        
        print("Beschikbare banden:")
        for i, tire in enumerate(tires.data, 1):
            print(f"  {i}. {tire['brand']} {tire['size']} ({tire['condition']}) - Voorraad: {tire['stock']}")
        
        try:
            choice = int(input("\nSelecteer band (nummer): ")) - 1
            if choice < 0 or choice >= len(tires.data):
                print("❌ Ongeldige keuze!")
                return
            
            tire = tires.data[choice]
            print(f"\nBewerken van: {tire['brand']} {tire['size']}")
            
            # Nieuwe waarden invoeren
            brands = {
                '1': 'Michelin', '2': 'Continental', '3': 'Vredestein', '4': 'Bridgestone',
                '5': 'Goodyear', '6': 'Dunlop', '7': 'Pirelli', '8': 'Hankook',
                '9': 'Kumho Tyres', '10': 'Hifly'
            }
            print(f"\nMerk (huidig: {tire['brand']}):")
            print("1. Michelin")
            print("2. Continental")
            print("3. Vredestein")
            print("4. Bridgestone")
            print("5. Goodyear")
            print("6. Dunlop")
            print("7. Pirelli")
            print("8. Hankook")
            print("9. Kumho Tyres")
            print("10. Hifly")
            brand_choice = input("Keuze (1-10, Enter voor huidige): ").strip()
            brand = brands.get(brand_choice) if brand_choice else tire['brand']
            print(f"Maat (huidig: {tire['size']})")
            print("Formaat: xxx/xx/Rxx (bijv. 205/55R16, 225/45R17)")
            size_input = input("Nieuwe maat (Enter voor huidige): ").strip()
            if size_input:
                # Eenvoudige validatie voor formaat xxx/xx/Rxx
                import re
                if not re.match(r'^\d{3}/\d{2}R\d{2}$', size_input):
                    print("❌ Ongeldig formaat! Gebruik formaat: xxx/xx/Rxx (bijv. 205/55R16)")
                    return
                size = size_input
            else:
                size = tire['size']
            
            tire_types = {'1': 'zomer', '2': 'winter', '3': 'all_season'}
            print(f"\nType (huidig: {tire['tire_type']}):")
            print("1. Zomer")
            print("2. Winter")
            print("3. All Season")
            type_choice = input("Keuze (1-3, Enter voor huidige): ").strip()
            tire_type = tire_types.get(type_choice) if type_choice else tire['tire_type']
            
            stock = input(f"Aantal op voorraad ({tire['stock']}): ").strip()
            try:
                stock = int(stock) if stock else tire['stock']
                if stock < 0:
                    raise ValueError()
            except ValueError:
                print("❌ Ongeldig aantal!")
                return
            
            price = input(f"Inkoopprijs (€, huidig: {tire['price'] or 'geen'}): ").strip()
            try:
                price = float(price) if price else tire['price']
            except ValueError:
                print("❌ Ongeldige prijs!")
                return
            
            # Update database
            data = {
                'brand': brand,
                'size': size,
                'tire_type': tire_type,
                'stock': stock,
                'price': price
            }
            
            supabase.table('tires').update(data).eq('id', tire['id']).execute()
            print("✅ Banden succesvol bijgewerkt!")
            
        except Exception as e:
            print(f"❌ Fout bij bewerken: {e}")
    
    def delete_tire(self):
        """Verwijder banden"""
        print("\n🗑️  BANDEN VERWIJDEREN")
        print("-"*50)
        
        # Toon beschikbare banden
        tires = supabase.table('tires').select('*').execute()
        if not tires.data:
            print("❌ Geen banden gevonden!")
            return
        
        print("Beschikbare banden:")
        for i, tire in enumerate(tires.data, 1):
            print(f"  {i}. {tire['brand']} {tire['size']} ({tire['condition']}) - Voorraad: {tire['stock']}")
        
        try:
            choice = int(input("\nSelecteer band (nummer): ")) - 1
            if choice < 0 or choice >= len(tires.data):
                print("❌ Ongeldige keuze!")
                return
            
            tire = tires.data[choice]
            confirm = input(f"\nWeet je zeker dat je {tire['brand']} {tire['size']} wilt verwijderen? (j/N): ").strip().lower()
            
            if confirm == 'j':
                supabase.table('tires').delete().eq('id', tire['id']).execute()
                print("✅ Banden succesvol verwijderd!")
            else:
                print("❌ Verwijderen geannuleerd.")
                
        except Exception as e:
            print(f"❌ Fout bij verwijderen: {e}")
    
    def make_reservation(self):
        """Maak nieuwe reservering"""
        print("\n📅 NIEUWE RESERVERING")
        print("-"*50)
        
        # Toon beschikbare banden
        available_tires = supabase.table('tires').select('*').gte('stock', 1).execute()
        if not available_tires.data:
            print("❌ Geen beschikbare banden!")
            return
        
        print("Beschikbare banden:")
        for i, tire in enumerate(available_tires.data, 1):
            print(f"  {i}. {tire['brand']} {tire['size']} ({tire['condition']}) - Voorraad: {tire['stock']}")
        
        try:
            choice = int(input("\nSelecteer band (nummer): ")) - 1
            if choice < 0 or choice >= len(available_tires.data):
                print("❌ Ongeldige keuze!")
                return
            
            tire = available_tires.data[choice]
            customer_name = input("Klantnaam: ").strip()
            if not customer_name:
                print("❌ Klantnaam is verplicht!")
                return
            
            date_str = input("Datum (YYYY-MM-DD, Enter voor vandaag): ").strip()
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print("❌ Ongeldige datum!")
                return
            
            notes = input("Opmerkingen (optioneel): ").strip()
            
            # Maak reservering
            reservation_data = {
                'tire_id': tire['id'],
                'customer_name': customer_name,
                'reservation_date': date_str,
                'notes': notes
            }
            
            # Controleer voorraad en maak reservering
            if tire['stock'] < 1:
                print("❌ Niet genoeg voorraad!")
                return
            
            # Maak reservering en verminder voorraad
            supabase.table('reservations').insert(reservation_data).execute()
            supabase.table('tires').update({'stock': tire['stock'] - 1}).eq('id', tire['id']).execute()
            
            print("✅ Reservering succesvol gemaakt!")
            
        except Exception as e:
            print(f"❌ Fout bij reserveren: {e}")
    
    def show_reservations(self):
        """Toon alle reserveringen"""
        print("\n📋 ALLE RESERVERINGEN")
        print("-"*50)
        
        reservations = supabase.table('reservations').select('*, tires(*)').order('reservation_date', desc=True).execute()
        
        if not reservations.data:
            print("❌ Geen reserveringen gevonden!")
            return
        
        for reservation in reservations.data:
            tire = reservation['tires']
            print(f"📅 {reservation['reservation_date']} - {reservation['customer_name']}")
            print(f"   🚗 {tire['brand']} {tire['size']} ({tire['condition']})")
            if reservation['notes']:
                print(f"   📝 {reservation['notes']}")
            print()
    
    def show_customer_reservations(self):
        """Toon reserveringen per klant"""
        print("\n👤 RESERVERINGEN PER KLANT")
        print("-"*50)
        
        customer_name = input("Klantnaam: ").strip()
        if not customer_name:
            print("❌ Klantnaam is verplicht!")
            return
        
        reservations = supabase.table('reservations').select('*, tires(*)').eq('customer_name', customer_name).execute()
        
        if not reservations.data:
            print(f"❌ Geen reserveringen gevonden voor {customer_name}")
            return
        
        print(f"\n📋 Reserveringen van {customer_name}:")
        for reservation in reservations.data:
            tire = reservation['tires']
            print(f"  📅 {reservation['reservation_date']} - {tire['brand']} {tire['size']} ({tire['condition']})")
            if reservation['notes']:
                print(f"     📝 {reservation['notes']}")
    
    def run(self):
        """Start de console applicatie"""
        print("🚗 Welkom bij Banden Voorraad Beheer!")
        
        while True:
            self.show_menu()
            choice = input("Keuze (0-7): ").strip()
            
            if choice == '0':
                print("👋 Tot ziens!")
                break
            elif choice == '1':
                self.show_inventory()
            elif choice == '2':
                self.add_tire()
            elif choice == '3':
                self.edit_tire()
            elif choice == '4':
                self.delete_tire()
            elif choice == '5':
                self.make_reservation()
            elif choice == '6':
                self.show_reservations()
            elif choice == '7':
                self.show_customer_reservations()
            else:
                print("❌ Ongeldige keuze!")

if __name__ == '__main__':
    app = ConsoleBandenVoorraad()
    app.run() 