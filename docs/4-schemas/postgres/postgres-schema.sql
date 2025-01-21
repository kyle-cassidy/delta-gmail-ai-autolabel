-- PostgreSQL schema for Delta Analytics Registration Tracking System

-- Enable UUID extension for ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE business_type_enum AS ENUM (
    'Corporation',
    'Limited Liability Corporation',
    'Partnership', 
    'Individual',
    'Sole Proprietor'
);

CREATE TYPE registration_status_enum AS ENUM (
    'Planned',
    'No Submission',
    'Approved',
    'Approved - Initial',
    'Not Regulated',
    'Pending',
    'Pending - Response',
    'Provisional',
    'Automatic w/ License',
    'Denied',
    'Cancelled',
    'D1',
    'D2',
    'Client Managed',
    'Not Needed',
    'Unknown',
    'TON Required',
    'TON Not Required'
);

-- Clients table (formerly Client List)
CREATE TABLE clients (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    comp_code VARCHAR(50) UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    business_type business_type_enum,
    epa_company_number VARCHAR(50),
    is_inactive BOOLEAN DEFAULT false,
    manage_renewals BOOLEAN DEFAULT false,
    manage_tonnage BOOLEAN DEFAULT false,
    producing_selling_product BOOLEAN DEFAULT false,
    parent_company_id uuid REFERENCES clients(id),
    -- Contact Information
    company_address1 VARCHAR(255),
    company_address2 VARCHAR(255),
    company_city VARCHAR(100),
    company_state VARCHAR(2),
    company_zip VARCHAR(20),
    company_county VARCHAR(100),
    company_country VARCHAR(100),
    company_contact VARCHAR(255),
    company_contact_title VARCHAR(255),
    company_contact_phone VARCHAR(50),
    primary_contact_email VARCHAR(255),
    emergency_contact_name VARCHAR(255),
    emergency_phone VARCHAR(50),
    has_24hr_phone BOOLEAN DEFAULT false,
    -- Tax Information
    fein_tax_id VARCHAR(50),
    state_incorporated VARCHAR(2),
    date_incorporated DATE,
    -- Label Information
    company_name_label VARCHAR(255),
    street_address_label TEXT,
    city_label VARCHAR(100),
    state_label VARCHAR(2),
    zip_label VARCHAR(20),
    manufacturer_name VARCHAR(255),
    manufacturer_address TEXT,
    -- Corporate Officer Information (for NY)
    corporate_officer_name VARCHAR(255),
    corporate_officer_title VARCHAR(255),
    -- Billing Information
    billing_level INTEGER,
    last_billing_increase DATE,
    -- Additional Information
    organic_registrations VARCHAR(50),
    tonnage_contact_email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_billing_level CHECK (billing_level BETWEEN 1 AND 10)
);

