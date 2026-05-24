import chromadb

# 1. RETRIEVAL: Tarik data relevan dari ChromaDB yang sudah kita isi di Hari 4
client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data") # Sesuaikan path-nya jika beda folder
collection = client.get_collection(name="pengetahuan_logistik")

pertanyaan_user = "Kenapa barang pesanan saya belum sampai juga?"

hasil_pencarian = collection.query(
    query_texts=[pertanyaan_user],
    n_results=1,
    where={"kategori": "kendala"}
)

# Ekstrak string murni dari hasil pencarian (menghilangkan format array)
konteks_ditemukan = hasil_pencarian['documents'][0][0]


# 2. AUGMENTATION: Merakit Prompt dengan konteks (Inilah inti utama RAG!)
prompt_untuk_llm = f"""
Kamu adalah asisten Customer Service yang sopan untuk Smile Platform.
Tugasmu adalah menjawab pertanyaan pengguna HANYA berdasarkan informasi yang disediakan di bawah ini.
Jika informasi di bawah tidak menjawab pertanyaan, katakan dengan sopan bahwa kamu tidak tahu, jangan mengarang jawaban.

--- INFORMASI DATABASE ---
{konteks_ditemukan}
--------------------------

Pertanyaan Pengguna: {pertanyaan_user}

Jawabanmu:
"""

print("=== 🔍 PROMPT YANG AKAN DIKIRIM KE LLM ===")
print(prompt_untuk_llm)


# 3. GENERATION: Mengirim prompt ke LLM
# Untuk saat ini, kita gunakan fungsi dummy sebelum menyambungkannya ke API sungguhan
def panggil_llm_api(prompt):
    # Di dunia nyata, di sinilah kita memanggil axios.post('api.openai.com/v1/chat/completions')
    return "Mohon maaf atas ketidaknyamanannya. Berdasarkan pengecekan pada sistem kami, paket Anda (resi 12345) saat ini sedang mengalami keterlambatan pengiriman yang diakibatkan oleh cuaca buruk dan banjir. Kami memohon kesabarannya."

jawaban_ai = panggil_llm_api(prompt_untuk_llm)

print("\n=== 🤖 JAWABAN AI KE PENGGUNA ===")
print(jawaban_ai)
