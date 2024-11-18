import os
import json
from pdf2image import convert_from_path
import google.generativeai as genai
from Log_Cred import local_login

# Configure Google Gemini API
genai.configure(api_key="AIzaSyCP6JZiT1SCjT7d0R1WHwS6mt7BO3btvcs")

MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
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


# Main function to process all pages and consolidate results
def process_pdf(pdf_path, system_prompt, user_prompt):
    """Extract data from all pages of a PDF and consolidate into a single JSON."""
    image_paths = pdf_to_image(pdf_path)
    consolidated_data = {}

    for page_number, image_path in enumerate(image_paths):
        print(f"Processing page {page_number + 1}...")
        output_json = gemini_output(image_path, system_prompt, user_prompt)
        try:
            page_data = json.loads(output_json)
            consolidated_data[f"page_{page_number + 1}"] = page_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for page {page_number + 1}: {e}")
            consolidated_data[f"page_{page_number + 1}"] = {"error": "Failed to extract data"}

    return consolidated_data


# Example usage:
if __name__ == "__main__":
    if not local_login():
        print("Login failed, cannot proceed.")
        exit(1)
    pdf_path = "Bank Use Case\\sbi CA opening form.pdf"  # Replace with actual PDF path
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
    """

    consolidated_results = process_pdf(pdf_path, system_prompt, user_prompt)

    # Save or display consolidated JSON
    output_file = "extracted_data.json"
    with open(output_file, "w") as f:
        json.dump(consolidated_results, f, indent=4)

    print(f"Data extracted and saved to {output_file}.")
