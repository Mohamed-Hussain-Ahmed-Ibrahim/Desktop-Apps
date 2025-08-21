import os
from datetime import datetime
def ensure_patients_folder():
    """Create the 'patients' folder two levels up from the current script's directory if it does not exist."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
    parent_dir = os.path.dirname(script_dir)                # One level up (parent)
    grandparent_dir = os.path.dirname(parent_dir)           # Two levels up (parent of parent)
    
    folder_path = os.path.join(grandparent_dir, "patients")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return folder_path
ensure_patients_folder()
def create_patient_subfolder(patient_name):
    """Create a sub-folder inside the 'patients' folder with the patient's name, and a date sub-folder inside it."""
    # Get the parent directory where 'patients' folder exists
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
    parent_dir = os.path.dirname(script_dir)                # One level up (parent)
    grandparent_dir = os.path.dirname(parent_dir)           # Two levels up (parent of parent)
    patients_folder = os.path.join(grandparent_dir, "patients")
    
    # Sanitize patient_name to avoid illegal characters in folder names
    safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    patient_folder = os.path.join(patients_folder, safe_name)
    
    if not os.path.exists(patient_folder):
        os.makedirs(patient_folder)
    
    # Create date sub-folder (format: DD-MM-YYYY)
    date_str = datetime.now().strftime("%d-%m-%Y")
    date_folder = os.path.join(patient_folder, date_str)
    
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)
    
    # Return the path to the date sub-folder
    return date_folder
create_patient_subfolder("aaa")
def ensure_temp_folder():
    """Create the 'temp' folder in the parent directory of the current script's directory if it does not exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
    parent_dir = os.path.dirname(base_dir)  # Get parent directory
    parent_dir = os.path.dirname(parent_dir)  # Get the parent of the parent directory
    folder_path = os.path.join(parent_dir, "temp")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path
ensure_temp_folder()