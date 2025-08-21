from tkinter import simpledialog, colorchooser, NW, LEFT
from PIL import Image, ImageTk, ImageDraw
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docxcompose.composer import Composer
from docx import Document as Document_compose
from customtkinter import CTkCanvas, CTkButton, CTkFrame, CTkLabel
import os
from math import radians, cos, sin, degrees, atan2
from tkinter import EventType
from tkinter.messagebox import askyesno
from tkinter import colorchooser, filedialog

class ImageMarkingApp:
    def __init__(self, master, im_name, image, doc_template_name, type, entries_1=None):
        # --- Color Palette (matching main app) ---
        self.colors = {
            'primary': '#1e3a8a',      # Deep blue
            'secondary': '#3b82f6',   # Bright blue
            'accent': '#10b981',      # Emerald green
            'success': '#059669',     # Dark green
            'warning': '#f59e0b',     # Amber
            'danger': '#dc2626',      # Red
            'light': '#f8fafc',       # Light gray
            'dark': '#1e293b',        # Dark gray
            'white': '#ffffff',       # White
            'border': '#e2e8f0',      # Border color
        }
        self.master = master
        self.master.title("Image Marking App")
        self.master.configure(bg=self.colors['light'])
        # Store entries data
        self.entries_1 = entries_1 or {}
        # Main container frame
        self.container = CTkFrame(master, fg_color=self.colors['light'], corner_radius=15)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        # Header
        self.header = CTkLabel(self.container, text="Image Marking Tool", font=("Arial Black", 22, "bold"), text_color=self.colors['primary'])
        self.header.pack(pady=(0, 10))
        # Canvas frame with border
        self.canvas_frame = CTkFrame(self.container, fg_color=self.colors['white'], border_color=self.colors['border'], border_width=2, corner_radius=10)
        self.canvas_frame.pack(pady=(0, 10))
        # Load and display image
        self.image_path = image
        self.image = Image.open(self.image_path).resize((1200, 350))
        self.photo_img = ImageTk.PhotoImage(self.image)
        self.canvas = CTkCanvas(self.canvas_frame, width=self.image.width, height=self.image.height, bg=self.colors['light'], highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
        self.canvas.focus_set()
        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonPress-3>", self.start_draw)
        self.canvas.bind("<B3-Motion>", self.draw_rotated_oval)
        self.canvas.bind("<ButtonRelease-3>", self.end_draw)
        self.canvas.bind("<Double-Button-1>", self.draw_mark)
        self.canvas.bind("<Key>", self.add_oval)
        # Button bar
        self.button_frame = CTkFrame(self.container, fg_color="transparent")
        self.button_frame.pack(pady=(10, 5))
        self.color_button = CTkButton(self.button_frame, text="Choose Color", command=self.change_color, fg_color=self.colors['accent'], hover_color=self.colors['success'], corner_radius=8, width=130)
        self.color_button.pack(side=LEFT, padx=8, pady=7)
        self.undo_button = CTkButton(self.button_frame, text="Undo", command=self.undo, fg_color=self.colors['warning'], hover_color="#d97706", corner_radius=8, width=90)
        self.undo_button.pack(side=LEFT, padx=8, pady=7)
        self.render_button = CTkButton(self.button_frame, text="Render to Word", command=self.render_to_word, fg_color=self.colors['primary'], hover_color=self.colors['accent'], corner_radius=8, width=160, text_color=self.colors['white'])
        self.render_button.pack(side=LEFT, padx=8, pady=7)
        self.clear_button = CTkButton(self.button_frame, text="Clear", command=self.clear, fg_color=self.colors['danger'], hover_color="#b91c1c", corner_radius=8, width=90)
        self.clear_button.pack(side=LEFT, padx=8, pady=7)
        # Instructions/legend
        self.instructions = CTkLabel(self.container, text="Left click: move | Right click: draw oval | Double click: mark | Choose color, Undo, Render, Clear", font=("Arial", 13), text_color=self.colors['dark'], fg_color=self.colors['light'])
        self.instructions.pack(pady=(0, 10))
        # Status label
        self.status_label = CTkLabel(self.container, text="Ready", font=("Arial", 12), text_color=self.colors['secondary'], fg_color=self.colors['light'])
        self.status_label.pack(pady=(0, 0))
        # --- Rest of __init__ logic (variables, protocol, etc.) ---
        self.marking_type = type
        self.doc_template = doc_template_name
        self.color = self.colors['primary']
        self.drawing = False
        self.image_name = im_name
        self.last_x, self.last_y, self.x, self.y = None, None, None, None
        self.temp = [0, 0, 0, 0, ""]
        self.marked_ovals = []
        self.marked_positions = []
        self.mark_radius = 14
        self.current_x, self.current_y = None, None
        self.selected_item = None
        self.button_clicked = False
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def start_draw(self, event):
        """Start drawing the rotated oval."""
        self.start_x = event.x
        self.start_y = event.y
        self.angle = 0
        self.current_oval = None

    def draw_rotated_oval(self, event):
        """Draw a rotated oval as the user drags the mouse."""
        if self.start_x is None or self.start_y is None:
            return

        x = event.x
        y = event.y

        width = abs(x - self.start_x)
        height = abs(y - self.start_y)
        center_x = (self.start_x + x) // 2
        center_y = (self.start_y + y) // 2

        delta_x = x - self.start_x
        delta_y = y - self.start_y

        if delta_x == 0:
            self.angle = 0 if delta_y >= 0 else 180
        else:
            self.angle = degrees(atan2(delta_y, delta_x))

        if self.current_oval:
            self.canvas.delete(self.current_oval)

        points = self.calculate_rotated_oval_points(center_x, center_y, width, height, self.angle)
        self.current_oval = self.canvas.create_polygon(points, smooth=True, outline=self.colors["warning"], fill="")

    def end_draw(self, event):
        """Finalize the drawn rotated oval."""
        if self.current_oval:
            self.marked_ovals.append((self.start_x, self.start_y, event.x, event.y, self.angle, self.color))
            self.current_oval = None
    def calculate_rotated_oval_points(self, center_x, center_y, width, height, angle):
        """Calculate the points for a rotated oval."""
        points = []
        for i in range(0, 360, 5):
            rad = radians(i)
            x = center_x + (width / 2) * cos(rad)
            y = center_y + (height / 2) * sin(rad)

            rotated_x = center_x + (x - center_x) * cos(radians(angle)) - (y - center_y) * sin(radians(angle))
            rotated_y = center_y + (x - center_x) * sin(radians(angle)) + (y - center_y) * cos(radians(angle))

            points.extend([rotated_x, rotated_y])
        return points
    def redraw_all_ovals(self):
        """Redraw all marked ovals on the canvas."""
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)
        for oval in self.marked_ovals:
            start_x, start_y, end_x, end_y, angle, color = oval
            points = self.calculate_rotated_oval_points((start_x + end_x) // 2, (start_y + end_y) // 2, abs(end_x - start_x), abs(end_y - start_y), angle)
            self.canvas.create_polygon(points, smooth=True, outline='yellow', fill="")
    def img(self):
        # Create a new blank image with RGBA mode
        marked_image = Image.new("RGBA", (self.canvas.winfo_width(), self.canvas.winfo_height()), (255, 255, 255, 0))
        draw = ImageDraw.Draw(marked_image)
    
        # Open the original image
        image = Image.open(self.image_path)
    
        # Resize the original image to match the canvas size
        resized_image = image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
    
        # Paste the resized original image onto the marked image
        marked_image.paste(resized_image, (0, 0))
    
        # Draw rotated ovals for marked ovals
        if self.marked_ovals:
            for oval in self.marked_ovals:
                start_x, start_y, end_x, end_y, angle, color = oval
                points = self.calculate_rotated_oval_points(
                    (start_x + end_x) // 2, 
                    (start_y + end_y) // 2, 
                    abs(end_x - start_x), 
                    abs(end_y - start_y), 
                    angle
                )
                draw.polygon(points, outline="yellow", fill=None)
    
        # Draw ellipses for marked positions (if applicable)
        if hasattr(self, "marked_positions") and self.marked_positions:
            for x0, y0, x1, y1, fill, i, _ in self.marked_positions:
                draw.ellipse([x0, y0, x1, y1], fill=fill)
    
        # Update the image on the canvas
        self.photo = ImageTk.PhotoImage(marked_image)
        self.canvas.delete("image")
        self.canvas.create_image(0, 0, anchor=NW, image=self.photo, tags="image")
    
        # Save the marked image to a file
        marked_image.save(self.image_name)
    
        # Optionally, update the canvas or perform additional actions
        if hasattr(self, "update_canvas"):
            self.update_canvas()
    def on_button_click(self):
        self.button_clicked = True
    def on_window_close(self):
        if not self.button_clicked:
            ask = askyesno(
                "Warning",
                "You have not rendered the image to Word. Are you sure you want to close without saving your marks?"
            )
            if ask:
                self.master.destroy()
            else:
                self.master.focus_force()
        else:
            self.master.destroy()
    def clear(self):
        # Delete the existing canvas
        self.canvas.destroy()
        self.marked_ovals = []
        self.marked_positions = []
        # Create a new canvas with the new image
        self.canvas = CTkCanvas(self.canvas_frame, width=1200, height=350, bg=self.colors['light'], highlightthickness=0)
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.create_image(0, 0, anchor=NW, image=self.photo_img, tags="image")    
        # Bind the necessary events to the new canvas
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Button-3>", self.draw_ellipse)
        self.canvas.bind("<B3-Motion>", self.draw_ellipse)
        self.canvas.bind("<Double-Button-1>", self.draw_mark)
        self.canvas.bind("<Key>", self.add_oval)
    def on_press(self, event):
        self.current_x, self.current_y = event.x, event.y
        items = self.canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1)
        if items:
            self.selected_item = items[-1]  # Select the topmost item
        else:
            self.selected_item = None
    def on_drag(self, event):
        dx = event.x - self.current_x
        dy = event.y - self.current_y    
        # Move the selected item (circle) on the canvas
        self.canvas.move(self.selected_item, dx, dy)    
        # Update the current mouse position
        self.current_x = event.x
        self.current_y = event.y    
        # Update marked positions
        if self.marked_positions:
            for mark in self.marked_positions:
                # Check if the selected item is the current circle in the list
                if mark[-1] == self.selected_item:
                    # Update coordinates for the selected circle
                    x1, y1, x2, y2, _, _, _ = mark
                    x1 += dx
                    y1 += dy
                    x2 += dx
                    y2 += dy
                    mark[0] = x1
                    mark[1] = y1
                    mark[2] = x2
                    mark[3] = y2
                    # Update the canvas with the new coordinates
                    self.canvas.coords(self.selected_item, x1, y1, x2, y2)
                    break  # Exit the loop after updating the selected circle
    def add_oval(self, event):
        see = self.temp
        self.marked_ovals.append(see)
        self.temp = []
    def draw_ellipse(self, event):
        x, y = event.x, event.y
        self.canvas.delete('oval')
        if event.type == EventType.ButtonPress:
            self.drawing = True
            self.last_x, self.last_y = x, y
        elif event.type == EventType.Motion and self.drawing:
            self.canvas.create_oval(self.last_x, self.last_y, x, y, outline=self.color, tags="oval", width=5)
            self.temp[:] = [self.last_x, self.last_y, x, y]
        elif event.type == EventType.ButtonRelease:
            self.drawing = False
            self.canvas.create_oval(self.temp[0], self.temp[1], self.temp[2], self.temp[3], outline=self.temp[4])
    def draw_mark(self, event):
        num = simpledialog.askinteger("Question", "How Many Circles")       
        self.draw_mark_circle(event,num)     
        self.update_canvas()
    def draw_mark_circle(self, event, num):
        t = 0
        if self.marked_positions:
            # Find the maximum index in the marked positions
            t = max(mark[5] for mark in self.marked_positions) + 1
        x, y = event.x, event.y
        color = colorchooser.askcolor(title="Choose Color")[1]
        self.master.focus_force()
        for i in range(num):
            x1 = x - self.mark_radius
            y1 = y - self.mark_radius
            x2 = x + self.mark_radius
            y2 = y + self.mark_radius
            # Create the circle on the canvas and store its ID
            mark_id = self.canvas.create_oval(x1, y1, x2, y2, width=1, fill=color, tags=("mark", "position"))
            # Store the circle's coordinates and canvas ID in marked_positions
            self.marked_positions.append([x1, y1, x2, y2, color, t + i, mark_id])
    def update_canvas(self):
        if self.marked_ovals:
            for oval in self.marked_ovals:
                self.canvas.coords(oval, *self.get_scaled_coords(oval))
                self.canvas.itemconfig(oval, outline="white", width=5, tags=("mark", "ellipse"))
        if self.marked_positions:
            for mark in self.marked_positions:
                self.canvas.coords(mark, *self.get_scaled_coords(mark))
                self.canvas.itemconfig(mark, fill=self.canvas.itemcget(mark, "fill"), tags=("mark", "position"))
        self.master.focus_force()
    def get(self):
        remove_list = []
        for file in os.listdir("temp"):
            if ".docx" in file:
                remove_list.append(file)
        return remove_list
    def combine_all_docx(self,files_list):
        number_of_sections=len(files_list)
        mast = Document_compose(files_list[0])
        composer = Composer(mast)
        for i in range(1, number_of_sections):
            doc_temp = Document_compose(files_list[i])
            composer.append(doc_temp)
        file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files", "*.docx")])
        self.master.focus_force()
        if file_path:
            composer.save(file_path)
    def render_to_word(self):
        self.button_clicked = True
        if self.marking_type == "save":
            self.img()
            save_path = self.image_name
            try:
                render_to_word = DocxTemplate(self.doc_template)
                marked_inline_image = InlineImage(render_to_word, save_path, width=Mm(136), height=Mm(32))
                
                # Determine which entries to use (check in order of priority)
                entries = {}
                if hasattr(self, 'entries_1'):
                    entries = self.entries_1
                elif hasattr(self, 'entries_3'):
                    entries = self.entries_3
                elif hasattr(self, 'entries_4'):
                    entries = self.entries_4
                
                # Create context with both Image and entries data
                context = {
                    "Image": marked_inline_image,
                    "entries": entries
                }
                
                # render_to_word.render(context)
                # render_to_word.save(self.doc_template)
                self.status_label.configure(text="Image rendered to Word successfully!")
                
            except FileNotFoundError:
                from tkinter.messagebox import showerror
                showerror("Error", f"Word template file '{self.doc_template}' not found. Please ensure the template exists.")
                self.status_label.configure(text="Error: Template file not found")
            except Exception as e:
                from tkinter.messagebox import showerror
                showerror("Error", f"Error rendering to Word: {str(e)}")
                self.status_label.configure(text="Error rendering to Word")
        elif self.marking_type == "export":
            self.img()
            save_path = self.image_name
            try:
                render_to_word = DocxTemplate(self.doc_template)
                marked_inline_image = InlineImage(render_to_word, save_path, width=Mm(136), height=Mm(32))
                # Create context with both Image and entries data
                context = {
                    "Image": marked_inline_image,
                    "entries": self.entries_1 if hasattr(self, 'entries_1') else {}
                }
                render_to_word.render(context)
                render_to_word.save(self.doc_template)
                files = self.get()
                #Calling the function
                self.combine_all_docx(files)
                self.status_label.configure(text="Image exported successfully!")
            except FileNotFoundError:
                from tkinter.messagebox import showerror
                showerror("Error", f"Word template file '{self.doc_template}' not found. Please ensure the template exists.")
                self.status_label.configure(text="Error: Template file not found")
            except Exception as e:
                from tkinter.messagebox import showerror
                showerror("Error", f"Error exporting: {str(e)}")
                self.status_label.configure(text="Error exporting")
    def undo(self):
        if self.marked_positions:
            self.marked_positions.pop()
        if self.marked_ovals:
            self.marked_ovals.pop()
        self.update_canvas()
    def change_color(self):
        new_color = colorchooser.askcolor(color=self.color)[1]
        if new_color:
            self.color = new_color
        if self.selected_item:
            if self.marked_positions:
                for mark in self.marked_positions:
                    # Check if the selected item is the current circle in the list
                    if mark[-1] == self.selected_item:
                        # Update coordinates for the selected circle
                        x1, y1, x2, y2, c, _, _ = mark
                        mark[4] = c
    def resize_image(self, image_path, new_width, new_height):
        image = Image.open(image_path)
        resized_image = image.resize((new_width, new_height))
        resized_photo = ImageTk.PhotoImage(resized_image)
        return resized_photo
    def get_scaled_coords(self, item):
        coords = self.canvas.coords(item)
        if coords:
            if len(coords) == 4:
                x0, y0, x1, y1 = coords
                x0_pixel = self.canvas.canvasx(x0)
                y0_pixel = self.canvas.canvasy(y0)
                x1_pixel = self.canvas.canvasx(x1)
                y1_pixel = self.canvas.canvasy(y1)
                return x0_pixel, y0_pixel, x1_pixel, y1_pixel
        return None, None, None, None
    def get_scaled_coords_circle(self, item):
        coords = self.canvas.coords(item)
        if coords:
            if len(coords) == 3:
                x_center, y_center, radius = coords
                x_center_pixel = self.canvas.canvasx(x_center)
                y_center_pixel = self.canvas.canvasy(y_center)
                scaled_radius = self.canvas.canvasx(x_center + radius) - x_center_pixel
                return x_center_pixel, y_center_pixel, scaled_radius
        return None, None, None  