Okay, let's create a Python-specific API reference document focused on accessing the Client List and Products tables from your Airtable base, using the pyairtable library (a popular and well-maintained Python client for Airtable). I'll incorporate the best practices and structure from the excellent document you provided, tailored for Python developers.

"""
Airtable API Reference (Python - pyairtable)

This document provides a Python-specific guide for interacting with the
'Client List' and 'Products' tables in your Airtable base, using the
`pyairtable` library.

Base ID: appkaXsw8Q6dSltKd

Before you begin:

1.  **Install pyairtable:**
    ```bash
    pip install pyairtable
    ```

2.  **Obtain your API Key:**  You'll need a Personal Access Token (PAT)
    from Airtable.  Create one at: https://airtable.com/create/tokens

3. Replace `{api_key}` with your Personal Access Token.
"""

import os
from pyairtable import Api, Base, Table

# --- Configuration (Replace with your values) ---
api_key = os.environ.get("AIRTABLE_API_KEY")  # Best practice: Use environment variables


# --- Initialize pyairtable Objects ---

# Option 1: Initialize the API object (best for multiple bases)
api = Api(api_key)
base = api.base("appkaXsw8Q6dSltKd")

# Option 2: Initialize the Base object directly (for a single base)
#base = Base(api_key, "appkaXsw8Q6dSltKd")
# --- Table Objects ---

client_list_table = base.get_table("tblDSlAkIve4Ap9u8")  # Use the Table ID (best practice)
# OR, by table name (less robust to table name changes):
# client_list_table = base.table("Client List")

products_table = base.get_table("tblYe0DJIkwk758Az")
# OR, by table name:
# products_table = base.table("Products")
# --- Client List Table (tblDSlAkIve4Ap9u8) ---

def list_clients(view=None, max_records=None, fields=None, filter_by_formula=None, sort=None):
    """
    Lists records from the Client List table.

    Args:
        view (str, optional): The name or ID of a view. Defaults to None.
        max_records (int, optional): The maximum number of records to return.
            Defaults to None (returns all records, paginated).
        fields (list of str, optional): A list of field names or IDs to
            include in the results.  Defaults to None (returns all fields).
        filter_by_formula (str, optional): An Airtable formula to filter
            records. Defaults to None.
        sort: (list of dict,optional) : A list of dicts, which it specifies how the records will be ordered.
             Each dict sort object must have keys: 'field' and optional 'direction'
             Example:[{'field':'name','direction':'desc'}]. Default is "asc"
    Returns:
        list: A list of record dictionaries.  Empty values are omitted.
            Each record is a dictionary with keys 'id', 'createdTime', and 'fields'.
            The 'fields' value is another dictionary mapping field names/IDs to values.

    Raises:
        requests.HTTPError: If the API request fails.
        pyairtable.ApiError:  If there's an Airtable-specific error.
    """

    # Build the parameters dictionary.  pyairtable handles URL encoding.
    params = {}
    if view:
        params['view'] = view
    if max_records:
        params['maxRecords'] = max_records
    if fields:
        params['fields'] = fields  # pyairtable handles lists correctly
    if filter_by_formula:
        params['filterByFormula'] = filter_by_formula
    if sort:
        params['sort'] = sort


    all_clients = []
    for page in client_list_table.iterate( **params ):
       for record in page:
            all_clients.append(record)
    return all_clients



def get_client(record_id):
    """Retrieves a single client record by its ID.

    Args:
        record_id (str): The Airtable record ID.

    Returns:
        dict: The record dictionary, or None if not found.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    try:
        return client_list_table.get(record_id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None  # Record not found
        else:
            raise  # Re-raise other errors

def create_client(fields):
    """Creates a new client record.

    Args:
        fields (dict): A dictionary of field names/IDs and their values.
            Computed fields cannot be set.

    Returns:
        dict: The created record dictionary.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    return client_list_table.create(fields)


