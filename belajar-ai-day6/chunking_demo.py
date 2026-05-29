# Simulasi teks dokumen SOP yang panjang
dokumen_sop = """SOP Pengiriman Smile Platform. 
Bab 1: Persiapan. Kurir wajib memeriksa kondisi kendaraan sebelum berangkat. Pastikan bensin penuh dan rem berfungsi. 
Bab 2: Kendala Cuaca. Jika terjadi hujan lebat atau banjir, kurir berhak menunda pengiriman dan melaporkannya ke sistem tiket. Paket harus dibungkus plastik ganda. 
Bab 3: Pengantaran Gagal. Jika pelanggan tidak ada di rumah, kurir harus menelepon maksimal 3 kali. Jika tidak diangkat, paket dikembalikan ke gudang Hub.
"""

def potong_teks(teks, ukuran_kata=15, overlap=5):
    """
    Fungsi untuk memotong teks panjang menjadi chunks dengan overlap.
    ukuran_kata: Jumlah kata per potongan
    overlap: Jumlah kata yang diulang dari potongan sebelumnya agar konteks tidak putus
    """
    kata_kumpulan = teks.split()
    chunks = []
    
    # Looping lompat sejauh (ukuran_kata - overlap)
    step = ukuran_kata - overlap
    for i in range(0, len(kata_kumpulan), step):
        # Ambil potongan kata
        potongan = kata_kumpulan[i : i + ukuran_kata]
        
        # Gabungkan kembali array kata menjadi string
        teks_potongan = " ".join(potongan)
        chunks.append(teks_potongan)
        
        # Berhenti jika kita sudah mencapai akhir teks
        if i + ukuran_kata >= len(kata_kumpulan):
            break
            
    return chunks

# Mari kita jalankan mesin pemotongnya
hasil_potongan = potong_teks(dokumen_sop, ukuran_kata=20, overlap=5)

print(f"Total karakter asli: {len(dokumen_sop)}")
print(f"Berhasil dipotong menjadi {len(hasil_potongan)} bagian.\n")

print("=== HASIL CHUNKING ===")
for index, chunk in enumerate(hasil_potongan):
    print(f"Chunk {index + 1} : {chunk}")