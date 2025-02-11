# Regulatory Ontology Brief

**1. Introduction**

This document describes the ontology developed for classifying and managing regulatory information related to fertilizers, soil amendments, liming materials, biostimulants, and adjuvants across different US states. The ontology is designed to be used in an automated system for processing incoming emails and documents related to these products and their regulatory requirements.

**2. Purpose**

The primary goals of this ontology are:

*   **Standardization:** Provide a consistent, standardized vocabulary for describing product categories and regulatory actions, overcoming variations in terminology used by different states.
*   **Automation:** Enable automated classification of incoming emails and documents based on their content.
*   **Data Management:** Organize and structure regulatory data in a way that facilitates efficient querying, reporting, and tracking of compliance status.
*   **Workflow Support:** Model the typical workflows and dependencies between different regulatory actions (e.g., registration, licensing, tonnage reporting).
*   **Data Validation:** Provide rules for validating extracted data to ensure accuracy.
*   **Extensibility:** Be easily extendable to accommodate new product categories, regulatory actions, and state-specific rules.

**3. Ontology Structure (YAML)**

The ontology is defined using YAML, a human-readable data serialization format. It is divided into multiple files for better organization and maintainability:

*   **`product_categories.yaml`:** Defines the hierarchical structure of product categories and subcategories (e.g., `fertilizer.commercial`, `biostimulant.soil_amendment`).  Includes state-specific terms and regular expression patterns for matching.
*   **`regulatory_actions.yaml`:** Defines the different types of regulatory actions (e.g., `registration`, `licensing`, `tonnage`). Includes document markers and regex patterns for identification.
*   **`state_specific.yaml`:** Contains state-specific overrides and additions to the general rules (e.g., unique requirements, fees, renewal schedules).
*   **`email_tags.yaml`:** Defines the structure for tagging incoming emails, including required and optional fields, and contextual rules for classification.
*   **`validation_rules.yaml`:** Defines rules for validating extracted data (e.g., registration number formats, date formats).
*   **`relationships.yaml`:** Defines relationships between different parts of the ontology (e.g., product types and required actions, dependencies between actions).
*   **`status_workflows.yaml`:** Defines the possible states and transitions for different regulatory actions, enabling workflow management.
*   **`fee_structures.yaml`:** (Planned) Defines fee structures for different actions and states, enabling automated fee calculation.

**4. Key Concepts**

*   **Canonical Names:** Standardized terms used to represent concepts across different states (e.g., "Commercial Fertilizer").
*   **State Terms:** The specific terms used by each state for a given concept (e.g., "Agricultural Fertilizer", "Fertilizer").
*   **Patterns (Regex):** Regular expressions used for robust matching of state terms and other keywords in email and document content.
*   **Document Markers:**  Keywords, phrases, and structural elements (headers, sections) that help identify the type of document and extract relevant information.
*   **Contextual Rules:** Rules that use the presence of multiple keywords or other contextual information to refine classifications.
*   **Validation Rules:** Rules that check the format and validity of extracted data.
*   **Relationships:**  Connections between different parts of the ontology, defining dependencies and workflows.
*   **Status Workflows:**  Defined sequences of states that track the progress of a regulatory item.

**5. Implementation Notes**

*   **YAML Parsing:** Use the `PyYAML` library in Python to load the YAML files into Python data structures (dictionaries and lists).
*   **Regex Compilation:** Compile the regular expression patterns *once* when the application starts, for efficiency.  Use the `re.IGNORECASE` flag for case-insensitive matching.
*   **Keyword Matching:** Start with basic keyword matching using the `state_terms` and `canonical_name`.
*   **Regex Matching:** Implement more robust matching using the `patterns` defined in the YAML.
*   **Contextual Rules:** Implement the logic for evaluating contextual rules after initial keyword/regex matching.
*   **Data Validation:** Use the `validation_rules` to check the format and validity of extracted data.
*   **State-Specific Overrides:** Always check the `state_specific` section for any overrides to the general rules.
*   **Status Tracking:** Implement a mechanism (database table or in-memory data structure) to track the `current_state` of each regulatory item, based on the `status_workflows`.
*   **Iterative Refinement:**  The ontology and matching logic will likely need to be refined iteratively as you test the system with real-world data.

