from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage, CTkScrollableFrame
from prostate_modular.utils import CustomCTkComboBox
from tkinter import Toplevel
from docxtpl import DocxTemplate
from tkinter.messagebox import askquestion, showerror
from prostate_modular.image_marking import ImageMarkingApp
from PIL import Image
from prostate_modular.constant import entries_2
from prostate_modular.stats import ProstateStatisticsGUI
class SecondDataEntryGUI(CTkFrame):
    def __init__(self, parent, controller, entries_1, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.master = parent  # Ensure reference to parent/root window
        self.entries_1 = entries_1
        self.entries_2 = entries_2
        self.function_called = False
        self.doc_saved = False
        
        # Initialize field_widgets for storing references to input fields
        self.field_widgets = {}
        
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
            'hover': '#f1f5f9',          # Hover color
            'text_light': '#94a3b8'     # Lighter text color
        }
        
        # Initialize images
        self.setup_images()
        
        # Setup UI
        self.setup_ui()

    def setup_images(self):
        """Initialize all images used in the UI"""
        try:
            # Logo images
            logo_image = Image.open("Logo/main/Best11.png")
            self.logo_img = CTkImage(dark_image=logo_image, light_image=logo_image, size=(150, 150))
            
            # Sidebar images
            ana_image = Image.open("Logo/side bar/stat2.png")
            self.analytics_img = CTkImage(dark_image=ana_image, light_image=ana_image, size=(80, 60))
            
            pat_image = Image.open("Logo/side bar/pat11.png")
            self.patient_img = CTkImage(dark_image=pat_image, light_image=pat_image, size=(100, 60))
            
            # Patient images
            patient_img = Image.open("Logo/patient/ElogoButton-1.png")
            self.patient_counter_img = CTkImage(dark_image=patient_img, light_image=patient_img, size=(40, 30))
            
            family_image = Image.open("Logo/patient/family_history1.png")
            self.family_img = CTkImage(dark_image=family_image, light_image=family_image, size=(40, 30))
            
            dre_image = Image.open("Logo/patient/dre_logo.png")
            self.dre_img = CTkImage(dark_image=dre_image, light_image=dre_image, size=(40, 30))
            
            add_patient_light = Image.open("Logo/patient/add_user_light.png")
            self.add_user_data_img = CTkImage(dark_image=add_patient_light, light_image=add_patient_light, size=(60, 25))
            
        except Exception as e:
            showerror(f"Warning: Could not load some images: {e}")
            # Create placeholder images if files don't exist
            self.logo_img = None
            self.analytics_img = None
            self.patient_img = None
            self.patient_counter_img = None
            self.family_img = None
            self.dre_img = None
            self.add_user_data_img = None

    def setup_ui(self):
        """Setup the main UI with sidebar and content area"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Initialize the second page
        self.second_page()

    def create_sidebar(self):
        """Create and configure the sidebar with professional styling"""
        # Create sidebar frame
        self.sidebar_frame = CTkFrame(self, fg_color=self.colors['sidebar'], 
                                     bg_color="transparent", corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Logo with enhanced styling
        if self.logo_img:
            logo_label = CTkButton(self.sidebar_frame, text="", image=self.logo_img, compound='left', 
                                  fg_color="transparent", width=200, height=150, 
                                  font=("Arial-BoldMT", 12), hover_color=self.colors['primary'])
            logo_label.grid(row=0, column=0, pady=(20, 10))
            logo_label.configure(state="disabled")
        
        # Page title
        title_label = CTkLabel(self.sidebar_frame, text="Prostate Data Entry", 
                              font=("Arial Black", 16, "bold"), text_color=self.colors['white'])
        title_label.grid(row=1, column=0, pady=(0, 20))
        
        # Navigation buttons
        self.create_nav_button("Statistics", self.analytics_img, row=2, command=self.show_statistics)
        self.create_nav_button("Patients", self.patient_img, row=3, command=self.go_to_main_window)
        
        # Progress indicator
        progress_label = CTkLabel(self.sidebar_frame, text="Step 2 of 4", 
                                 font=("Arial", 12), text_color=self.colors['accent'])
        progress_label.grid(row=4, column=0, pady=(20, 10))
        
        # Progress bar
        self.progress_frame = CTkFrame(self.sidebar_frame, fg_color=self.colors['dark'], height=8)
        self.progress_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.progress_bar = CTkFrame(self.progress_frame, fg_color=self.colors['accent'], width=125)
        self.progress_bar.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
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

    def create_header(self, parent=None):
        """Create the header section with title and navigation, optionally in a given parent"""
        if parent is None:
            parent = self.main_content
        header_frame = CTkFrame(parent, fg_color=self.colors['white'], 
                               border_width=1, border_color=self.colors['border'])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = CTkLabel(header_frame, text="Prostate Zone Assessment", 
                              font=("Arial Black", 24, "bold"), text_color=self.colors['primary'])
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Navigation buttons
        nav_frame = CTkFrame(header_frame, fg_color="transparent")
        nav_frame.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
        self.back_btn = CTkButton(nav_frame, text="\u2190 Back", 
                                 fg_color=self.colors['secondary'], text_color=self.colors['white'],
                                 hover_color=self.colors['primary'], corner_radius=8,
                                 command=self.back_to_first)
        self.back_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn = CTkButton(nav_frame, text="Next \u2192", 
                                 fg_color=self.colors['accent'], text_color=self.colors['white'],
                                 hover_color=self.colors['success'], corner_radius=8,
                                 command=self.go_to_third)
        self.next_btn.pack(side="left")

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
                             command=self.go_to_third)
        next_btn.grid(row=0, column=0, sticky="ew")

    def second_page(self):
        """Create the enhanced second page with professional styling"""
        self.function_called = True
        
        # Clear existing content
        for widget in self.content_scroll.winfo_children():
            widget.destroy()
        
        # Configure grid weights for content
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=1)
        
        # Create section cards
        self.create_anterior_section()
        self.create_medial_section()
        self.create_posterior_section()
        self.create_transition_section()
        self.create_bulk_controls()

    def create_section_card(self, title, row, column, columnspan=1):
        """Create a professional section card"""
        card = CTkFrame(self.content_scroll, fg_color=self.colors['white'], 
                       border_width=2, border_color=self.colors['border'], 
                       corner_radius=15)
        card.grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10, sticky="nsew")
        
        # Title with accent line
        title_frame = CTkFrame(card, fg_color="transparent", height=50)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = CTkLabel(title_frame, text=title, 
                              font=("Arial Black", 18, "bold"), text_color=self.colors['primary'])
        title_label.pack(side="left")
        
        # Accent line
        accent_line = CTkFrame(title_frame, fg_color=self.colors['accent'], height=3)
        accent_line.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)
        
        return card

    def create_anterior_section(self):
        """Create the Anterior prostate section"""
        card = self.create_section_card("Anterior Prostate", 0, 0, 2)
        
        # Configure grid for the card
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(3, weight=1)
        
        # Section content
        content_frame = CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)
        
        # Apex Horn
        self.create_zone_row(content_frame, "Apex", "AApexR", "AApexL", 0)
        
        # Mid-Prostate
        self.create_zone_row(content_frame, "MidProstate", "AMidProstateR", "AMidProstateL", 1)
        
        # Base
        self.create_zone_row(content_frame, "Base", "ABaseR", "ABaseL", 2)

    def create_medial_section(self):
        """Create the Medial PZ section"""
        card = self.create_section_card("Medial PZ", 1, 0, 2)
        
        content_frame = CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)
        
        # Apex
        self.create_zone_row(content_frame, "Apex", "MApexR", "MApexL", 0)
        
        # Mid-Prostate
        self.create_zone_row(content_frame, "MidProstate", "MMidprostateR", "MMidprostateL", 1)
        
        # Base
        self.create_zone_row(content_frame, "Base", "MBaseR", "MBaseL", 2)

    def create_posterior_section(self):
        """Create the Prostate PZ lateral section"""
        card = self.create_section_card("Posterior PZ Lateral", 2, 0, 2)
        
        content_frame = CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)
        
        # Apex
        self.create_zone_row(content_frame, "Apex", "PApexR", "PApexL", 0)
        
        # Mid-Prostate
        self.create_zone_row(content_frame, "MidProstate", "PMidprostateR", "PMidprostateL", 1)
        
        # Base
        self.create_zone_row(content_frame, "Base", "PBaseR", "PBaseL", 2)

    def create_transition_section(self):
        """Create the Transition Zone section"""
        card = self.create_section_card("Transition Zone (TZ)", 3, 0, 2)
        
        content_frame = CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)
        
        # Mid-Prostate
        self.create_zone_row(content_frame, "MidProstate", "TMidprostateR", "TMidprostateL", 0)
        
        # Base
        self.create_zone_row(content_frame, "Base", "TBaseR", "TBaseL", 1)

    def create_zone_row(self, parent, zone_name, right_attr, left_attr, row):
        """Create a row for zone selection with Right and Left options"""
        # Zone name label
        zone_label = CTkLabel(parent, text=zone_name, 
                             font=("Arial Black", 14), text_color=self.colors['dark'])
        zone_label.grid(row=row, column=0, padx=(0, 15), pady=10, sticky="w")
        
        # Right side
        right_label = CTkLabel(parent, text="Right", 
                              font=("Arial", 12, "bold"), text_color=self.colors['secondary'])
        right_label.grid(row=row, column=1, padx=(0, 10), pady=10, sticky="w")
        
        right_combo = CustomCTkComboBox(parent, values=["low", "intermediate", "high"])
        right_combo.grid(row=row, column=1)
        
        # Left side
        left_label = CTkLabel(parent, text="Left", 
                             font=("Arial", 12, "bold"), text_color=self.colors['secondary'])
        left_label.grid(row=row, column=2, padx=(0, 10), pady=10, sticky="w")
        
        left_combo = CustomCTkComboBox(parent, values=["low", "intermediate", "high"])
        left_combo.grid(row=row, column=3)
        
        # Use the attribute names (which should match entries_2 keys)
        self.field_widgets[right_attr] = right_combo
        self.field_widgets[left_attr] = left_combo

    def create_bulk_controls(self):
        """Create bulk control section for changing all values at once"""
        card = self.create_section_card("Bulk Controls", 4, 0, 2)
        
        content_frame = CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header for bulk controls
        header_label = CTkLabel(content_frame, text="Quick Set All Values", 
                               font=("Arial Black", 16), text_color=self.colors['primary'])
        header_label.pack(pady=(0, 15))
        
        # Description
        desc_label = CTkLabel(content_frame, text="Use these controls to set all values for each zone at once", 
                             font=("Arial", 12), text_color=self.colors['text_light'])
        desc_label.pack(pady=(0, 20))
        
        # Create a grid for bulk controls
        controls_frame = CTkFrame(content_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=10)
        
        # Anterior controls
        anterior_frame = CTkFrame(controls_frame, fg_color=self.colors['hover'], corner_radius=12)
        anterior_frame.pack(fill="x", pady=8)
        
        anterior_header = CTkLabel(anterior_frame, text="Anterior Prostate", 
                                  font=("Arial Black", 14), text_color=self.colors['primary'])
        anterior_header.pack(side="left", padx=20, pady=15)
        
        controls_container = CTkFrame(anterior_frame, fg_color="transparent")
        controls_container.pack(side="right", padx=20, pady=10)
        
        CTkLabel(controls_container, text="Right:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_anterior_r = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                               font=("Helvetica", 12), width=120, 
                                               command=self.change_anterior_r,
                                               button_color=self.colors['accent'], 
                                               border_color=self.colors['accent'], 
                                               border_width=2, button_hover_color=self.colors['success'], 
                                               dropdown_hover_color=self.colors['success'], 
                                               dropdown_fg_color=self.colors['accent'], 
                                               dropdown_text_color=self.colors['white'])
        self.all_anterior_r.pack(side="left", padx=(0, 15))
        self.all_anterior_r.set("low")
        
        CTkLabel(controls_container, text="Left:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_anterior_l = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                               font=("Helvetica", 12), width=120, 
                                               command=self.change_anterior_l,
                                               button_color=self.colors['accent'], 
                                               border_color=self.colors['accent'], 
                                               border_width=2, button_hover_color=self.colors['success'], 
                                               dropdown_hover_color=self.colors['success'], 
                                               dropdown_fg_color=self.colors['accent'], 
                                               dropdown_text_color=self.colors['white'])
        self.all_anterior_l.pack(side="left", padx=(0, 5))
        self.all_anterior_l.set("low")
        
        # Medial controls
        medial_frame = CTkFrame(controls_frame, fg_color=self.colors['hover'], corner_radius=12)
        medial_frame.pack(fill="x", pady=8)
        
        medial_header = CTkLabel(medial_frame, text="Medial PZ", 
                                font=("Arial Black", 14), text_color=self.colors['primary'])
        medial_header.pack(side="left", padx=20, pady=15)
        
        controls_container = CTkFrame(medial_frame, fg_color="transparent")
        controls_container.pack(side="right", padx=20, pady=10)
        
        CTkLabel(controls_container, text="Right:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Medial_r = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                             font=("Helvetica", 12), width=120, 
                                             command=self.change_medial_r,
                                             button_color=self.colors['accent'], 
                                             border_color=self.colors['accent'], 
                                             border_width=2, button_hover_color=self.colors['success'], 
                                             dropdown_hover_color=self.colors['success'], 
                                             dropdown_fg_color=self.colors['accent'], 
                                             dropdown_text_color=self.colors['white'])
        self.all_Medial_r.pack(side="left", padx=(0, 15))
        self.all_Medial_r.set("low")
        
        CTkLabel(controls_container, text="Left:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Medial_l = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                             font=("Helvetica", 12), width=120, 
                                             command=self.change_medial_l,
                                             button_color=self.colors['accent'], 
                                             border_color=self.colors['accent'], 
                                             border_width=2, button_hover_color=self.colors['success'], 
                                             dropdown_hover_color=self.colors['success'], 
                                             dropdown_fg_color=self.colors['accent'], 
                                             dropdown_text_color=self.colors['white'])
        self.all_Medial_l.pack(side="left", padx=(0, 5))
        self.all_Medial_l.set("low")
        
        # Posterior controls
        posterior_frame = CTkFrame(controls_frame, fg_color=self.colors['hover'], corner_radius=12)
        posterior_frame.pack(fill="x", pady=8)
        
        posterior_header = CTkLabel(posterior_frame, text="Posterior PZ", 
                                   font=("Arial Black", 14), text_color=self.colors['primary'])
        posterior_header.pack(side="left", padx=20, pady=15)
        
        controls_container = CTkFrame(posterior_frame, fg_color="transparent")
        controls_container.pack(side="right", padx=20, pady=10)
        
        CTkLabel(controls_container, text="Right:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Prostate_PZ_r = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                                   font=("Helvetica", 12), width=120, 
                                                   command=self.change_Prostate_PZ_r,
                                                   button_color=self.colors['accent'], 
                                                   border_color=self.colors['accent'], 
                                                   border_width=2, button_hover_color=self.colors['success'], 
                                                   dropdown_hover_color=self.colors['success'], 
                                                   dropdown_fg_color=self.colors['accent'], 
                                                   dropdown_text_color=self.colors['white'])
        self.all_Prostate_PZ_r.pack(side="left", padx=(0, 15))
        self.all_Prostate_PZ_r.set("low")
        
        CTkLabel(controls_container, text="Left:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Prostate_PZ_l = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                                   font=("Helvetica", 12), width=120, 
                                                   command=self.change_Prostate_PZ_l,
                                                   button_color=self.colors['accent'], 
                                                   border_color=self.colors['accent'], 
                                                   border_width=2, button_hover_color=self.colors['success'], 
                                                   dropdown_hover_color=self.colors['success'], 
                                                   dropdown_fg_color=self.colors['accent'], 
                                                   dropdown_text_color=self.colors['white'])
        self.all_Prostate_PZ_l.pack(side="left", padx=(0, 5))
        self.all_Prostate_PZ_l.set("low")
        
        # Transition controls
        transition_frame = CTkFrame(controls_frame, fg_color=self.colors['hover'], corner_radius=12)
        transition_frame.pack(fill="x", pady=8)
        
        transition_header = CTkLabel(transition_frame, text="Transition Zone", 
                                    font=("Arial Black", 14), text_color=self.colors['primary'])
        transition_header.pack(side="left", padx=20, pady=15)
        
        controls_container = CTkFrame(transition_frame, fg_color="transparent")
        controls_container.pack(side="right", padx=20, pady=10)
        
        CTkLabel(controls_container, text="Right:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Prostate_tz_r = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                                   font=("Helvetica", 12), width=120, 
                                                   command=self.change_Prostate_tz_r,
                                                   button_color=self.colors['accent'], 
                                                   border_color=self.colors['accent'], 
                                                   border_width=2, button_hover_color=self.colors['success'], 
                                                   dropdown_hover_color=self.colors['success'], 
                                                   dropdown_fg_color=self.colors['accent'], 
                                                   dropdown_text_color=self.colors['white'])
        self.all_Prostate_tz_r.pack(side="left", padx=(0, 15))
        self.all_Prostate_tz_r.set("low")
        
        CTkLabel(controls_container, text="Left:", font=("Arial", 12, "bold"), 
                text_color=self.colors['secondary']).pack(side="left", padx=(0, 5))
        
        self.all_Prostate_tz_l = CustomCTkComboBox(controls_container, values=["low", "intermediate", "high"], 
                                                   font=("Helvetica", 12), width=120, 
                                                   command=self.change_Prostate_tz_l,
                                                   button_color=self.colors['accent'], 
                                                   border_color=self.colors['accent'], 
                                                   border_width=2, button_hover_color=self.colors['success'], 
                                                   dropdown_hover_color=self.colors['success'], 
                                                   dropdown_fg_color=self.colors['accent'], 
                                                   dropdown_text_color=self.colors['white'])
        self.all_Prostate_tz_l.pack(side="left", padx=(0, 5))
        self.all_Prostate_tz_l.set("low")
        
        # Quick actions frame
        quick_actions_frame = CTkFrame(content_frame, fg_color=self.colors['light'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        quick_actions_frame.pack(fill="x", pady=(20, 0))
        
        quick_label = CTkLabel(quick_actions_frame, text="Quick Actions", 
                              font=("Arial Black", 14), text_color=self.colors['primary'])
        quick_label.pack(pady=15)
        
        buttons_frame = CTkFrame(quick_actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15))
        
        # Reset all button
        reset_btn = CTkButton(buttons_frame, text="Reset All to Low", 
                             fg_color=self.colors['warning'], text_color=self.colors['white'],
                             hover_color="#d97706", corner_radius=8,
                             command=self.reset_all_to_low)
        reset_btn.pack(side="left", padx=5)
        
        # Set all to intermediate button
        intermediate_btn = CTkButton(buttons_frame, text="Set All to Intermediate", 
                                    fg_color=self.colors['secondary'], text_color=self.colors['white'],
                                    hover_color=self.colors['primary'], corner_radius=8,
                                    command=self.set_all_to_intermediate)
        intermediate_btn.pack(side="left", padx=5)
        
        # Set all to high button
        high_btn = CTkButton(buttons_frame, text="Set All to High", 
                            fg_color=self.colors['danger'], text_color=self.colors['white'],
                            hover_color="#b91c1c", corner_radius=8,
                            command=self.set_all_to_high)
        high_btn.pack(side="left", padx=5)

    def reset_all_to_low(self):
        """Reset all values to low"""
        all_combos = [
            self.all_anterior_r, self.all_anterior_l, self.all_Medial_r, self.all_Medial_l,
            self.all_Prostate_PZ_r, self.all_Prostate_PZ_l, self.all_Prostate_tz_r, self.all_Prostate_tz_l
        ]
        
        for combo in all_combos:
            combo.set("low")

    def set_all_to_intermediate(self):
        """Set all values to intermediate"""
        all_combos = [
            self.all_anterior_r, self.all_anterior_l, self.all_Medial_r, self.all_Medial_l,
            self.all_Prostate_PZ_r, self.all_Prostate_PZ_l, self.all_Prostate_tz_r, self.all_Prostate_tz_l
        ]
        
        for combo in all_combos:
            combo.set("intermediate")

    def set_all_to_high(self):
        """Set all values to high"""
        all_combos = [
            self.all_anterior_r, self.all_anterior_l, self.all_Medial_r, self.all_Medial_l,
            self.all_Prostate_PZ_r, self.all_Prostate_PZ_l, self.all_Prostate_tz_r, self.all_Prostate_tz_l
        ]
        
        for combo in all_combos:
            combo.set("high")

    # Navigation and utility methods
    def show_statistics(self):
        """Show statistics dashboard"""
        from tkinter.messagebox import showwarning
        showwarning("Statistics", "you should return to main window to see statistics")

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

    def back_to_prostate_assessment(self):
        """Return to prostate assessment form"""
        # Clear current widgets
        for widget in self.controller.winfo_children():
            widget.destroy()
        
        # Recreate the prostate assessment form
        from prostate_modular.first_gui_data_entry import FirstDataEntryGUI
        self.controller._first_data_entry = FirstDataEntryGUI(self.controller.parent)
        self.controller._first_data_entry.grid(row=0, column=0, sticky="nsew")

    def show_patients(self):
        """Show patients view"""
        showerror("Patients view requested")

    def show_help(self):
        """Show help dialog"""
        from tkinter.messagebox import showinfo
        help_text = """Prostate Zone Assessment Help

