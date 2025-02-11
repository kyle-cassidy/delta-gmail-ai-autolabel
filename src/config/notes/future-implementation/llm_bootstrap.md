You've hit on a very intelligent and practical strategy. Using an LLM to jumpstart the dataset and refine your YAML configuration, then transitioning to a primarily regex-based system with LLM fallback, is an excellent approach. Here's a breakdown of why this is a good idea and how to implement it:

**Why This Approach is Effective:**

*   **Bootstrapping with LLM:**
    *   **Initial Labeling:** LLMs are great at understanding context and semantics. You can give the LLM a set of emails and your initial (possibly incomplete) category/action definitions, and ask it to classify them. This gives you a *much* better starting point than manually labeling everything.
    *   **Pattern Discovery:** The LLM can identify keywords and phrases that you might have missed when defining your initial regex patterns.  You can ask it to "explain its reasoning" or "list the key phrases that led to this classification," which helps you build more robust regexes.
    *   **Edge Case Identification:** The LLM will likely flag emails that it's unsure about. These are your edge cases – the emails that your simple regex rules might miss.  You can then manually review these and either adjust your regexes or create special rules.
    *   **Iterative Refinement:** This is a cyclical process.  You use the LLM's output to improve your YAML, re-classify, see where the LLM and regex disagree, and continue refining.

*   **Regex for Speed and Efficiency:**
    *   **Speed:** Once your regex patterns are well-defined, they are *much* faster than calling an LLM API for every email. This is crucial for real-time processing or handling large volumes of email.
    *   **Cost:** LLM API calls can be expensive, especially at scale. Regex matching is essentially free in terms of processing cost.
    *   **Control:** Regex gives you precise control over the matching logic. You can fine-tune the patterns to be as specific or as broad as needed.
    *   **Deterministic:** Regex is deterministic – given the same input, it will always produce the same output.  LLMs can have some variability.

*   **LLM as Fallback:**
    *   **Handling Ambiguity:** Even with well-crafted regexes, there will be cases where the email content is ambiguous or doesn't perfectly match your patterns. The LLM can handle these nuanced cases.
    *   **Continuous Learning:** You can continue to use the LLM on a smaller subset of emails to identify new patterns and improve your rules over time.
    *   **Confidence Scoring:**  You can use the LLM's confidence score (if available) to determine when to trigger the fallback.  For example, if the regex matches, but the LLM has low confidence in its classification, you might flag the email for manual review.

**Implementation Steps (Building on the Previous Code):**

1.  **Choose an LLM:** You'll need to choose a Vision LLM. Some popular options include:
    *   **Google's Gemini Pro Vision:** A good all-around model.
    *   **OpenAI's GPT-4 with Vision:** Very powerful, but can be more expensive.
    *   **Anthropic's Claude 3:** Strong on text understanding and reasoning.
    *   **Open-source models (like LLaVA):**  Require more setup but offer more control and potentially lower cost.

    For immediate implementability, I'd recommend starting with Gemini Pro Vision or GPT-4 with Vision, as they have readily available APIs and good Python libraries.

2.  **Install the LLM Library:**
    *   **Google Gemini:** `pip install google-generativeai`
    *   **OpenAI:** `pip install openai`

