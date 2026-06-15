import json
import random

NUM_TESTS = 1000000

if __name__ == "__main__":
    random.seed(67)
    print("Ładowanie bazy autoryzowanych hostów...")
    with open("authorized_hosts.json", "r") as f:
        auth_hosts_list = json.load(f)
        
    auth_hosts_set = set(auth_hosts_list)
        
    test_traffic = []
    
    print(f"Generowanie {NUM_TESTS} pakietów testowych...")
    for _ in range(NUM_TESTS):
        # Symulujemy 50% szans na ruch poprawny i 50% na wrogi
        if random.choice([True, False]):
            # Ruch poprawny:
            pkt = random.choice(auth_hosts_list)
            test_traffic.append({"flow": pkt, "expected": "FORWARD"})
        else:
            # Ruch wrogi, losujemy dopóki pakietu nie ma w zaufanych: 
            while True:
                bad_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.0.1:80-10.0.0.1:443-TCP"
                
                
                if bad_ip not in auth_hosts_set:
                    break
                    
            test_traffic.append({"flow": bad_ip, "expected": "DROP"})
            
    with open("test_traffic.json", "w") as f:
        json.dump(test_traffic, f)
        
    print(f"Wygenerowano {NUM_TESTS} ramek testowych (gwarancja braku fałszywych wrogów!).")