This is the Prostate Zone Assessment form (Step 2 of 4).

Navigation:
• Statistics: View comprehensive patient statistics and analytics
• Patients: Return to main patient management dashboard
• Back: Return to patient data entry (Step 1)
• Next: Proceed to biopsy data entry (Step 3)

Prostate Zones:
• Anterior Prostate: Front portion of the prostate
• Medial PZ: Middle peripheral zone
• Posterior PZ: Back peripheral zone
• Transition Zone (TZ): Central transition area

Assessment Levels:
• Very Low: Minimal risk indicators
• Low: Low risk indicators
• Intermediate: Moderate risk indicators
• High: High risk indicators

Features:
• Individual zone assessment for Right and Left sides
• Bulk controls for efficient data entry
• Quick action buttons for common settings
• Professional card-based layout

Tips:
• Assess each zone carefully for both Right and Left sides
• Use bulk controls to set multiple values at once
• Use quick action buttons for common scenarios
• Ensure accurate assessment for medical diagnosis
• All data is automatically saved as you progress"""
        
        showinfo("Help - Prostate Zone Assessment", help_text)

    def edit_image(self, master, i_name, image_path, doc_template, type):
        if master is None:
            master = Toplevel()
        image_marking_app = ImageMarkingApp(master, i_name, image_path, doc_template, type)
        self.doc_saved = True

    def go_to_second(self):
        doc1 = DocxTemplate("DOC/Life/1.docx")
        doc11 = DocxTemplate("DOC/Kidney and Tract/1.docx")
        name = "1.docx"
        if self.entries_1["Hospital"] == "life":
            for key, value in self.entries_1.items():
                if value is None:
                    self.entries_1[key] = ''
            context = {"entries": self.entries_1}
            input_data = [v if v != '' else None for v in self.entries_1.values()]
            first_entry = input_data
            see_none = any(value is None for value in first_entry)
            if see_none:
                ask = askquestion("Confirmation", "Not All Data Are Entered\nDo you want to proceed Data with None Values into DataBase?")
                if ask == "yes":
                    doc1.render(context)
                    doc1.save(name)
                    toplevel = Toplevel(self.controller.parent)
                    self.edit_image(toplevel, "1.png", "DOC/marker1.png", name, "save")
                    self.second_page()
                elif ask == "no":
                    pass
            else:
                self.second_page()
        else:
            for key, value in self.entries_1.items():
                if value is None:
                    self.entries_1[key] = ''
            context = {"entries": self.entries_1}
            input_data = [v if v != '' else None for v in self.entries_1.values()]
            first_entry = input_data
            see_none = any(value is None for value in first_entry)
            if see_none:
                ask = askquestion("Confirmation", "Not All Data Are Entered\nDo you want to proceed Data with None Values into DataBase?")
                if ask == "yes":
                    doc11.render(context)
                    doc11.save(name)
                    toplevel = Toplevel(self.controller.parent)
                    self.edit_image(toplevel, "1.png", "DOC/marker1.png", name, "save")
                    self.second_page()
                elif ask == "no":
                    pass
            else:
                self.second_page()

    # All the change_* and navigation methods become methods of this class
    def change_Prostate_tz_r(self, new: str):
        """Change all Transition Zone Right values"""
        if "TMidprostateR" in self.field_widgets:
            self.field_widgets["TMidprostateR"].set(new)
        if "TBaseR" in self.field_widgets:
            self.field_widgets["TBaseR"].set(new)

    def change_Prostate_tz_l(self, new: str):
        """Change all Transition Zone Left values"""
        if "TMidprostateL" in self.field_widgets:
            self.field_widgets["TMidprostateL"].set(new)
        if "TBaseL" in self.field_widgets:
            self.field_widgets["TBaseL"].set(new)

    def change_Prostate_PZ_r(self, new: str):
        """Change all Posterior PZ Right values"""
        if "PApexR" in self.field_widgets:
            self.field_widgets["PApexR"].set(new)
        if "PMidprostateR" in self.field_widgets:
            self.field_widgets["PMidprostateR"].set(new)
        if "PBaseR" in self.field_widgets:
            self.field_widgets["PBaseR"].set(new)

    def change_Prostate_PZ_l(self, new: str):
        """Change all Posterior PZ Left values"""
        if "PApexL" in self.field_widgets:
            self.field_widgets["PApexL"].set(new)
        if "PMidprostateL" in self.field_widgets:
            self.field_widgets["PMidprostateL"].set(new)
        if "PBaseL" in self.field_widgets:
            self.field_widgets["PBaseL"].set(new)

    def change_medial_r(self, new: str):
        """Change all Medial Right values"""
        if "MApexR" in self.field_widgets:
            self.field_widgets["MApexR"].set(new)
        if "MMidprostateR" in self.field_widgets:
            self.field_widgets["MMidprostateR"].set(new)
        if "MBaseR" in self.field_widgets:
            self.field_widgets["MBaseR"].set(new)

    def change_medial_l(self, new: str):
        """Change all Medial Left values"""
        if "MApexL" in self.field_widgets:
            self.field_widgets["MApexL"].set(new)
        if "MMidprostateL" in self.field_widgets:
            self.field_widgets["MMidprostateL"].set(new)
        if "MBaseL" in self.field_widgets:
            self.field_widgets["MBaseL"].set(new)

    def change_anterior_r(self, new: str):
        """Change all Anterior Right values"""
        if "AApexR" in self.field_widgets:
            self.field_widgets["AApexR"].set(new)
        if "AMidProstateR" in self.field_widgets:
            self.field_widgets["AMidProstateR"].set(new)
        if "ABaseR" in self.field_widgets:
            self.field_widgets["ABaseR"].set(new)

    def change_anterior_l(self, new: str):
        """Change all Anterior Left values"""
        if "AApexL" in self.field_widgets:
            self.field_widgets["AApexL"].set(new)
        if "AMidProstateL" in self.field_widgets:
            self.field_widgets["AMidProstateL"].set(new)
        if "ABaseL" in self.field_widgets:
            self.field_widgets["ABaseL"].set(new)

    def back_to_first(self):
        """Navigate back to the first data entry page"""
        from prostate_modular.first_gui_data_entry import FirstDataEntryGUI
        
        # Clear current widgets
        for widget in self.controller.winfo_children():
            widget.destroy()
        
        # Create and display the first data entry GUI
        self.controller._first_data_entry = FirstDataEntryGUI(self.controller.parent)
        self.controller._first_data_entry.grid(row=0, column=0, sticky="nsew")

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

    def save_to_patients_side(self, patientsinfo_id):
        from prostate_modular.database import DatabaseManager
        db = DatabaseManager("DB/Informations.db")
        db.insert_into_patients_side(patientsinfo_id, self.entries_2)
        db.update_table()
    def go_to_third(self):
        doc1 = DocxTemplate("DOC/Life/2.docx")
        doc11 = DocxTemplate("DOC/Kidney and Tract/2.docx")
        name = "temp/2.docx"
        im_path = "temp/2.png"
        self.collect_entries_2_data()
        # Save to PatientsSide table
        # You must provide the correct patientsinfo_id here. If entries_1 has the ID, use it; otherwise, pass it as an argument.
        patientsinfo_id = self.entries_1.get('US')
        if patientsinfo_id:
            self.save_to_patients_side(patientsinfo_id)
        import tkinter as tk
        from prostate_modular.image_marking import ImageMarkingApp
        from prostate_modular.third_gui_data_entry import ThirdDataEntryGUI
        context = {"entries":self.entries_2}
        if self.entries_1["Hospital"] == "life":
            doc1.render(context)
            doc1.save(name)
        else:
            doc11.render(context)
            doc11.save(name)
        # Open Toplevel for image editing
        toplevel = tk.Toplevel(self.master)
        image_marker = ImageMarkingApp(toplevel, "temp/2.png", "DOC/marker2.png", "temp/2.docx", "save", self.entries_2)
        def check_toplevel_closed():
            if not toplevel.winfo_exists():
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
                    self.master.grid_rowconfigure(0, weight=1)
                    self.master.grid_columnconfigure(0, weight=1)
                    self.master._third_data_entry = ThirdDataEntryGUI(self.master, self.controller, self.entries_1, self.entries_2)
                    self.master._third_data_entry.grid(row=0, column=0, sticky="nsew")
                    self.master.update()
                except Exception as e:
                    showerror("Error creating ThirdDataEntryGUI:", e)
            else:
                self.after(200, check_toplevel_closed)
        check_toplevel_closed()
        
    def collect_entries_2_data(self):
        for key, widget in self.field_widgets.items():
            if hasattr(widget, "get"):
                self.entries_2[key] = widget.get()