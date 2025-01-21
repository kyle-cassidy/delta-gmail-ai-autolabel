from src.client.gmail import Gmail


def test_connectivity() -> bool:
    """Basic connectivity test for Gmail API"""
    try:
        # Initialize with our existing credentials
        gmail = Gmail(
            client_secret_file="secrets/secret-gmail-ai-autolabel.json",
            creds_file="secrets/gmail_token.json",
        )

        # Test 1: List labels (simplest API call)
        print("Testing label retrieval...")
        labels = gmail.list_labels()
        print("\nGmail Labels:")
        print("-" * 50)
        for label in labels:
            print(f"• {label.name:<30} (ID: {label.id})")
        print("-" * 50)
        print(f"Success! Found {len(labels)} labels\n")

        # Test 2: Try to get one unread message
        # print("\nTesting message retrieval...")
        # messages = gmail.get_unread_inbox()
        # print(f"Success! Found {len(messages)} unread messages")

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    test_connectivity()
