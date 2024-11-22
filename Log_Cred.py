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


api_key= "AIzaSyCraN2qjLcwFoWlmmCyFuWGhAQmcWYuQZE"
# ----------------------------------------------------------------------------------------------------------------------------------------------


system_prompt = """
        You are a specialist in extracting structured data from bank account opening forms and loan account forms.
        These forms may include both printed and handwritten data. Your task is to accurately interpret all the content
         in the form, regardless of format or handwriting style.
        Handle handwritten text carefully, considering variations in handwriting.
        """

user_prompt = """
          Analyze the images provided of the "Current Account Opening Form for Sole Proprietorship Firm" with
          extreme precision. Extract and organize all visible details, including headers, subheaders, 
          footnotes, field names, instructions, disclaimers, and form sections. Ensure no details are missed.
          Present the extracted data in a well-structured and machine-readable JSON format, following the 
          detailed structure outlined below:
          and if you find data related to specific data along with that field then only extract and show dont take reference of 
          previous any field
          For Below all parameter Specific Section present then only extrac the data other wise make it null and dont consider 
          for the output
        {Groups of the Sections  :       Group 1 
                                            Application Type and Account Details
                                            Sole Proprietor/Firm Details
                                            Proof of Identity (POI)
                                            Proof of Address (POA)
                                            Contact Details 
                                        Group 2
                                            Nature of Business
                                            Account Variant
                                            Service Requirements
                                            Mode of Operation
                                            Country of Residence as per Tax Laws
                                        Group 3
                                            Form 60 (If PAN is Not Available)
                                            Declaration and Undertaking
               on page only one group sections will be present  Any page have only one group of section }
        
        1. Application Type and Account Details
            Extract all fields under this section, including:
            
            Application Type (e.g., "New", "Update")
            Account Type (e.g., "Savings", "Current", "Others" - specify if mentioned)
            Current Account Number ("Not Filled" if blank)
            CIF Number, Branch Code, or Cycle Number
            Date of Application ("dd/mm/yyyy")
            Account Holder Type (e.g., "US REPORTABLE", "OTHER REPORTABLE")
        
        2. Sole Proprietor/Firm Details
            Extract the following:
            
            Name of Firm/Business
            Name of Proprietor
            Place of Formation
            Date of Formation ("dd/mm/yyyy")
            Business PAN Number or checkbox for "Form 60" (indicate if checked)
            Business TAN Number
            GSTN Number
            Any other identification numbers or additional notes
        
        3. Proof of Identity (POI)
            For each listed proof type, extract:
            
            Primary Proof of Identity Type (e.g., "Registration Certificate", "GST Certificate")
            Activity Proof 1
            Activity Proof 2
            Identity Number (this field is always more than 20 digit not less than 20 digit in any situations)
            Activity proof number (it i alswas 16 digit not more than or less than)
            If multiple documents are listed, extract all details while distinguishing between them.
        
        
        4. Proof of Address (POA)
            Extract fields for both Business/Office Address and Correspondence/Local Address (if different):
            
            Address Line 1
            Address Line 2
            Address Line 3
            City/District
            State
            Pin/Post Code
            Country Code and Name
            
            Same as Business/Office Address : If the checkbox for "Same as Business/Office Address" is ticked, mark 
            Correspondence/Local Address fields as "Not Filled".
        
        5. Contact Details
            Extract the following:
            
            Tele(RES.)
            Tele(OFF)
            Mobile Number of authorised signatory
            FAX
            Email Address
        
        6. Nature of Business
            Capture:
            
            Type of Business Activity (e.g., "Manufacturer", "Trader", "Service Provider", "Retailer", "Other")
            Industry Classification Code (if specified)
            Business Sector Code
            Sector Description
            Approximate Annual Turnover (e.g., "Amount")
            Approximate Turnover Year (e.g., "2020-21")
            Source of Funds (e.g., "Business Income", "Investments", "Donations")
            Include any additional fields or checkboxes in this section.
        
        
        7. Account Variant
            Preferred Account Variant (e.g., "Regular", "Gold", "Platinum")
        
        8. Service Requirements (for this Section all Cheak Boxs are present at right hand side some at exact right some little bit far  but all Cheak boxes are in the Right hand side  )
            For each service listed, indicate its checkbox status. Example:
            
            Corporate Internet Banking [one of this wil true both will never true so focus on cheak box ] ( (Viewing Rights (True/False) , Transaction Rights (True/False)  )
            Business Debit Card (e.g., "Pride", "Premium")
            Cash Management Products (e.g., "Cash Pick-up", "e-Collection", "e-Payment")
            Registration for Positive Pay System ("Yes"/"No")
            For sub-services (e.g., "POS Facility", "Cheque Machine", "UPI/QR Code","SMS Alerts", "E-Hand Shake Insta Deposit Card")
            , include details only if their corresponding checkboxes are ticked.
        
        9. Mode of Operation
            Specify Mode (e.g., "Singly", "Others" with additional details if provided)
        
        10. Country of Residence as per Tax Laws
            Extract all checkboxes and their corresponding labels.
        
        11. Form 60 (If PAN is Not Available)
            Capture the following fields:
        
            Name (must match ID proof)
            If applied for PAN but not yet generated:
            Date of Application
            Acknowledgment Number
            If PAN is not applied:
            Agriculture Income ("True"/"False")
            Other than Agriculture Income ("True"/"False")
            Verification Paragraph
            
        13. Declaration and Undertaking
            Extract the following:
        
            Name of the Customer
            Table Content (e.g., "Total Credit Exposure")
            Declaration Paragraph
        
        
        VERY IMPORTANT NOTE : 1) if some section Not present in images then Extract the data from that section only dump rest of
                                 the section dont include it in the out put" (this is very main part dont miss this )
                              2) and it is not necessary that all section that is mentioned above is need to present in the 
                                 every image some section will not be present so dont consider theM for output  
                              3) All Section that is given above is for the reference Dont give output like above section
            
        Important Notes for Extraction:
        Preserve Formatting and Structure: Ensure extracted data reflects the original form's layout and logical order.
        Capture All Field Names: Include fields even if blank or optional, marking them as "Not Filled".
        Handwritten Details: Accurately transcribe all handwritten content.
        Extract Marginal Notes: Include notes, footnotes, page headers, footers, or marginal instructions.
        Language Content: Extract text in all visible languages, noting the language for each.
        Visual Elements: Include logos, stamps, or signatures as annotations/metadata.
        Exclude Missing Sections: If a section is absent, omit it from the output."""



