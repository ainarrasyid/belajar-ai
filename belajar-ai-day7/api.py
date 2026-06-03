from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import ollama

# 1. INISIALISASI SERVER & DATABASE
app = FastAPI(title="Smile Platform AI API")

# Load database satu kali saat server menyala
client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

# 2. DEFINISI SKEMA PAYLOAD (Mirip Interface di TypeScript)
class ChatRequest(BaseModel):
    pertanyaan: str

class ChatResponse(BaseModel):
    jawaban: str
    sumber_konteks: int

# 3. ENDPOINT REST API
@app.post("/api/v1/ask", response_model=ChatResponse)
async def tanya_ai(payload: ChatRequest):
    try:
        # A. Retrieval
        hasil_pencarian = collection.query(
            query_texts=[payload.pertanyaan],
            n_results=2,
            where={"kategori": "sop_internal"}
        )
        
        # Ekstrak teks jika data ditemukan
        kumpulan_chunk = hasil_pencarian['documents'][0]
        if not kumpulan_chunk:
            return {"jawaban": "Maaf, tidak ada informasi SOP yang relevan.", "sumber_konteks": 0}
            
        konteks_gabungan = "\n---\n".join(kumpulan_chunk)

        # B. Augmentation (Prompt Engineering)
        prompt_untuk_llm = f"""
        Kamu adalah asisten AI internal untuk tim operasional Smile Platform.
        Jawab pertanyaan berikut hanya berdasarkan potongan SOP ini:
        
        --- POTONGAN SOP ---
        {konteks_gabungan}
        --------------------
        
        Pertanyaan: {payload.pertanyaan}
        Jawabanmu:
        """

        # C. Generation (Tanpa streaming untuk versi API dasar ini)
        response = ollama.generate(
            model='llama3',
            prompt=prompt_untuk_llm,
            stream=False, # Kita matikan streaming agar mudah dikonsumsi via JSON biasa
            options={'temperature': 0.0}
        )

        return {
            "jawaban": response['response'].strip(),
            "sumber_konteks": len(kumpulan_chunk)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
