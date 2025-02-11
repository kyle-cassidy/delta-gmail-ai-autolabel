Okay, I understand. You want a flexible, "hot-swappable" parsing engine that can handle different document types (PDF, potentially others) and potentially integrate with different parsing technologies (PyPDF2, Tesseract OCR, cloud-based APIs, LLMs, etc.) without requiring major code rewrites each time. This is an excellent approach for building a robust and adaptable system.

Here's a design for a `DocumentParser` class hierarchy, along with updated code to integrate it:

**1. Design Principles:**

*   **Abstract Base Class (ABC):** We'll create an abstract base class `DocumentParser` that defines the *interface* for all parsers. This ensures consistency.  It will have an abstract `parse()` method.
*   **Concrete Implementations:**  We'll create concrete classes (e.g., `PDFParser`, `TextParser`, `OCRParser`, `LLMParser`) that inherit from `DocumentParser` and implement the `parse()` method in a way specific to their technology.
*   **Factory Pattern (Optional but Recommended):** A factory function or class can be used to create the appropriate parser instance based on the input (e.g., file extension, MIME type, or a configuration setting). This keeps the main processing logic clean and decoupled from the specific parser implementation.
*   **Error Handling:**  Each parser should handle its own potential errors (e.g., file not found, invalid PDF format) and return a consistent error indicator (e.g., `None` for the text, or a dictionary with an "error" key).
*   **Configuration:**  The choice of which parser to use (and any parser-specific settings) can be driven by a configuration file (like your YAML files) or environment variables.

**2. Code Implementation:**

