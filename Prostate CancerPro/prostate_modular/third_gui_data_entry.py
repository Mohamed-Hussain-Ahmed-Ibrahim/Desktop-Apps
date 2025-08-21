from docxtpl import DocxTemplate
from tkinter.messagebox import askquestion, showinfo
from customtkinter import CTkButton, CTkLabel, CTkFrame, CTkImage
from customtkinter import CTkEntry, CTkCheckBox, CTkTabview, CTkScrollableFrame
from tkinter import  W, Toplevel, filedialog
from PIL import Image
from prostate_modular.utils import CustomCTkComboBox
from prostate_modular.logic_for_third import ThirdLogic
from tkinter.messagebox import showerror
from prostate_modular.constant import entries_3, entries_4
from prostate_modular.backend import Backend
class ThirdDataEntryGUI(CTkFrame):
    def __init__(self, parent, controller, entries_1=None, entries_2=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Use passed dictionaries directly; initialize if None
        self.entries_1 = entries_1 
        self.entries_2 = entries_2 
        
        # These are specific to this GUI, so they should be fresh copies
        self.entries_3 = entries_3
        self.entries_4 = entries_4
        self.backend = Backend()
        self.logic = ThirdLogic(self)
        self.colors = {
            'primary': '#1e3a8a',
            'secondary': '#3b82f6',
            'accent': '#10b981',
            'success': '#059669',
            'warning': '#f59e0b',
            'danger': '#dc2626',
            'light': '#f8fafc',
            'dark': '#1e293b',
            'white': '#ffffff',
            'sidebar': '#0f172a',
            'card': '#ffffff',
            'border': '#e2e8f0',
            'text_dark': '#1f2937',
            'text_light': '#6b7280'
        }
        self.setup_images()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.side_bar()
        self.third_page()

    def setup_images(self):
        try:
            logo_image = Image.open("Logo/main/Best11.png")
            self.logo_img = CTkImage(dark_image=logo_image, light_image=logo_image, size=(150, 150))
            ana_image = Image.open("Logo/side bar/stat2.png")
            self.analytics_img = CTkImage(dark_image=ana_image, light_image=ana_image, size=(80, 60))
            pat_image = Image.open("Logo/side bar/pat11.png")
            self.patient_img = CTkImage(dark_image=pat_image, light_image=pat_image, size=(100, 60))
        except Exception as e:
            showerror(f"Warning: Could not load some images: {e}")
            self.logo_img = None
            self.analytics_img = None
            self.patient_img = None

    def side_bar(self):
        self.sidebar_frame = CTkFrame(self, fg_color=self.colors['sidebar'], corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        # Logo
        if self.logo_img:
            logo_label = CTkButton(self.sidebar_frame, text="", image=self.logo_img, compound='left', fg_color="transparent", width=200, height=150, font=("Arial-BoldMT", 12), hover_color=self.colors['primary'])
            logo_label.grid(row=0, column=0, pady=(20, 10))
            logo_label.configure(state="disabled")
        # Title
        title_label = CTkLabel(self.sidebar_frame, text="Biopsy Bottles 1-10", font=("Arial Black", 16, "bold"), text_color=self.colors['white'])
        title_label.grid(row=1, column=0, pady=(0, 20))
        # Navigation buttons
        self.create_nav_button("Statistics", self.analytics_img, row=2, command=self.show_statistics)
        self.create_nav_button("Patients", self.patient_img, row=3, command=self.go_to_main_window)
        self.create_nav_button("Next 11-20", None, row=4, command=self.controller.display_fourth_data_entry_gui)
        # Progress indicator
        progress_label = CTkLabel(self.sidebar_frame, text="Step 3 of 4", font=("Arial", 12), text_color=self.colors['accent'])
        progress_label.grid(row=5, column=0, pady=(20, 10))
        # Progress bar
        self.progress_frame = CTkFrame(self.sidebar_frame, fg_color=self.colors['dark'], height=8)
        self.progress_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar = CTkFrame(self.progress_frame, fg_color=self.colors['accent'], width=187)
        self.progress_bar.place(relx=0, rely=0, relwidth=0.75, relheight=1)
        # Bottom section
        bottom_frame = CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=7, column=0, sticky="s", pady=20)
        help_btn = CTkButton(bottom_frame, text="Help", fg_color=self.colors['accent'], text_color=self.colors['white'], hover_color=self.colors['success'], corner_radius=8, command=self.show_help)
        help_btn.pack(pady=5)

    def create_nav_button(self, text, image, row, command=None):
        btn = CTkButton(self.sidebar_frame, text=text, image=image, compound='left', fg_color="transparent", hover_color=self.colors['primary'], corner_radius=10, command=command, text_color=self.colors['white'])
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="w")

    def show_statistics(self):
        """Show statistics dashboard"""
        from tkinter.messagebox import showwarning
        showwarning("Statistics", "you should return to main window to see statistics")

    def go_to_main_window(self):
        """Navigate to main window"""
        # Clear all widgets from the root window
        for widget in self.master.winfo_children():
            widget.destroy()
        # Configure the master window grid properly
        self.master.grid_columnconfigure(0, weight=0)  # Sidebar column
        self.master.grid_columnconfigure(1, weight=1)  # Main content column
        self.master.grid_rowconfigure(0, weight=1)
        # Create new main window instance
        from prostate_modular.main_window import MainWindow
        main_window = MainWindow(self.master)
        # Set up the interface exactly like the welcome GUI does
        main_window.side_bar()
        main_window.display_search_patients()

    def show_help(self):
        from tkinter.messagebox import showinfo
        help_text = (
            "Biopsy Bottles 1-10 Help\n\n"
            "This section allows you to enter detailed biopsy data for bottles 1-10.\n\n"
            "Navigation:\n"
            "• Statistics: View patient statistics and analytics\n"
            "• Patients: Return to main dashboard\n"
            "• Next 11-20: Proceed to bottles 11-20 data entry\n\n"
            "Data Entry:\n"
            "• For each bottle, enter the site of biopsy, US risk features, number of cores, and pathology findings.\n"
            "• Use the dropdowns and entry fields for each parameter.\n"
            "• Ensure all required fields are filled for accurate record keeping.\n\n"
            "Tips:\n"
            "• Double-check each entry before proceeding.\n"
            "• Use the Export button to save or print the current data.\n"
            "• Use the sidebar to quickly navigate between sections.\n"
        )
        showinfo("Help - Biopsy Bottles 1-10", help_text)

    def go_to_fourth(self):
        from prostate_modular.fourth_gui_data_entry import FourthDataEntryGUI
        try:
            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)
            self.master._third_data_entry = FourthDataEntryGUI(self.master, self.controller, self.entries_1, self.entries_2)
            self.master._third_data_entry.grid(row=0, column=0, sticky="nsew")
            self.master.update()
        except Exception as e:
            showerror("Error creating ThirdDataEntryGUI:", e)
        
    def clear_entries(self):
        # Reset entry fields and other variables
        self.entries_1={key: None for key in self.entries_1}
        self.entries_1["Image"] = "{{Image}}"
        self.entries_1["Hospital"] = self.hospital
        for i in range(1, 21):
            self.entries_3[f"ca_prostate_{i}"] = 0
        self.check_box_1=[]
        self.check_box_2=[]
        self.check_box_3=[]
        self.check_box_4=[]
        self.check_box_5=[]
        self.check_box_6=[]
        self.check_box_7=[]
        self.check_box_8=[]
        self.check_box_9=[]
        self.check_box_10=[]
        self.check_box_11=[]
        self.check_box_12=[]
        self.check_box_13=[]
        self.check_box_14=[]
        self.check_box_15=[]
        self.check_box_16=[]
        self.check_box_17=[]
        self.check_box_18=[]
        self.check_box_19=[]
        self.check_box_20=[]

    def save_to_FirstBottles(self, patientsinfo_id):
        from prostate_modular.database import DatabaseManager
        db = DatabaseManager("DB/Informations.db")
        try:
            self.entries_3["Image"] = "temp/2.png"
            with open("temp/2.png", "rb") as img_file:
                self.entries_3["Image"] = img_file.read()
        except Exception as e:
            self.entries_3["Image"] = None
            showerror("Error reading image:", e)
        db.insert_into_FirstBottles(patientsinfo_id, self.entries_3)
        db.update_table()
        self.go_to_main_window()
    def third_page(self):
        for W in self.place_slaves():
            W.place_forget()
        # Configure grid for main content area (besides sidebar)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Main content frame
        content_frame = CTkFrame(self, fg_color=self.colors['card'], corner_radius=16)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=30)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Header label
        header = CTkLabel(content_frame, text="Biopsy Bottles 1-10", font=("Arial Black", 20, "bold"), text_color=self.colors['primary'])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Tabview for bottles
        self.tab_view_bottles_1 = CTkTabview(
            content_frame,
            fg_color=self.colors['light'],
            border_color=self.colors['primary'],
            border_width=2,
            corner_radius=12,
            cursor='arrow',
        )
        self.tab_view_bottles_1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_view_bottles_1.add("Bottle-1")
        self.bottle_1()
        self.tab_view_bottles_1.add("Bottle-2")
        self.bottle_2()
        self.tab_view_bottles_1.add("Bottle-3")
        self.bottle_3()
        self.tab_view_bottles_1.add("Bottle-4")
        self.bottle_4()
        self.tab_view_bottles_1.add("Bottle-5")
        self.bottle_5()
        self.tab_view_bottles_1.add("Bottle-6")
        self.bottle_6()
        self.tab_view_bottles_1.add("Bottle-7")
        self.bottle_7()
        self.tab_view_bottles_1.add("Bottle-8")
        self.bottle_8()
        self.tab_view_bottles_1.add("Bottle-9")
        self.bottle_9()
        self.tab_view_bottles_1.add("Bottle-10")
        self.bottle_10()

        # Next 11-20 button at the bottom
        next_btn = CTkButton(
            content_frame,
            text="Next 11-20",
            width=350,
            height=48,
            font=("Arial Black", 16),
            fg_color=self.colors['accent'],
            text_color=self.colors['white'],
            hover_color=self.colors['success'],
            corner_radius=10,
            command=self.go_to_fourth  # Ensure this calls the controller method
        )
        next_btn.grid(row=2, column=0, sticky="ew", pady=(20, 0), padx=10)

    def export_third(self):
        from docxtpl import DocxTemplate, InlineImage
        from docx.shared import Mm
        import os
        # Ensure the temp directory exists
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Load the appropriate template based on the hospital
        if self.entries_1["Hospital"] == 'life':
            doc = DocxTemplate("DOC/Life/3.docx")
        else:
            doc = DocxTemplate("DOC/Kidney and Tract/3.docx")
        
        # Prepare the data for the template
        self.entries_3["Lesions"] = self.entries_1.get("Lesions", "")
        self.entries_3["Degree"] = self.entries_1.get("Degree", "")
        self.entries_3["DRE"] = self.entries_1.get("DRE", "")
        
        # Clean up entries (replace None with empty string)
        last_entry = {key: '' if v is None else v for key, v in self.entries_3.items()}
        
        # Set up the image path
        image_path = "temp/2.png"
        
        try:
            # Create the image object only if the image exists
            if os.path.exists(image_path):
                marked_inline_image = InlineImage(doc, image_path, width=Mm(136), height=Mm(32))
                last_entry["Image"]=marked_inline_image
                context = {
                    "entries": last_entry
                }
            else:
                context = {
                    "entries": last_entry
                }
            
            # Render the document with the context
            doc.render(context)
            
            # Save the rendered document
            output_path = "temp/3.docx"
            doc.save(output_path)
            
            # Collect all bottle data before inserting into DB
            for i in range(1, 11):
                get_data_func = getattr(self, f'get_data_frame_{i}', None)
                if get_data_func:
                    get_data_func()
            
            # Remove temporary keys
            del self.entries_3['Lesions']
            del self.entries_3['Degree']
            del self.entries_3['DRE']
            
            # Insert into database
            try:
                patientsinfo_id = self.entries_1.get('US')
                if patientsinfo_id:
                    self.save_to_FirstBottles(patientsinfo_id)
            except Exception as e:
                showerror("Database Error", f"Failed to insert data: {e}")
            
            # Combine all documents
            self.combine_all_docx(["temp/1.docx", "temp/2.docx", output_path])
            showinfo("Complete", "Data exported successfully!")
            
        except Exception as e:
            showerror("Export Error", f"Failed to export document: {str(e)}")        

    def get_data_frame_1(self):
        self.entries_3["Site_of_biopsy_1"] = self.entry_bottles1.get()
        self.entries_3["US_risk_features_1"] = self.checkbox_option_risk1.get()
        self.entries_3["no_of_cores_1"] = self.entry_no_of_cores1.get()
        self.entries_3["BPH_1"] = self.entry_bph1.get()
        self.entries_3["Prostatitis_1"] = self.entry_Prostatitis1.get()
        self.entries_3["Atrophy_1"] = self.entry_A1.get()
        self.entries_3["BasalCellHqPerPlasiq_1"] = self.entry_BHPPlasiq_1.get()
        self.entries_3["PIN_1"] = self.entry_pin_1.get()
        self.entries_3["ca_grade_1"]= self.entry_grade_1.get()
    def bottle_1(self):
        self.one_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-1"), height=1000, fg_color="transparent", corner_radius=0)
        self.one_frame.pack(fill="both", expand=True)
        # Section header for Bottle 1
        section_header = CTkLabel(self.one_frame, text="Bottle 1", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        # Grouped entry fields in a card-like frame
        entry_card = CTkFrame(self.one_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        # Row 1: Site of biopsy
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles1.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles1.insert(0, "Left Apex and Apical Horn")
        # Row 2: US Risk Features
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk1 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk1.set("low")
        self.checkbox_option_risk1.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        # Row 3: no. of Cores
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores1.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores1.insert(0, "2")
        # Row 4: BPH
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph1.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        # Row 5: Prostatitis
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis1.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        # Row 6: Atrophy
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A1.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        # Row 7: Basal Cell Hq Per Plasiq
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_1.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        # Row 8: PIN
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_1.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        # Row 9: Cancer Prostate
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk1 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 1))
        self.option_risk1.set("No")
        self.option_risk1.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_1 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_1.grid(row=9, column=1, padx=12, pady=6, sticky=W)
        # Gleason Patterns frame (visually separated)
        self.gleason_frame_1 = CTkFrame(self.one_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_1.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_1, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_1, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_1", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(1, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        # Buttons row (centered)
        button_row = CTkFrame(self.one_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button21 = CTkButton(button_row, text="Get Bottle-1", width=150, height=40, command=self.get_data_frame_1, fg_color="#10b981")
        button21.pack(side="left", padx=12)
        button41 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button41.pack(side="left", padx=12)
    def get_data_frame_2(self):
        self.entries_3["Site_of_biopsy_2"] = self.entry_bottles2.get()
        self.entries_3["US_risk_features_2"] = self.checkbox_option_risk2.get()
        self.entries_3["no_of_cores_2"] = self.entry_no_of_cores2.get()
        self.entries_3["BPH_2"] = self.entry_bph2.get()
        self.entries_3["Prostatitis_2"] = self.entry_Prostatitis2.get()
        self.entries_3["Atrophy_2"] = self.entry_A2.get()
        self.entries_3["BasalCellHqPerPlasiq_2"] = self.entry_BHPPlasiq_2.get()
        self.entries_3["PIN_2"] = self.entry_pin_2.get()
        self.entries_3["ca_grade_2"]= self.entry_grade_2.get()
    def bottle_2(self):
        self.two_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-2"), height=1000, fg_color="transparent", corner_radius=0)
        self.two_frame.pack(fill="both", expand=True)

        # Section header for Bottle 2
        section_header = CTkLabel(self.two_frame, text="Bottle 2", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        # Grouped entry fields in a card-like frame
        entry_card = CTkFrame(self.two_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        # Row 1: Site of biopsy
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles2.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles2.insert(0, "Right Apex and Apical Horn")

        # Row 2: US Risk Features
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk2 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk2.set("low")
        self.checkbox_option_risk2.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        # Row 3: no. of Cores
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores2.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores2.insert(0, "2")

        # Row 4: BPH
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph2.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        # Row 5: Prostatitis
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis2.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        # Row 6: Atrophy
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A2.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        # Row 7: Basal Cell Hq Per Plasiq
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_2.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        # Row 8: PIN
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_2.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        # Row 9: Cancer Prostate
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk2 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 2))
        self.option_risk2.set("No")
        self.option_risk2.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_2 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_2.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        # Gleason Patterns frame
        self.gleason_frame_2 = CTkFrame(self.two_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_2.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_2, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_2, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_2", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(2, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()

        # Buttons row
        button_row = CTkFrame(self.two_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button22 = CTkButton(button_row, text="Get Bottle-2", width=150, height=40, command=self.get_data_frame_2, fg_color="#10b981")
        button22.pack(side="left", padx=12)
        button42 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button42.pack(side="left", padx=12)

    def get_data_frame_3(self):
        self.entries_3["Site_of_biopsy_3"] = self.entry_bottles3.get()
        self.entries_3["US_risk_features_3"] = self.checkbox_option_risk3.get()
        self.entries_3["no_of_cores_3"] = self.entry_no_of_cores3.get()
        self.entries_3["BPH_3"] = self.entry_bph3.get()
        self.entries_3["Prostatitis_3"] = self.entry_Prostatitis3.get()
        self.entries_3["Atrophy_3"] = self.entry_A3.get()
        self.entries_3["BasalCellHqPerPlasiq_3"] = self.entry_BHPPlasiq_3.get()
        self.entries_3["PIN_3"] = self.entry_pin_3.get()
        self.entries_3["ca_grade_3"] = self.entry_grade_3.get()
    def bottle_3(self):
        self.three_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-3"), height=1000, fg_color="transparent", corner_radius=0)
        self.three_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.three_frame, text="Bottle 3", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.three_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles3.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles3.insert(0, "Left Mid-Prostate Lateral,Anterior")
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk3 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk3.set("low")
        self.checkbox_option_risk3.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores3.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores3.insert(0, "2")
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph3.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis3.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A3.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_3.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_3.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk3 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 3))
        self.option_risk3.set("No")
        self.option_risk3.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_3 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_3.grid(row=9, column=1, padx=12, pady=6, sticky=W)
        self.gleason_frame_3 = CTkFrame(self.three_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_3.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_3, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_3, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_3", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(3, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.three_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button23 = CTkButton(button_row, text="Get Bottle-3", width=150, height=40, command=self.get_data_frame_3, fg_color="#10b981")
        button23.pack(side="left", padx=12)
        button43 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button43.pack(side="left", padx=12)

    def get_data_frame_4(self):
        self.entries_3["Site_of_biopsy_4"] = self.entry_bottles4.get()
        self.entries_3["US_risk_features_4"] = self.checkbox_option_risk4.get()
        self.entries_3["no_of_cores_4"] = self.entry_no_of_cores4.get()
        self.entries_3["BPH_4"] = self.entry_bph4.get()
        self.entries_3["Prostatitis_4"] = self.entry_Prostatitis4.get()
        self.entries_3["Atrophy_4"] = self.entry_A4.get()
        self.entries_3["BasalCellHqPerPlasiq_4"] = self.entry_BHPPlasiq_4.get()
        self.entries_3["PIN_4"] = self.entry_pin_4.get()
        self.entries_3["ca_grade_4"]= self.entry_grade_4.get()
    def bottle_4(self):
        self.four_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-4"), height=1000, fg_color="transparent", corner_radius=0)
        self.four_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.four_frame, text="Bottle 4", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.four_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles4.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles4.insert(0, "Right Mid-Prostate Lateral, Anterior")
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk4 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk4.set("low")
        self.checkbox_option_risk4.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores4.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores4.insert(0, "2")
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph4.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis4.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A4.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_4.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_4.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk4 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 4))
        self.option_risk4.set("No")
        self.option_risk4.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_4 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_4.grid(row=9, column=1, padx=12, pady=6, sticky=W)
        self.gleason_frame_4 = CTkFrame(self.four_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_4.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_4, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_4, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_4", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(4, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.four_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button24 = CTkButton(button_row, text="Get Bottle-4", width=150, height=40, command=self.get_data_frame_4, fg_color="#10b981")
        button24.pack(side="left", padx=12)
        button44 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button44.pack(side="left", padx=12)

    def get_data_frame_5(self):
        self.entries_3["Site_of_biopsy_5"] = self.entry_bottles5.get()
        self.entries_3["US_risk_features_5"] = self.checkbox_option_risk5.get()
        self.entries_3["no_of_cores_5"] = self.entry_no_of_cores5.get()
        self.entries_3["BPH_5"] = self.entry_bph5.get()
        self.entries_3["Prostatitis_5"] = self.entry_Prostatitis5.get()
        self.entries_3["Atrophy_5"] = self.entry_A5.get()
        self.entries_3["BasalCellHqPerPlasiq_5"] = self.entry_BHPPlasiq_5.get()
        self.entries_3["PIN_5"] = self.entry_pin_5.get()
        self.entries_3["ca_grade_5"]= self.entry_grade_5.get()
    def bottle_5(self):
        self.five_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-5"), height=1000, fg_color="transparent", corner_radius=0)
        self.five_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.five_frame, text="Bottle 5", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.five_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles5.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles5.insert(0, "Left Base Postero-Medial, Lateral")
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk5 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk5.set("low")
        self.checkbox_option_risk5.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores5.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores5.insert(0, "2")
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph5.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis5.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A5.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_5.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_5.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk5 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 5))
        self.option_risk5.set("No")
        self.option_risk5.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_5 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_5.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_5 = CTkFrame(self.five_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_5.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_5, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_5, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_5", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(5, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.five_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button25 = CTkButton(button_row, text="Get Bottle-5", width=150, height=40, command=self.get_data_frame_5, fg_color="#10b981")
        button25.pack(side="left", padx=12)
        button45 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button45.pack(side="left", padx=12)

    def get_data_frame_6(self):
        self.entries_3["Site_of_biopsy_6"] = self.entry_bottles6.get()
        self.entries_3["US_risk_features_6"] = self.checkbox_option_risk6.get()
        self.entries_3["no_of_cores_6"] = self.entry_no_of_cores6.get()
        self.entries_3["BPH_6"] = self.entry_bph6.get()
        self.entries_3["Prostatitis_6"] = self.entry_Prostatitis6.get()
        self.entries_3["Atrophy_6"] = self.entry_A6.get()
        self.entries_3["BasalCellHqPerPlasiq_6"] = self.entry_BHPPlasiq_6.get()
        self.entries_3["PIN_6"] = self.entry_pin_6.get()
        self.entries_3["ca_grade_6"]= self.entry_grade_6.get()
    def bottle_6(self):
        self.six_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-6"), height=1000, fg_color="transparent", corner_radius=0)
        self.six_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.six_frame, text="Bottle 6", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.six_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles6.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        self.entry_bottles6.insert(0, "Right Base Postero-Medial, Lateral")
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk6 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk6.set("low")
        self.checkbox_option_risk6.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores6.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores6.insert(0, "2")
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph6.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis6.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A6.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_6.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_6.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk6 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 6))
        self.option_risk6.set("No")
        self.option_risk6.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_6 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_6.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_6 = CTkFrame(self.six_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_6.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_6, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_6, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_6", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(6, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.six_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button26 = CTkButton(button_row, text="Get Bottle-6", width=150, height=40, command=self.get_data_frame_6, fg_color="#10b981")
        button26.pack(side="left", padx=12)
        button46 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button46.pack(side="left", padx=12)

    def get_data_frame_7(self):
        self.entries_3["Site_of_biopsy_7"] = self.entry_bottles7.get()
        self.entries_3["US_risk_features_7"] = self.checkbox_option_risk7.get()
        self.entries_3["no_of_cores_7"] = self.entry_no_of_cores7.get()
        self.entries_3["BPH_7"] = self.entry_bph7.get()
        self.entries_3["Prostatitis_7"] = self.entry_Prostatitis7.get()
        self.entries_3["Atrophy_7"] = self.entry_A7.get()
        self.entries_3["BasalCellHqPerPlasiq_7"] = self.entry_BHPPlasiq_7.get()
        self.entries_3["PIN_7"] = self.entry_pin_7.get()
        self.entries_3["ca_grade_7"]= self.entry_grade_7.get()
    def bottle_7(self):
        self.seven_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-7"), height=1000, fg_color="transparent", corner_radius=0)
        self.seven_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.seven_frame, text="Bottle 7", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.seven_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles7.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk7 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk7.set("")
        self.checkbox_option_risk7.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores7.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph7.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis7.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A7.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_7.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_7.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk7 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 7))
        self.option_risk7.set("")
        self.option_risk7.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_7 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_7.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_7 = CTkFrame(self.seven_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_7.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_7, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_7, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_7", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(7, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.seven_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button27 = CTkButton(button_row, text="Get Bottle-7", width=150, height=40, command=self.get_data_frame_7, fg_color="#10b981")
        button27.pack(side="left", padx=12)
        button47 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button47.pack(side="left", padx=12)

    def get_data_frame_8(self):
        self.entries_3["Site_of_biopsy_8"] = self.entry_bottles8.get()
        self.entries_3["US_risk_features_8"] = self.checkbox_option_risk8.get()
        self.entries_3["no_of_cores_8"] = self.entry_no_of_cores8.get()
        self.entries_3["BPH_8"] = self.entry_bph8.get()
        self.entries_3["Prostatitis_8"] = self.entry_Prostatitis8.get()
        self.entries_3["Atrophy_8"] = self.entry_A8.get()
        self.entries_3["BasalCellHqPerPlasiq_8"] = self.entry_BHPPlasiq_8.get()
        self.entries_3["PIN_8"] = self.entry_pin_8.get()
        self.entries_3["ca_grade_8"]= self.entry_grade_8.get()
    def bottle_8(self):
        self.eight_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-8"), height=1000, fg_color="transparent", corner_radius=0)
        self.eight_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.eight_frame, text="Bottle 8", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.eight_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles8.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk8 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk8.set("")
        self.checkbox_option_risk8.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores8.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph8.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis8.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A8.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_8.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_8.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk8 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 8))
        self.option_risk8.set("")
        self.option_risk8.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_8 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_8.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_8 = CTkFrame(self.eight_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_8.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_8, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_8, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_8", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(8, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.eight_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button28 = CTkButton(button_row, text="Get Bottle-8", width=150, height=40, command=self.get_data_frame_8, fg_color="#10b981")
        button28.pack(side="left", padx=12)
        button48 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button48.pack(side="left", padx=12)

    def get_data_frame_9(self):
        self.entries_3["Site_of_biopsy_9"] = self.entry_bottles9.get()
        self.entries_3["US_risk_features_9"] = self.checkbox_option_risk9.get()
        self.entries_3["no_of_cores_9"] = self.entry_no_of_cores9.get()
        self.entries_3["BPH_9"] = self.entry_bph9.get()
        self.entries_3["Prostatitis_9"] = self.entry_Prostatitis9.get()
        self.entries_3["Atrophy_9"] = self.entry_A9.get()
        self.entries_3["BasalCellHqPerPlasiq_9"] = self.entry_BHPPlasiq_9.get()
        self.entries_3["PIN_9"] = self.entry_pin_9.get()
        self.entries_3["ca_grade_9"]= self.entry_grade_9.get()
    def bottle_9(self):
        self.nine_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-9"), height=1000, fg_color="transparent", corner_radius=0)
        self.nine_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.nine_frame, text="Bottle 9", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.nine_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles9.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk9 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk9.set("")
        self.checkbox_option_risk9.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores9.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph9.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis9.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A9.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_9.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_9.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk9 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 9))
        self.option_risk9.set("")
        self.option_risk9.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_9 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_9.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_9 = CTkFrame(self.nine_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_9.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_9, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_9, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_9", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(9, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.nine_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button29 = CTkButton(button_row, text="Get Bottle-9", width=150, height=40, command=self.get_data_frame_9, fg_color="#10b981")
        button29.pack(side="left", padx=12)
        button49 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button49.pack(side="left", padx=12)

    def get_data_frame_10(self):
        self.entries_3["Site_of_biopsy_10"] = self.entry_bottles10.get()
        self.entries_3["US_risk_features_10"] = self.checkbox_option_risk10.get()
        self.entries_3["no_of_cores_10"] = self.entry_no_of_cores10.get()
        self.entries_3["BPH_10"] = self.entry_bph10.get()
        self.entries_3["Prostatitis_10"] = self.entry_Prostatitis10.get()
        self.entries_3["Atrophy_10"] = self.entry_A10.get()
        self.entries_3["BasalCellHqPerPlasiq_10"] = self.entry_BHPPlasiq_10.get()
        self.entries_3["PIN_10"] = self.entry_pin_10.get()
        self.entries_3["ca_grade_10"]= self.entry_grade_10.get()
    def bottle_10(self):
        self.ten_frame = CTkScrollableFrame(self.tab_view_bottles_1.tab("Bottle-10"), height=1000, fg_color="transparent", corner_radius=0)
        self.ten_frame.pack(fill="both", expand=True)
        section_header = CTkLabel(self.ten_frame, text="Bottle 10", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        entry_card = CTkFrame(self.ten_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles10.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk10 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk10.set("")
        self.checkbox_option_risk10.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores10.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph10.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis10.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A10.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_10.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_10.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk10 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 10))
        self.option_risk10.set("")
        self.option_risk10.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_10 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_10.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_10 = CTkFrame(self.ten_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_10.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_10, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_10, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_10", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(10, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        button_row = CTkFrame(self.ten_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button30 = CTkButton(button_row, text="Get Bottle-10", width=150, height=40, command=self.get_data_frame_10, fg_color="#10b981")
        button30.pack(side="left", padx=12)
        button50 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_third)
        button50.pack(side="left", padx=12)
        
    def combine_all_docx(self, files_list):
        import os
        """
        Combine multiple DOCX files into one and save it.
        
        Args:
            files_list: List of paths to DOCX files to combine
            
        Returns:
            None, but shows success/error message to user
        """
        try:
            # First validate input files exist
            for file_path in files_list:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Input file not found: {file_path}")

            # Combine documents
            from docxcompose.composer import Composer
            from docx import Document as Document_compose
            
            master_doc = Document_compose(files_list[0])
            composer = Composer(master_doc)
            
            for file_path in files_list[1:]:
                doc_temp = Document_compose(file_path)
                composer.append(doc_temp)

            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx")],
                title="Save Combined Document As"
            )
            
            if not file_path:  # User cancelled
                return

            # Create directory structure if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            composer.save(file_path)

            # Also save to patient subfolder
            try:
                patient_name = self.entries_1.get("Name", "Unknown")
                patient_folder = self.backend.create_patient_subfolder(patient_name)
                if not os.path.exists(patient_folder):
                    os.makedirs(patient_folder)
                    
                output_path = os.path.join(patient_folder, "prostate.docx")
                composer.save(output_path)
                
                showinfo("Success", f"Data exported successfully to:\n{output_path}")
                
            except Exception as e:
                showerror("Backup Save Error", 
                        f"Document saved to {file_path} but failed to save to patient folder:\n{str(e)}")

        except FileNotFoundError as e:
            showerror("File Error", f"Could not combine documents: {str(e)}")
        except Exception as e:
            showerror("Error", f"Failed to export document: {str(e)}")
    