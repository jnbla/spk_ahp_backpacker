import pandas as pd

def normalize_column(series):
    return (series - series.min()) / (series.max() - series.min())

def compute_ahp_scores(df, weights):
    df_norm = df.copy()
    for col in weights.keys():
        df_norm[col + '_norm'] = normalize_column(df[col])

    df_norm['Skor Total'] = sum(df_norm[col+'_norm'] * w for col, w in weights.items())
    df_result = df_norm[['Destinasi', 'Skor Total']].sort_values('Skor Total', ascending=False)
    return df_result, df_norm
