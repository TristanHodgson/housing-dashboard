# Housing Price Dashboard

An interactive data dashboard for exploring UK house prices over time and across regions.
Built with Streamlit, Plotly, Pandas, GeoPandas, and Folium, this project provides multiple complementary views of regional house price levels, returns, and correlations.

## Usage

```
git clone https://github.com/TristanHodgson/housing-dashboard.git
cd housing-dashboard
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

[Download the data](https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-september-2025)

```
python scripts\import_data.py
```
You may need to adjust the above file to use the correct file name in the csv_file variable
```
python -m streamlit run main.py
```

## Screenshots

![](img/vis.png)
![](img/pca.png)
![](img/clustering.png)

## System Architecture


**Data Flow:**
1. Raw CSV data from the UK Government is processed, cleaned, and loaded into a SQLite database
2. SQL queries fetch the necessary data
3. Statistical modules perform calculations on Pandas DataFrames.
4. Streamlit renders the interactive dashboard, utilizing Plotly for dynamic charts and Folium for geospatial mapping

| File | Description |
| :--- | :--- |
| `main.py` | Handles the Streamlit layout |
| `scripts/import_data.py` | Script that cleans raw UK HPI CSV data and writes it to the SQLite database |
| `modules/data.py` | Modules for using the SQL database |
| `modules/geo_data.py` | Geospatial modules, including fetching/caching UK boundary files and generating choropleth maps |
| `modules/pca.py` | Implements Principal Component Analysis (PCA) |
| `modules/kmeans.py` | Implements K-Means clustering |
| `modules/line.py` | Contains logic for generating interactive time-series line charts |

## Insights

* PCA
    * First few components do not explain much of the variance in the log returns
    * The first component seems to be a simple size component, nearly all values are positive
    * The second component seems to capture the North/South divide
    * The third component very clearly captures Northern Ireland
    * The forth component is much less clear but could be said to capture Scotland
    * Beyond that I cannot discern a pattern

* K-Means, we see strong geographic divides despite no geographic data in the model
    * 2 clusters
        * With two clusters we see what we might expect with a North/South divide 
        * Somewhat surprisingly however, North Yorkshire is in the South 
    * 3 clusters
        * See the North/South/Scotland divide
        * Northern Ireland yet to get its own cluster, it has been placed in the North of England
    * 5 clusters
        * Northern Ireland gets its own cluster for the first time
        * Other clusters for Scotland (divide at the border), North of England and two clusters for the South
        * South split seems to be split along socio-economic lines with Cotswolds, Cornwall, and Wales in one section and London, home counties etc in the other

* Do not see strong correlation between regions