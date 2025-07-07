import pandas as pd
import numpy as np

def normalize_column(series):
    return series / np.sqrt((series**2).sum())

def compute_topsis_scores(df, weights):
    df_norm = df.copy()
    for col in weights.keys():
        df_norm[col + '_norm'] = normalize_column(df[col])

    ideal_best = df_norm[[c+'_norm' for c in weights.keys()]].max()
    ideal_worst = df_norm[[c+'_norm' for c in weights.keys()]].min()

    dist_best = np.sqrt(((df_norm[[c+'_norm' for c in weights.keys()]] - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((df_norm[[c+'_norm' for c in weights.keys()]] - ideal_worst)**2).sum(axis=1))

    df_norm['Skor Total'] = dist_worst / (dist_best + dist_worst)
    df_result = df_norm[['Destinasi', 'Skor Total']].sort_values('Skor Total', ascending=False)
    return df_result, df_norm
