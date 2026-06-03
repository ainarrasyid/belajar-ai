from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chromadb
import ollama

app = FastAPI(title="Smile Platform AI API (Stateful + Rewriter)")

client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

class Pesan(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    pertanyaan: str
    riwayat: Optional[List[Pesan]] = []

class ChatResponse(BaseModel):
    jawaban: str
    sumber_konteks: int
    kueri_bersih: str # Kita tambahkan ini agar UI tahu teks aslinya diubah jadi apa

@app.post("/api/v1/ask", response_model=ChatResponse)
async def tanya_ai(payload: ChatRequest):
    try:
        # --- 0. QUERY REWRITING (Normalisasi Teks) ---
        prompt_rewriter = f"""
        Tugasmu HANYA memperbaiki ejaan kalimat di bawah ini menjadi bahasa Indonesia baku dan profesional.
        JANGAN menjawab pertanyaannya, JANGAN menambahkan penjelasan. Langsung berikan kalimat perbaikannya saja.
        
        Teks Asli: {payload.pertanyaan}
        Teks Perbaikan:
        """
        
        response_rewriter = ollama.generate(
            model='llama3',
            prompt=prompt_rewriter,
            options={'temperature': 0.0}
        )
        
        pertanyaan_bersih = response_rewriter['response'].strip()
        # Membersihkan tanda kutip tambahan jika LLM iseng menambahkannya
        pertanyaan_bersih = pertanyaan_bersih.replace('"', '').replace("'", "")
        
        print(f"\n[DEBUG] Teks Asli: '{payload.pertanyaan}'")
        print(f"[DEBUG] Teks Bersih: '{pertanyaan_bersih}'\n")

        # --- A. RETRIEVAL (Pencarian menggunakan Teks Bersih) ---
        hasil_pencarian = collection.query(
            query_texts=[pertanyaan_bersih],
            n_results=2,
            where={"kategori": "sop_internal"}
        )
        
        kumpulan_chunk = hasil_pencarian['documents'][0]
        konteks_gabungan = "\n---\n".join(kumpulan_chunk) if kumpulan_chunk else "Tidak ada referensi SOP."

        # --- B. Membangun String Riwayat Obrolan ---
        teks_riwayat = ""
        if payload.riwayat:
            for pesan in payload.riwayat:
                prefix = "Pengguna:" if pesan.role == "user" else "AI:"
                teks_riwayat += f"{prefix} {pesan.content}\n"

        # --- C. AUGMENTATION (Prompting menggunakan Teks Bersih) ---
        prompt_untuk_llm = f"""
        Kamu adalah asisten AI internal untuk operasional Smile Platform.
        Jawab pertanyaan terbaru pengguna berdasarkan POTONGAN SOP dan RIWAYAT OBROLAN di bawah ini.
        
        --- POTONGAN SOP ---
        {konteks_gabungan}
        --------------------
        
        --- RIWAYAT OBROLAN SEBELUMNYA ---
        {teks_riwayat if teks_riwayat else "(Belum ada riwayat)"}
        ----------------------------------
        
        Pertanyaan Terbaru Pengguna: {pertanyaan_bersih}
        Jawabanmu:
        """

        # --- D. GENERATION ---
        response_final = ollama.generate(
            model='llama3',
            prompt=prompt_untuk_llm,
            options={'temperature': 0.0}
        )

        return {
            "jawaban": response_final['response'].strip(),
            "sumber_konteks": len(kumpulan_chunk),
            "kueri_bersih": pertanyaan_bersih
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))