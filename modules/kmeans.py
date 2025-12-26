import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize


@st.cache_data
def kmeans(df, n_clusters=5):
    X = normalize(df)
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X)

    results = pd.DataFrame({
        "areacode": df.index, 
        "value": model.labels_,
        "label_value": [f"Cluster {l+1}" for l in model.labels_]})
    return results