from tkinter import simpledialog, W

class ThirdLogic:
    """
    Refactored logic for handling biopsy bottle data (1-10) in ThirdDataEntryGUI.
    This class provides generic methods for handling Gleason checkboxes, data assignment,
    and event binding for all bottles, reducing code repetition and improving maintainability.
    """
    def __init__(self, gui):
        self.gui = gui  # Instance of ThirdDataEntryGUI
        self.bottle_count = 10
        # Each bottle will have its own check_box list for tracking checked Gleason options
        self.check_boxes = {i: [] for i in range(1, self.bottle_count + 1)}

    def handle_gleason_checkboxes(self, bottle_num):
        """
        Handle Gleason checkboxes for a given bottle number.
        If a checkbox is checked and not already in the list, prompt for a value and update entries_3.
        """
        for gleason_idx in range(1, 21):
            cb_name = f"check_button_{gleason_idx}_{bottle_num}"
            cb = getattr(self.gui, cb_name, None)
            if cb and cb.get():
                text = cb.cget('text')
                if text not in self.check_boxes[bottle_num]:
                    value = simpledialog.askstring(f"{text}", f"Enter {text}:")
                    self.check_boxes[bottle_num].append(text)
                    self.gui.entries_3[f"ca_prostate_{bottle_num}"] = int(value)

    def gleason_event(self, event, bottle_num):
        """
        Event handler for Cancer Prostate dropdown for a given bottle.
        Shows/hides Gleason checkboxes based on selection.
        """
        option_name = f"option_risk{bottle_num}"
        cb_prefix = f"check_button_"
        value = getattr(self.gui, option_name).get()
        self.gui.entries_3[f"ca_prostate_{bottle_num}"] = value
        for gleason_idx in range(1, 21):
            cb_name = f"{cb_prefix}{gleason_idx}_{bottle_num}"
            cb = getattr(self.gui, cb_name, None)
            if cb:
                if value == "Yes":
                    cb.grid(row=(gleason_idx-1)//3 + 11, column=(gleason_idx-1)%3, padx=20, pady=2, sticky=W)
                else:
                    cb.grid_remove()

    def collect_bottle_data(self, bottle_num):
        """
        Collects all entry and combobox data for a given bottle and updates entries_3.
        """
        fields = [
            (f"entry_bottle{bottle_num}", f"Site_of_biopsy_{bottle_num}"),
            (f"checkbox_option_risk{bottle_num}", f"US_risk_features_{bottle_num}"),
            (f"entry_no_of_cores{bottle_num}", f"no_of_cores_{bottle_num}"),
            (f"entry_bph{bottle_num}", f"BPH_{bottle_num}"),
            (f"entry_Prostatitis{bottle_num}", f"Prostatitis_{bottle_num}"),
            (f"entry_A{bottle_num}", f"Atrophy_{bottle_num}"),
            (f"entry_BHPPlasiq_{bottle_num}", f"BasalCellHqPerPlasiq_{bottle_num}"),
            (f"entry_pin_{bottle_num}", f"PIN_{bottle_num}")
        ]
        for widget_name, entry_key in fields:
            widget = getattr(self.gui, widget_name, None)
            if widget:
                self.gui.entries_3[entry_key] = widget.get()
        # Cancer Prostate and Grade
        option_risk = getattr(self.gui, f"option_risk{bottle_num}", None)
        if option_risk:
            self.gui.entries_3[f"Cancer_Prostate_{bottle_num}"] = option_risk.get()
        entry_grade = getattr(self.gui, f"entry_grade_{bottle_num}", None)
        if entry_grade:
            self.gui.entries_3[f"Cancer_Grade_{bottle_num}"] = entry_grade.get()

    def bind_events(self):
        """
        Binds gleason_event and handle_gleason_checkboxes to the appropriate widgets for all bottles.
        Should be called after GUI widgets are created.
        """
        for bottle_num in range(1, self.bottle_count + 1):
            option_risk = getattr(self.gui, f"option_risk{bottle_num}", None)
            if option_risk:
                option_risk.bind("<<ComboboxSelected>>", lambda e, n=bottle_num: self.gleason_event(e, n))
            # Optionally, bind a button to call handle_gleason_checkboxes
            # Example: get_data_btn = getattr(self.gui, f"button_get_data_{bottle_num}", None)
            # if get_data_btn:
            #     get_data_btn.configure(command=lambda n=bottle_num: self.handle_gleason_checkboxes(n))

    # Optionally, add a method to reset all checkboxes and entries for a bottle
    def reset_bottle(self, bottle_num):
        """
        Resets all checkboxes and entries for a given bottle.
        """
        self.check_boxes[bottle_num] = []
        for gleason_idx in range(1, 21):
            cb = getattr(self.gui, f"check_button_{gleason_idx}_{bottle_num}", None)
            if cb:
                cb.deselect()
        # Optionally reset entries in entries_3
        for key in list(self.gui.entries_3.keys()):
            if key.endswith(f"_{bottle_num}"):
                self.gui.entries_3[key] = None

    def update_gleason_selection(self, bottle_num, idx, checked):
        """
        When a Gleason checkbox is checked, prompt the user to enter a number and save it to the corresponding old key (e.g., 'Gleason_1_2', 'Gleason_1_2_3', etc.) in entries_3.
        When unchecked, set the old key to None.
        Print the current state after each change.
        """
        # Get the checkbox label to determine the old key
        cb = getattr(self.gui, f"check_button_{idx}_{bottle_num}", None)
        old_key = None
        if cb:
            label = cb.cget('text').replace(' ', '').replace('+', '_')  # e.g., 'Gleason2', 'Gleason2_3'
            old_key = f"Gleason_{bottle_num}_" + label.replace('Gleason', '')
        if checked:
            value = simpledialog.askstring("Gleason Value", f"Enter value for Gleason {idx} (Bottle {bottle_num}):")
            if value is not None and value.strip() != "":
                if old_key:
                    self.gui.entries_3[old_key] = value
        else:
            if old_key:
                self.gui.entries_3[old_key] = None



    # Example for bottle_1 (repeat for other bottles):
    # In bottle_1, after creating each checkbox:
    # cb.configure(command=lambda idx=idx, cb=cb: self.update_gleason_selection(1, idx, cb.get()))