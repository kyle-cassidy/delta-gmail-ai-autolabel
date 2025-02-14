"""Version checker utility for configuration files."""

from pathlib import Path
import yaml
from typing import Dict, Optional, List
import semver
import logging

logger = logging.getLogger(__name__)


class VersionChecker:
    """Checks and validates configuration file versions."""

    def __init__(self, config_dir: Path):
        """Initialize the version checker.

        Args:
            config_dir: Path to configuration directory
        """
        self.config_dir = config_dir
        self.version_control = self._load_version_control()

    def _load_version_control(self) -> Dict:
        """Load version control configuration."""
        version_file = self.config_dir / "version_control.yaml"
        if not version_file.exists():
            logger.warning(f"Version control file not found: {version_file}")
            return {
                "min_compatible_version": "1.0.0",
                "current_versions": {},
                "migrations_required": {},
            }

        with open(version_file) as f:
            data = yaml.safe_load(f)
            return data.get("version_control", {}) if data else {}

    def _load_config_version(self, config_file: Path) -> Optional[str]:
        """Extract version from a config file."""
        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
                return config.get("version") if config else None
        except Exception as e:
            logger.warning(f"Error loading config file {config_file}: {e}")
            return None

    def check_compatibility(self) -> List[str]:
        """Check compatibility of all config files.

        Returns:
            List of warning messages for any version mismatches
        """
        warnings = []
        min_version = self.version_control.get("min_compatible_version", "1.0.0")
        current_versions = self.version_control.get("current_versions", {})

        for config_name, expected_version in current_versions.items():
            config_file = self.config_dir / f"{config_name}.yaml"
            if not config_file.exists():
                warnings.append(f"Missing config file: {config_name}.yaml")
                continue

            actual_version = self._load_config_version(config_file)
            if not actual_version:
                warnings.append(f"No version found in {config_name}.yaml")
                continue

            try:
                if semver.compare(actual_version, min_version) < 0:
                    warnings.append(
                        f"Config {config_name}.yaml version {actual_version} is below "
                        f"minimum compatible version {min_version}"
                    )
                if actual_version != expected_version:
                    warnings.append(
                        f"Config {config_name}.yaml version {actual_version} does not "
                        f"match expected version {expected_version}"
                    )
            except ValueError as e:
                warnings.append(
                    f"Invalid version format in {config_name}.yaml: {str(e)}"
                )

        return warnings

    def needs_migration(self, config_name: str) -> bool:
        """Check if a config file needs migration.

        Args:
            config_name: Name of the config file (without .yaml)

        Returns:
            Whether migration is needed
        """
        config_file = self.config_dir / f"{config_name}.yaml"
        if not config_file.exists():
            return False

        actual_version = self._load_config_version(config_file)
        if not actual_version:
            return False

        expected_version = self.version_control.get("current_versions", {}).get(
            config_name
        )
        if not expected_version:
            return False

        try:
            return semver.compare(actual_version, expected_version) < 0
        except ValueError:
            return False

    def get_required_migrations(self, config_name: str) -> List[str]:
        """Get list of required migrations for a config file.

        Args:
            config_name: Name of the config file (without .yaml)

        Returns:
            List of migration steps needed
        """
        if not self.needs_migration(config_name):
            return []

        config_file = self.config_dir / f"{config_name}.yaml"
        if not config_file.exists():
            return []

        actual_version = self._load_config_version(config_file)
        if not actual_version:
            return []

        migrations = []
        migrations_required = self.version_control.get("migrations_required", {})

        for version, steps in migrations_required.items():
            try:
                if semver.compare(actual_version, version) < 0:
                    migrations.extend(steps)
            except ValueError:
                continue

        return migrations

    @staticmethod
    def validate_version_format(version: str) -> bool:
        """Validate that a version string follows semver format.

        Args:
            version: Version string to validate

        Returns:
            Whether the version is valid
        """
        try:
            semver.parse(version)
            return True
        except ValueError:
            return False
