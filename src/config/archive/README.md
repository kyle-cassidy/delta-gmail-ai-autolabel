# Configuration Archive

This directory contains archived versions of configuration files that are no longer in active use. The archive is organized by major version and date to maintain a clear history of our configuration evolution.

## Directory Structure

```
archive/
├── v1/                     # Major version directories
│   ├── 2024-03/           # Archive by date
│   │   ├── pre-versioning/  # Configs from before versioning system
│   │   └── initial/         # Initial versioned configs
│   └── README.md          # Version-specific notes
├── v2/
│   └── ...
└── deprecated/            # Deprecated configs that don't fit version structure
    └── legacy/            # Very old configs without clear versioning
```

## Archiving Process

When archiving configuration files:

1. Create a directory for the major version if it doesn't exist
2. Create a subdirectory with the date (YYYY-MM)
3. Copy the old config files into this directory
4. Add a `CHANGELOG.md` in the version directory documenting:
   - Why the configs were archived
   - What replaced them
   - Any migration notes

## Archive Types

### Version Archives
- Complete sets of configs from a specific version
- Organized by major version number
- Include all related files from that version

### Pre-versioning Archives
- Configs from before the versioning system
- Stored in `v1/2024-03/pre-versioning/`
- Maintained for historical reference

### Deprecated Configs
- One-off or experimental configs
- Configs that don't fit the version structure
- Stored in `deprecated/` with clear documentation

## Naming Convention

Archive filenames should include:
- Original filename
- Version number
- Archive date

Example:
```
product_categories_v1.0.0_2024-03.yaml
regulatory_actions_v1.0.0_2024-03.yaml
```

## Documentation Requirements

Each archive directory must include:

1. `CHANGELOG.md` documenting:
   - Date of archival
   - Reason for archival
   - List of archived files
   - Migration path to newer versions

2. `README.md` with:
   - Description of the archived configs
   - Any special notes about the version
   - Known issues or limitations

## Best Practices

1. **Never Delete**
   - Archive rather than delete old configs
   - Maintain complete version history
   - Document reasons for archival

2. **Version Clarity**
   - Clear labeling of versions
   - Document relationships between versions
   - Note breaking changes

3. **Migration Path**
   - Document upgrade path to newer versions
   - Include any necessary migration scripts
   - Note any manual steps required

4. **Organization**
   - Group related configs together
   - Maintain consistent directory structure
   - Use clear, descriptive names

## Security Note

While these files are archived, they may contain sensitive information. Ensure:
- Proper access controls are maintained
- Sensitive data is redacted if necessary
- Archive access is logged

## Cleanup Policy

- Archives are permanent by default
- Annual review for relevance
- May compress older archives
- Document any cleanup actions in CHANGELOG 