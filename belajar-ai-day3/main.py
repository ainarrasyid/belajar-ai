from sentence_transformers import SentenceTransformer, util

print("Memuat model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

kalimat_1 = "Kurir sedang mengantar barang ke alamat pelanggan."
kalimat_2 = "Paket sedang dalam perjalanan menuju rumah pembeli."
kalimat_3 = "Aplikasi mobile Smile Platform menggunakan React Native."

embedding_1 = model.encode(kalimat_1)
embedding_2 = model.encode(kalimat_2)
embedding_3 = model.encode(kalimat_3)

print(f"\nBentuk array kalimat 1: Terdiri dari {len(embedding_1)} dimensi angka")
print(f"Contoh 5 angka pertamanya: {embedding_1[:5]}")

kemiripan_1_dan_2 = util.cos_sim(embedding_1, embedding_2)
kemiripan_1_dan_3 = util.cos_sim(embedding_1, embedding_3)

print("\n=== HASIL ANALISIS SEMANTIK ===")
print(f"Skor kemiripan Kalimat 1 dan Kalimat 2: {kemiripan_1_dan_2[0][0]:.4f} (Makna Mirip)")
print(f"Skor kemiripan Kalimat 1 dan Kalimat 3: {kemiripan_1_dan_3[0][0]:.4f} (Makna Berbeda)")