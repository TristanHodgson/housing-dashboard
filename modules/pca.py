from modules import data
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import streamlit as st
import pandas as pd


@st.cache_data
def pca(returns, n=10):
    returns = np.log(returns).diff().dropna()
    scaler = StandardScaler()
    standard_return = scaler.fit_transform(returns)
    pca = PCA(n_components=n)
    pca_returns = pca.fit_transform(standard_return)
    pca_skee = pca.explained_variance_ratio_
    eigenvectors = pd.DataFrame(
        pca.components_.T,
        index=returns.columns,
        columns=[f"PC{i+1}" for i in range(n)]
    )
    return eigenvectors, pca_skee