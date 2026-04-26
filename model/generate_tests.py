import json
import random

NUM_TESTS = 100000

if __name__ == "__main__":
    with open("authorized_hosts.json", "r") as f:
        auth_hosts = json.load(f)
        
    test_traffic = []
    
    for _ in range(NUM_TESTS):
        if random.choice([True, False]):
            # Ruch poprawny
            pkt = random.choice(auth_hosts)
            test_traffic.append({"flow": pkt, "expected": "FORWARD"})
        else:
            # Ruch wrogi (losowy IP)
            bad_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.0.1:80-10.0.0.1:443-TCP"
            test_traffic.append({"flow": bad_ip, "expected": "DROP"})
            
    with open("test_traffic.json", "w") as f:
        json.dump(test_traffic, f)
    print(f"Wygenerowano {NUM_TESTS} ramek testowych.")