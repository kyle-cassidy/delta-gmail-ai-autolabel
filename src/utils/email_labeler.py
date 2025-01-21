import re
from typing import List, Optional, Set, Tuple

from src.utils.data_extractor import Client, DataExtractor, StateRegulator


class EmailLabeler:
    def __init__(self, csv_dir: str):
        self.extractor = DataExtractor(csv_dir)
        self.clients, self.regulators = self.extractor.get_all_data()

    def extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or "@" not in email:
            return ""
        return email.split("@")[1].lower()

    def match_domain_pattern(self, domain: str, pattern: str) -> bool:
        """Match domain against a pattern that may contain wildcards."""
        if not domain or not pattern:
            return False

        # Convert glob pattern to regex
        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", domain))

    def get_labels(self, from_email: str, subject: str = "") -> List[str]:
        """
        Get appropriate labels for an email based on sender and subject.
        Returns a list of label strings in the format:
        - Client/{ClientName}
        - Regulator/{StateName}
        """
        domain = self.extract_domain(from_email)
        if not domain:
            return []

        labels = []

        # Check client domains
        for client in self.clients.values():
            if domain in client.email_domains:
                labels.append(f"Client/{client.name}")

        # Check regulator domains
        for reg in self.regulators.values():
            for pattern in reg.email_domains:
                if self.match_domain_pattern(domain, pattern):
                    labels.append(f"Regulator/{reg.name}")
                    break

        return labels


def main() -> None:
    # Example usage
    labeler = EmailLabeler("docs/4-schemas/airtable/csv")

    # Test some example emails
    test_emails = [
        "pieterbooysen@ableagsolutions.com",  # Client
        "someone@cdfa.ca.gov",  # CA regulator
        "person@doh.state.fl.us",  # FL regulator
        "other@gmail.com",  # Neither
    ]

    for email in test_emails:
        labels = labeler.get_labels(email)
        print(f"\nEmail: {email}")
        print(f"Labels: {labels}")


if __name__ == "__main__":
    main()
