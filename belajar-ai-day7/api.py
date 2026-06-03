from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chromadb
import ollama

app = FastAPI(title="Smile Platform AI API (Stateful)")

client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

# 1. SKEMA DATA BARU: Mendukung Riwayat Obrolan
class Pesan(BaseModel):
    role: str # 'user' atau 'ai'
    content: str

class ChatRequest(BaseModel):
    pertanyaan: str
    riwayat: Optional[List[Pesan]] = [] # Opsional, array kosong jika obrolan baru

class ChatResponse(BaseModel):
    jawaban: str
    sumber_konteks: int

# 2. ENDPOINT API
@app.post("/api/v1/ask", response_model=ChatResponse)
async def tanya_ai(payload: ChatRequest):
    try:
        # A. Retrieval (Pencarian Vector)
        hasil_pencarian = collection.query(
            query_texts=[payload.pertanyaan],
            n_results=2,
            where={"kategori": "sop_internal"}
        )
        
        kumpulan_chunk = hasil_pencarian['documents'][0]
        konteks_gabungan = "\n---\n".join(kumpulan_chunk) if kumpulan_chunk else "Tidak ada referensi SOP."

        # B. Membangun String Riwayat Obrolan
        teks_riwayat = ""
        if payload.riwayat:
            for pesan in payload.riwayat:
                prefix = "Pengguna:" if pesan.role == "user" else "AI:"
                teks_riwayat += f"{prefix} {pesan.content}\n"

        # C. Augmentation (Merakit Prompt Lanjutan dengan Memori)
        prompt_untuk_llm = f"""
        Kamu adalah asisten AI internal untuk operasional Smile Platform.
        Jawab pertanyaan terbaru pengguna berdasarkan POTONGAN SOP dan RIWAYAT OBROLAN di bawah ini.
        
        --- POTONGAN SOP ---
        {konteks_gabungan}
        --------------------
        
        --- RIWAYAT OBROLAN SEBELUMNYA ---
        {teks_riwayat if teks_riwayat else "(Belum ada riwayat)"}
        ----------------------------------
        
        Pertanyaan Terbaru Pengguna: {payload.pertanyaan}
        Jawabanmu:
        """

        # D. Generation
        response = ollama.generate(
            model='llama3',
            prompt=prompt_untuk_llm,
            stream=False,
            options={'temperature': 0.0}
        )

        return {
            "jawaban": response['response'].strip(),
            "sumber_konteks": len(kumpulan_chunk)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))