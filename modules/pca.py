from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import streamlit as st
import pandas as pd



@st.cache_data
def pca(log_returns: pd.DataFrame, n: int = 7):
    scaler = StandardScaler()
    X = scaler.fit_transform(log_returns)
    model = PCA(n_components=n)
    model.fit(X)

    eigenvectors = {}
    for i in range(n):
        eigenvectors[f"PC{i+1}"] = pd.DataFrame({
            "areacode": log_returns.columns,
            "value": model.components_[i]
        })

    scree = pd.DataFrame(
        model.explained_variance_ratio_.round(4),
        index=[f"PC{i+1}" for i in range(n)],
        columns=["Variance"]
    )

    return eigenvectors, scree
