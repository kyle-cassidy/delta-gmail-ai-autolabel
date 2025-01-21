# auto-labeler mvp 

## goal: 
create a simple script that:

1. Uses existing Gmail client
2. Extracts sender domains and subject lines 
3. stores the sender domains in a simple db, csv, or json file
4. Matches against known client/regulator patterns from our data
5. Applies appropriate labels

## example of how we could implement this:

```python
# src/labeler/auto_labeler.py
import re
from typing import Dict, List, Optional, Tuple
from src.client.gmail import Gmail

class AutoLabeler:
    def __init__(self, gmail: Gmail):
        self.gmail = gmail
        
        # Known client domains from your schema
        self.client_domains = {
            'ableagsolutions.com': 'Able Ag Solutions',
            'agrauxine.lesaffre.com': 'Agrauxine',
            'andermatt.usa.com': 'Andermatt',
            'arborjet.com': 'Arborjet',
            'corteva.com': 'Corteva',
            'ecologel.com': 'Ecologel',
            'elementalenzymes.com': 'Elemental Enzymes',
            'omya.com': 'Omya',
            'phillips66.com': 'Phillips 66',
            'pivotbio.com': 'Pivot Bio',
            'symborg.com': 'Symborg'
            # Add other domains from your list
        }
        
        # Common regulator domain patterns
        self.regulator_patterns = {
            r'.*\.ca\.gov': 'California',
            r'.*\.ny\.gov': 'New York',
            r'.*\.state\.tx\.us': 'Texas',
            r'.*\.state\.[a-z]{2}\.us': 'State Agency',
            r'.*\.[a-z]{2}\.gov': 'State Agency'
        }
        
        # Cache for labels
        self._labels_cache = None

    async def ensure_label_exists(self, label_name: str) -> str:
        """Ensure a label exists, creating it if needed"""
        if self._labels_cache is None:
            self._labels_cache = {
                label.name: label.id for label in await self.gmail.list_labels()
            }
            
        if label_name not in self._labels_cache:
            label = await self.gmail.create_label(label_name)
            self._labels_cache[label_name] = label.id
            
        return self._labels_cache[label_name]

    def extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address"""
        if not email:
            return None
            
        match = re.search(r'@([^@\s]+)', email)
        return match.group(1).lower() if match else None

    def classify_email(self, from_address: str, subject: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Classify email by client and regulator
        Returns: (client_label, regulator_label)
        """
        domain = self.extract_domain(from_address)
        if not domain:
            return None, None
            
        # Check client domains
        client_label = None
        if domain in self.client_domains:
            client_label = f"Client/{self.client_domains[domain]}"
            
        # Check regulator patterns
        regulator_label = None
        for pattern, state in self.regulator_patterns.items():
            if re.match(pattern, domain, re.IGNORECASE):
                regulator_label = f"Regulator/{state}"
                break
                
        return client_label, regulator_label

    async def process_unread_messages(self, max_messages: int = 100):
        """Process unread messages and apply labels"""
        messages = await self.gmail.get_unread_messages(max_results=max_messages)
        
        for message in messages:
            from_address = message.get('from', '')
            subject = message.get('subject', '')
            
            client_label, regulator_label = self.classify_email(from_address, subject)
            
            # Apply labels if found
            labels_to_add = []
            if client_label:
                label_id = await self.ensure_label_exists(client_label)
                labels_to_add.append(label_id)
                
            if regulator_label:
                label_id = await self.ensure_label_exists(regulator_label)
                labels_to_add.append(label_id)
                
            if labels_to_add:
                await self.gmail.add_labels(message['id'], labels_to_add)
                print(f"Labeled message: {subject}")
                print(f"Applied labels: {', '.join(filter(None, [client_label, regulator_label]))}")
```

And a simple script to run it:

```python
# scripts/label_emails.py
import asyncio
from src.client.gmail import Gmail
from src.labeler.auto_labeler import AutoLabeler

async def main():
    # Initialize with your existing credentials
    gmail = Gmail(
        client_secret_file="secrets/secret-gmail-ai-autolabel.json",
        creds_file="secrets/gmail_token.json",
    )
    
    labeler = AutoLabeler(gmail)
    
    print("Starting auto-labeling process...")
    await labeler.process_unread_messages(max_messages=50)
    print("Completed auto-labeling process!")

if __name__ == "__main__":
    asyncio.run(main())
```

This MVP will:
1. Use existing Gmail credentials
2. Process unread messages
3. Extract domains from sender addresses 
4. Match against known client domains
5. Match against common regulator domain patterns
6. Create and apply hierarchical labels (Client/CompanyName, Regulator/StateName)
7. Print progress to console


next?
1. Add more sophisticated pattern matching?
2. Add additional logging/reporting?
3. Add subject line analysis for more context?
4. Help set up some test emails for the demo?