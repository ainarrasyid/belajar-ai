from langchain_text_splitters import RecursiveCharacterTextSplitter

dokumen_sop = """SOP Pengiriman Smile Platform. 

Bab 1: Persiapan. 
Kurir wajib memeriksa kondisi kendaraan sebelum berangkat. Pastikan bensin penuh dan rem berfungsi. 

Bab 2: Kendala Cuaca. 
Jika terjadi hujan lebat atau banjir, kurir berhak menunda pengiriman dan melaporkannya ke sistem tiket. Paket harus dibungkus plastik ganda. 

Bab 3: Pengantaran Gagal. 
Jika pelanggan tidak ada di rumah, kurir harus menelepon maksimal 3 kali. Jika tidak diangkat, paket dikembalikan ke gudang Hub.
"""

# Inisialisasi pemotong teks cerdas (menggunakan karakter, bukan kata)
pemotong = RecursiveCharacterTextSplitter(
    chunk_size=150,       # Maksimal 150 karakter per potongan
    chunk_overlap=30,     # Overlap 30 karakter agar konteks nyambung
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""] # Hierarki pencarian titik potong
)

# Eksekusi pemotongan
hasil_potongan = pemotong.split_text(dokumen_sop)

print("=== HASIL CHUNKING LANGCHAIN ===")
for index, chunk in enumerate(hasil_potongan):
    print(f"\n[Chunk {index + 1} | {len(chunk)} karakter]")
    print(chunk)