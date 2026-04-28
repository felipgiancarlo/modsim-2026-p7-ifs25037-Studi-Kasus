import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Memuat isi file .env
load_dotenv()

# Inisialisasi client OpenAI
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_TOKEN")
)

def generate_itinerary(prompt):
    system_instruction = """
    Kamu adalah asisten travel planner profesional.
    Kamu WAJIB membalas HANYA dengan format JSON murni tanpa teks awalan atau akhiran apapun.
    Struktur JSON HARUS persis seperti ini:
    {
        "itinerary": [
            {
                "day": 1,
                "activity": "Deskripsi aktivitas dan tempat yang dikunjungi",
                "estimated_cost": "Rp xxx.xxx",
                "tips": "Tips lokal atau saran perjalanan singkat"
            }
        ]
    }
    """

    try:
        response = client.chat.completions.create(
            # PENTING: Gunakan model yang persis sama dengan yang baru saja berhasil kamu pakai
            model="nvidia/nemotron-3-super-120b-a12b:free", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 
        )
        
        raw_output = response.choices[0].message.content or ""
        print("====== BALASAN DARI AI ======\n", raw_output, "\n=============================")

        # --- LOGIKA PENGAMAN JSON SUPER (Mendukung Objek & Array) ---
        raw_output = raw_output.strip()
        
        # Cari posisi awal JSON (bisa berupa '{' atau '[')
        start_idx = -1
        for i, char in enumerate(raw_output):
            if char in ['{', '[']:
                start_idx = i
                break
                
        # Cari posisi akhir JSON (bisa berupa '}' atau ']')
        end_idx = -1
        for i in range(len(raw_output)-1, -1, -1):
            if raw_output[i] in ['}', ']']:
                end_idx = i + 1
                break
        
        # Jika tanda kurung ditemukan
        if start_idx != -1 and end_idx != -1:
            clean_json = raw_output[start_idx:end_idx]
            parsed_output = json.loads(clean_json)
            
            # Jika AI membalas langsung dengan Array/List [...], bungkus menjadi Object
            if isinstance(parsed_output, list):
                return {"itinerary": parsed_output}
            else:
                # Jika sudah berupa Object {...}, langsung kembalikan
                return parsed_output
        else:
            print("Peringatan: AI tidak memberikan format JSON yang valid.")
            return {"itinerary": []}

    except Exception as e:
        print(f"Terjadi kesalahan pada LLM Service: {e}")
        return {"itinerary": []}