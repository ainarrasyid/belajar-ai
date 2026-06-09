from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chromadb
import ollama
import json # Tambahkan modul json bawaan Python

app = FastAPI(title="Smile Platform AI API (Router Edition)")

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
    intent: str # Tambahkan balasan intent ke UI
    sumber_konteks: int
    kueri_bersih: str

@app.post("/api/v1/ask", response_model=ChatResponse)
async def tanya_ai(payload: ChatRequest):
    try:
        # --- 0. QUERY REWRITING (Dari Hari 7) ---
        prompt_rewriter = f"""
        Tugasmu HANYA memperbaiki ejaan (typo) dan singkatan menjadi bahasa Indonesia baku.
        ATURAN MUTLAK: DILARANG mengubah makna, DILARANG menjawab pertanyaan, DILARANG menambah teks lain.
        Teks Asli: {payload.pertanyaan}
        Teks Perbaikan:
        """
        response_rewriter = ollama.generate(model='llama3', prompt=prompt_rewriter, options={'temperature': 0.0})
        pertanyaan_bersih = response_rewriter['response'].strip().replace('"', '').replace("'", "")

        if pertanyaan_bersih.lower().startswith("teks perbaikan:"):
            pertanyaan_bersih = pertanyaan_bersih[15:].strip()
        
        print(f"\n[DEBUG] Teks Bersih: '{pertanyaan_bersih}'")

        # --- 1. INTENT ROUTING (FITUR BARU) ---
        prompt_router = f"""
        Analisis pertanyaan berikut dan tentukan niat penggunanya.
        Pilih HANYA satu dari 3 kategori berikut:
        - "sop" : Bertanya tentang aturan, pedoman, atau cara kerja sistem.
        - "tracking" : Bertanya tentang nomor resi, status paket spesifik, atau data pelanggan.
        - "general" : Sekadar sapaan (halo, pagi) atau di luar topik logistik.

        Berikan balasan HANYA dalam format JSON valid dengan satu key "intent".
        Contoh balasan: {{"intent": "sop"}}
        
        Pertanyaan: {pertanyaan_bersih}
        """

        # Memaksa Ollama membalas dalam bentuk JSON
        response_router = ollama.generate(
            model='llama3',
            prompt=prompt_router,
            format='json', # Fitur ajaib untuk integrasi API
            options={'temperature': 0.0}
        )
        
        # Parse output JSON dari LLM
        routing_data = json.loads(response_router['response'])
        user_intent = routing_data.get('intent', 'general')
        print(f"[DEBUG] Terdeteksi Niat: {user_intent.upper()}")

        # --- 2. PERCABANGAN LOGIKA BERDASARKAN INTENT ---
        
        if user_intent == "general":
            # Langsung jawab tanpa membebani Vector DB
            jawaban_final = "Halo! Saya adalah AI Asisten Operasional. Ada yang bisa saya bantu terkait SOP atau pengecekan paket hari ini?"
            sumber_konteks = 0
            
        elif user_intent == "tracking":
            # Nanti di sini kita bisa panggil API eksternal / SQL Query
            jawaban_final = "Sistem deteksi paket sedang dalam pengembangan. Mohon tunggu integrasi database operasional."
            sumber_konteks = 0
            
        else:
            # user_intent == "sop" (Jalankan RAG ChromaDB Normal)
            hasil_pencarian = collection.query(
                query_texts=[pertanyaan_bersih],
                n_results=2,
                where={"kategori": "sop_internal"}
            )
            kumpulan_chunk = hasil_pencarian['documents'][0]
            konteks_gabungan = "\n---\n".join(kumpulan_chunk) if kumpulan_chunk else "Tidak ada referensi SOP."

            prompt_rag = f"""
            Jawab pertanyaan pengguna berdasarkan POTONGAN SOP ini.
            --- POTONGAN SOP ---
            {konteks_gabungan}
            --------------------
            Pertanyaan: {pertanyaan_bersih}
            """
            
            response_rag = ollama.generate(model='llama3', prompt=prompt_rag, options={'temperature': 0.0})
            jawaban_final = response_rag['response'].strip()
            sumber_konteks = len(kumpulan_chunk)

        # --- 3. RETURN RESPONSE API ---
        return {
            "jawaban": jawaban_final,
            "intent": user_intent,
            "sumber_konteks": sumber_konteks,
            "kueri_bersih": pertanyaan_bersih
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))