-- Products table
CREATE TABLE products (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    company_id uuid NOT NULL REFERENCES clients(id),
    active BOOLEAN DEFAULT true,
    material_state VARCHAR(50),
    grade VARCHAR(50),
    density NUMERIC(10, 4),
    density_unit VARCHAR(10),
    package_size NUMERIC(10, 2),
    package_unit VARCHAR(10),
    net_weight_lbs NUMERIC(10, 2),
    fertilizer_code INTEGER,
    is_repack BOOLEAN DEFAULT false,
    repack_company_id uuid REFERENCES clients(id),
    repack_product_id uuid REFERENCES products(id),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create enum for product types
CREATE TYPE product_type_enum AS ENUM (
    'Fertilizer',
    'Soil/Plant Amendment',
    'Biological Inoculant',
    'Adjuvant',
    'Wetting Agent',
    'PGR',
    'Specialty Fertilizer',
    'Not Regulated',
    'Legume Inoculant',
    'Pesticide',
    'Liming Material',
    'Surfactant'
);

-- Product Types junction table (many-to-many)
CREATE TABLE product_types (
    product_id uuid REFERENCES products(id),
    product_type product_type_enum,
    PRIMARY KEY (product_id, product_type)
);

-- States table
CREATE TABLE states (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    state_id VARCHAR(2) UNIQUE NOT NULL,
    state_name TEXT NOT NULL,
    check_payable_to TEXT,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    address_line3 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Registration Tracking table
CREATE TABLE registrations (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id uuid NOT NULL REFERENCES products(id),
    company_id uuid NOT NULL REFERENCES clients(id),
    state_id uuid NOT NULL REFERENCES states(id),
    registration_status registration_status_enum NOT NULL,
    certificate_exp DATE,
    initial_sub_date DATE,
    approval_received DATE,
    cancellation_effective DATE,
    submission_date DATE,
    registration_number VARCHAR(100),
    internal_action_needed BOOLEAN DEFAULT false,
    submission_notes TEXT,
    -- Renewal fields
    renewal_status VARCHAR(50),
    renewal_reminder_received BOOLEAN DEFAULT false,
    ready_to_mail BOOLEAN DEFAULT false,
    submitted BOOLEAN DEFAULT false,
    day_of_month_due INTEGER,
    -- Tracking fields
    priority_phase INTEGER,
    pll_phase INTEGER,
    label_change_request TEXT,
    label_update_submission DATE,
    label_update_needed BOOLEAN DEFAULT false,
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by uuid,  -- References users table (to be created)
    updated_by uuid,  -- References users table (to be created)
    CONSTRAINT valid_priority_phase CHECK (priority_phase BETWEEN 1 AND 4),
    CONSTRAINT valid_pll_phase CHECK (pll_phase BETWEEN 1 AND 4)
);

-- Client Logins table
CREATE TABLE client_logins (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id uuid NOT NULL REFERENCES clients(id),
    state_id uuid REFERENCES states(id),
    classification VARCHAR(50),
    regulation_type VARCHAR(50),
    website VARCHAR(255),
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Should be properly hashed
    usa_plant_id VARCHAR(100),
    license_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Audit trail table for tracking all changes
CREATE TABLE audit_log (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id uuid NOT NULL,
    action VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    user_id uuid,  -- References users table (to be created)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for common lookup patterns
CREATE INDEX idx_clients_comp_code ON clients(comp_code);
CREATE INDEX idx_clients_company_name ON clients(company_name);
CREATE INDEX idx_products_company_id ON products(company_id);
CREATE INDEX idx_registrations_product_id ON registrations(product_id);
CREATE INDEX idx_registrations_company_id ON registrations(company_id);
CREATE INDEX idx_registrations_state_id ON registrations(state_id);
CREATE INDEX idx_client_logins_company_id ON client_logins(company_id);
CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all tables
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_registrations_updated_at
    BEFORE UPDATE ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_client_logins_updated_at
    BEFORE UPDATE ON client_logins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create audit trail triggers
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        old_data = to_jsonb(OLD);
        INSERT INTO audit_log 
            (table_name, record_id, action, old_data, new_data)
        VALUES 
            (TG_TABLE_NAME, OLD.id, 'DELETE', old_data, null);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        old_data = to_jsonb(OLD);
        new_data = to_jsonb(NEW);
        INSERT INTO audit_log 
            (table_name, record_id, action, old_data, new_data)
        VALUES 
            (TG_TABLE_NAME, NEW.id, 'UPDATE', old_data, new_data);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        new_data = to_jsonb(NEW);
        INSERT INTO audit_log 
            (table_name, record_id, action, old_data, new_data)
        VALUES 
            (TG_TABLE_NAME, NEW.id, 'INSERT', null, new_data);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Apply audit triggers to main tables
CREATE TRIGGER audit_clients
    AFTER INSERT OR UPDATE OR DELETE ON clients
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_registrations
    AFTER INSERT OR UPDATE OR DELETE ON registrations
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_client_logins
    AFTER INSERT OR UPDATE OR DELETE ON client_logins
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

-- Comments for documentation
COMMENT ON TABLE clients IS 'Primary table containing client/company information';
COMMENT ON TABLE products IS 'Product catalog and specifications';
COMMENT ON TABLE states IS 'State-specific regulatory information';
COMMENT ON TABLE registrations IS 'Tracks product registrations across different states';
COMMENT ON TABLE client_logins IS 'Manages client access credentials for various state systems';
COMMENT ON TABLE audit_log IS 'Tracks all changes to major tables for compliance purposes';

-- Add some example data validation functions