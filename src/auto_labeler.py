import asyncio
from typing import Dict, List, Optional

from src.client.gmail import Gmail
from src.utils.email_labeler import EmailLabeler


class AutoLabeler:
    def __init__(
        self,
        client_secret_file: str = "secrets/secret-gmail-ai-autolabel.json",
        creds_file: str = "secrets/gmail_token.json",
        csv_dir: str = "docs/4-schemas/airtable/csv",
    ):
        self.gmail = Gmail(
            client_secret_file=client_secret_file,
            creds_file=creds_file,
        )
        self.labeler = EmailLabeler(csv_dir)
        self._labels_cache: Dict[str, str] = {}  # name -> id mapping

    def ensure_label_exists(self, label_name: str) -> str:
        """Ensure a label exists, creating it if needed."""
        if not self._labels_cache:
            labels = self.gmail.list_labels()
            self._labels_cache = {label.name: label.id for label in labels}

        if label_name not in self._labels_cache:
            label = self.gmail.create_label(label_name)
            self._labels_cache[label_name] = label.id

        return self._labels_cache[label_name]

    def process_unread_messages(self, max_messages: int = 50) -> None:
        """Process unread messages and apply labels."""
        messages = self.gmail.get_unread_inbox(max_messages=max_messages)

        for message in messages:
            # Extract from address from headers
            from_address = None
            for header in message.headers:
                if header["name"].lower() == "from":
                    from_address = header["value"]
                    break

            if not from_address:
                print(
                    f"WARNING: Skipping message - no from address found: {message.id}"
                )
                continue

            subject = message.subject or ""

            # Log messages with missing content for investigation
            if not message.plain and not message.html:
                print(f"WARNING: Message has no content - ID: {message.id}")
                print(f"From: {from_address}")
                print(f"Subject: {subject}")
                if message.attachments:
                    print(f"Has {len(message.attachments)} attachments")
                print("---")

            # Get content and attachments for classification
            content = {
                "plain": message.plain,
                "html": message.html,
                "snippet": message.snippet,
                "has_attachments": bool(message.attachments),
                "attachments": (
                    [
                        {
                            "filename": att.filename,
                            "mime_type": att.mime_type,
                            "size": att.size,
                        }
                        for att in message.attachments
                    ]
                    if message.attachments
                    else []
                ),
            }

            # Get appropriate labels
            labels_to_add = self.labeler.get_labels(
                from_address=from_address, subject=subject, content=content
            )

            if not labels_to_add:
                continue

            # Ensure labels exist and get their IDs
            label_ids = []
            for label_name in labels_to_add:
                label_id = self.ensure_label_exists(label_name)
                label_ids.append(label_id)

            # Apply labels
            if label_ids:
                message.modify(add_label_ids=label_ids)
                print(f"Labeled message: {subject}")
                print(f"Applied labels: {', '.join(labels_to_add)}")


def main() -> None:
    labeler = AutoLabeler()
    print("Starting auto-labeling process...")
    labeler.process_unread_messages(max_messages=50)
    print("Completed auto-labeling process!")


if __name__ == "__main__":
    main()
