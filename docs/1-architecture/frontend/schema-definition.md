# Data Schema Definition for Client Portal Prototype

## Core Data Models

### 1. Client
```typescript
interface Client {
  id: string;                    // Airtable Record ID
  compCode: string;              // fldqjHUmUkGP01WAw
  companyName: string;           // fldtqUOmaLwFjoTgu
  isInactive: boolean;           // fldvCmJSQlqYAM6cm
  manageRenewals: boolean;       // flddM0vpgt11JgfMH
  manageTonnage: boolean;        // fldZt7QIFtRkwpOj0
  contactEmail: string;          // fldXfT5cL1sLnf7Yi
  products: Product[];           // Linked Products
  registrations: Registration[]; // Linked Registrations
}
```

### 2. Product 
```typescript
interface Product {
  id: string;                  // Airtable Record ID
  name: string;                // Product Name field
  companyId: string;           // Link to Company
  isActive: boolean;           // Active field
  grade: string;               // Optional grade info
  productType: ProductType[];  // Product classification
  netWeightLbs: number;        // Weight info
  registrations: Registration[]; // State registrations
}

enum ProductType {
  Fertilizer = "Fertilizer",
  SoilAmendment = "Soil/Plant Amendment",
  BiologicalInoculant = "Biological Inoculant",
  Adjuvant = "Adjuvant",
  WettingAgent = "Wetting Agent",
  // ... other types
}
```

### 3. State
```typescript
interface State {
  id: string;                 // Airtable Record ID
  stateId: string;           // State abbreviation (e.g. "CA")
  stateName: string;         // Full state name
  department: string;        // Regulatory department
  contactEmail: string;      // State contact email
  website: string;           // State website
  registrations: Registration[]; // All registrations for state
}
```

### 4. Registration
```typescript
interface Registration {
  id: string;                       // Airtable Record ID
  productId: string;                // Link to Product
  stateId: string;                  // Link to State
  companyId: string;                // Link to Company
  status: RegistrationStatus;       // Current status
  certificateExp?: Date;            // fldpQwn55bazWBhQb
  registrationNumber?: string;      // fldTKxgGwKJLaYbkr
  initialSubmissionDate?: Date;     // fld1r7xu2oZahnyPi
  approvalDate?: Date;              // fld0H2fZ3Ynm12z0S
  isInternalActionNeeded: boolean;  // fldFnFor45qomC5jE
  submissionNotes?: string;         // fldkqEOt6u28CshSv
  currentCertificate?: Attachment[]; // fldz42BDJER5tFqq5
  lastModified: Date;               // fldk0oO4W6ei3D6Pc
}

enum RegistrationStatus {
  Planned = "Planned",
  NoSubmission = "No Submission", 
  Approved = "Approved",
  ApprovedInitial = "Approved - Initial",
  NotRegulated = "Not Regulated",
  Pending = "Pending",
  PendingResponse = "Pending - Response",
  Provisional = "Provisional",
  // ... other statuses
}
```

## View Models (For Client Portal)

### Product Matrix View
```typescript
interface ProductMatrixView {
  client: {
    id: string;
    name: string;
    compCode: string;
  };
  products: ProductRow[];
  states: StateColumn[];
}

interface ProductRow {
  id: string;
  name: string;
  registrations: Record<string, RegistrationCell>; // Keyed by stateId
}

interface StateColumn {
  id: string;
  stateId: string;
  name: string;
}

interface RegistrationCell {
  id: string;
  status: RegistrationStatus;
  expirationDate?: Date;
  registrationNumber?: string;
  lastModified: Date;
  hasAction: boolean;
}
```

### Filtering & Search
```typescript
interface FilterOptions {
  status?: RegistrationStatus[];
  states?: string[];           // State IDs
  productTypes?: ProductType[];
  searchTerm?: string;
  showInactiveProducts?: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
}
```

## Data Access Layer

### Airtable Service
```typescript
interface AirtableService {
  // Core data fetching
  getClient(clientId: string): Promise<Client>;
  getProducts(clientId: string): Promise<Product[]>;
  getRegistrations(filters: FilterOptions): Promise<Registration[]>;
  
  // Matrix specific queries
  getProductStateMatrix(clientId: string): Promise<ProductMatrixView>;
  getRegistrationDetails(registrationId: string): Promise<Registration>;
  
  // Updates
  updateRegistrationStatus(
    registrationId: string, 
    status: RegistrationStatus
  ): Promise<void>;
  
  uploadCertificate(
    registrationId: string, 
    file: File
  ): Promise<void>;
}
```

### Cache Keys
```typescript
const CACHE_KEYS = {
  client: (id: string) => `client:${id}`,
  products: (clientId: string) => `products:${clientId}`,
  matrix: (clientId: string) => `matrix:${clientId}`,
  registration: (id: string) => `registration:${id}`,
}

const CACHE_TTL = {
  client: 3600,        // 1 hour
  products: 1800,      // 30 minutes
  matrix: 300,         // 5 minutes
  registration: 300    // 5 minutes
}
```

## API Routes

### Core Endpoints
```typescript
// Client data
GET    /api/clients/:clientId
GET    /api/clients/:clientId/products
GET    /api/clients/:clientId/matrix

// Registration management
GET    /api/registrations/:registrationId
PUT    /api/registrations/:registrationId/status
POST   /api/registrations/:registrationId/certificate
GET    /api/registrations/:registrationId/history

// Search & Filters
GET    /api/search?term=:term
GET    /api/filters?status=:status&state=:state
```

## Authentication

### Client Portal User
```typescript
interface PortalUser {
  id: string;
  clientId: string;
  email: string;
  role: "admin" | "viewer";
  permissions: {
    canUpdateStatus: boolean;
    canUploadDocuments: boolean;
    canExportData: boolean;
  };
}

interface AuthResponse {
  token: string;
  user: PortalUser;
  expiresAt: number;
}
```

## Notes

1. **Required vs Optional Fields**
   - Essential fields for MVP are marked as required
   - Optional fields can be added based on client needs
   - All dates should handle null/undefined values

2. **Airtable Integration**
   - All IDs reference Airtable record IDs
   - Use field IDs for direct field access
   - Cache frequently accessed data

3. **Performance Considerations**
   - Batch Airtable requests where possible
   - Index key lookups in Redis cache
   - Optimize matrix view generation

4. **Future Extensions**
   - Document storage integrations
   - Workflow automation
   - Enhanced reporting
   - Audit logging