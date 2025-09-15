# Turkey Elections Visualizer

A Python/Tkinter GUI that reads official Turkish municipal election results (2019 & 2024) from Excel files, organizes them into hierarchical DataFrames, and lets users explore them with pie charts and sortable tables.

---

## Features
- **Interactive GUI** - Built with Tkinter, providing a clean interface for browsing official Turkish municipal (local) and general election results from 2019 and 2024.
- **Data-driven analysis** - Reads multiple Excel workbooks into hierarchical pandas DataFrames with multi-level indices for flexible filtering and aggregation
- **Dynamic charts** - Uses matplotlib (via chart_utils.py) to create sortable tables and interactive pie charts on demand.
- **Self-contained** - Can be bundled as a standalone executable (e.g via PyInstaller) or run directly from source.
- **Clear data organization** - Separates municipal summaries, general results, and per-year tables in a well-structured directory layout

---

## Project Structure
```
turkey-elections-visualizer
|   LICENSE
|   README.md
|   requirements.txt
|   
+---data
|   +---general_results
|   |       belediye_baskanligi_sonuclar.xlsx
|   |       belediye_meclisleri_sonuclar.xlsx
|   |       buyuksehir_baskanligi_sonuclar.xlsx
|   |       il_meclisleri_sonuclar.xlsx
|   |       
|   \---municipal_summary
|           baskanlik_summary_df_2019.xlsx
|           baskanlik_summary_df_2024.xlsx
|           meclis_summary_df_2019.xlsx
|           meclis_summary_df_2024.xlsx
|           
+---docs
|       img1.png
|       img2.png
|       
\---src
    |   app.py
    |   chart_utils.py
    |   config.py
    |   data_loader.py
    |   main.py
    \---   __init__.py
```
---

## Requirements
* Python **3.9+**  
* Python dependencies listed in requirements.txt
---

## Installation & Setup

1. ### Clone the repository:
```bash
git clone https://github.com/EmreYildiz448/turkey-elections-visualizer.git
cd turkey-elections-visualizer
```

2. ### Create and activate a virtual environment:

Run this command first (all platforms):
```bash
python -m venv .venv
```

1. *On Windows*

    ```bash
    .venv\Scripts\activate
    ```

2. *On macOS/Linux*

    ```bash
    source .venv/bin/activate
    ```

3. ### Install dependencies:
```bash
pip install -r requirements.txt
```
---

## Usage

### Run the visualizer:
```bash
python -m src.main
```
---

## Output
Launching the project opens the election visualizer interface shown below.
- [Pie chart visualizer](docs/img1.png)
- [Sortable tables](docs/img2.png)

The application itself is the final output - there are no extra data files generated.

---

## Known Issues

- **Silent no-data case**

If a user selects a combination of options that yields no matching table (for example, after using the Karşıya Kopyala "copy across" button), the "Grafik oluştur" (Create Graph) action currently performs no visible update and does not raise an error.

The application continues to run normally, but the absence of feedback can confuse users. Improving this with an explicit "No data available" dialog is planned.

---

## Roadmap

- Show a message box or status label when a graph cannot be generated because the selection returns no data.
- Add a "Reset Filters" button to clear all selections at once.
- Enhance chart interactivity (hover tooltips, export to PDF).
- Potential future data updates for upcoming election cycles (e.g., 2029).
---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## Acknowledgements

The election data displayed in this application originates from my companion project [turkey-elections-scraper](https://github.com/EmreYildiz448/turkey-elections-scraper.git).
That scraper collects and aggregates official 2019 & 2024 Turkish municipal election results, which are then consumed by this visualizer.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---