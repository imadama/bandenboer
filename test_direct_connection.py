#!/usr/bin/env python3
"""
Test script voor directe PostgreSQL connectie met Supabase
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection parameters
connection_params = {
    'user': os.getenv('user', 'postgres'),
    'password': os.getenv('password', 'Bandenboer123!'),
    'host': os.getenv('host', 'db.tfcgwmxiqgnlyjtpymzy.supabase.co'),
    'port': os.getenv('port', '5432'),
    'dbname': os.getenv('dbname', 'postgres')
}

print("🔍 Direct PostgreSQL Connectie Test")
print("="*50)
print(f"Host: {connection_params['host']}")
print(f"Port: {connection_params['port']}")
print(f"Database: {connection_params['dbname']}")
print(f"User: {connection_params['user']}")
print(f"Password: {'*' * len(connection_params['password'])}")

try:
    # Connect to the database
    connection = psycopg2.connect(**connection_params)
    print("\n✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    
    # Test query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"🕐 Current Time: {result['now']}")

    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('tires', 'reservations');
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"📋 Existing tables: {[table['table_name'] for table in tables]}")
    else:
        print("📋 No tables found - they will be created when you run the application")

    # Check tires if table exists
    try:
        cursor.execute("SELECT COUNT(*) as count FROM tires;")
        tire_count = cursor.fetchone()
        print(f"🚗 Tires in database: {tire_count['count']}")
    except:
        print("🚗 Tires table not found")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("🔒 Connection closed.")
    print("\n🎉 Database connectie test succesvol!")

except Exception as e:
    print(f"\n❌ Failed to connect: {e}")
    print("\n🔧 Troubleshooting tips:")
    print("1. Controleer of je .env bestand correct is ingesteld")
    print("2. Controleer of je database credentials correct zijn")
    print("3. Controleer of je netwerk connectie werkt")
    print("4. Controleer of de database server bereikbaar is")
    print("5. Controleer of je IP adres is toegestaan in Supabase") 