#!/usr/bin/env python3
"""
Test script voor Supabase connectie
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("🔍 Supabase Connectie Test")
print("="*40)
print(f"URL: {supabase_url}")
print(f"Key: {'Set' if supabase_key else 'Not set'}")

if not supabase_url or not supabase_key:
    print("\n❌ Fout: SUPABASE_URL en SUPABASE_SERVICE_ROLE_KEY moeten ingesteld zijn in .env bestand")
    exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Test connection
    result = supabase.table('tires').select('*').limit(1).execute()
    print("\n✅ Supabase connectie succesvol!")
    
    # Check if tables exist
    try:
        tires = supabase.table('tires').select('*').execute()
        print(f"📋 Tires tabel: {len(tires.data)} items gevonden")
    except Exception as e:
        print(f"❌ Tires tabel niet gevonden: {e}")
    
    try:
        reservations = supabase.table('reservations').select('*').execute()
        print(f"📅 Reservations tabel: {len(reservations.data)} items gevonden")
    except Exception as e:
        print(f"❌ Reservations tabel niet gevonden: {e}")
    
    print("\n🎉 Test succesvol voltooid!")
    
except Exception as e:
    print(f"\n❌ Fout bij connectie: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Controleer of je .env bestand correct is ingesteld")
    print("2. Controleer of je Supabase project URL correct is")
    print("3. Controleer of je service role key correct is")
    print("4. Voer database_setup.sql uit in je Supabase SQL Editor") 