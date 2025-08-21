from prostate_modular.database import DatabaseManager
import os
from datetime import datetime

class Backend:
    def __init__(self, db_path="DB/Informations.db"):
        self.db = DatabaseManager(db_path)

    def insert_patient_info(self, entries_1, entries_2=None, entries_3=None, entries_4=None):
        # Ensure all dicts are present
        if entries_2 is None:
            entries_2 = {}
        if entries_3 is None:
            entries_3 = {}
        if entries_4 is None:
            entries_4 = {}
        # Prepare a copy for DB insert
        entries_for_db = dict(entries_1)
        # Set ImagePath to the path, and Image to the binary
        entries_for_db["ImagePath"] = entries_for_db.get("Image", "")
        entries_for_db["Image"] = entries_for_db.get("Image_stored", None)
        # Remove the temporary key
        if "Image_stored" in entries_for_db:
            del entries_for_db["Image_stored"]
        # Now insert using your DatabaseManager
        self.db.insert_into_first_db(entries_for_db, entries_2, entries_3, entries_4)

    def ensure_patients_folder(self):
        """Create the 'patients' folder two levels up from the current script's directory if it does not exist."""
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
        parent_dir = os.path.dirname(script_dir)                # One level up (parent)
        grandparent_dir = os.path.dirname(parent_dir)           # Two levels up (parent of parent)
        folder_path = os.path.join(grandparent_dir, "patients")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        return folder_path

    def create_patient_subfolder(self,patient_name):
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
    
    def ensure_temp_folder(self):
        """Create the 'temp' folder in the parent directory of the current script's directory if it does not exist."""
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
        parent_dir = os.path.dirname(base_dir)  # Get parent directory
        grandparent_dir = os.path.dirname(parent_dir)           # Two levels up (parent of parent)
        folder_path = os.path.join(grandparent_dir, "temp")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path
    
    def combine_all_docx(self,folder_path,files_list):
        from docxcompose.composer import Composer
        from docx import Document as Document_compose
        number_of_sections=len(files_list)
        mast = Document_compose(files_list[0])
        composer = Composer(mast)
        for i in range(1, number_of_sections):
            doc_temp = Document_compose(files_list[i])
            composer.append(doc_temp)
        if folder_path:
            composer.save(folder_path + "/prostate.docx")
    