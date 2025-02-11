# Airtable API Reference

This document provides a comprehensive reference for the Airtable database schema and relationships.

## Tables Overview

1. Registration Tracking (Primary)
2. Client List
3. Registration Requirements
4. Products
5. States

## Registration Tracking

Primary table for tracking registration status and progress.

### Fields
- `id` (Primary Key)
- `client_id` (Link to Client List)
- `state` (Link to States)
- `product_id` (Link to Products)
- `registration_status`
- `submission_date`
- `approval_date`
- `renewal_date`
- `notes`

## Client List

Contains client information and metadata.

### Fields
- `id` (Primary Key)
- `client_name`
- `contact_email`
- `contact_phone`
- `address`
- `active_status`
- `onboarding_date`

## Registration Requirements (Reg Reqs)

Tracks specific requirements for different state registrations.

### Fields
- `id` (Primary Key)
- `state_id` (Link to States)
- `requirement_name`
- `requirement_description`
- `required_documents`
- `processing_time`
- `fees`

## Products

Product catalog and details.

### Fields
- `id` (Primary Key)
- `product_name`
- `product_type`
- `description`
- `active_status`
- `registration_needed`

## States

State-specific information and requirements.

### Fields
- `id` (Primary Key)
- `state_name`
- `state_code`
- `regulatory_authority`
- `contact_information`
- `special_requirements`

## Relationships

1. Registration Tracking
   - Links to Client List (many-to-one)
   - Links to States (many-to-one)
   - Links to Products (many-to-one)

2. Registration Requirements
   - Links to States (many-to-one)

## API Usage Examples

```javascript
// Fetch registration records for a specific client
const records = await base('Registration Tracking')
  .select({
    filterByFormula: `{client_id} = 'client_123'`
  })
  .all();

// Get all active products
const activeProducts = await base('Products')
  .select({
    filterByFormula: `{active_status} = 1`
  })
  .all();

// Get state requirements
const stateReqs = await base('Registration Requirements')
  .select({
    filterByFormula: `{state_id} = 'CA'`
  })
  .all();
```

## Best Practices

1. Always check for existing records before creating new ones
2. Use appropriate linking between tables to maintain data integrity
3. Keep registration status up to date
4. Document any special cases in the notes field
5. Regularly verify renewal dates

## Rate Limits

- 5 requests per second per base
- 100 records per request maximum
- 10,000 records per table maximum

For more detailed information, refer to the [Airtable API Documentation](https://airtable.com/developers/web/api/introduction). 