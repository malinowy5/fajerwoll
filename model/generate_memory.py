import json
import hashlib
import random

BLOOM_SIZE = 100000
BLOOM_HASH_COUNT = 5
CUCKOO_BANKS = 3
CUCKOO_SIZE = 8000
MAX_KICKS = 500

def hw_hash(data_str, seed, max_val):
    h = hashlib.md5(f"{seed}_{data_str}".encode()).hexdigest()
    return int(h, 16) % max_val

def build_memory(hosts):
    bloom_array = [0] * BLOOM_SIZE
    cuckoo_banks = [[None] * CUCKOO_SIZE for _ in range(CUCKOO_BANKS)]
    
    # Budowa Filtra Blooma
    for flow in hosts:
        for i in range(BLOOM_HASH_COUNT):
            idx = hw_hash(flow, i, BLOOM_SIZE)
            bloom_array[idx] = 1

    # Budowa Cuckoo Hashing
    for flow in hosts:
        current_flow = flow
        inserted = False
        for _ in range(MAX_KICKS):
            for bank_idx in range(CUCKOO_BANKS):
                addr = hw_hash(current_flow, bank_idx + 100, CUCKOO_SIZE)
                if cuckoo_banks[bank_idx][addr] is None:
                    cuckoo_banks[bank_idx][addr] = current_flow
                    inserted = True
                    break
            if inserted: break
            
            # Wypychanie
            kick_bank = random.randint(0, CUCKOO_BANKS - 1)
            kick_addr = hw_hash(current_flow, kick_bank + 100, CUCKOO_SIZE)
            evicted_flow = cuckoo_banks[kick_bank][kick_addr]
            cuckoo_banks[kick_bank][kick_addr] = current_flow
            current_flow = evicted_flow
            
        if not inserted:
            raise Exception(f"Błąd Cuckoo dla {flow}")

    return bloom_array, cuckoo_banks

if __name__ == "__main__":
    with open("authorized_hosts.json", "r") as f:
        hosts = json.load(f)
    
    bloom, cuckoo = build_memory(hosts)
    with open("mem_bloom.json", "w") as f: json.dump(bloom, f)
    with open("mem_cuckoo.json", "w") as f: json.dump(cuckoo, f)
    print("Wygenerowano pliki pamięci dla warstwy 1 i 2.")