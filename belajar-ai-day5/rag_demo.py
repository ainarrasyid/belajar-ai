import chromadb
import ollama  # Import library Ollama yang baru saja diinstal

# 1. RETRIEVAL
client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

pertanyaan_user = "Kenapa barang pesanan saya belum sampai juga?"

print(f"Mencari data untuk: '{pertanyaan_user}'...")
hasil_pencarian = collection.query(
    query_texts=[pertanyaan_user],
    n_results=1,
    where={"kategori": "kendala"}
)
konteks_ditemukan = hasil_pencarian['documents'][0][0]

# 2. AUGMENTATION
prompt_untuk_llm = f"""
Kamu adalah asisten Customer Service yang sopan untuk Smile Platform.
Tugasmu adalah menjawab pertanyaan pengguna HANYA berdasarkan informasi yang disediakan di bawah ini.
Gunakan bahasa Indonesia yang baik, ramah, dan profesional.
Jika informasi di bawah tidak menjawab pertanyaan, katakan dengan sopan bahwa kamu tidak tahu.

--- INFORMASI DATABASE ---
{konteks_ditemukan}
--------------------------

Pertanyaan Pengguna: {pertanyaan_user}

Jawabanmu:
"""

# 3. GENERATION (MENGGUNAKAN OLLAMA LOKAL)
print("\nSedang memikirkan jawaban (menggunakan akselerasi GPU M1)...")

# Memanggil model Llama 3 yang sudah berjalan di localhost
response = ollama.generate(
    model='llama3',
    prompt=prompt_untuk_llm
)

print("\n=== 🤖 JAWABAN AI (Llama 3) KE PENGGUNA ===")
# Ollama mengembalikan dictionary, kita ambil key 'response'-nya
print(response['response'])