# models/__init__.py
from .base import Base
from .client import Client
from .product import Product
from .state import State
from .registration import Registration
from .login import ClientLogin
from .audit import AuditLog

# models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from datetime import datetime
import enum

Base = declarative_base()

# Configure SQLAlchemy to automatically update updated_at timestamps
@event.listens_for(Base, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # Only update timestamp for tables with updated_at column
    if hasattr(target, 'updated_at'):
        target.updated_at = datetime.utcnow()

# Shared Enums
class BusinessType(enum.Enum):
    Corporation = "Corporation"
    LLC = "Limited Liability Corporation"
    Partnership = "Partnership"  
    Individual = "Individual"
    SoleProprietor = "Sole Proprietor"

class RegistrationStatus(enum.Enum):
    Planned = "Planned"
    NoSubmission = "No Submission"
    Approved = "Approved"
    ApprovedInitial = "Approved - Initial"
    NotRegulated = "Not Regulated"
    Pending = "Pending"
    PendingResponse = "Pending - Response"
    Provisional = "Provisional"
    AutomaticLicense = "Automatic w/ License"
    Denied = "Denied"
    Cancelled = "Cancelled"
    D1 = "D1"
    D2 = "D2"
    ClientManaged = "Client Managed"
    NotNeeded = "Not Needed"
    Unknown = "Unknown"
    TonRequired = "TON Required"
    TonNotRequired = "TON Not Required"

class ProductType(enum.Enum):
    Fertilizer = "Fertilizer"
    SoilAmendment = "Soil/Plant Amendment"
    BiologicalInoculant = "Biological Inoculant"
    Adjuvant = "Adjuvant"
    WettingAgent = "Wetting Agent"
    PGR = "PGR"
    SpecialtyFertilizer = "Specialty Fertilizer"
    NotRegulated = "Not Regulated"
    LegumeInoculant = "Legume Inoculant"
    Pesticide = "Pesticide"
    LimingMaterial = "Liming Material"
    Surfactant = "Surfactant"

# models/client.py
from sqlalchemy import (
    Column, String, Boolean, Integer, Date, Text, DateTime, ForeignKey,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base, BusinessType

class Client(Base):
    __tablename__ = 'clients'
    __table_args__ = (
        CheckConstraint('billing_level BETWEEN 1 AND 10', name='valid_billing_level'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comp_code = Column(String(50), unique=True)
    company_name = Column(String(255), nullable=False)
    business_type = Column(BusinessType)
    epa_company_number = Column(String(50))
    is_inactive = Column(Boolean, default=False)
    manage_renewals = Column(Boolean, default=False)
    manage_tonnage = Column(Boolean, default=False)
    producing_selling_product = Column(Boolean, default=False)
    parent_company_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'))

    # Contact Information
    company_address1 = Column(String(255))
    company_address2 = Column(String(255))
    company_city = Column(String(100))
    company_state = Column(String(2))
    company_zip = Column(String(20))
    company_county = Column(String(100))
    company_country = Column(String(100))
    company_contact = Column(String(255))
    company_contact_title = Column(String(255))
    company_contact_phone = Column(String(50))
    primary_contact_email = Column(String(255))
    emergency_contact_name = Column(String(255))
    emergency_phone = Column(String(50))
    has_24hr_phone = Column(Boolean, default=False)

    # Tax Information
    fein_tax_id = Column(String(50))
    state_incorporated = Column(String(2))
    date_incorporated = Column(Date)

    # Label Information
    company_name_label = Column(String(255))
    street_address_label = Column(Text)
    city_label = Column(String(100))
    state_label = Column(String(2))
    zip_label = Column(String(20))
    manufacturer_name = Column(String(255))
    manufacturer_address = Column(Text)

    # Corporate Officer Information
    corporate_officer_name = Column(String(255))
    corporate_officer_title = Column(String(255))

    # Billing Information
    billing_level = Column(Integer)
    last_billing_increase = Column(Date)

    # Additional Information
    organic_registrations = Column(String(50))
    tonnage_contact_email = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="company", 
                          foreign_keys="Product.company_id")
    repack_products = relationship("Product", back_populates="repack_company", 
                                 foreign_keys="Product.repack_company_id")
    registrations = relationship("Registration", back_populates="company")
    logins = relationship("ClientLogin", back_populates="company")
    parent_company = relationship("Client", remote_side=[id])

# models/product.py
from sqlalchemy import (
    Column, String, Boolean, Float, Integer, DateTime, ForeignKey, Table, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base, ProductType

# Association table for product types
product_types = Table('product_types', Base.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True),
    Column('product_type', ProductType, primary_key=True)
)

class Product(Base):
    __tablename__ = 'products'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    active = Column(Boolean, default=True)
    material_state = Column(String(50))
    grade = Column(String(50))
    density = Column(Float(precision=10, scale=4))
    density_unit = Column(String(10))
    package_size = Column(Float(precision=10, scale=2))
    package_unit = Column(String(10))
    net_weight_lbs = Column(Float(precision=10, scale=2))
    fertilizer_code = Column(Integer)
    is_repack = Column(Boolean, default=False)
    repack_company_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'))
    repack_product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    company = relationship("Client", back_populates="products", foreign_keys=[company_id])
    repack_company = relationship("Client", back_populates="repack_products", 
                                foreign_keys=[repack_company_id])
    product_types = relationship("ProductType", secondary=product_types)
    registrations = relationship("Registration", back_populates="product")
    repack_source = relationship("Product", remote_side=[id], uselist=False)

# models/state.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base

class State(Base):
    __tablename__ = 'states'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(String(2), unique=True, nullable=False)
    state_name = Column(Text, nullable=False)
    check_payable_to = Column(Text)
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    address_line3 = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))
    zip = Column(String(20))
    
    # Contact
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    registrations = relationship("Registration", back_populates="state")
    client_logins = relationship("ClientLogin", back_populates="state")

# models/registration.py
from sqlalchemy import (
    Column, String, Boolean, Integer, Date, DateTime, ForeignKey, Text,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base, RegistrationStatus

class Registration(Base):
    __tablename__ = 'registrations'
    __table_args__ = (
        CheckConstraint('priority_phase BETWEEN 1 AND 4', name='valid_priority_phase'),
        CheckConstraint('pll_phase BETWEEN 1 AND 4', name='valid_pll_phase'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    state_id = Column(UUID(as_uuid=True), ForeignKey('states.id'), nullable=False)
    
    registration_status = Column(RegistrationStatus, nullable=False)
    certificate_exp = Column(Date)
    initial_sub_date = Column(Date)
    approval_received = Column(Date)
    cancellation_effective = Column(Date)
    submission_date = Column(Date)
    registration_number = Column(String(100))
    internal_action_needed = Column(Boolean, default=False)
    submission_notes = Column(Text)
    
    # Renewal fields
    renewal_status = Column(String(50))
    renewal_reminder_received = Column(Boolean, default=False)
    ready_to_mail = Column(Boolean, default=False)
    submitted = Column(Boolean, default=False)
    day_of_month_due = Column(Integer)
    
    # Tracking fields
    priority_phase = Column(Integer)
    pll_phase = Column(Integer)
    label_change_request = Column(Text)
    label_update_submission = Column(Date)
    label_update_needed = Column(Boolean, default=False)

    # Timestamps and audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))  # Will reference users table
    updated_by = Column(UUID(as_uuid=True))  # Will reference users table

    # Relationships
    product = relationship("Product", back_populates="registrations")
    company = relationship("Client", back_populates="registrations")
    state = relationship("State", back_populates="registrations")

# models/login.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base

class ClientLogin(Base):
    __tablename__ = 'client_logins'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    state_id = Column(UUID(as_uuid=True), ForeignKey('states.id'))
    
    classification = Column(String(50))
    regulation_type = Column(String(50))
    website = Column(String(255))
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Should be properly hashed
    usa_plant_id = Column(String(100))
    license_number = Column(String(100))
    notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    company = relationship("Client", back_populates="logins")
    state = relationship("State", back_populates="client_logins")

# models/audit.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base

class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(50), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    old_data = Column(JSON)
    new_data = Column(JSON)
    user_id = Column(UUID(as_uuid=True))  # Will reference users table
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# config/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/delta')

# Create engine with appropriate PostgreSQL connection settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        