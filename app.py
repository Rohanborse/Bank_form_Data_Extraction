import os
import json
from pdf2image import convert_from_path
import google.generativeai as genai
from Log_Cred import local_login, system_prompt, user_prompt

# Configure Google Gemini API
genai.configure(api_key="AIzaSyCP6JZiT1SCjT7d0R1WHwS6mt7BO3btvcs")

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


# Main function to process all files (PDF and images) and consolidate results
def process_files(file_paths, system_prompt, user_prompt):
    """Extract data from provided files (PDF or images) and consolidate into a single JSON."""
    consolidated_data = {}  # Use a dictionary to create a single JSON structure

    for file_path in file_paths:
        print(f"Processing file: {file_path}...")

        if file_path.lower().endswith('.pdf'):
            # If it's a PDF, convert to images first
            image_paths = pdf_to_image(file_path)
            pdf_data = []  # Temporary list to hold data for this PDF
            for page_number, image_path in enumerate(image_paths):
                print(f"Processing PDF page {page_number + 1}...")
                output_json = gemini_output(image_path, system_prompt, user_prompt)
                try:
                    page_data = json.loads(output_json)
                    pdf_data.append(page_data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for page {page_number + 1}: {e}")
                    pdf_data.append({"error": "Failed to extract data"})
            consolidated_data[file_path] = pdf_data  # Store all PDF page data under its filename

        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # If it's an image, process it directly
            output_json = gemini_output(file_path, system_prompt, user_prompt)
            try:
                image_data = json.loads(output_json)
                consolidated_data[file_path] = image_data  # Use filename as key for image data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for image {file_path}: {e}")
                consolidated_data[file_path] = {"error": "Failed to extract data"}

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
