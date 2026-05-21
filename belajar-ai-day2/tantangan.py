import pandas as pd

df = pd.read_csv("api_logs.csv")

avg_process_ms_per_route = df.dropna() \
                    .groupby("rute_api")["waktu_proses_ms"] \
                    .mean()
print(avg_process_ms_per_route)