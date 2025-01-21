import csv
from dataclasses import dataclass
from typing import Dict, List, Set
from pathlib import Path


@dataclass
class Client:
    code: str  # Company code (e.g., 'AAS', 'AGR')
    name: str  # Full company name
    email_domains: Set[str]  # Email domains associated with the company


@dataclass
class StateRegulator:
    code: str  # 2-letter state code
    name: str  # Full state name
    email_domains: Set[str]  # Common state email domain patterns


class DataExtractor:
    def __init__(self, csv_dir: str):
        self.csv_dir = Path(csv_dir)
        self.clients: Dict[str, Client] = {}
        self.regulators: Dict[str, StateRegulator] = {}

    def extract_email_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or "@" not in email:
            return ""
        return email.split("@")[1].lower()

    def load_clients(self) -> Dict[str, Client]:
        """Load client information from Clients.csv"""
        clients_file = self.csv_dir / "Clients.csv"

        with open(clients_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row["Comp Code"]:  # Skip empty rows
                    continue

                code = row["Comp Code"]
                name = row["Company Name"]
                email = row["Primary Contact Email"]

                # Extract email domain
                domain = self.extract_email_domain(email)
                domains = {domain} if domain else set()

                self.clients[code] = Client(code=code, name=name, email_domains=domains)

        return self.clients

    def load_regulators(self) -> Dict[str, StateRegulator]:
        """Load regulator information from State-Regulators.csv"""
        regulators_file = self.csv_dir / "State-Regulators.csv"

        with open(regulators_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["State ID"]
                name = row["State Name"]

                # Common state email domain patterns
                email_domains = {f"*.{code.lower()}.gov", f"*.state.{code.lower()}.us"}

                self.regulators[code] = StateRegulator(
                    code=code, name=name, email_domains=email_domains
                )

        return self.regulators

    def get_all_data(self) -> tuple[Dict[str, Client], Dict[str, StateRegulator]]:
        """Load both clients and regulators data"""
        self.load_clients()
        self.load_regulators()
        return self.clients, self.regulators


def main() -> None:
    # Example usage
    extractor = DataExtractor("docs/4-schemas/airtable/csv")
    clients, regulators = extractor.get_all_data()

    print("Clients:")
    for client in clients.values():
        print(f"{client.code}: {client.name} ({client.email_domains})")

    print("\nRegulators:")
    for reg in regulators.values():
        print(f"{reg.code}: {reg.name} ({reg.email_domains})")


if __name__ == "__main__":
    main()
