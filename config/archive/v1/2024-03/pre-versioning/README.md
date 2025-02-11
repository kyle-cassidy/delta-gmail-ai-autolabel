# Pre-versioning Configuration Archive

This directory contains configuration files from before the implementation of our versioning system. These files serve as the foundation for our versioned configurations.

## Archived Files

### Regulatory Actions Evolution
- `regulatory_actions_v2.yaml`: Second iteration with expanded state terms
- `regulatory_actions_v3.yaml`: Last pre-versioning iteration with comprehensive state-specific terms
- Base for current `regulatory_actions.yaml` (v1.0.0)

### Product Categories Evolution
- `product_categories_v2.yaml`: Enhanced version with detailed state-specific terminology
- Foundation for current `product_categories.yaml` (v1.0.0)

### Supporting Configurations
- `state_specific.yaml`: Original state-specific overrides and rules
  - Functionality now integrated into respective domain files
  - State-specific logic now more tightly coupled with each domain

## Historical Context

These files represent the evolution of our configuration system before formal versioning:

1. Initial development focused on capturing state-specific terminology
2. Iterative improvements to pattern matching and recognition
3. Growing complexity led to need for versioning
4. Progressive refinement of state-specific rules

## Migration to Versioned System

The transition to versioned configs involved:
1. Adding version headers
2. Standardizing file structure
3. Implementing validation rules
4. Creating version control system
5. Integrating state-specific rules into domain files
6. Establishing clear relationships between configurations

## Key Changes in Versioned System

1. **Regulatory Actions**:
   - Cleaner structure with base types
   - Improved pattern matching
   - Better state-specific integration

2. **Product Categories**:
   - Enhanced hierarchy
   - More precise pattern matching
   - Better handling of state variations

3. **State Handling**:
   - Integrated directly into domain files
   - More maintainable structure
   - Clearer relationships

## Usage Notes

These files are maintained for:
- Historical reference
- Understanding evolution of configurations
- Troubleshooting legacy patterns
- Tracking development decisions

**Note**: These files should not be used in production. Refer to current versioned configurations in the main config directory. 