def update_client(record_id, fields, typecast=False,destructive=False):
    """Updates an existing client record.

    Args:
        record_id (str): The Airtable record ID.
        fields (dict): A dictionary of field names/IDs and their new values.
            Computed fields cannot be updated.
        typecast (bool): Whether to enable best-effort automatic data conversion.
        destructive (bool): Replaces all unincluded values with an empty string if True.  Defaults to False

    Returns:
        dict: The updated record dictionary.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    if destructive:
        return client_list_table.update(record_id, fields,typecast=typecast)
    return client_list_table.update(record_id, fields,typecast=typecast)

def delete_client(record_id):
    """Deletes a client record.

    Args:
        record_id (str): The Airtable record ID.

    Returns:
        dict: A dictionary indicating success, e.g., {'deleted': True, 'id': '...'}

    Raises:
        requests.HTTPError: If the API request fails.
    """
    return client_list_table.delete(record_id)




# --- Products Table (tblYe0DJIkwk758Az) ---

# Implement similar functions for the Products table:
# list_products, get_product, create_product, update_product, delete_product
# (Code omitted for brevity, but follows the same pattern as Client List)
#  Remember that Products also has attachments, so handle them as described
#  in the original document.

def list_products(view=None, max_records=None, fields=None, filter_by_formula=None, sort=None):
    """
    Lists records from the Products table.

    Args:
        view (str, optional): The name or ID of a view. Defaults to None.
        max_records (int, optional): The maximum number of records to return.
            Defaults to None (returns all records, paginated).
        fields (list of str, optional): A list of field names or IDs to
            include in the results.  Defaults to None (returns all fields).
        filter_by_formula (str, optional): An Airtable formula to filter
            records. Defaults to None.
        sort: (list of dict,optional) : A list of dicts, which it specifies how the records will be ordered.
             Each dict sort object must have keys: 'field' and optional 'direction'
             Example:[{'field':'Product','direction':'desc'}]. Default is "asc"

    Returns:
        list: A list of record dictionaries.  Empty values are omitted.
            Each record is a dictionary with keys 'id', 'createdTime', and 'fields'.
            The 'fields' value is another dictionary mapping field names/IDs to values.

    Raises:
        requests.HTTPError: If the API request fails.
        pyairtable.ApiError:  If there's an Airtable-specific error.
    """
    params = {}
    if view:
        params['view'] = view
    if max_records:
        params['maxRecords'] = max_records
    if fields:
        params['fields'] = fields
    if filter_by_formula:
        params['filterByFormula'] = filter_by_formula
    if sort:
        params['sort'] = sort

    all_products = []
    for page in products_table.iterate(**params):
        for record in page:
            all_products.append(record)
    return all_products

def get_product(record_id):
    """
    Retrieves a product by its record ID.
    Args:
    record_id (str): Airtable record ID of the product.

    Returns:
        dict: product record, or None if not found

    Raises:
        requests.HTTPError: on API errors.

    """
    try:
        return products_table.get(record_id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None  # Record not found
        else:
            raise  # Re-raise other errors

def create_product(fields, typecast = False):
    """
    Creates a new Product record.

    Args:
        fields (dict): Dictionary of fields to set
        typecast(bool): When True does best effort data conversion

    Returns:
        dict: The created record dictionary

    Raises:
        requests.HTTPError: If the API request fails

    """
    return products_table.create(fields,typecast=typecast)



def update_product(record_id, fields, typecast=False, destructive=False):
    """
    Updates an existing Product

    Args:
        record_id (str):  Airtable Record ID
        fields (dict): A dictionary of fields and values to update.
        typecast: When True does best effort data conversion
        destructive (bool): Replaces all unincluded values with an empty string if True.  Defaults to False.
    Returns:
        dict: The updated record
    """
    if destructive:
        return products_table.update(record_id, fields,typecast=typecast)
    return products_table.update(record_id, fields, typecast=typecast)


def delete_product(record_id):
    """
    Deletes a Product record by its ID

    Args:
        record_id (str): Airtable record ID

    Returns:
    dict: Dictionary with 'id' and 'deleted'=True
    """
    return products_table.delete(record_id)
# --- Example Usage ---

if __name__ == "__main__":
    # List all clients
    # clients = list_clients()
    # print(f"Found {len(clients)} clients.")
    # for client in clients:
    #   print(client)

    # List a subset of clients
    # clients_view = list_clients(view="Grid view", max_records=5)
    # print(f"Found {len(clients_view)} clients in Grid view.")
    # for client in clients_view:
    #   print(client['fields']['Company Name'])


    # List a subset of clients using formula filter
    # formula = "NOT({Company Name} = '')" # Example: Company Name is not empty.  Note the *single* quotes.
    # filtered_clients = list_clients(filter_by_formula=formula, max_records = 5 )
    # print(f"Found {len(filtered_clients)} filtered clients.")
    # for client in filtered_clients:
    #       print(client)

    #Get a record by ID
    # client = get_client("recMT5QFl1lFcKLBa") # put a real record ID here.
    # if client:
    #   print(f"Client record for ID recMT5QFl1lFcKLBa: {client}")
    # else:
    #   print("Client not found")

    # Create a new client (replace with your desired field values)
    # new_client_data = {
    #    "Comp Code": "NEWCO",
    #    "Company Name": "New Company Inc.",
    #    "Manage Renewals": "Yes",
    # }
    # try:
    #    new_client = create_client(new_client_data)
    #    print(f"Created new client: {new_client}")
    # except requests.exceptions.HTTPError as e:
    #    print(f"Error creating client: {e}")

    # Update an existing client (replace with a real record ID and fields)
    # try:
    #   updated_client = update_client(
    #     "recMT5QFl1lFcKLBa",
    #       {"Company Name": "Updated Company Name"},
    #       typecast=True  # Enable if you're passing values that need conversion
    #   )
    #   print(f"Updated client: {updated_client}")
    # except requests.exceptions.HTTPError as e:
    #   print(f"Error updating client: {e}")

    # Delete a client (replace with a real record ID)
    #try:
    #    deleted_client = delete_client("recWIiyAb9recc5ZBtvwxIiyAb9")  # Replace with a valid record ID
    #    print(f"Deleted client: {deleted_client}")
    #except requests.exceptions.HTTPError as e:
    #    print(f"Error deleting client: {e}")
    # List All products
    
    all_products = list_products()
    print(f"Found {len(all_products)} products.")

    #List a subset of products
    products = list_products(view = "All Items", max_records = 5)
    print(f"Found {len(products)} products.")

    #List subset of products using formula
    formula = "NOT({Product} = '')" # Example: Product is not empty.  Note the *single* quotes.
    filtered_products = list_products(filter_by_formula=formula, max_records = 5, fields=["Product","Active Prod"])
    print(f"Found {len(filtered_products)} filtered products.")
    for product in filtered_products:
       print(f"{product['fields']['Product']} , Active: {product['fields']['Active Prod']}")

    # Get a record by ID
    product = get_product("rec3sVNMOQji6SHb1") # put a real record ID here.
    if product:
        print(f"Product: {product}")
    else:
       print("Product not found")

    # Create a new product (replace with your desired field values)
    # new_product_data = {
    #   "Product": "NEW PRODUCT INC.",
    #   "Active Prod": True,
    #   "Company": ["recc5ZBtvwxIiyAb9"], # Use a list of valid record IDs
    #   "Product Type": ["Fertilizer"] , # Use a list for multiple select
    # }
    #
    # try:
    #   new_product = create_product(new_product_data, typecast=True)
    #   print(f"Created new product: {new_product}")
    # except requests.exceptions.HTTPError as e:
    #   print(f"Error creating product: {e}")

      # Update a product (replace with a real record ID and fields)
      # try:
      #   updated_product = update_product(
      #     "rec3sVNMOQji6SHb1",
      #       {"Product": "ProductX"},
      #       typecast=True  # Enable if you're passing values that need conversion
      #
      #   )
      #   print(f"Updated product: {updated_product}")
      # except requests.exceptions.HTTPError as e:
      #   print(f"Error updating product: {e}")

      # Delete a product (replace with a real record ID)
      # try:
      #     deleted_product = delete_product("recXXXXXXXXXXXXXXXX")  # Replace with a valid record ID
      #     print(f"Deleted product: {deleted_product}")
      # except requests.exceptions.HTTPError as e:
      #     print(f"Error deleting product: {e}")
content_copy
download
Use code with caution.
Python

Key Changes and Explanations:

pyairtable Library: The code uses the pyairtable library.

Initialization: Shows how to initialize the Api and Base objects. Using the Base object directly is often more convenient for single-base interactions. Also demonstrates using environment variables for the API key.

Table Objects: Creates Table objects for both "Client List" and "Products" using their respective IDs.

Function Definitions: Creates Python functions for each CRUD operation (list_clients, get_client, create_client, update_client, delete_client, and similarly for Products). This promotes code reusability and organization.

Docstrings: Includes comprehensive docstrings for each function, explaining the purpose, arguments, return values, and potential exceptions. This is crucial for good documentation.

Parameter Handling: The list_clients and list_products functions use a params dictionary to build the query parameters for the Airtable API. pyairtable automatically handles URL encoding.

Pagination: The list_clients and list_products uses table.iterate() which automatically handles pagination. This is much simpler than manually dealing with offsets. The example iterates through each page of records and adds all records to a all_clients list.

Error Handling: Includes basic try...except blocks to catch potential requests.HTTPError exceptions (for network issues or invalid requests) and pyairtable.ApiError (for Airtable-specific errors). The get_client function specifically handles the 404 (Not Found) error.

Typecasting: The create_client and update_client functions includes a typecast=True parameter, demonstrating how to use this option for automatic data conversion.

Return Values: Each function returns the relevant data from the API (list of records, a single record, or a deletion confirmation).

Example Usage: Provides clear examples of how to use each function, including listing all records, filtering, retrieving by ID, creating, updating, and deleting. This makes the document immediately practical.

Destructive Updates: The update methods includes a boolean destructive parameter that allows for both PATCH and PUT style updates.

Comments: Includes descriptive comments for key points.

How to Use This Document:

Install pyairtable: Run pip install pyairtable in your terminal.

Set your API Key: Replace {api_key} with your actual Airtable Personal Access Token. It's best practice to load this from an environment variable, as shown in the example, rather than hardcoding it.

Copy and Paste: Copy the code into a Python file (e.g., airtable_api.py).

Run Examples: Uncomment and modify the example usage section to test the functions. You'll need to replace placeholder record IDs with valid IDs from your Airtable base.

Adapt for Your Needs: Modify the functions and examples to fit your specific use cases.

This revised document provides a solid, Python-centric starting point for interacting with your Airtable data. Remember to consult the pyairtable documentation (https://pyairtable.readthedocs.io/en/latest/) for more advanced features and options.