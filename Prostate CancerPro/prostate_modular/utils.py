from customtkinter import CTkComboBox

class CustomCTkComboBox(CTkComboBox):
    def __init__(self, master, values, *args, **kwargs):
        super().__init__(master, values=values, *args, **kwargs)
        self.bind("<Up>", self.navigate_up_dropdown)
        self.bind("<Down>", self.navigate_dropdown)
        self.bind("<<ComboboxSelected>>", self.update_second_dropdown)
    def navigate_dropdown(self, event):
        current_value = self.get()
        current_index = self.cget('values').index(current_value)
        next_index = (current_index + 1) % len(self.cget('values'))
        self.set(self.cget('values')[next_index])
    def navigate_up_dropdown(self, event):
        current_value = self.get()
        current_index = self.cget('values').index(current_value)
        prev_index = (current_index - 1) % len(self.cget('values'))
        self.set(self.cget('values')[prev_index])
    def update_second_dropdown(self, event):
        selected_item = self.get()
        for d in self.dropdowns:
            if d != self:
                d.set(f"{selected_item} Option")

    def get_combobox_values(self,group_frame):
        values=[]
        for combobox in group_frame.winfo_children():
            if isinstance(combobox,CTkComboBox):
                values.append(combobox.get())
        return values

