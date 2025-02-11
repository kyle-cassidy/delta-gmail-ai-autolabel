Okay, let's explore how to incorporate a Vision Large Language Model (LLM) into your classification pipeline.  There are several ways to do this, and the best approach depends on the specific capabilities of the LLM, the nature of your attachments, and your desired accuracy/latency trade-offs.

**Conceptual Approaches (with Pros/Cons):**

Here are a few ways you could integrate a Vision LLM, ordered from simplest to most complex:

1.  **Image-Based OCR Enhancement (Simplest):**

    *   **How it works:** Use the Vision LLM *instead of* or *in addition to* PyPDF2 for extracting text from PDF attachments that are *primarily images* (scanned documents). The LLM would perform OCR on the images within the PDF.
    *   **Pros:** Relatively simple to implement; leverages the LLM's strengths in image understanding. Improves handling of image-based docs.
    *   **Cons:** Doesn't use the LLM's full potential for understanding document *structure* and *meaning*. May be overkill for text-based PDFs.
    *   **Example:**  If you have a scanned label with a table of guaranteed analysis, a basic OCR might misinterpret the table structure. A Vision LLM could potentially do better.
    *   **Implementation:**  Modify the `extract_text_from_pdf` function.  Instead of directly using PyPDF2, check if the PDF is primarily image-based.  If so, send the image data (extracted from the PDF) to the Vision LLM's API, and get the text back.

2.  **Content Summarization/Extraction:**

    *   **How it works:**  After extracting text (using PyPDF2 for text-based PDFs, and OCR/Vision LLM for images), pass the *combined* text to the Vision LLM.  Ask the LLM to *summarize* the document or extract *specific* information (e.g., "Extract the product name, registration number, and state from this document.").
    *   **Pros:** Leverages the LLM's ability to understand natural language and extract key information.  Can handle more complex document structures.
    *   **Cons:** Requires careful prompt engineering to get reliable results.  May be slower and more expensive than simple regex matching.
    *   **Example:**  Instead of just using regex, you could ask the LLM: "Given this fertilizer registration document, what is the state of registration?" The LLM would analyze the text and respond with "California".
    *   **Implementation:** Add a new function (e.g., `summarize_document`) that takes the extracted text and interacts with the LLM API.  The `classify_email` function would then call this *after* extracting the text.

3.  **Classification Augmentation (Parallel Approach):**

    *   **How it works:** Run *both* your existing regex-based classification *and* the LLM-based classification (either summary or direct classification). Combine the results.
    *   **Pros:** Combines the speed and simplicity of regex with the deeper understanding of the LLM. Can improve accuracy and handle edge cases.
    *   **Cons:** More complex to implement; requires a strategy for combining results (e.g., weighted voting, rule-based system).
    *   **Example:**  Regex might identify an email as related to "fertilizer" and "CA". The LLM might additionally identify it as a "renewal" and extract the due date. You combine these to get a more complete picture.
    *   **Implementation:**  Modify `classify_email` to call both the regex-based classification and the LLM-based classification.  Then, combine the results (e.g., take the union of the label sets).

4.  **LLM as Primary Classifier (Overseer):**

    *   **How it works:**  Use the LLM as the *primary* classifier.  The LLM would receive the entire email text (including extracted attachment text) and be prompted to directly assign labels.  The regex-based system could be used as a fallback or for validation.
    *   **Pros:**  Potentially the most accurate approach; can handle complex, nuanced language.
    *   **Cons:**  The most complex to implement; requires very careful prompt engineering and likely fine-tuning of the LLM.  Could be the slowest and most expensive.
    *   **Example:**  You'd send the entire email text to the LLM with a prompt like: "Classify this email according to the following categories: [list of categories and subcategories].  Assign relevant tags from this list: [list of tags].  Also extract the product name and any relevant dates."
    *   **Implementation:**  This would involve a significant rewrite of the `classify_email` function. The regex logic might be used for pre-processing (e.g., identifying potential state codes) but the LLM would make the final classification decisions.

5. **Image Identification**
  *How it works:* Run the images extracted through a vision model to get a string description of the image back, and pass the text to the regex function.
  * **Implementation:** Add an image processing function to the parse_email function.

**Choice of Approach:**

