import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Persiapan Dokumen (Simulasi baca dari file/database)
dokumen_sop = """SOP Pengiriman Smile Platform. 
Bab 1: Persiapan. Kurir wajib memeriksa kondisi kendaraan sebelum berangkat. Pastikan bensin penuh dan rem berfungsi. 
Bab 2: Kendala Cuaca. Jika terjadi hujan lebat atau banjir, kurir berhak menunda pengiriman dan melaporkannya ke sistem tiket. Paket harus dibungkus plastik ganda. 
Bab 3: Pengantaran Gagal. Jika pelanggan tidak ada di rumah, kurir harus menelepon maksimal 3 kali. Jika tidak diangkat, paket dikembalikan ke gudang Hub.
"""

# 2. Pemotongan Teks (Chunking)
pemotong = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = pemotong.split_text(dokumen_sop)

# 3. Koneksi ke Vector Database
client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_or_create_collection(name="pengetahuan_logistik")

# 4. Persiapan Array untuk Upsert
dokumen_untuk_db = []
metadata_untuk_db = []
id_untuk_db = []

dokumen_sumber = "sop_pengiriman_v1" # Anggap ini Primary Key dari tabel dokumen

for index, teks_potongan in enumerate(chunks):
    dokumen_untuk_db.append(teks_potongan)
    
    # Metadata sangat penting agar kita tahu potongan ini berasal dari dokumen mana
    metadata_untuk_db.append({
        "sumber": dokumen_sumber,
        "chunk_index": index,
        "kategori": "sop_internal"
    })
    
    # Deterministic ID: "sop_pengiriman_v1_chunk_0", "sop_pengiriman_v1_chunk_1", dst.
    id_untuk_db.append(f"{dokumen_sumber}_chunk_{index}")

# 5. Eksekusi Upsert ke ChromaDB
print(f"Menyuntikkan {len(chunks)} potongan teks ke dalam Vector DB...")
collection.upsert(
    documents=dokumen_untuk_db,
    metadatas=metadata_untuk_db,
    ids=id_untuk_db
)
print("Berhasil! Pengetahuan sistem telah diperbarui secara permanen.")