import json

NUM_HOSTS = 10000

def generate_authorized_hosts():
    hosts = []
    for i in range(NUM_HOSTS):
        octet3 = i // 256
        octet4 = i % 256
        flow = f"192.168.{octet3}.{octet4}:80-10.0.0.1:443-TCP"
        hosts.append(flow)
    return hosts

if __name__ == "__main__":
    hosts = generate_authorized_hosts()
    with open("authorized_hosts.json", "w") as f:
        json.dump(hosts, f)
    print(f"Wygenerowano {len(hosts)} autoryzowanych adresów.")