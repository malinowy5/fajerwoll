import json
import random
from net_utils import flow_to_128bit, hw_hash

# --- PARAMETRY SPRZĘTOWE (Zgodne z Verilogiem) ---
BLOOM_SIZE = 131072       # 2^17
BLOOM_HASH_COUNT = 5
CUCKOO_BANKS = 3
CUCKOO_SIZE = 8192        # 2^13
MAX_KICKS = 50000

# Ziarna (Seeds) dokładnie takie same jak w aegis_zero_top.v
SEEDS_BLOOM = [0xCAFEBABE, 0xDEADBEEF, 0x8BADF00D, 0x0DEFACED, 0xBADDCAFE]
SEEDS_CUCKOO = [0xFEEDFACE, 0xC0FFEE00, 0x1CEB00DA]



def build_memory(hosts):
    bloom_array = [0] * BLOOM_SIZE
    cuckoo_banks = [[0] * CUCKOO_SIZE for _ in range(CUCKOO_BANKS)]
    
    print(f"Rozpoczynam haszowanie i budowanie struktur dla {len(hosts)} hostów...")

    # 1. Budowa Filtra Blooma (Layer 1)
    for flow in hosts:
        flow_128 = flow_to_128bit(flow)
        for i in range(BLOOM_HASH_COUNT):
            idx = hw_hash(flow_128, SEEDS_BLOOM[i], 17) # 17 bitów = 131072
            bloom_array[idx] = 1

    # 2. Budowa Cuckoo Hashing (Layer 2)
    for flow in hosts:
        current_flow_128 = flow_to_128bit(flow)
        inserted = False
        
        for _ in range(MAX_KICKS):
            # Próbujemy wstawić do jednego z 3 banków
            for bank_idx in range(CUCKOO_BANKS):
                addr = hw_hash(current_flow_128, SEEDS_CUCKOO[bank_idx], 13) # 13 bitów = 8192
                if cuckoo_banks[bank_idx][addr] == 0:
                    cuckoo_banks[bank_idx][addr] = current_flow_128
                    inserted = True
                    break
            
            if inserted:
                break
            
            # Wypychanie jeśli wszystkie miejsca są zajęte
            kick_bank = random.randint(0, CUCKOO_BANKS - 1)
            kick_addr = hw_hash(current_flow_128, SEEDS_CUCKOO[kick_bank], 13)
            
            evicted_flow = cuckoo_banks[kick_bank][kick_addr]
            cuckoo_banks[kick_bank][kick_addr] = current_flow_128
            current_flow_128 = evicted_flow
            
        if not inserted:
            raise Exception(f"Błąd krytyczny: Pętla nieskończona Cuckoo dla hosta {flow}. Zwiększ rozmiar banków!")

    return bloom_array, cuckoo_banks

def save_mem_files(bloom, cuckoo):
    """Zapisuje wygenerowane struktury do plików .mem dla Veriloga."""
    
    # Zapis Filtra Blooma 
    print("Zapisywanie bloom_init.mem...")
    with open("bloom_init.mem", "w") as f:
        for bit in bloom:
            f.write(f"{bit}\n")

    # Zapis Banków Cuckoo 
    for i in range(CUCKOO_BANKS):
        filename = f"cuckoo_bank{i}.mem"
        print(f"Zapisywanie {filename}...")
        with open(filename, "w") as f:
            for val in cuckoo[i]:
                # Formatowanie na 32 znaki HEX (128 bitów), wypełniamy zerami
                hex_str = f"{val:032x}" 
                f.write(f"{hex_str}\n")

if __name__ == "__main__":
    try:
        with open("authorized_hosts.json", "r") as f:
            hosts = json.load(f)
    except FileNotFoundError:
        print("Brak pliku authorized_hosts.json! Wygeneruj najpierw adresy.")
        exit(1)
    
    bloom_mem, cuckoo_mem = build_memory(hosts)
    save_mem_files(bloom_mem, cuckoo_mem)
    print("Gotowe! Pliki .mem można wgrać do symulacji FPGA.")
