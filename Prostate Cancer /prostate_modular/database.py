from datetime import datetime
from tkinter.messagebox import showinfo, showerror
import sqlite3

class DatabaseManager:
    def __init__(self, db_path="DB/Informations.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)

    def create_database_user_tables(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS PatientsInfo(
                ID INTEGER PRIMARY KEY,US TEXT,Hospital TEXT,Date TEXT,Name TEXT,Age INTEGER,Nationality TEXT,DR TEXT,Mri_Result TEXT,
                FPSA REAL,TPSA REAL,PSA REAL,Degree TEXT,Machine TEXT,DRE TEXT,Family TEXT,WG_TD_mm REAL,
                WG_Height_mm REAL,WG_Length_mm REAL,WG_Volume_cc REAL,A_TD_mm REAL,A_Height_mm REAL,A_Length_mm REAL,A_Volume_cc REAL,
                Urinary_Bladder TEXT,Bladder_Neck TEXT,Seminal_Vesicles TEXT,Vasa_Deferentia TEXT,Ejaculatory_Ducts TEXT,Lesions TEXT,Image BLOB,ImagePath TEXT
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS PatientsSide(
                id INTEGER PRIMARY KEY,patientsinfo_id INTEGER,
                AApexR TEXT,AApexL TEXT,AMidProstateR TEXT,AMidProstateL TEXT,ABaseR TEXT,ABaseL TEXT,MApexR TEXT,MApexL TEXT,
                MMidprostateR TEXT,MMidprostateL TEXT,MBaseR TEXT,MBaseL TEXT,PApexR TEXT,PApexL TEXT,PMidprostateR TEXT,
                PMidprostateL TEXT,PBaseR TEXT,PBaseL TEXT,TMidprostateR TEXT,TMidprostateL TEXT,TBaseR TEXT,TBaseL TEXT,
                FOREIGN KEY (patientsinfo_id) REFERENCES PatientsInfo(id) ON DELETE CASCADE ON UPDATE CASCADE)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS FirstBottles(
                id INTEGER PRIMARY KEY,patientsinfo_id INTEGER,Lesions TEXT,Degree TEXT,DRE TEXT,Image BLOB,ImagePath TEXT,
                Site_of_biopsy_1 TEXT,US_risk_features_1 TEXT,no_of_cores_1 INTEGER,BPH_1 TEXT,Prostatitis_1 TEXT,Atrophy_1 TEXT,
                BasalCellHqPerPlasiq_1 TEXT,PIN_1 TEXT,ca_prostate_1 TEXT,ca_grade_1 REAL,
                Gleason_1_2 REAL,Gleason_1_2_3 REAL,Gleason_1_3_3 REAL,Gleason_1_3_4 REAL,Gleason_1_4_3 REAL,Gleason_1_4_4 REAL,
                Gleason_1_4_5 REAL,Gleason_1_5_4 REAL,Gleason_1_5_5 REAL,Gleason_1_5_6 REAL,Gleason_1_6_5 REAL,Gleason_1_6_6 REAL,
                Gleason_1_6_7 REAL,Gleason_1_7_6 REAL,Gleason_1_7_7 REAL,Gleason_1_7_8 REAL,Gleason_1_8_7 REAL,Gleason_1_8_8 REAL,
                Gleason_1_8_9 REAL,Gleason_1_9_9 REAL,
                Site_of_biopsy_2 TEXT,US_risk_features_2 TEXT,no_of_cores_2 INTEGER,BPH_2 TEXT,Prostatitis_2 TEXT,Atrophy_2 TEXT,
                BasalCellHqPerPlasiq_2 TEXT,PIN_2 TEXT,ca_prostate_2 TEXT,ca_grade_2 REAL,
                Gleason_2_2 REAL,Gleason_2_2_3 REAL,Gleason_2_3_3 REAL,Gleason_2_3_4 REAL,Gleason_2_4_3 REAL,Gleason_2_4_4 REAL,
                Gleason_2_4_5 REAL,Gleason_2_5_4 REAL,Gleason_2_5_5 REAL,Gleason_2_5_6 REAL,Gleason_2_6_5 REAL,Gleason_2_6_6 REAL,
                Gleason_2_6_7 REAL,Gleason_2_7_6 REAL,Gleason_2_7_7 REAL,Gleason_2_7_8 REAL,Gleason_2_8_7 REAL,Gleason_2_8_8 REAL,
                Gleason_2_8_9 REAL,Gleason_2_9_9 REAL,
                Site_of_biopsy_3 TEXT,US_risk_features_3 TEXT,no_of_cores_3 INTEGER,BPH_3 TEXT,Prostatitis_3 TEXT,Atrophy_3 TEXT,
                BasalCellHqPerPlasiq_3 TEXT,PIN_3 TEXT,ca_prostate_3 TEXT,ca_grade_3 REAL,
                Gleason_3_2 REAL,Gleason_3_2_3 REAL,Gleason_3_3_3 REAL,Gleason_3_3_4 REAL,Gleason_3_4_3 REAL,Gleason_3_4_4 REAL,
                Gleason_3_4_5 REAL,Gleason_3_5_4 REAL,Gleason_3_5_5 REAL,Gleason_3_5_6 REAL,Gleason_3_6_5 REAL,Gleason_3_6_6 REAL,
                Gleason_3_6_7 REAL,Gleason_3_7_6 REAL,Gleason_3_7_7 REAL,Gleason_3_7_8 REAL,Gleason_3_8_7 REAL,Gleason_3_8_8 REAL,
                Gleason_3_8_9 REAL,Gleason_3_9_9 REAL,
                Site_of_biopsy_4 TEXT,US_risk_features_4 TEXT,no_of_cores_4 INTEGER,BPH_4 TEXT,Prostatitis_4 TEXT,Atrophy_4 TEXT,
                BasalCellHqPerPlasiq_4 TEXT,PIN_4 TEXT,ca_prostate_4 TEXT,ca_grade_4 REAL,
                Gleason_4_2 REAL,Gleason_4_2_3 REAL,Gleason_4_3_3 REAL,Gleason_4_3_4 REAL,Gleason_4_4_3 REAL,Gleason_4_4_4 REAL,
                Gleason_4_4_5 REAL,Gleason_4_5_4 REAL,Gleason_4_5_5 REAL,Gleason_4_5_6 REAL,Gleason_4_6_5 REAL,Gleason_4_6_6 REAL,
                Gleason_4_6_7 REAL,Gleason_4_7_6 REAL,Gleason_4_7_7 REAL,Gleason_4_7_8 REAL,Gleason_4_8_7 REAL,Gleason_4_8_8 REAL,
                Gleason_4_8_9 REAL,Gleason_4_9_9 REAL,
                Site_of_biopsy_5 TEXT,US_risk_features_5 TEXT,no_of_cores_5 INTEGER,BPH_5 TEXT,Prostatitis_5 TEXT,Atrophy_5 TEXT,
                BasalCellHqPerPlasiq_5 TEXT,PIN_5 TEXT,ca_prostate_5 TEXT,ca_grade_5 REAL,
                Gleason_5_2 REAL,Gleason_5_2_3 REAL,Gleason_5_3_3 REAL,Gleason_5_3_4 REAL,Gleason_5_4_3 REAL,Gleason_5_4_4 REAL,
                Gleason_5_4_5 REAL,Gleason_5_5_4 REAL,Gleason_5_5_5 REAL,Gleason_5_5_6 REAL,Gleason_5_6_5 REAL,Gleason_5_6_6 REAL,
                Gleason_5_6_7 REAL,Gleason_5_7_6 REAL,Gleason_5_7_7 REAL,Gleason_5_7_8 REAL,Gleason_5_8_7 REAL,Gleason_5_8_8 REAL,
                Gleason_5_8_9 REAL,Gleason_5_9_9 REAL,
                Site_of_biopsy_6 TEXT,US_risk_features_6 TEXT,no_of_cores_6 INTEGER,BPH_6 TEXT,Prostatitis_6 TEXT,Atrophy_6 TEXT,
                BasalCellHqPerPlasiq_6 TEXT,PIN_6 TEXT,ca_prostate_6 TEXT,ca_grade_6 REAL,
                Gleason_6_2 REAL,Gleason_6_2_3 REAL,Gleason_6_3_3 REAL,Gleason_6_3_4 REAL,Gleason_6_4_3 REAL,Gleason_6_4_4 REAL,
                Gleason_6_4_5 REAL,Gleason_6_5_4 REAL,Gleason_6_5_5 REAL,Gleason_6_5_6 REAL,Gleason_6_6_5 REAL,Gleason_6_6_6 REAL,
                Gleason_6_6_7 REAL,Gleason_6_7_6 REAL,Gleason_6_7_7 REAL,Gleason_6_7_8 REAL,Gleason_6_8_7 REAL,Gleason_6_8_8 REAL,
                Gleason_6_8_9 REAL,Gleason_6_9_9 REAL,
                Site_of_biopsy_7 TEXT,US_risk_features_7 TEXT,no_of_cores_7 INTEGER,BPH_7 TEXT,Prostatitis_7 TEXT,Atrophy_7 TEXT,
                BasalCellHqPerPlasiq_7 TEXT,PIN_7 TEXT,ca_prostate_7 TEXT,ca_grade_7 REAL,
                Gleason_7_2 REAL,Gleason_7_2_3 REAL,Gleason_7_3_3 REAL,Gleason_7_3_4 REAL,Gleason_7_4_3 REAL,Gleason_7_4_4 REAL,
                Gleason_7_4_5 REAL,Gleason_7_5_4 REAL,Gleason_7_5_5 REAL,Gleason_7_5_6 REAL,Gleason_7_6_5 REAL,Gleason_7_6_6 REAL,
                Gleason_7_6_7 REAL,Gleason_7_7_6 REAL,Gleason_7_7_7 REAL,Gleason_7_7_8 REAL,Gleason_7_8_7 REAL,Gleason_7_8_8 REAL,
                Gleason_7_8_9 REAL,Gleason_7_9_9 REAL,
                Site_of_biopsy_8 TEXT,US_risk_features_8 TEXT,no_of_cores_8 INTEGER,BPH_8 TEXT,Prostatitis_8 TEXT,Atrophy_8 TEXT,
                BasalCellHqPerPlasiq_8 TEXT,PIN_8 TEXT,ca_prostate_8 TEXT,ca_grade_8 REAL,
                Gleason_8_2 REAL,Gleason_8_2_3 REAL,Gleason_8_3_3 REAL,Gleason_8_3_4 REAL,Gleason_8_4_3 REAL,Gleason_8_4_4 REAL,
                Gleason_8_4_5 REAL,Gleason_8_5_4 REAL,Gleason_8_5_5 REAL,Gleason_8_5_6 REAL,Gleason_8_6_5 REAL,Gleason_8_6_6 REAL,
                Gleason_8_6_7 REAL,Gleason_8_7_6 REAL,Gleason_8_7_7 REAL,Gleason_8_7_8 REAL,Gleason_8_8_7 REAL,Gleason_8_8_8 REAL,
                Gleason_8_8_9 REAL,Gleason_8_9_9 REAL,
                Site_of_biopsy_9 TEXT,US_risk_features_9 TEXT,no_of_cores_9 INTEGER,BPH_9 TEXT,Prostatitis_9 TEXT,Atrophy_9 TEXT,
                BasalCellHqPerPlasiq_9 TEXT,PIN_9 TEXT,ca_prostate_9 TEXT,ca_grade_9 REAL,
                Gleason_9_2 REAL,Gleason_9_2_3 REAL,Gleason_9_3_3 REAL,Gleason_9_3_4 REAL,Gleason_9_4_3 REAL,Gleason_9_4_4 REAL,
                Gleason_9_4_5 REAL,Gleason_9_5_4 REAL,Gleason_9_5_5 REAL,Gleason_9_5_6 REAL,Gleason_9_6_5 REAL,Gleason_9_6_6 REAL,
                Gleason_9_6_7 REAL,Gleason_9_7_6 REAL,Gleason_9_7_7 REAL,Gleason_9_7_8 REAL,Gleason_9_8_7 REAL,Gleason_9_8_8 REAL,
                Gleason_9_8_9 REAL,Gleason_9_9_9 REAL,
                Site_of_biopsy_10 TEXT,US_risk_features_10 TEXT,no_of_cores_10 INTEGER,BPH_10 TEXT,Prostatitis_10 TEXT,Atrophy_10 TEXT,
                BasalCellHqPerPlasiq_10 TEXT,PIN_10 TEXT,ca_prostate_10 TEXT,ca_grade_10 REAL,
                Gleason_10_2 REAL,Gleason_10_2_3 REAL,Gleason_10_3_3 REAL,Gleason_10_3_4 REAL,Gleason_10_4_3 REAL,Gleason_10_4_4 REAL,
                Gleason_10_4_5 REAL,Gleason_10_5_4 REAL,Gleason_10_5_5 REAL,Gleason_10_5_6 REAL,Gleason_10_6_5 REAL,Gleason_10_6_6 REAL,
                Gleason_10_6_7 REAL,Gleason_10_7_6 REAL,Gleason_10_7_7 REAL,Gleason_10_7_8 REAL,Gleason_10_8_7 REAL,Gleason_10_8_8 REAL,
                Gleason_10_8_9 REAL,Gleason_10_9_9 REAL,
                FOREIGN KEY (patientsinfo_id) REFERENCES PatientsInfo(id) ON DELETE CASCADE ON UPDATE CASCADE)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS SecondBottles(
                id INTEGER PRIMARY KEY,patientsside_id INTEGER,firstbottles_id INTEGER,
                Site_of_biopsy_11 TEXT,US_risk_features_11 TEXT,no_of_cores_11 INTEGER,BPH_11 TEXT,Prostatitis_11 TEXT,Atrophy_11 TEXT,
                BasalCellHqPerPlasiq_11 TEXT,PIN_11 TEXT,ca_prostate_11 TEXT,ca_grade_11 REAL,
                Gleason_11_2 REAL,Gleason_11_2_3 REAL,Gleason_11_3_3 REAL,Gleason_11_3_4 REAL,Gleason_11_4_3 REAL,Gleason_11_4_4 REAL,
                Gleason_11_4_5 REAL,Gleason_11_5_4 REAL,Gleason_11_5_5 REAL,Gleason_11_5_6 REAL,Gleason_11_6_5 REAL,Gleason_11_6_6 REAL,
                Gleason_11_6_7 REAL,Gleason_11_7_6 REAL,Gleason_11_7_7 REAL,Gleason_11_7_8 REAL,Gleason_11_8_7 REAL,Gleason_11_8_8 REAL,
                Gleason_11_8_9 REAL,Gleason_11_9_9 REAL,
                Site_of_biopsy_12 TEXT,US_risk_features_12 TEXT,no_of_cores_12 TEXT,BPH_12 TEXT,Prostatitis_12 TEXT,Atrophy_12 TEXT,
                BasalCellHqPerPlasiq_12 TEXT,PIN_12 TEXT,ca_prostate_12 TEXT,ca_grade_12 REAL,
                Gleason_12_2 REAL,Gleason_12_2_3 REAL,Gleason_12_3_3 REAL,Gleason_12_3_4 REAL,Gleason_12_4_3 REAL,Gleason_12_4_4 REAL,
                Gleason_12_4_5 REAL,Gleason_12_5_4 REAL,Gleason_12_5_5 REAL,Gleason_12_5_6 REAL,Gleason_12_6_5 REAL,Gleason_12_6_6 REAL,
                Gleason_12_6_7 REAL,Gleason_12_7_6 REAL,Gleason_12_7_7 REAL,Gleason_12_7_8 REAL,Gleason_12_8_7 REAL,Gleason_12_8_8 REAL,
                Gleason_12_8_9 REAL,Gleason_12_9_9 REAL,
                Site_of_biopsy_13 TEXT,US_risk_features_13 TEXT,no_of_cores_13 TEXT,BPH_13 TEXT,Prostatitis_13 TEXT,Atrophy_13 TEXT,
                BasalCellHqPerPlasiq_13 TEXT,PIN_13 TEXT,ca_prostate_13 TEXT,ca_grade_13 REAL,
                Gleason_13_2 REAL,Gleason_13_2_3 REAL,Gleason_13_3_3 REAL,Gleason_13_3_4 REAL,Gleason_13_4_3 REAL,Gleason_13_4_4 REAL,
                Gleason_13_4_5 REAL,Gleason_13_5_4 REAL,Gleason_13_5_5 REAL,Gleason_13_5_6 REAL,Gleason_13_6_5 REAL,Gleason_13_6_6 REAL,
                Gleason_13_6_7 REAL,Gleason_13_7_6 REAL,Gleason_13_7_7 REAL,Gleason_13_7_8 REAL,Gleason_13_8_7 REAL,Gleason_13_8_8 REAL,
                Gleason_13_8_9 REAL,Gleason_13_9_9 REAL,
                Site_of_biopsy_14 TEXT,US_risk_features_14 TEXT,no_of_cores_14 TEXT,BPH_14 TEXT,Prostatitis_14 TEXT,Atrophy_14 TEXT,
                BasalCellHqPerPlasiq_14 TEXT,PIN_14 TEXT,ca_prostate_14 TEXT,ca_grade_14 REAL,
                Gleason_14_2 REAL,Gleason_14_2_3 REAL,Gleason_14_3_3 REAL,Gleason_14_3_4 REAL,Gleason_14_4_3 REAL,Gleason_14_4_4 REAL,
                Gleason_14_4_5 REAL,Gleason_14_5_4 REAL,Gleason_14_5_5 REAL,Gleason_14_5_6 REAL,Gleason_14_6_5 REAL,Gleason_14_6_6 REAL,
                Gleason_14_6_7 REAL,Gleason_14_7_6 REAL,Gleason_14_7_7 REAL,Gleason_14_7_8 REAL,Gleason_14_8_7 REAL,Gleason_14_8_8 REAL,
                Gleason_14_8_9 REAL,Gleason_14_9_9 REAL,
                Site_of_biopsy_15 TEXT,US_risk_features_15 TEXT,no_of_cores_15 TEXT,BPH_15 TEXT,Prostatitis_15 TEXT,Atrophy_15 TEXT,
                BasalCellHqPerPlasiq_15 TEXT,PIN_15 TEXT,ca_prostate_15 TEXT,ca_grade_15 REAL,
                Gleason_15_2 REAL,Gleason_15_2_3 REAL,Gleason_15_3_3 REAL,Gleason_15_3_4 REAL,Gleason_15_4_3 REAL,Gleason_15_4_4 REAL,
                Gleason_15_4_5 REAL,Gleason_15_5_4 REAL,Gleason_15_5_5 REAL,Gleason_15_5_6 REAL,Gleason_15_6_5 REAL,Gleason_15_6_6 REAL,
                Gleason_15_6_7 REAL,Gleason_15_7_6 REAL,Gleason_15_7_7 REAL,Gleason_15_7_8 REAL,Gleason_15_8_7 REAL,Gleason_15_8_8 REAL,
                Gleason_15_8_9 REAL,Gleason_15_9_9 REAL,
                Site_of_biopsy_16 TEXT,US_risk_features_16 TEXT,no_of_cores_16 TEXT,BPH_16 TEXT,Prostatitis_16 TEXT,Atrophy_16 TEXT,
                BasalCellHqPerPlasiq_16 TEXT,PIN_16 TEXT,ca_prostate_16 TEXT,ca_grade_16 REAL,
                Gleason_16_2 REAL,Gleason_16_2_3 REAL,Gleason_16_3_3 REAL,Gleason_16_3_4 REAL,Gleason_16_4_3 REAL,Gleason_16_4_4 REAL,
                Gleason_16_4_5 REAL,Gleason_16_5_4 REAL,Gleason_16_5_5 REAL,Gleason_16_5_6 REAL,Gleason_16_6_5 REAL,Gleason_16_6_6 REAL,
                Gleason_16_6_7 REAL,Gleason_16_7_6 REAL,Gleason_16_7_7 REAL,Gleason_16_7_8 REAL,Gleason_16_8_7 REAL,Gleason_16_8_8 REAL,
                Gleason_16_8_9 REAL,Gleason_16_9_9 REAL,
                Site_of_biopsy_17 TEXT,US_risk_features_17 TEXT,no_of_cores_17 TEXT,BPH_17 TEXT,Prostatitis_17 TEXT,Atrophy_17 TEXT,
                BasalCellHqPerPlasiq_17 TEXT,PIN_17 TEXT,ca_prostate_17 TEXT,ca_grade_17 REAL,
                Gleason_17_2 REAL,Gleason_17_2_3 REAL,Gleason_17_3_3 REAL,Gleason_17_3_4 REAL,Gleason_17_4_3 REAL,Gleason_17_4_4 REAL,
                Gleason_17_4_5 REAL,Gleason_17_5_4 REAL,Gleason_17_5_5 REAL,Gleason_17_5_6 REAL,Gleason_17_6_5 REAL,Gleason_17_6_6 REAL,
                Gleason_17_6_7 REAL,Gleason_17_7_6 REAL,Gleason_17_7_7 REAL,Gleason_17_7_8 REAL,Gleason_17_8_7 REAL,Gleason_17_8_8 REAL,
                Gleason_17_8_9 REAL,Gleason_17_9_9 REAL,
                Site_of_biopsy_18 TEXT,US_risk_features_18 TEXT,no_of_cores_18 TEXT,BPH_18 TEXT,Prostatitis_18 TEXT,Atrophy_18 TEXT,
                BasalCellHqPerPlasiq_18 TEXT,PIN_18 TEXT,ca_prostate_18 TEXT,ca_grade_18 REAL,
                Gleason_18_2 REAL,Gleason_18_2_3 REAL,Gleason_18_3_3 REAL,Gleason_18_3_4 REAL,Gleason_18_4_3 REAL,Gleason_18_4_4 REAL,
                Gleason_18_4_5 REAL,Gleason_18_5_4 REAL,Gleason_18_5_5 REAL,Gleason_18_5_6 REAL,Gleason_18_6_5 REAL,Gleason_18_6_6 REAL,
                Gleason_18_6_7 REAL,Gleason_18_7_6 REAL,Gleason_18_7_7 REAL,Gleason_18_7_8 REAL,Gleason_18_8_7 REAL,Gleason_18_8_8 REAL,
                Gleason_18_8_9 REAL,Gleason_18_9_9 REAL,
                Site_of_biopsy_19 TEXT,US_risk_features_19 TEXT,no_of_cores_19 TEXT,BPH_19 TEXT,Prostatitis_19 TEXT,Atrophy_19 TEXT,
                BasalCellHqPerPlasiq_19 TEXT,PIN_19 TEXT,ca_prostate_19 TEXT,ca_grade_19 REAL,
                Gleason_19_2 REAL,Gleason_19_2_3 REAL,Gleason_19_3_3 REAL,Gleason_19_3_4 REAL,Gleason_19_4_3 REAL,Gleason_19_4_4 REAL,
                Gleason_19_4_5 REAL,Gleason_19_5_4 REAL,Gleason_19_5_5 REAL,Gleason_19_5_6 REAL,Gleason_19_6_5 REAL,Gleason_19_6_6 REAL,
                Gleason_19_6_7 REAL,Gleason_19_7_6 REAL,Gleason_19_7_7 REAL,Gleason_19_7_8 REAL,Gleason_19_8_7 REAL,Gleason_19_8_8 REAL,
                Gleason_19_8_9 REAL,Gleason_19_9_9 REAL,
                Site_of_biopsy_20 TEXT,US_risk_features_20 TEXT,no_of_cores_20 TEXT,BPH_20 TEXT,Prostatitis_20 TEXT,Atrophy_20 TEXT,
                BasalCellHqPerPlasiq_20 TEXT,PIN_20 TEXT,ca_prostate_20 TEXT,ca_grade_20 REAL,
                Gleason_20_2 REAL,Gleason_20_2_3 REAL,Gleason_20_3_3 REAL,Gleason_20_3_4 REAL,Gleason_20_4_3 REAL,Gleason_20_4_4 REAL,
                Gleason_20_4_5 REAL,Gleason_20_5_4 REAL,Gleason_20_5_5 REAL,Gleason_20_5_6 REAL,Gleason_20_6_5 REAL,Gleason_20_6_6 REAL,
                Gleason_20_6_7 REAL,Gleason_20_7_6 REAL,Gleason_20_7_7 REAL,Gleason_20_7_8 REAL,Gleason_20_8_7 REAL,Gleason_20_8_8 REAL,
                Gleason_20_8_9 REAL,Gleason_20_9_9 REAL,Image BLOB,ImagePath TEXT,
                FOREIGN KEY (patientsside_id) REFERENCES PatientsSide(id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (firstbottles_id) REFERENCES FirstBottles(id) ON DELETE CASCADE ON UPDATE CASCADE)''')

    def get_patient_count(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo")
            return cursor.fetchone()[0]

    def get_family_history_count(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo where Family = '+ve'")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 0

    def get_dre_hard_count(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo where DRE = 'Hard'")
            num = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo where DRE = 'Right'")
            num += cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo where DRE = 'Left'")
            num += cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM PatientsInfo where DRE = 'Diffuse'")
            num += cursor.fetchone()[0]
            return num

    def get_max_us_code(self):
        with self.connection:
            cursor = self.connection.cursor()
            # Use the correct field name
            cursor.execute("SELECT US FROM PatientsInfo WHERE US IS NOT NULL AND US != ''")
            results = cursor.fetchall()
            
            if not results:
                return 0
                
            max_value = 0
            for row in results:
                us_code = row[0]
                if us_code and us_code.strip():
                    try:
                        numeric_value = int(us_code.lstrip('0') or '0')
                        max_value = max(max_value, numeric_value)
                    except (ValueError, TypeError):
                        continue
        
            return max_value

    def perform_search(self, search_category_one, search_text_one, search_category_two, search_text_two):
        """Perform a search across all patient-related tables with proper SQL injection protection.
        
        Args:
            search_category_one: Column name for first search condition
            search_text_one: Text to search in first category
            search_category_two: Column name for second search condition
            search_text_two: Text to search in second category
            
        Returns:
            Dictionary containing search results from all related tables
        """
        try:
            # Validate input parameters
            if not search_text_one and not search_text_two:
                return {
                    'patients_info': [],
                    'patients_side': [],
                    'first_bottles': [],
                    'second_bottles': []  # Fixed typo from original
                }

            # Initialize parameter list for safe query construction
            params = []
            conditions = []
            
            # Construct conditions with parameterized inputs
            if search_text_one:
                conditions.append(f"{search_category_one} LIKE ?")
                params.append(f"%{search_text_one}%")

            if search_text_two:
                conditions.append(f"{search_category_two} LIKE ?")
                params.append(f"%{search_text_two}%")

            # Build the base query
            base_query = "SELECT * FROM PatientsInfo"
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            with self.connection:
                cursor = self.connection.cursor()
                
                # Execute main patient info query
                cursor.execute(base_query, params)
                search_results = cursor.fetchall()

                if not search_results:
                    return {
                        'patients_info': [],
                        'patients_side': [],
                        'first_bottles': [],
                        'second_bottles': []
                    }

                # Get IDs from search results
                ids = [row[0] for row in search_results]
                id_placeholders = ','.join(['?'] * len(ids))

                # Query PatientsSide table (excluding ID column)
                side_query = f"""
                    SELECT 
                        AApexR, AApexL, AMidProstateR, AMidProstateL, 
                        ABaseR, ABaseL, MApexR, MApexL,
                        MMidprostateR, MMidprostateL, MBaseR, MBaseL,
                        PApexR, PApexL, PMidprostateR, PMidprostateL,
                        PBaseR, PBaseL, TMidprostateR, TMidprostateL,
                        TBaseR, TBaseL
                    FROM PatientsSide 
                    WHERE patientsinfo_id IN ({id_placeholders})
                """
                cursor.execute(side_query, ids)
                side_results = cursor.fetchall()

                # Query FirstBottles table
                bottles_query = f"""
                    SELECT patientsinfo_id,
                    Site_of_biopsy_1,US_risk_features_1,no_of_cores_1,BPH_1,Prostatitis_1,Atrophy_1,
                    BasalCellHqPerPlasiq_1,PIN_1,ca_prostate_1,ca_grade_1,
                    Site_of_biopsy_2,US_risk_features_2,no_of_cores_2,BPH_2,Prostatitis_2,Atrophy_2,
                    BasalCellHqPerPlasiq_2,PIN_2,ca_prostate_2,ca_grade_2,
                    Site_of_biopsy_3,US_risk_features_3,no_of_cores_3,BPH_3,Prostatitis_3,Atrophy_3,
                    BasalCellHqPerPlasiq_3,PIN_3,ca_prostate_3,ca_grade_3,
                    Site_of_biopsy_4,US_risk_features_4,no_of_cores_4,BPH_4,Prostatitis_4,Atrophy_4,
                    BasalCellHqPerPlasiq_4,PIN_4,ca_prostate_4,ca_grade_4,
                    Site_of_biopsy_5,US_risk_features_5,no_of_cores_5,BPH_5,Prostatitis_5,Atrophy_5,
                    BasalCellHqPerPlasiq_5,PIN_5,ca_prostate_5,ca_grade_5,
                    Site_of_biopsy_6,US_risk_features_6,no_of_cores_6,BPH_6,Prostatitis_6,Atrophy_6,
                    BasalCellHqPerPlasiq_6,PIN_6,ca_prostate_6,ca_grade_6,
                    Site_of_biopsy_7,US_risk_features_7,no_of_cores_7,BPH_7,Prostatitis_7,Atrophy_7,
                    BasalCellHqPerPlasiq_7,PIN_7,ca_prostate_7,ca_grade_7,
                    Site_of_biopsy_8,US_risk_features_8,no_of_cores_8,BPH_8,Prostatitis_8,Atrophy_8,
                    BasalCellHqPerPlasiq_8,PIN_8,ca_prostate_8,ca_grade_8,
                    Site_of_biopsy_9,US_risk_features_9,no_of_cores_9,BPH_9,Prostatitis_9,Atrophy_9,
                    BasalCellHqPerPlasiq_9,PIN_9,ca_prostate_9,ca_grade_9,
                    Site_of_biopsy_10,US_risk_features_10,no_of_cores_10,BPH_10,Prostatitis_10,Atrophy_10,
                    BasalCellHqPerPlasiq_10,PIN_10,ca_prostate_10,ca_grade_10
                  FROM FirstBottles 
                    WHERE patientsinfo_id IN ({id_placeholders})
                """
                cursor.execute(bottles_query, ids)
                bottles_results = cursor.fetchall()
                # Query SecondBottles table
                second_bottles_query = f"""
                    SELECT firstbottles_id,
                    Site_of_biopsy_11,US_risk_features_11,no_of_cores_11,BPH_11,Prostatitis_11,Atrophy_11,
                    BasalCellHqPerPlasiq_11,PIN_11,ca_prostate_11,ca_grade_11,
                    Site_of_biopsy_12,US_risk_features_12,no_of_cores_12,BPH_12,Prostatitis_12,Atrophy_12,
                    BasalCellHqPerPlasiq_12,PIN_12,ca_prostate_12,ca_grade_12,
                    Site_of_biopsy_13,US_risk_features_13,no_of_cores_13,BPH_13,Prostatitis_13,Atrophy_13,
                    BasalCellHqPerPlasiq_13,PIN_13,ca_prostate_13,ca_grade_13,
                    Site_of_biopsy_14,US_risk_features_14,no_of_cores_14,BPH_14,Prostatitis_14,Atrophy_14,
                    BasalCellHqPerPlasiq_14,PIN_14,ca_prostate_14,ca_grade_14,
                    Site_of_biopsy_15,US_risk_features_15,no_of_cores_15,BPH_15,Prostatitis_15,Atrophy_15,
                    BasalCellHqPerPlasiq_15,PIN_15,ca_prostate_15,ca_grade_15,
                    Site_of_biopsy_16,US_risk_features_16,no_of_cores_16,BPH_16,Prostatitis_16,Atrophy_16,
                    BasalCellHqPerPlasiq_16,PIN_16,ca_prostate_16,ca_grade_16,
                    Site_of_biopsy_17,US_risk_features_17,no_of_cores_17,BPH_17,Prostatitis_17,Atrophy_17,
                    BasalCellHqPerPlasiq_17,PIN_17,ca_prostate_17,ca_grade_17,
                    Site_of_biopsy_18,US_risk_features_18,no_of_cores_18,BPH_18,Prostatitis_18,Atrophy_18,
                    BasalCellHqPerPlasiq_18,PIN_18,ca_prostate_18,ca_grade_18,
                    Site_of_biopsy_19,US_risk_features_19,no_of_cores_19,BPH_19,Prostatitis_19,Atrophy_19,
                    BasalCellHqPerPlasiq_19,PIN_19,ca_prostate_19,ca_grade_19,
                    Site_of_biopsy_20,US_risk_features_20,no_of_cores_20,BPH_20,Prostatitis_20,Atrophy_20,
                    BasalCellHqPerPlasiq_20,PIN_20,ca_prostate_20,ca_grade_20 
                FROM SecondBottles 
                    WHERE patientsside_id IN (
                        SELECT id FROM PatientsSide 
                        WHERE patientsinfo_id IN ({id_placeholders})
                    )
                """
                cursor.execute(second_bottles_query, ids)
                second_bottles_results = cursor.fetchall()

                return {
                    'patients_info': search_results,
                    'patients_side': side_results,
                    'first_bottles': self.clean_data(bottles_results),
                    'second_bottles': self.clean_data(second_bottles_results)
                }
                

        except sqlite3.Error as e:
            showerror("Database Error", f"Failed to perform search: {str(e)}")
            return {
                'patients_info': [],
                'patients_side': [],
                'first_bottles': [],
                'second_bottles': []
            }
        except Exception as e:
            showerror("Error", f"An unexpected error occurred: {str(e)}")
            return {
                'patients_info': [],
                'patients_side': [],
                'first_bottles': [],
                'second_bottles': []
            }
    
    def insert_into_first_db(self, entries_1, entries_2, entries_3, entries_4):
        try:
            # Prepare the INSERT statements dynamically based on the table schemas
            entries_for_db = dict(entries_1)
            # Ensure ImagePath is set to the path, and Image is the binary
            if "Image_stored" in entries_for_db:
                entries_for_db["Image"] = entries_for_db["Image_stored"]
            if "Image" in entries_for_db:
                entries_for_db["ImagePath"] = entries_1.get("Image", None)
            # Only use columns that exist in the table
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(PatientsInfo)")
                valid_cols = [col[1] for col in cursor.fetchall()]
            # Use quoted column names for Image and ImagePath
            columns_1 = []
            values_1 = []
            for k, v in entries_for_db.items():
                if k == "Image":
                    columns_1.append('"Image"')
                    values_1.append(v)
                elif k == "ImagePath":
                    columns_1.append('"ImagePath"')
                    values_1.append(v)
                elif k in valid_cols:
                    columns_1.append(k)
                    values_1.append(v)
            columns_1_str = ', '.join(columns_1)
            placeholders_1 = ', '.join(['?' for _ in range(len(values_1))])
            sql_1 = f"INSERT INTO PatientsInfo ({columns_1_str}) VALUES ({placeholders_1})"
            # ... rest of the method unchanged ...
            input_data_1 = [v if v != '' else None for v in values_1]
            columns_2 = ', '.join(entries_2.keys())
            placeholders_2 = ', '.join(['?' for _ in range(len(entries_2))])
            columns_3 = ', '.join(entries_3.keys())
            placeholders_3 = ', '.join(['?' for _ in range(len(entries_3))])
            columns_4 = ', '.join(entries_4.keys())
            placeholders_4 = ', '.join(['?' for _ in range(len(entries_4))])
            sql_2=f"INSERT INTO PatientsSide ({columns_2}) VALUES ({placeholders_2})"
            sql_3=f"INSERT INTO FirstBottles ({columns_3}) VALUES ({placeholders_3})"
            sql_4=f"INSERT INTO SecondBottles ({columns_4}) VALUES ({placeholders_4})"
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql_1, input_data_1)
                self.connection.commit()  # Commit first insertion
                if columns_2:
                    cursor.execute(sql_2, [v if v != '' else None for v in entries_2.values()])
                    self.connection.commit()
                if columns_3:
                    cursor.execute(sql_3, [v if v != '' else None for v in entries_3.values()])
                    self.connection.commit()
                if columns_4:
                    cursor.execute(sql_4, [v if v != '' else None for v in entries_4.values()])
                    self.connection.commit()
        except sqlite3.Error as e:
            showinfo("SQLite Error", f"SQLite error: {e}")
            
    def insert_into_patients_side(self, patientsinfo_id, entries_2):
        """
        Insert a row into the PatientsSide table for the given patient.
        :param patientsinfo_id: The ID from PatientsInfo to link this entry.
        :param entries_2: Dictionary of data for PatientsSide (zone values, etc).
        """
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(PatientsSide)")
                valid_cols = [col[1] for col in cursor.fetchall() if col[1] != 'id']
            # Always include patientsinfo_id
            entries_for_db = dict(entries_2)
            entries_for_db['patientsinfo_id'] = patientsinfo_id
            columns = []
            values = []
            for k, v in entries_for_db.items():
                if k in valid_cols:
                    columns.append(k)
                    values.append(v)
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?' for _ in range(len(values))])
            sql = f"INSERT INTO PatientsSide ({columns_str}) VALUES ({placeholders})"
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                self.connection.commit()
        except sqlite3.Error as e:
            showinfo("SQLite Error", f"Failed to insert into PatientsSide: {e}")

    def insert_into_FirstBottles(self, patientsinfo_id, entries_3):
        """
        Insert a row into the FirstBottles table for the given patient.
        
        Args:
            patientsinfo_id: The ID from PatientsInfo to link this entry
            entries_3: Dictionary of data for FirstBottles (biopsy data, images, etc.)
        
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        try:
            # Get valid columns from the FirstBottles table
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(FirstBottles)")
                valid_cols = {col[1] for col in cursor.fetchall()}  # Using set for faster lookups
                valid_cols.discard('id')  # Remove auto-increment ID column

            # Prepare data for insertion with image handling
            entries_for_db = {}
            
            # Process image data first
            if "Image" in entries_3:
                # Case 1: Already binary data
                if isinstance(entries_3["Image"], (bytes, bytearray)):
                    entries_for_db["Image"] = entries_3["Image"]
                    entries_for_db["ImagePath"] = entries_3.get("ImagePath")
                
                # Case 2: Path to image file (convert to binary)
                elif isinstance(entries_3["Image"], str):
                    try:
                        with open(entries_3["Image"], 'rb') as img_file:
                            entries_for_db["Image"] = img_file.read()
                        entries_for_db["ImagePath"] = entries_3["Image"]  # Store original path
                    except Exception as e:
                        print(f"Error reading image file: {e}")
                        entries_for_db["Image"] = None
                        entries_for_db["ImagePath"] = None
                
                # Case 3: Invalid image data
                else:
                    entries_for_db["Image"] = None
                    entries_for_db["ImagePath"] = None
            
            # Add all other valid fields
            for col in valid_cols:
                if col in entries_3 and col not in ("Image", "ImagePath"):
                    entries_for_db[col] = entries_3[col]
            
            # Always include patientsinfo_id
            entries_for_db['patientsinfo_id'] = patientsinfo_id

            # Build the SQL query
            columns = []
            values = []
            for col, val in entries_for_db.items():
                if col in valid_cols or col == 'patientsinfo_id':
                    columns.append(col)
                    values.append(val)

            if not columns:
                raise ValueError("No valid columns to insert")

            columns_str = ', '.join(f'"{col}"' for col in columns)
            placeholders = ', '.join(['?'] * len(columns))
            sql = f"INSERT INTO FirstBottles ({columns_str}) VALUES ({placeholders})"

            # Execute the insertion
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                return True

        except sqlite3.Error as e:
            print(f"SQLite Error inserting into FirstBottles: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error inserting into FirstBottles: {e}")
            return False

    # Add this method to the DatabaseManager class in database.py
    def update_first_bottles(self, patientsinfo_id, updated_fields):
        """
        Update a patient's information in the FirstBottles table.
        :param patientsinfo_id: The patientsinfo_id to update.
        :param updated_fields: A dictionary of column names and their new values.
        """
        if not updated_fields:
            return
        set_clause = ', '.join([f'{k} = ?' for k in updated_fields.keys()])
        values = list(updated_fields.values())
        values.append(patientsinfo_id)
        sql = f"UPDATE FirstBottles SET {set_clause} WHERE patientsinfo_id = ?"
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                self.connection.commit()
        except sqlite3.Error as e:
            showinfo("SQLite Error", f"Failed to update FirstBottles: {e}")      
    def update_table(self):
            try:
                with self.connection:
                    cursor1 = self.connection.cursor()
                    # Get column names for each table (excluding 'id')
                    cursor1.execute("PRAGMA table_info(PatientsInfo)")
                    patients_info_cols = [col[1] for col in cursor1.fetchall() if col[1] != 'id']
                    cursor1.execute("PRAGMA table_info(PatientsSide)")
                    patients_side_cols = [col[1] for col in cursor1.fetchall() if col[1] != 'id']
                    cursor1.execute("PRAGMA table_info(FirstBottles)")
                    first_bottles_cols = [col[1] for col in cursor1.fetchall() if col[1] != 'id'][5:]
                    cursor1.execute("PRAGMA table_info(SecondBottles)")
                    second_bottles_cols = [col[1] for col in cursor1.fetchall() if col[1] != 'id'][1:]
                    try:
                        # Clean first_bottles_cols
                        first_bottles_cols[:] = [col for col in first_bottles_cols 
                                                if not (isinstance(col, str) and "Gleason" in col)]
                        
                        # Clean second_bottles_cols
                        second_bottles_cols[:] = [col for col in second_bottles_cols 
                                                if not (isinstance(col, str) and "Gleason" in col)]
                        
                    except Exception as e:
                        showerror(f"Error occurred: {e}")

                    # Get the last 10 patient IDs (descending order)
                    cursor1.execute("SELECT ID FROM PatientsInfo ORDER BY ID DESC LIMIT 10")
                    last_10_ids = [row[0] for row in cursor1.fetchall()]
                    if not last_10_ids:
                        return {
                            'patients_info': [],
                            'patients_side': [],
                            'first_bottles': [],
                            'second_bottles': []
                        }
                    ids_str = ','.join(str(i) for i in last_10_ids)
                    # Select all columns except 'id' for the last 10 patients
                    cursor1.execute(f"SELECT {', '.join(patients_info_cols)} FROM PatientsInfo WHERE ID IN ({ids_str}) ORDER BY ID DESC")
                    data1 = cursor1.fetchall()
                    cursor1.execute(f"SELECT {', '.join(patients_side_cols)} FROM PatientsSide WHERE patientsinfo_id IN ({ids_str}) ORDER BY ID DESC")
                    data2 = cursor1.fetchall()
                    cursor1.execute(f"SELECT {', '.join(first_bottles_cols)} FROM FirstBottles WHERE patientsinfo_id IN ({ids_str}) ORDER BY ID DESC")
                    data3 = cursor1.fetchall()
                    # For SecondBottles, get patientsside_id for the last 10 patients
                    cursor1.execute(f"SELECT id FROM PatientsSide WHERE patientsinfo_id IN ({ids_str}) ORDER BY ID DESC")
                    side_ids = [row[0] for row in cursor1.fetchall()]
                    if side_ids:
                        side_ids_str = ','.join(str(i) for i in side_ids)
                        cursor1.execute(f"SELECT {', '.join(second_bottles_cols)} FROM SecondBottles WHERE patientsside_id IN ({side_ids_str}) ORDER BY ID DESC")
                        data4 = cursor1.fetchall()
                    else:
                        data4 = []
                return {
                    'patients_info': data1,
                    'patients_side': data2,
                    'first_bottles': self.clean_data(data3),
                    'second_bottles': self.clean_data(data4)
                }
            except Exception as e:
                showinfo("Error", e)
                return {
                    'patients_info': [],
                    'patients_side': [],
                    'first_bottles': [],
                    'second_bottles': []
                }
    def clean_data(self,data):
                return [tuple("" if item is None else item for item in row) for row in data]
    def update_patient(self, patient_id, updated_fields):
        """
        Update a patient's information in the PatientsInfo table.
        :param patient_id: The ID of the patient to update.
        :param updated_fields: A dictionary of column names and their new values.
        """
        if not updated_fields:
            return
        set_clause = ', '.join([f'{k} = ?' for k in updated_fields.keys()])
        values = list(updated_fields.values())
        values.append(patient_id)
        sql = f"UPDATE PatientsInfo SET {set_clause} WHERE ID = ?"
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                self.connection.commit()
        except sqlite3.Error as e:
            showinfo("SQLite Error", f"Failed to update patient: {e}")

    def update_patients_side(self, patientsinfo_id, updated_fields):
        """
        Update a patient's information in the PatientsSide table.
        :param patientsinfo_id: The patientsinfo_id to update.
        :param updated_fields: A dictionary of column names and their new values.
        """
        if not updated_fields:
            return
        set_clause = ', '.join([f'{k} = ?' for k in updated_fields.keys()])
        values = list(updated_fields.values())
        values.append(patientsinfo_id)
        sql = f"UPDATE PatientsSide SET {set_clause} WHERE patientsinfo_id = ?"
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                self.connection.commit()
        except sqlite3.Error as e:
            showinfo("SQLite Error", f"Failed to update PatientsSide: {e}")
    def insert_into_SecondBottles(self, patientsside_id, entries_4):
        """
        Insert a row into the SecondBottles table for the given patient.
        
        Args:
            patientsside_id: The ID from PatientsSide to link this entry
            firstbottles_id: The ID from FirstBottles to link this entry
            entries_4: Dictionary of data for SecondBottles (biopsy data, images, etc.)
        
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        try:
            # Get valid columns from the SecondBottles table
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(SecondBottles)")
                valid_cols = {col[1] for col in cursor.fetchall()}  # Using set for faster lookups
                valid_cols.discard('id')  # Remove auto-increment ID column

            # Prepare data for insertion with image handling
            entries_for_db = {}
            
            # Process image data if present
            if "Image" in entries_4:
                # Case 1: Already binary data
                if isinstance(entries_4["Image"], (bytes, bytearray)):
                    entries_for_db["Image"] = entries_4["Image"]
                
                # Case 2: Path to image file (convert to binary)
                elif isinstance(entries_4["Image"], str):
                    try:
                        with open(entries_4["Image"], 'rb') as img_file:
                            entries_for_db["Image"] = img_file.read()
                    except Exception as e:
                        print(f"Error reading image file: {e}")
                        entries_for_db["Image"] = None
                
                # Case 3: Invalid image data
                else:
                    entries_for_db["Image"] = None
            
            # Add all other valid fields
            for col in valid_cols:
                if col in entries_4 and col != "Image":
                    entries_for_db[col] = entries_4[col]
            
            # Always include the foreign keys
            entries_for_db['patientsside_id'] = patientsside_id
            entries_for_db['firstbottles_id'] = patientsside_id

            # Build the SQL query
            columns = []
            values = []
            for col, val in entries_for_db.items():
                if col in valid_cols or col in ('patientsside_id', 'firstbottles_id'):
                    columns.append(col)
                    values.append(val)

            if not columns:
                raise ValueError("No valid columns to insert")

            columns_str = ', '.join(f'"{col}"' for col in columns)
            placeholders = ', '.join(['?'] * len(columns))
            sql = f"INSERT INTO SecondBottles ({columns_str}) VALUES ({placeholders})"

            # Execute the insertion
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                return True

        except sqlite3.Error as e:
            showerror("SQLite Error",f"SQLite Error inserting into SecondBottles: {e}")
            return False
        except Exception as e:
            showinfo("Error",f"Unexpected error inserting into SecondBottles: {e}")
            return False

    def update_second_bottles(self, second_bottles_id, updated_fields):
        """
        Update a patient's information in the SecondBottles table.
        
        Args:
            second_bottles_id: The ID of the SecondBottles record to update
            updated_fields: A dictionary of column names and their new values
        """
        if not updated_fields:
            return False
            
        try:
            # Get valid columns from the SecondBottles table
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(SecondBottles)")
                valid_cols = {col[1] for col in cursor.fetchall()}
                valid_cols.discard('id')  # Don't allow updating the ID

            # Filter the updated_fields to only include valid columns
            filtered_fields = {}
            for col, val in updated_fields.items():
                if col in valid_cols:
                    # Handle image data conversion if needed
                    if col == "Image" and isinstance(val, str):
                        try:
                            with open(val, 'rb') as img_file:
                                filtered_fields[col] = img_file.read()
                        except Exception as e:
                            print(f"Error reading image file: {e}")
                            continue
                    else:
                        filtered_fields[col] = val

            if not filtered_fields:
                return False

            # Build the update query
            set_clause = ', '.join([f'{k} = ?' for k in filtered_fields.keys()])
            values = list(filtered_fields.values())
            values.append(second_bottles_id)
            
            sql = f"UPDATE SecondBottles SET {set_clause} WHERE id = ?"

            # Execute the update
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(sql, values)
                return True

        except sqlite3.Error as e:
            showerror("SQLite Error",f"SQLite Error updating SecondBottles: {e}")
            return False
        except Exception as e:
            showerror("Error",f"Unexpected error updating SecondBottles: {e}")
            return False