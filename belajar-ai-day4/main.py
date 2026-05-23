import chromadb

# 1. Inisialisasi Database
client = chromadb.PersistentClient(path="./db_data")
collection = client.get_or_create_collection(name="pengetahuan_logistik")

# 2. Upsert Data (Update or Insert)
print("Melakukan sinkronisasi data ke Vector DB (Upsert)...")
collection.upsert(
    documents=[
        "Kurir bernama Budi sedang mengantar paket ke alamat pelanggan di Jakarta Selatan.",
        "Paket nomor resi 12345 mengalami keterlambatan pengiriman karena cuaca buruk dan banjir.",
        "Aplikasi Smile Platform dibangun menggunakan React Native dan TypeScript untuk performa mobile."
    ],
    metadatas=[
        # Menambahkan atribut spesifik seperti kurir_id dan nomor resi
        {"kategori": "pengiriman", "sumber": "tabel_log_kurir", "kurir_id": "K-001"}, 
        {"kategori": "kendala", "sumber": "tabel_tiket_cs", "resi": "12345"}, 
        {"kategori": "teknis", "sumber": "wiki_internal", "platform": "mobile"}
    ],
    ids=[
        # Menggunakan Deterministic ID (Gabungan nama tabel dan Primary Key)
        "log_kurir_001",   
        "tiket_cs_12345",  
        "wiki_smile_01"    
    ]
)
print("Sinkronisasi sukses! Data aman dari duplikasi.\n")

# 3. Pengujian Pencarian dengan Filter Metadata yang Diperbarui
pertanyaan = "Kenapa barang pesanan saya belum sampai juga?"
print(f"Mencari keluhan pelanggan untuk: '{pertanyaan}'\n")

hasil_pencarian = collection.query(
    query_texts=[pertanyaan],
    n_results=1,
    where={"kategori": "kendala"} # Filter tetap berjalan
)

print("=== HASIL PENCARIAN TERBAIK ===")
print("ID Dokumen :", hasil_pencarian['ids'][0][0])
print("Teks Asli  :", hasil_pencarian['documents'][0][0])
print("Metadata   :", hasil_pencarian['metadatas'][0][0])
print("Jarak      :", f"{hasil_pencarian['distances'][0][0]:.4f}")