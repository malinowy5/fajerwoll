import json
from importlib import import_module
firewall_module = import_module("firewall")

if __name__ == "__main__":
    print("[*] Ładowanie pamięci RAM i danych testowych")
    with open("mem_bloom.json", "r") as f: bloom_mem = json.load(f)
    with open("mem_cuckoo.json", "r") as f: cuckoo_mem = json.load(f)
    with open("test_traffic.json", "r") as f: traffic = json.load(f)

    fw = firewall_module.FPGA_Firewall(bloom_mem, cuckoo_mem)

    passed = 0
    l1_drops = 0
    l2_drops = 0
    
    print("\n--- ROZPOCZĘCIE SYMULACJI RUCHU ---")
    for test in traffic:
        flow = test["flow"]
        expected = test["expected"]
        
        result = fw.process_packet(flow)
        
        if result["decision"] == expected:
            passed += 1
            if result["layer"] == 1 and result["decision"] == "DROP":
                l1_drops += 1
                print(f"[!] Opuszczono pakiet: {flow} w warstwie L1")
            if result["layer"] == 2 and result["decision"] == "DROP": 
                l2_drops += 1
                print(f"[!] Opuszczono pakiet: {flow} w warstwie L2")
            if result["decision"] == "FORWARD":
                print(f"[!] Przepuszczono pakiet: {flow}")
        else:
            print(f"[BŁĄD] Pakiet: {flow} | Oczekiwano: {expected} | Otrzymano: {result['decision']} ({result['reason']})")

    print(f"Pomyślnie zweryfikowane: {passed}/{len(traffic)}")
    print(f"Zatrzymane na Layer 1 (Bloom): {l1_drops}")
    print(f"Zatrzymane na Layer 2 (False Positives z L1): {l2_drops}")