# Prototype Architecture & Implementation Guide

## 1. Data Layer Strategy

### Airtable as Primary Database
- Initially, keep Airtable as the source of truth
- No need for PostgreSQL in prototype phase
- Use Airtable API for all data operations
- Leverage Airtable views for filtered data

```typescript
// Example Airtable service
class AirtableService {
  async getClientProducts(clientId: string) {
    return await this.base('Products')
      .select({
        filterByFormula: `{CompanyId} = '${clientId}'`,
        sort: [{field: 'ProductName', direction: 'asc'}]
      })
      .all();
  }

  async getStateRegistrations(productId: string) {
    return await this.base('Registrations')
      .select({
        filterByFormula: `{ProductId} = '${productId}'`,
        sort: [{field: 'State', direction: 'asc'}]
      })
      .all();
  }
}
```

## 2. Backend Requirements

### Lightweight API Layer
- Need minimal backend to:
  1. Handle authentication
  2. Proxy Airtable requests
  3. Cache responses
  4. Handle file uploads
  5. Send notifications

```typescript
// Example FastAPI structure
app
├── main.py
├── auth/
│   ├── jwt_handler.py
│   └── middleware.py
├── cache/
│   └── redis_client.py
├── routers/
│   ├── client_portal.py
│   ├── products.py
│   └── registrations.py
└── services/
    ├── airtable.py
    └── notification.py
```

### Authentication Flow
```typescript
interface AuthFlow {
  // Initial login
  login: {
    endpoint: '/auth/login',
    method: 'POST',
    body: {
      username: string,
      password: string
    },
    response: {
      token: string,
      user: UserProfile
    }
  },

  // Client portal access
  portalAccess: {
    endpoint: '/auth/portal/{clientId}',
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`
    },
    response: {
      clientData: ClientProfile,
      products: Product[],
      registrations: Registration[]
    }
  }
}
```

## 3. Client Portal Interface

### Component Architecture
```typescript
interface PortalComponents {
  // Main layout
  Layout: {
    header: HeaderNav,
    sidebar: ProductList,
    main: RegistrationMatrix
  },

  // Product list
  ProductList: {
    products: Product[],
    filters: {
      status: string[],
      type: string[],
      search: string
    },
    onSelect: (productId: string) => void
  },

  // Registration matrix
  RegistrationMatrix: {
    product: Product,
    states: State[],
    registrations: Registration[],
    onCellClick: (registration: Registration) => void
  }
}
```

### State Management
```typescript
interface PortalState {
  // Client context
  client: {
    id: string,
    name: string,
    preferences: ClientPreferences
  },

  // Product data
  products: {
    items: Product[],
    selected: string | null,
    loading: boolean,
    error: Error | null
  },

  // Registration data
  registrations: {
    byProduct: Record<string, Registration[]>,
    loading: boolean,
    error: Error | null
  }
}
```

## 4. Essential Features

### MVP Features
1. Client Authentication
   - Email/password login
   - JWT tokens
   - Role-based access

2. Product View
   - List of client products
   - Basic filtering
   - Search functionality
   - Status indicators

3. Registration Matrix
   - State-by-state status
   - Basic status updates
   - Document uploads
   - Status history

4. Notifications
   - Status changes
   - Upcoming deadlines
   - Document requests

## 5. Caching Strategy

### Redis Implementation
```typescript
interface CacheStrategy {
  // Product cache
  products: {
    key: `products:${clientId}`,
    ttl: 5 minutes,
    invalidation: ['product:update', 'product:create']
  },

  // Registration cache
  registrations: {
    key: `registrations:${productId}`,
    ttl: 5 minutes,
    invalidation: ['registration:update', 'status:change']
  }
}
```

## 6. API Routes

### Essential Endpoints
```typescript
interface APIRoutes {
  // Authentication
  '/auth/login': {
    POST: LoginCredentials => AuthToken
  },

  // Products
  '/products': {
    GET: void => Product[],
    POST: ProductData => Product
  },

  // Registrations
  '/registrations': {
    GET: void => Registration[],
    POST: RegistrationData => Registration,
    PUT: RegistrationUpdate => Registration
  },

  // Documents
  '/documents': {
    POST: FormData => DocumentInfo,
    GET: DocumentId => DocumentData
  }
}
```

## 7. Implementation Steps

1. **Frontend Setup** (Week 1)
   - Next.js project setup
   - Authentication flow
   - Basic layout components
   - Product list view

2. **Backend Setup** (Week 1)
   - FastAPI setup
   - Airtable integration
   - Authentication middleware
   - Basic routes

3. **Matrix Implementation** (Week 2)
   - Registration grid component
   - State management
   - Status updates
   - Caching layer

4. **Document Handling** (Week 2)
   - Upload interface
   - Storage integration
   - Document preview
   - Download functionality

5. **Notifications** (Week 3)
   - Email integration
   - Status notifications
   - Deadline reminders
   - In-app alerts

## 8. Infrastructure Requirements

### Minimal Setup
- Vercel (Frontend hosting)
- Railway or Heroku (Backend hosting)
- Redis Cloud (Caching)
- SendGrid (Email notifications)
- AWS S3 (Document storage)

### Environment Variables
```bash
# Frontend
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_STORAGE_URL=

# Backend
AIRTABLE_API_KEY=
AIRTABLE_BASE_ID=
JWT_SECRET=
REDIS_URL=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
SENDGRID_API_KEY=
```

## 9. Development Process

1. Local Development
   - Use Next.js dev server
   - Local FastAPI server
   - Redis Docker container
   - LocalStack for S3

2. Staging Environment
   - Branch-based deployments
   - Staging Airtable base
   - Test email notifications

3. Production Deployment
   - CI/CD pipeline
   - Production Airtable base
   - Monitor performance

## 10. Next Steps

1. **Immediate**
   - Set up development environment
   - Create frontend skeleton
   - Implement auth flow
   - Basic product list

2. **Short Term**
   - Complete matrix view
   - Add document handling
   - Implement caching
   - Basic notifications

3. **Future**
   - Enhanced filtering
   - Bulk operations
   - Analytics dashboard
   - Mobile optimization