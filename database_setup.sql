-- Database setup voor Banden Voorraad Beheer
-- Voer dit script uit in je Supabase SQL Editor

-- Tires table (Banden tabel)
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

-- Reservations table (Reserveringen tabel)
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    tire_id INTEGER NOT NULL REFERENCES tires(id) ON DELETE CASCADE,
    customer_name VARCHAR(100) NOT NULL,
    reservation_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes voor betere performance
CREATE INDEX IF NOT EXISTS idx_tires_condition ON tires(condition);
CREATE INDEX IF NOT EXISTS idx_tires_brand ON tires(brand);
CREATE INDEX IF NOT EXISTS idx_tires_stock ON tires(stock);
CREATE INDEX IF NOT EXISTS idx_reservations_customer ON reservations(customer_name);
CREATE INDEX IF NOT EXISTS idx_reservations_date ON reservations(reservation_date);
CREATE INDEX IF NOT EXISTS idx_reservations_tire ON reservations(tire_id);

-- Trigger voor updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tires_updated_at 
    BEFORE UPDATE ON tires 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data voor testing (optioneel)
INSERT INTO tires (brand, size, tire_type, condition, stock, price) VALUES
('Michelin', '205/55R16', 'zomer', 'new', 10, 89.99),
('Bridgestone', '225/45R17', 'winter', 'new', 8, 129.99),
('Continental', '195/65R15', 'all_season', 'new', 15, 79.99),
('Pirelli', '215/55R17', 'zomer', 'used', 4, 45.00),
('Goodyear', '205/60R16', 'all_season', 'used', 6, 35.00),
('Dunlop', '225/40R18', 'winter', 'new', 12, 149.99),
('Hankook', '195/55R16', 'zomer', 'new', 20, 65.99),
('Yokohama', '215/50R17', 'all_season', 'used', 3, 40.00);

-- Sample reservations
INSERT INTO reservations (tire_id, customer_name, reservation_date, notes) VALUES
(1, 'Jan Jansen', '2024-01-15', 'Voor VW Golf'),
(2, 'Piet Pietersen', '2024-01-16', 'Winterbanden nodig'),
(4, 'Marie de Vries', '2024-01-17', 'Budget optie'),
(6, 'Klaas Klaassen', '2024-01-18', 'Voor BMW 3-serie');

-- RLS (Row Level Security) policies (optioneel voor productie)
-- ALTER TABLE tires ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;

-- Grant permissions (pas aan naar jouw gebruikers)
-- GRANT ALL ON TABLE tires TO authenticated;
-- GRANT ALL ON TABLE reservations TO authenticated;
-- GRANT USAGE, SELECT ON SEQUENCE tires_id_seq TO authenticated;
-- GRANT USAGE, SELECT ON SEQUENCE reservations_id_seq TO authenticated; 