#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pathlib import Path
import pandas as pd
import sys

def load_excel_files():
    # Check if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS) / "data"
    else:
        # Running in a normal environment
        base_path = Path(__file__).resolve().parent.parent / "data"

    municipal_data_path = base_path / 'municipal_summary'
    general_results_path = base_path / 'general_results'

    # Define dictionaries for storing DataFrames
    df_dict_map = {'2019': {'başkanlık': {'büyükşehir': None, 'ilçe': None},
                            'meclis': {'il': None, 'ilçe': None}},
                   '2024': {'başkanlık': {'büyükşehir': None, 'ilçe': None},
                            'meclis': {'il': None, 'ilçe': None}}}

    countrywide_df_dict_map = {'başkanlık': {'büyükşehir': None, 'ilçe': None},
                               'meclis': {'il': None, 'ilçe': None}}

    datatable_df_dict = {'2019': {'başkanlık': None, 'meclis': None},
                         '2024': {'başkanlık': None, 'meclis': None}}

    # Define file names
    municipal_file_names = ["baskanlik_summary_df_2019.xlsx", "meclis_summary_df_2019.xlsx",
                            "baskanlik_summary_df_2024.xlsx", "meclis_summary_df_2024.xlsx"]

    general_results_file_names = ["belediye_baskanligi_sonuclar.xlsx", "belediye_meclisleri_sonuclar.xlsx",
                                  "buyuksehir_baskanligi_sonuclar.xlsx", "il_meclisleri_sonuclar.xlsx"]

    # Load municipal Excel files and store them in the dictionaries
    for file_name in municipal_file_names:
        year = '2019' if '2019' in file_name else '2024'
        type_key = 'başkanlık' if 'baskanlik' in file_name else 'meclis'

        file_path = municipal_data_path / file_name
        xls = pd.ExcelFile(file_path)

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name)
            df[['Province', 'County', 'Town']] = df[['Province', 'County', 'Town']].ffill()

            # Set MultiIndex for summary DataFrames
            if '_summary_df' in file_name:
                df.set_index(['Province', 'County', 'Town'], inplace=True)

            if 'ilceler' in sheet_name:
                if type_key == 'başkanlık':
                    df_dict_map[year][type_key]['ilçe'] = df
                else:
                    df_dict_map[year][type_key]['ilçe'] = df

            elif 'iller' in sheet_name:
                if type_key == 'başkanlık':
                    df_dict_map[year][type_key]['büyükşehir'] = df
                else:
                    df_dict_map[year][type_key]['il'] = df

            else:
                if type_key == 'başkanlık':
                    datatable_df_dict[year][type_key] = df
                else:
                    datatable_df_dict[year][type_key] = df

    # Load general results Excel files and store them in countrywide_df_dict_map
    for file_name in general_results_file_names:
        type_key = 'başkanlık' if 'baskanligi' in file_name else 'meclis'
        region_key = 'büyükşehir' if 'buyuksehir' in file_name else ('ilçe' if 'belediye' in file_name else 'il')

        file_path = general_results_path / file_name
        df = pd.read_excel(file_path)
        df.set_index(df.columns[0], inplace=True)
        countrywide_df_dict_map[type_key][region_key] = df

    return df_dict_map, countrywide_df_dict_map, datatable_df_dict