3.  **Create an LLM Interaction Function:**  Write a function that takes the email text (and potentially image data) as input, sends it to the LLM, and returns the LLM's response.  This function will handle API authentication, prompting, and response parsing.

    ```python
    import google.generativeai as genai
    import os
    from dotenv import load_dotenv

    load_dotenv()
    GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY') #Best practice store key outside of script

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision') #You'll need to set your model

    def classify_with_llm(email_text, image_data=None):
        """Classifies an email using a Vision LLM.

        Args:
            email_text: The text content of the email.
            image_data: Optional.  A list of image data (bytes) for attachments, if applicable.

        Returns:
            A dictionary containing the LLM's classification, or None on error.
        """
        try:
            prompt = f"""
            You are an expert at classifying emails related to fertilizer and agricultural product regulations.
            Based on the provided email text, determine the following, using ONLY the provided options.
            Do NOT provide any output other than the specified JSON format.

            Product Categories: {", ".join(product_categories.keys())}
            {"""Subcategories: """ + ", ".join(f"{category}: {', '.join(data['subcategories'].keys())}" for category, data in product_categories.items() if 'subcategories' in data) if [f"{category}" for category, data in product_categories.items() if 'subcategories' in data] else ""}
            Actions: {", ".join(regulatory_actions.keys())}
            States:  AL, AK, AZ, AR, CA, CO, CT, DE, DC, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VA, VT, WA, WV, WY
            Email Text:
            {email_text}

            
            Desired output format:
            {{
              "product_category": "<category>",
              "subcategory": "<subcategory>",
              "action": "<action>",
              "state": "<state_code>",
              "confidence": <confidence_score>
            }}
            
            If you cannot determine a value, set as "unknown"
            """
            
            if image_data:
              #Process each image in image data.
              responses = []
              for image in image_data:
                response = model.generate_content([prompt,image]) #Send the prompt, and image.
                responses.append(response.text)
              return responses #Return a list of responses
            else:
                response = model.generate_content(prompt)
                return response.text

        except Exception as e:
            print(f"LLM classification error: {e}")
            return None

    ```

    *   **Prompt Engineering:** The `prompt` is *critical*.  It tells the LLM what you want it to do.  A good prompt should:
        *   **Clearly define the task:**  "Classify this email..."
        *   **Provide context:** Explain what the email is about (fertilizer regulations).
        *   **Specify the output format:**  Tell the LLM *exactly* how you want the output (e.g., JSON with specific keys).  This is *essential* for programmatic use.
        *   **Give examples (few-shot learning):**  Include a few examples of input emails and the desired output. This drastically improves accuracy.  You'll build these examples as you test.
        *   **Constrain the output:** Tell the LLM to only use the provided categories and actions.
        *   **Handle uncertainty:** Tell the LLM what to do if it can't determine a value (e.g., return "unknown").
        * **Include error handling:** use a try-except block.
    *   **API Interaction:** The example uses `model.generate_content()`.  You'll need to adapt this based on your chosen LLM's API.
    *   **Image Handling:** The `if image_data:` block is a placeholder.  You'll need to implement the logic to convert image bytes into a format the LLM accepts (usually base64 encoded).
    *   **Return Value:** The function should return a dictionary that's easy to work with, *not* raw text from the LLM.

4.  **Update `classify_email`:**

    ```python
    def classify_email(email_data, product_categories, regulatory_actions, clients, llm_threshold=0.8):
        """Classifies an email using both regex and (optionally) an LLM.

        Args:
            email_data: Parsed email data (from parse_email).
            product_categories: Loaded product categories.
            regulatory_actions: Loaded regulatory actions.
            clients: Loaded client data.
            llm_threshold: Confidence threshold for using LLM results.

        Returns:
            A set of Gmail labels (strings).
        """

        labels = set()

      # ... (rest of your regex-based classification, as before) ...

        # --- LLM Classification (after regex) ---

        llm_results = classify_with_llm(email_data['email_text'], email_data.get('images')) # Pass images
        if llm_results:
              if type(llm_results) == str: #if not a list, make a list.
                llm_results = [llm_results]
              for result in llm_results: #loop through incase of multiple responses.
                try:
                    result_dict = json.loads(result)  # Parse the JSON
                    if 'product_category' in result_dict and result_dict['product_category'] != "unknown":
                        labels.add(f"product_category:{result_dict['product_category']}")
                    if 'subcategory' in result_dict and result_dict['subcategory'] != "unknown":
                        labels.add(f"subcategory:{result_dict['subcategory']}")
                    if 'action' in result_dict and result_dict['action'] != "unknown":
                        labels.add(f"action:{result_dict['action']}")
                    if 'state' in result_dict and result_dict['state'] != "unknown":
                        labels.add(f"state:{result_dict['state']}")


                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing LLM response: {e}")
                    print(f"Raw LLM output: {result}") # Log the raw output for debugging.

        return list(labels)
    ```

    *   **Combined Logic:**  The function now calls *both* the regex-based classification *and* the LLM classification.
    *   **JSON Parsing:**  The `json.loads()` function attempts to parse the LLM's output as JSON. *Crucially*, this assumes the LLM is following your instructions and returning valid JSON.  This is why prompt engineering is so important.
    *   **Error Handling:** The `try...except` block handles potential errors when parsing the JSON.
    * **Confidence Threshold** I had added this previously, but removed it. It's better to start without this and add it if the other methods are giving many false positives.

