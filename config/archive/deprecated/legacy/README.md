# Deprecated and Legacy Configurations

This directory contains configuration files that are either deprecated or don't fit into the main versioning structure. These files are maintained for historical reference but should not be used in production.

## Archived Files

### Email Configuration
- `email_tags.yaml`: Original email tagging configuration
  - Replaced by more comprehensive document classification
  - Historical approach to email categorization
  - Some patterns may still be relevant for reference

### Client Data
- `clients.yaml`: Legacy client information structure
  - Replaced by `company_codes.yaml` in main config
  - More basic structure without versioning
  - Contains historical client mappings

## Historical Context

These configurations represent early attempts at:
1. Email classification and tagging
2. Client data organization
3. Basic pattern matching
4. Simple data structures

## Replacement Notes

### Email Tags → Document Classification
- More comprehensive approach in current system
- Integration with regulatory actions
- Better state and company recognition
- Enhanced pattern matching

### Clients → Company Codes
- Standardized 3-letter codes
- Better alias handling
- Validation rules
- Version control

## Usage Notes

These files are maintained for:
- Historical reference only
- Understanding previous approaches
- Legacy pattern reference
- Development history

**Important**: These files should never be used in production. They are kept only for:
- Historical documentation
- Pattern reference
- Development context
- Legacy understanding

## Migration Path

If you need functionality from these files:
1. Refer to current versioned configurations
2. Use `company_codes.yaml` for company information
3. Use document classification for email handling
4. Consult current documentation for best practices 