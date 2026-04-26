import hashlib

def hw_hash(data_str, seed, max_val):
    h = hashlib.md5(f"{seed}_{data_str}".encode()).hexdigest()
    return int(h, 16) % max_val

class Layer1_BloomFilter:
    def __init__(self, bloom_ram):
        self.bloom_ram = bloom_ram
        self.bloom_size = len(bloom_ram)

    def process(self, flow_id):
        for i in range(5):
            idx = hw_hash(flow_id, i, self.bloom_size)
            if self.bloom_ram[idx] == 0:
                # Na pewno nie zaufany, odrzucamy
                return "DENY" 
                
        # Przechodzi L1, do weryfikacji w L2
        return "VERIFY"


class Layer2_CuckooHashing:
    def __init__(self, cuckoo_ram):
        self.cuckoo_ram = cuckoo_ram
        self.cuckoo_banks = len(cuckoo_ram)
        self.cuckoo_size = len(cuckoo_ram[0])

    def process(self, flow_id, hint):
        if hint == "DENY":
            return {"decision": "DROP", "layer": 1, "reason": "Not in Bloom Filter (Hint=DENY)"}

        for bank_idx in range(self.cuckoo_banks):
            addr = hw_hash(flow_id, bank_idx + 100, self.cuckoo_size)
            if self.cuckoo_ram[bank_idx][addr] == flow_id:
                return {"decision": "FORWARD", "layer": 2, "reason": "Exact Match Found"} # Pasuje, przepuszczamy
                
        # False positive w L1, opuszczamy
        return {"decision": "DROP", "layer": 2, "reason": "False Positive in L1 caught"}


class FPGA_Firewall:
    def __init__(self, bloom_ram, cuckoo_ram):
        # Inicjalizacja podmodułów
        self.layer1 = Layer1_BloomFilter(bloom_ram)
        self.layer2 = Layer2_CuckooHashing(cuckoo_ram)

    def process_packet(self, flow_id):
        l1_hint = self.layer1.process(flow_id)
        
        final_decision = self.layer2.process(flow_id, hint=l1_hint)
        
        return final_decision