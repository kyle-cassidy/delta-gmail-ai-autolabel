from autolabel.simplegmail import Gmail

# Initialize Gmail with our credentials file
gmail = Gmail(
    client_secret_file='secrets/secret-gmail-ai-autolabel.json',
    creds_file='gmail-token.json'
)

# Test by getting labels (simple operation)
try:
    labels = gmail.list_labels()
    print("Authentication successful!")
    print("\nAvailable labels:")
    for label in labels:
        print(f"- {label.name}")
except Exception as e:
    print("Authentication failed:")
    print(e)