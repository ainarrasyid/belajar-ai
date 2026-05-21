# Import library dan berikan alias 'pd' (ini adalah standar industri)
import pandas as pd

# 1. Membaca file CSV
# JS analogi: const df = parseCSV(readFile('log_transaksi.csv'))
df = pd.read_csv("log_transaksi.csv")

print("=== Semua Data ===")
print(df)
print("\n")

# 2. Memfilter Data: Ambil hanya yang statusnya 'failed'
# JS analogi: const failedTx = df.filter(row => row.status === 'failed')
failed_tx = df[df["status"] == "failed"]

print("=== Transaksi Gagal ===")
print(failed_tx)
print("\n")

# 3. Operasi Matematika: Rata-rata waktu proses (ms)
# JS analogi: const avg = df.reduce(...) / df.length
rata_rata_waktu = df["waktu_proses_ms"].mean()

print(f"Rata-rata waktu proses: {rata_rata_waktu} ms")
failed_tx.to_json("failed_transactions.json", orient="records", indent=2)
print("File failed_transactions.json berhasil dibuat!")