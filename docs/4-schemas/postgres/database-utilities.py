# config/database.py (continued)
        db.close()

# Audit configuration
def setup_audit_triggers(engine):
    """Set up database triggers for audit logging"""
    with engine.connect() as conn:
        conn.execute("""
            CREATE OR REPLACE FUNCTION audit_trigger_func()
            RETURNS TRIGGER AS $$
            DECLARE
                old_data JSON;
                new_data JSON;
            BEGIN
                IF (TG_OP = 'DELETE') THEN
                    old_data = row_to_json(OLD);
                    INSERT INTO audit_log 
                        (table_name, record_id, action, old_data, new_data)
                    VALUES 
                        (TG_TABLE_NAME, OLD.id, 'DELETE', old_data, null);
                    RETURN OLD;
                ELSIF (TG_OP = 'UPDATE') THEN
                    old_data = row_to_json(OLD);
                    new_data = row_to_json(NEW);
                    INSERT INTO audit_log 
                        (table_name, record_id, action, old_data, new_data)
                    VALUES 
                        (TG_TABLE_NAME, NEW.id, 'UPDATE', old_data, new_data);
                    RETURN NEW;
                ELSIF (TG_OP = 'INSERT') THEN
                    new_data = row_to_json(NEW);
                    INSERT INTO audit_log 
                        (table_name, record_id, action, old_data, new_data)
                    VALUES 
                        (TG_TABLE_NAME, NEW.id, 'INSERT', null, new_data);
                    RETURN NEW;
                END IF;
                RETURN NULL;
            END;
            $$ language 'plpgsql';
        """)

        # Apply triggers to main tables
        tables = ['clients', 'products', 'registrations', 'client_logins']
        for table in tables:
            conn.execute(f"""
                DROP TRIGGER IF EXISTS audit_{table} ON {table};
                CREATE TRIGGER audit_{table}
                    AFTER INSERT OR UPDATE OR DELETE ON {table}
                    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
            """)

# schemas/base.py
from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class BusinessTypeEnum(str, Enum):
    Corporation = "Corporation"
    LLC = "Limited Liability Corporation"
    Partnership = "Partnership"
    Individual = "Individual"
    SoleProprietor = "Sole Proprietor"

class RegistrationStatusEnum(str, Enum):
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

# schemas/client.py
class ClientBase(BaseModel):
    comp_code: Optional[str]
    company_name: str
    business_type: Optional[BusinessTypeEnum]
    epa_company_number: Optional[str]
    is_inactive: bool = False
    manage_renewals: bool = False
    manage_tonnage: bool = False
    producing_selling_product: bool = False
    parent_company_id: Optional[UUID4]
    
    # Contact Information
    company_address1: Optional[str]
    company_address2: Optional[str]
    company_city: Optional[str]
    company_state: Optional[str]
    company_zip: Optional[str]
    company_contact: Optional[str]
    company_contact_title: Optional[str]
    company_contact_phone: Optional[str]
    primary_contact_email: Optional[EmailStr]
    
    class Config:
        orm_mode = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class Client(ClientBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

# schemas/product.py
class ProductBase(BaseModel):
    name: str
    company_id: UUID4
    active: bool = True
    material_state: Optional[str]
    grade: Optional[str]
    density: Optional[float]
    density_unit: Optional[str]
    package_size: Optional[float]
    package_unit: Optional[str]
    net_weight_lbs: Optional[float]
    fertilizer_code: Optional[int]
    notes: Optional[str]
    
    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

# schemas/registration.py
class RegistrationBase(BaseModel):
    product_id: UUID4
    company_id: UUID4
    state_id: UUID4
    registration_status: RegistrationStatusEnum
    certificate_exp: Optional[date]
    initial_sub_date: Optional[date]
    approval_received: Optional[date]
    cancellation_effective: Optional[date]
    submission_date: Optional[date]
    registration_number: Optional[str]
    internal_action_needed: bool = False
    submission_notes: Optional[str]
    
    class Config:
        orm_mode = True

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(RegistrationBase):
    pass

class Registration(RegistrationBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

# utils/db_helpers.py
from sqlalchemy.orm import Session
from typing import Optional, List, TypeVar, Type, Generic
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID4) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: UUID4) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

# utils/airtable_sync.py
from typing import Dict, Any, List
import aiohttp
import asyncio
from models import Client, Product, Registration, State
from sqlalchemy.orm import Session

class AirtableSync:
    def __init__(self, api_key: str, base_id: str):
        self.api_key = api_key
        self.base_id = base_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    async def fetch_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch all records from an Airtable table"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
        records = []
        
        async with aiohttp.ClientSession() as session:
            async def fetch_page(offset=None):
                params = {"pageSize": 100}
                if offset:
                    params["offset"] = offset
                    
                async with session.get(url, headers=self.headers, params=params) as response:
                    data = await response.json()
                    records.extend(data["records"])
                    return data.get("offset")
            
            offset = await fetch_page()
            while offset:
                offset = await fetch_page(offset)
                
        return records
    
    async def sync_clients(self, db: Session):
        """Sync clients from Airtable to local database"""
        records = await self.fetch_table("Clients")
        
        for record in records:
            fields = record["fields"]
            client = db.query(Client).filter_by(comp_code=fields.get("Comp Code")).first()
            
            client_data = {
                "comp_code": fields.get("Comp Code"),
                "company_name": fields.get("Company Name"),
                "is_inactive": fields.get("Inactive", False),
                "manage_renewals": fields.get("Manage Renewals", False),
                "manage_tonnage": fields.get("Manage Tonnage", False),
                # Add other fields mapping
            }
            
            if client:
                for key, value in client_data.items():
                    setattr(client, key, value)
            else:
                client = Client(**client_data)
                db.add(client)
                
        db.commit()

# Initialize database with indexes
def setup_db_indexes(engine):
    """Create database indexes for common queries"""
    with engine.connect() as conn:
        # Client indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_comp_code ON clients(comp_code);')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_clients_company_name ON clients(company_name);')
        
        # Product indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_products_company_id ON products(company_id);')
        
        # Registration indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_registrations_product_id ON registrations(product_id);')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_registrations_company_id ON registrations(company_id);')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_registrations_state_id ON registrations(state_id);')
