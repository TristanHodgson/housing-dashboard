# Housing Price Dashboard

An interactive data dashboard for exploring UK house prices over time and across regions.

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


## Plots Description

This section details the visualizations available in the dashboard, explaining the data transformations and plotting logic used in each view.

### Visualisation Tab

* **Prices Map**
    * Data Input: Raw average house price data (£) for a specific month, fetched from the database.
    * Plotting: A choropleth map plotting the selected month's average price against geographic Area Codes
    * Colouring: By default, it uses a non-linear scale to avoid being dominated by very high prices in central London. Users can toggle a linear colour map
    * Notes: The month shown is selected via a slider in the sidebar
* **Line Graphs**
    * **Raw Price**
        * Data Input: Raw average house price (£) over time
        * Plotting: Date (x-axis) vs. Average Price (y-axis)
        * Colouring: different colors for each selected region
    * **Rebased**:
        * Data Input: Prices indexed to a user-selected base month. Calculated as $\frac{\text{Price}}{\text{Base Month Price}} \times 100\%$
        * Plotting: Date (x-axis) vs. Indexed Price (y-axis), starting at 100 for the base month
        * Colouring: different colors for each selected region
    * **Log Returns**:
        * Data Input: Monthly log returns, calculated as the difference in natural log of prices between months, multiplied by 100 to express as a percentage
        * Plotting: Date (x-axis) vs. Monthly Log Return % (y-axis)
        * Colouring: Distinct colors for each selected region
* **Correlation Matrix**
    * Data Input: The correlation of log returns between the user-selected regions
    * Plotting: A heatmap grid of the correlation

### PCA Tab

* **Principal Component Analysis Map**
    * Data Input: Eigenvectors derived from the log returns of all regions. The data is standardised (mean 0 and s.d. 1) before PCA is applied
    * Plotting: A choropleth map plotting the loading values of the selected principal component onto the geography
    * Colouring: Colors represent the weight (loading) of that specific region in the selected principal component
    * Notes: The principle component shown is selected via a slider in the sidebar
* **Scree Plot**
    * Data Input: The explained variance ratio for each of the calculated principal components
    * Plotting: Principle component (x-axis) vs. variance explained (y-axis)

### Clustering Tab

* **K-Means Clustering Map**
    * Data Input: Normalized time-series data of log returns for all regions.
    * Plotting: A choropleth map displaying the cluster assignment for each region.
    * Colouring: Each discrete colour represents a distinct cluster group
    * Notes: The number of clusters (k) is determined by the user via a slider


## Architecture

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

* Do not see strong correlation between regions, except where regions are contained inside others (e.g. England and North West of England)