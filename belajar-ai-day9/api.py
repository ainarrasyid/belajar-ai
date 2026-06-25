from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chromadb
import ollama
import json

app = FastAPI(title="Smile Platform AI API (Agentic Edition)")

client = chromadb.PersistentClient(path="../belajar-ai-day4/db_data")
collection = client.get_collection(name="pengetahuan_logistik")

# ==========================================
# 📦 DUMMY DATABASE LOGISTIK
# ==========================================
DB_RESI = {
    "SMILE-99123": {"status": "Tertahan di Hub Jakarta", "kendala": "Banjir - Menunggu cuaca reda", "kurir": "-"},
    "SMILE-11223": {"status": "Sedang diantar ke alamat tujuan", "kendala": "Aman", "kurir": "Budi Santoso"},
    "SMILE-55555": {"status": "Terkirim", "kendala": "Aman", "kurir": "Andi"}
}

def cek_database_resi(nomor_resi: str) -> dict:
    # Fungsi ini mensimulasikan query "SELECT * FROM pengiriman WHERE resi = ?"
    # Mengubah teks menjadi uppercase agar pencarian tidak case-sensitive
    return DB_RESI.get(nomor_resi.upper(), {"status": "Resi tidak ditemukan", "kendala": "-", "kurir": "-"})
# ==========================================

class Pesan(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    pertanyaan: str
    riwayat: Optional[List[Pesan]] = []

class ChatResponse(BaseModel):
    jawaban: str
    intent: str
    sumber_konteks: int
    kueri_bersih: str

@app.post("/api/v1/ask", response_model=ChatResponse)
async def tanya_ai(payload: ChatRequest):
    try:
        # --- 0. QUERY REWRITING ---
        prompt_rewriter = f"""
        Tugasmu HANYA memperbaiki ejaan (typo) dan singkatan menjadi bahasa Indonesia baku.
        ATURAN MUTLAK: DILARANG mengubah makna, DILARANG menjawab pertanyaan, DILARANG menambah teks lain.
        Teks Asli: {payload.pertanyaan}
        Teks Perbaikan:
        """
        response_rewriter = ollama.generate(model='llama3', prompt=prompt_rewriter, options={'temperature': 0.0})
        pertanyaan_bersih = response_rewriter['response'].strip().replace('"', '').replace("'", "")
        
        # Sanitasi teks (Post-Processing)
        if pertanyaan_bersih.lower().startswith("teks perbaikan:"):
            pertanyaan_bersih = pertanyaan_bersih[15:].strip()

        print(f"\n[DEBUG] Teks Bersih: '{pertanyaan_bersih}'")

        # --- 1. INTENT ROUTING ---
        prompt_router = f"""
        Analisis pertanyaan berikut dan tentukan niat penggunanya.
        Pilih HANYA satu dari 3 kategori berikut:
        - "sop" : Bertanya tentang aturan, pedoman, atau cara kerja sistem.
        - "tracking" : Bertanya tentang nomor resi, melacak paket, atau status pengiriman.
        - "general" : Sekadar sapaan (halo, pagi) atau di luar topik logistik.

        Berikan balasan HANYA dalam format JSON valid dengan satu key "intent".
        Contoh: {{"intent": "tracking"}}
        
        Pertanyaan: {pertanyaan_bersih}
        """

        response_router = ollama.generate(model='llama3', prompt=prompt_router, format='json', options={'temperature': 0.0})
        routing_data = json.loads(response_router['response'])
        user_intent = routing_data.get('intent', 'general')
        print(f"[DEBUG] Terdeteksi Niat: {user_intent.upper()}")

        # --- 2. PERCABANGAN LOGIKA BERDASARKAN INTENT ---
        
        if user_intent == "general":
            jawaban_final = "Halo! Saya adalah AI Asisten Operasional Smile Platform. Ada yang bisa saya bantu terkait SOP internal atau pengecekan resi paket hari ini?"
            sumber_konteks = 0
            
        elif user_intent == "tracking":
            # A. Ekstrak Parameter (Entity Extraction)
            prompt_ekstrak = f"""
            Ekstrak nomor resi dari teks berikut. Format resi biasanya gabungan huruf dan angka (misal SMILE-123).
            Balas HANYA dengan JSON valid format: {{"nomor_resi": "isi_nomor_disini"}}
            Jika tidak ada nomor resi yang disebutkan, isi dengan string kosong "".
            
            Teks: {pertanyaan_bersih}
            """
            res_ekstrak = ollama.generate(model='llama3', prompt=prompt_ekstrak, format='json', options={'temperature': 0.0})
            data_resi = json.loads(res_ekstrak['response'])
            nomor_resi = data_resi.get('nomor_resi', '')
            
            print(f"[DEBUG] Nomor Resi Terdeteksi: '{nomor_resi}'")

            # B. Eksekusi Fungsi Python (Tool Calling)
            if nomor_resi:
                hasil_db = cek_database_resi(nomor_resi)
                
                # C. Generate Jawaban Manusiawi dari Data Mentah DB
                prompt_pembaca_db = f"""
                Kamu adalah CS yang ramah. Beritahu pengguna status paket mereka berdasarkan data mentah dari database berikut.
                Nomor Resi: {nomor_resi}
                Status: {hasil_db['status']}
                Kendala: {hasil_db['kendala']}
                Kurir: {hasil_db['kurir']}
                """
                res_final_tracking = ollama.generate(model='llama3', prompt=prompt_pembaca_db, options={'temperature': 0.3})
                jawaban_final = res_final_tracking['response'].strip()
            else:
                jawaban_final = "Mohon maaf, saya tidak menemukan nomor resi dalam pertanyaan Anda. Bisa tolong sebutkan nomor resinya? (contoh: SMILE-99123)"
            
            sumber_konteks = 0
            
        else:
            # user_intent == "sop"
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
            Jawabanmu:
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