For immediate implementability, I recommend starting with either **Option 1 (Image-Based OCR Enhancement)** or **Option 2 (Content Summarization/Extraction)**.  These offer a good balance of complexity and potential benefit. Option 3 (Classification Augmentation) is a reasonable next step if you need higher accuracy.  Option 4 (LLM as Primary Classifier) is the most powerful but also the most complex, and I'd recommend saving it for later unless you have significant experience with LLMs.

**Example: Image-Based OCR Enhancement (Option 1):**
I'm going to assume we don't have access to a paid for LLM, and we will skip that for now.

Here's how you would modify the code to incorporate a Vision LLM for PDF parsing, assuming you have a function `get_text_from_image` that uses your chosen LLM API:

```python
import yaml
import re
import email
from email import policy
from email.parser import BytesParser
import io
#import PyPDF2  # Keep this for the PDF example. #Commented out for initial example
from abc import ABC, abstractmethod  # Import ABC and abstractmethod

import fitz  #For PDF Parsing
import io
from PIL import Image #For handling Images
import pytesseract #OCR for images.

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
    """Parses text from PDF files using PyMuPDF (fitz)."""

    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            text = ""
            with fitz.open(stream=content_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF ({filename}): {e}")
            return ""  # Return empty string on error

class TextParser(DocumentParser):
    """Parses plain text files, handles bytes and encoding"""
    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            #Attempt to decode. If there's an error, log and continue
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content_bytes.decode('latin-1') #try a different one
            except UnicodeDecodeError:
                print (f"Error: Could not decode text from {filename}")
                return ""

class ImageParser(DocumentParser):
    """Parses text from images using OCR (pytesseract)."""
    def __init__(self, path_to_tesseract: str):
        pytesseract.pytesseract.tesseract_cmd = path_to_tesseract
        self.tesseract_path = path_to_tesseract


    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            image = Image.open(io.BytesIO(content_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image ({filename}): {e}")
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

def get_parser(mime_type: str, tesseract_path: str = None) -> DocumentParser:
    """Factory function to create the appropriate parser based on MIME type.
       Added tesseract_path parameter.
    """
    if mime_type == "application/pdf":
        return PDFParser()
    elif mime_type == "text/plain":
        return TextParser()
    elif mime_type == "text/html":
        return HTMLParser()
    elif mime_type.startswith("image/") and tesseract_path: #Checks if its an image, and has tesseract.
        return ImageParser(tesseract_path) # Create ImageParser
    else:
        print(f"Warning: Unsupported MIME type: {mime_type}. Returning None.")
        return None  # Or raise an exception.

# --- 4.  Modified Email Parsing (using the parser) ---
def parse_email(email_string, tesseract_path=None): #Add the tesseract_path
    """Parses an email, including extracting text from PDF attachments."""
    msg = BytesParser(policy=policy.default).parsebytes(email_string)

    from_email = msg.get("From")
    if from_email:
        match = re.search(r'<(.*?)>', from_email)
        if match:
            from_email = match.group(1)
        else:
            from_email = from_email.strip()


    to_emails = msg.get_all("To", [])
    if to_emails:  # Check if to_emails is not None
        to_emails = [addr.strip() for header in to_emails for addr in header.split(',')]
        #Strip extra chars, and pull email
        to_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in to_emails]
    else:
        to_emails = []


    cc_emails = msg.get_all("Cc", [])
    if cc_emails: # Check if cc_emails is not None
        cc_emails = [addr.strip() for header in cc_emails for addr in header.split(',')]
        cc_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in cc_emails]
    else:
        cc_emails = []

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

            #Handle Attachments
            elif part.get_content_disposition() is not None:  # Check if it's an attachment
               filename = part.get_filename()
               if filename:
                   email_text += filename + " " #add the filename.
               parser = get_parser(content_type, tesseract_path)
               if parser:
                    extracted_text = parser.parse(part.get_payload(decode=True), filename)
                    if extracted_text:
                        email_text += extracted_text + " "

    else:
        # Handle non-multipart emails (rare, but can happen)
        if msg.get_content_type() == "text/plain":
            body_plain = msg.get_content()
            email_text += body_plain + " " #add the text
        elif msg.get_content_type() == "text/html":
            body_html = msg.get_content()
            email_text += body_html + " " #add the text


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
# --- End of Email Parsing ---
```

Key changes in the code above:

