def local_login():
    """Simulate local login with username and password."""
    # Define valid credentials (username and password)
    valid_username = "admin"
    valid_password = "123"

    print("Please login to continue.")
    username = input("Username: ")
    password = input("Password: ")

    if username == valid_username and password == valid_password:
        print("Login successful!")
        return True
    else:
        print("Invalid credentials. Please try again.")
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------


system_prompt = """
        You are a specialist in extracting structured data from bank account opening forms and loan account forms.
        These forms may include both printed and handwritten data. Your task is to accurately interpret all the content in the form, regardless of format or handwriting style.
        Handle handwritten text carefully, considering variations in handwriting.
        """


user_prompt = """
    You are an intelligent assistant specialized in extracting structured data from bank account opening forms and loan account forms.
    Given the text extracted from these forms, please extract **all identifiable fields** in JSON format. 

    For each field, include the following:
    - The field's label or description as it appears on the form.
    - The corresponding value, as provided (whether printed or handwritten).
    - Notes if any data is illegible or ambiguous.

    Provide the extracted data in a structured and human-readable JSON format, preserving the hierarchy and relationships between fields if applicable.
    If any field cannot be clearly identified, include it with a value of "null" and an appropriate note.  
    and JSON should be in key value pair (key means parameter and value means the content of the parameter)  
    
    """

# ------------------------------------------------------------------------------------------------------------------------------------------

API_KEY = "AIzaSyCP6JZiT1SCjT7d0R1WHwS6mt7BO3btvcs"

# ------------------------------------------------------------------------------------------------------------------------------------------

system_prompt_1 = """You are a specialist in extracting structured data from bank account opening forms and loan account forms. These forms may include both printed and handwritten data. Your task is to accurately interpret all the content in the form, regardless of format or handwriting style.

You will generate a structured tabular representation of all the data, with each row representing a field or a data point extracted from the form. Each column should represent a specific aspect or category of the form, such as "Field Label," "Field Value," and "Notes." Ensure all data is organized clearly for further processing, suitable for Excel export.

Handle handwritten text carefully, considering variations in handwriting, and include the corresponding notes where needed.
"""


user_prompt_1 = """You are an intelligent assistant specialized in extracting structured data from bank account opening forms and loan account forms. Given the text extracted from these forms, please extract **all identifiable fields** and organize them in a table format for Excel generation.

For each field, please provide the following columns:
1. **Field Label**: The label or description of the field as it appears on the form.
2. **Field Value**: The corresponding value, whether it is printed or handwritten.
3. **Notes**: Any notes or explanations if the data is illegible, ambiguous, or missing.

Each row should represent one field. If any field cannot be clearly identified, include it with "null" in the "Field Value" column and provide an appropriate note in the "Notes" column.

Ensure the table is well-structured, with columns clearly labeled and ready for Excel export. If any field is missing or unclear, indicate it appropriately with "null" or a relevant note.
"""