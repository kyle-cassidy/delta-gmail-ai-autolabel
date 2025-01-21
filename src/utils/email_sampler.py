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

        # Handle both Message objects and raw message dictionaries
        if isinstance(message, dict):
            raw_message = message
        else:
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

    def get_messages_by_label(
        self, label_name: str, max_messages: int = 100
    ) -> List[Any]:
        """Get messages with a specific label."""
        # Get label ID
        labels = self.gmail.list_labels()
        label_id = None
        for label in labels:
            if label.name == label_name:
                label_id = label.id
                break

        if not label_id:
            raise ValueError(f"Label '{label_name}' not found")

        # Get messages with this label
        query = f"label:{label_name}"
        messages = (
            self.gmail.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_messages)
            .execute()
        )

        if "messages" not in messages:
            return []

        # Get full message details
        return [
            self.gmail.service.users()
            .messages()
            .get(userId="me", id=msg["id"])
            .execute()
            for msg in messages["messages"][:max_messages]
        ]

    def download_sample_emails(
        self, max_messages: int = 100, label_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Download and store sample emails."""
        if label_filter:
            messages = self.get_messages_by_label(label_filter, max_messages)
        else:
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
        if label_filter:
            print(f"Filtered by label: {label_filter}")

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
