from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

class BandenVoorraad:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """Setup database tables if they don't exist"""
        try:
            # Test de connectie door een eenvoudige query uit te voeren
            supabase.table('tires').select('*').limit(1).execute()
            print("✅ Database connectie succesvol!")
        except Exception as e:
            print(f"❌ Database connectie fout: {e}")
            print("🔧 Controleer je .env bestand:")
            print("   - SUPABASE_URL moet correct zijn")
            print("   - SUPABASE_SERVICE_ROLE_KEY moet correct zijn")
            print("   - Voer database_setup.sql uit in je Supabase SQL Editor")
    
    def get_all_tires(self, condition='all'):
        """Get all tires, optionally filtered by condition"""
        query = supabase.table('tires').select('*')
        if condition != 'all':
            query = query.eq('condition', condition)
        return query.order('created_at', desc=True).execute()
    
    def add_tire(self, data):
        """Add a new tire to inventory"""
        return supabase.table('tires').insert(data).execute()
    
    def update_tire(self, tire_id, data):
        """Update tire information"""
        return supabase.table('tires').update(data).eq('id', tire_id).execute()
    
    def delete_tire(self, tire_id):
        """Delete a tire from inventory"""
        return supabase.table('tires').delete().eq('id', tire_id).execute()
    
    def reserve_tire(self, data):
        """Reserve a tire for a customer"""
        # First check if tire is available
        tire = supabase.table('tires').select('*').eq('id', data['tire_id']).execute()
        if not tire.data or tire.data[0]['stock'] < 1:
            raise Exception("Tire not available")
        
        # Create reservation
        reservation = supabase.table('reservations').insert(data).execute()
        
        # Reduce stock
        supabase.table('tires').update({'stock': tire.data[0]['stock'] - 1}).eq('id', data['tire_id']).execute()
        
        return reservation
    
    def get_reservations(self, customer_name=None):
        """Get all reservations, optionally filtered by customer"""
        query = supabase.table('reservations').select('*, tires(*)')
        if customer_name:
            query = query.eq('customer_name', customer_name)
        return query.order('reservation_date', desc=True).execute()

# Initialize the application
banden_voorraad = BandenVoorraad()

@app.route('/')
def index():
    """Homepage with overview"""
    new_tires = banden_voorraad.get_all_tires('new')
    used_tires = banden_voorraad.get_all_tires('used')
    return render_template('index.html', new_tires=new_tires.data, used_tires=used_tires.data)

@app.route('/tires/add', methods=['GET', 'POST'])
def add_tire():
    """Add new tire to inventory"""
    if request.method == 'POST':
        data = {
            'brand': request.form['brand'],
            'size': request.form['size'],
            'tire_type': request.form['tire_type'],
            'condition': request.form['condition'],
            'stock': int(request.form['stock']),
            'price': float(request.form['price']) if request.form['price'] else None
        }
        
        try:
            banden_voorraad.add_tire(data)
            flash('Banden succesvol toegevoegd!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Fout bij toevoegen: {str(e)}', 'error')
    
    return render_template('add_tire.html')

@app.route('/tires/edit/<int:tire_id>', methods=['GET', 'POST'])
def edit_tire(tire_id):
    """Edit existing tire"""
    if request.method == 'POST':
        data = {
            'brand': request.form['brand'],
            'size': request.form['size'],
            'tire_type': request.form['tire_type'],
            'condition': request.form['condition'],
            'stock': int(request.form['stock']),
            'price': float(request.form['price']) if request.form['price'] else None
        }
        
        try:
            banden_voorraad.update_tire(tire_id, data)
            flash('Banden succesvol bijgewerkt!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Fout bij bijwerken: {str(e)}', 'error')
    
    # Get tire data for form
    tire = supabase.table('tires').select('*').eq('id', tire_id).execute()
    if not tire.data:
        flash('Banden niet gevonden!', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_tire.html', tire=tire.data[0])

@app.route('/tires/delete/<int:tire_id>', methods=['POST'])
def delete_tire(tire_id):
    """Delete tire from inventory"""
    try:
        banden_voorraad.delete_tire(tire_id)
        flash('Banden succesvol verwijderd!', 'success')
    except Exception as e:
        flash(f'Fout bij verwijderen: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    """Manage reservations"""
    if request.method == 'POST':
        data = {
            'tire_id': int(request.form['tire_id']),
            'customer_name': request.form['customer_name'],
            'reservation_date': request.form['reservation_date'],
            'notes': request.form.get('notes', '')
        }
        
        try:
            banden_voorraad.reserve_tire(data)
            flash('Reservering succesvol gemaakt!', 'success')
            return redirect(url_for('reservations'))
        except Exception as e:
            flash(f'Fout bij reserveren: {str(e)}', 'error')
    
    # Get all reservations and available tires
    reservations = banden_voorraad.get_reservations()
    available_tires = supabase.table('tires').select('*').gte('stock', 1).execute()
    
    return render_template('reservations.html', 
                         reservations=reservations.data, 
                         available_tires=available_tires.data)

@app.route('/reservations/customer/<customer_name>')
def customer_reservations(customer_name):
    """View reservations for specific customer"""
    reservations = banden_voorraad.get_reservations(customer_name)
    return render_template('customer_reservations.html', 
                         reservations=reservations.data, 
                         customer_name=customer_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 