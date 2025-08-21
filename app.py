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
supabase_url = os.getenv('SUPABASE_URL', 'https://tfcgwmxiqgnlyjtpymzy.supabase.co')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Check if we have the required configuration
if not supabase_key:
    print("❌ SUPABASE_SERVICE_ROLE_KEY is niet ingesteld!")
    print("🔧 Maak een .env bestand aan met je Supabase configuratie:")
    print("   SUPABASE_URL=https://tfcgwmxiqgnlyjtpymzy.supabase.co")
    print("   SUPABASE_SERVICE_ROLE_KEY=jouw-service-role-key-hier")
    print("   Ga naar je Supabase dashboard > Settings > API om de service role key te vinden")
    exit(1)

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
    
    def search_tires(self, search=None, condition=None, tire_type=None, stock_filter=None):
        """Search and filter tires"""
        query = supabase.table('tires').select('*')
        
        # Zoeken in merk, maat en type
        if search:
            query = query.or_(f'brand.ilike.%{search}%,size.ilike.%{search}%,tire_type.ilike.%{search}%')
        
        # Filter op conditie
        if condition:
            query = query.eq('condition', condition)
        
        # Filter op type
        if tire_type:
            query = query.eq('tire_type', tire_type)
        
        # Filter op voorraad
        if stock_filter:
            if stock_filter == 'in_stock':
                query = query.gt('stock', 0)
            elif stock_filter == 'low_stock':
                query = query.lt('stock', 5).gt('stock', 0)
            elif stock_filter == 'out_of_stock':
                query = query.eq('stock', 0)
        
        return query.order('created_at', desc=True).execute()
    
    def get_inventory_stats(self):
        """Get inventory statistics"""
        all_tires = supabase.table('tires').select('*').execute()
        
        if not all_tires.data:
            return {
                'total_tires': 0,
                'new_tires': 0,
                'used_tires': 0,
                'total_stock': 0,
                'low_stock': 0,
                'out_of_stock': 0
            }
        
        tires = all_tires.data
        total_stock = sum(tire['stock'] for tire in tires)
        new_tires = len([t for t in tires if t['condition'] == 'new'])
        used_tires = len([t for t in tires if t['condition'] == 'used'])
        low_stock = len([t for t in tires if 0 < t['stock'] < 5])
        out_of_stock = len([t for t in tires if t['stock'] == 0])
        
        return {
            'total_tires': len(tires),
            'new_tires': new_tires,
            'used_tires': used_tires,
            'total_stock': total_stock,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock
        }

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

@app.route('/inventory')
def inventory():
    """Inventory management page with search and filters"""
    search = request.args.get('search', '')
    condition = request.args.get('condition', '')
    tire_type = request.args.get('tire_type', '')
    stock_filter = request.args.get('stock_filter', '')
    
    # Get filtered tires
    tires_result = banden_voorraad.search_tires(
        search=search if search else None,
        condition=condition if condition else None,
        tire_type=tire_type if tire_type else None,
        stock_filter=stock_filter if stock_filter else None
    )
    
    # Get statistics
    stats = banden_voorraad.get_inventory_stats()
    
    return render_template('inventory.html', 
                         tires=tires_result.data,
                         stats=stats)

@app.route('/inventory/export')
def export_inventory():
    """Export inventory to CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    search = request.args.get('search', '')
    condition = request.args.get('condition', '')
    tire_type = request.args.get('tire_type', '')
    stock_filter = request.args.get('stock_filter', '')
    
    # Get filtered tires
    tires_result = banden_voorraad.search_tires(
        search=search if search else None,
        condition=condition if condition else None,
        tire_type=tire_type if tire_type else None,
        stock_filter=stock_filter if stock_filter else None
    )
    
    # Create CSV
    si = StringIO()
    cw = csv.writer(si)
    
    # Write header
    cw.writerow(['ID', 'Merk', 'Maat', 'Type', 'Conditie', 'Voorraad', 'Prijs', 'Aangemaakt', 'Bijgewerkt'])
    
    # Write data
    for tire in tires_result.data:
        cw.writerow([
            tire['id'],
            tire['brand'],
            tire['size'],
            tire['tire_type'],
            'Nieuw' if tire['condition'] == 'new' else 'Tweedehands',
            tire['stock'],
            f"€{tire['price']:.2f}" if tire['price'] else '',
            tire['created_at'][:10] if tire['created_at'] else '',
            tire['updated_at'][:10] if tire['updated_at'] else ''
        ])
    
    output = si.getvalue()
    si.close()
    
    # Create response
    response = Response(output, mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=voorraad_export.csv'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 