5. **Parse Email Function Update**
   *  **Image Extraction**: Added a new key to the email parsing function to store the image data:

    ```python
        def parse_email(email_string, tesseract_path=None):
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
            images = [] # Create an empty list to store image data.

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

                    elif content_type.startswith("image/"):
                        filename = part.get_filename()
                        if filename:
                            email_text += filename + " "
                        image_data = part.get_payload(decode=True)  # Get image bytes
                        images.append(image_data)  # Append the image data
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
                "message_id": message_id,
                "images" : images #Added
            }
    ```

**Action Plan (with LLM Integration):**

1.  **Choose LLM:** Select your Vision LLM provider (Google, OpenAI, Anthropic, etc.).
2.  **Install Library:** Install the necessary Python library for your chosen LLM.
3.  **Implement `classify_with_llm`:** Write this function, including your API key and prompt.  Start with a simple prompt and refine it iteratively.
4.  **Update `parse_email`:** Modify the `parse_email` function as shown above to handle attachments.
5.  **Update `classify_email`:**  Modify the `classify_email` function as shown above to:
    *   Call your new `classify_with_llm` function, passing in the `email_text` and the image list.
    *   Parse the LLM's JSON response.
    *   Add the appropriate labels based on the LLM's output (and potentially the confidence score).
6.  **Initial Testing:**  Run the script on a sample of emails *without* applying labels to Gmail.  Print the detected labels and the LLM's raw output.
7.  **Refine Prompt:**  Iteratively refine your LLM prompt based on the results.  You'll likely need to experiment to find the best wording.
8.  **Refine Regex:**  Use the LLM's output and explanations to identify keywords and phrases you can add to your `product_categories.yaml` and `regulatory_actions.yaml` files.
9. **Set Threshold (Optional but useful):** Determine threshold for the regex/LLM.
10. **Integrate with Gmail API:** Once you're confident in the classification accuracy, integrate the code with the Gmail API to automatically apply labels.
11. **Monitor and Iterate:**  Continuously monitor the performance and make adjustments as needed.

**Example Prompt (for `classify_with_llm` - adjust as needed):**

```python
prompt = f"""
You are an expert at classifying emails related to fertilizer and agricultural product regulations.
Based on the provided email text, determine the following, using ONLY the provided options.
Do NOT provide any output other than the specified JSON format.

Product Categories: {", ".join(product_categories.keys())}
{"""Subcategories: """ + ", ".join(f"{category}: {', '.join(data['subcategories'].keys())}" for category, data in product_categories.items() if 'subcategories' in data) if [f"{category}" for category, data in product_categories.items() if 'subcategories' in data] else ""}
Actions: {", ".join(regulatory_actions.keys())}
States:  AL, AK, AZ, AR, CA, CO, CT, DE, DC, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VA, VT, WA, WV, WY

Email Text:
{email_text}


Desired output format:
{{
  "product_category": "<category>",
  "subcategory": "<subcategory>",
  "action": "<action>",
  "state": "<state_code>",
  "confidence": <confidence_score>
}}

If you cannot determine a value, set as "unknown"
"""
```

This prompt:

*   Clearly instructs the LLM on its task.
*   Provides the allowed categories and actions *directly* from your YAML.  This keeps everything synchronized.
*   Specifies the JSON output format.
*   Handles the "unknown" case.
This provides the best next step to incorporate a vision LLM into our classification pipeline.
