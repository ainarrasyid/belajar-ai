import chromadb
import ollama

# 1. KONEKSI DATABASE
client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

# Simulasi pertanyaan operasional dari kurir atau tim ops di lapangan
pertanyaan_user = "Kalau di luar sedang banjir, apakah saya boleh menunda pengiriman paket?"

print(f"Mencari referensi SOP untuk: '{pertanyaan_user}'...\n")

# 2. RETRIEVAL (Mengambil 2 chunk teratas yang paling relevan)
hasil_pencarian = collection.query(
    query_texts=[pertanyaan_user],
    n_results=2,  # Kita ambil 2 chunk teratas agar informasi lebih padat
    where={"kategori": "sop_internal"}
)

# Menggabungkan seluruh chunk dokumen yang ditemukan menjadi satu kesatuan teks
kumpulan_chunk = hasil_pencarian['documents'][0]
konteks_gabungan = "\n---\n".join(kumpulan_chunk)


# 3. AUGMENTATION (Merakit Prompt)
prompt_untuk_llm = f"""
Kamu adalah asisten AI internal untuk tim operasional Smile Platform.
Tugasmu adalah menjawab pertanyaan pengguna berdasarkan potongan SOP yang disediakan di bawah ini.
Jawab dengan ramah, lugas, dan profesional menggunakan bahasa Indonesia.
Jika informasi di bawah tidak menyebutkan jawabannya, katakan dengan sopan bahwa informasi tidak ditemukan di SOP.

--- POTONGAN SOP INTERNAL ---
{konteks_gabungan}
-----------------------------

Pertanyaan Pengguna: {pertanyaan_user}

Jawabanmu:
"""


# 4. GENERATION (Streaming dengan Llama 3)
print("=== 🤖 JAWABAN AI (Llama 3 Lokal) ===")

stream_response = ollama.generate(
    model='llama3',
    prompt=prompt_untuk_llm,
    stream=True,
    options={
        'temperature': 0.0  # Menjaga jawaban tetap konsisten sesuai SOP, tidak ngawur
    }
)

# Tampilkan kata demi kata saat model selesai memprosesnya di GPU
for chunk in stream_response:
    print(chunk['response'], end='', flush=True)

print("\n")