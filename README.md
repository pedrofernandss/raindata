# 🌧️ RainData - Historical Precipitation Data Explorer

Web application for accessing and downloading historical precipitation data in Brazil.

## 🚀 Key Features

- **🗺️ Interactive Map:**
  - Geospatial visualization of monitoring stations across Brazil using Folium.
  - Intuitive navigation: click on a map point to view station details.

- **📊 Detailed Dashboard:**
  - **Dynamic Filters:** Filter by year, month, date range, and operational status.
  - **Interactive Charts:** Time-series precipitation analysis.
  - **Metadata Display:** Station code, coordinates, and status.

- **💧 Hydrological & Statistical Analysis:**
  - **Distributions & Tests:** PDF, CDF, and Kolmogorov-Smirnov test to find the best statistical fit (GEV, Gumbel, Normal, Weibull, etc.).
  - **IDF Curves & HMax:** Intensity-Duration-Frequency curves and maximum precipitation by return period.
  - **SPI-1 Index:** Standardized Precipitation Index calculations modeling drought and wet cycles.

- **🌾 Commodities vs SPI:**
  - Dual-axis time-series visualizations correlating the State's average SPI-1 with local commodity prices (Soybean, Corn, Coffee, Sugarcane) using normalized scales.

- **⚡ High Performance:**
  - Uses **Parquet** format for ultra-fast data loading.
  - Optimized data pipeline.

- **🌍 Bilingual Support:** English and Portuguese (PT-BR) localizations.

## 📡 Data Source

The meteorological data used in this project is extracted from **BDMEP** (Banco de Dados Meteorológicos para Ensino e Pesquisa), provided by **INMET** (National Institute of Meteorology - Brazil). Commodity data relies on historical price series for Brazilian states.

## 🛠️ Tech Stack

- **Language:** Python 3.12
- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, NumPy, SciPy (Scientific & Hydrological computing)
- **Visualization:** Plotly Express, Plotly Graph Objects, Matplotlib, Folium

## 📂 Project Structure

```text
raindata/
├── app.py                # Application entry point (Navigation)
├── src/                  
│   ├── functions/        # Analytical functions (charts, data prep, hydrology, statistics)
│   └── utils/            # Utilities (i18n, Streamlit wakeup script)
├── pages/
│   ├── home.py           # Home Page (Folium Map)
│   ├── explorer_page.py  # Dataset Explorer (Station filters and raw metrics)
│   └── data_analysis_page.py # Hydrological Analysis & Commodities vs SPI
├── data/
│   ├── metadata_estacoes.parquet # Generated metadata file
└── requirements.txt      # Project dependencies
```

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/raindata.git
   cd raindata
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Data (ETL):**
   - Place your raw `.csv` files from BDMEP in the `rain_datasets` folder.
   - Run the `convert.ipynb` notebook to generate `metadata_estacoes.parquet` and convert data to Parquet.

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 🎨 Theme

The application uses a custom dark theme with blue accents for better data visualization. Configuration is located in `.streamlit/config.toml`.