```python
import yaml
import re
import email
from email import policy
from email.parser import BytesParser
import io
import PyPDF2  # Keep this for the PDF example.
from abc import ABC, abstractmethod  # Import ABC and abstractmethod


# --- 1. Abstract Base Class for Parsers ---

class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        """Parses the document content and returns the extracted text.

        Args:
            content_bytes: The document content as bytes.
            filename: The filename (optional, for format detection).

        Returns:
            The extracted text as a string, or None if parsing failed.
        """
        pass


# --- 2. Concrete Parser Implementations ---

class PDFParser(DocumentParser):
    """Parses text from PDF files using PyPDF2."""

    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            with io.BytesIO(content_bytes) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"  # Add newline between pages.
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""  # Return an empty string on error.
        
class TextParser(DocumentParser):
    """Parses plain text files, handles bytes and encoding"""
    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            #Attempt to decode. If there's an error, log and continue
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content_bytes.decode('latin-1') #try different encoding
            except UnicodeDecodeError:
                print (f"Error: Could not decode text from {filename}")
                return ""
            
class HTMLParser(DocumentParser):# Added to include parsing of HTML
    """Parses text from HTML files directly, best for emails."""
    def parse(self, content_bytes: bytes, filename: str = "")-> str:
        try:
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content_bytes.decode('latin-1')#try a different one
            except UnicodeDecodeError:
                print (f"Error: Could not decode HTML from {filename}")
                return ""


# --- 3. Parser Factory (Optional, but recommended) ---

def get_parser(mime_type: str) -> DocumentParser:
    """Factory function to create the appropriate parser based on MIME type."""
    if mime_type == "application/pdf":
        return PDFParser()
    elif mime_type == "text/plain":
        return TextParser()
    elif mime_type == "text/html":
        return HTMLParser()
    # elif mime_type == "image/jpeg":  # Example: If you add OCR later
    #     return OCRParser()
    else:
        print(f"Warning: Unsupported MIME type: {mime_type}. Returning None.")
        return None  # Or raise an exception, depending on your needs.


# --- 4.  Modified Email Parsing (using the parser) ---

def parse_email(email_string):
    """Parses an email, including extracting text from attachments."""
    msg = BytesParser(policy=policy.default).parsebytes(email_string)

    from_email = msg.get("From")
    if from_email:
        match = re.search(r'<(.*?)>', from_email)
        if match:
            from_email = match.group(1)
        else:
            from_email = from_email.strip()

    to_emails = [addr.strip() for header in msg.get_all("To", []) for addr in header.split(',')]
    to_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in to_emails]

    cc_emails = [addr.strip() for header in msg.get_all("Cc", []) for addr in header.split(',')]
    cc_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in cc_emails]

    subject = msg.get("Subject", "")
    message_id = msg.get("Message-ID", "")

    body_plain = ""
    body_html = ""
    email_text = ""  # Accumulate all text here

    if msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            if content_type == "text/plain" and body_plain is None:
                body_plain = part.get_content()
                email_text += body_plain + " " #add plain content
            elif content_type == "text/html" and body_html is None:
                body_html = part.get_content()
                email_text += body_html + " " #add html
            elif content_type.startswith("application/"): #For any application attachments
                filename = part.get_filename()
                if filename:
                    email_text += filename + " "  # Add filename
                parser = get_parser(content_type)
                if parser:
                    extracted_text = parser.parse(part.get_payload(decode=True), filename) #Gets the attachment
                    if extracted_text:
                        email_text += extracted_text + " "
    else:
      if msg.get_content_type() == "text/plain":
          body_plain = msg.get_content()
          email_text += body_plain + " "
      elif msg.get_content_type() == "text/html":
          body_html = msg.get_content()
          email_text += body_html + " "


    return {
        "from_email": from_email,
        "to_emails": to_emails,
        "cc_emails": cc_emails,
        "subject": subject,
        "body_plain": body_plain,  # Keep these for potential separate use
        "body_html": body_html,
        "email_text": email_text,  # Combined text for classification
        "message_id": message_id
    }

# --- 5. Loading YAML Files (same as before) ---
def load_yaml(filepath):
   #same as previous code
    try:
        with open(filepath, 'r', encoding='utf-8') as f:  # Use encoding='utf-8' for broad compatibility
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parsing error in {filepath}: {e}")
        return None

# --- 6. Classification Logic (remains largely the same) ---
def classify_email(email_data, product_categories, regulatory_actions, clients):
      #The rest is the same as before
    #copy and paste from previous code.
    """Classifies an email based on the provided ontology.

    Args:
        email_data: A dictionary containing parsed email data (from parse_email).
        product_categories: The loaded product_categories YAML data.
        regulatory_actions: The loaded regulatory_actions YAML data.
        clients: The loaded clients YAML data.


    Returns:
        A set of Gmail labels (strings).
    """
    labels = set()
    email_text = ""

    if email_data['body_plain']:
        email_text += email_data['body_plain']
    if email_data['body_html']:
        email_text += email_data['body_html'] #Combine for accurate matching
    email_text += " " + email_data['subject']

    # --- 1. Client Identification ---
    sender_domain = email_data['from_email'].split('@')[-1] if email_data['from_email'] else None   # get domain, set None if no from email
    for client_code, client_data in clients.items():
        if sender_domain and sender_domain in client_data['domains']:
            labels.add(f"client:{client_code}")
            break  # Stop after the first client match

        # Check for primary contact email.  This is less reliable than domain.
        if client_data.get('primary_contact_email') == email_data['from_email']:
             labels.add(f"client:{client_code}")
             break
        # Check recipient emails for the primary email
        for email in email_data['to_emails'] + email_data.get('cc_emails', []):  # Check 'to' and 'cc'.
            if client_data.get('primary_contact_email') == email:
                labels.add(f"client:{client_code}")
                break
        else:
            continue  # Continue to the next client if no match is found.
        break  # Break outer loop if a client match is found in recipients


    # --- 2. Product Category and Subcategory ---
    for category, cat_data in product_categories.items():
        if re.search(cat_data['regex'], email_text, re.IGNORECASE):
            labels.add(f"product_category:{category}")
            # Check subcategories
            if 'subcategories' in cat_data:
                for subcategory, sub_data in cat_data['subcategories'].items():
                    if re.search(sub_data['regex'], email_text, re.IGNORECASE):
                        labels.add(f"subcategory:{subcategory}")
                        break  # Stop after the first subcategory match
            break  # Stop after first category match

    # --- 3. Regulatory Action ---
    for action, action_data in regulatory_actions.items():
        if re.search(action_data['regex'], email_text, re.IGNORECASE):
            labels.add(f"action:{action}")
             # Check the Email Subject  # Less reliable, so don't break.
            if re.search(action_data['regex'], email_data['subject'], re.IGNORECASE):
                labels.add(f"action:{action}") # If the subject also matches, less likely to be wrong
            #Removed Break

     # --- 4. State ---
    for state_code in ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]:
            if re.search(f"\\b{state_code}\\b", email_text): #Using the state 2 letter abbreviation, check if in email
                labels.add(f"state:{state_code}")

    # --- 5. Optional Tags (using regex from email_tags.yaml) ---
    for tag_name, tag_data in email_tags['optional'].items():
        if 'regex' in tag_data and re.search(tag_data['regex'], email_text, re.IGNORECASE):
            if 'values' in tag_data:
                #For boolean
                if tag_data['values'] == [True, False]:
                     labels.add(f"{tag_name}:true")
                else: #For List Values
                    match = re.search(tag_data['regex'], email_text, re.IGNORECASE)
                    if match:
                        labels.add(f"{tag_name}:{match.group(0)}")
            #For items with defined values
            elif tag_data['regex']:
                match = re.search(tag_data['regex'], email_text, re.IGNORECASE)
                if match:
                    labels.add(f"{tag_name}:{match.group(0)}")
            else: #for free text values.
                labels.add(f"{tag_name}:true") #Simply Marks as true

    return list(labels) # Convert set to list for Gmail API.

# --- 6. Example usage (replace with your email retrieval) ---
def main():
  # 1. Load configurations
  product_categories = load_yaml("product_categories.yaml")
  regulatory_actions = load_yaml("regulatory_actions.yaml")
  clients = load_yaml("clients.yaml")
  email_tags = load_yaml("email_tags.yaml")
  if not all([product_categories, regulatory_actions, clients, email_tags]):
        print("Error: Could not load all necessary YAML files.")
        return
    
  with open("all_messages.json", "rb") as f:
    emails = json.load(f)
  for email in emails:
    email_str = json.dumps(email).encode('utf-8')
    email_data = parse_email(email_str)
    # print (email_data) #Print to show all email elements
    labels = classify_email(email_data, product_categories, regulatory_actions, clients)
    print (labels)
  
if __name__ == "__main__":
  main()

```

