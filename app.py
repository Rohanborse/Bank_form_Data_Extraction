import os
import json
from pdf2image import convert_from_path
import google.generativeai as genai
from Log_Cred import local_login, system_prompt, user_prompt, API_KEY
from PIL import Image

# Configure Google Gemini API
genai.configure(api_key=API_KEY)

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
# Prepare image data for Gemini input
def image_format(image_path):
    """Prepare image data for API input."""
    try:
        with open(image_path, "rb") as img_file:
            return [{
                "mime_type": "image/png",  # Ensure the correct MIME type is used
                "data": img_file.read()
            }]
    except FileNotFoundError:
        print(f"Error: File not found - {image_path}")
        return []
    except Exception as e:
        print(f"Error preparing image data: {e}")
        return []


# Gemini output generation
def gemini_output(image_path, system_prompt, user_prompt):
    """Generate JSON output from Gemini using an image and prompts."""
    try:
        image_info = image_format(image_path)
        if not image_info:
            return {"error": f"Failed to process image: {image_path}"}

        input_prompt = [system_prompt, image_info[0], user_prompt]
        response = model.generate_content(input_prompt)
        raw_output = response.text.strip()

        # Remove potential markdown formatting
        if raw_output.startswith("```json"):
            raw_output = raw_output[8:-3].strip()

        return raw_output
    except Exception as e:
        print(f"Error during Gemini API call for {image_path}: {e}")
        return {"error": f"API call failed for {image_path}"}
# Process a single image file
def process_file(file_path, system_prompt, user_prompt, image_files=None):
    """Process a file (PDF or multiple images) and return extracted data."""
    # Check if a PDF is provided
    if file_path and file_path.lower().endswith(".pdf"):
        print("Detected file type: PDF")
        return process_pdf(file_path, system_prompt, user_prompt)

    # Check if image files are provided
    elif image_files:
        print(f"Detected file type: Images (multiple images to be processed)")
        consolidated_data = {}
        for index, image_path in enumerate(image_files):
            print(f"Processing image {index + 1}: {image_path}")
            output_json = gemini_output(image_path, system_prompt, user_prompt)
            try:
                page_data = json.loads(output_json)
                consolidated_data[f"image_{index + 1}"] = page_data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for image {image_path}: {e}")
                consolidated_data[f"image_{index + 1}"] = {"error": "Failed to extract data"}

        return consolidated_data

    # Handle unsupported or missing inputs
    else:
        print("Error: No valid file or images provided.")
        return {"error": "No valid file or images provided."}


# Process a PDF file
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


# Main function to process a PDF or multiple images
def process_file(file_path, system_prompt, user_prompt, image_files=None):
    """Process a file (PDF or multiple images) and return extracted data."""
    # Check if a PDF is provided
    if file_path and file_path.lower().endswith(".pdf"):
        print("Detected file type: PDF")
        return process_pdf(file_path, system_prompt, user_prompt)

    # Check if image files are provided
    elif image_files:
        print(f"Detected file type: Images (multiple images to be processed)")
        consolidated_data = {}
        for index, image_path in enumerate(image_files):
            print(f"Processing image {index + 1}: {image_path}")
            output_json = gemini_output(image_path, system_prompt, user_prompt)
            try:
                page_data = json.loads(output_json)
                consolidated_data[f"image_{index + 1}"] = page_data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for image {image_path}: {e}")
                consolidated_data[f"image_{index + 1}"] = {"error": "Failed to extract data"}

        return consolidated_data

    # Handle unsupported or missing inputs
    else:
        print("Error: No valid file or images provided.")
        return {"error": "No valid file or images provided."}



def upload_multiple_images(system_prompt, user_prompt):
    """Collect multiple images from the user and process them."""
    image_files = []
    while True:
        image_path = input("Enter the path of an image (or 'done' to finish): ").strip()
        if image_path.lower() == "done":
            break
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue
        image_files.append(image_path)

    if not image_files:
        print("No images provided. Exiting.")
        return {"error": "No images provided"}

    print(f"Processing {len(image_files)} images...")
    return process_file(None, system_prompt, user_prompt, image_files=image_files)