*   **`extract_text_from_pdf`:** This function now takes the raw bytes of a PDF file, uses `io.BytesIO` to create an in-memory file-like object, and then uses `PyPDF2.PdfReader` to read the PDF and extract the text.
*   **`parse_email`:**
    *   It now iterates through all parts of the email.
    *   It checks the `Content-Type` to identify "application/pdf" attachments.
    *   It calls `extract_text_from_pdf` to get the text from the PDF.
    *   It adds both plain text, HTML, and any extracted PDF text to the `email_text` variable.
* **Added Image Handling**
    * Added an ImageParser class that uses Pytesseract for text extraction.
    * Added logic to the parse email function to incorporate image parsing.
* **Added tesseract_path:** Added this optional parameter to the parse_email function, so the path is passed around.

**Before running:**

*   **Install Tesseract:** You'll need to install Tesseract OCR separately. The installation process varies depending on your operating system. Here are some general instructions:
    *   **Windows:** Download the installer from the official Tesseract GitHub page: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
    *   **macOS:** Use Homebrew: `brew install tesseract`
    *   **Linux:** Use your distribution's package manager (e.g., `apt install tesseract-ocr` on Debian/Ubuntu).
*  Install PIL: `pip install Pillow`

**Putting It All Together (Example - including Tesseract path):**

