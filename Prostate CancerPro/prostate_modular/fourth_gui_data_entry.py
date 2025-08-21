from customtkinter import CTkButton, CTkLabel, CTkFrame, CTkImage
from customtkinter import CTkEntry, CTkCheckBox, CTkTabview, CTkScrollableFrame
from prostate_modular.utils import CustomCTkComboBox
from tkinter.messagebox import showinfo, showerror
from tkinter import W
from prostate_modular.logic_for_fourth import FourthLogic
from prostate_modular.constant import entries_3, entries_4
from prostate_modular.backend import Backend
class FourthDataEntryGUI(CTkFrame):
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
        self.logic = FourthLogic(self)
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
        self.parent = parent
        self.logic = FourthLogic(self)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.side_bar()
        self.last_twen()

    def side_bar(self):
        # Color scheme (should ideally be shared, but for now, define here)
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
        # Setup images (logo, analytics, patient)
        try:
            from PIL import Image
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
        self.sidebar_frame = CTkFrame(self, fg_color=self.colors['sidebar'], corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(0, weight=0)  # Logo
        self.sidebar_frame.grid_rowconfigure(1, weight=0)  # Title
        # Configure other rows...
        self.sidebar_frame.grid_rowconfigure(6, weight=1)  # For progress bar
        self.sidebar_frame.grid_rowconfigure(7, weight=0)  # Bottom section
        # Logo
        if hasattr(self, 'logo_img') and self.logo_img:
            logo_label = CTkButton(self.sidebar_frame, text="", image=self.logo_img, compound='left', fg_color="transparent", width=200, height=150, font=("Arial-BoldMT", 12), hover_color=self.colors['primary'])
            logo_label.grid(row=0, column=0, pady=(20, 10))
            logo_label.configure(state="disabled")
        # Title
        title_label = CTkLabel(self.sidebar_frame, text="Biopsy Bottles 11-20", font=("Arial Black", 16, "bold"), text_color=self.colors['white'])
        title_label.grid(row=1, column=0, pady=(0, 20))
        # Navigation buttons
        self.create_nav_button("Statistics", getattr(self, 'analytics_img', None), row=2, command=self.show_statistics)
        self.create_nav_button("Patients", getattr(self, 'patient_img', None), row=3, command=self.go_to_main_window)
        self.create_nav_button("Back 1-10", None, row=4, command=(lambda: self.controller.display_third_data_entry_gui() if self.controller else None))
        # Progress indicator
        progress_label = CTkLabel(self.sidebar_frame, text="Step 4 of 4", font=("Arial", 12), text_color=self.colors['accent'])
        progress_label.grid(row=5, column=0, pady=(20, 10))
        # Progress bar
        self.progress_frame = CTkFrame(self.sidebar_frame, fg_color=self.colors['dark'], height=8)
        self.progress_frame.grid(row=6, column=0, padx=(0, 20), pady=(0, 20), sticky="ew")
        self.progress_bar = CTkFrame(self.progress_frame, fg_color=self.colors['accent'], width=250)
        self.progress_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1)
        # Bottom section
        bottom_frame = CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=7, column=0, sticky="s", pady=20)
        help_btn = CTkButton(bottom_frame, text="Help", fg_color=self.colors['accent'], text_color=self.colors['white'], hover_color=self.colors['success'], corner_radius=8, command=self.show_help)
        help_btn.pack(pady=5)

    def create_nav_button(self, text, image, row, command=None):
        btn = CTkButton(self.sidebar_frame, text=text, image=image, compound='left', fg_color="transparent", hover_color=self.colors['primary'], corner_radius=10, command=command, text_color=self.colors['white'])
        btn.grid(row=row, column=0, padx=(0, 20), pady=10, sticky="w")

    def show_statistics(self):
        """Show statistics dashboard"""
        from tkinter.messagebox import showinfo, showwarning        
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
            "Biopsy Bottles 11-20 Help\n\n"
            "This section allows you to enter detailed biopsy data for bottles 11-20.\n\n"
            "Navigation:\n"
            "• Statistics: View patient statistics and analytics\n"
            "• Patients: Return to main dashboard\n"
            "• Back to Bottles 1-10: Return to bottles 1-10 data entry\n\n"
            "Data Entry:\n"
            "• For each bottle, enter the site of biopsy, US risk features, number of cores, and pathology findings.\n"
            "• Use the dropdowns and entry fields for each parameter.\n"
            "• Ensure all required fields are filled for accurate record keeping.\n\n"
            "Tips:\n"
            "• Double-check each entry before proceeding.\n"
            "• Use the Export button to save or print the current data.\n"
            "• Use the sidebar to quickly navigate between sections.\n"
        )
        showinfo("Help - Biopsy Bottles 11-20", help_text)

    def last_twen(self):
        # Main content frame
        content_frame = CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=30)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Header label
        header = CTkLabel(content_frame, text="Biopsy Bottles 11-20", font=("Arial Black", 20, "bold"), text_color="#1e3a8a")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Tabview for bottles 11-20
        self.tab_view_bottles_2 = CTkTabview(
            content_frame,
            fg_color="transparent",
            border_color="blue",
            border_width=2,
            corner_radius=12,
            cursor='arrow',
            width=1000
        )
        self.tab_view_bottles_2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_view_bottles_2.add("Bottle-11")
        self.bottle_11()
        self.tab_view_bottles_2.add("Bottle-12")
        self.bottle_12()
        self.tab_view_bottles_2.add("Bottle-13")
        self.bottle_13()
        self.tab_view_bottles_2.add("Bottle-14")
        self.bottle_14()
        self.tab_view_bottles_2.add("Bottle-15")
        self.bottle_15()
        self.tab_view_bottles_2.add("Bottle-16")
        self.bottle_16()
        self.tab_view_bottles_2.add("Bottle-17")
        self.bottle_17()
        self.tab_view_bottles_2.add("Bottle-18")
        self.bottle_18()
        self.tab_view_bottles_2.add("Bottle-19")
        self.bottle_19()
        self.tab_view_bottles_2.add("Bottle-20")
        self.bottle_20()

        # Back button at the bottom
        back_bottles = CTkButton(
            content_frame,
            text="Back 1-10",
            width=350,
            height=40,
            font=("Arial Black", 16),
            fg_color="#10b981",
            text_color="#fff",
            hover_color="#059669",
            corner_radius=10,
            command=lambda: self.controller.display_third_data_entry_gui() if self.controller else None
        )
        back_bottles.grid(row=2, column=0, sticky="ew", pady=(20, 0), padx=10)
    def get_data_frame_11(self):
        self.entries_4["Site_of_biopsy_11"] = self.entry_bottle11.get()
        self.entries_4["US_risk_features_11"] = self.checkbox_option_risk11.get()
        self.entries_4["no_of_cores_11"] = self.entry_no_of_cores11.get()
        self.entries_4["BPH_11"] = self.entry_bph11.get()
        self.entries_4["Prostatitis_11"] = self.entry_Prostatitis11.get()
        self.entries_4["Atrophy_11"] = self.entry_A11.get()
        self.entries_4["BasalCellHqPerPlasiq_11"] = self.entry_BHPPlasiq_11.get()
        self.entries_4["PIN_11"] = self.entry_pin_11.get()
        self.entries_4["ca_prostate_11"] = self.option_risk11.get()
        self.entries_4["ca_grade_11"]= self.entry_grade_11.get()
    def bottle_11(self):
        self.frame_eleven = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-11"), height=1000, fg_color="transparent", corner_radius=0)
        self.frame_eleven.pack(fill="both", expand=True)
        
        # Section header for Bottle 11
        section_header = CTkLabel(self.frame_eleven, text="Bottle 11", font=("Arial Black", 18, "bold"), 
                                text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, 
                                pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))
        
        # Grouped entry fields in a card-like frame
        entry_card = CTkFrame(self.frame_eleven, fg_color="#f8fafc", corner_radius=12, 
                            border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")
        
        # Row 1: Site of biopsy
        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottle11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottle11.grid(row=0, column=1, padx=12, pady=6, sticky=W)
        
        # Row 2: US Risk Features
        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk11 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], 
                                                    width=220, font=("Helvetica", 16), button_color="#2A8C55", 
                                                    border_color="#2A8C55", border_width=2, button_hover_color="#207244", 
                                                    dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", 
                                                    dropdown_text_color="#fff")
        self.checkbox_option_risk11.set("")
        self.checkbox_option_risk11.grid(row=1, column=1, padx=12, pady=6, sticky=W)
        
        # Row 3: no. of Cores
        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores11.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        
        # Row 4: BPH
        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph11.grid(row=3, column=1, padx=12, pady=6, sticky=W)
        
        # Row 5: Prostatitis
        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis11.grid(row=4, column=1, padx=12, pady=6, sticky=W)
        
        # Row 6: Atrophy
        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A11.grid(row=5, column=1, padx=12, pady=6, sticky=W)
        
        # Row 7: Basal Cell Hq Per Plasiq
        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_11.grid(row=6, column=1, padx=12, pady=6, sticky=W)
        
        # Row 8: PIN
        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_11.grid(row=7, column=1, padx=12, pady=6, sticky=W)
        
        # Row 9: Cancer Prostate
        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk11 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), 
                                            button_color="#2A8C55", border_color="#2A8C55", border_width=2, 
                                            button_hover_color="#207244", dropdown_hover_color="#207244", 
                                            dropdown_fg_color="#2A8C55", dropdown_text_color="#fff",
                                            command=lambda value: self.logic.gleason_event(None, 11))
        self.option_risk11.set("")
        self.option_risk11.grid(row=8, column=1, padx=12, pady=6, sticky=W)
        
        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_11 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_11.grid(row=9, column=1, padx=12, pady=6, sticky=W)
        
        # Gleason Patterns frame (visually separated)
        self.gleason_frame_11 = CTkFrame(self.frame_eleven, fg_color="#f1f5f9", border_color="#e2e8f0", 
                                    border_width=1, corner_radius=10)
        self.gleason_frame_11.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        
        CTkLabel(self.gleason_frame_11, text="Gleason Patterns", text_color="#1e3a8a", 
                font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)
        
        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", 
            "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", 
            "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_11, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_11", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(11, idx, cb.get()))
            cb.grid(row=1 + (idx-1)//10, column=(idx-1)%10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
        
        # Buttons row (centered)
        button_row = CTkFrame(self.frame_eleven, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        
        button211 = CTkButton(button_row, text="Get Bottle-11", width=150, height=40, 
                            command=self.get_data_frame_11, fg_color="#10b981")
        button211.pack(side="left", padx=12)
        
        button_export = CTkButton(button_row, text="Export", width=200, height=40, 
                                command=self.export_fourth)
        button_export.pack(side="left", padx=12)

    

    def get_data_frame_12(self):
        self.entries_4["Site_of_biopsy_12"] = self.entry_bottles12.get()
        self.entries_4["US_risk_features_12"] = self.checkbox_option_risk12.get()
        self.entries_4["no_of_cores_12"] = self.entry_no_of_cores12.get()
        self.entries_4["BPH_12"] = self.entry_bph12.get()
        self.entries_4["Prostatitis_12"] = self.entry_Prostatitis12.get()
        self.entries_4["Atrophy_12"] = self.entry_A12.get()
        self.entries_4["BasalCellHqPerPlasiq_12"] = self.entry_BHPPlasiq_12.get()
        self.entries_4["PIN_12"] = self.entry_pin_12.get()
        self.entries_4["ca_grade_12"]= self.entry_grade_12.get()
    def bottle_12(self):
        self.twelve_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-12"), height=1000, fg_color="transparent", corner_radius=0)
        self.twelve_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.twelve_frame, text="Bottle 12", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.twelve_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles12.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk12 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk12.set("")
        self.checkbox_option_risk12.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores12.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph12.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis12.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A12.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_12.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_12.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk12 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 12))
        self.option_risk12.set("")
        self.option_risk12.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_12 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_12.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_12 = CTkFrame(self.twelve_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_12.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_12, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_12 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_12, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_12", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(12, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_12.append(cb)

        button_row = CTkFrame(self.twelve_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button12 = CTkButton(button_row, text="Get Bottle-12", width=150, height=40, command=self.get_data_frame_12, fg_color="#10b981")
        button12.pack(side="left", padx=12)
        button42 = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth)
        button42.pack(side="left", padx=12)


    def get_data_frame_13(self):
        self.entries_4["Site_of_biopsy_13"] = self.entry_bottles13.get()
        self.entries_4["US_risk_features_13"] = self.checkbox_option_risk13.get()
        self.entries_4["no_of_cores_13"] = self.entry_no_of_cores13.get()
        self.entries_4["BPH_13"] = self.entry_bph13.get()
        self.entries_4["Prostatitis_13"] = self.entry_Prostatitis13.get()
        self.entries_4["Atrophy_13"] = self.entry_A13.get()
        self.entries_4["BasalCellHqPerPlasiq_13"] = self.entry_BHPPlasiq_13.get()
        self.entries_4["PIN_13"] = self.entry_pin_13.get()
        self.entries_4["ca_grade_13"]= self.entry_grade_13.get()
    def bottle_13(self):
        self.thirteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-13"), height=1000, fg_color="transparent", corner_radius=0)
        self.thirteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.thirteen_frame, text="Bottle 13", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.thirteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles13.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk13 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk13.set("")
        self.checkbox_option_risk13.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores13.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph13.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis13.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A13.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_13.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_13.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk13 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 13))
        self.option_risk13.set("")
        self.option_risk13.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_13 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_13.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_13 = CTkFrame(self.thirteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_13.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_13, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_13 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_13, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_13", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(13, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_13.append(cb)

        button_row = CTkFrame(self.thirteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button13 = CTkButton(button_row, text="Get Bottle-13", width=150, height=40, command=self.get_data_frame_13, fg_color="#10b981")
        button13.pack(side="left", padx=12)
        button_export = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth)
        button_export.pack(side="left", padx=12)


    def get_data_frame_14(self):
        self.entries_4["Site_of_biopsy_14"] = self.entry_bottles14.get()
        self.entries_4["US_risk_features_14"] = self.checkbox_option_risk14.get()
        self.entries_4["no_of_cores_14"] = self.entry_no_of_cores14.get()
        self.entries_4["BPH_14"] = self.entry_bph14.get()
        self.entries_4["Prostatitis_14"] = self.entry_Prostatitis14.get()
        self.entries_4["Atrophy_14"] = self.entry_A14.get()
        self.entries_4["BasalCellHqPerPlasiq_14"] = self.entry_BHPPlasiq_14.get()
        self.entries_4["PIN_14"] = self.entry_pin_14.get()
        self.entries_4["ca_grade_14"]= self.entry_grade_14.get()
    def bottle_14(self):
        self.fourteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-14"), height=1000, fg_color="transparent", corner_radius=0)
        self.fourteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.fourteen_frame, text="Bottle 14", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.fourteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles14.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk14 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk14.set("")
        self.checkbox_option_risk14.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores14.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph14.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis14.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A14.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_14.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_14.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk14 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 14))
        self.option_risk14.set("")
        self.option_risk14.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_14 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_14.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_14 = CTkFrame(self.fourteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_14.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_14, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_14 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_14, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_14", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(14, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_14.append(cb)

        button_row = CTkFrame(self.fourteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button14 = CTkButton(button_row, text="Get Bottle-14", width=150, height=40, command=self.get_data_frame_14, fg_color="#10b981")
        button14.pack(side="left", padx=12)
        button_export = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth)
        button_export.pack(side="left", padx=12)

    def get_data_frame_15(self):
        self.entries_4["Site_of_biopsy_15"] = self.entry_bottles15.get()
        self.entries_4["US_risk_features_15"] = self.checkbox_option_risk15.get()
        self.entries_4["no_of_cores_15"] = self.entry_no_of_cores15.get()
        self.entries_4["BPH_15"] = self.entry_bph15.get()
        self.entries_4["Prostatitis_15"] = self.entry_Prostatitis15.get()
        self.entries_4["Atrophy_15"] = self.entry_A15.get()
        self.entries_4["BasalCellHqPerPlasiq_15"] = self.entry_BHPPlasiq_15.get()
        self.entries_4["PIN_15"] = self.entry_pin_15.get()
        self.entries_4["ca_grade_15"]= self.entry_grade_15.get()
    def bottle_15(self):
        self.fifteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-15"), height=1000, fg_color="transparent", corner_radius=0)
        self.fifteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.fifteen_frame, text="Bottle 15", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.fifteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles15.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk15 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk15.set("")
        self.checkbox_option_risk15.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores15.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph15.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis15.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A15.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_15.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_15.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk15 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 15))
        self.option_risk15.set("")
        self.option_risk15.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_15 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_15.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_15 = CTkFrame(self.fifteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_15.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_15, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_15 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_15, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_15", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(15, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_15.append(cb)

        button_row = CTkFrame(self.fifteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button15 = CTkButton(button_row, text="Get Bottle-15", width=150, height=40, command=self.get_data_frame_15, fg_color="#10b981")
        button15.pack(side="left", padx=12)
        button_export = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth)
        button_export.pack(side="left", padx=12)

    def get_data_frame_16(self):
        self.entries_4["Site_of_biopsy_16"] = self.entry_bottles16.get()
        self.entries_4["US_risk_features_16"] = self.checkbox_option_risk16.get()
        self.entries_4["no_of_cores_16"] = self.entry_no_of_cores16.get()
        self.entries_4["BPH_16"] = self.entry_bph16.get()
        self.entries_4["Prostatitis_16"] = self.entry_Prostatitis16.get()
        self.entries_4["Atrophy_16"] = self.entry_A16.get()
        self.entries_4["BasalCellHqPerPlasiq_16"] = self.entry_BHPPlasiq_16.get()
        self.entries_4["PIN_16"] = self.entry_pin_16.get()
        self.entries_4["ca_grade_16"]= self.entry_grade_16.get()
    def bottle_16(self):
        self.sixteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-16"), height=1000, fg_color="transparent", corner_radius=0)
        self.sixteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.sixteen_frame, text="Bottle 16", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.sixteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles16.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk16 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk16.set("")
        self.checkbox_option_risk16.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores16.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph16.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis16.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A16.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_16.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_16.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk16 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 16))
        self.option_risk16.set("")
        self.option_risk16.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_16 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_16.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_16 = CTkFrame(self.sixteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_16.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_16, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_16 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_16, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_16", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(16, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_16.append(cb)

        button_row = CTkFrame(self.sixteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        button16 = CTkButton(button_row, text="Get Bottle-16", width=150, height=40, command=self.get_data_frame_16, fg_color="#10b981")
        button16.pack(side="left", padx=12)
        button_export = CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth)
        button_export.pack(side="left", padx=12)

    def get_data_frame_17(self):
        self.entries_4["Site_of_biopsy_17"] = self.entry_bottles17.get()
        self.entries_4["US_risk_features_17"] = self.checkbox_option_risk17.get()
        self.entries_4["no_of_cores_17"] = self.entry_no_of_cores17.get()
        self.entries_4["BPH_17"] = self.entry_bph17.get()
        self.entries_4["Prostatitis_17"] = self.entry_Prostatitis17.get()
        self.entries_4["Atrophy_17"] = self.entry_A17.get()
        self.entries_4["BasalCellHqPerPlasiq_17"] = self.entry_BHPPlasiq_17.get()
        self.entries_4["PIN_17"] = self.entry_pin_17.get()
        self.entries_4["ca_grade_17"]= self.entry_grade_17.get()
    def bottle_17(self):
        self.seventeen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-17"), height=1000, fg_color="transparent", corner_radius=0)
        self.seventeen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.seventeen_frame, text="Bottle 17", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.seventeen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles17.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk17 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk17.set("")
        self.checkbox_option_risk17.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores17.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph17.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis17.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A17.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_17.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_17.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk17 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 17))
        self.option_risk17.set("")
        self.option_risk17.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_17 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_17.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_17 = CTkFrame(self.seventeen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_17.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_17, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5",
            "Gleason 5+4", "Gleason 5+5", "Gleason 5+6", "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6",
            "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_17 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_17, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_17", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(17, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_17.append(cb)

        button_row = CTkFrame(self.seventeen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        CTkButton(button_row, text="Get Bottle-17", width=150, height=40, command=self.get_data_frame_17, fg_color="#10b981").pack(side="left", padx=12)
        CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth).pack(side="left", padx=12)


    def get_data_frame_18(self):
        self.entries_4["Site_of_biopsy_18"]=self.entry_bottles18.get()
        self.entries_4["US_risk_features_18"]=self.checkbox_option_risk18.get()
        self.entries_4["no_of_cores_18"]=self.entry_no_of_cores18.get()
        self.entries_4["BPH_18"]=self.entry_bph18.get()
        self.entries_4["Prostatitis_18"]=self.entry_Prostatitis18.get()
        self.entries_4["Atrophy_18"]=self.entry_A18.get()
        self.entries_4["BasalCellHqPerPlasiq_18"]=self.entry_BHPPlasiq_18.get()
        self.entries_4["PIN_18"]=self.entry_pin_18.get()
        self.entries_4["ca_grade_18"]= self.entry_grade_18.get()
    def bottle_18(self):
        self.eighteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-18"), height=1000, fg_color="transparent", corner_radius=0)
        self.eighteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.eighteen_frame, text="Bottle 18", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.eighteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles18.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk18 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk18.set("")
        self.checkbox_option_risk18.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores18.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph18.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis18.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A18.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_18.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_18.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk18 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 18))
        self.option_risk18.set("")
        self.option_risk18.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_18 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_18.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_18 = CTkFrame(self.eighteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_18.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_18, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_18 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_18, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_18", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(18, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_18.append(cb)

        button_row = CTkFrame(self.eighteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        CTkButton(button_row, text="Get Bottle-18", width=150, height=40, command=self.get_data_frame_18, fg_color="#10b981").pack(side="left", padx=12)
        CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth).pack(side="left", padx=12)


    def get_data_frame_19(self):
        self.entries_4["Site_of_biopsy_19"]=self.entry_bottles19.get()
        self.entries_4["US_risk_features_19"]=self.checkbox_option_risk19.get()
        self.entries_4["no_of_cores_19"]=self.entry_no_of_cores19.get()
        self.entries_4["BPH_19"]=self.entry_bph19.get()
        self.entries_4["Prostatitis_19"]=self.entry_Prostatitis19.get()
        self.entries_4["Atrophy_19"]=self.entry_A19.get()
        self.entries_4["BasalCellHqPerPlasiq_19"]=self.entry_BHPPlasiq_19.get()
        self.entries_4["PIN_19"]=self.entry_pin_19.get()
        self.entries_4["ca_grade_19"]= self.entry_grade_19.get()
    def bottle_19(self):
        self.nineteen_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-19"), height=1000, fg_color="transparent", corner_radius=0)
        self.nineteen_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.nineteen_frame, text="Bottle 19", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.nineteen_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles19.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk19 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk19.set("low")
        self.checkbox_option_risk19.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores19.grid(row=2, column=1, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores19.insert(0, "2")

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph19.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis19.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A19.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_19.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_19.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk19 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 19))
        self.option_risk19.set("No")
        self.option_risk19.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_19 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_19.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_19 = CTkFrame(self.nineteen_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_19.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_19, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_19 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_19, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_19", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(19, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_19.append(cb)

        button_row = CTkFrame(self.nineteen_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        CTkButton(button_row, text="Get Bottle-19", width=150, height=40, command=self.get_data_frame_19, fg_color="#10b981").pack(side="left", padx=12)
        CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth).pack(side="left", padx=12)


    def get_data_frame_20(self):
        self.entries_4["Site_of_biopsy_20"] = self.entry_bottles20.get()
        self.entries_4["US_risk_features_20"] = self.checkbox_option_risk20.get()
        self.entries_4["no_of_cores_20"] = self.entry_no_of_cores20.get()
        self.entries_4["BPH_20"] = self.entry_bph20.get()
        self.entries_4["Prostatitis_20"] = self.entry_Prostatitis20.get()
        self.entries_4["Atrophy_20"] = self.entry_A20.get()
        self.entries_4["BasalCellHqPerPlasiq_20"] = self.entry_BHPPlasiq_20.get()
        self.entries_4["PIN_20"] = self.entry_pin_20.get()
        self.entries_4["ca_grade_20"]= self.entry_grade_20.get()
    def bottle_20(self):
        self.twenty_frame = CTkScrollableFrame(self.tab_view_bottles_2.tab("Bottle-20"), height=1000, fg_color="transparent", corner_radius=0)
        self.twenty_frame.pack(fill="both", expand=True)

        section_header = CTkLabel(self.twenty_frame, text="Bottle 20", font=("Arial Black", 18, "bold"), text_color="#1e3a8a", fg_color="#e2e8f0", corner_radius=8, pady=8, padx=16)
        section_header.grid(row=0, column=3, columnspan=4, sticky="ew", pady=(10, 16))

        entry_card = CTkFrame(self.twenty_frame, fg_color="#f8fafc", corner_radius=12, border_color="#e2e8f0", border_width=1)
        entry_card.grid(row=1, column=0, columnspan=4, padx=16, pady=(0, 8), sticky="ew")

        CTkLabel(entry_card, text="Site of biopsy:", text_color="#000").grid(row=0, column=0, padx=12, pady=6, sticky=W)
        self.entry_bottles20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bottles20.grid(row=0, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="US Risk Features:", text_color="#000").grid(row=1, column=0, padx=12, pady=6, sticky=W)
        self.checkbox_option_risk20 = CustomCTkComboBox(entry_card, values=["very low", "low", "intermediate", "high"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff")
        self.checkbox_option_risk20.set("")
        self.checkbox_option_risk20.grid(row=1, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="no. of Cores:", text_color="#000").grid(row=2, column=0, padx=12, pady=6, sticky=W)
        self.entry_no_of_cores20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_no_of_cores20.grid(row=2, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="BPH:", text_color="#000").grid(row=3, column=0, padx=12, pady=6, sticky=W)
        self.entry_bph20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_bph20.grid(row=3, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Prostatitis:", text_color="#000").grid(row=4, column=0, padx=12, pady=6, sticky=W)
        self.entry_Prostatitis20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_Prostatitis20.grid(row=4, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Atrophy:", text_color="#000").grid(row=5, column=0, padx=12, pady=6, sticky=W)
        self.entry_A20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_A20.grid(row=5, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Basal Cell Hq Per Plasiq:", text_color="#000").grid(row=6, column=0, padx=12, pady=6, sticky=W)
        self.entry_BHPPlasiq_20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_BHPPlasiq_20.grid(row=6, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="PIN:", text_color="#000").grid(row=7, column=0, padx=12, pady=6, sticky=W)
        self.entry_pin_20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_pin_20.grid(row=7, column=1, padx=12, pady=6, sticky=W)

        CTkLabel(entry_card, text="Cancer Prostate:", text_color="#000").grid(row=8, column=0, padx=12, pady=6, sticky=W)
        self.option_risk20 = CustomCTkComboBox(entry_card, values=["Yes", "No"], width=220, font=("Helvetica", 16), button_color="#2A8C55", border_color="#2A8C55", border_width=2, button_hover_color="#207244", dropdown_hover_color="#207244", dropdown_fg_color="#2A8C55", dropdown_text_color="#fff", command=lambda value: self.logic.gleason_event(None, 20))
        self.option_risk20.set("")
        self.option_risk20.grid(row=8, column=1, padx=12, pady=6, sticky=W)

        # Row 10: Cancer Grade
        CTkLabel(entry_card, text="Cancer Grade:", text_color="#000").grid(row=9, column=0, padx=12, pady=6, sticky=W)
        self.entry_grade_20 = CTkEntry(entry_card, width=220, border_color="#2A8C55", border_width=2)
        self.entry_grade_20.grid(row=9, column=1, padx=12, pady=6, sticky=W)

        self.gleason_frame_20 = CTkFrame(self.twenty_frame, fg_color="#f1f5f9", border_color="#e2e8f0", border_width=1, corner_radius=10)
        self.gleason_frame_20.grid(row=1, column=5, columnspan=4, padx=16, pady=(0, 12), sticky="ew")
        CTkLabel(self.gleason_frame_20, text="Gleason Patterns", text_color="#1e3a8a", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky=W, pady=(4, 8), padx=8)

        gleason_labels = [
            "Gleason 2", "Gleason 2+3", "Gleason 3+3", "Gleason 3+4", "Gleason 4+3", "Gleason 4+4", "Gleason 4+5", "Gleason 5+4", "Gleason 5+5", "Gleason 5+6",
            "Gleason 6+5", "Gleason 6+6", "Gleason 6+7", "Gleason 7+6", "Gleason 7+7", "Gleason 7+8", "Gleason 8+7", "Gleason 8+8", "Gleason 8+9", "Gleason 9+9"
        ]
        self.gleason_btns_20 = []
        for idx, label in enumerate(gleason_labels, start=1):
            cb = CTkCheckBox(self.gleason_frame_20, text=label, text_color="#000")
            setattr(self, f"check_button_{idx}_20", cb)
            cb.configure(command=lambda idx=idx, cb=cb: self.logic.update_gleason_selection(20, idx, cb.get()))
            cb.grid(row=1 + (idx - 1) // 10, column=(idx - 1) % 10, padx=6, pady=4, sticky=W)
            cb.grid_remove()
            self.gleason_btns_20.append(cb)

        button_row = CTkFrame(self.twenty_frame, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, pady=(8, 16), sticky="ew")
        CTkButton(button_row, text="Get Bottle-20", width=150, height=40, command=self.get_data_frame_20, fg_color="#10b981").pack(side="left", padx=12)
        CTkButton(button_row, text="Export", width=200, height=40, command=self.export_fourth).pack(side="left", padx=12)      
    def save_to_FirstBottles(self, patientsinfo_id):
        from prostate_modular.database import DatabaseManager
        db = DatabaseManager("DB/Informations.db")
        try:
            self.entries_3["Image"] = "temp/2.png"
            with open("temp/2.png", "rb") as img_file:
                self.entries_3["ImagePath"] = img_file.read()
        except Exception as e:
            self.entries_3["ImagePath"] = None
            showerror("Error reading image:", e)
        db.insert_into_FirstBottles(patientsinfo_id, self.entries_3)
        db.update_table()
    def save_third(self):
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
                self.entries_3["Image"] = "temp/2.png"
                with open("temp/2.png", "rb") as img_file:
                    self.entries_3["Image"] = img_file.read()
                patientsinfo_id = self.entries_1.get('US')
                if patientsinfo_id:
                    self.save_to_FirstBottles(patientsinfo_id)
            except Exception as e:
                showerror("Database Error", f"Failed to insert data: {e}")
        except Exception as e:
            showerror("Error", f"Failed to save document: {e}")
    def export_fourth(self):
        from tkinter import Toplevel
        from prostate_modular.image_marking import ImageMarkingApp
        from prostate_modular.database import DatabaseManager
        from docxtpl import DocxTemplate, InlineImage
        from docx.shared import Mm
        import os
        from tkinter.messagebox import showerror, showinfo
        
        try:
            # Ensure temp directory exists
            if not os.path.exists("temp"):
                os.makedirs("temp")
            self.save_third()
            # Create and wait for image marking window
            marked_image_path = "temp/3.png"  # Unique filename for this export
            toplevel = Toplevel(self.master)
            image_marker = ImageMarkingApp(
                toplevel, 
                marked_image_path,  # Where to save marked image
                "DOC/marker2.png",  # Template image
                "temp/4.docx",      # Output DOCX path
                "save", 
                self.entries_4
            )
            toplevel.wait_window()

            # Verify the marked image was created
            if not os.path.exists(marked_image_path):
                raise FileNotFoundError("Marked image was not saved properly")

            # Load appropriate template
            if self.entries_1["Hospital"] == 'life':
                doc = DocxTemplate("DOC/Life/4.docx")
            else:
                doc = DocxTemplate("DOC/Kidney and Tract/4.docx")

            # Clean entries and prepare context
            last_entry = {key: '' if v is None else v for key, v in self.entries_4.items()}
            marked_inline_image = InlineImage(doc, marked_image_path, width=Mm(136), height=Mm(32))
            last_entry["Image"] = marked_inline_image
            context = {"entries": last_entry}
            
            # Render and save document
            doc.render(context)
            doc.save("temp/4.docx")

            # Save all data to database
            patientsinfo_id = self.entries_1.get('US')
            if patientsinfo_id:
                # Read the marked image as binary data
                with open("temp/3.png", "rb") as img_file:
                    self.entries_4["Image"] = img_file.read()
                
                # Save to SecondBottles table
                self.save_to_SecondBottles(patientsinfo_id)
            
            # Combine all documents
            self.combine_all_docx([
                "temp/1.docx", 
                "temp/2.docx", 
                "temp/3.docx", 
                "temp/4.docx"
            ])
            
            self.go_to_main_window()
            showinfo("Success", "Data exported successfully!")
        except Exception as e:
            showerror("Export Error", f"Failed to export document: {str(e)}")
    def save_to_SecondBottles(self, patientsinfo_id):
        from prostate_modular.database import DatabaseManager
        import os  # Add this import
        
        db = DatabaseManager("DB/Informations.db")
        
        try:
            # First get the patientsside_id from PatientsSide table
            with db.connection:
                cursor = db.connection.cursor()
                cursor.execute("SELECT id FROM PatientsSide WHERE patientsinfo_id = ?", (patientsinfo_id,))
                result = cursor.fetchone()
                if result:
                    patientsside_id = result[0]
                else:
                    showerror("Error", "Could not find matching PatientsSide record")
                    return
            
            # Handle image
            image_path = "temp/3.png"
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    self.entries_4["Image"] = img_file.read()
            else:
                self.entries_4["Image"] = None
            # Insert into SecondBottles
            success = db.insert_into_SecondBottles(patientsside_id, self.entries_4)
            
            if success:
                showinfo("Success", "Data saved successfully to SecondBottles")
                db.update_table()
            else:
                showerror("Error", "Failed to save data to SecondBottles")
                
        except Exception as e:
            showerror("Database Error", f"Failed to save data: {str(e)}")
    def combine_all_docx(self, files_list):
        import os
        from tkinter import filedialog
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
                showinfo(f"Patient folder created at: {patient_folder}")
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

    
    
    
    
    
    
    
    