**6. YAML File Contents**
(All previous YAML code block outputs are included below)

**`product_categories.yaml`**

```yaml
# product_categories.yaml
# Defines the hierarchical structure of product categories and subcategories.
# Maps state-specific terms to canonical names, including regex patterns for matching.

product_categories:
  fertilizer:
    canonical_name: "Fertilizer"
    priority: 1  # Higher number = higher priority (for conflict resolution)
    common_misspellings: ["fertlizer", "fertilser", "fert"] #For fuzzy matching
    related_terms: ["plant food", "plant nutrient", "NPK"] #For contextual clues
    exclusions: ["pesticide", "herbicide", "insecticide", "fungicide"] # Avoid misclassification
    subcategories:
      commercial:
        canonical_name: "Commercial Fertilizer"
        state_terms:
          - term: "Commercial Fertilizer"
            states: ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MO", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
              - regex: "(?i)\\bcommercial\\s+fertilizer\\b"  # Case-insensitive, word boundaries
                confidence: 0.9
              - regex: "(?i)\\bcomm\\.?\\s+fertilizer\\b" #Handles abbreviation "comm."
                confidence: 0.8
          - term: "Agricultural Fertilizer"
            states: ["CA"]
            patterns:
              - regex: "(?i)\\bagricultural\\s+fertilizer\\b"
                confidence: 0.9
              - regex: "(?i)\\bag\\s+fertilizer\\b"  # Common abbreviation
                confidence: 0.7
          - term: "Farm Fertilizer"
            states: ["KY"]
            patterns:
              - regex: "(?i)\\bfarm\\s+fertilizer\\b"
                confidence: 0.9
          - term: "Fertilizer" # A general term if a more specific doesn't fit
            states: ["AK","DC", "HI"]
            patterns:
              - regex: "(?i)\\bfertilizer\\b"
                confidence: 0.95 #High confidence because it's the base term.
      specialty:
        canonical_name: "Specialty Fertilizer"
        state_terms:
          - term: "Specialty Fertilizer"
            states: [ "AR", "AZ", "CA", "CO", "CT", "FL", "GA", "IA", "KS", "KY", "MA", "MD", "ME", "MI", "MN", "MS", "MO", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
              - regex: "(?i)\\bspecialty\\s+fertilizer\\b"
                confidence: 0.95
          - term: "Non-Agricultural Fertilizer"
            states: []
            patterns:
              - regex: "(?i)\\bnon-?agricultural\\s+fertilizer\\b" # Handles with and without hyphen
                confidence: 0.9
          - term: "Special Mix Fertilizer"
            states: []
            patterns:
              - regex: "(?i)\\bspecial\\s+mix\\s+fertilizer\\b"
                confidence: 0.8

      agricultural_mineral:
        canonical_name: "Agricultural Mineral"
        state_terms:
          - term: "Agricultural Mineral"
            states: ["CA"]
            patterns:
                - regex: "(?i)\\bagricultural\\s+mineral\\b"
                  confidence: 0.95

      bulk_agricultural_mineral:
        canonical_name: "Bulk Agricultural Mineral"
        state_terms:
          - term: "Bulk Agricultural Mineral"
            states: ["CA"]
            patterns:
                - regex: "(?i)\\bbulk\\s+agricultural\\s+mineral\\b"
                  confidence: 0.95

  biostimulant:
    canonical_name: "Biostimulant"
    priority: 2
    common_misspellings: []
    related_terms: ["plant growth regulator", "soil enhancer", "plant amendment"]
    exclusions: ["fertilizer", "pesticide", "herbicide"]
    subcategories:
      biological_inoculant:
        canonical_name: "Biological Inoculant"
        state_terms:
          - term: "Biological Inoculant"
            states: ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
              - regex: "(?i)\\bbiological\\s+inoculant\\b"
                confidence: 0.9
          - term: "Pure or Mixed Cultures of Microorganisms"
            states: ["IN"]
            patterns:
              - regex: "(?i)\\bpure\\s+or\\s+mixed\\s+cultures\\s+of\\s+microorganisms?\\b"
                confidence: 0.9
          - term: "Legume Inoculant"
            states: ["OH"]
            patterns:
              - regex: "(?i)\\blegume\\s+inoculant\\b"
                confidence: 0.9
          - term: "Microbial Inoculant"
            states: ["HI", "NJ"]
            patterns:
                - regex: "(?i)\\microbial\\s+inoculant\\b"
                  confidence: 0.95
          - term: "Microbial Product" #HI uses this
            states: ["HI"]
            patterns:
                - regex: "(?i)\\bmicrobial\\s+product\\b"
                  confidence: 0.9
          - term: "Soil or Plant Inoculants"
            states: ["NY"]
            patterns:
                - regex: "(?i)\\bsoil\\s+or\\s+plant\\s+inoculants?\\b"
                  confidence: 0.9
          - term: "Seed Treatment Label" # Added based on CA
            states: ["CA"]
            patterns:
                - regex: "(?i)\\bseed\\s+treatment\\s+label\\b"
                  confidence: 0.9
      soil_amendment:
        canonical_name: "Soil Amendment"
        state_terms:
          - term: "Soil Amendment"
            states:  ["AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
              - regex: "(?i)\\bsoil\\s+amendment\\b"
                confidence: 0.95
          - term: "Soil Conditioner"
            states: ["DE", "MO"] #Added IA, DE
            patterns:
              - regex: "(?i)\\bsoil\\s+conditioner\\b"
                confidence: 0.9
          - term: "Auxiliary soil and plant substance" #From CA
            states: ["CA"]
            patterns:
                - regex: "(?i)\\bauxiliary\\s+soil\\s+and\\s+plant\\s+substance\\b"
                  confidence: 0.9
          - term: "Plant Amendment"
            states: ["CO", "ND"]
            patterns:
              - regex: "(?i)\\bplant\\s+amendment\\b"
                confidence: 0.9
      plant_amendment: # Added based on CO, ND
        canonical_name: "Plant Amendment"
        state_terms:
          - term: "Plant Amendment"
            states: ["CO", "ND"]
            patterns:
              - regex: "(?i)\\bplant\\s+amendment\\b" #same pattern, higher confidence in this context.
                confidence: 0.95
      beneficial_substance:  # Added, covers multiple subcategories.
        canonical_name: "Beneficial Substance"
        state_terms:
            - term: "Beneficial Substance"
              states:  ["AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
                - regex: "(?i)\\bbeneficial\\s+substance\\b"
                  confidence: 0.9

  liming_material:
    canonical_name: "Liming Material"
    priority: 3
    common_misspellings: ["limeing"]
    related_terms: ["agricultural lime", "ag lime", "lime"]
    exclusions: []
    subcategories:
      agricultural_liming_material:
        canonical_name: "Agricultural Liming Material"
        state_terms:
          - term: "Agricultural Liming Material"
            states: ["NH", "NY"]
            patterns:
                - regex: "(?i)\\bagricultural\\s+liming\\s+material\\b" #From before
                  confidence: 0.9
                - regex: "(?i)\\bagricultural\\s+lime\\b" #From before
                  confidence: 0.8
          - term: "Lime Material"
            states: ["AL", "CO", "CT", "DE", "FL", "GA", "IA", "KY", "MD", "ME", "MS", "NJ", "OK", "TN"]
            patterns:
                - regex: "(?i)\\blime\\s+material\\b"
                  confidence: 0.9
          - term: "Liming Material"
            states:  ["AR", "AZ", "CT", "DE", "FL", "GA", "IA", "KS", "KY", "LA", "ME", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
            patterns:
              - regex: "(?i)\\bliming\\s+material\\b"
                confidence: 0.95

  adjuvant:
      canonical_name: "Adjuvant"
      priority: 4
      common_misspellings: []
      related_terms: ["surfactant", "wetting agent"]
      exclusions: []
      subcategories: {}
      state_terms:
        - term: "Adjuvant"
          states: ["AR", "AZ", "CA", "CO", "DE", "ID"]
          patterns:
            - regex: "(?i)\\badjuvant\\b"
              confidence: 0.95
        - term: "Pesticide" #Some states classify adjuvants as pesticides
          states: ["AL", "AR", "CA", "DE", "ID", "KY", "TN"]
          patterns:
            - regex: "(?i)\\bpesticide\\b"
              confidence: 0.7  #Lower confidence, as it could be other pesticides
        - term: "Adjuvant/Pesticide" #Combined term
          states: ["AR", "CA", "DE"]
          patterns:
            - regex: "(?i)\\badjuvant\\s*/\\s*pesticide\\b" #Handles the "/"
              confidence: 0.9
```

