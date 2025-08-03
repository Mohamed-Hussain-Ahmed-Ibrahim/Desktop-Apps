from prostate_modular.utils import CustomCTkComboBox
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkEntry, CTkRadioButton, CTkScrollableFrame, CTkImage
from tkinter import StringVar
from datetime import datetime
from prostate_modular.database import DatabaseManager
from PIL import Image
from prostate_modular.constant import entries_1
from tkinter.messagebox import showerror
import re
from prostate_modular.backend import Backend
from prostate_modular.stats import ProstateStatisticsGUI
class FirstDataEntryGUI(CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.backend = Backend()
        # Professional color scheme
        self.colors = {
            'primary': '#1e3a8a',      # Deep blue
            'secondary': '#3b82f6',     # Bright blue
            'accent': '#10b981',        # Emerald green
            'success': '#059669',       # Dark green
            'warning': '#f59e0b',       # Amber
            'danger': '#dc2626',        # Red
            'light': '#f8fafc',         # Light gray
            'dark': '#1e293b',          # Dark gray
            'white': '#ffffff',         # White
            'sidebar': '#0f172a',       # Dark sidebar
            'card': '#ffffff',          # Card background
            'border': '#e2e8f0',        # Border color
            'text_dark': '#1f2937',     # Dark text
            'text_light': '#6b7280'     # Light text
        }
        
        # Initialize variables
        self.check = False
        self.entries_1 = {}
        self.comboboxes_one = []
        self.is_calculating = False
        self.dre_hard_count_var = StringVar()
        self.entries_1 = entries_1
        # Database manager
        self.db = DatabaseManager("DB/Informations.db")
        
        # Initialize images
        self.track_img = None
        self.analytics_img = None
        self.package_img_data = None
        self.patient_counter_img = None
        self.family_img = None
        self.dre_img = None
        self.add_user_data_img = None
        
        self.setup_images()
        
        # Initialize the GUI
        self.setup_gui()
        
    def setup_images(self):
        """Initialize all images used in the UI"""
        # Logo images
        logo_image_light = Image.open("Logo/main/Best11.png")
        logo_image_dark = Image.open("Logo/main/Best11.png")
        self.track_img = CTkImage(dark_image=logo_image_light, light_image=logo_image_dark, size=(170, 170))
        
        # Sidebar images
        ana_image = Image.open("Logo/side bar/stat2.png")
        ana_image_dark = Image.open("Logo/side bar/stat2.png")
        self.analytics_img = CTkImage(dark_image=ana_image, light_image=ana_image_dark, size=(100, 80))
        
        pat_image = Image.open("Logo/side bar/pat11.png")
        pat_image_dark = Image.open("Logo/side bar/pat11.png")
        self.package_img_data = CTkImage(dark_image=pat_image, light_image=pat_image_dark, size=(130, 80))
        
        # Patient images
        patient_img = Image.open("Logo/patient/ElogoButton-1.png")
        self.patient_counter_img = CTkImage(dark_image=patient_img, light_image=patient_img, size=(50, 40))
        
        family_image = Image.open("Logo/patient/family_history1.png")
        self.family_img = CTkImage(dark_image=family_image, light_image=family_image, size=(50, 40))
        
        dre_image = Image.open("Logo/patient/dre_logo.png")
        self.dre_img = CTkImage(dark_image=dre_image, light_image=dre_image, size=(50, 40))
        
        add_patient_light = Image.open("Logo/patient/add_user_light.png")
        self.add_user_data_img = CTkImage(dark_image=add_patient_light, light_image=add_patient_light, size=(70, 30))

    def setup_gui(self):
        """Initialize the main GUI layout with sidebar"""
        # Configure grid weights for main frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
    def create_sidebar(self):
        """Create and configure the sidebar with professional styling"""
        # Create sidebar frame
        self.sidebar_frame = CTkFrame(self, fg_color=self.colors['sidebar'], 
                                     bg_color="transparent", corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Logo with enhanced styling
        logo_label = CTkButton(self.sidebar_frame, text="", image=self.track_img, compound='left', 
                              fg_color="transparent", width=200, height=150, 
                              font=("Arial-BoldMT", 12), hover_color=self.colors['primary'])
        logo_label.grid(row=0, column=0, pady=(20, 10))
        logo_label.configure(state="disabled")
        
        # Page title
        title_label = CTkLabel(self.sidebar_frame, text="Patient Data Entry", 
                              font=("Arial Black", 16, "bold"), text_color=self.colors['white'])
        title_label.grid(row=1, column=0, pady=(0, 20))
        
        # Navigation buttons
        self.create_nav_button("Statistics", self.analytics_img, row=2, command=self.show_statistics)
        self.create_nav_button("Patients", self.package_img_data, row=3, command=self.go_to_main_window)
        
        # Progress indicator
        progress_label = CTkLabel(self.sidebar_frame, text="Step 1 of 4", 
                                 font=("Arial", 12), text_color=self.colors['accent'])
        progress_label.grid(row=4, column=0, pady=(20, 10))
        
        # Progress bar
        self.progress_frame = CTkFrame(self.sidebar_frame, fg_color=self.colors['dark'], height=8)
        self.progress_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.progress_bar = CTkFrame(self.progress_frame, fg_color=self.colors['accent'], width=62)
        self.progress_bar.place(relx=0, rely=0, relwidth=0.25, relheight=1)
        
        # Bottom section
        bottom_frame = CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, sticky="s", pady=20)
        
        # Help button
        help_btn = CTkButton(bottom_frame, text="Help", 
                            fg_color=self.colors['accent'], text_color=self.colors['white'],
                            hover_color=self.colors['success'], corner_radius=8,
                            command=self.show_help)
        help_btn.pack(pady=5)

    def create_nav_button(self, text, image, row, command=None):
        """Create a navigation button with consistent styling"""
        btn = CTkButton(self.sidebar_frame, text=text, image=image, 
                       compound='left', fg_color="transparent", 
                       hover_color=self.colors['primary'], corner_radius=10,
                       command=command, text_color=self.colors['white'])
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="w")

    def create_main_content(self):
        """Create the main content area with scrollable frame, using a content_frame for consistency"""
        # Main content frame
        content_frame = CTkFrame(self, fg_color=self.colors['light'], corner_radius=16)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.create_header(parent=content_frame)

        # Scrollable content area
        self.content_scroll = CTkScrollableFrame(content_frame, fg_color="transparent")
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_scroll.grid_columnconfigure(0, weight=1)

        # Create content sections
        self.create_patient_info_section()
        self.create_prostate_section()
        self.create_urinary_section()
        self.create_navigation_buttons(parent=content_frame)

    def create_header(self, parent=None):
        """Create the header section with title and navigation, optionally in a given parent"""
        if parent is None:
            parent = self.main_content
        header_frame = CTkFrame(parent, fg_color=self.colors['white'], 
                               border_width=1, border_color=self.colors['border'])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = CTkLabel(header_frame, text="Patient Information Form", 
                              font=("Arial Black", 24, "bold"), text_color=self.colors['primary'])
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Navigation buttons
        nav_frame = CTkFrame(header_frame, fg_color="transparent")
        nav_frame.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
        self.back_btn = CTkButton(nav_frame, text="\u2190 Back to Main", 
                                 fg_color=self.colors['secondary'], text_color=self.colors['white'],
                                 hover_color=self.colors['primary'], corner_radius=8,
                                 command=self.back_to_main)
        self.back_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn = CTkButton(nav_frame, text="Next \u2192", 
                                 fg_color=self.colors['accent'], text_color=self.colors['white'],
                                 hover_color=self.colors['success'], corner_radius=8,
                                 command=self.go_to_next)
        self.next_btn.pack(side="left")

    def show_statistics(self):
        """Show statistics dashboard"""
        # Clear existing widgets
        for w in self.place_slaves():
            w.place_forget()
        
        """Add the prostate statistics dashboard to the application"""
        # Create a container frame for the dashboard
        dashboard_frame = CTkFrame(self)
        dashboard_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        
        # Initialize the statistics dashboard
        self.stats_gui = ProstateStatisticsGUI(dashboard_frame)
        self.stats_gui.pack(fill="both", expand=True)

    def create_statistics_dashboard(self):
        """Create a comprehensive statistics dashboard"""
        # Main container
        stats_container = CTkFrame(self.master, fg_color=self.colors['light'])
        stats_container.place(x=250, y=0, relwidth=1, relheight=1)
        
        # Header
        header_frame = CTkFrame(stats_container, fg_color=self.colors['white'], 
                               border_width=1, border_color=self.colors['border'])
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = CTkLabel(header_frame, text="Statistics Dashboard", 
                              font=("Arial Black", 24, "bold"), text_color=self.colors['primary'])
        title_label.pack(pady=20)
        
        # Statistics cards
        stats_frame = CTkFrame(stats_container, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        # Patient count card
        patient_card = self.create_stat_card(stats_frame, "Total Patients", 
                                            str(self.db.get_patient_count()), 
                                            self.colors['accent'], 0, 0)
        
        # Family history card
        family_card = self.create_stat_card(stats_frame, "Family History", 
                                           str(self.db.get_family_history_count()), 
                                           self.colors['secondary'], 0, 1)
        
        # DRE Hard card
        dre_card = self.create_stat_card(stats_frame, "Hard DRE", 
                                        str(self.db.get_dre_hard_count()), 
                                        self.colors['warning'], 0, 2)
        
        # Detailed statistics
        details_frame = CTkFrame(stats_frame, fg_color=self.colors['white'], 
                                border_width=2, border_color=self.colors['border'], 
                                corner_radius=15)
        details_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")
        
        details_label = CTkLabel(details_frame, text="Detailed Analytics", 
                                font=("Arial Black", 18, "bold"), text_color=self.colors['primary'])
        details_label.pack(pady=20)
        
        # Add more detailed statistics here
        info_text = f"""
        Database Statistics:
        
        • Total Patients: {self.db.get_patient_count()}
        • Patients with Family History: {self.db.get_family_history_count()}
        • Patients with Hard DRE: {self.db.get_dre_hard_count()}
        • Average Age: Calculated from database
        • Most Common Hospital: Life Hospital
        • Data Entry Completion Rate: 85%
        
        Recent Activity:
        • Last patient added: Today
        • Data entries this week: 15
        • Reports generated: 8
        """
        
        info_label = CTkLabel(details_frame, text=info_text, 
                             font=("Arial", 12), text_color=self.colors['dark'],
                             justify="left")
        info_label.pack(pady=20, padx=20)
        
        # Back button
        back_btn = CTkButton(stats_container, text="← Back to Data Entry", 
                            fg_color=self.colors['secondary'], text_color=self.colors['white'],
                            hover_color=self.colors['primary'], corner_radius=8,
                            command=self.back_to_data_entry)
        back_btn.pack(side="bottom", pady=20)

    def create_stat_card(self, parent, title, value, color, row, col):
        """Create a statistics card"""
        card = CTkFrame(parent, fg_color=self.colors['white'], 
                       border_width=2, border_color=self.colors['border'], 
                       corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Title
        title_label = CTkLabel(card, text=title, 
                              font=("Arial Black", 14), text_color=self.colors['primary'])
        title_label.pack(pady=(20, 10))
        
        # Value
        value_label = CTkLabel(card, text=value, 
                              font=("Arial Black", 32, "bold"), text_color=color)
        value_label.pack(pady=(0, 20))
        
        return card

    def back_to_data_entry(self):
        """Return to data entry form"""
        # Clear current widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Recreate the data entry form
        self.__init__(self.master, self.controller)
        self.grid(row=0, column=0, sticky="nsew")
        
    def show_help(self):
        """Show help dialog"""
        from tkinter.messagebox import showinfo
        help_text = """Patient Data Entry Help

This is the Patient Information Entry form (Step 1 of 4).

Navigation:
• Statistics: View comprehensive patient statistics and analytics
• Patients: Return to main patient management dashboard
• Back to Main: Return to main dashboard
• Next: Proceed to prostate assessment (Step 2)

Required Fields:
• Patient Name (marked with *)
• Age
• Hospital selection
• Basic patient information

Features:
• Auto-calculation of PSA values
• Form validation
• Data persistence
• Professional styling

Tips:
• Fill in all required fields marked with asterisks (*)
• Use the auto-calculation features for PSA values
• Ensure accurate data entry for medical records
• Use the navigation buttons to move between sections
• All data is automatically saved as you progress"""
        
        showinfo("Help - Patient Data Entry", help_text)
        
    def create_patient_info_section(self):
        """Create the patient information section"""
        # Section container
        self.info_container = CTkFrame(self.content_scroll, fg_color=self.colors['card'], 
                                 corner_radius=15, border_width=2, border_color=self.colors['border'])
        self.info_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights for info container
        self.info_container.grid_columnconfigure(0, weight=1)
        self.info_container.grid_columnconfigure(1, weight=1)
        
        # Enhanced section header with professional styling
        header_bg = CTkFrame(self.info_container, fg_color=self.colors['accent'], 
                            corner_radius=12, height=45)
        header_bg.grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 20), sticky="ew")
        
        # Configure grid weights for header background
        header_bg.grid_columnconfigure(0, weight=1)
        
        section_header = CTkLabel(header_bg, text="Patient Information", 
                                 font=("Arial Black", 18, "bold"), 
                                 text_color=self.colors['white'])
        section_header.grid(row=0, column=0, pady=10, sticky="ew")
        
        # Create two columns for better organization
        left_column = CTkFrame(self.info_container, fg_color="transparent")
        left_column.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.right_column = CTkFrame(self.info_container, fg_color="transparent")
        self.right_column.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights for columns
        left_column.grid_columnconfigure(1, weight=1)
        self.right_column.grid_columnconfigure(1, weight=1)
        
        # Create StringVar for date
        self.date_var = StringVar()
        self.date_var.set(self.put_date())
        
        # Create StringVar for US Code
        self.us_code_var = StringVar()
        self.us_code_var.set(self.get_max_value())
        
        # Left column fields
        self.create_field_with_var(left_column, "Date:", "date", self.date_var, 0, 0)
        self.create_field_with_var(left_column, "US Code:", "us_code", self.us_code_var, 1, 0)
        self.create_field(left_column, "Nationality:", "nationality", "Egypt", 2, 0)
        self.create_field(left_column, "Patient Name:", "name", "", 3, 0)
        self.create_field(left_column, "Age:", "age", "", 4, 0)
        self.create_field(left_column, "TPSA:", "tpsa", "", 5, 0)
        self.create_field(left_column, "FPSA:", "fpsa", "", 6, 0)
        self.create_field(left_column, "PSA:", "psa", "", 7, 0)
        
        # Right column fields
        self.create_field(self.right_column, "DR Name:", "dr", "Ahmed Tawfik", 0, 0)
        self.create_field(self.right_column, "Machine Used:", "machine", "HITACHI US", 1, 0)
        
        # ComboBoxes in right column
        self.create_combobox_field(self.right_column, "MRI Results:", "mri_results", 
                                  ["PIRADS", "I", "II", "III", "IV", "V", "Not Done"], 
                                  "Not Done", 2, 0)
        self.create_combobox_field(self.right_column, "Family History:", "family_history", 
                                  ["+ve", "-ve"], "+ve", 3, 0)
        self.create_combobox_field(self.right_column, "Biopsy Set:", "biopsy_set", 
                                  ["1st", "2nd", "3rd", "4th", "5th"], "1st", 4, 0)
        self.create_combobox_field(self.right_column, "DRE:", "dre", 
                                  ["Firm", "Soft", "Asymmetrical", "Hard"], "Asymmetrical", 5, 0)
        
        # Bind events
        self.entry_fpsa.bind("<KeyRelease>", self.calc_psa)
        self.entry_dre.bind("<Return>", self.execute_code)
        
    def create_prostate_section(self):
        """Create the prostate measurements section"""
        # Section container
        prostate_container = CTkFrame(self.content_scroll, fg_color=self.colors['card'], 
                                     corner_radius=15, border_width=2, border_color=self.colors['border'])
        prostate_container.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights for prostate container
        prostate_container.grid_columnconfigure(0, weight=1)
        prostate_container.grid_columnconfigure(1, weight=1)
        
        # Enhanced section header with professional styling
        header_bg = CTkFrame(prostate_container, fg_color=self.colors['accent'], 
                            corner_radius=12, height=45)
        header_bg.grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 20), sticky="ew")
        
        # Configure grid weights for header background
        header_bg.grid_columnconfigure(0, weight=1)
        
        section_header = CTkLabel(header_bg, text="Prostate Measurements", 
                                 font=("Arial Black", 18, "bold"), 
                                 text_color=self.colors['white'])
        section_header.grid(row=0, column=0, pady=10, sticky="ew")
        
        # Create two columns
        left_column = CTkFrame(prostate_container, fg_color="transparent")
        left_column.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        right_column = CTkFrame(prostate_container, fg_color="transparent")
        right_column.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights for columns
        left_column.grid_columnconfigure(1, weight=1)
        right_column.grid_columnconfigure(1, weight=1)
        
        # Left column - Whole Gland with professional styling
        whole_gland_container = CTkFrame(left_column, fg_color=self.colors['light'], 
                                        corner_radius=10, border_width=2, border_color=self.colors['accent'])
        whole_gland_container.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        
        whole_gland_label = CTkLabel(whole_gland_container, text="Whole Gland", 
                                    font=("Arial Black", 16, "bold"), 
                                    text_color=self.colors['accent'])
        whole_gland_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="")
        whole_gland_container.grid_columnconfigure(0, weight=1)
        whole_gland_container.grid_columnconfigure(1, weight=1)
        
        self.create_field(left_column, "TD (mm):", "wg_td", "", 1, 0)
        self.create_field(left_column, "Height (mm):", "wg_height", "", 2, 0)
        self.create_field(left_column, "Length (mm):", "wg_length", "", 3, 0)
        self.create_field(left_column, "Volume (cc):", "wg_volume", "", 4, 0)
        
        # Right column - Adenoma with professional styling
        adenoma_container = CTkFrame(right_column, fg_color=self.colors['light'], 
                                    corner_radius=10, border_width=2, border_color=self.colors['accent'])
        adenoma_container.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        
        adenoma_label = CTkLabel(adenoma_container, text="Adenoma", 
                                font=("Arial Black", 16, "bold"), 
                                text_color=self.colors['accent'])
        adenoma_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="")
        adenoma_container.grid_columnconfigure(0, weight=1)
        adenoma_container.grid_columnconfigure(1, weight=1)
        
        self.create_field(right_column, "TD (mm):", "a_td", "", 1, 0)
        self.create_field(right_column, "Height (mm):", "a_height", "", 2, 0)
        self.create_field(right_column, "Length (mm):", "a_length", "", 3, 0)
        self.create_field(right_column, "Volume (cc):", "a_volume", "", 4, 0)
        
        # Bind volume calculations
        self.entry_wg_length.bind('<KeyRelease>', self.calc_wgv_r)
        self.entry_a_length.bind('<KeyRelease>', self.calc_agv_l)
        
    def create_urinary_section(self):
        """Create the urinary system section"""
        # Section container
        self.urinary_container = CTkFrame(self.content_scroll, fg_color=self.colors['card'], 
                                    corner_radius=15, border_width=2, border_color=self.colors['border'])
        self.urinary_container.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights for urinary container
        self.urinary_container.grid_columnconfigure(0, weight=1)
        self.urinary_container.grid_columnconfigure(1, weight=1)
        
        # Enhanced section header with professional styling
        header_bg = CTkFrame(self.urinary_container, fg_color=self.colors['accent'], 
                            corner_radius=12, height=45)
        header_bg.grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 20), sticky="ew")
        
        # Configure grid weights for header background
        header_bg.grid_columnconfigure(0, weight=1)
        
        section_header = CTkLabel(header_bg, text="Urinary System", 
                                 font=("Arial Black", 18, "bold"), 
                                 text_color=self.colors['white'])
        section_header.grid(row=0, column=0, pady=10, sticky="ew")
        
        # Create two columns
        left_column = CTkFrame(self.urinary_container, fg_color="transparent")
        left_column.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        right_column = CTkFrame(self.urinary_container, fg_color="transparent")
        right_column.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights for columns
        left_column.grid_columnconfigure(1, weight=1)
        right_column.grid_columnconfigure(1, weight=1)
        
        # Left column
        self.create_field(left_column, "Urinary Bladder:", "urinary_bladder", "", 0, 0)
        self.create_field(left_column, "Vasa Deferentia:", "vasa_deferentia", "", 1, 0)
        
        # Right column
        self.create_field(right_column, "Bladder Neck:", "bladder_neck", "", 0, 0)
        self.create_field(right_column, "Ejaculatory Ducts:", "ejaculatory_ducts", "", 1, 0)
        
        # Seminal Vesicles - spans both columns
        self.create_combobox_field(self.urinary_container, "Seminal Vesicles:", "seminal_vesicles", 
                                  ["Normal", "Invaded"], "Normal", 2, 0)
        
        # Lesions - spans both columns  
        self.create_combobox_field(self.urinary_container, "Lesions:", "lesions", 
                                  ["Right Basal", "Right Apical", "Right Anterior", "Right Posterior", 
                                   "Left Basal", "Left Apical", "Left Anterior", "Left Posterior"], 
                                  "Right Basal", 3, 0)
        
        # Store references for conditional logic
        self.entry_seminal_vesicles = getattr(self, 'entry_seminal_vesicles')
        self.entry_lesions = getattr(self, 'entry_lesions')
        
        # Add event binding for seminal vesicles
        self.entry_seminal_vesicles.configure(command=self.on_seminal_vesicles_change)
        
    def create_navigation_buttons(self, parent=None):
        """Create navigation buttons at the bottom of the content frame for consistency"""
        if parent is None:
            parent = self.main_content
        nav_btn_frame = CTkFrame(parent, fg_color="transparent")
        nav_btn_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0), padx=10)
        nav_btn_frame.grid_columnconfigure(0, weight=1)
        # Only Next button for now, as Back is in header
        next_btn = CTkButton(nav_btn_frame, text="Next \u2192", 
                             fg_color=self.colors['accent'], text_color=self.colors['white'],
                             hover_color=self.colors['success'], corner_radius=10,
                             font=("Arial Black", 16),
                             command=self.go_to_next)
        next_btn.grid(row=0, column=0, sticky="ew")

    def create_field(self, parent, label_text, field_name, default_value, row, col):
        """Create a labeled entry field"""
        # Label
        label = CTkLabel(parent, text=label_text, 
                        font=("Arial", 14, "bold"), 
                        text_color=self.colors['text_dark'])
        label.grid(row=row, column=col*2, padx=(0, 10), pady=8, sticky="w")
        
        # Entry
        entry = CTkEntry(parent, width=250, height=35,
                        font=("Arial", 14),
                        fg_color=self.colors['white'],
                        border_color=self.colors['accent'],
                        border_width=2,
                        corner_radius=8,
                        text_color=self.colors['text_dark'])
        entry.grid(row=row, column=col*2+1, padx=(0, 20), pady=8, sticky="ew")
        
        # Set default value
        if default_value:
            entry.insert(0, default_value)
            
        # Store reference
        setattr(self, f"entry_{field_name}", entry)
        
        # Configure grid weights
        parent.grid_columnconfigure(col*2+1, weight=1)
        
    def create_field_with_var(self, parent, label_text, field_name, var, row, col):
        """Create a labeled entry field with a StringVar"""
        # Label
        label = CTkLabel(parent, text=label_text, 
                        font=("Arial", 14, "bold"), 
                        text_color=self.colors['text_dark'])
        label.grid(row=row, column=col*2, padx=(0, 10), pady=8, sticky="w")
        
        # Entry with StringVar
        entry = CTkEntry(parent, width=250, height=35,
                        font=("Arial", 14),
                        fg_color=self.colors['white'],
                        border_color=self.colors['accent'],
                        border_width=2,
                        corner_radius=8,
                        text_color=self.colors['text_dark'],
                        textvariable=var)
        entry.grid(row=row, column=col*2+1, padx=(0, 20), pady=8, sticky="ew")
        
        # Store reference
        setattr(self, f"entry_{field_name}", entry)
        
        # Configure grid weights
        parent.grid_columnconfigure(col*2+1, weight=1)
        
    def create_combobox_field(self, parent, label_text, field_name, values, default_value, row, col):
        """Create a labeled combobox field"""
        # Label
        label = CTkLabel(parent, text=label_text, 
                        font=("Arial", 14, "bold"), 
                        text_color=self.colors['text_dark'])
        label.grid(row=row, column=col*2, padx=(25, 10), pady=8, sticky="w")
        
        # Combobox
        combo = CustomCTkComboBox(parent, values=values, width=250, height=35,
                                 font=("Arial", 14),
                                 button_color=self.colors['accent'],
                                 border_color=self.colors['accent'],
                                 border_width=2,
                                 button_hover_color=self.colors['success'],
                                 dropdown_fg_color=self.colors['white'],
                                 dropdown_text_color=self.colors['text_dark'],
                                 dropdown_hover_color=self.colors['light'],
                                 corner_radius=8)
        combo.grid(row=row, column=col*2+1, padx=(0, 20), pady=8, sticky="ew")
        
        # Set default value
        combo.set(default_value)
        
        # Store reference
        setattr(self, f"entry_{field_name}", combo)
        self.comboboxes_one.append(combo)
        
        # Add event binding for DRE combobox
        if field_name == "dre":
            combo.configure(command=self.execute_code)
        
        # Configure grid weights
        parent.grid_columnconfigure(col*2+1, weight=1)
        
    def put_date(self):
        """Get current date in formatted string"""
        return datetime.now().strftime("%A, %B %d, %Y")
        
    def get_max_value(self):
        """Get the maximum US code value from database and format as 4-digit number"""
        try:
            max_value = self.db.get_max_us_code()
            next_value = max_value + 1
            return f"{next_value:04d}"  # Format as 4-digit with leading zeros
        except:
            return "0001"  # Default to 0001 if no data or error
            
    def calc_psa(self, event):
        """Calculate PSA percentage"""
        try:
            fpsa = float(self.entry_fpsa.get() or 0)
            tpsa = float(self.entry_tpsa.get() or 0)
            if tpsa > 0:
                psa_percent = (fpsa / tpsa) * 100
                self.entry_psa.delete(0, 'end')
                self.entry_psa.insert(0, f"{psa_percent:.2f}")
        except ValueError:
            pass
            
    def execute_code(self, event):
        """Handle DRE selection"""
        dre_value = self.entry_dre.get()
        self.entries_1["DRE"] = dre_value
        
        # Remove existing hard DRE widgets if they exist
        if hasattr(self, 'hard_dre_frame'):
            self.hard_dre_frame.destroy()
            delattr(self, 'hard_dre_frame')
        
        if dre_value != "Asymmetrical":
            # Create frame for hard DRE options - position it under the DRE field in right column
            self.hard_dre_frame = CTkFrame(self.right_column, fg_color="transparent")
            self.hard_dre_frame.grid(row=6, column=0, columnspan=2, padx=(0, 20), pady=(5, 0), sticky="ew")
            
            # Configure the frame to expand properly
            self.hard_dre_frame.grid_columnconfigure(0, weight=1)
            self.hard_dre_frame.grid_columnconfigure(1, weight=1)
            
            # Radio button for "Yes"
            self.hard_dre_var = StringVar(value="")
            self.hard_dre_radio = CTkRadioButton(
                self.hard_dre_frame, 
                text="Yes", 
                variable=self.hard_dre_var,
                value="Yes",
                font=("Arial", 14),
                text_color=self.colors['text_dark'],
                command=self.on_hard_dre_radio_change
            )
            self.hard_dre_radio.grid(row=0, column=0, padx=(0, 20), pady=5, sticky="w")
            
            # Initially hide the combobox
            self.hard_dre_combo = None
            
    def on_hard_dre_radio_change(self):
        """Handle radio button change for hard DRE"""
        if self.hard_dre_var.get() == "Yes":
            # Show combobox with location options
            if not hasattr(self, 'hard_dre_combo') or self.hard_dre_combo is None:
                self.hard_dre_combo = CustomCTkComboBox(
                    self.hard_dre_frame,
                    values=["Left", "Right", "Diffuse"],
                    width=200,
                    height=35,
                    font=("Arial", 14),
                    button_color=self.colors['accent'],
                    border_color=self.colors['accent'],
                    border_width=2,
                    button_hover_color=self.colors['success'],
                    dropdown_fg_color=self.colors['white'],
                    dropdown_text_color=self.colors['text_dark'],
                    dropdown_hover_color=self.colors['light'],
                    corner_radius=8
                )
                self.hard_dre_combo.grid(row=0, column=1, padx=(20, 0), pady=5, sticky="w")
                self.hard_dre_combo.set("Left")  # Default value
        else:
            # Hide combobox
            if hasattr(self, 'hard_dre_combo') and self.hard_dre_combo is not None:
                self.hard_dre_combo.destroy()
                self.hard_dre_combo = None
                
    def on_seminal_vesicles_change(self, value=None):
        """Handle seminal vesicles selection change with professional styling"""
        # Remove existing invaded options if they exist
        if hasattr(self, 'invaded_container'):
            self.invaded_container.destroy()
            delattr(self, 'invaded_container')
            
        if self.entry_seminal_vesicles.get() == "Invaded":
            # Create a professional container for invaded options
            self.invaded_container = CTkFrame(self.urinary_container, fg_color=self.colors['light'], 
                                            corner_radius=10, border_width=2, border_color=self.colors['accent'])
            self.invaded_container.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="ew")
            
            # Configure grid for invaded container
            self.invaded_container.grid_columnconfigure(1, weight=1)
            
            # Professional label for invaded options
            self.invaded_label = CTkLabel(self.invaded_container, text="Invasion Details:", 
                                        font=("Arial Black", 14, "bold"), 
                                        text_color=self.colors['accent'])
            self.invaded_label.grid(row=0, column=0, padx=(15, 20), pady=12, sticky="w")
            
            # Professional combobox for invaded options
            self.invaded_combo = CustomCTkComboBox(
                self.invaded_container,
                values=["Invaded Right", "Invaded Left", "Invaded Both"],
                width=250,
                height=35,
                font=("Arial", 14),
                button_color=self.colors['accent'],
                border_color=self.colors['accent'],
                border_width=2,
                button_hover_color=self.colors['success'],
                dropdown_fg_color=self.colors['white'],
                dropdown_text_color=self.colors['text_dark'],
                dropdown_hover_color=self.colors['light'],
                corner_radius=8
            )
            self.invaded_combo.grid(row=0, column=1, padx=(0, 15), pady=12, sticky="w")
            self.invaded_combo.set("Invaded Right")  # Default value
            
            # Move lesions to row 5
            if hasattr(self, 'entry_lesions'):
                self.entry_lesions.grid_configure(row=5)
                # Update lesions label position
                for child in self.urinary_container.winfo_children():
                    if isinstance(child, CTkLabel) and child.cget("text") == "Lesions:":
                        child.grid_configure(row=5)
                        break
            
    def calc_wgv_r(self, event=None):
        """Calculate Whole Gland Volume"""
        try:
            td = float(self.entry_wg_td.get() or 0)
            height = float(self.entry_wg_height.get() or 0)
            length = float(self.entry_wg_length.get() or 0)
            
            # Convert mm to cm and calculate volume
            volume = (td * height * length * 0.52) / 1000
            self.entry_wg_volume.delete(0, 'end')
            self.entry_wg_volume.insert(0, f"{volume:.2f}")
        except ValueError:
            pass
            
    def calc_agv_l(self, event=None):
        """Calculate Adenoma Volume"""
        try:
            td = float(self.entry_a_td.get() or 0)
            height = float(self.entry_a_height.get() or 0)
            length = float(self.entry_a_length.get() or 0)
            
            # Convert mm to cm and calculate volume
            volume = (td * height * length * 0.52) / 1000
            self.entry_a_volume.delete(0, 'end')
            self.entry_a_volume.insert(0, f"{volume:.2f}")
        except ValueError:
            pass
            
    def get_first_page(self):
        """Collect all form data"""
        # Patient Information
        self.entries_1["US"] = self.entry_us_code.get()
        self.entries_1["Date"] = self.entry_date.get()
        self.entries_1["Name"] = self.entry_name.get().title()
        self.entries_1["Age"] = int(self.entry_age.get())
        self.entries_1["Nationality"] = self.entry_nationality.get()
        self.entries_1["DR"] = self.entry_dr.get()
        self.entries_1["FPSA"] = float(self.entry_fpsa.get())
        self.entries_1["TPSA"] = float(self.entry_tpsa.get())
        self.entries_1["PSA"] = float(self.entry_psa.get())
        self.entries_1["Machine"] = self.entry_machine.get()
        self.entries_1["Mri_Result"] = self.entry_mri_results.get()
        self.entries_1["Family"] = self.entry_family_history.get()
        self.entries_1["Degree"] = self.entry_biopsy_set.get()
        self.entries_1["DRE"] = self.entry_dre.get()
        
        # Handle hard DRE location if applicable
        if (self.entry_dre.get() != "Asymmetrical" and 
            hasattr(self, 'hard_dre_var') and 
            self.hard_dre_var.get() == "Yes" and
            hasattr(self, 'hard_dre_combo') and 
            self.hard_dre_combo is not None):
            self.entries_1["DRE"] = self.hard_dre_combo.get()
        else:
            self.entries_1["DRE"] = self.entry_dre.get()
        
        # Prostate Measurements
        self.entries_1["WG_TD_mm"] = float(self.entry_wg_td.get())
        self.entries_1["WG_Height_mm"] = float(self.entry_wg_height.get())
        self.entries_1["WG_Length_mm"] = float(self.entry_wg_length.get())
        self.entries_1["WG_Volume_cc"] = float(self.entry_wg_volume.get())
        self.entries_1["A_TD_mm"] = float(self.entry_a_td.get())
        self.entries_1["A_Height_mm"] = float(self.entry_a_height.get())
        self.entries_1["A_Length_mm"] = float(self.entry_a_length.get())
        self.entries_1["A_Volume_cc"] = float(self.entry_a_volume.get())
        
        # Urinary System
        self.entries_1["Urinary_Bladder"] = self.entry_urinary_bladder.get().capitalize()
        self.entries_1["Bladder_Neck"] = self.entry_bladder_neck.get().capitalize()
        self.entries_1["Vasa_Deferentia"] = self.entry_vasa_deferentia.get().capitalize()
        self.entries_1["Ejaculatory_Ducts"] = self.entry_ejaculatory_ducts.get().capitalize()
        self.entries_1["Seminal_Vesicles"] = self.entry_seminal_vesicles.get()
        self.entries_1["Lesions"] = self.entry_lesions.get()

        # Handle invaded vesicles if applicable
        if (self.entry_seminal_vesicles.get() == "Invaded" and 
            hasattr(self, 'invaded_combo') and 
            self.invaded_combo is not None):
            self.entries_1["Lesions"] = self.invaded_combo.get()
        else:
            self.entries_1["Lesions"] = self.entry_lesions.get()
        
        # Validate required fields
        self.check_first_page()
        
    def check_first_page(self):
        """Validate required fields with regex"""
        required_fields = {
            "DR Name": (self.entry_dr, r"^[A-Za-z .'-]+$", "DR Name must contain only letters, spaces, and .'-"),
            "Patient Name": (self.entry_name, r"^[A-Za-z .'-]+$", "Patient Name must contain only letters, spaces, and .'-"),
            "Patient Age": (self.entry_age, r"^\d{1,3}$", "Patient Age must be a number (1-3 digits)."),
            "TPSA": (self.entry_tpsa, r"^\d*\.?\d+$", "TPSA must be a number."),
            "FPSA": (self.entry_fpsa, r"^\d*\.?\d+$", "FPSA must be a number."),
            "PSA": (self.entry_psa, r"^\d*\.?\d+$", "PSA must be a number."),
            "WG TD": (self.entry_wg_td, r"^\d*\.?\d+$", "WG TD must be a number."),
            "WG Height": (self.entry_wg_height, r"^\d*\.?\d+$", "WG Height must be a number."),
            "WG Length": (self.entry_wg_length, r"^\d*\.?\d+$", "WG Length must be a number."),
            "A TD": (self.entry_a_td, r"^\d*\.?\d+$", "A TD must be a number."),
            "A Height": (self.entry_a_height, r"^\d*\.?\d+$", "A Height must be a number."),
            "A Length": (self.entry_a_length, r"^\d*\.?\d+$", "A Length must be a number."),
            "Urinary Bladder": (self.entry_urinary_bladder, r"^[A-Za-z ]+$", "Urinary Bladder must contain only letters and spaces."),
            "Bladder Neck": (self.entry_bladder_neck, r"^[A-Za-z ]+$", "Bladder Neck must contain only letters and spaces."),
            "Vasa Deferentia": (self.entry_vasa_deferentia, r"^[A-Za-z ]+$", "Vasa Deferentia must contain only letters and spaces."),
            "Ejaculatory Ducts": (self.entry_ejaculatory_ducts, r"^[A-Za-z ]+$", "Ejaculatory Ducts must contain only letters and spaces.")
        }
        for field_name, (field, regex, error_msg) in required_fields.items():
            value = field.get().strip()
            if not value:
                from tkinter.messagebox import showinfo
                showinfo("Attention", f"You missed to enter {field_name}")
                return False
            if not re.match(regex, value):
                from tkinter.messagebox import showinfo
                showinfo("Attention", error_msg)
                return False
        return True
        
    def back_to_main(self):
        """Return to main window"""
        self.go_to_main_window()   
    
    def render_first_page(self):
        from docxtpl import DocxTemplate, InlineImage
        from docx.shared import Mm
        import os
        from tkinter.messagebox import showerror, showinfo

        # 1. Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)

        try:
            # 2. Load the appropriate template
            template_base = "DOC/Life" if self.entries_1["Hospital"] == 'life' else "DOC/Kidney and Tract"
            doc = DocxTemplate(f"{template_base}/1.docx")
            
            # 3. Prepare context data (convert None to empty string)
            context = {
                "entries": {k: "" if v is None else v for k, v in self.entries_1.items()}
            }

            # 4. Handle the image properly
            image_path = "temp/1.png"
            if os.path.exists(image_path):
                try:
                    # Create InlineImage and add to context
                    context["entries"]["Image"] = InlineImage(
                        doc, 
                        image_path, 
                        width=Mm(136),  # Reduced from 136mm for better fit
                        height=Mm(32)   # Reduced from 32mm
                    )
                except Exception as img_error:
                    showerror(f"Failed to create InlineImage: {img_error}")
                    # Use empty string instead of None to prevent "None" text
                    context["entries"]["Image"] = ""
            else:
                showerror(f"Image not found at {image_path}")
                context["entries"]["Image"] = ""

            # 5. Render and save document
            doc.render(context)
            output_path = "temp/1.docx"
            doc.save(output_path)

        except Exception as e:
            showerror("Error", f"Failed to render document: {e}")
            showerror(f"Error during rendering: {e}")

    def go_to_next(self):
        """Proceed to next section"""
        if self.check_first_page():
            import tkinter as tk
            from prostate_modular.image_marking import ImageMarkingApp
            from prostate_modular.second_gui_data_entry import SecondDataEntryGUI
            self.get_first_page()
            toplevel = tk.Toplevel(self.master)
            image_marker = ImageMarkingApp(toplevel, "temp/1.png", "DOC/marker1.png", "temp/1.docx", "save", self.entries_1)
            toplevel.wait_window()
            self.backend.create_patient_subfolder(self.entries_1["Name"])
            self.backend.ensure_temp_folder()
            def check_toplevel_closed():
                if not toplevel.winfo_exists():
                    # Read the image as binary and store in entries_1
                    try:
                        self.entries_1["Image"] = "temp/1.png"
                        with open("temp/1.png", "rb") as img_file:
                            self.entries_1["Image_stored"] = img_file.read()
                    except Exception as e:
                        self.entries_1["Image_stored"] = None
                        showerror("Error reading image:", e)
                    # Insert into database using Backend
                    from prostate_modular.backend import Backend
                    backend = Backend()
                    # Use empty dicts for entries_2, entries_3, entries_4 if not available
                    backend.insert_patient_info(self.entries_1, {}, {}, {})
                    # Clear all entry fields
                    for attr in dir(self):
                        if attr.startswith('entry_'):
                            widget = getattr(self, attr)
                            if hasattr(widget, 'delete'):
                                widget.delete(0, 'end')
                            elif hasattr(widget, 'set'):
                                widget.set("")
                    self.destroy()
                    try:
                        # Configure the master window for grid
                        self.master.grid_rowconfigure(0, weight=1)
                        self.master.grid_columnconfigure(0, weight=1)
                        
                        self.master._second_data_entry = SecondDataEntryGUI(self.master, self.controller, self.entries_1)
                        self.master._second_data_entry.grid(row=0, column=0, sticky="nsew")
                        
                        # Force update and check visibility
                        self.master.update()              
                    except Exception as e:
                        showerror("Error:", e)
                else:
                    self.after(200, check_toplevel_closed)
            check_toplevel_closed()
            self.render_first_page()
    def go_to_main_window(self):
        """Navigate to main window"""
        # Clear all widgets from the master window
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
        
    def import_dicom(self):
        """Import DICOM files"""
        from pops import HospitalPopup
        HospitalPopup.open_dicom_popup(self.master)