# Example usage:
if __name__ == "__main__":
    # if not local_login():
    #     print("Login failed, cannot proceed.")
    #     exit(1)

    file_option = input("Do you want to process a PDF or multiple images? (Enter 'pdf' or 'images'): ").strip().lower()

    if file_option == "pdf":
        pdf_path = input("Enter the path to the file: ")
        consolidated_results = process_file(pdf_path, system_prompt, user_prompt)
    elif file_option == "images":
        consolidated_results = upload_multiple_images(system_prompt, user_prompt)
    else:
        print("Invalid option.")
        exit(1)

    # Save or display consolidated JSON
    output_file = "extracted_data.json"
    with open(output_file, "w") as f:
        json.dump(consolidated_results, f, indent=4)

    print(f"Data extracted and saved to {output_file}.")



#
# import os
# import json
# from pdf2image import convert_from_path
# import google.generativeai as genai
# from Log_Cred import local_login, system_prompt, user_prompt, API_KEY
# from PIL import Image
# import pandas as pd
#
# # Configure Google Gemini API
# genai.configure(api_key=API_KEY)
#
# MODEL_CONFIG = {
#     "temperature": 0.2,
#     "top_p": 1,
#     "top_k": 32,
#     "max_output_tokens": 4096,
# }
#
# # Gemini model configuration
# model = genai.GenerativeModel(model_name="gemini-1.5-flash",
#                               generation_config=MODEL_CONFIG,
#                               safety_settings=[
#                                   {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#                                   {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#                                   {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#                                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#                                   {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
#                               ])
#
#
# # PDF to Image Conversion
# def pdf_to_image(pdf_path, output_folder="uploads"):
#     """Convert PDF pages to images and save them."""
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#
#     images = convert_from_path(pdf_path, poppler_path='C:\\Program Files (x86)\\poppler-24.08.0\\Library\\bin')
#     image_paths = []
#     for i, image in enumerate(images):
#         image_path = os.path.join(output_folder, f"temp_image_{i}.png")
#         image.save(image_path, "PNG")
#         image_paths.append(image_path)
#     return image_paths
#
#
# # Prepare image data for Gemini input
# def image_format(image_path):
#     """Prepare image data for API input."""
#     try:
#         with open(image_path, "rb") as img_file:
#             return [{
#                 "mime_type": "image/png",
#                 "data": img_file.read()
#             }]
#     except FileNotFoundError:
#         print(f"Error: File not found - {image_path}")
#         return []
#     except Exception as e:
#         print(f"Error preparing image data: {e}")
#         return []
#
#
# # Gemini output generation
# def gemini_output(image_path, system_prompt, user_prompt):
#     """Generate JSON output from Gemini using an image and prompts."""
#     try:
#         image_info = image_format(image_path)
#         if not image_info:
#             return {"error": f"Failed to process image: {image_path}"}
#
#         input_prompt = [system_prompt, image_info[0], user_prompt]
#         response = model.generate_content(input_prompt)
#         raw_output = response.text.strip()
#
#         # Remove potential markdown formatting
#         if raw_output.startswith("```json"):
#             raw_output = raw_output[8:-3].strip()
#
#         return raw_output
#     except Exception as e:
#         print(f"Error during Gemini API call for {image_path}: {e}")
#         return {"error": f"API call failed for {image_path}"}
#
#
# # Process a PDF file
# def process_pdf(pdf_path, system_prompt, user_prompt):
#     """Extract data from all pages of a PDF and consolidate into a single JSON."""
#     image_paths = pdf_to_image(pdf_path)
#     consolidated_data = {}
#
#     for page_number, image_path in enumerate(image_paths):
#         print(f"Processing page {page_number + 1}...")
#         output_json = gemini_output(image_path, system_prompt, user_prompt)
#         try:
#             page_data = json.loads(output_json)
#             consolidated_data[f"page_{page_number + 1}"] = page_data
#         except json.JSONDecodeError as e:
#             print(f"Error parsing JSON for page {page_number + 1}: {e}")
#             consolidated_data[f"page_{page_number + 1}"] = {"error": "Failed to extract data"}
#
#     return consolidated_data
#
#
# # Save data to Excel
# def save_to_excel(data, output_file):
#     """
#     Save JSON-like data to an Excel file in a structured format.
#     """
#     try:
#         with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
#             # Flatten JSON structure and save each key (page/image) to a new sheet
#             for key, value in data.items():
#                 if isinstance(value, dict):
#                     # Convert nested dictionary to DataFrame
#                     df = pd.json_normalize(value)
#                     df.to_excel(writer, sheet_name=key, index=False)
#                 else:
#                     # If data isn't a dictionary, save as a generic DataFrame
#                     df = pd.DataFrame([value])
#                     df.to_excel(writer, sheet_name=key, index=False)
#         print(f"Data saved to Excel file: {output_file}")
#     except Exception as e:
#         print(f"Error saving data to Excel: {e}")
#
#
# # Upload and process multiple images
# def upload_multiple_images(system_prompt, user_prompt):
#     """Collect multiple images from the user and process them."""
#     image_files = []
#     while True:
#         image_path = input("Enter the path of an image (or 'done' to finish): ").strip()
#         if image_path.lower() == "done":
#             break
#         if not os.path.exists(image_path):
#             print(f"File not found: {image_path}")
#             continue
#         image_files.append(image_path)
#
#     if not image_files:
#         print("No images provided. Exiting.")
#         return {"error": "No images provided"}
#
#     print(f"Processing {len(image_files)} images...")
#     return process_file(None, system_prompt, user_prompt, image_files=image_files)
#
#
# # Main function to process a PDF or multiple images
# def process_file(file_path, system_prompt, user_prompt, image_files=None):
#     """Process a file (PDF or multiple images) and return extracted data."""
#     # Check if a PDF is provided
#     if file_path and file_path.lower().endswith(".pdf"):
#         print("Detected file type: PDF")
#         return process_pdf(file_path, system_prompt, user_prompt)
#
#     # Check if image files are provided
#     elif image_files:
#         print(f"Detected file type: Images (multiple images to be processed)")
#         consolidated_data = {}
#         for index, image_path in enumerate(image_files):
#             print(f"Processing image {index + 1}: {image_path}")
#             output_json = gemini_output(image_path, system_prompt, user_prompt)
#             try:
#                 page_data = json.loads(output_json)
#                 consolidated_data[f"image_{index + 1}"] = page_data
#             except json.JSONDecodeError as e:
#                 print(f"Error parsing JSON for image {image_path}: {e}")
#                 consolidated_data[f"image_{index + 1}"] = {"error": "Failed to extract data"}
#
#         return consolidated_data
#
#     # Handle unsupported or missing inputs
#     else:
#         print("Error: No valid file or images provided.")
#         return {"error": "No valid file or images provided."}
#
#
# if __name__ == "__main__":
#     file_option = input("Do you want to process a PDF or multiple images? (Enter 'pdf' or 'images'): ").strip().lower()
#
#     if file_option == "pdf":
#         pdf_path = input("Enter the path to the file: ")
#         consolidated_results = process_file(pdf_path, system_prompt, user_prompt)
#     elif file_option == "images":
#         consolidated_results = upload_multiple_images(system_prompt, user_prompt)
#     else:
#         print("Invalid option.")
#         exit(1)
#
#     # Save consolidated results
#     json_output_file = "extracted_data.json"
#     excel_output_file = "extracted_data.xlsx"
#
#     with open(json_output_file, "w") as f:
#         json.dump(consolidated_results, f, indent=4)
#     print(f"Data extracted and saved to JSON file: {json_output_file}")
#
#     save_to_excel(consolidated_results, excel_output_file)
