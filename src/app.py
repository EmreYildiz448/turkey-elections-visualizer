#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
import os
import webbrowser
import random
from src.chart_utils import *
from src.config import party_list, tooltip_texts, groupby_list, groupby_remover, size_configurations

def find_best_resolution_match(screen_width, screen_height):
    available_resolutions = [(int(w), int(h)) for w, h in [res.split('x') for res in size_configurations.keys() if res != "default"]]
    best_match = "default"
    for width, height in available_resolutions:
        if width <= screen_width and height <= screen_height:
            if best_match == "default" or (width > int(best_match.split('x')[0]) and height > int(best_match.split('x')[1])):
                best_match = f"{width}x{height}"
    return best_match

class YerelSecimApp:
    def __init__(self, root, df_dict_map, countrywide_df_dict_map, datatable_df_dict):
        self.root = root
        self.root.minsize(800, 600)
        self.df_dict_map = df_dict_map
        self.countrywide_df_dict_map = countrywide_df_dict_map
        self.datatable_df_dict = datatable_df_dict
        self.root.title('Yerel Seçim Analiz Programı')
        self.root.state("zoomed")

        # Initialize size globals
        self.initialize_size_globals()

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(
            row=0, column=0, sticky="nsew"
        )

        # Frames within the notebook
        self.pie_chart_frame = ttk.Frame(
            self.notebook, width=self.PIE_CHART_FRAME_WIDTH, height=self.PIE_CHART_FRAME_HEIGHT
        )
        self.notebook.add(
            self.pie_chart_frame, text="Dairesel Grafik Üreticisi"
        )

        self.data_table_frame = ttk.Frame(
            self.notebook, width=self.DATA_TABLE_FRAME_WIDTH, height=self.DATA_TABLE_FRAME_HEIGHT
        )
        self.notebook.add(
            self.data_table_frame, text="Veri Tablosu"
        )

        # Configure root grid for centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize UI elements
        self.current_df = None
        self.unfiltered_df = None
        self.filtered_df = None
        self.page_number = 1
        self.row_limit = 100
        self.total_pages = 1
        self.column_check_vars = {}
        self.add_data_table_widgets()

        # Initialize additional UI components
        self.frames_widgets = []
        self.data_storage = {}
        self.data_screen_count = 1
        self.comparison_var = tk.BooleanVar()
        self.comparison_checkbox = tk.Checkbutton(
            self.pie_chart_frame,
            text="Karşılaştırmalı analiz",
            variable=self.comparison_var,
            command=self.toggle_comparison
        )
        self.comparison_checkbox.grid(
            row=0, column=0, columnspan=3, pady=self.PADY
        )

        # Initialize frames
        self.data_frame = tk.Frame(
            self.pie_chart_frame, width=self.DATA_FRAME_WIDTH, height=self.DATA_FRAME_HEIGHT
        )
        self.data_frame.grid(
            row=1, column=2, sticky="ns", padx=self.PADX, pady=self.PADY
        )

        self.checkbox_frame = tk.Frame(self.data_frame)
        self.checkbox_frame.grid(
            row=0, column=0, sticky="nsew", padx=self.PADX, pady=self.PADY
        )

        self.calculate_difference_var = tk.BooleanVar()
        self.calculate_difference_checkbox = tk.Checkbutton(
            self.checkbox_frame,
            text="Fark hesapla",
            variable=self.calculate_difference_var,
            command=self.toggle_difference_screen
        )
        self.calculate_difference_checkbox.grid(
            row=1, column=0, pady=self.PADY
        )
        self.calculate_difference_checkbox.grid_remove()

        self.percentage_var = tk.BooleanVar()
        self.percentage_checkbox = tk.Checkbutton(
            self.checkbox_frame,
            text="Yüzdelik (%)",
            variable=self.percentage_var,
            command=self.toggle_percentages
        )
        self.percentage_checkbox.grid(
            row=1, column=1, pady=self.PADY, padx=(10, 0)
        )

        self.analysis_container_frame = tk.Frame(
            self.pie_chart_frame, width=self.ANALYSIS_CONTAINER_FRAME_WIDTH, height=self.ANALYSIS_CONTAINER_FRAME_HEIGHT
        )
        self.analysis_container_frame.grid(
            row=1, column=0, sticky="nsew", padx=self.PADX, pady=self.PADY
        )

        self.chart_frame = tk.Frame(
            self.pie_chart_frame, width=self.CHART_FRAME_WIDTH, height=self.CHART_FRAME_HEIGHT
        )
        self.chart_frame.grid(
            row=1, column=1, sticky="nsew", padx=self.PADX, pady=self.PADY
        )

        # Grid configuration within frames
        self.pie_chart_frame.grid_columnconfigure(0, weight=1)
        self.pie_chart_frame.grid_columnconfigure(1, weight=3)
        self.pie_chart_frame.grid_columnconfigure(2, weight=0)
        self.pie_chart_frame.grid_rowconfigure(1, weight=1)
        self.analysis_container_frame.grid_rowconfigure(0, weight=1)
        self.analysis_container_frame.grid_columnconfigure(0, weight=1)

        # Initialize data text areas and analysis frame
        self.data_text_areas = []
        self.create_analysis_frame()
        self.create_data_text_areas(1)
        self.analysis_combo_state = "disabled"

    def __del__(self):
        self.root.quit()

    def initialize_size_globals(self):
        # Detect screen resolution and retrieve configuration
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        resolution_key = f"{screen_width}x{screen_height}"
        config = size_configurations.get(resolution_key, size_configurations["default"])
    
        # Set application size
        self.APP_WIDTH = config["app_size"]["width"]
        self.APP_HEIGHT = config["app_size"]["height"]
    
        # Set frame sizes
        self.PIE_CHART_FRAME_WIDTH = config["frame_sizes"]["pie_chart_frame"]["width"]
        self.PIE_CHART_FRAME_HEIGHT = config["frame_sizes"]["pie_chart_frame"]["height"]
        self.DATA_TABLE_FRAME_WIDTH = config["frame_sizes"]["data_table_frame"]["width"]
        self.DATA_TABLE_FRAME_HEIGHT = config["frame_sizes"]["data_table_frame"]["height"]
        self.DATA_FRAME_WIDTH = config["frame_sizes"]["data_frame"]["width"]
        self.DATA_FRAME_HEIGHT = config["frame_sizes"]["data_frame"]["height"]
        self.ANALYSIS_CONTAINER_FRAME_WIDTH = config["frame_sizes"]["analysis_container_frame"]["width"]
        self.ANALYSIS_CONTAINER_FRAME_HEIGHT = config["frame_sizes"]["analysis_container_frame"]["height"]
        self.CHART_FRAME_WIDTH = config["frame_sizes"]["chart_frame"]["width"]
        self.CHART_FRAME_HEIGHT = config["frame_sizes"]["chart_frame"]["height"]
        self.ANALYSIS_FRAME_WIDTH = config["frame_sizes"]["analysis_frame"]["width"]
        self.ANALYSIS_FRAME_HEIGHT = config["frame_sizes"]["analysis_frame"]["height"]
    
        # Set minimum widths for index_frame and tree_frame
        self.INDEX_FRAME_MIN_WIDTH = config["frame_sizes"]["index_frame_min_width"]
        self.TREE_FRAME_MIN_WIDTH = config["frame_sizes"]["tree_frame_min_width"]
    
        # Set widget sizes
        self.COMBOBOX_WIDTH = config["widget_sizes"]["combobox_width"]
        self.HELP_BUTTON_WIDTH = config["widget_sizes"]["help_button_width"]
        self.BUTTON_WIDTH = config["widget_sizes"]["button_width"]
        self.ENTRY_WIDTH = config["widget_sizes"]["entry_width"]
        self.TEXT_AREA_WIDTH = config["widget_sizes"]["text_area_width"]
    
        # Tooltip sizes
        self.TOOLTIP_WIDTH = config["tooltip_size"]["width"]
        self.TOOLTIP_HEIGHT = config["tooltip_size"]["height"]
        
        # Set spacing
        self.PADX = config["spacing"]["padx"]
        self.PADY = config["spacing"]["pady"]

    def add_data_table_widgets(self):
        """Add widgets for 'Seçim yılı', 'Seçim türü', 'Seç', pagination controls, and DataFrame display."""
        year_values = ['2019', '2024']
        type_values = ['başkanlık', 'meclis']
        
        self.control_frame_left = ttk.Frame(self.data_table_frame)
        self.control_frame_left.grid(row=0, column=0, rowspan=2, padx=self.PADX, pady=self.PADY, sticky="nsew")
    
        # Province selection
        self.province_label = ttk.Label(self.control_frame_left, text="İl")
        self.province_label.grid(row=0, column=0, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.province_combo = ttk.Combobox(self.control_frame_left, state="readonly", width=self.COMBOBOX_WIDTH)
        self.province_combo.grid(row=0, column=1, padx=self.PADX, pady=self.PADY, sticky="w")
        self.province_combo.bind("<<ComboboxSelected>>", self.update_county_combo)
    
        # County selection
        self.county_label = ttk.Label(self.control_frame_left, text="İlçe")
        self.county_label.grid(row=1, column=0, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.county_combo = ttk.Combobox(self.control_frame_left, state="readonly", width=self.COMBOBOX_WIDTH)
        self.county_combo.grid(row=1, column=1, padx=self.PADX, pady=self.PADY, sticky="w")
        self.county_combo.bind("<<ComboboxSelected>>", self.update_town_combo)
    
        # Town selection
        self.town_label = ttk.Label(self.control_frame_left, text="Belde")
        self.town_label.grid(row=2, column=0, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.town_combo = ttk.Combobox(self.control_frame_left, state="readonly", width=self.COMBOBOX_WIDTH)
        self.town_combo.grid(row=2, column=1, padx=self.PADX, pady=self.PADY, sticky="w")
    
        # Selection buttons
        self.select_index_button = ttk.Button(self.control_frame_left, text="Satır filtrele", command=self.query_df_rows, width=self.BUTTON_WIDTH)
        self.select_index_button.grid(row=3, column=0, columnspan=2, padx=self.PADX, pady=self.PADY)
    
        self.reset_button = ttk.Button(self.control_frame_left, text="Sıfırla", command=self.reset_selections, width=self.BUTTON_WIDTH)
        self.reset_button.grid(row=4, column=0, columnspan=2, padx=self.PADX, pady=self.PADY)
    
        # Upper Control Frame
        self.control_frame_upper = ttk.Frame(self.data_table_frame)
        self.control_frame_upper.grid(row=0, column=1, columnspan=6, padx=self.PADX, pady=self.PADY, sticky="nsew")
    
        # Year and type selection
        self.year_label = ttk.Label(self.control_frame_upper, text="Seçim yılı:")
        self.year_label.grid(row=0, column=0, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.year_combo = ttk.Combobox(self.control_frame_upper, values=year_values, state="readonly")
        self.year_combo.grid(row=0, column=1, padx=self.PADX, pady=self.PADY, sticky="w")
        self.year_combo.set(year_values[0])
    
        self.type_label = ttk.Label(self.control_frame_upper, text="Seçim türü:")
        self.type_label.grid(row=0, column=2, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.type_combo = ttk.Combobox(self.control_frame_upper, values=type_values, state="readonly")
        self.type_combo.grid(row=0, column=3, padx=self.PADX, pady=self.PADY, sticky="w")
        self.type_combo.set(type_values[0])
    
        self.select_button = ttk.Button(self.control_frame_upper, text="Tablo seç", command=self.load_and_populate, width=self.BUTTON_WIDTH)
        self.select_button.grid(row=0, column=4, padx=self.PADX, pady=self.PADY)
    
        # Column picker and filter buttons
        self.control_frame_upperright = ttk.Frame(self.data_table_frame)
        self.control_frame_upperright.grid(row=0, column=8, padx=self.PADX, pady=self.PADY, sticky="ne")
    
        self.columnpicker_label = ttk.Label(self.control_frame_upperright, text="Sütun filtresi")
        self.columnpicker_label.grid(row=0, column=0, padx=self.PADX, pady=self.PADY)
    
        self.columnpicker_button = ttk.Button(self.control_frame_upperright, text="Sütun seç", command=self.open_column_selection_window, width=self.BUTTON_WIDTH)
        self.columnpicker_button.grid(row=1, column=0, padx=self.PADX, pady=self.PADY)
    
        self.filter_button = ttk.Button(self.control_frame_upperright, text="Sütun filtrele", command=self.query_df_columns, width=self.BUTTON_WIDTH)
        self.filter_button.grid(row=2, column=0, padx=self.PADX, pady=self.PADY)
    
        # Treeviews for displaying data
        self.index_frame = ttk.Frame(self.data_table_frame)
        self.index_frame.grid(row=1, column=1, padx=self.PADX, pady=self.PADY, sticky="nsew")
        
        self.tree_frame = ttk.Frame(self.data_table_frame)
        self.tree_frame.grid(row=1, column=2, padx=self.PADX, pady=self.PADY, sticky="nsew")
        
        # Set Treeview widgets in their respective frames
        self.index_tree = ttk.Treeview(self.index_frame, show="headings", selectmode="browse")
        self.index_tree.grid(row=0, column=0, sticky="nsew", padx=self.PADX, pady=self.PADY)
        
        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=self.PADX, pady=self.PADY)
        
        # Lock minimum width of frames to keep `index_tree` visible and prevent it from collapsing
        self.index_frame.grid_propagate(False)
        self.index_frame.config(width=self.INDEX_FRAME_MIN_WIDTH)  # Set a minimum width for `index_tree` container
    
        self.tree_frame.grid_propagate(False)
        self.tree_frame.config(width=self.TREE_FRAME_MIN_WIDTH)  # Set a wider minimum width for `tree` container
    
        # Original scrollbar setup without modifications
        self.scrollbar_y = ttk.Scrollbar(self.data_table_frame, orient="vertical", command=self.sync_scroll_y)
        self.scrollbar_y.grid(row=1, column=3, sticky="ns")  # Adjust position as necessary
    
        self.scrollbar_x = ttk.Scrollbar(self.data_table_frame, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.grid(row=2, column=1, columnspan=2, sticky="ew")  # Covers both frames horizontally
    
        # Configure scroll commands for the existing scroll setup
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)
        self.tree.configure(yscrollcommand=lambda *args: self.update_scrollbar_y(*args))
        self.index_tree.configure(yscrollcommand=lambda *args: self.update_scrollbar_y(*args))
    
        # Grid configuration for expansion behavior
        self.data_table_frame.grid_rowconfigure(1, weight=1)
        self.data_table_frame.grid_columnconfigure(1, weight=1)  # Less priority for `index_frame`
        self.data_table_frame.grid_columnconfigure(2, weight=3)  # More priority for `tree_frame`
    
        # Configure expansion within index_frame and tree_frame
        self.index_frame.grid_rowconfigure(0, weight=1)
        self.index_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
    
        # Lower control frame with pagination controls
        self.control_frame_lower = ttk.Frame(self.data_table_frame)
        self.control_frame_lower.grid(row=3, column=1, columnspan=6, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.row_limit_label = ttk.Label(self.control_frame_lower, text="Satır limiti:")
        self.row_limit_label.grid(row=0, column=0, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.row_limit_combo = ttk.Combobox(self.control_frame_lower, values=[10, 50, 100], state="readonly", width=5)
        self.row_limit_combo.grid(row=0, column=1, padx=self.PADX, pady=self.PADY, sticky="w")
        self.row_limit_combo.set(100)
        self.row_limit_combo.bind("<<ComboboxSelected>>", self.update_row_limit)
    
        self.prev_button = ttk.Button(self.control_frame_lower, text="Önceki", command=self.prev_page, width=self.BUTTON_WIDTH)
        self.prev_button.grid(row=0, column=2, padx=self.PADX, pady=self.PADY, sticky="w")
    
        self.next_button = ttk.Button(self.control_frame_lower, text="Sonraki", command=self.next_page, width=self.BUTTON_WIDTH)
        self.next_button.grid(row=0, column=3, padx=self.PADX, pady=self.PADY, sticky="w")
    
        # Lower right control frame with save button
        self.control_frame_lowerright = ttk.Frame(self.data_table_frame)
        self.control_frame_lowerright.grid(row=3, column=7, padx=self.PADX, pady=self.PADY, sticky="e")
    
        self.save_button = ttk.Button(self.control_frame_lowerright, text="Kaydet", command=self.save_dataframe, width=self.BUTTON_WIDTH)
        self.save_button.grid(row=0, column=0, padx=self.PADX, pady=self.PADY, sticky="e")

    def get_column_names(self):
        """Get column names from the currently selected DataFrame."""
        if self.current_df is not None:
            return list(self.current_df.columns)
        else:
            return []

    def open_column_selection_window(self):
        """Open a new window with checkboxes for selecting columns, with Reset, All, and Confirm buttons."""
        column_names = self.get_column_names()
        if not column_names:
            tk.messagebox.showwarning("Veri yok", "Lütfen önce bir veri tablosu seçiniz.")
            return
    
        # Create the new Toplevel window for column selection
        self.column_window = tk.Toplevel(self.root)
        self.column_window.title("Sütun seç")
        self.column_window.geometry("+{}+{}".format(self.root.winfo_x() + 150, self.root.winfo_y() + 100))
    
        max_columns_per_row = 5
        self.column_check_vars_temp = {}
    
        # Create checkboxes for each column
        for i, col in enumerate(column_names):
            var = tk.BooleanVar(value=self.column_check_vars.get(col).get() if col in self.column_check_vars else True)
            self.column_check_vars_temp[col] = var
            checkbox = tk.Checkbutton(self.column_window, text=col, variable=var)
            checkbox.grid(row=i // max_columns_per_row, column=i % max_columns_per_row, sticky="w", padx=self.PADX, pady=self.PADY)
    
        # "All" button
        all_button = ttk.Button(self.column_window, text="Tümü", command=self.toggle_all_columns)
        all_button.grid(row=(i // max_columns_per_row) + 1, column=0, pady=self.PADY, sticky="ew")
    
        # "Reset" button
        reset_button = ttk.Button(self.column_window, text="Sıfırla", command=self.reset_column_selection)
        reset_button.grid(row=(i // max_columns_per_row) + 1, column=1, pady=self.PADY, sticky="ew")
    
        # "Confirm" button
        confirm_button = ttk.Button(self.column_window, text="Onayla", command=self.confirm_column_selection)
        confirm_button.grid(row=(i // max_columns_per_row) + 1, column=2, pady=self.PADY, sticky="ew")
    
        # Window settings
        self.column_window.transient(self.root)
        self.column_window.grab_set()
        self.column_window.protocol("WM_DELETE_WINDOW", self.on_column_window_close)

    def toggle_all_columns(self):
        """Toggle all checkboxes between checked and unchecked."""
        all_checked = all(
            var.get() for var 
            in self.column_check_vars_temp.values()
        )
        for var in self.column_check_vars_temp.values():
            var.set(not all_checked)

    def reset_column_selection(self):
        """Reset checkboxes to the default state (all checked)."""
        for var in self.column_check_vars_temp.values():
            var.set(True)

    def confirm_column_selection(self):
        """Confirm column selections and close the column window."""
        self.column_check_vars = self.column_check_vars_temp.copy()
        self.column_window.destroy()

    def on_column_window_close(self):
        """Handle closing the column window without confirmation."""
        self.column_window.destroy()
    
    def load_and_populate(self):
        """Call both load_dataframe and populate_combo_boxes, and reset Province, County, and Town selections."""
        self.reset_selections()
        self.load_dataframe()
        self.populate_combo_boxes()
    
    def populate_combo_boxes(self):
        """Populate the combo boxes using MultiIndex levels."""
        df = self.current_df
        province_values = sorted(df.index
                                 .get_level_values(0)
                                 .unique())
        self.province_combo['values'] = province_values
        self.county_combo['values'] = []
        self.town_combo['values'] = []
    
    def update_county_combo(self, event):
        """Update County combo box based on selected Province and reset Town combo."""
        selected_province = self.province_combo.get()
        df = self.current_df
        self.county_combo.set('')
        self.town_combo.set('')
        self.town_combo['values'] = []
        if selected_province:
            county_values = sorted(
                df[df.index.get_level_values(0) == selected_province]
                .index.get_level_values(1).unique())
            self.county_combo['values'] = ['tümü'] + county_values
        else:
            self.county_combo['values'] = []
    
    def update_town_combo(self, event):
        """Update Town combo box based on selected County and Province."""
        selected_province = self.province_combo.get()
        selected_county = self.county_combo.get()
        df = self.current_df
        self.town_combo.set('')
        if selected_county == 'tümü':
            self.town_combo['values'] = ['tümü']
        elif (
            selected_province 
            and selected_county
        ):
            town_values = sorted(df[(df.index.get_level_values(0) == selected_province) &
                                    (df.index.get_level_values(1) == selected_county)]
                                 .index.get_level_values(2).unique())
            self.town_combo['values'] = ['tümü'] + town_values
        else:
            self.town_combo['values'] = []

    def reset_selections(self):
        """Reset the Province, County, and Town dropdown menus."""
        self.province_combo.set('')
        self.county_combo.set('')
        self.town_combo.set('')
        self.county_combo['values'] = []
        self.town_combo['values'] = []

    def query_df_columns(self):
        """Apply column filter based on the checked checkboxes."""
        selected_columns = [col for col, var 
                            in self.column_check_vars.items() 
                            if var.get()]
        if not selected_columns:
            tk.messagebox.showwarning(
                "Sütun seçilmedi", 
                "Lütfen en az bir sütun seçimi yapınız."
            )
            return
        df = self.unfiltered_df.copy()
        if 'Province' not in df.columns:
            df = df.reset_index(
                names=[
                    'Province', 
                    'County', 
                    'Town'], 
                drop=False)
        df = self.apply_row_filter(df)
        try:
            df = df[selected_columns + ['Province', 'County', 'Town']]
        except KeyError:
            pass
        self.filtered_df = df
        self.display_filtered_dataframe(self.filtered_df)
    
    def apply_row_filter(self, df):
        """Applies row filters based on Province, County, and Town selections."""
        selected_province = self.province_combo.get()
        selected_county = self.county_combo.get()
        selected_town = self.town_combo.get()
        if selected_province:
            df = df[df['Province'] == selected_province]
        if (selected_county 
            and selected_county != 'tümü'
           ):
            df = df[df['County'] == selected_county]
        if (selected_town 
            and selected_town != 'tümü'
           ):
            df = df[df['Town'] == selected_town]
        return df

    def apply_column_filter_to_df(self, df):
        """Applies column filters based on the selected checkboxes."""
        selected_columns = [col for col, var 
                            in self.column_check_vars.items() 
                            if var.get()]
        if selected_columns:
            try:
                df = df[selected_columns + ['Province', 'County', 'Town']]
            except KeyError:
                pass
        return df

    def query_df_rows(self):
        """Query the DataFrame based on combo box selections and apply pagination."""
        df = self.unfiltered_df.copy()
        if 'Province' not in df.columns:
            df = df.reset_index(
                names=[
                    'Province', 
                    'County', 
                    'Town'], 
                drop=False)
        df = self.apply_row_filter(df)
        
        if isinstance(df, pd.Series):
            df = df.to_frame().T
    
        if self.column_check_vars:
            df = self.apply_column_filter_to_df(df)
    
        # Update the filtered DataFrame
        self.filtered_df = df
    
        # Reset the page number to the first page and update total pages
        self.page_number = 1
        self.update_total_pages()
    
        # Display the DataFrame with pagination
        self.display_dataframe()

    def update_treeviews(self, df, index_columns, data_columns):
        """Helper method to update treeviews with data, replacing '0' values with an empty string."""
        self.index_tree['columns'] = index_columns
        for column in index_columns:
            self.index_tree.heading(column, text=column, anchor="center")
            self.index_tree.column(column, anchor="center", width=50, minwidth=50, stretch=True)
    
        self.tree['columns'] = data_columns
        for column in data_columns:
            self.tree.heading(column, text=column, anchor="center")
            self.tree.column(column, anchor="center", width=50, minwidth=50, stretch=False)
    
        # Iterate over each row and insert data into the Treeview
        for _, row in df.iterrows():
            # Replace '0' values with an empty string in both index and data columns
            index_values = ["" if value == 0 else value for value in row[index_columns].tolist()]
            data_values = ["" if value == 0 else value for value in row[data_columns].tolist()]
    
            self.index_tree.insert("", "end", values=index_values)
            self.tree.insert("", "end", values=data_values)
    
    def display_filtered_dataframe(self, df):
        """Display the filtered DataFrame in the Treeview."""
        self.tree.delete(*self.tree.get_children())
        self.index_tree.delete(*self.index_tree.get_children())
        if df.empty:
            return
        if (
            'Province' not in df.columns 
            or 'County' not in df.columns 
            or 'Town' not in df.columns
        ):
            df = df.reset_index(
                names=[
                    'Province', 
                    'County', 
                    'Town'], 
                drop=False)
        index_columns = ['Province', 'County', 'Town']
        data_columns = [col for col 
                        in df.columns 
                        if col not in index_columns]
        self.update_treeviews(
            df, 
            index_columns, 
            data_columns
        )
    
    def update_scrollbar_y(self, *args):
        """Update the vertical scrollbar position for both Treeviews."""
        self.scrollbar_y.set(*args)
        self.sync_scroll_y(
            'moveto', 
            args[0]
        )

    def sync_scroll_y(self, *args):
        """Synchronize the vertical scrolling of both Treeviews."""
        self.tree.yview(*args)
        self.index_tree.yview(*args)

    def load_dataframe(self):
        """Load the selected DataFrame and store it in unfiltered_df and current_df."""
        selected_year = self.year_combo.get()
        selected_type = self.type_combo.get()
        if (selected_year in self.datatable_df_dict 
            and selected_type in self.datatable_df_dict[selected_year]
           ):
            self.current_df = self.datatable_df_dict[selected_year][selected_type]
            self.unfiltered_df = self.current_df.copy()
            self.filtered_df = None
            self.page_number = 1
            self.update_total_pages()
            self.display_dataframe()
            self.populate_combo_boxes()

    def display_dataframe(self):
        """Display a portion of the DataFrame based on the selected page and row limit."""
        df = (
            self.filtered_df 
            if self.filtered_df is not None 
            else self.unfiltered_df)
        
        if 'Province' not in df.columns:
            df = df.reset_index(
                names=['Province', 
                       'County', 
                       'Town'], 
                drop=False)
    
        start_row = (self.page_number - 1) * self.row_limit
        end_row = start_row + self.row_limit
        
        if start_row >= len(df):
            tk.messagebox.showinfo(
                "Veri yok", 
                "Gösterilecek satır bulunamadı."
            )
            return
    
        self.tree.delete(*self.tree.get_children())
        self.index_tree.delete(*self.index_tree.get_children())
    
        visible_dataframe = df.iloc[start_row:end_row]
        index_columns = ['Province', 'County', 'Town']
        data_columns = [col for col in df.columns 
                        if col not in index_columns]
        self.update_treeviews(
            visible_dataframe, 
            index_columns, 
            data_columns
        )
        self.root.update_idletasks()

    def update_row_limit(self, event):
        """Update the row limit based on user selection and refresh the DataFrame display."""
        self.row_limit = int(self.row_limit_combo.get())
        self.update_total_pages()
        self.page_number = 1
        self.display_dataframe()

    def update_total_pages(self):
        """Update the total number of pages based on the DataFrame size and row limit."""
        if self.current_df is not None:
            self.total_pages = (len(self.current_df) + self.row_limit - 1) // self.row_limit

    def next_page(self):
        """Navigate to the next page, showing a message if no more rows are available."""
        start_row = (self.page_number * self.row_limit)
        df = (
            self.filtered_df 
            if self.filtered_df is not None 
            else self.unfiltered_df)
        if start_row >= len(df):
            tk.messagebox.showinfo(
                "Veri Yok", 
                "Bulunduğunuz sayfa, son veri sayfasıdır."
            )
        else:
            self.page_number += 1
            self.display_dataframe()

    def prev_page(self):
        """Navigate to the previous page, showing a message if no previous rows are available."""
        if self.page_number > 1:
            self.page_number -= 1
            self.display_dataframe()
        else:
            tk.messagebox.showinfo(
                "Veri Yok", 
                "Bulunduğunuz sayfa, ilk veri sayfasıdır."
            )

    def save_dataframe(self):
        """Save the current DataFrame to an Excel file with the index columns placed first."""
        df = (
            self.filtered_df 
            if self.filtered_df is not None 
            else self.unfiltered_df)
        if 'Province' not in df.columns:
            df = df.reset_index(
                names=['Province', 
                       'County', 
                       'Town'], 
                drop=False
            )
        index_columns = ['Province', 'County', 'Town']
        other_columns = [col for col in df.columns 
                         if col not in index_columns]
        df = df[index_columns + other_columns]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            try:
                df.to_excel(
                    file_path, 
                    index=False
                )
                tk.messagebox.showinfo(
                    "Başarılı", 
                    f"Veri, {file_path} konumuna başarıyla kaydedildi."
                )
            except Exception as e:
                tk.messagebox.showerror(
                    "Hata", 
                    f"Failed to save the file: {e}"
                )
    
    def update_data_screen_count(self):
        """Update the number of data screens based on user selections."""
        if self.comparison_var.get():
            self.data_screen_count = 2
            if self.calculate_difference_var.get():
                self.data_screen_count = 3
        else:
            self.data_screen_count = 1
        self.create_data_text_areas(self.data_screen_count)
    
    def get_selections(self, widgets):
        """Store current selections as instance variables."""
        self.selected_year = widgets['selections']['year_combo'][1].get()
        self.selected_electiontype = widgets['selections']['electiontype_combo'][1].get()
        self.selected_level = widgets['selections']['level_combo'][1].get()
        self.analysis_type = widgets['selections']['analysis_combo'][1].get()
        
        if self.analysis_type == 'şehir':
            self.selected_level1 = (
                widgets['selections'].get('level1_combo', (None, None))[1].get() 
                if widgets['selections'].get('level1_combo') 
                else None
            )
            self.selected_level2 = (
                widgets['selections'].get('level2_combo', (None, None))[1].get() 
                if widgets['selections'].get('level2_combo') 
                else None
            )
            self.selected_level3 = (
                widgets['selections'].get('level3_combo', (None, None))[1].get() 
                if widgets['selections'].get('level3_combo') 
                else None
            )
            
        elif self.analysis_type == 'kategorik':
            self.selected_category = (
                widgets['selections'].get('category_combo', (None, None))[1].get() 
                if widgets['selections'].get('category_combo') 
                else None
            )
            self.selected_subcategory = (
                widgets['selections'].get('subcategory_combo', (None, None))[1].get() 
                if widgets['selections'].get('subcategory_combo') 
                else None
            )
            
        elif self.analysis_type == 'parti':
            self.selected_party = (
                widgets['selections'].get('party_combo', (None, None))[1].get() 
                if widgets['selections'].get('party_combo') 
                else None
            )
            self.selected_category = (
                widgets['selections'].get('category_combo', (None, None))[1].get() 
                if widgets['selections'].get('category_combo') 
                else None
            )
            
        elif self.analysis_type == 'ülke geneli':
            self.selected_countrywide_category = (
                widgets['selections'].get('countrywide_category_combo', (None, None))[1].get() 
                if widgets['selections'].get('countrywide_category_combo') 
                else None
            )
            
    def update_combo_boxes(self, event, widgets):
        """Unified method to update combo box options and reset dependent selections based on the selections."""
        self.get_selections(widgets)
        df = None
    
        # Try to retrieve the DataFrame based on selection, handling KeyErrors gracefully.
        try:
            if self.analysis_type != 'ülke geneli':
                df = (
                    self.df_dict_map[self.selected_year]
                                   [self.selected_electiontype]
                                   [self.selected_level]
                )
            else:
                df = (
                    self.countrywide_df_dict_map[self.selected_electiontype]
                                                [self.selected_level]
                )
        except KeyError:
            pass
    
        # Update election type combo box based on selected year
        if self.selected_year:
            election_types = list(
                self.df_dict_map[self.selected_year].keys()
            )
            electiontype_combo = widgets['selections']['electiontype_combo'][1]
            electiontype_combo['values'] = election_types
            if self.selected_electiontype not in election_types:
                electiontype_combo.set('')
                self.selected_electiontype = ''
    
        # Update level combo box based on selected election type
        if self.selected_electiontype:
            levels = list(
                self.df_dict_map[self.selected_year][self.selected_electiontype].keys()
            )
            level_combo = widgets['selections']['level_combo'][1]
            level_combo['values'] = levels
            if self.selected_level not in levels:
                level_combo.set('')
                self.selected_level = ''
    
        if df is not None:
            # Handle categorical analysis updates
            if self.analysis_type == "kategorik":
                category_options = [
                    x for x in groupby_list 
                    if groupby_remover[self.selected_level] not in x
                ]
                category_combo = widgets['selections']['category_combo'][1]
                category_combo['values'] = category_options
                if self.selected_category not in category_options:
                    category_combo.set('')
                    self.selected_category = None
    
                if self.selected_category:
                    subcategory_values = sorted(
                        df.groupby(self.selected_category)
                        .sum()
                        .index
                    )
                    subcategory_combo = widgets['selections']['subcategory_combo'][1]
                    subcategory_combo['values'] = [str(value) for value in subcategory_values]  # Convert values to strings
                    if str(self.selected_subcategory) not in [str(value) for value in subcategory_values]:
                        subcategory_combo.set('')
                        self.selected_subcategory = None
    
            # Handle city-level analysis updates
            elif self.analysis_type == "şehir":
                # Update level1 combo (Province)
                level1_values = sorted(
                    list(
                        set(
                            df.index
                            .get_level_values(0)
                        )
                    )
                )
                if len(level1_values) == 1 and level1_values[0] == '-':
                    level1_combo = widgets['selections']['level1_combo'][1]
                    level1_combo['values'] = level1_values
                    level1_combo.set('-')
                    self.selected_level1 = '-'
                else:
                    level1_combo = widgets['selections']['level1_combo'][1]
                    level1_combo['values'] = level1_values
                    if self.selected_level1 not in level1_values:
                        level1_combo.set('')
                        self.selected_level1 = None
                        # Reset dependent dropdowns
                        level2_combo = widgets['selections']['level2_combo'][1]
                        level2_combo.set('')
                        level2_combo['values'] = []
                        self.selected_level2 = None
    
                        level3_combo = widgets['selections']['level3_combo'][1]
                        level3_combo.set('')
                        level3_combo['values'] = []
                        self.selected_level3 = None
    
                # Update level2 combo (County)
                if self.selected_level1:
                    level2_values = sorted(
                        list(
                            set(
                                df.loc[self.selected_level1]
                                .index
                                .get_level_values(0)
                            )
                        )
                    )
                    if len(level2_values) == 1 and level2_values[0] == '-':
                        level2_combo = widgets['selections']['level2_combo'][1]
                        level2_combo['values'] = level2_values
                        level2_combo.set('-')
                        self.selected_level2 = '-'
                    else:
                        level2_combo = widgets['selections']['level2_combo'][1]
                        level2_combo['values'] = level2_values
                        if self.selected_level2 not in level2_values:
                            level2_combo.set('')
                            self.selected_level2 = None
                            # Reset town combo if county is reset
                            level3_combo = widgets['selections']['level3_combo'][1]
                            level3_combo.set('')
                            level3_combo['values'] = []
                            self.selected_level3 = None
    
                # Update level3 combo (Town)
                if self.selected_level1 and self.selected_level2:
                    level3_values = sorted(
                        list(
                            set(
                                df.loc[self.selected_level1, self.selected_level2]
                                .index
                                .get_level_values(0)
                            )
                        )
                    )
                    if len(level3_values) == 1 and level3_values[0] == '-':
                        level3_combo = widgets['selections']['level3_combo'][1]
                        level3_combo['values'] = level3_values
                        level3_combo.set('-')
                        self.selected_level3 = '-'
                    else:
                        level3_combo = widgets['selections']['level3_combo'][1]
                        level3_combo['values'] = level3_values
                        if self.selected_level3 not in level3_values:
                            level3_combo.set('')
                            self.selected_level3 = None
    
            # Handle party-level analysis updates
            elif self.analysis_type == "parti":
                category_options = [
                    x for x in groupby_list
                    if groupby_remover[self.selected_level] not in x
                ]
                category_combo = widgets['selections']['category_combo'][1]
                category_combo['values'] = category_options
                if self.selected_category not in category_options:
                    category_combo.set('')
                    self.selected_category = None
    
            # Handle countrywide analysis updates
            elif self.analysis_type == "ülke geneli":
                countrywide_category_values = list(
                    set([col[5:] for col in df.columns if 'ORANI' not in col])
                )
                countrywide_category_combo = widgets['selections']['countrywide_category_combo'][1]
                countrywide_category_combo['values'] = countrywide_category_values
                if self.selected_countrywide_category not in countrywide_category_values:
                    countrywide_category_combo.set('')
                    self.selected_countrywide_category = None
    
        # Final method call to validate and enable analysis type
        self.check_and_enable_analysis_type(widgets)

    def check_and_enable_analysis_type(self, widgets):
        """Enable 'Analiz tipi' combobox only when all other selections are made and reset if necessary."""
        if (widgets['selections']['year_combo'][1].get() 
            and widgets['selections']['electiontype_combo'][1].get() 
            and widgets['selections']['level_combo'][1].get()
           ):
            widgets['selections']['analysis_combo'][1].config(state="readonly")
        else:
            widgets['selections']['analysis_combo'][1].set('')
            widgets['selections']['analysis_combo'][1].config(state="disabled")
            self.clear_dynamic_widgets(widgets)
    
    def center_window(self, window, width, height):
        """Center a given window on the screen or relative to the root window."""
        main_window_x = self.root.winfo_x()
        main_window_y = self.root.winfo_y()
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()
        x = main_window_x + (main_window_width // 2) - (width // 2)
        y = main_window_y + (main_window_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    def convert_to_percentages(self):
        """Convert all values in data screens to their percentage values."""
        # Store the original data and total values before converting
        for index in self.data_storage.keys():
            if 'original_data' not in self.data_storage[index]:
                self.data_storage[index]['original_data'] = self.data_storage[index]['data']
                self.data_storage[index]['original_total_value'] = self.data_storage[index]['total_value']
    
            # Convert current data to percentages
            data = self.data_storage[index]['data']
            total_value = self.data_storage[index]['total_value']
    
            if index == 3 and len(self.data_storage) == 3:
                # Convert differences to percentage differences
                data1 = self.data_storage[1]['data']
                total_value1 = self.data_storage[1]['total_value']
                data2 = self.data_storage[2]['data']
                total_value2 = self.data_storage[2]['total_value']
    
                percentage_diff_data = {
                    key: ((data2.get(key, 0) / total_value2) * 100)
                        - ((data1.get(key, 0) / total_value1) * 100)
                    for key in set(data1) | set(data2)
                }
                self.display_data_in_text_area(percentage_diff_data, index - 1, is_percentage=True)
            else:
                percentage_data = {key: (value / total_value) * 100 for key, value in data.items()}
                self.display_data_in_text_area(percentage_data, index - 1, is_percentage=True)

                
    def toggle_comparison(self):
        """Toggle between single and comparison mode."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        frame_width = int(screen_width * 0.4)
        frame_height = int(screen_height * 0.3)
    
        for frame_widget in self.frames_widgets:
            frame_widget['frame'].grid_remove()
    
        if self.comparison_var.get():
            if len(self.frames_widgets) < 2:
                self.create_analysis_frame()
            for frame_widget in self.frames_widgets:
                frame_widget['frame'].config(
                    width=frame_width,
                    height=frame_height
                )
                frame_widget['frame'].grid_propagate(False)
            
            # Update data screen count and make sure the copy buttons are enabled
            self.update_data_screen_count()
            self.calculate_difference_checkbox.grid()
            self.calculate_difference_checkbox.config(state='normal')
            
            # New line added to enable copy buttons for both frames
            self.toggle_copy_buttons()
    
            if 1 in self.data_storage:
                data = self.data_storage[1]['data']
                total_value = self.data_storage[1]['total_value']
                self.display_data_in_text_area(
                    data,
                    0,
                    total_value
                )
        else:
            self.clear_comparison_frame()
            self.update_data_screen_count()
            self.calculate_difference_checkbox.grid_remove()
            self.calculate_difference_var.set(False)
    
        for frame_widget in self.frames_widgets:
            frame_widget['frame'].grid()
    
        if self.percentage_var.get():
            self.toggle_percentages()
        
        self.root.update_idletasks()
    
    def toggle_difference_screen(self):
        """Show or hide the third data screen based on calculate_difference checkbox."""
        for text_area in self.data_text_areas:
            text_area.master.grid_remove()
        self.update_data_screen_count()
        for index in range(1, 3):
            if index in self.data_storage:
                data = self.data_storage[index]['data']
                total_value = self.data_storage[index]['total_value']
                self.display_data_in_text_area(
                    data, 
                    index - 1, 
                    total_value
                )
        if self.calculate_difference_var.get():
            if len(self.data_storage) >= 2:
                dict_diff, total_diff = self.calculate_difference(
                    self.data_storage[2]['data'],
                    self.data_storage[1]['data'],
                    self.data_storage[2]['total_value'],
                    self.data_storage[1]['total_value'],
                )
                self.data_storage[3] = {
                    'data': dict_diff, 
                    'total_value': total_diff
                }
                self.display_data_in_text_area(
                    dict_diff, 
                    2, 
                    total_diff
                )
        if self.percentage_var.get():
            self.toggle_percentages()
        for text_area in self.data_text_areas:
            text_area.master.grid()
        self.root.update_idletasks()

    def toggle_percentages(self):
        """Toggle between percentage and absolute values in the data screens."""
        if self.percentage_var.get():  # If percentage mode is activated
            self.convert_to_percentages()
        else:  # If percentage mode is deactivated
            # Restore the original data and total values
            for index in self.data_storage.keys():
                if 'original_data' in self.data_storage[index]:
                    self.data_storage[index]['data'] = self.data_storage[index]['original_data']
                    self.data_storage[index]['total_value'] = self.data_storage[index]['original_total_value']
    
                    # Display the restored original data
                    self.display_data_in_text_area(
                        self.data_storage[index]['data'],
                        index - 1,
                        self.data_storage[index]['total_value']
                    )
    
            # Remove the 'original_data' and 'original_total_value' to avoid stale data
            for index in self.data_storage.keys():
                if 'original_data' in self.data_storage[index]:
                    del self.data_storage[index]['original_data']
                    del self.data_storage[index]['original_total_value']
            
    def create_data_text_areas(self, num_areas):
        """Create data text areas based on the number of areas (1, 2, or 3)."""
        if len(self.data_text_areas) != num_areas:
            # Remove existing text areas
            for text_area in self.data_text_areas:
                text_area.master.grid_remove()
            for widget in self.data_frame.winfo_children():
                if widget != self.checkbox_frame:
                    widget.destroy()
            self.data_text_areas.clear()
            
            # Create new text areas based on num_areas
            for i in range(num_areas):
                text_frame = tk.Frame(self.data_frame)
                text_frame.grid(row=i + 1, column=0, sticky="nsew", padx=self.PADX, pady=self.PADY)
                
                scrollbar = tk.Scrollbar(text_frame)
                scrollbar.grid(row=0, column=1, sticky="ns")
                
                text = tk.Text(
                    text_frame, 
                    wrap='word', 
                    yscrollcommand=scrollbar.set, 
                    state='disabled', 
                    width=self.TEXT_AREA_WIDTH  # Replaced hardcoded width
                )
                text.grid(row=0, column=0, sticky="nsew")
                scrollbar.config(command=text.yview)
                
                # Configure frame grid to be responsive
                text_frame.grid_rowconfigure(0, weight=1)
                text_frame.grid_columnconfigure(0, weight=1)
                
                self.data_text_areas.append(text)
            
            # Configure data_frame grid rows to adjust based on number of areas
            self.data_frame.grid_rowconfigure(0, weight=0)
            for i in range(num_areas):
                self.data_frame.grid_rowconfigure(i + 1, weight=1)
            
            # Display updated text areas
            for text_area in self.data_text_areas:
                text_area.master.grid()
        self.root.update_idletasks()

    def create_analysis_frame(self):
        """Create a new frame for analysis input, handling both single and comparison cases."""
        # Use predefined width and height for the analysis frame
        frame = tk.Frame(
            self.analysis_container_frame, 
            width=self.ANALYSIS_FRAME_WIDTH, 
            height=self.ANALYSIS_FRAME_HEIGHT
        )
        column_index = len(self.frames_widgets)
        frame.grid(row=0, column=column_index, sticky="nsew", padx=self.PADX, pady=self.PADY)
        frame.grid_propagate(False)
    
        # Configure column and row weights to make the frame responsive
        self.analysis_container_frame.grid_columnconfigure(column_index, weight=1)
        self.analysis_container_frame.grid_rowconfigure(0, weight=1)
    
        widgets = {'frame': frame, 'canvas': None}
        self.frames_widgets.append(widgets)
    
        # Input frame inside the analysis frame
        input_frame = tk.Frame(frame)
        input_frame.grid(row=0, column=0, sticky="nw")
        self.create_initial_input_menu(input_frame, widgets)
    
        # Canvas frame for displaying analysis results
        canvas_frame = tk.Frame(frame)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        widgets['canvas_frame'] = canvas_frame

        # Bind the comparison checkbox to enable/disable the Copy Across button
        self.comparison_var.trace_add('write', lambda *args: self.toggle_copy_buttons())

    def copy_across(self, source_widgets):
        """Copy dropdown selections from the source frame to the other frame."""
        # Identify the target frame (the opposite of the source)
        target_widgets = None
        for widgets in self.frames_widgets:
            if widgets != source_widgets:
                target_widgets = widgets
                break
        
        if target_widgets is None:
            return
        
        # Copy values from source to target for main selections
        for key, (label, source_combo) in source_widgets['selections'].items():
            if key in target_widgets['selections']:
                _, target_combo = target_widgets['selections'][key]
                target_combo.set(source_combo.get())
                # If the combo box is 'analysis_combo', enable it if necessary
                if key == 'analysis_combo' and not target_combo['state'] == 'readonly':
                    target_combo.config(state='readonly')
        
        # Ensure required selections are set before initializing subcategories
        if (target_widgets['selections']['year_combo'][1].get() and
            target_widgets['selections']['electiontype_combo'][1].get() and
            target_widgets['selections']['level_combo'][1].get()):
            # Initialize subcategories in the target frame after copying values
            self.display_category_selectors(None, target_widgets)
        
        # Copy values for subcategories if they exist
        for key in ['category_combo', 'subcategory_combo', 'level1_combo', 'level2_combo', 'level3_combo', 'party_combo', 'countrywide_category_combo']:
            if key in source_widgets['selections'] and key in target_widgets['selections']:
                _, source_combo = source_widgets['selections'][key]
                _, target_combo = target_widgets['selections'][key]
                target_combo.set(source_combo.get())
        
        # Update dependent combo boxes after copying values
        self.update_combo_boxes(None, target_widgets)

    def fill_random(self, widgets):
        """Fill all dropdown menus in the given analysis frame with random values."""
        def set_random_value(combo_box):
            if combo_box['values']:
                combo_box.set(random.choice(combo_box['values']))
        
        # Set random values for the main selections in order
        set_random_value(widgets['selections']['year_combo'][1])
        self.update_combo_boxes(None, widgets)
        set_random_value(widgets['selections']['electiontype_combo'][1])
        self.update_combo_boxes(None, widgets)
        set_random_value(widgets['selections']['level_combo'][1])
        self.update_combo_boxes(None, widgets)
        set_random_value(widgets['selections']['analysis_combo'][1])
        self.display_category_selectors(None, widgets)
        self.update_combo_boxes(None, widgets)

        # If there are more dropdowns available (dependent on analysis type), set their values
        for key in ['category_combo', 'subcategory_combo', 'level1_combo', 'level2_combo', 'level3_combo', 'party_combo', 'countrywide_category_combo']:
            if key in widgets['selections']:
                set_random_value(widgets['selections'][key][1])
                self.update_combo_boxes(None, widgets)

    def toggle_copy_buttons(self):
        """Enable or disable the Copy Across buttons based on the comparison checkbox."""
        state = "normal" if self.comparison_var.get() else "disabled"
        for widgets in self.frames_widgets:
            if 'copy_button' in widgets:
                widgets['copy_button'].config(state=state)

    def clear_comparison_frame(self):
        """Clear the second analysis frame (if it exists)."""
        if len(self.frames_widgets) > 1:
            frame_to_remove = self.frames_widgets.pop()
            frame_to_remove['frame'].grid_remove()
            frame_to_remove['frame'].destroy()
        self.root.update_idletasks()
            
    def clear_dynamic_widgets(self, widgets):
        """Clear any dynamic widgets (dropdowns) before creating new ones."""
        dynamic_keys = [
            'category_combo', 
            'subcategory_combo', 
            'level1_combo', 
            'level2_combo', 
            'level3_combo', 
            'party_combo', 
            'countrywide_category_combo'
        ]
        for key in dynamic_keys:
            if (key in widgets['selections'] 
                and widgets['selections'][key] is not None
               ):
                label, combobox = widgets['selections'][key]
                if label is not None:
                    label.destroy()
                if combobox is not None:
                    combobox.destroy()
                del widgets['selections'][key]
                
    def create_initial_input_menu(self, parent_frame, widgets):
        """Create dropdown menus and buttons for selecting data inside the provided parent frame."""
        widgets['selections'] = {}
    
        # Year Selection
        year_label = ttk.Label(parent_frame, text='Seçim yılı:')
        year_label.grid(row=0, column=0, sticky="w")
        
        year_combo = ttk.Combobox(parent_frame, values=list(self.df_dict_map.keys()), state="readonly", width=self.COMBOBOX_WIDTH)
        year_combo.grid(row=0, column=1, sticky="ew")
        year_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
        widgets['selections']['year_combo'] = (year_label, year_combo)
    
        # Election Type Selection
        electiontype_label = ttk.Label(parent_frame, text='Seçim türü:')
        electiontype_label.grid(row=1, column=0, sticky="w")
        
        electiontype_combo = ttk.Combobox(parent_frame, state="readonly", width=self.COMBOBOX_WIDTH)
        electiontype_combo.grid(row=1, column=1, sticky="ew")
        electiontype_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
        widgets['selections']['electiontype_combo'] = (electiontype_label, electiontype_combo)
    
        # Level Selection
        level_label = ttk.Label(parent_frame, text='Seçim seviyesi:')
        level_label.grid(row=2, column=0, sticky="w")
        
        level_combo = ttk.Combobox(parent_frame, state="readonly", width=self.COMBOBOX_WIDTH)
        level_combo.grid(row=2, column=1, sticky="ew")
        level_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
        widgets['selections']['level_combo'] = (level_label, level_combo)
    
        # Analysis Type Selection
        analysis_label = ttk.Label(parent_frame, text='Analiz tipi:')
        analysis_label.grid(row=3, column=0, sticky="w")
        
        analysis_combo = ttk.Combobox(parent_frame, values=["kategorik", "şehir", "parti", "ülke geneli"], state="disabled", width=self.COMBOBOX_WIDTH)
        analysis_combo.grid(row=3, column=1, sticky="ew")
        analysis_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.display_category_selectors(event, w))
        widgets['selections']['analysis_combo'] = (analysis_label, analysis_combo)
    
        # Threshold Entry
        threshold_label = ttk.Label(parent_frame, text='Baraj:')
        threshold_label.grid(row=4, column=0, sticky="w")
        
        threshold_entry = ttk.Entry(parent_frame, width=self.COMBOBOX_WIDTH)
        threshold_entry.insert(0, 1)
        threshold_entry.grid(row=4, column=1, sticky="ew")
        widgets['threshold_entry'] = threshold_entry
    
        # Help Buttons
        help_button_year = ttk.Button(parent_frame, text='?', width=self.HELP_BUTTON_WIDTH, command=lambda: self.show_tooltip('year_combo'))
        help_button_year.grid(row=0, column=2, sticky="w", padx=self.PADX)
    
        help_button_electiontype = ttk.Button(parent_frame, text='?', width=self.HELP_BUTTON_WIDTH, command=lambda: self.show_tooltip('electiontype_combo'))
        help_button_electiontype.grid(row=1, column=2, sticky="w", padx=self.PADX)
    
        help_button_level = ttk.Button(parent_frame, text='?', width=self.HELP_BUTTON_WIDTH, command=lambda: self.show_tooltip('level_combo'))
        help_button_level.grid(row=2, column=2, sticky="w", padx=self.PADX)
    
        help_button_analysis = ttk.Button(parent_frame, text='?', width=self.HELP_BUTTON_WIDTH, command=lambda: self.show_tooltip('analysis_combo'))
        help_button_analysis.grid(row=3, column=2, sticky="w", padx=self.PADX)
    
        help_button_threshold = ttk.Button(parent_frame, text='?', width=self.HELP_BUTTON_WIDTH, command=lambda: self.show_tooltip('threshold_entry'))
        help_button_threshold.grid(row=4, column=2, sticky="w", padx=self.PADX)

        # Copy Across Button
        copy_button = ttk.Button(parent_frame, text="Karşıya kopyala", command=lambda w=widgets: self.copy_across(w))
        copy_button.grid(row=3, column=3, sticky="ew", padx=self.PADX)
        copy_button.config(state="disabled")  # Initially disabled
        widgets['copy_button'] = copy_button  # Store reference to the button for later updates

        # Random Button
        random_button = ttk.Button(parent_frame, text="Rastgele", command=lambda w=widgets: self.fill_random(w))
        random_button.grid(row=4, column=3, sticky="ew", padx=self.PADX)

        # Plot and Save Buttons
        plot_button = ttk.Button(parent_frame, text='Grafik oluştur', command=lambda w=widgets, idx=self.frames_widgets.index(widgets): self.generate_pie_chart(w, idx))
        plot_button.grid(row=5, column=0, columnspan=2, sticky="ew")
    
        save_button = ttk.Button(parent_frame, text="Grafiği kaydet", command=lambda idx=self.frames_widgets.index(widgets): self.save_image(idx))
        save_button.grid(row=5, column=2, sticky="ew", padx=self.PADX)
    
        # Configure grid layout
        parent_frame.grid_columnconfigure(0, weight=0)
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_columnconfigure(2, weight=0)
        parent_frame.grid_columnconfigure(3, weight=1)

    def show_tooltip(self, widget_key):
        """Show tooltip message in a custom Toplevel window for the specified widget."""
        if widget_key in tooltip_texts:
            tooltip_window = tk.Toplevel(self.root)
            tooltip_window.title("Açıklama")
    
            self.center_window(tooltip_window, width=self.TOOLTIP_WIDTH, height=self.TOOLTIP_HEIGHT)
            
            tooltip_window.resizable(False, False)
    
            # Tooltip text area
            tooltip_text = tk.Text(
                tooltip_window, 
                wrap="word", 
                width=self.TOOLTIP_WIDTH,
                height=self.TOOLTIP_HEIGHT
            )
            tooltip_text.grid(row=0, column=0, columnspan=2, padx=self.PADX, pady=self.PADY, sticky="nsew")
            tooltip_text.tag_configure('default_font', font=('TkDefaultFont', 10))
    
            # Insert tooltip text content
            text_content = tooltip_texts[widget_key]
            tooltip_text.insert(tk.END, text_content, 'default_font')
            tooltip_text.config(state='disabled')
            
            # Add hyperlink if the widget key is 'analysis_combo'
            if widget_key == 'analysis_combo':
                url = "https://www.sanayi.gov.tr/merkez-birimi/b94224510b7b/sege"
                tooltip_text.tag_config("url", foreground="blue", underline=True)
                tooltip_text.tag_bind("url", "<Button-1>", lambda e: webbrowser.open(url))
                start_pos = tooltip_text.search(url, "1.0", stopindex=tk.END)
                if start_pos:
                    end_pos = f"{start_pos}+{len(url)}c"
                    tooltip_text.tag_add("url", start_pos, end_pos)
    
            # OK button
            ok_button = tk.Button(tooltip_window, text="OK", command=tooltip_window.destroy)
            ok_button.grid(row=1, column=0, columnspan=2, pady=self.PADY, padx=self.PADX, sticky="ew")
    
            # Configure grid layout for expandability
            tooltip_window.grid_rowconfigure(0, weight=1)
            tooltip_window.grid_columnconfigure(0, weight=1)
    
            # Set modal behavior for the tooltip window
            tooltip_window.transient(self.root)
            tooltip_window.grab_set()
            tooltip_window.focus_set()
        
    def display_category_selectors(self, event, widgets):
        """Display appropriate dropdowns based on the analysis type inside the provided frame."""
        input_frame = widgets['frame'].winfo_children()[0]
        input_frame.grid_remove()
        self.get_selections(widgets)
        self.clear_dynamic_widgets(widgets)
    
        if self.analysis_type != 'ülke geneli':
            df = (self.df_dict_map[self.selected_year][self.selected_electiontype][self.selected_level])
            valid_parties = [p for p in party_list if p in df.columns]
        else:
            df = (self.countrywide_df_dict_map[self.selected_electiontype][self.selected_level])
            valid_parties = [p for p in party_list if p in df.index]
    
        if self.analysis_type == "kategorik":
            category_label = ttk.Label(input_frame, text='Kategori Seçiniz:')
            category_label.grid(row=6, column=0, sticky="e")
            
            category_combo = ttk.Combobox(input_frame, values=[x for x in groupby_list if groupby_remover[self.selected_level] not in x], state="readonly", width=self.COMBOBOX_WIDTH)
            category_combo.grid(row=6, column=1, sticky="ew")
            category_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['category_combo'] = (category_label, category_combo)
            
            subcategory_label = ttk.Label(input_frame, text='Alt Kategori Seçiniz:')
            subcategory_label.grid(row=6, column=2, sticky="e", padx=self.PADX)
            
            subcategory_combo = ttk.Combobox(input_frame, state="readonly", width=self.COMBOBOX_WIDTH)
            subcategory_combo.grid(row=6, column=3, sticky="ew")
            widgets['selections']['subcategory_combo'] = (subcategory_label, subcategory_combo)
    
        elif self.analysis_type == "şehir":
            level1_label = ttk.Label(input_frame, text='İl:')
            level1_label.grid(row=6, column=0, sticky="e")
            
            level1_combo = ttk.Combobox(input_frame, values=sorted(list(set(df.index.get_level_values(0)))), state="readonly", width=self.COMBOBOX_WIDTH)
            level1_combo.grid(row=6, column=1, sticky="ew")
            level1_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['level1_combo'] = (level1_label, level1_combo)
    
            level2_label = ttk.Label(input_frame, text='İlçe:')
            level2_label.grid(row=6, column=2, sticky="e", padx=self.PADX)
            
            level2_combo = ttk.Combobox(input_frame, state="readonly", width=self.COMBOBOX_WIDTH)
            level2_combo.grid(row=6, column=3, sticky="ew")
            level2_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['level2_combo'] = (level2_label, level2_combo)
    
            level3_label = ttk.Label(input_frame, text='Belde:')
            level3_label.grid(row=6, column=4, sticky="e", padx=self.PADX)
            
            level3_combo = ttk.Combobox(input_frame, state="readonly", width=self.COMBOBOX_WIDTH)
            level3_combo.grid(row=6, column=5, sticky="ew")
            level3_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['level3_combo'] = (level3_label, level3_combo)
    
        elif self.analysis_type == "parti":
            category_label = ttk.Label(input_frame, text='Kategori Seçiniz:')
            category_label.grid(row=6, column=0, sticky="e")
            
            category_combo = ttk.Combobox(input_frame, values=[x for x in groupby_list if groupby_remover[self.selected_level] not in x], state="readonly", width=self.COMBOBOX_WIDTH)
            category_combo.grid(row=6, column=1, sticky="ew")
            widgets['selections']['category_combo'] = (category_label, category_combo)
            
            party_label = ttk.Label(input_frame, text='Parti seçiniz:')
            party_label.grid(row=6, column=2, sticky="e")
            
            party_combo = ttk.Combobox(input_frame, values=sorted(valid_parties), state="readonly", width=self.COMBOBOX_WIDTH)
            party_combo.grid(row=6, column=3, sticky="ew")
            party_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['party_combo'] = (party_label, party_combo)
    
        elif self.analysis_type == "ülke geneli":
            countrywide_category_label = ttk.Label(input_frame, text='Kategori Seçiniz:')
            countrywide_category_label.grid(row=6, column=0, sticky="e")
            
            countrywide_category_combo = ttk.Combobox(input_frame, values=list(set([col[5:] for col in df.columns if 'ORANI' not in col])), state="readonly", width=self.COMBOBOX_WIDTH)
            countrywide_category_combo.grid(row=6, column=1, sticky="ew")
            countrywide_category_combo.bind("<<ComboboxSelected>>", lambda event, w=widgets: self.update_combo_boxes(event, w))
            widgets['selections']['countrywide_category_combo'] = (countrywide_category_label, countrywide_category_combo)
    
        input_frame.grid()
        self.root.update_idletasks()
        
    def get_selected_dataframe(self, widgets):
        """Fetch the selected DataFrame based on the widget selections."""
        self.get_selections(widgets)
        df = None
        total_value = None
    
        # City-level analysis ('şehir')
        if self.analysis_type == 'şehir':
            if self.selected_level1 and self.selected_level2 and self.selected_level3:
                df = (
                    self.df_dict_map[self.selected_year]
                                   [self.selected_electiontype]
                                   [self.selected_level]
                )
                total_value = df.loc[
                    (self.selected_level1, self.selected_level2, self.selected_level3),
                    'gecerli oy toplami'
                ]
                return (
                    df.loc[self.selected_level1, self.selected_level2, self.selected_level3]
                    .filter(items=party_list), 
                    total_value
                )
    
        # Categorical analysis ('kategorik')
        elif self.analysis_type == 'kategorik':
            if self.selected_category and self.selected_subcategory:
                df = (
                    self.df_dict_map[self.selected_year][self.selected_electiontype]
                    [self.selected_level].groupby(self.selected_category).sum()
                )
                if self.selected_category == 'bolge':
                    total_value = df.loc[self.selected_subcategory, 'gecerli oy toplami']
                    return df.filter(items=party_list).loc[self.selected_subcategory], total_value
                else:
                    total_value = df.loc[float(self.selected_subcategory), 'gecerli oy toplami']
                    return (
                        df.filter(items=party_list)
                          .loc[float(self.selected_subcategory)], 
                        total_value
                    )
    
        # Party-level analysis ('parti')
        elif self.analysis_type == 'parti':
            if self.selected_party and self.selected_category:
                df = (
                    self.df_dict_map[self.selected_year][self.selected_electiontype]
                    [self.selected_level].groupby(self.selected_category).sum()[self.selected_party]
                )
                total_value = df.sum()
                return df, total_value
    
        # Countrywide analysis ('ülke geneli')
        elif self.analysis_type == 'ülke geneli':
            if self.selected_countrywide_category:
                columnpicker = f"{self.selected_year} {self.selected_countrywide_category}"
                df = (
                    self.countrywide_df_dict_map[self.selected_electiontype]
                    [self.selected_level][columnpicker]
                )
                total_value = df.sum()
                return df, total_value
    
        return None, None

    def process_data(self, widgets, frame_index):
        """Process data by storing it and calculating the difference if both sets are available."""
        df, total_value = self.get_selected_dataframe(widgets)
        if df is not None:
            # Store the current data and total value in data_storage
            self.data_storage[frame_index + 1] = {
                'data': df.to_dict(), 
                'total_value': total_value
            }
            # Display the current data in the respective text area
            self.display_data_in_text_area(
                self.data_storage[frame_index + 1]['data'], 
                frame_index, 
                self.data_storage[frame_index + 1]['total_value']
            )
            
            # If we have both datasets, calculate and display the difference
            if len(self.data_storage) >= 2 and self.data_screen_count == 3:
                dict_diff, total_diff = self.calculate_difference(
                    self.data_storage[2]['data'], 
                    self.data_storage[1]['data'], 
                    self.data_storage[2]['total_value'], 
                    self.data_storage[1]['total_value']
                )
                # Update data_storage with the new difference data
                self.data_storage[3] = {
                    'data': dict_diff, 
                    'total_value': total_diff
                }
                # Display the updated difference in the third text area
                if len(self.data_text_areas) > 2:
                    self.display_data_in_text_area(
                        dict_diff, 
                        2, 
                        total_diff
                    )

    def display_data_in_text_area(self, data, index, total_value=None, is_percentage=False):
        """Display data from a dictionary into the specified text area with formatted keys, sorted by values."""
        # Sort data by values in descending order
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    
        text_area = self.data_text_areas[index]
        text_area.config(state='normal')
        text_area.delete(1.0, tk.END)
        text_area.tag_configure('title', font=('TkDefaultFont', 12, 'bold', 'underline'))
        text_area.tag_configure('bold', font=('TkDefaultFont', 10, 'bold'))
        text_area.tag_configure('default_font', font=('TkDefaultFont', 10))
        text_area.tag_configure('positive', foreground='green', font=('TkDefaultFont', 10))
        text_area.tag_configure('negative', foreground='red', font=('TkDefaultFont', 10))
    
        text_area.insert(tk.END, f"{str(index + 1) + '.' if index < 2 else 'Karşılaştırmalı'} Ekran:\n", 'title')
    
        for key, value in sorted_data.items():
            if value != 0:
                if isinstance(key, str):
                    capitalized_key = key.capitalize()
                    text_area.insert(tk.END, f'{capitalized_key}: ', 'bold')
                elif isinstance(key, (float, int)):
                    text_area.insert(tk.END, f'{key}: ', 'bold')
    
                # Check if it's the difference screen (index == 2) and highlight accordingly
                if index == 2:
                    if is_percentage:
                        if value > 0:
                            text_area.insert(tk.END, f'{value:.1f}%\n', 'positive')
                        else:
                            text_area.insert(tk.END, f'{value:.1f}%\n', 'negative')
                    else:
                        if value > 0:
                            text_area.insert(tk.END, f'{value:,}\n', 'positive')
                        else:
                            text_area.insert(tk.END, f'{value:,}\n', 'negative')
                else:
                    if is_percentage:
                        text_area.insert(tk.END, f'{value:.1f}%\n', 'default_font')
                    else:
                        text_area.insert(tk.END, f'{value:,}\n', 'default_font')
    
        if total_value is not None and not is_percentage:
            text_area.insert(tk.END, f'Total: ', 'bold')
            if total_value > 0:
                text_area.insert(tk.END, f'{total_value:,}', 'positive')
            else:
                text_area.insert(tk.END, f'{total_value:,}', 'negative')
    
        text_area.config(state='disabled')

    def calculate_difference(self, dict1, dict2, total_value1, total_value2):
        """Calculate the difference between two one-level dictionaries with numeric values, including total_value."""
        diff_dict = {}
        for key in dict1.keys():
            if key in dict2:
                diff_dict[key] = dict1[key] - dict2[key]
            else:
                diff_dict[key] = dict1[key]
        for key in dict2.keys():
            if key not in dict1:
                diff_dict[key] = -dict2[key]
        total_value_diff = total_value1 - total_value2
        return diff_dict, total_value_diff

    def get_missing_selection(self, widgets):
        """Identify all missing selections and return their labels."""
        missing_selections = [label.cget("text") 
                              for key, (label, combobox) 
                              in widgets['selections'].items() 
                              if isinstance(combobox, ttk.Combobox) 
                              and not combobox.get()]
        return missing_selections
    
    def generate_footnote_and_figname(self, widgets):
        """Generate the footnote and figure name for the pie chart."""
        self.get_selections(widgets)
        threshold_input = widgets['threshold_entry'].get()
        threshold_input = threshold_input.replace(",", ".")
        threshold = float(threshold_input)
    
        if self.analysis_type == 'şehir':
            footnote = (
                f"{self.selected_year} yılında gerçekleşen yerel seçimin {self.selected_electiontype} oylarının\n"
                f"{self.selected_level1}"
                f"{', ' + self.selected_level2 if self.selected_level2 != '-' else ''}"
                f"{', ' + self.selected_level3 if self.selected_level3 != '-' else ''} "
                "bölgesinde partilere göre dağılımı\n"
                f"Not: Yüzde {threshold} değerinin altında oy alan partiler 'diger' kategorisine dahil edilmiştir"
            )
            fig_name = (
                f"{self.selected_year} - "
                f"{self.selected_level1}"
                f"{', ' + self.selected_level2 if self.selected_level2 != '-' else ''}"
                f"{', ' + self.selected_level3 if self.selected_level3 != '-' else ''}\n"
                f"({self.selected_electiontype} oyları)"
            )
    
        elif self.analysis_type == 'kategorik':
            footnote = (
                f"{self.selected_year} yılında gerçekleşen yerel seçimin {self.selected_electiontype} oylarının\n"
                f"{self.selected_category} verisinin {self.selected_subcategory} alt kategorisine göre gruplandırıldıktan sonra "
                "partilere göre dağılımı\n"
                f"Not: Yüzde {threshold} değerinin altında oy alan partiler 'diger' kategorisine dahil edilmiştir"
            )
            fig_name = (
                f"{self.selected_year} - "
                f"{self.selected_category}, {self.selected_subcategory}\n"
                f"({self.selected_electiontype} oyları)"
            )
    
        elif self.analysis_type == 'parti':
            footnote = (
                f"{self.selected_year} yılında gerçekleşen yerel seçimde\n"
                f"{self.selected_party} tarafından elde edilen {self.selected_electiontype} oylarının\n"
                f"{self.selected_category} kategorisinin alt kategorilerine göre dağılımı"
            )
            fig_name = (
                f"{self.selected_year} - "
                f"{self.selected_category} - {self.selected_party}"
            )
    
        elif self.analysis_type == 'ülke geneli':
            footnote = (
                f"{self.selected_year} yılında gerçekleşen yerel seçimde\n"
                f"ülke genelinde {self.selected_electiontype} oyları bazında\n"
                f"parti başına {self.selected_level} {self.selected_countrywide_category} dağılımı"
            )
            fig_name = (
                f"{self.selected_year} - "
                f"{self.selected_electiontype} {self.selected_countrywide_category}"
            )
    
        return footnote, fig_name, threshold
            
    def generate_pie_chart(self, widgets, frame_index):
        """Generate a pie chart and display the DataFrame data in the text areas."""
        self.get_selections(widgets)
        df, total_value = self.get_selected_dataframe(widgets)
        if df is not None:
            self.process_data(
                widgets, 
                frame_index
            )
            fig_name = f'Frame {frame_index + 1}'
            footnote, fig_name, threshold = self.generate_footnote_and_figname(widgets)
            
            if widgets['canvas'] is not None:
                widgets['canvas'].get_tk_widget().grid_remove()
            fig, _ = df_row_selector(df, threshold, fig_name, footnote)
            
            if widgets['canvas'] is not None:
                plt.close(widgets['canvas'].figure)
                widgets['canvas'].get_tk_widget().destroy()
                
            canvas = FigureCanvasTkAgg(
                fig, 
                master=widgets['canvas_frame']
            )
            canvas.draw()
            canvas.get_tk_widget().grid(
                row=0, column=0, sticky="nsew"
            )
            widgets['canvas'] = canvas
            widgets['canvas_frame'].grid_rowconfigure(0, weight=1)
            widgets['canvas_frame'].grid_columnconfigure(0, weight=1)
            widgets['canvas'].get_tk_widget().grid()
            
            if self.percentage_var.get():
                self.toggle_percentages()
                
        else:
            missing_selections = self.get_missing_selection(widgets)
            
            if missing_selections:
                error_message = f"Görsel üretmek için gerekli girdiler sağlanmadı.\nEksik değerler: {', '.join(missing_selections)}"
                messagebox.showerror(
                    "Hatalı Giriş", 
                    error_message
                )
        self.root.update_idletasks()

    def save_image(self, frame_index):
        """Save the current chart image to a file."""
        if (frame_index < len(self.frames_widgets) 
            and self.frames_widgets[frame_index]['canvas'] is not None
           ):
            fig = self.frames_widgets[frame_index]['canvas'].figure
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files","*.png"), 
                    ("JPEG files", "*.jpg"), 
                    ("All Files", "*.*")
                ],
                title="Kaydet"
            )
            if file_path:
                try:
                    fig.savefig(
                        file_path, 
                        dpi=300, 
                        bbox_inches='tight'
                    )
                    messagebox.showinfo(
                        "Başarılı", 
                        f"Görsel, belirtilen isim ile başarılya kaydedildi:\n{os.path.basename(file_path)}"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Hata", 
                        f"Görsel kaydedilemedi:\n{str(e)}"
                    )
        else:
            messagebox.showwarning(
                "Uyarı", 
                "Kaydedilecek görsel tespit edilemedi.\n Lütfen önce görseli oluşturunuz."
            )

    def save_data(self):
        """Export the data from all screens into an Excel file."""
        if not self.data_storage:
            messagebox.showwarning(
                "Uyarı", 
                "Kaydedilecek veri bulunmamakta.\nLütfen önce veri yüklemek için görsel oluşturun."
            )
            return
        combined_data = {}
        for frame_index, data_info in self.data_storage.items():
            if frame_index - 1 < len(self.frames_widgets):
                widgets = self.frames_widgets[frame_index - 1]
                _, fig_name, _ = self.generate_footnote_and_figname(widgets)
                data_series = pd.Series(
                    data_info['data'], 
                    name=fig_name
                )
                combined_data[fig_name] = data_series
            elif (frame_index == 3 
                  and self.calculate_difference_var.get()
                 ):
                data_series = pd.Series(
                    data_info['data'], 
                    name="Karşılaştırma"
                )
                combined_data["Karşılaştırma"] = data_series
        if not combined_data:
            messagebox.showwarning(
                "Uyarı", 
                "Kaydedilecek veri tespit edilemedi."
            )
            return
        combined_df = pd.DataFrame(combined_data).fillna(0)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"), 
                ("All Files", "*.*")
            ],
            title="Veriyi Kaydet"
        )
        if file_path:
            try:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, sheet_name="Data")
                messagebox.showinfo(
                    "Başarılı", 
                    f"Veri, belirtilen dosya ismi ile kaydedildi:\n{os.path.basename(file_path)}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Hata", 
                    f"Veri kaydedilemedi:\n{str(e)}"
                )