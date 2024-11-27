import os
import json

import psycopg2
from pdf2image import convert_from_path
import google.generativeai as genai
from Log_Cred import local_login, system_prompt, user_prompt

# Configure Google Gemini API
genai.configure(api_key="AIzaSyC0-mdLaPgzxEmxQVK71SH4MxXjIAB6SqM")

MODEL_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "max_output_tokens": 2048,
    "presence_penalty": 0.3,
    "frequency_penalty": 0.3
}


# Gemini model configuration
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=MODEL_CONFIG,
                              safety_settings=[
                                  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                   "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                              ])

DB_CONFIG = {
    "host": "157.20.51.93",          # Change this to your database host
    "database": "adm_db",  # Replace with your database name
    "user": "postgres",          # Replace with your username
    "password": "Vikas$7!5&v^ate@",  # Replace with your password
    "port": 9871                  # Default PostgreSQL port
}


def insert_json_to_db(json_data):
    """
    Insert JSON data into the database using a stored procedure.
    :param json_data: JSON data to pass to the stored procedure.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Convert JSON to string for insertion
        json_str = json.dumps(json_data)

        # Call the stored procedure
        cursor.execute("SELECT * FROM f_insert_bank_application_data(%s);", (json_str,))

        # Commit the transaction
        conn.commit()

        # Fetch and print the result (optional)
        result = cursor.fetchall()
        print("Stored Procedure Result:", result)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# PDF to Image Conversion
def pdf_to_image(pdf_path, output_folder="uploads"):
    """Convert PDF pages to images and save them."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path, poppler_path='C:\\Program Files (x86)\\poppler-24.08.0\\Library\\bin')
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"temp_image_{i}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths


# Prepare image data for Gemini input
def image_format(image_path):
    """Prepare image data for API input."""
    with open(image_path, "rb") as img_file:
        return [{
            "mime_type": "image/png",
            "data": img_file.read()
        }]


# Gemini output generation
def gemini_output(image_path, system_prompt, user_prompt):
    """Generate JSON output from Gemini using an image and prompts."""
    try:
        image_info = image_format(image_path)
        input_prompt = [system_prompt, image_info[0], user_prompt]
        response = model.generate_content(input_prompt)
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[8:-3].strip()
        return raw_output
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return ""


def process_files(file_paths, system_prompt, user_prompt):
    """Extract data from provided files (PDF or images) and consolidate into a single JSON."""
    consolidated_data = {}  # Use a dictionary to create a single JSON structure

    for idx, file_path in enumerate(file_paths, start=1):
        page_name = f"Page {idx}"  # Generate standardized page names
        print(f"Processing file: {file_path} as {page_name}...")

        if file_path.lower().endswith('.pdf'):
            # If it's a PDF, convert to images first
            image_paths = pdf_to_image(file_path)
            pdf_data = []  # Temporary list to hold data for this PDF
            for page_number, image_path in enumerate(image_paths, start=1):
                print(f"Processing PDF page {page_number}...")
                output_json = gemini_output(image_path, system_prompt, user_prompt)
                try:
                    page_data = json.loads(output_json)
                    pdf_data.append(page_data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for page {page_number}: {e}")
                    pdf_data.append({"error": "Failed to extract data"})
            consolidated_data[page_name] = pdf_data  # Store all PDF page data under its page name

        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # If it's an image, process it directly
            output_json = gemini_output(file_path, system_prompt, user_prompt)
            try:
                image_data = json.loads(output_json)
                consolidated_data[page_name] = image_data  # Use page name as key for image data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for image {file_path}: {e}")
                consolidated_data[page_name] = {"error": "Failed to extract data"}

        else:
            print(f"Unsupported file format: {file_path}. Skipping...")

    return consolidated_data




# Example usage:
if __name__ == "__main__":
    # if not local_login():
    #     print("Login failed, cannot proceed.")
    #     exit(1)

    # Prompt the user for file paths
    print("Please enter the paths of the files you want to process (separated by commas):")
    input_files = input().split(",")  # Get input from the user and split by commas
    input_files = [file.strip() for file in input_files]  # Clean up any extra spaces around the file paths

    # Process the files
    consolidated_results = process_files(input_files, system_prompt, user_prompt)

    # Save or display consolidated JSON
    output_file = "extracted_data.json"
    with open(output_file, "w") as f:
        json.dump(consolidated_results, f, indent=4)

    print(f"Data extracted and saved to {output_file}.")
    insert_json_to_db(consolidated_results)
    print("Data saved in Data Base")