from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'user': os.getenv('user', 'postgres'),
            'password': os.getenv('password', 'Bandenboer123!'),
            'host': os.getenv('host', 'db.tfcgwmxiqgnlyjtpymzy.supabase.co'),
            'port': os.getenv('port', '5432'),
            'dbname': os.getenv('dbname', 'postgres')
        }
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class BandenVoorraad:
    def __init__(self):
        self.db = DatabaseConnection()
        self.setup_database()
    
    def setup_database(self):
        """Setup database tables if they don't exist"""
        try:
            # Test connection
            self.db.execute_query("SELECT NOW();")
            print("✅ Database connectie succesvol!")
            
            # Create tables if they don't exist
            self.create_tables()
        except Exception as e:
            print(f"❌ Database connectie fout: {e}")
            print("🔧 Controleer je .env bestand en database instellingen")
    
    def create_tables(self):
        """Create database tables"""
        # Create tires table
        tires_table = """
        CREATE TABLE IF NOT EXISTS tires (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(100) NOT NULL,
            size VARCHAR(50) NOT NULL,
            tire_type VARCHAR(20) NOT NULL CHECK (tire_type IN ('zomer', 'winter', 'all_season')),
            condition VARCHAR(10) NOT NULL CHECK (condition IN ('new', 'used')),
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            price DECIMAL(10,2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create reservations table
        reservations_table = """
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            tire_id INTEGER NOT NULL REFERENCES tires(id) ON DELETE CASCADE,
            customer_name VARCHAR(100) NOT NULL,
            reservation_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tires_condition ON tires(condition);",
            "CREATE INDEX IF NOT EXISTS idx_tires_brand ON tires(brand);",
            "CREATE INDEX IF NOT EXISTS idx_tires_stock ON tires(stock);",
            "CREATE INDEX IF NOT EXISTS idx_reservations_customer ON reservations(customer_name);",
            "CREATE INDEX IF NOT EXISTS idx_reservations_date ON reservations(reservation_date);",
            "CREATE INDEX IF NOT EXISTS idx_reservations_tire ON reservations(tire_id);"
        ]
        
        # Create trigger function
        trigger_function = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
        
        # Create trigger
        trigger = """
        DROP TRIGGER IF EXISTS update_tires_updated_at ON tires;
        CREATE TRIGGER update_tires_updated_at 
            BEFORE UPDATE ON tires 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        try:
            self.db.execute_query(tires_table, fetch=False)
            self.db.execute_query(reservations_table, fetch=False)
            
            for index in indexes:
                self.db.execute_query(index, fetch=False)
            
            self.db.execute_query(trigger_function, fetch=False)
            self.db.execute_query(trigger, fetch=False)
            
            print("✅ Database tabellen succesvol aangemaakt!")
        except Exception as e:
            print(f"❌ Fout bij aanmaken tabellen: {e}")
    
    def get_all_tires(self, condition='all'):
        """Get all tires, optionally filtered by condition"""
        if condition == 'all':
            query = "SELECT * FROM tires ORDER BY created_at DESC;"
            return self.db.execute_query(query)
        else:
            query = "SELECT * FROM tires WHERE condition = %s ORDER BY created_at DESC;"
            return self.db.execute_query(query, (condition,))
    
    def add_tire(self, data):
        """Add a new tire to inventory"""
        query = """
        INSERT INTO tires (brand, size, tire_type, condition, stock, price)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        return self.db.execute_query(query, (
            data['brand'], data['size'], data['tire_type'], 
            data['condition'], data['stock'], data['price']
        ))
    
    def update_tire(self, tire_id, data):
        """Update tire information"""
        query = """
        UPDATE tires 
        SET brand = %s, size = %s, tire_type = %s, condition = %s, stock = %s, price = %s
        WHERE id = %s;
        """
        return self.db.execute_query(query, (
            data['brand'], data['size'], data['tire_type'], 
            data['condition'], data['stock'], data['price'], tire_id
        ), fetch=False)
    
    def delete_tire(self, tire_id):
        """Delete a tire from inventory"""
        query = "DELETE FROM tires WHERE id = %s;"
        return self.db.execute_query(query, (tire_id,), fetch=False)
    
    def get_tire_by_id(self, tire_id):
        """Get tire by ID"""
        query = "SELECT * FROM tires WHERE id = %s;"
        result = self.db.execute_query(query, (tire_id,))
        return result[0] if result else None
    
    def reserve_tire(self, data):
        """Reserve a tire for a customer"""
        # First check if tire is available
        tire = self.get_tire_by_id(data['tire_id'])
        if not tire or tire['stock'] < 1:
            raise Exception("Tire not available")
        
        # Create reservation
        reservation_query = """
        INSERT INTO reservations (tire_id, customer_name, reservation_date, notes)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        self.db.execute_query(reservation_query, (
            data['tire_id'], data['customer_name'], 
            data['reservation_date'], data['notes']
        ))
        
        # Reduce stock
        update_query = "UPDATE tires SET stock = stock - 1 WHERE id = %s;"
        self.db.execute_query(update_query, (data['tire_id'],), fetch=False)
        
        return True
    
    def get_reservations(self, customer_name=None):
        """Get all reservations, optionally filtered by customer"""
        if customer_name:
            query = """
            SELECT r.*, t.brand, t.size, t.tire_type, t.condition
            FROM reservations r
            JOIN tires t ON r.tire_id = t.id
            WHERE r.customer_name = %s
            ORDER BY r.reservation_date DESC;
            """
            return self.db.execute_query(query, (customer_name,))
        else:
            query = """
            SELECT r.*, t.brand, t.size, t.tire_type, t.condition
            FROM reservations r
            JOIN tires t ON r.tire_id = t.id
            ORDER BY r.reservation_date DESC;
            """
            return self.db.execute_query(query)
    
    def get_available_tires(self):
        """Get tires with stock > 0"""
        query = "SELECT * FROM tires WHERE stock > 0 ORDER BY brand, size;"
        return self.db.execute_query(query)

# Initialize the application
banden_voorraad = BandenVoorraad()

@app.route('/')
def index():
    """Homepage with overview"""
    new_tires = banden_voorraad.get_all_tires('new')
    used_tires = banden_voorraad.get_all_tires('used')
    return render_template('index.html', new_tires=new_tires, used_tires=used_tires)

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
    tire = banden_voorraad.get_tire_by_id(tire_id)
    if not tire:
        flash('Banden niet gevonden!', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_tire.html', tire=tire)

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
    available_tires = banden_voorraad.get_available_tires()
    
    return render_template('reservations.html', 
                         reservations=reservations, 
                         available_tires=available_tires)

@app.route('/reservations/customer/<customer_name>')
def customer_reservations(customer_name):
    """View reservations for specific customer"""
    reservations = banden_voorraad.get_reservations(customer_name)
    return render_template('customer_reservations.html', 
                         reservations=reservations, 
                         customer_name=customer_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5002'))
    app.run(debug=True, host='0.0.0.0', port=port) 