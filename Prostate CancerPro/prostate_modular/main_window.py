from prostate_modular.utils import CustomCTkComboBox
from prostate_modular.database import DatabaseManager
from prostate_modular.pops import HospitalPopup, open_dicom_popup
from PIL import Image
from customtkinter import CTkImage, CTkFrame, CTkButton
from customtkinter import CTkLabel, CTkEntry, CTkTabview, CTkScrollableFrame
from tkinter import StringVar, ttk
from prostate_modular.first_gui_data_entry import FirstDataEntryGUI
from prostate_modular.third_gui_data_entry import ThirdDataEntryGUI
from prostate_modular.fourth_gui_data_entry import FourthDataEntryGUI
from prostate_modular.stats import ProstateStatisticsGUI
class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager("DB/Informations.db")
        self.search_text_var = StringVar()
        self.search_text_var_two = StringVar()
        # Remove self.switch_value and theme images
        # self.switch_value = BooleanVar(value=True)  # Remove this line
        # self.light_img = None
        # self.dark_img = None
        self.see = False
        self.first = FirstDataEntryGUI(self.parent, self)
        
        # Color scheme for professional appearance
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
            'border': '#e2e8f0'         # Border color
        }
        
        # Initialize UI components
        self.sidebar_frame = None
        self.count_frame = None
        self.search_container = None
        self.tab_view = None
        self.data_table = None
        self.data_table1 = None
        self.data_table2 = None
        self.data_table3 = None
        
        # Initialize images
        self.track_img = None
        self.analytics_img = None
        self.package_img_data = None
        self.patient_counter_img = None
        self.family_img = None
        self.dre_img = None
        self.add_user_data_img = None
        
        self.setup_images()
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

    def side_bar(self):
        # Destroy any existing sidebar frame to prevent duplicates
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame is not None and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()
        """Create and configure the sidebar with professional styling"""
        # Create sidebar frame
        self.sidebar_frame = CTkFrame(self.parent, fg_color=self.colors['sidebar'], 
                                     bg_color="transparent", corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Configure grid layout
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure((2, 3), weight=0)
        self.parent.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Logo with enhanced styling
        logo_label = CTkButton(self.sidebar_frame, text="", image=self.track_img, compound='left', 
                              fg_color="transparent", width=200, height=150, 
                              font=("Arial-BoldMT", 12), hover_color=self.colors['primary'])
        logo_label.grid(row=0, column=0, pady=(20, 10))
        logo_label.configure(state="disabled")
        
        # Page title
        title_label = CTkLabel(self.sidebar_frame, text="Patient Management", 
                              font=("Arial Black", 16, "bold"), text_color=self.colors['white'])
        title_label.grid(row=1, column=0, pady=(0, 20))
        
        # Navigation buttons
        self.create_nav_button("Statistics", self.analytics_img, row=2, command=self.show_statistics)
        self.create_nav_button("Patients", self.package_img_data, row=3, command=self.display_search_patients)
        self.create_nav_button("Biopsy Entry", self.dre_img, row=4, command=self.display_third_data_entry_gui)
        
        # Progress indicator
        progress_label = CTkLabel(self.sidebar_frame, text="Main Dashboard", 
                                 font=("Arial", 12), text_color=self.colors['accent'])
        progress_label.grid(row=4, column=0, pady=(20, 10))
        
        # Progress bar (full for main dashboard)
        self.progress_frame = CTkFrame(self.sidebar_frame, fg_color=self.colors['dark'], height=8)
        self.progress_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.progress_bar = CTkFrame(self.progress_frame, fg_color=self.colors['accent'], width=250)
        self.progress_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1)
        
        # Bottom section
        bottom_frame = CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, sticky="s", pady=20)
        
        # Add DICOM import button
        self.dicom_btn = CTkButton(bottom_frame, text="Import DICOM", 
                                  fg_color=self.colors['accent'], text_color=self.colors['white'],
                                  hover_color=self.colors['success'], corner_radius=8,
                                  command=lambda: open_dicom_popup(self.parent))
        self.dicom_btn.pack(pady=5)
        
        # Help button
        help_btn = CTkButton(bottom_frame, text="Help", 
                            fg_color=self.colors['secondary'], text_color=self.colors['white'],
                            hover_color=self.colors['primary'], corner_radius=8,
                            command=self.show_help)
        help_btn.pack(pady=5)

    def create_nav_button(self, text, image, row, command=None):
        """Create a navigation button with consistent styling"""
        btn = CTkButton(self.sidebar_frame, text=text, image=image, 
                       compound='left', fg_color="transparent", 
                       hover_color=self.colors['primary'], corner_radius=10,
                       command=command, text_color=self.colors['white'])
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="w")

    def show_statistics(self):
        """Show statistics dashboard"""
        # Clear existing widgets
        for w in self.parent.place_slaves():
            w.place_forget()
        """Add the prostate statistics dashboard to the application"""
        # Create a container frame for the dashboard
        dashboard_frame = CTkFrame(self.parent)
        dashboard_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        
        # Initialize the statistics dashboard
        self.stats_gui = ProstateStatisticsGUI(dashboard_frame)
        self.stats_gui.pack(fill="both", expand=True)

    def create_statistics_dashboard(self):
        """Create a comprehensive statistics dashboard"""
        # Main container
        stats_container = CTkFrame(self.parent, fg_color=self.colors['light'])
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
                                            str(self.get_patient_count()), 
                                            self.colors['accent'], 0, 0)
        
        # Family history card
        family_card = self.create_stat_card(stats_frame, "Family History", 
                                           str(self.get_family_history_count()), 
                                           self.colors['secondary'], 0, 1)
        
        # DRE Hard card
        dre_card = self.create_stat_card(stats_frame, "Hard DRE", 
                                        str(self.get_dre_hard_count()), 
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
        
        • Total Patients: {self.get_patient_count()}
        • Patients with Family History: {self.get_family_history_count()}
        • Patients with Hard DRE: {self.get_dre_hard_count()}
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
        back_btn = CTkButton(stats_container, text="← Back to Dashboard", 
                            fg_color=self.colors['secondary'], text_color=self.colors['white'],
                            hover_color=self.colors['primary'], corner_radius=8,
                            command=self.display_search_patients)
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

    def show_help(self):
        """Show help dialog"""
        from tkinter.messagebox import showinfo
        help_text = """Main Dashboard Help

This is the main patient management dashboard.

Navigation:
• Statistics: View comprehensive patient statistics and analytics
• Patients: Access patient search and management interface
• Import DICOM: Import DICOM medical imaging files

Features:
• View total patient count
• Search and filter patient records
• View detailed patient information
• Export patient data
• Generate reports

Tips:
• Use the search functionality to quickly find patients
• Click on patient records to view detailed information
• Use the tabbed interface to navigate between different data views
• Export data for external analysis"""
        
        showinfo("Help - Main Dashboard", help_text)

    def get_patient_count(self):
        """Get the total number of patients"""
        return self.db.get_patient_count()

    def get_family_history_count(self):
        """Get the count of patients with family history"""
        return self.db.get_family_history_count()

    def get_dre_hard_count(self):
        """Get the count of patients with hard DRE"""
        return self.db.get_dre_hard_count()

    def display_search_patients(self):
        """Display the patient search interface with professional styling"""
        #self.parent.state("normal")
        for w in self.parent.place_slaves():
            w.place_forget()
        for w in self.parent.pack_slaves():
            w.pack_forget()
        for w in self.parent.grid_slaves():
            w.grid_forget()
        self.see = True
        self.side_bar()
        self.create_count_frames()
        self.create_search_interface()
        self.create_data_tables()
        self.update_table()

    def create_count_frames(self):
        """Create the patient count display frames with modern card design"""
        # Create patient Count frame with shadow effect
        self.count_frame = CTkFrame(self.parent, fg_color="transparent", bg_color="transparent", 
                                   corner_radius=20)
        self.count_frame.place(x=250, y=20)
        
        # Patient frame with enhanced styling
        self.patient_frame = CTkFrame(self.count_frame, bg_color="transparent", width=120, 
                                     border_width=2, border_color=self.colors['border'], 
                                     fg_color=self.colors['card'], corner_radius=15)
        self.patient_frame.grid(row=0, column=0, ipadx=15, ipady=10, padx=10)
        
        self.patient_count_var = StringVar()
        self.patient_count_var.set(str(self.get_patient_count()))
        
        self.patient_logo = CTkLabel(master=self.patient_frame, text="", image=self.patient_counter_img, 
                                    fg_color="transparent")
        self.patient_logo.grid(row=0, column=0, padx=(10, 5))
        
        self.patient_label = CTkLabel(master=self.patient_frame, text="Patients Counter", 
                                     fg_color="transparent", font=("Arial Black", 14, "bold"),
                                     text_color=self.colors['primary'])
        self.patient_label.grid(row=0, column=1, padx=5)
        
        self.patient_count = CTkLabel(master=self.patient_frame, textvariable=self.patient_count_var, 
                                     fg_color="transparent", font=("Arial Black", 18, "bold"), 
                                     justify="left", text_color=self.colors['accent'])
        self.patient_count.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Family History frame with consistent styling
        self.family_frame = CTkFrame(master=self.count_frame, bg_color="transparent", 
                                    border_width=2, border_color=self.colors['border'], 
                                    fg_color=self.colors['card'], corner_radius=15)
        self.family_frame.grid(row=0, column=1, padx=15, ipadx=15, ipady=10)
        
        self.family_history_count_var = StringVar()
        self.family_history_count_var.set(str(self.get_family_history_count()))
        
        self.label_img = CTkLabel(master=self.family_frame, text="", image=self.family_img, 
                                 fg_color="transparent")
        self.label_img.grid(row=0, column=0, padx=(10, 5))
        
        self.family_text = CTkLabel(master=self.family_frame, text="+Family History", 
                                   fg_color="transparent", font=("Arial Black", 14, "bold"),
                                   text_color=self.colors['primary'])
        self.family_text.grid(row=0, column=1, padx=5)
        
        self.family_count = CTkLabel(master=self.family_frame, textvariable=self.family_history_count_var, 
                                    font=("Arial Black", 18, "bold"), justify="left", 
                                    fg_color="transparent", text_color=self.colors['accent'])
        self.family_count.grid(row=1, column=0, columnspan=2, pady=5)
        
        # DRE frame with consistent styling
        self.dre_frame = CTkFrame(master=self.count_frame, bg_color="transparent", 
                                 border_width=2, border_color=self.colors['border'], 
                                 fg_color=self.colors['card'], corner_radius=15)
        self.dre_frame.grid(row=0, column=2, padx=15, ipadx=15, ipady=10)
        
        self.dre_hard_count_var = StringVar()
        self.dre_hard_count_var.set(str(self.get_dre_hard_count()))
        
        self.dre_img_label = CTkLabel(master=self.dre_frame, text="", image=self.dre_img, 
                                     fg_color="transparent")
        self.dre_img_label.grid(row=0, column=0, padx=(10, 5))
        
        self.dre_text = CTkLabel(master=self.dre_frame, text="DRE: Hard", 
                                font=("Arial Black", 14, "bold"), fg_color="transparent",
                                text_color=self.colors['primary'])
        self.dre_text.grid(row=0, column=1, padx=5)
        
        self.dre_count = CTkLabel(master=self.dre_frame, textvariable=self.dre_hard_count_var, 
                                 font=("Arial Black", 18, "bold"), justify="left", 
                                 fg_color="transparent", text_color=self.colors['accent'])
        self.dre_count.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Add User Button frame with modern styling
        self.add_frame = CTkFrame(self.parent, bg_color="transparent", fg_color="transparent")
        self.add_frame.place(x=580, y=600)
        
        self.add_user = CTkButton(self.add_frame, image=self.add_user_data_img, text="New Patient", 
                                 font=("Arial Black", 18, "bold"), cursor='hand2', bg_color="transparent", 
                                 fg_color=self.colors['accent'], hover_color=self.colors['success'],
                                 corner_radius=15, border_width=2, border_color=self.colors['border'], command=self.add_patient)
        self.add_user.grid(row=0, column=3, ipadx=45, padx=100, pady=100, columnspan=2)

    def create_search_interface(self):
        """Create the search interface with modern design"""
        self.search_container = CTkFrame(self.parent, fg_color="transparent", bg_color="transparent", corner_radius=20)
        self.search_container.place(x=240, y=190)
        
        # First search row with enhanced styling
        self.search_by = CustomCTkComboBox(self.search_container, justify="center", 
                                          values=["US", "Hospital", "Date", "Name", "Nationality", "Machine", "DRE", "Family"], 
                                          width=220, font=("Helvetica", 16, "bold"), command=self.change_one, 
                                          button_color=self.colors['accent'], border_color=self.colors['accent'], 
                                          border_width=2, button_hover_color=self.colors['success'], 
                                          dropdown_hover_color=self.colors['success'], 
                                          dropdown_fg_color=self.colors['white'], 
                                          dropdown_text_color=self.colors['dark'],
                                          corner_radius=10)
        self.search_by.grid(row=0, column=1, padx=15)
        self.search_by.set("Name")
        self.parent.bind('<Key>', lambda event: self.on_space_key(event, self.search_by))
        self.search_by.bind("<<ComboboxSelected>>", self.perform_search)
        
        self.search_text_var.set(f"Search By {self.search_by.get()}")
        self.search = CTkEntry(self.search_container, text_color="#000", fg_color=self.colors['white'], justify="center", 
                              font=("Helvetica", 16), width=320, textvariable=self.search_text_var, 
                              border_color=self.colors['accent'], border_width=2, corner_radius=10)
        self.search.grid(row=0, column=0, padx=15)
        self.search.bind("<Button-1>", self.clear_text)
        self.search.bind("<Return>", self.perform_search)
        
        self.search_button = CTkButton(self.search_container, text="Search", fg_color=self.colors['accent'], 
                                      font=("Helvetica", 18, "bold"), cursor='hand2', 
                                      hover_color=self.colors['success'], command=self.perform_search,
                                      corner_radius=10, border_width=2, border_color=self.colors['border'])
        self.search_button.grid(row=0, column=2, padx=15)
        
        # Second search row with consistent styling
        self.search_by_two = CustomCTkComboBox(self.search_container, justify="center", 
                                              values=["US", "Hospital", "Date", "Name", "Nationality", "Machine", "DRE", "Family"], 
                                              width=220, font=("Helvetica", 16, "bold"), command=self.change_two, 
                                              button_color=self.colors['accent'], border_color=self.colors['accent'], 
                                              border_width=2, button_hover_color=self.colors['success'], 
                                              dropdown_hover_color=self.colors['success'], 
                                              dropdown_fg_color=self.colors['white'], 
                                              dropdown_text_color=self.colors['dark'],
                                              corner_radius=10)
        self.search_by_two.grid(row=1, column=1, padx=15, pady=10)
        self.search_by_two.set("Date")
        self.parent.bind("<Key>", lambda event: self.on_space_key(event, self.search_by_two))
        self.search_by_two.bind("<<ComboboxSelected>>", self.perform_search)
        
        self.search_text_var_two.set(f"Search By {self.search_by_two.get()}")
        self.search_two = CTkEntry(self.search_container, text_color="#000", fg_color=self.colors['white'], justify="center", 
                                  font=("Helvetica", 16), width=320, textvariable=self.search_text_var_two, 
                                  border_color=self.colors['accent'], border_width=2, corner_radius=10)
        self.search_two.grid(row=1, column=0, padx=15, pady=10)
        self.search_two.bind("<Button-1>", self.clear_text_2)
        self.search_two.bind("<Return>", self.perform_search)

    def create_data_tables(self):
        """Create the data tables with tabs and modern styling"""
        self.tab_view = CTkTabview(self.parent, fg_color="transparent", 
                                  segmented_button_fg_color=self.colors['light'],
                                  segmented_button_selected_color=self.colors['accent'],
                                  segmented_button_selected_hover_color=self.colors['success'],
                                  segmented_button_unselected_hover_color=self.colors['border'],
                                  text_color=self.colors['dark'])
        self.tab_view.place(x=240, y=280)
        
        # First Page
        self.tab_view.add("First Page")
        self.create_first_table()
        
        # Second Page
        self.tab_view.add("second Page")
        self.create_second_table()
        
        # Third Page
        self.tab_view.add("Third Page")
        self.create_third_table()
        
        # Fourth Page
        self.tab_view.add("Fourth Page")
        self.create_fourth_table()
        
        self.data_table.bind(
            "<<TreeviewSelect>>",
            lambda event: HospitalPopup.on_tree_select(event, self.data_table, self.parent, self)
        )

    def create_first_table(self):
        """Create the first table (main patient data) with enhanced styling"""
        self.table_container_first = CTkScrollableFrame(self.tab_view.tab("First Page"), width=1124, height=250,fg_color="transparent", orientation="horizontal")
        self.table_container_first.grid(row=0, column=0)

        self.columns = ["US Code", "Hospital", "Date",  "Name", "Age", "Nationality", "Reffered By", "MRI Results", 
                       "FPSA", "TPSA", "PSA", "Bioposy Set", "Machine Used", "DRE", "Family History", 
                       "Whole Gland TD mm", "Whole Gland Height mm", "Whole Gland Length mm", "Whole Gland Volume cc", 
                       "Adenoma TD mm", "Adenoma Height mm", "Adenoma Length mm", "Adenoma Volume cc", 
                       "Urinary Bladder", "Bladder Neck", "Seminal Vesicles", "Vasa Deferentia", "Ejaculatory Ducts", "Lesions"]
        
        self.data_table = ttk.Treeview(self.table_container_first, padding=8, columns=self.columns, 
                                       show="headings", style="Treeview", height=12, )
        self.data_table.grid(row=0, column=0, sticky="nsew")
        
        for col in self.columns:
            self.data_table.heading(col, text=col)
            self.data_table.column(col, width=120, anchor="center", stretch=True)
        
        # Configure styles with modern appearance
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=('Arial Black', 12, 'bold'), 
                            background=self.colors['accent'], foreground=self.colors['white'])
        self.style.configure("Treeview", font=('Arial', 11), rowheight=32, 
                            background=self.colors['white'], fieldbackground=self.colors['white'], 
                            borderwidth=1, bordercolor=self.colors['border'])
        self.style.map('Treeview', background=[('selected', self.colors['secondary'])], 
                       foreground=[('selected', self.colors['white'])])
        
        self.data_table.tag_configure("oddrow", background=self.colors['light'])
        self.data_table.tag_configure("evenrow", background=self.colors['white'])

    def create_second_table(self):
        """Create the second table (prostate zones) with consistent styling"""
        self.table_container_second = CTkScrollableFrame(self.tab_view.tab("second Page"), width=1124, 
                                                        fg_color="transparent", orientation="horizontal")
        self.table_container_second.grid(row=0, column=0)
        
        self.columns_two = ["Anterior RIGHT APEX Apical Horn", "Anterior LEFT APEX Apical Horn", 
                           "Anterior RIGHT Med Prostate", "Anterior LEFT Med Prostate", "Anterior RIGHT Base", 
                           "Anterior LEFT Base", "Medial PZ RIGHT Apex", "Medial PZ LEFT Apex", 
                           "Medial PZ RIGHT Med Prostate", "Medial PZ LEFT Med Prostate", "Medial PZ RIGHT Base", 
                           "Medial PZ LEFT Base", "Posterior PZ RIGHT Apex", "Posterior PZ LEFT Apex", 
                           "Posterior PZ RIGHT MED Prostate", "Posterior PZ LEFT Med Prostate", 
                           "Posterior PZ RIGHT Base", "Posterior PZ LEFT Base", "Transition RIGHT Med Prostate", 
                           "Transition LEFT Med Prostate", "Transition RIGHT Base", "Transition LEFT BASE"]
        
        self.data_table1 = ttk.Treeview(self.table_container_second, padding=8, columns=self.columns_two, 
                                        show="headings", style="Treeview", height=10)
        self.data_table1.grid(row=0, column=0, sticky="nsew")
        
        for col in self.columns_two:
            self.data_table1.heading(col, text=col)
            self.data_table1.column(col, width=120, anchor="center", stretch=True)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['accent'], foreground=self.colors['white'])
        self.style.configure("Treeview", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['white'], foreground=self.colors['dark'])

    def create_third_table(self):
        """Create the third table (biopsy data 1-10) with consistent styling"""
        self.table_container_third = CTkScrollableFrame(self.tab_view.tab("Third Page"), width=1124, 
                                                       fg_color="transparent", orientation="horizontal")
        self.table_container_third.grid(row=0, column=0)
        
        self.columns_three = ["Site of biopsy 1","US risk features 1","no of cores 1","BPH 1","Prostatitis 1","Atrophy 1","BasalCellHqPerPlasiq 1","PIN 1","ca_prostate 1","Cancer Grade 1",
                              "Site of biopsy 2","US risk features 2","no of cores 2","BPH 2","Prostatitis 2","Atrophy 2","BasalCellHqPerPlasiq 2","PIN 2","ca_prostate 2","Cancer Grade 2",
                              "Site of biopsy 3","US risk features 3","no of cores 3","BPH 3","Prostatitis 3","Atrophy 3","BasalCellHqPerPlasiq 3","PIN 3","ca_prostate 3","Cancer Grade 3",
                              "Site of biopsy 4","US risk features 4","no of cores 4","BPH 4","Prostatitis 4","Atrophy 4","BasalCellHqPerPlasiq 4","PIN 4","ca_prostate 4","Cancer Grade 4",
                              "Site of biopsy 5","US risk features 5","no of cores 5","BPH 5","Prostatitis 5","Atrophy 5","BasalCellHqPerPlasiq 5","PIN 5","ca_prostate 5","Cancer Grade 5",
                              "Site of biopsy 6","US risk features 6","no of cores 6","BPH 6","Prostatitis 6","Atrophy 6","BasalCellHqPerPlasiq 6","PIN 6","ca_prostate 6","Cancer Grade 6",
                              "Site of biopsy 7","US risk features 7","no of cores 7","BPH 7","Prostatitis 7","Atrophy 7","BasalCellHqPerPlasiq 7","PIN 7","ca_prostate 7","Cancer Grade 7",
                              "Site of biopsy 8","US risk features 8","no of cores 8","BPH 8","Prostatitis 8","Atrophy 8","BasalCellHqPerPlasiq 8","PIN 8","ca_prostate 8","Cancer Grade 8",
                              "Site of biopsy 9","US risk features 9","no of cores 9","BPH 9","Prostatitis 9","Atrophy 9","BasalCellHqPerPlasiq 9","PIN 9","ca_prostate 9","Cancer Grade 9",
                              "Site of biopsy 10","Us risk features 10","no of cores 10","BPH 10","Prostatitis 10","Atrophy 10","BasalCellHqPerPlasiq 10","PIN 10","ca_prostate 10","Cancer Grade 10"]
        
        self.data_table2 = ttk.Treeview(self.table_container_third, padding=8, columns=self.columns_three, 
                                        show="headings", style="Treeview", height=10)
        self.data_table2.grid(row=0, column=0, sticky="nsew")
        
        for col in self.columns_three:
            self.data_table2.heading(col, text=col)
            self.data_table2.column(col, width=120, anchor="center", stretch=True)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['accent'], foreground=self.colors['white'])
        self.style.configure("Treeview", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['white'], foreground=self.colors['dark'])

    def create_fourth_table(self):
        """Create the fourth table (biopsy data 11-20) with consistent styling"""
        self.table_container_fourth = CTkScrollableFrame(self.tab_view.tab("Fourth Page"), width=1124, 
                                                        fg_color="transparent", orientation="horizontal")
        self.table_container_fourth.grid(row=0, column=0)
        
        self.columns_fourth = [ "Site of biopsy 11","US risk features 11","no of cores 11","BPH 11","Prostatitis 11","Atrophy 11","BasalCellHqPerPlasiq 11","PIN 11","ca_prostate 11","cancer grade 11",
                                "Site of biopsy 12","US risk features 12","no of cores 12","BPH 12","Prostatitis 12","Atrophy 12","BasalCellHqPerPlasiq 12","PIN 12","ca_prostate 12","cancer grade 12",
                                "Site of biopsy 13","US risk features 13","no of cores 13","BPH 13","Prostatitis 13","Atrophy 13","BasalCellHqPerPlasiq 13","PIN 13","ca_prostate 13","cancer grade 13",
                                "Site of biopsy 14","US risk features 14","no of cores 14","BPH 14","Prostatitis 14","Atrophy 14","BasalCellHqPerPlasiq 14","PIN 14","ca_prostate 14","cancer grade 14",
                                "Site of biopsy 15","US risk features 15","no of cores 15","BPH 15","Prostatitis 15","Atrophy 15","BasalCellHqPerPlasiq 15","PIN 15","ca_prostate 15","cancer grade 15",
                                "Site of biopsy 16","US risk features 16","no of cores 16","BPH 16","Prostatitis 16","Atrophy 16","BasalCellHqPerPlasiq 16","PIN 16","ca_prostate 16","cancer grade 16",
                                "Site of biopsy 17","US risk features 17","no of cores 17","BPH 17","Prostatitis 17","Atrophy 17","BasalCellHqPerPlasiq 17","PIN 17","ca_prostate 17","cancer grade 17",
                                "Site of biopsy 18","US risk features 18","no of cores 18","BPH 18","Prostatitis 18","Atrophy 18","BasalCellHqPerPlasiq 18","PIN 18","ca_prostate 18","cancer grade 18",
                                "Site of biopsy 19","US risk features 19","no of cores 19","BPH 19","Prostatitis 19","Atrophy 19","BasalCellHqPerPlasiq 19","PIN 19","ca_prostate 19","cancer grade 19",
                                "Site of biopsy 20","US risk features 20","no of cores 20","BPH 20","Prostatitis 20","Atrophy 20","BasalCellHqPerPlasiq 20","PIN 20","ca_prostate 20","cancer grade 20"]
        
        self.data_table3 = ttk.Treeview(self.table_container_fourth, padding=8, columns=self.columns_fourth, 
                                        show="headings", style="Treeview", height=10)
        self.data_table3.grid(row=0, column=0, sticky="nsew")
        
        for col in self.columns_fourth:
            self.data_table3.heading(col, text=col)
            self.data_table3.column(col, width=120, anchor="center", stretch=True)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['accent'], foreground=self.colors['white'])
        self.style.configure("Treeview", font=('Helvetica', 10, 'bold'), 
                            background=self.colors['white'], foreground=self.colors['dark'])

    def clear_text(self, event):
        """Clear search text when clicked"""
        if "Search By" in self.search_text_var.get():
            self.search_text_var.set("")

    def clear_text_2(self, event=None):
        """Clear second search text when clicked"""
        if "Search By" in self.search_text_var_two.get():
            self.search_text_var_two.set("")

    def change_two(self, ch):
        """Update second search placeholder text"""
        self.search_text_var_two.set(f"Search By {self.search_by_two.get()}")

    def change_one(self, ch):
        """Update first search placeholder text"""
        self.search_text_var.set(f"Search By {self.search_by.get()}")

    def on_space_key(self, event, combobox_var):
        """Handle space key press for combobox"""
        if event.widget == combobox_var and event.char == ' ':
            combobox_var.event_generate("<<ComboboxSelected>>")

    def perform_search(self, event=None):
        """Perform search based on current criteria"""
        search_category_one = self.search_by.get()
        search_text_one = self.search_text_var.get().replace(f"Search By {search_category_one}", "").strip()
        search_category_two = self.search_by_two.get()
        search_text_two = self.search_text_var_two.get().replace(f"Search By {search_category_two}", "").strip()
        
        # Perform search using database manager
        results = self.db.perform_search(search_category_one, search_text_one, search_category_two, search_text_two)
        
        # Clear existing data from tables
        self.data_table.delete(*self.data_table.get_children())
        self.data_table1.delete(*self.data_table1.get_children())
        self.data_table2.delete(*self.data_table2.get_children())
        self.data_table3.delete(*self.data_table3.get_children())
        
        # Populate tables with search results
        if results:
            # Populate first table (PatientsInfo)
            for i, row in enumerate(results.get('patients_info', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate second table (PatientsSide)
            for i, row in enumerate(results.get('patients_side', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table1.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate third table (FirstBottles)
            for i, row in enumerate(results.get('first_bottles', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table2.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate fourth table (SecondBottles)
            for i, row in enumerate(results.get('second_bottles', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table3.insert("", "end", values=row[1:], tags=(tag,))

    def update_table(self):
        """Update the data tables with current data from database"""
        # Get all data from database
        results = self.db.update_table()
        
        # Clear existing data from tables
        self.data_table.delete(*self.data_table.get_children())
        self.data_table1.delete(*self.data_table1.get_children())
        self.data_table2.delete(*self.data_table2.get_children())
        self.data_table3.delete(*self.data_table3.get_children())
        
        # Populate tables with data
        if results:
            # Populate first table (PatientsInfo)
            for i, row in enumerate(results.get('patients_info', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate second table (PatientsSide)
            for i, row in enumerate(results.get('patients_side', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table1.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate third table (FirstBottles)
            for i, row in enumerate(results.get('first_bottles', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table2.insert("", "end", values=row[1:], tags=(tag,))
            
            # Populate fourth table (SecondBottles)
            for i, row in enumerate(results.get('second_bottles', [])):
                tag = "oddrow" if i % 2 == 0 else "evenrow"
                self.data_table3.insert("", "end", values=row[1:], tags=(tag,))     
        # Update count displays
        self.patient_count_var.set(str(self.get_patient_count()))
        self.family_history_count_var.set(str(self.get_family_history_count()))
        self.dre_hard_count_var.set(str(self.get_dre_hard_count()))

    def add_patient(self):
        """Add a new patient - opens the first data entry GUI"""
        # Import the FirstDataEntryGUI class
        from prostate_modular.first_gui_data_entry import FirstDataEntryGUI
        
        # Clear existing widgets
        for w in self.parent.place_slaves():
            w.place_forget()
        
        # Create and display the first data entry GUI
        self.first_data_entry = FirstDataEntryGUI(self.parent, self)
        self.first_data_entry.place(x=0, y=0, relwidth=1, relheight=1)

    def set_entries_for_third_data_entry(self, entries_1, entries_2):
        self.entries_1 = entries_1
        self.entries_2 = entries_2

    def display_third_data_entry_gui(self):
        self.clear_data_entry_gui()
        # Ensure entries_1 and entries_2 are always set
        if not hasattr(self, 'entries_1') or self.entries_1 is None:
            self.entries_1 = {}
        if not hasattr(self, 'entries_2') or self.entries_2 is None:
            self.entries_2 = {}
        print("in third:",self.entries_1)
        self.third_data_entry_gui = ThirdDataEntryGUI(self.parent, self, self.entries_1, self.entries_2)
        self.third_data_entry_gui.grid(row=0, column=1, sticky='nsew', padx=(0, 30), pady=30)

    def display_fourth_data_entry_gui(self):
        # Destroy any existing sidebar in the parent to prevent duplicate sidebars
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame is not None and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()
        self.clear_data_entry_gui()
        # Ensure entries_1 and entries_2 are always set
        if not hasattr(self, 'entries_1') or self.entries_1 is None:
            self.entries_1 = {}
        if not hasattr(self, 'entries_2') or self.entries_2 is None:
            self.entries_2 = {}
        print("in fourth:",self.entries_1)
        # Ensure parent grid is correct
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.parent.grid_columnconfigure(1, weight=1)  # Main content expands
        # Do NOT add sidebar here; the data entry GUI will add its own sidebar
        self.fourth_data_entry_gui = FourthDataEntryGUI(self.parent, self.entries_1, self.entries_2)
        self.fourth_data_entry_gui.grid(row=0, column=1, sticky='nsew', padx=(0, 30), pady=30)

    def clear_data_entry_gui(self):
        # Destroy all widgets in column 1 (main content area)
        for widget in self.parent.grid_slaves():
            info = widget.grid_info()
            if int(info.get('column', 0)) == 1:
                widget.destroy()
        # Force destroy any lingering ThirdDataEntryGUI or FourthDataEntryGUI
        from prostate_modular.third_gui_data_entry import ThirdDataEntryGUI
        from prostate_modular.fourth_gui_data_entry import FourthDataEntryGUI
        for widget in self.parent.winfo_children():
            if isinstance(widget, (ThirdDataEntryGUI, FourthDataEntryGUI)):
                widget.destroy()