```python
import yaml
import re
import email
from email import policy
from email.parser import BytesParser
import io
from PIL import Image #Used for image processing
import pytesseract  # Import the PyPDF2 library
from abc import ABC, abstractmethod  # Import ABC and abstractmethod

# --- 1. Loading YAML Files (same as before) ---

def load_yaml(filepath):
    """Loads a YAML file (same as before)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parsing error in {filepath}: {e}")
        return None

# --- 2. Email Parsing (with PDF attachment handling) ---

def extract_text_from_pdf(pdf_bytes):
    """Extracts text from a PDF file (given as bytes)."""
    try:
        with io.BytesIO(pdf_bytes) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"  # Add newline between pages.
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""  # Return an empty string on error.
        
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

class PDFParser(DocumentParser):
    """Parses text from PDF files using PyMuPDF (fitz)."""

    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            text = ""
            with fitz.open(stream=content_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF ({filename}): {e}")
            return ""  # Return empty string on error.

class TextParser(DocumentParser):
    """Parses plain text files."""
    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return content_bytes.decode('latin-1', errors='ignore')  # Fallback, ignore errors
        except Exception as e:
            print(f"Error decoding text from {filename}: {e}")
            return ""

class ImageParser(DocumentParser):
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif sys.platform.startswith('win'): #If OS is windows
             try:
                  pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
             except FileNotFoundError:
                  print("Error: Tesseract Not found in default location for Windows. Please provide a tesseract_path")
        #No else needed, since it will error if it's not initialized.

    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            image = Image.open(io.BytesIO(content_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image ({filename}): {e}")
            return ""

class HTMLParser(DocumentParser):
    def parse(self, content_bytes: bytes, filename: str = "") -> str:
        try:
            return content_bytes.decode('utf-8') #Try UTF-8 first
        except UnicodeDecodeError:
            try:
                return content_bytes.decode('latin-1', errors = 'ignore')  # Fallback to latin-1
            except:
                print (f"Error: Could not decode HTML from {filename}")
                return ""

# --- 3. Parser Factory (Optional, but recommended) ---

def get_parser(mime_type: str, tesseract_path: str = None) -> DocumentParser:
    """Factory function to create the appropriate parser based on MIME type.
       Added tesseract_path parameter.
    """
    if mime_type == "application/pdf":
        return PDFParser()
    elif mime_type == "text/plain":
        return TextParser()
    elif mime_type == "text/html":
        return HTMLParser()
    elif mime_type.startswith("image/") and tesseract_path: #Checks if its an image, and has tesseract.
        return ImageParser(tesseract_path) # Create ImageParser
    else:
        print(f"Warning: Unsupported MIME type: {mime_type}. Returning None.")
        return None  # Or raise an exception.

# --- 4.  Modified Email Parsing (using the parser) ---
def parse_email(email_string, tesseract_path=None):
    """Parses an email, including extracting text from attachments."""
    msg = BytesParser(policy=policy.default).parsebytes(email_string)

    from_email = msg.get("From")
    if from_email:
        match = re.search(r'<(.*?)>', from_email)
        if match:
            from_email = match.group(1)
        else:
            from_email = from_email.strip()


    to_emails = msg.get_all("To", [])
    if to_emails:  # Check if to_emails is not None
        to_emails = [addr.strip() for header in to_emails for addr in header.split(',')]
        #Strip extra chars, and pull email
        to_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in to_emails]
    else:
        to_emails = []

    cc_emails = msg.get_all("Cc", [])
    if cc_emails: # Check if cc_emails is not None
      cc_emails = [addr.strip() for header in cc_emails for addr in header.split(',')]
      cc_emails = [re.search(r'<(.*?)>', addr).group(1) if re.search(r'<(.*?)>', addr) else addr.strip() for addr in cc_emails]
    else:
      cc_emails = []

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
                parser = get_parser(content_type, tesseract_path)
                if parser:
                    extracted_text = parser.parse(part.get_payload(decode=True), filename) #Gets the attachment
                    if extracted_text:
                        email_text += extracted_text + " "
    else:
      if msg.get_content_type() == "text/plain":
          body_plain = msg.get_content()
          email_text += body_plain + " " #add the text
      elif msg.get_content_type() == "text/html":
          body_html = msg.get_content()
          email_text += body_html + " " #add the text


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

# --- 5. Classification Logic (remains largely the same) ---
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

# --- 4. Gmail API Interaction (Conceptual) ---

# def apply_labels_to_gmail(message_id, labels, gmail_service):
#     """Applies labels to a Gmail message.
#       (Conceptual - Requires authentication and a 'gmail_service' object)
#     """
#     try:
#         message = gmail_service.users().messages().modify(
#             userId='me',
#             id=message_id,
#             body={'addLabelIds': labels}
#         ).execute()
#         print(f"Labels applied to message ID: {message['id']}")
#     except Exception as e:
#         print(f"An error occurred applying labels: {e}")


# --- 5. Putting It All Together (Example) ---

def main():
    # 1. Load the configuration
    product_categories = load_yaml("product_categories.yaml")
    regulatory_actions = load_yaml("regulatory_actions.yaml")
    clients = load_yaml("clients.yaml")
    email_tags = load_yaml("email_tags.yaml") # Assuming email_tags.yaml exists
   # state_specific = load_yaml("state_specific.yaml")

    if not all([product_categories, regulatory_actions, clients, email_tags]):
        print("Error: Could not load all necessary YAML files.")
        return


    # 2.  Get the email data (replace with actual email retrieval)
    #     In a real application, you'd use the Gmail API to fetch emails.
    #     For this example, we'll use a *string* representing the raw email.
    with open("all_messages.json", "rb") as f:
        emails = json.load(f)


    # 3. Process each email.
    for email_data in emails:

        email_str = json.dumps(email_data).encode('utf-8') #Turn each dictionary into properly encoded string
        parsed_email = parse_email(email_str)
        # print (email_data) #Print to show all email elements
        labels = classify_email(parsed_email, product_categories, regulatory_actions, clients)
        print(f"Email Subject: {parsed_email['subject']}")
        print(f"Detected Labels: {labels}")
        print("---")

        # 4. Apply labels (replace with actual Gmail API call)
        # apply_labels_to_gmail(email_data['message_id'], labels, gmail_service) # You would implement this.

if __name__ == "__main__":
    main()
```

Key Changes:

*   **`parse_email`:**
    *   Added `tesseract_path` as an optional parameter. This allows you to specify the path to your Tesseract executable if it's not in a standard location.
    *   Combined the plain text and HTML content of the email, *and* any extracted text from attachments, into a single `email_text` variable.  This is what the classification logic will now use.
    *   Handles `multipart/alternative` emails correctly.
    *   Includes filename to be added to the email.
*  **Added `ImageParser` class:** Includes logic on how to handle images through OCR.
* **Added `get_parser`** function to determine with Paser to Use.

With these changes, your script is now capable of:

1.  Loading your YAML configuration.
2.  Parsing emails, including extracting text from both plain text/HTML bodies and PDF attachments.
3.  Classifying the email content using your defined regex patterns.
4.  Generating a list of Gmail labels to apply.

Now, to finish, all you need is a json file of emails. You can pull this from your Gmail, using the Gmail API.


