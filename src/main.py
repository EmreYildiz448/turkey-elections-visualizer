#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    project_root = Path(sys._MEIPASS)
else:
    # Running in a normal environment
    project_root = Path(__file__).resolve().parent.parent

sys.path.append(str(project_root))

from src.app import YerelSecimApp
from src.data_loader import load_excel_files
import tkinter as tk

def main():
    df_dict_map, countrywide_df_dict_map, datatable_df_dict = load_excel_files()
    root = tk.Tk()
    
    def on_closing():
        root.destroy()
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    app = YerelSecimApp(root, df_dict_map, countrywide_df_dict_map, datatable_df_dict)
    root.mainloop()

if __name__ == "__main__":
    main()


# In[ ]:




