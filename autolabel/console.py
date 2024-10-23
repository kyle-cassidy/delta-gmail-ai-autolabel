from simplegmail import Gmail

def main():
    # Initialize Gmail client with our credentials
    gmail = Gmail(
        client_secret_file='../secrets/secret-gmail-ai-autolabel.json',
        creds_file='../secrets/gmail_token.json'
    )

    try:
        # First test - get labels to verify authentication
        print("Testing authentication...")
        labels = gmail.list_labels()
        print("Success! Available labels:")
        for label in labels:
            print(f"- {label.name}")

        # Get some unread messages
        print("\nFetching unread messages...")
        messages = gmail.get_unread_inbox()
        print(f"Found {len(messages)} unread messages:")
        
        for message in messages[:5]:  # Show first 5 messages
            print(f"\nFrom: {message.sender}")
            print(f"Subject: {message.subject}")
            print(f"Date: {message.date}")
            print(f"Snippet: {message.snippet}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()