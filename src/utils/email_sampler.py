import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import email.utils

from src.client.gmail import Gmail


class EmailSampler:
    def __init__(
        self,
        client_secret_file: str = "secrets/secret-gmail-ai-autolabel.json",
        creds_file: str = "secrets/gmail_token.json",
        output_dir: str = "tests/data/sample_emails",
    ):
        self.gmail = Gmail(
            client_secret_file=client_secret_file,
            creds_file=creds_file,
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_email_address(self, addr_str: str) -> Optional[str]:
        """Parse email address from a string that may include a display name."""
        if not addr_str:
            return None
        try:
            name, addr = email.utils.parseaddr(addr_str)
            return addr.lower() if addr else None
        except:
            return None

    def extract_email_metadata(self, message: Any) -> Dict[str, Any]:
        """Extract key metadata from a Gmail message."""
        metadata = {}

        # Get raw message data
        raw_message = (
            self.gmail.service.users()
            .messages()
            .get(userId="me", id=message.id, format="full")
            .execute()
        )

        # Extract headers into a more usable format
        headers = {}
        if "payload" in raw_message and "headers" in raw_message["payload"]:
            for header in raw_message["payload"]["headers"]:
                name = header["name"].lower()
                value = header["value"]
                headers[name] = value

        # Get message content
        content: Dict[str, Optional[str]] = {"plain": None, "html": None}
        if "payload" in raw_message:
            if "body" in raw_message["payload"]:
                if "data" in raw_message["payload"]["body"]:
                    data = raw_message["payload"]["body"]["data"]
                    text = base64.urlsafe_b64decode(data).decode()
                    content["html"] = text

            if "parts" in raw_message["payload"]:
                for part in raw_message["payload"]["parts"]:
                    if (
                        part["mimeType"] == "text/plain"
                        and "body" in part
                        and "data" in part["body"]
                    ):
                        data = part["body"]["data"]
                        text = base64.urlsafe_b64decode(data).decode()
                        content["plain"] = text
                    elif (
                        part["mimeType"] == "text/html"
                        and "body" in part
                        and "data" in part["body"]
                    ):
                        data = part["body"]["data"]
                        text = base64.urlsafe_b64decode(data).decode()
                        content["html"] = text

        # Get label names
        label_ids = raw_message.get("labelIds", [])
        labels = []
        if label_ids:
            all_labels = {label.id: label.name for label in self.gmail.list_labels()}
            labels = [all_labels.get(label_id, label_id) for label_id in label_ids]

        # Get key fields
        metadata["message_id"] = raw_message["id"]
        metadata["thread_id"] = raw_message.get("threadId", "")
        metadata["from"] = headers.get("from", "")
        metadata["to"] = headers.get("to", "")
        metadata["subject"] = headers.get("subject", "")
        metadata["date"] = headers.get("date", "")
        metadata["snippet"] = raw_message.get("snippet", "")
        metadata["headers"] = headers
        metadata["label_ids"] = label_ids
        metadata["labels"] = labels
        metadata["content"] = content

        return metadata

    def download_sample_emails(self, max_messages: int = 100) -> List[Dict[str, Any]]:
        """Download and store sample emails."""
        messages = self.gmail.get_unread_inbox()[:max_messages]
        samples = []

        for i, message in enumerate(messages):
            metadata = self.extract_email_metadata(message)
            samples.append(metadata)

            # Save individual message
            message_file = self.output_dir / f"message_{i+1}.json"
            with open(message_file, "w") as f:
                json.dump(metadata, f, indent=2)

        # Save all messages in one file
        all_messages_file = self.output_dir / "all_messages.json"
        with open(all_messages_file, "w") as f:
            json.dump(samples, f, indent=2)

        print(f"Downloaded {len(samples)} sample emails to {self.output_dir}")
        return samples

    def analyze_domains(self, samples: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze frequency of email domains in samples."""
        domains: Dict[str, int] = {}
        for message in samples:
            addr = message.get("from_address")
            if addr and "@" in addr:
                domain = addr.split("@")[1].lower()
                domains[domain] = domains.get(domain, 0) + 1

        # Sort by frequency
        sorted_domains = dict(sorted(domains.items(), key=lambda x: x[1], reverse=True))

        # Save domain analysis
        analysis_file = self.output_dir / "domain_analysis.json"
        with open(analysis_file, "w") as f:
            json.dump(sorted_domains, f, indent=2)

        return sorted_domains


def main() -> None:
    sampler = EmailSampler()
    samples = sampler.download_sample_emails(max_messages=100)
    domains = sampler.analyze_domains(samples)

    print("\nTop email domains:")
    for domain, count in list(domains.items())[:10]:
        print(f"{domain}: {count} emails")


if __name__ == "__main__":
    main()
