import json
import os
from tkinter import simpledialog, Toplevel, filedialog
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkEntry
from tkinter.messagebox import showinfo
from prostate_modular.utils import CustomCTkComboBox
from customtkinter import CTkImage
from docxtpl import DocxTemplate, InlineImage
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo, showerror
from prostate_modular.database import DatabaseManager
from prostate_modular.constant import entries_1, entries_2, entries_3
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image
import io
from tkinter import ttk
class HospitalPopup(Toplevel):
    def __init__(self, parent, current_value, on_select_callback):
        super().__init__(parent)
        self.parent = parent
        self.current_value = current_value
        self.on_select_callback = on_select_callback
        self.hospital_list = []
        self.hospital_combobox = None
        self.setup_popup()
        self.load_hospitals()
        self.create_widgets()
    def setup_popup(self):
        """Configure the popup window properties"""
        self.geometry("400x250+550+410")
        self.config(bg="black")
        self.title("Choose Hospital")
        self.focus_force()
        
    def load_hospitals(self):
        """Load hospital list from file or use default"""
        hospital_file_path = os.path.join("DB", "hospitals.json")
        if os.path.exists(hospital_file_path):
            try:
                with open(hospital_file_path, 'r', encoding='utf-8') as f:
                    self.hospital_list = json.load(f)
            except Exception:
                self.hospital_list = ["NGH", "AL-SALAM", "IHUN"]
        else:
            self.hospital_list = ["NGH", "AL-SALAM", "IHUN"]
            
    def create_widgets(self):
        """Create and place all widgets in the popup"""
        # ComboBox for hospital selection
        combo_label = CTkLabel(self, text="Select Hospital:", font=("Helvetica", 16, 'bold'))
        combo_label.pack(pady=(20, 5))
        
        self.hospital_combobox = CustomCTkComboBox(self, values=self.hospital_list, font=("Helvetica", 16), width=250)
        self.hospital_combobox.pack(pady=5)
        
        if self.current_value in self.hospital_list:
            self.hospital_combobox.set(self.current_value)
        else:
            self.hospital_combobox.set(self.hospital_list[0])

        # Add Hospital button
        add_button = CTkButton(self, text="Add Hospital", command=self.add_hospital, font=("Helvetica", 14))
        add_button.pack(pady=10)

        # Confirm button
        confirm_button = CTkButton(self, text="Confirm", command=self.confirm_selection, font=("Helvetica", 14), fg_color="green")
        confirm_button.pack(pady=10)
        
    def add_hospital(self):
        """Add a new hospital to the list"""
        new_hospital = simpledialog.askstring("Add Hospital", "Enter new hospital name:", parent=self)
        if new_hospital and new_hospital.strip() and new_hospital not in self.hospital_list:
            self.hospital_list.append(new_hospital.strip())
            try:
                hospital_file_path = os.path.join("DB", "hospitals.json")
                with open(hospital_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.hospital_list, f, ensure_ascii=False, indent=2)
            except Exception as e:
                showinfo("Error", f"Failed to save hospital list: {e}")
            self.hospital_combobox.configure(values=self.hospital_list)
            self.hospital_combobox.set(new_hospital.strip())
            
    def confirm_selection(self):
        """Confirm the selected hospital and close popup"""
        selected = self.hospital_combobox.get()
        self.on_select_callback(selected)
        self.destroy()
        
        # Resize parent window
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        window_width = int(screen_width * 0.99)
        window_height = int(screen_height * 0.99)
        self.parent.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")
        self.parent.protocol("WM_DELETE_WINDOW", lambda: self.parent.on_close_window())
        self.parent.state("normal")
        self.parent.focus_force()
        return selected
    
    @staticmethod
    def on_tree_select(event, data_table, parent, main_window=None):
        selected_item = data_table.selection()
        if selected_item:
            # Get the selected row data
            item_values = data_table.item(selected_item[0])['values']
            
            # Create a professional popup window
            popup = Toplevel(parent)
            popup.title(f"Patient: {item_values[3]}")
            popup.geometry("500x600+600+200")
            popup.config(bg="#f8f8fa")
            
            # Header
            header = CTkLabel(popup, text=f"Patient Details", font=("Arial Black", 20), fg_color="transparent", text_color="black")
            header.pack(pady=(20, 10))
            
            # Display selected patient info in a grid
            info_frame = CTkFrame(popup, fg_color="white", corner_radius=15)
            info_frame.pack(padx=30, pady=10, fill="both", expand=True)
            
            labels = [
                ("Hospital", 1), ("Date", 2), ("Name", 3), ("Age", 4), 
                ("MRI Results", 7), ("PSA", 10), ("DRE", 13), ("Family History", 14)
            ]
            
            for row, (label, idx) in enumerate(labels):
                if idx < len(item_values):
                    CTkLabel(info_frame, text=f"{label}: ", font=("Arial", 14, "bold"), 
                            fg_color="transparent", text_color="black", anchor="w").grid(
                        row=row, column=0, sticky="w", padx=10, pady=6)
                    CTkLabel(info_frame, text=str(item_values[idx]), font=("Arial", 14), 
                            fg_color="transparent", text_color="black", anchor="w").grid(
                        row=row, column=1, sticky="w", padx=10, pady=6)    
            # Button frame
            button_frame = CTkFrame(popup, fg_color="transparent")
            button_frame.pack(pady=20)    
            export_btn = CTkButton(button_frame, text="Export", font=("Arial Black", 15), 
                                 fg_color="#2A8C55", hover_color="#207244", width=120, height=40, 
                                 command=lambda: HospitalPopup.export_patient(item_values,popup))
            export_btn.pack(side="left", padx=20)       
            update_btn = CTkButton(button_frame, text="Update", font=("Arial Black", 15), 
                                 fg_color="#00008B", hover_color="#071330", width=120, height=40, 
                                 command=lambda: HospitalPopup.update_patient(item_values,popup, update_callback=main_window.update_table if main_window else None))
            update_btn.pack(side="left", padx=20)
    
    @staticmethod
    def export_patient(item_values, popup):
        from docxcompose.composer import Composer
        from docx import Document as Document_compose
        from docxtpl import DocxTemplate, InlineImage
        from docx.shared import Mm
        from PIL import Image
        import io
        import os
        from tkinter.filedialog import asksaveasfilename
        from tkinter.messagebox import showerror, showinfo
        from prostate_modular.database import DatabaseManager

        def get():
            """Clear temp directory"""
            try:
                if not os.path.exists("temp"):
                    os.makedirs("temp")
                for file in os.listdir("temp"):
                    file_path = os.path.join("temp", file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception as e:
                showerror(f"Warning: Could not clear temp directory: {e}")
            return []

        def combine_all_docx(files_list):
            """Combine multiple docx files into one"""
            try:
                # Filter out non-existent files
                existing_files = [f for f in files_list if os.path.exists(f)]
                
                if not existing_files:
                    showerror("Export Error", "No valid document files to combine.")
                    return
                
                number_of_sections = len(existing_files)
                mast = Document_compose(existing_files[0])
                composer = Composer(mast)
                
                for i in range(1, number_of_sections):
                    doc_temp = Document_compose(existing_files[i])
                    composer.append(doc_temp)
                
                file_path = asksaveasfilename(
                    defaultextension=".docx", 
                    filetypes=[("Word files", "*.docx")]
                )
                
                if file_path:
                    composer.save(file_path)
                    showinfo("Success", "Data exported successfully!")
                else:
                    showinfo("Info","Export cancelled by user.")
                    
            except Exception as e:
                showerror("Combine Error", f"Failed to combine documents: {str(e)}")

        def binary_to_image(image_data):
            """Convert image data to PIL Image"""
            try:
                if isinstance(image_data, bytes):
                    return Image.open(io.BytesIO(image_data))
                elif isinstance(image_data, str):
                    if os.path.exists(image_data):
                        return Image.open(image_data)
                    try:
                        import base64
                        return Image.open(io.BytesIO(base64.b64decode(image_data)))
                    except:
                        pass
                return Image.new('RGB', (100, 100), color='white')
            except Exception as e:
                showerror("Image Conversion Error", f"Failed to convert image data to PIL Image: {str(e)}")
                return Image.new('RGB', (100, 100), color='white')

        def create_placeholder_image(image_path):
            """Create a placeholder image if none exists"""
            try:
                placeholder = Image.new('RGB', (100, 100), color='white')
                placeholder.save(image_path)
                return True
            except Exception as e:
                showerror("Image Creation Error", f"Failed to create placeholder image: {str(e)}")
                return False

        def process_image_for_document(image_data, temp_image_path):
            """Process image data and save to temp path"""
            try:
                if image_data:
                    img = binary_to_image(image_data)
                    img.save(temp_image_path)
                    return True
                else:
                    return create_placeholder_image(temp_image_path)
            except Exception as e:
                showerror("Image Processing Error", f"Failed to process image: {str(e)}")
                return create_placeholder_image(temp_image_path)

        try:
            get()  # Clear temp directory
            
            # Verify template files exist
            template_paths = {
                "life": {
                    "doc1": "DOC/Life/1.docx",
                    "doc2": "DOC/Life/2.docx",
                    "doc3": "DOC/Life/3.docx",
                    "doc4": "DOC/Life/4.docx"
                },
                "kidney": {
                    "doc1": "DOC/Kidney and Tract/1.docx",
                    "doc2": "DOC/Kidney and Tract/2.docx",
                    "doc3": "DOC/Kidney and Tract/3.docx",
                    "doc4": "DOC/Kidney and Tract/4.docx"
                }
            }

            # Determine hospital type
            hospital = item_values[1].lower()
            if "life" in hospital:
                templates = template_paths["life"]
                hospital_type = "life"
            else:
                templates = template_paths["kidney"]
                hospital_type = "kidney"

            # Verify all template files exist
            missing_templates = []
            for doc_name, path in templates.items():
                if not os.path.exists(path):
                    missing_templates.append(path)
            
            if missing_templates:
                showerror("Template Error", f"Template files not found:\n" + "\n".join(missing_templates))
                return

            # Temporary document paths
            temp_files = [
                "temp/1.docx",
                "temp/2.docx",
                "temp/3.docx",
                "temp/4.docx"
            ]

            # Temporary image paths
            temp_images = [
                "temp/1.png",
                "temp/2.png",
                "temp/3.png"
            ]

            # Get patient data
            patient_id = item_values[0]
            db = DatabaseManager("DB/Informations.db")
            cursor = db.connection.cursor()

            try:
                # Fetch patient info
                cursor.execute("SELECT * FROM PatientsInfo WHERE ID=?", (patient_id,))
                patient_row = cursor.fetchone()
                if not patient_row:
                    showerror("Export Error", "Patient not found in database.")
                    return

                # Get column names and populate entries_1
                cursor.execute("SELECT * FROM PatientsInfo LIMIT 1")
                columns = [desc[0] for desc in cursor.description]
                entries_1 = dict(zip(columns, patient_row))
                
                # Process first image
                image1_processed = False
                if "Image" in entries_1:
                    image1_processed = process_image_for_document(entries_1["Image"], temp_images[0])
                    entries_1["Image"] = "{{Image}}"

                # Fetch PatientsSide data
                cursor.execute("SELECT * FROM PatientsSide WHERE patientsinfo_id=?", (patient_id,))
                side_row = cursor.fetchone()
                entries_2 = {}
                if side_row:
                    cursor.execute("SELECT * FROM PatientsSide LIMIT 1")
                    side_columns = [desc[0] for desc in cursor.description]
                    entries_2 = dict(zip(side_columns, side_row))

                # Fetch FirstBottles data
                cursor.execute("SELECT * FROM FirstBottles WHERE patientsinfo_id=?", (patient_id,))
                bottle_row = cursor.fetchone()
                bottle_row = tuple('' if value is None else value for value in bottle_row) if bottle_row else None

                entries_3 = {}
                image2_processed = False
                if bottle_row:
                    cursor.execute("SELECT * FROM FirstBottles LIMIT 1")
                    bottle_columns = [desc[0] for desc in cursor.description]
                    entries_3 = dict(zip(bottle_columns, bottle_row))

                    # Process second image
                    if "Image" in entries_3:
                        image2_processed = process_image_for_document(entries_3["Image"], temp_images[1])
                        entries_3["Image"] = "{{Image}}"
                
                # Fetch SecondBottles data (fourth page)
                cursor.execute("SELECT id FROM PatientsSide WHERE patientsinfo_id=?", (patient_id,))
                patientsside_id_result = cursor.fetchone()
                entries_4 = {}
                image3_processed = False
                if patientsside_id_result:
                    patientsside_id = patientsside_id_result[0]
                    cursor.execute("SELECT * FROM SecondBottles WHERE patientsside_id=?", (patientsside_id,))
                    second_bottle_row = cursor.fetchone()
                    second_bottle_row = tuple('' if value is None else value for value in second_bottle_row) if second_bottle_row else None

                    if second_bottle_row:
                        cursor.execute("SELECT * FROM SecondBottles LIMIT 1")
                        second_bottle_columns = [desc[0] for desc in cursor.description]
                        entries_4 = dict(zip(second_bottle_columns, second_bottle_row))
                        
                        # Process third image
                        if "Image" in entries_4:
                            image3_processed = process_image_for_document(entries_4["Image"], temp_images[2])
                            entries_4["Image"] = "{{Image}}"

                # Prepare entries for rendering
                entries_3["Lesions"] = entries_1.get("Lesions", "")
                entries_3["Degree"] = entries_1.get("Degree", "")
                entries_3["DRE"] = entries_1.get("DRE", "")
                
                # Prepare contexts for document rendering
                context1 = {"entries": entries_1}
                context2 = {"entries": entries_2}
                context3 = {"entries": entries_3}
                context4 = {"entries": entries_4}

                # Load templates
                doc1 = DocxTemplate(templates["doc1"])
                doc2 = DocxTemplate(templates["doc2"])
                doc3 = DocxTemplate(templates["doc3"])
                doc4 = DocxTemplate(templates["doc4"])

                # Render documents
                try:
                    # Render first document
                    doc1.render(context1)
                    doc1.save(temp_files[0])
                    
                    # Add image to first document if processed
                    if image1_processed and os.path.exists(temp_images[0]):
                        doc1 = DocxTemplate(temp_files[0])
                        marked_inline_image = InlineImage(doc1, temp_images[0], width=Mm(136), height=Mm(32))
                        context1["Image"] = marked_inline_image
                        doc1.render(context1)
                        doc1.save(temp_files[0])

                    # Render second document
                    if entries_2:  # Only render if data exists
                        doc2.render(context2)
                        doc2.save(temp_files[1])
                    else:
                        # Create empty document or skip
                        print("No PatientsSide data found, skipping document 2")

                    # Render third document
                    if entries_3:  # Only render if data exists
                        doc3.render(context3)
                        doc3.save(temp_files[2])
                        
                        # Add image to third document if processed
                        if image2_processed and os.path.exists(temp_images[1]):
                            doc3 = DocxTemplate(temp_files[2])
                            marked_inline_image = InlineImage(doc3, temp_images[1], width=Mm(136), height=Mm(32))
                            context3["Image"] = marked_inline_image
                            doc3.render(context3)
                            doc3.save(temp_files[2])
                    else:
                        print("No FirstBottles data found, skipping document 3")
                    
                    # Render fourth document
                    if entries_4:  # Only render if data exists
                        # First render without image
                        doc4.render(context4)
                        doc4.save(temp_files[3])
                        
                        # Add image to fourth document if processed
                        if image3_processed and os.path.exists(temp_images[2]):
                            doc4 = DocxTemplate(temp_files[3])
                            marked_inline_image = InlineImage(doc4, temp_images[2], width=Mm(136), height=Mm(32))
                            context4["Image"] = marked_inline_image
                            doc4.render(context4)
                            doc4.save(temp_files[3])
                    else:
                        print("No SecondBottles data found, skipping document 4")

                    # Combine all existing documents
                    combine_all_docx(temp_files)

                except Exception as e:
                    showerror("Document Render Error", f"Failed to render documents: {str(e)}")
                    return

            except Exception as e:
                showerror("Database Error", f"Failed to fetch patient data: {str(e)}")
                return

        except Exception as e:
            showerror("Export Error", f"Failed to export patient: {str(e)}")
        finally:
            if 'db' in locals():
                db.connection.close()
            if 'popup' in locals():
                popup.focus_force()
    def clean_data(self,data):
        return [tuple("" if item is None else item for item in row) for row in data]
    @staticmethod
    def update_patient(item_values, popup, update_callback=None):
        """
        Open the PatientUpdatePopup for editing.
        Pass update_callback=main_window_instance.update_table to refresh after update.
        """
        patient_id = item_values[0]
        PatientUpdatePopup(popup, patient_id, update_callback=update_callback)


class PatientUpdatePopup(Toplevel):
    def __init__(self, parent, patient_id, update_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.patient_id = patient_id
        self.db = DatabaseManager("DB/Informations.db")
        self.entries = {}
        self.update_callback = update_callback
        self.title("Update Patient")
        self.geometry("1256x900+600+100")
        self.config(bg="#f8f8fa")
        self.create_widgets()
        self.load_patient_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        # Show the parent window before closing
        if hasattr(self, 'parent') and self.parent:
            self.parent.deiconify()
        self.destroy()
    def create_widgets(self):
        self.geometry("1256x900+600+100")
        # Scrollable frame for many fields
        self.frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)
        self.fields = [
            ("Hospital", "Hospital"), ("Date", "Date"), ("Name", "Name"), ("US", "US"), ("Age", "Age"),
            ("Nationality", "Nationality"), ("DR", "DR"), ("Mri_Result", "Mri_Result"), ("FPSA", "FPSA"),
            ("TPSA", "TPSA"), ("PSA", "PSA"), ("Degree", "Degree"), ("Machine", "Machine"), ("DRE", "DRE"),
            ("Family", "Family"), ("WG_TD_mm", "WG_TD_mm"), ("WG_Height_mm", "WG_Height_mm"), ("WG_Length_mm", "WG_Length_mm"),
            ("WG_Volume_cc", "WG_Volume_cc"), ("A_TD_mm", "A_TD_mm"), ("A_Height_mm", "A_Height_mm"), ("A_Length_mm", "A_Length_mm"),
            ("A_Volume_cc", "A_Volume_cc"), ("Urinary_Bladder", "Urinary_Bladder"), ("Bladder_Neck", "Bladder_Neck"),
            ("Seminal_Vesicles", "Seminal_Vesicles"), ("Vasa_Deferentia", "Vasa_Deferentia"), ("Ejaculatory_Ducts", "Ejaculatory_Ducts"),
            ("Lesions", "Lesions")
        ]
        # Display two fields per row
        for idx in range(0, len(self.fields), 2):
            col = 0
            for offset in range(2):
                if idx + offset < len(self.fields):
                    label, key = self.fields[idx + offset]
                    CTkLabel(self.frame, text=label+":", font=("Arial", 13, "bold"), text_color="#222").grid(row=idx//2, column=col, sticky="w", padx=10, pady=4)
                    entry = CTkEntry(self.frame, width=250, font=("Arial", 13))
                    entry.grid(row=idx//2, column=col+1, padx=10, pady=4, sticky="ew")
                    self.entries[key] = entry
                    col += 2
        # Save button
        save_btn = CTkButton(self.frame, text="Save", font=("Arial Black", 15), fg_color="#059669", hover_color="#047857", width=120, height=40, command=self.save_patient)
        save_btn.grid(row=(len(self.fields)+1)//2, column=0, columnspan=4, pady=20)
        # Next button
        next_btn = CTkButton(self.frame, text="Next", font=("Arial Black", 15), fg_color="#3b82f6", hover_color="#1e3a8a", width=120, height=40, command=self.open_second_page_update)
        next_btn.grid(row=(len(self.fields)+2)//2, column=3, columnspan=4, pady=10)

    def load_patient_data(self):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM PatientsInfo WHERE ID=?", (self.patient_id,))
        row = cursor.fetchone()
        cursor.execute("SELECT * FROM PatientsInfo LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        if not row:
            showerror("Error", "Patient not found.")
            self.destroy()
            return
        data = dict(zip(columns, row))
        for key in self.entries:
            value = data.get(key, "")
            if value is None:
                value = ""
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, str(value))

    def save_patient(self, call_update_callback=True, close_after_save=True):
        updated_fields = {}
        for key, entry in self.entries.items():
            updated_fields[key] = entry.get()
        try:
            self.db.update_patient(self.patient_id, updated_fields)
            showinfo("Update Success", "Patient updated successfully!")
            if call_update_callback and self.update_callback:
                self.update_callback()
            if close_after_save:
                self.destroy()
        except Exception as e:
            showerror("Update Error", f"Failed to update patient: {e}")

    def open_second_page_update(self):
        # Save first page changes before moving to second page
        self.save_patient(call_update_callback=True, close_after_save=False)
        # Don't destroy the parent window, just hide it
        self.parent.withdraw()  # Instead of self.parent.destroy()
        SecondPageUpdatePopup(self, self.patient_id, update_callback=self.update_callback)

class SecondPageUpdatePopup(Toplevel):
    def __init__(self, parent, patientsinfo_id, update_callback=None):
        super().__init__(parent)
        self.parent = parent  # Store the parent reference
        self.patientsinfo_id = patientsinfo_id
        self.patientsinfo_id = patientsinfo_id
        self.db = DatabaseManager("DB/Informations.db")
        self.entries = {}
        self.update_callback = update_callback
        self.title("Update Second Page (Prostate Zones)")
        self.geometry("900x700+650+150")
        self.config(bg="#f8f8fa")
        self.create_widgets()
        self.load_patients_side_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        # Show the parent window before closing
        if hasattr(self, 'parent') and self.parent:
            self.parent.deiconify()
        self.destroy()
    def create_widgets(self):
        from prostate_modular.constant import entries_2
        self.frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)
        self.fields = [
            ("AApexR", "AApexR"), ("AApexL", "AApexL"), ("AMidProstateR", "AMidProstateR"), ("AMidProstateL", "AMidProstateL"),
            ("ABaseR", "ABaseR"), ("ABaseL", "ABaseL"), ("MApexR", "MApexR"), ("MApexL", "MApexL"),
            ("MMidprostateR", "MMidprostateR"), ("MMidprostateL", "MMidprostateL"), ("MBaseR", "MBaseR"), ("MBaseL", "MBaseL"),
            ("PApexR", "PApexR"), ("PApexL", "PApexL"), ("PMidprostateR", "PMidprostateR"), ("PMidprostateL", "PMidprostateL"),
            ("PBaseR", "PBaseR"), ("PBaseL", "PBaseL"), ("TMidprostateR", "TMidprostateR"), ("TMidprostateL", "TMidprostateL"),
            ("TBaseR", "TBaseR"), ("TBaseL", "TBaseL")
        ]
        for idx in range(0, len(self.fields), 2):
            col = 0
            for offset in range(2):
                if idx + offset < len(self.fields):
                    label, key = self.fields[idx + offset]
                    CTkLabel(self.frame, text=label+":", font=("Arial", 13, "bold"), text_color="#222").grid(row=idx//2, column=col, sticky="w", padx=10, pady=4)
                    entry = CTkEntry(self.frame, width=180, font=("Arial", 13))
                    entry.grid(row=idx//2, column=col+1, padx=10, pady=4, sticky="ew")
                    self.entries[key] = entry
                    col += 2
        save_btn = CTkButton(self.frame, text="Save", font=("Arial Black", 15), fg_color="#059669", hover_color="#047857", width=120, height=40, command=self.save_patients_side)
        save_btn.grid(row=(len(self.fields)+1)//2, column=0, columnspan=4, pady=20)
        # Next button
        next_btn = CTkButton(self.frame, text="Next", font=("Arial Black", 15), fg_color="#3b82f6", hover_color="#1e3a8a", width=120, height=40, command=self.open_third_page_update)
        next_btn.grid(row=(len(self.fields)+1)//2, column=3, columnspan=4, pady=10)
    def load_patients_side_data(self):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM PatientsSide WHERE patientsinfo_id=?", (self.patientsinfo_id,))
        row = cursor.fetchone()
        cursor.execute("SELECT * FROM PatientsSide LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        if not row:
            showerror("Error", "Second page data not found.")
            self.destroy()
            return
        data = dict(zip(columns, row))
        for key in self.entries:
            value = data.get(key, "")
            if value is None:
                value = ""
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, str(value))

    def save_patients_side(self, call_update_callback=True, close_after_save=True):
        updated_fields = {}
        for key, entry in self.entries.items():
            updated_fields[key] = entry.get()
        try:
            self.db.update_patients_side(self.patientsinfo_id, updated_fields)
            showinfo("Update Success", "Second page updated successfully!")
            if call_update_callback and self.update_callback:
                self.update_callback()
            if close_after_save:
                self.destroy()
        except Exception as e:
            showerror("Update Error", f"Failed to update second page: {e}")

    def open_third_page_update(self):
        # Save second page changes before moving to third page
        self.save_patients_side(call_update_callback=True, close_after_save=False)
        self.withdraw()  # Hide instead of destroy
        ThirdPageUpdatePopup(self, self.patientsinfo_id, update_callback=self.update_callback)

class ThirdPageUpdatePopup(Toplevel):
    def __init__(self, parent, patientsinfo_id, update_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.patientsinfo_id = patientsinfo_id
        self.db = DatabaseManager("DB/Informations.db")
        self.entries = {}
        self.update_callback = update_callback
        self.title("Update Third Page (Biopsy Bottles)")
        self.geometry("1400x800+500+100")
        self.config(bg="#f8f8fa")
        self.create_widgets()
        self.load_first_bottles_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        # Show the parent window before closing
        if hasattr(self, 'parent') and self.parent:
            self.parent.deiconify()
        self.destroy()
    def create_widgets(self):
        # Create scrollable frame
        self.frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each bottle (1-10)
        self.bottle_tabs = []
        for i in range(1, 11):
            tab = CTkFrame(self.notebook, fg_color="white")
            self.notebook.add(tab, text=f"Bottle {i}")
            self.bottle_tabs.append(tab)
            self.create_bottle_tab(tab, i)
        
        # Save button
        save_btn = CTkButton(self.frame, text="Save Changes", font=("Arial Black", 15), 
                            fg_color="#059669", hover_color="#047857", width=150, height=40, 
                            command=self.save_first_bottles)
        save_btn.pack(pady=20)
        # Next button
        # In ThirdPageUpdatePopup.create_widgets(), add this after the save button:
        next_btn = CTkButton(self.frame, text="Next", font=("Arial Black", 15), 
                            fg_color="#3b82f6", hover_color="#1e3a8a", width=120, height=40, 
                            command=self.open_fourth_page_update)
        next_btn.pack(pady=10)

    # Add this method to ThirdPageUpdatePopup:
    def open_fourth_page_update(self):
        self.save_first_bottles(call_update_callback=False, close_after_save=False)
        self.withdraw()
        FourthPageUpdatePopup(self, self.patientsinfo_id, update_callback=self.update_callback)

    def create_bottle_tab(self, tab, bottle_num):
        # Fields for each bottle
        fields = [
            ("Site of Biopsy", f"Site_of_biopsy_{bottle_num}"),
            ("US Risk Features", f"US_risk_features_{bottle_num}"),
            ("No of Cores", f"no_of_cores_{bottle_num}"),
            ("BPH", f"BPH_{bottle_num}"),
            ("Prostatitis", f"Prostatitis_{bottle_num}"),
            ("Atrophy", f"Atrophy_{bottle_num}"),
            ("Basal Cell Hyperplasia", f"BasalCellHqPerPlasiq_{bottle_num}"),
            ("PIN", f"PIN_{bottle_num}"),
            ("CA Prostate", f"ca_prostate_{bottle_num}"),
            ("CA Grade", f"ca_grade_{bottle_num}")
        ]
        
        # Add Gleason score fields
        gleason_fields = [
            ("Gleason 2", f"Gleason_{bottle_num}_2"),
            ("Gleason 2+3", f"Gleason_{bottle_num}_2_3"),
            ("Gleason 3+3", f"Gleason_{bottle_num}_3_3"),
            ("Gleason 3+4", f"Gleason_{bottle_num}_3_4"),
            ("Gleason 4+3", f"Gleason_{bottle_num}_4_3"),
            ("Gleason 4+4", f"Gleason_{bottle_num}_4_4"),
            ("Gleason 4+5", f"Gleason_{bottle_num}_4_5"),
            ("Gleason 5+4", f"Gleason_{bottle_num}_5_4"),
            ("Gleason 5+5", f"Gleason_{bottle_num}_5_5"),
            ("Gleason 5+6", f"Gleason_{bottle_num}_5_6"),
            ("Gleason 6+5", f"Gleason_{bottle_num}_6_5"),
            ("Gleason 6+6", f"Gleason_{bottle_num}_6_6"),
            ("Gleason 6+7", f"Gleason_{bottle_num}_6_7"),
            ("Gleason 7+6", f"Gleason_{bottle_num}_7_6"),
            ("Gleason 7+7", f"Gleason_{bottle_num}_7_7"),
            ("Gleason 7+8", f"Gleason_{bottle_num}_7_8"),
            ("Gleason 8+7", f"Gleason_{bottle_num}_8_7"),
            ("Gleason 8+8", f"Gleason_{bottle_num}_8_8"),
            ("Gleason 8+9", f"Gleason_{bottle_num}_8_9"),
            ("Gleason 9+9", f"Gleason_{bottle_num}_9_9")
        ]
        
        # Create frame for regular fields
        fields_frame = CTkFrame(tab, fg_color="white")
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add regular fields
        for i, (label, key) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            CTkLabel(fields_frame, text=label+":", font=("Arial", 12, "bold"), 
                    text_color="#222").grid(row=row, column=col, sticky="w", padx=10, pady=4)
            entry = CTkEntry(fields_frame, width=200, font=("Arial", 12))
            entry.grid(row=row, column=col+1, padx=10, pady=4, sticky="ew")
            self.entries[key] = entry
        
        # Create frame for Gleason scores
        gleason_frame = CTkFrame(tab, fg_color="white")
        gleason_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add Gleason score fields
        CTkLabel(gleason_frame, text="Gleason Scores:", font=("Arial", 14, "bold"), 
                text_color="#222").grid(row=0, column=0, columnspan=4, pady=10)
        
        for i, (label, key) in enumerate(gleason_fields):
            row = (i // 4) + 1
            col = (i % 4) * 2
            CTkLabel(gleason_frame, text=label+":", font=("Arial", 11, "bold"), 
                    text_color="#222").grid(row=row, column=col, sticky="w", padx=5, pady=2)
            entry = CTkEntry(gleason_frame, width=80, font=("Arial", 11))
            entry.grid(row=row, column=col+1, padx=5, pady=2, sticky="ew")
            self.entries[key] = entry

    def load_first_bottles_data(self):
        """Load existing data from FirstBottles table"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM FirstBottles WHERE patientsinfo_id=?", (self.patientsinfo_id,))
        row = cursor.fetchone()
        
        if not row:
            # No existing data - this is fine, user can create new data
            showinfo("Info", "No existing biopsy data found. You can enter new data.")
            return
            
        # Get column names
        cursor.execute("SELECT * FROM FirstBottles LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        
        # Create data dictionary
        data = dict(zip(columns, row))
        
        # Populate the entry fields
        for key, entry_widget in self.entries.items():
            value = data.get(key, "")
            if value is None:
                value = ""
                
            if hasattr(entry_widget, 'delete') and hasattr(entry_widget, 'insert'):
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, str(value))

    def save_first_bottles(self, call_update_callback=True, close_after_save=True):
        """Save the updated data to FirstBottles table"""
        updated_fields = {}
        
        # Collect data from all entry fields
        for key, entry_widget in self.entries.items():
            if hasattr(entry_widget, 'get'):
                updated_fields[key] = entry_widget.get()
        
        try:
            # Check if record exists
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM FirstBottles WHERE patientsinfo_id=?", (self.patientsinfo_id,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing record
                self.db.update_first_bottles(self.patientsinfo_id, updated_fields)
                showinfo("Success", "Biopsy bottles data updated successfully!")
            else:
                # Insert new record
                updated_fields['patientsinfo_id'] = self.patientsinfo_id
                columns = ', '.join(updated_fields.keys())
                placeholders = ', '.join(['?' for _ in updated_fields])
                sql = f"INSERT INTO FirstBottles ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(updated_fields.values()))
                self.db.connection.commit()
                showinfo("Success", "Biopsy bottles data saved successfully!")
            
            # Call update callback to refresh parent table if requested
            if call_update_callback and self.update_callback:
                self.update_callback()
                
            # Close window if requested
            if close_after_save:
                self.destroy()
            
        except Exception as e:
            showerror("Error", f"Failed to save biopsy bottles data: {e}")

class FourthPageUpdatePopup(Toplevel):
    def __init__(self, parent, patientsinfo_id, update_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.patientsinfo_id = patientsinfo_id
        self.db = DatabaseManager("DB/Informations.db")
        self.entries = {}
        self.update_callback = update_callback
        self.title("Update Fourth Page (Additional Biopsy Bottles)")
        self.geometry("1400x800+500+100")
        self.config(bg="#f8f8fa")
        self.create_widgets()
        self.load_second_bottles_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        if hasattr(self, 'parent') and self.parent:
            self.parent.deiconify()
        self.destroy()
    
    def create_widgets(self):
        # Create scrollable frame
        self.frame = CTkFrame(self, fg_color="white", corner_radius=15)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each bottle (11-20)
        self.bottle_tabs = []
        for i in range(11, 21):
            tab = CTkFrame(self.notebook, fg_color="white")
            self.notebook.add(tab, text=f"Bottle {i}")
            self.bottle_tabs.append(tab)
            self.create_bottle_tab(tab, i)
        
        # Save button
        save_btn = CTkButton(self.frame, text="Save Changes", font=("Arial Black", 15), 
                            fg_color="#059669", hover_color="#047857", width=150, height=40, 
                            command=self.save_second_bottles)
        save_btn.pack(pady=20)

    def create_bottle_tab(self, tab, bottle_num):
        # Fields for each bottle
        fields = [
            ("Site of Biopsy", f"Site_of_biopsy_{bottle_num}"),
            ("US Risk Features", f"US_risk_features_{bottle_num}"),
            ("No of Cores", f"no_of_cores_{bottle_num}"),
            ("BPH", f"BPH_{bottle_num}"),
            ("Prostatitis", f"Prostatitis_{bottle_num}"),
            ("Atrophy", f"Atrophy_{bottle_num}"),
            ("Basal Cell Hyperplasia", f"BasalCellHqPerPlasiq_{bottle_num}"),
            ("PIN", f"PIN_{bottle_num}"),
            ("CA Prostate", f"ca_prostate_{bottle_num}"),
            ("CA Grade", f"ca_grade_{bottle_num}")
        ]
        
        # Add Gleason score fields
        gleason_fields = [
            ("Gleason 2", f"Gleason_{bottle_num}_2"),
            ("Gleason 2+3", f"Gleason_{bottle_num}_2_3"),
            ("Gleason 3+3", f"Gleason_{bottle_num}_3_3"),
            ("Gleason 3+4", f"Gleason_{bottle_num}_3_4"),
            ("Gleason 4+3", f"Gleason_{bottle_num}_4_3"),
            ("Gleason 4+4", f"Gleason_{bottle_num}_4_4"),
            ("Gleason 4+5", f"Gleason_{bottle_num}_4_5"),
            ("Gleason 5+4", f"Gleason_{bottle_num}_5_4"),
            ("Gleason 5+5", f"Gleason_{bottle_num}_5_5"),
            ("Gleason 5+6", f"Gleason_{bottle_num}_5_6"),
            ("Gleason 6+5", f"Gleason_{bottle_num}_6_5"),
            ("Gleason 6+6", f"Gleason_{bottle_num}_6_6"),
            ("Gleason 6+7", f"Gleason_{bottle_num}_6_7"),
            ("Gleason 7+6", f"Gleason_{bottle_num}_7_6"),
            ("Gleason 7+7", f"Gleason_{bottle_num}_7_7"),
            ("Gleason 7+8", f"Gleason_{bottle_num}_7_8"),
            ("Gleason 8+7", f"Gleason_{bottle_num}_8_7"),
            ("Gleason 8+8", f"Gleason_{bottle_num}_8_8"),
            ("Gleason 8+9", f"Gleason_{bottle_num}_8_9"),
            ("Gleason 9+9", f"Gleason_{bottle_num}_9_9")
        ]
        
        # Create frame for regular fields
        fields_frame = CTkFrame(tab, fg_color="white")
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add regular fields
        for i, (label, key) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            CTkLabel(fields_frame, text=label+":", font=("Arial", 12, "bold"), 
                    text_color="#222").grid(row=row, column=col, sticky="w", padx=10, pady=4)
            entry = CTkEntry(fields_frame, width=200, font=("Arial", 12))
            entry.grid(row=row, column=col+1, padx=10, pady=4, sticky="ew")
            self.entries[key] = entry
        
        # Create frame for Gleason scores
        gleason_frame = CTkFrame(tab, fg_color="white")
        gleason_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add Gleason score fields
        CTkLabel(gleason_frame, text="Gleason Scores:", font=("Arial", 14, "bold"), 
                text_color="#222").grid(row=0, column=0, columnspan=4, pady=10)
        
        for i, (label, key) in enumerate(gleason_fields):
            row = (i // 4) + 1
            col = (i % 4) * 2
            CTkLabel(gleason_frame, text=label+":", font=("Arial", 11, "bold"), 
                    text_color="#222").grid(row=row, column=col, sticky="w", padx=5, pady=2)
            entry = CTkEntry(gleason_frame, width=80, font=("Arial", 11))
            entry.grid(row=row, column=col+1, padx=5, pady=2, sticky="ew")
            self.entries[key] = entry

    def load_second_bottles_data(self):
        """Load existing data from SecondBottles table"""
        cursor = self.db.connection.cursor()
        
        # First get the patientsside_id from PatientsSide table
        cursor.execute("SELECT id FROM PatientsSide WHERE patientsinfo_id=?", (self.patientsinfo_id,))
        patientsside_id_result = cursor.fetchone()
        
        if not patientsside_id_result:
            showinfo("Info", "No prostate zone data found. Please complete second page first.")
            self.destroy()
            return
            
        patientsside_id = patientsside_id_result[0]
        
        # Now query SecondBottles
        cursor.execute("SELECT * FROM SecondBottles WHERE patientsside_id=?", (patientsside_id,))
        row = cursor.fetchone()
        
        if not row:
            # No existing data - this is fine, user can create new data
            showinfo("Info", "No existing additional biopsy data found. You can enter new data.")
            return
            
        # Get column names
        cursor.execute("SELECT * FROM SecondBottles LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        
        # Create data dictionary
        data = dict(zip(columns, row))
        
        # Populate the entry fields
        for key, entry_widget in self.entries.items():
            value = data.get(key, "")
            if value is None:
                value = ""
                
            if hasattr(entry_widget, 'delete') and hasattr(entry_widget, 'insert'):
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, str(value))

    def save_second_bottles(self):
        """Save the updated data to SecondBottles table"""
        updated_fields = {}
        
        # Collect data from all entry fields
        for key, entry_widget in self.entries.items():
            if hasattr(entry_widget, 'get'):
                updated_fields[key] = entry_widget.get()
        
        try:
            # First get the patientsside_id from PatientsSide table
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT id FROM PatientsSide WHERE patientsinfo_id=?", (self.patientsinfo_id,))
            patientsside_id_result = cursor.fetchone()
            
            if not patientsside_id_result:
                showerror("Error", "No prostate zone data found. Please complete second page first.")
                return
                
            patientsside_id = patientsside_id_result[0]
            
            # Check if record exists
            cursor.execute("SELECT COUNT(*) FROM SecondBottles WHERE patientsside_id=?", (patientsside_id,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Update existing record
                self.db.update_second_bottles(patientsside_id, updated_fields)
                showinfo("Success", "Additional biopsy bottles data updated successfully!")
            else:
                # Insert new record
                updated_fields['patientsside_id'] = patientsside_id
                updated_fields['firstbottles_id'] = patientsside_id  # Assuming same as patientsside_id
                
                columns = ', '.join(updated_fields.keys())
                placeholders = ', '.join(['?' for _ in updated_fields])
                sql = f"INSERT INTO SecondBottles ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(updated_fields.values()))
                self.db.connection.commit()
                showinfo("Success", "Additional biopsy bottles data saved successfully!")
            
            # Call update callback to refresh parent table
            if self.update_callback:
                self.update_callback()
                
            self.destroy()
            
        except Exception as e:
            showerror("Error", f"Failed to save additional biopsy bottles data: {e}")
@staticmethod
def open_dicom_popup(parent):
    # Professional color scheme
    ACCENT = "#059669"
    CARD_BG = "#fff"
    TEXT_DARK = "#222"
    BTN_TEXT = "#fff"
    BORDER = "#e2e8f0"
    
    top = Toplevel(parent)
    top.title("DICOM to PNG Converter")
    top.geometry("600x500")
    top.config(bg=ACCENT)
    top.resizable(False, False)

    dicom_img = {'img': None}

    # Header
    header = CTkLabel(top, text="DICOM to PNG Converter", font=("Arial Black", 22, "bold"),
                      text_color=ACCENT, fg_color=CARD_BG, corner_radius=10)
    header.pack(pady=(18, 8), padx=0, fill="x")

    # Card frame for content
    card = CTkFrame(top, fg_color=CARD_BG, corner_radius=18, border_width=2, border_color=BORDER)
    card.pack(padx=30, pady=10, fill="both", expand=True)

    # Image preview
    image_label = CTkLabel(card, text="No image loaded", fg_color=CARD_BG, text_color=TEXT_DARK, font=("Arial", 14))
    image_label.grid(row=0, column=0, columnspan=4, pady=(18, 8), padx=50)

    # File selection button
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("DICOM files", "*.dcm")])
        if file_path:
            try:
                import pydicom
                from PIL import Image
                ds = pydicom.dcmread(file_path)
                
                # Check if the DICOM file has pixel data
                if not hasattr(ds, 'pixel_array'):
                    showerror("Error", "The selected DICOM file doesn't contain image data")
                    return
                    
                try:
                    arr = ds.pixel_array
                    img = Image.fromarray(arr)
                    img = img.convert("L") if img.mode != "L" else img
                    dicom_img['img'] = img
                    show_image(img)
                    width_entry.delete(0, 'end')
                    height_entry.delete(0, 'end')
                    width_entry.insert(0, img.width)
                    height_entry.insert(0, img.height)
                except Exception as e:
                    showerror("Error", f"Failed to process DICOM image: {str(e)}")
            except Exception as e:
                showerror("Error", f"Failed to read DICOM file: {str(e)}")
    top.state("normal")
    top.focus_force()
    select_btn = CTkButton(card, text="Select DICOM File", font=("Arial Black", 14),
                          fg_color=ACCENT, text_color=BTN_TEXT, hover_color="#047857",
                          corner_radius=10, command=select_file, width=160, height=36)
    select_btn.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=10, sticky="w")

    # Resize controls
    CTkLabel(card, text="Width:", font=("Arial", 13, "bold"), text_color=TEXT_DARK, fg_color=CARD_BG).grid(row=2, column=0, pady=6, padx=(10,2), sticky="e")
    width_entry = CTkEntry(card, width=70, font=("Arial", 13),text_color="#000", fg_color="#f8fafc", border_color=ACCENT, border_width=2)
    width_entry.grid(row=2, column=1, pady=6, padx=(0,10), sticky="w")
    width_entry.insert(0, "Width")
    width_entry.bind("<FocusIn>", lambda e: width_entry.delete(0, 'end') if width_entry.get() == "Width" else None)

    CTkLabel(card, text="Height:", font=("Arial", 13, "bold"), text_color=TEXT_DARK, fg_color=CARD_BG).grid(row=2, column=2, pady=6, padx=(10,2), sticky="e")
    height_entry = CTkEntry(card, width=70, font=("Arial", 13),text_color="#000", fg_color="#f8fafc", border_color=ACCENT, border_width=2)
    height_entry.grid(row=2, column=3, pady=6, padx=(0,10), sticky="w")
    height_entry.insert(0, "Height")
    height_entry.bind("<FocusIn>", lambda e: height_entry.delete(0, 'end') if height_entry.get() == "Height" else None)

    # Resize button
    def resize_image():
        if dicom_img['img'] is None:
            showerror("Error", "No image loaded.")
            return
        try:
            w = int(width_entry.get())
            h = int(height_entry.get())
            if w <= 0 or h <= 0:
                showerror("Error", "Width and height must be positive numbers")
                return
            img_resized = dicom_img['img'].resize((w, h))
            show_image(img_resized)
            dicom_img['img'] = img_resized
        except ValueError:
            showerror("Error", "Please enter valid numbers for width and height")
        except Exception as e:
            showerror("Error", f"Resize failed: {str(e)}")

    def save_png():
        if dicom_img['img'] is None:
            showerror("Error", "No image loaded.")
            return
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png", 
                filetypes=[("PNG files", "*.png")]
            )
            if file_path:
                dicom_img['img'].save(file_path)
                showinfo("Saved", f"Image saved as {file_path}")
        except Exception as e:
            showerror("Error", f"Failed to save image: {str(e)}")
        top.state("normal")
        top.focus_force()

    resize_btn = CTkButton(card, text="Resize", font=("Arial Black", 13),
                          fg_color=ACCENT, text_color=BTN_TEXT, hover_color="#047857",
                          corner_radius=10, command=resize_image, width=90, height=32)
    resize_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10), padx=10, sticky="w")

    # Save as PNG button
    def save_png():
        if dicom_img['img'] is None:
            showinfo("Error", "No image loaded.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            dicom_img['img'].save(file_path)
            showinfo("Saved", f"Image saved as {file_path}")
        top.state("normal")
        top.focus_force()

    save_btn = CTkButton(card, text="Save as PNG", font=("Arial Black", 13),
                        fg_color=ACCENT, text_color=BTN_TEXT, hover_color="#047857",
                        corner_radius=10, command=save_png, width=120, height=32)
    save_btn.grid(row=3, column=2, columnspan=2, pady=(0, 10), padx=10, sticky="e")

    # Image preview function
    def show_image(img):
        img_resized = img.copy()
        # Keep aspect ratio for preview
        max_size = 220
        w, h = img.size
        scale = min(max_size/w, max_size/h, 1)
        new_w, new_h = int(w*scale), int(h*scale)
        img_resized = img_resized.resize((new_w, new_h))
        img_tk = CTkImage(light_image=img_resized, dark_image=img_resized, size=img_resized.size)
        image_label.configure(image=img_tk, text="")
        image_label.image = img_tk
        top.state("normal")
        top.focus_force()

    # Grid config for spacing
    card.grid_rowconfigure(0, weight=1)
    card.grid_rowconfigure(1, weight=0)
    card.grid_rowconfigure(2, weight=0)
    card.grid_rowconfigure(3, weight=0)
    card.grid_columnconfigure((0,1,2,3), weight=1)


# Backward compatibility function
def hospital_popup(parent, current_value, on_select_callback):
    """Legacy function for backward compatibility"""
    return HospitalPopup(parent, current_value, on_select_callback)