Key Changes in the Code:

*   **`parse_email` Function:**
    *   Now takes the raw email content as `email_string` (in bytes).
    *   Uses `BytesParser(policy=policy.default).parsebytes(email_string)` to parse the email, which correctly handles various encodings and structures.  The `policy=policy.default` is important for modern email handling.
    *   Iterates through parts of multipart emails.
    *   Checks `Content-Type` to identify plain text (`text/plain`), HTML (`text/html`), and PDF (`application/pdf`) parts.
    *   Calls `extract_text_from_pdf` to get text from PDFs.
    *   Accumulates all text (plain, HTML, and from PDFs) into the `email_text` variable.  This is what will be used for classification.
    *   Returns a dictionary with *both* the separate `body_plain` and `body_html` (in case you need them later) *and* the combined `email_text`.
    *   **Robustness:** Includes error handling within `extract_text_from_pdf` and checks if the extracted text is not empty before appending.  This prevents crashes if a PDF can't be parsed.
* **Email Tags Regex:** Added some basic Regex to the email tags, so now the main function can use it to add aditional tags.
* **Client file:** Included the Client email to the clients.yaml in order to get the proper client.
* **Main Function:** Updated the main function to use the parse_email function.

This improved structure gives you a much more flexible and robust foundation.  You can easily add new parsers (for Word documents, images, etc.) by creating new classes that inherit from `DocumentParser`. You can switch between parsers by changing the `get_parser` function or a configuration setting.  And the core classification logic remains clean and separated from the details of how the content is extracted.
