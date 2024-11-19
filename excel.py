import os
import json
import pandas as pd

from Log_Cred import  system_prompt_1, user_prompt_1


# Placeholder for your AI model's API interaction
class DummyModel:
    @staticmethod
    def generate_content(prompts):
        """Simulated API response (replace with your actual API call)."""
        return type('Response', (object,), {"text": '{"field1": "value1", "field2": "value2"}'})


# Initialize dummy model
model = DummyModel()


# Helper Functions
def image_format(image_path):
    """Validate image format and return info (dummy implementation)."""
    if os.path.exists(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        return [f"Image file: {image_path}"]
    print(f"Invalid image format or file not found: {image_path}")
    return None


def save_to_excel(data, output_file="extracted_data.xlsx"):
    """Save consolidated data to an Excel file."""
    try:
        records = []
        for key, value in data.items():
            if isinstance(value, dict):
                flat_record = {"Source": key}
                flat_record.update(value)
                records.append(flat_record)
            else:
                records.append({"Source": key, "Data": value})

        # Create DataFrame and save as Excel
        df = pd.DataFrame(records)
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def gemini_output(image_path, system_prompt, user_prompt):
    """Generate structured data from Gemini using an image and prompts."""
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

        # Parse raw output into structured data
        try:
            structured_data = json.loads(raw_output)
            return structured_data
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON format in response for {image_path}"}
    except Exception as e:
        print(f"Error during Gemini API call for {image_path}: {e}")
        return {"error": f"API call failed for {image_path}"}


def process_file(file_path=None, system_prompt=None, user_prompt=None, image_files=None):
    """Process a file (PDF or multiple images) and return extracted data."""
    if file_path and file_path.lower().endswith(".pdf"):
        print("Detected file type: PDF")
        # You need to implement `process_pdf` function to handle PDF parsing
        extracted_data = process_pdf(file_path, system_prompt, user_prompt)
    elif image_files:
        print(f"Detected file type: Images (multiple images to be processed)")
        extracted_data = {}
        for index, image_path in enumerate(image_files):
            print(f"Processing image {index + 1}: {image_path}")
            output_data = gemini_output(image_path, system_prompt, user_prompt)
            extracted_data[f"image_{index + 1}"] = output_data
    else:
        print("Error: No valid file or images provided.")
        return {"error": "No valid file or images provided."}

    # Save data to Excel
    save_to_excel(extracted_data)
    return extracted_data


def upload_multiple_images(system_prompt, user_prompt):
    """Simulate multiple image upload for processing."""
    num_images = int(input("Enter the number of images to process: "))
    image_files = []
    for i in range(num_images):
        image_path = input(f"Enter the path for image {i + 1}: ")
        image_files.append(image_path)

    return process_file(system_prompt=system_prompt, user_prompt=user_prompt, image_files=image_files)


# Main Script
if __name__ == "__main__":
    # Example prompts (customize based on your requirements)


    file_option = input("Do you want to process a PDF or multiple images? (Enter 'pdf' or 'images'): ").strip().lower()

    if file_option == "pdf":
        pdf_path = input("Enter the path to the PDF file: ")
        consolidated_results = process_file(file_path=pdf_path, system_prompt=system_prompt_1, user_prompt=user_prompt_1)
    elif file_option == "images":
        consolidated_results = upload_multiple_images(system_prompt_1, user_prompt_1)
    else:
        print("Invalid option.")
        exit(1)

    print("Processing complete.")
