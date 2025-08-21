from customtkinter import set_appearance_mode, CTk, BooleanVar, CTkLabel
from customtkinter import CTkImage, CTkCanvas, CTkButton
from tkinter import StringVar
import threading
from prostate_modular.database import DatabaseManager
from PIL import Image, ImageTk
from prostate_modular.constant import entries_1
from prostate_modular.pops import hospital_popup
from prostate_modular.main_window import MainWindow
from prostate_modular.backend import Backend
class Welecome(CTk):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()  # <-- Move this here!
        self.db = DatabaseManager("DB/Informations.db")
        self.db.create_database_user_tables()
        self.create_widgets()  # Make sure this is called!
        self.main_window = MainWindow(self)
        self.backend = Backend()
        self.backend.ensure_patients_folder()
    def on_space_key(self,event, combobox_var):
        if event.widget == combobox_var and event.char == ' ':
            combobox_var.event_generate("<<ComboboxSelected>>")
    def initialize(self):
        self.resizable(True, True)
        self.title("Prostate Cancer Detection System")
        self.geometry("720x390+500+100")
        set_appearance_mode("dark")
        self.config(bg="#000")
        # Initialize image editing variables
        self.image_path1 = r"DOC\Life\marker1.png"  # Specify the image path here
        self.image_path3 = r"DOC\Life\marker3.png"  # Specify the image path here
        self.image_path4 = r"DOC\Life\marker4.png"  # Specify the image path here
        self.doc = r"DOC/Life/1.docx"
        self.undo_stack = []
        self.comboboxes_one=[]
        self.current_color = "#ff0000"
        self.point_radius = 5
        self.is_drawing = False
        self.doc_saved = False
        self.hospital = None  
        self.create_widgets()   
        self.main=False
        self.radio_value = StringVar()
        self.li=False
        self.ngh=False
        self.al_salam=False
        self.ihun=False
        self.function_called=False
        self.switch_value = BooleanVar(value=True)
        self.glaosan = None
        self.type = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Bind the close event to on_close method
        self.db.create_database_user_tables()

    def create_widgets(self):
        self.geometry("630x310+400+100")  # Adjusted window size
        self.canvas = CTkCanvas(self, bg="#00008B", height=600, width=900, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(440,0,400+400,0+400,fill="#FCFCFC",outline="tomato")
        logo_image = Image.open("Logo/main/Best11.png")
        self.logo_img = CTkImage(dark_image=logo_image, light_image=logo_image,size=(190,150))
        self.logo_label = CTkLabel(self, text="",image=self.logo_img,text_color="#fff", bg_color="#00008b", justify="left", font=("Arial-BoldMT", 24,"bold"))
        self.logo_label.place(x=70.0,y=10.0) 
        self.title_label = CTkLabel(self, text="   Welcome to DR.Ahmed Tawfik\n\t   Application",text_color="#fff", bg_color="#00008b", justify="left", font=("Arial-BoldMT", 20,"bold"))
        self.title_label.place(x=5.0,y=155.0)   
        self.info_text = CTkLabel(self, text="\nProfessional Doctor for any Kind of need\n""in PROSTATE CANCER DETECTION\n""DIAGNOSIS And DUCT SYSTEM \n\tEVALUATION",text_color="#fff", bg_color="#00008B",justify="left", font=("Georgia", 14,"bold"))
        self.info_text.place(x=20.0, y=220.0)    
        # Load and resize images
        life_image = Image.open("Logo/main/Life.png")
        self.life_img = CTkImage(dark_image=life_image, light_image=life_image,size=(70,80))   
        logo_image = Image.open("Logo/ico/doctor-applogo.png")
        self.track_img = CTkImage(dark_image=logo_image, light_image=logo_image,size=(100,112))       
        # Create buttons
        self.life_btn = CTkButton(self, text="Life",text_color="#d5ceb9", image=self.life_img, command=self.life,cursor='hand2',compound='top',bg_color="#00008B", fg_color="#00008b", font=("Arial-BoldMT", 20,"bold"), width=100, height=100)
        self.life_btn.place(x=370.0, y=137+25)      
        self.track_btn = CTkButton(self, text="", image=self.track_img, command=self.Hospitals,cursor='hand2',bg_color="#00008B", fg_color="#00008b", compound='top',width=100, height=100)
        self.track_btn.place(x=490.0, y=137+25)        
        self.canvas.create_text(620, 88.0, text="Hospitals", fill="#00008B", font=("Arial-BoldMT", 23,"bold"))  
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.resizable(True, True)
        self.search_text_var=StringVar()  # Variable to hold the placeholder text

    def life(self):
        logo = ImageTk.PhotoImage(file="Logo/main/Life.png")
        self.call('wm', 'iconphoto', self._w, logo)  
        self.check=False
        self.li=True
        self.hospital = 'life'
        self.coefficient=None
        self.track_btn.place_forget()
        self.canvas.place_forget()
        self.title_label.place_forget()
        self.info_text.place_forget()
        self.life_btn.place_forget()
        self.track_btn.place_forget()
        entries_1["Hospital"]="life"
        self.main = True
        # Adding light and dark mode images and resizing them
        self.title("Life Hospital for Prostate Cancer Detection System")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.90)
        self.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_close_window())
        self.main_window.side_bar()
        self.main_window.display_search_patients()
        self.deiconify()
    def Hospitals(self):
        logo = ImageTk.PhotoImage(file="Logo/ico/doctor-applogo.png")
        self.call('wm', 'iconphoto', self._w, logo) 
        self.li=False
        self.state("withdrawn")
        self.check=False
        self.track_btn.place_forget()
        self.canvas.place_forget()
        self.title_label.place_forget()
        self.info_text.place_forget()
        self.life_btn.place_forget()
        self.track_btn.place_forget()
        self.main = True
        # Adding light and dark mode images and resizing them
        self.title(f"Hospital for Prostate Cancer Detection System")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.99)
        window_height = int(screen_height * 0.99)
        self.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_close_window())
        self.main = True
        self.main_window.side_bar()
        self.main_window.display_search_patients()
        self.deiconify()
        entries_1["Hospital"]= hospital_popup(self,entries_1.get("Hospital"), lambda selected: entries_1.update({"Hospital": selected}))
    def reset(self):
        self.initialize()
    def on_close_window(self):
        self.stop_event.set()  # Set the event to signal background threads to stop
        self.reset()
    def on_close(self):
        self.stop_event.set()  # Set the event to signal background threads to stop
        self.destroy()
    def on_close_edit(self):
        self.stop_event.set()  # Set the event to signal background threads to stop
        self.edit_image.destroy()