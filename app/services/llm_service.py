import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
                "activity": "Deskripsi aktivitas",
                "estimated_cost": "Rp xxx.xxx",
                "tips": "Tips lokal"
            }
        ]
    }
    """

    try:
        response = client.chat.completions.create(
            model="inclusionai/ling-2.6-1t:free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 
        )
        
        raw_output = response.choices[0].message.content or ""
        print("====== BALASAN DARI AI ======\n", raw_output, "\n=============================")

        raw_output = raw_output.strip()
        start_idx = -1
        for i, char in enumerate(raw_output):
            if char in ['{', '[']:
                start_idx = i
                break
                
        end_idx = -1
        for i in range(len(raw_output)-1, -1, -1):
            if raw_output[i] in ['}', ']']:
                end_idx = i + 1
                break
        
        if start_idx != -1 and end_idx != -1:
            clean_json = raw_output[start_idx:end_idx]
            parsed_output = json.loads(clean_json)
            
            if isinstance(parsed_output, list):
                return {"itinerary": parsed_output}
            else:
                return parsed_output
        else:
            raise ValueError("AI tidak memberikan format JSON yang valid.")

    except Exception as e:
        print(f"🔥🔥🔥 ERROR LLM: {e} 🔥🔥🔥")
        raise Exception(f"Gagal memanggil AI: {e}")