**`regulatory_actions.yaml`**

```yaml
# regulatory_actions.yaml
# Defines the different types of regulatory actions.

regulatory_actions:
  registration:
    canonical_name: "Product Registration"
    document_markers:  # Information to help identify registration-related documents
      required_fields:
        - "company name"
        - "product name"
        - "registration number"  # Might not be present on initial registration
        - "guaranteed analysis" # Very common for fertilizers
        - "ingredients" # Or "active ingredients"
      typical_headers:
        - "(?i)Product Registration Form"
        - "(?i)New Registration Application"
        - "(?i)Application for Registration"
        - "(?i)Registration Form"
      typical_sections:
        - "(?i)Product Information"
        - "(?i)Company Information"
        - "(?i)Fee Calculation"  #Might be present
        - "(?i)Guaranteed Analysis"
        - "(?i)Ingredients"
        - "(?i)Directions for Use"
      # State-specific overrides *within* document_markers can go here.
      state_specific:
        CA:
          required_fields: ["heavy metals analysis"]

    state_terms:
      - term: "New Registration"
        states: []
        patterns:
          - regex: "(?i)\\bnew\\s+registration\\b"
            confidence: 0.9
      - term: "Initial Registration"
        states: []
        patterns:
          - regex: "(?i)\\binitial\\s+registration\\b"
            confidence: 0.9
      - term: "Product Registration"
        states: []
        patterns:
          - regex: "(?i)\\bproduct\\s+registration\\b"
            confidence: 0.95
      - term: "Label Submission" #Sometimes this is all that is required
        states:  ["AL", "AZ", "FL", "GA", "IA", "KS", "LA", "ME", "MO", "NC", "NE", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns:
            - regex: "(?i)\\blabel\\s+submission\\b"
              confidence: 0.95
            - regex: "(?i)\\bsubmit(?:ting)?\\s+label\\b" # Handles "submit label" and "submitting label"
              confidence: 0.9
            - regex: "(?i)\\blabel\\s+only\\b"
              confidence: 0.8
      - term: "Guidance" #For CA seed treatment
        states: ["CA"]
        patterns:
            - regex: "(?i)\\bguidance\\b"
              confidence: 0.9
      - term: "Registration" #Catch all for when not specified as New or Initial
        states: ["AR", "AZ", "CA", "CO", "CT", "DE", "GA", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns: #add a general regex for Registration
          - regex: "(?i)\\bregistration\\b"
            confidence: 0.85  # Slightly lower confidence, as it's very general
      - term: "Regulated with License" #Added because some states have this designation
        states: ["FL", "KY"]
        patterns:
          - regex: "(?i)\\bregulated\\s+with\\s+license\\b" # Example
            confidence: 0.9

  licensing:
    canonical_name: "Company Licensing"
    document_markers:
        required_fields:
            - "company name"
            - "company address"
        typical_headers:
            - "(?i)license application"
            - "(?i)permit application"
            - "(?i)application for license"
        typical_sections:
            - "(?i)company information"
            - "(?i)facility information"
            - "(?i)contact information"
            - "(?i)fee schedule"

    state_terms:
      - term: "License"
        states: ["AR", "CO", "CT", "FL", "GA", "IA", "IL", "KY", "LA", "ME", "MN", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns:
              - regex: "(?i)\\blicense\\b"
                confidence: 0.95
      - term: "Permit"  # Sometimes used interchangeably with License
        states: ["AL","CT","FL", "GA", "MO"]
        patterns:
              - regex: "(?i)\\bpermit\\b"
                confidence: 0.9
      - term: "Fertilizer Dealer Permit"
        states: ["AL"]
        patterns:
              - regex: "(?i)\\bfertilizer\\s+dealer\\s+permit\\b"
                confidence: 0.95
      - term: "Fertilizer Manufacturers Permit"
        states: ["AL"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+manufacturers?\\s+permit\\b" #Handles manufacturer/manufacturers
              confidence: 0.95
      - term: "Fertilizing Material License"
        states: ["CA"]
        patterns:
            - regex: "(?i)\\bfertilizing\\s+material\\s+license\\b"
              confidence: 0.95
      - term: "Commercial Fertilizer License"
        states: ["AZ", "GA", "MA"]
        patterns:
            - regex: "(?i)\\bcommercial\\s+fertilizer\\s+license\\b"
              confidence: 0.95
      - term: "Lime Location Permit"
        states: ["AL"]
        patterns:
            - regex: "(?i)\\blime\\s+location\\s+permit\\b"
              confidence: 0.95
      - term: "Facility License"
        states: ["AR"]
        patterns:
            - regex: "(?i)\\bfacility\\s+license\\b"
              confidence: 0.9
      - term: "Fertilizer Distributor Permit"
        states: ["IL"]
        patterns:
              - regex: "(?i)\\bfertilizer\\s+distributor\\s+permit\\b"
                confidence: 0.95
      - term: "Fertilizer Mixing Facility" # Specific to DE
        states: ["DE"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+mixing\\s+facility\\b"
              confidence: 0.95
      - term: "Lime Company License"
        states: ["GA", "IA", "MO"]
        patterns:
            - regex: "(?i)\\blime\\s+company\\s+license\\b"
              confidence: 0.95
      - term: "Fertilizer Manufacturer/Dealers License"
        states: ["IA"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+manufacturer\\s*/\\s*dealers?\\s+license\\b" #Handles /, and plural
              confidence: 0.95
      - term: "Distributor's License"
        states: ["ND"]
        patterns:
              - regex: "(?i)\\bdistributor'?s\\s+license\\b" #Handles possessive
                confidence: 0.95
      - term: "Bulk Specialty Fertilizer License"  # Specific to KY
        states: ["KY"]
        patterns:
            - regex: "(?i)\\bbulk\\s+specialty\\s+fertilizer\\s+license\\b"
              confidence: 0.95
      - term: "Custom Mix Farm Fertilizers Only"  # Specific to KY
        states: ["KY"]
        patterns:
            - regex: "(?i)\\bcustom\\s+mix\\s+farm\\s+fertilizers?\\s+only\\b"
              confidence: 0.95
      - term: "Custom Mix Specialty Fertilizer" # Specific to KY
        states: ["KY"]
        patterns:
            - regex: "(?i)\\bcustom\\s+mix\\s+specialty\\s+fertilizer\\b"
              confidence: 0.95
      - term: "Fertilizer Blender License"
        states: ["KS"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+blender\\s+license\\b"
              confidence: 0.95
      - term: "Lime Production Site License"
        states: ["KS"]
        patterns:
            - regex: "(?i)\\blime\\s+production\\s+site\\s+license\\b"
              confidence: 0.95
      - term: "Permit to Move Regulated Organisms" #added based on FL
        states: ["FL"]
        patterns:
            - regex: "(?i)\\bpermit\\s+to\\s+move\\s+regulated\\s+organisms?\\b"
              confidence: 0.9

  renewal:
    canonical_name: "Registration Renewal"
    state_terms:
      - term: "License Renewal"
        states: []
        patterns:
            - regex: "(?i)\\blicense\\s+renewal\\b"
              confidence: 0.95
      - term: "Annual Renewal"
        states: []
        patterns:
            - regex: "(?i)\\bannual\\s+renewal\\b"
              confidence: 0.95
      - term: "Registration Maintenance"
        states: []
        patterns:
          - regex: "(?i)\\bregistration\\s+maintenance\\b"
            confidence: 0.8 #Slightly lower, as "maintenance" is more general

  tonnage:
    canonical_name: "Tonnage Reporting"
    document_markers:
       required_fields:
         - "reporting period"
         - "tons sold"
         - "company name"
       typical_headers:
         - "(?i)tonnage report"
         - "(?i)inspection fee report"
         - "(?i)sales report"
       typical_sections:
         - "(?i)sales by county"
         - "(?i)total tons"
         - "(?i)fee calculation"
    state_terms:
      - term: "Tonnage Report"
        states:  ["CT", "DE", "FL", "GA", "IA", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "MI", "MN", "MS", "MO", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns:
           - regex: "(?i)\\btonnage\\s+report\\b"
             confidence: 0.95
           - regex: "(?i)\\btons?\\s+sold\\b" # "ton sold" or "tons sold"
             confidence: 0.8
           - regex: "(?i)\\btons?\\b" # "ton sold" or "tons sold"
             confidence: 0.7
      - term: "Inspection Fee" #Many states collect fees based on tonnage
        states: ["AL", "AR","AZ", "CA", "CO", "CT", "DE", "FL", "GA", "IA", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MS", "MO", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns:
            - regex: "(?i)\\binspection\\s+fee\\b"
              confidence: 0.9
      - term: "Mill Fee"
        states: ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "IA", "KS", "KY", "LA", "ME", "MN", "MS", "MT", "NC", "ND", "NE", "NJ", "NM", "NV", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WV", "WY"]
        patterns:
           - regex: "(?i)\\bmill\\s+fee\\b"
             confidence: 0.9
      - term: "Sales Report" #Less specific, lower confidence
        states: []
        patterns:
            - regex: "(?i)\\bsales\\s+report\\b"
              confidence: 0.7
      - term: "Quarterly Report"
        states: []
        patterns:
            - regex: "(?i)\\bquarterly\\s+report\\b"
              confidence: 0.8
      - term: "Semi-Annual Report"
        states: []
        patterns:
            - regex: "(?i)\\bsemi-?annual\\s+report\\b" # Handles hyphen
              confidence: 0.8
      - term: "Monthly Report"
        states:  ["FL"]
        patterns:
            - regex: "(?i)\\bmonthly\\s+report\\b"
              confidence: 0.8
      - term: "Annual Report"
        states: []
        patterns:
            - regex: "(?i)\\bannual\\s+report\\b"
              confidence: 0.8
      - term: "Fertilizer Large Package Fees"  #Specific to CO
        states: ["CO"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+large\\s+package\\s+fees?\\b"
              confidence: 0.95
      - term: "Fertilizer Small Package Fees" #Specific to CO
        states: ["CO"]
        patterns:
            - regex: "(?i)\\bfertilizer\\s+small\\s+package\\s+fees?\\b"
              confidence: 0.95
      - term: "Large & Small Package Inspection Fees" #Specific to CO
        states: ["CO"]
        patterns:
            - regex: "(?i)\\blarge\\s+&\\s+small\\s+package\\s+inspection\\s+fees?\\b" #Handles ampersand
              confidence: 0.95
      - term: "Specialty Distribution fees" #CO, archived
        states: ["CO"]
        patterns:
          - regex: "(?i)\\bspecialty\\s+distribution\\s+fees?\\b"
            confidence: 0.9
      - term: "Quarterly Materials Mill Fees" #CA
        states: ["CA"]
        patterns:
          - regex: "(?i)\\bquarterly\\s+materials?\\s+mill\\s+fees?\\b"
            confidence: 0.95
      - term: "Semi-Ann Com Fert Reports" #CA
        states: ["CA"]
        patterns:
            - regex: "(?i)\\bsemi-?annual\\s+com(?:mercial)?\\s+fert(?:ilizer)?\\s+reports?\\b" #Handles "com" and "fert"
              confidence: 0.9
      - term: "Lime Quarterly Tonnage Report" #AR
        states: ["AR"]
        patterns:
            - regex: "(?i)\\blime\\s+quarterly\\s+tonnage\\s+report\\b"
              confidence: 0.95
      - term: "Lime Reporting" #AL
        states: ["AL"]
        patterns:
            - regex: "(?i)\\blime\\s+reporting\\b"
              confidence: 0.9
      - term: "Lime Semi-Annual Tonnage" #DE
        states: ["DE"]
        patterns:
            - regex: "(?i)\\blime\\s+semi-?annual\\s+tonnage\\b"
              confidence: 0.95
      - term: "Lime Annual Tonnage" #GA
        states: ["GA"]
        patterns:
            - regex: "(?i)\\blime\\s+annual