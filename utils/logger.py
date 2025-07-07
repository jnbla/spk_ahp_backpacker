import pandas as pd
from datetime import datetime

def log_result(df, method):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"history_{method}_{timestamp}.csv"
    df.to_csv(f"data/{filename}", index=False)
