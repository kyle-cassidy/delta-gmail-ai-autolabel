# Configuration Version Control System

This document describes the version control system for our configuration files that define domain-specific rules, patterns, and terminology for document classification. The system uses semantic versioning to track changes and ensure compatibility.

## Directory Structure

```
config/
├── version_control.yaml     # Master version control configuration
├── regulatory_actions.yaml  # Regulatory action definitions
├── product_categories.yaml  # Product category hierarchies
├── document_types.yaml      # Base document type definitions
├── company_codes.yaml      # Company name standardization
└── state_patterns.yaml     # State recognition patterns
```

## Version Control System

### Semantic Versioning

We follow semantic versioning (MAJOR.MINOR.PATCH) for all configuration files:

- **MAJOR**: Breaking changes that require code updates (e.g., schema changes)
- **MINOR**: Backwards-compatible additions (new fields, patterns)
- **PATCH**: Content updates (new terms, companies, patterns)

### File Structure

Each configuration file includes:

```yaml
version: "1.0.0"           # Current version of this config
last_updated: "2024-03-14" # Date of last update
description: "..."         # Brief description of the config's purpose

# Configuration content follows...
```

### Version Control Management

The `version_control.yaml` file serves as the master configuration for versioning:

- Tracks current versions of all config files
- Defines minimum compatible versions
- Records version history and changes
- Specifies required migrations
- Maps validation schemas

## Version Checking

The system includes a `VersionChecker` utility that:

1. Validates config file versions against `version_control.yaml`
2. Checks for compatibility with minimum required versions
3. Identifies when migrations are needed
4. Ensures version format compliance

### Usage Example

```python
from src.utils.version_checker import VersionChecker

# Initialize checker
checker = VersionChecker(config_dir=Path("config"))

# Check all configs for compatibility
warnings = checker.check_compatibility()
for warning in warnings:
    logger.warning(warning)

# Check if specific config needs migration
if checker.needs_migration("regulatory_actions"):
    steps = checker.get_required_migrations("regulatory_actions")
    print(f"Migration steps needed: {steps}")
```

## Making Changes

### Adding New Content

For content additions (e.g., new companies, patterns):
1. Update the relevant config file
2. Increment the PATCH version
3. Update `last_updated` date
4. Add entry to version history in `version_control.yaml`

Example:
```yaml
# In company_codes.yaml
version: "1.0.1"  # Increment PATCH
last_updated: "2024-03-15"

# In version_control.yaml
history:
  company_codes:
    - version: "1.0.1"
      date: "2024-03-15"
      changes:
        - "Added new company XYZ"
```

### Schema Changes

For changes that affect the structure:
1. Increment MAJOR version if breaking, MINOR if backward compatible
2. Document required migrations in `version_control.yaml`
3. Update validation schemas if needed
4. Update code to handle changes

## Migration System

When config files need migration:

1. Define migration steps in `version_control.yaml`:
```yaml
migrations_required:
  "2.0.0": 
    - "Update field X to new format"
    - "Add required field Y"
```

2. The `VersionChecker` will detect and report needed migrations:
```python
if checker.needs_migration("regulatory_actions"):
    steps = checker.get_required_migrations("regulatory_actions")
    # Handle migration steps
```

## Validation

The system includes JSON schemas for each major version:

```
schemas/
└── v1_0_0/
    ├── regulatory_actions.schema.json
    ├── product_categories.schema.json
    └── ...
```

Use these schemas to validate config files against their specified version.

## Best Practices

1. **Version Bumping**:
   - PATCH: Adding patterns, companies, terms
   - MINOR: New optional fields, features
   - MAJOR: Breaking schema changes

2. **Documentation**:
   - Always update version history
   - Document migration steps
   - Keep descriptions clear and concise

3. **Compatibility**:
   - Maintain backward compatibility when possible
   - Test migrations thoroughly
   - Update dependent code when needed

4. **Validation**:
   - Always validate configs after changes
   - Use provided schema validation
   - Run version compatibility checks

## Error Handling

The system provides warnings for:
- Missing config files
- Version mismatches
- Invalid version formats
- Required migrations
- Compatibility issues

Monitor logs for these warnings during application startup.

## Integration with Domain Config

The versioning system is integrated with the `DomainConfig` class, which:

1. Initializes the `VersionChecker` on startup
2. Validates all config versions before loading
3. Warns about needed migrations
4. Ensures config compatibility

Example integration:
```python
class DomainConfig:
    def __init__(self, config_dir: Path):
        # Initialize version checker
        self.version_checker = VersionChecker(config_dir)
        
        # Check compatibility
        warnings = self.version_checker.check_compatibility()
        for warning in warnings:
            logger.warning(warning)
            
        # Load and validate configs
        self._load_configs()
        self._check_migrations()
```

## Development Workflow

When making changes to configurations:

1. **Planning**:
   - Determine the type of change (MAJOR/MINOR/PATCH)
   - Plan migration steps if needed
   - Document the changes

2. **Implementation**:
   - Update the config file(s)
   - Increment version numbers
   - Update version history
   - Add migration steps if needed

3. **Validation**:
   - Run version compatibility checks
   - Validate against schemas
   - Test migrations if applicable

4. **Deployment**:
   - Update all related configs
   - Deploy changes together
   - Monitor for warnings

## Troubleshooting

Common issues and solutions:

1. **Version Mismatch**:
   - Check `version_control.yaml` for current versions
   - Ensure all related configs are updated
   - Run version compatibility check

2. **Migration Needed**:
   - Review migration steps in version control
   - Apply migrations in order
   - Validate after migration

3. **Invalid Version Format**:
   - Ensure versions follow MAJOR.MINOR.PATCH
   - Use `validate_version_format()` to check
   - Fix any malformed versions

4. **Missing Configs**:
   - Check file paths and names
   - Ensure all required configs exist
   - Update version control if removing configs 