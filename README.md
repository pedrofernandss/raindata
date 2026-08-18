# 🌧️ RainData - Historical Precipitation Data Explorer

Web application for exploring, visualizing, downloading, and analyzing historical precipitation data from INMET automatic weather stations in Brazil.

## 🚀 Key Features

- **🗺️ Interactive Map:**
  - Geospatial visualization of INMET automatic weather stations across Brazil using Folium.
  - Click on a station marker to view information and access the Dataset Explorer.

- **📊 Dataset Explorer:**
  - **Dynamic Filters:** Filter stations by operational status and records by date range.
  - **Interactive Charts:** Time-series visualization of available numerical variables.
  - **Metadata Display:** Station code, coordinates, and operational status.
  - **Data Download:** Export filtered records as CSV or download the distributed dataset as ZIP.

- **💧 Hydrological & Statistical Analysis:**
  - **Monthly Climatology:** Mean monthly precipitation, driest and wettest months, and hydrological-year identification.
  - **Probability Distributions:** Fits GEV, Gumbel, Log-Normal, and Pearson Type III distributions to annual maximum daily precipitation.
  - **Kolmogorov-Smirnov Criterion:** Candidate distributions are compared using the KS statistic, and the distribution with the smallest value is selected.
  - **PDF & CDF:** Visualization of empirical and fitted probability distributions.
  - **IDF Curves & HMax:** Maximum precipitation by return period and Intensity-Duration-Frequency curves for return periods from 2 to 100 years.
  - **SPI-1 Index:** Standardized Precipitation Index at the one-month timescale, calculated from complete monthly precipitation records.
  - **Data-Quality Warnings:** Record-length and applicability warnings are displayed for frequency analysis, IDF, and SPI-1 results.

- **⚡ Efficient Data Storage:**
  - Uses **Apache Parquet** files for compact station-level storage and data loading.
  - Hydrological and statistical analyses are computed on demand for the selected station.

- **🌍 Bilingual Support:** English and Portuguese (PT-BR).

## 📡 Data Source

The precipitation data used in this project originate from **BDMEP** (Banco de Dados Meteorológicos do INMET), maintained by **INMET** (National Institute of Meteorology - Brazil).

The current dataset focuses on daily precipitation records from INMET automatic weather stations and is updated periodically through a curator-driven workflow.

## 🛠️ Tech Stack

- **Language:** Python
- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, NumPy
- **Statistical Analysis:** SciPy
- **Visualization:** Matplotlib, Folium
- **Data Storage:** Apache Parquet

## 📂 Project Structure

```text
raindata/
├── app.py                     # Application entry point and navigation
├── src/
│   ├── functions/             # Data processing, hydrology, statistics, and charts
│   └── utils/                 # Internationalization and application utilities
├── pages/
│   ├── home.py                # Home page and interactive station map
│   ├── explorer_page.py       # Dataset Explorer and data downloads
│   └── data_analysis_page.py  # Hydrological and statistical analyses
├── data/
│   ├── metadata_estacoes.parquet
│   └── dados_*.parquet        # Station-level precipitation datasets
└── requirements.txt           # Project dependencies
```

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wmpjrufg/raindata.git
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

4. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## ⚠️ Scope of Use

RainData is intended for research, exploratory hydrological analysis, planning, and preliminary engineering assessments.

IDF curves are based on empirical DAEE/CETESB rainfall-disaggregation coefficients and should be interpreted as screening and pre-design estimates rather than locally calibrated design relationships. SPI-1 and extreme-rainfall frequency results should also be interpreted considering the available record length and data completeness.

## 🎨 Theme

The application uses a custom dark theme with blue accents. Configuration is located in `.streamlit/config.toml`.
