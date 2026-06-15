# net_utils.py
import socket
import struct

def ip2int(addr):
    """Zamiana adresu IP w formie tekstu (np. '192.168.1.1') na 32-bitową liczbę"""
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def proto2int(proto_str):
    """Tłumaczenie nazwę protokołu na jego oficjalny numer IANA (TCP=6, UDP=17)"""
    if proto_str.upper() == "TCP": return 6
    elif proto_str.upper() == "UDP": return 17
    elif proto_str.upper() == "ICMP": return 1
    else: return 0

def flow_to_128bit(flow_str):
    """
    Fizyczny Parser 5-krotki. 
    Wejście: np. "192.168.0.1:80-10.0.0.1:443-TCP"
    Wyjście: 128-bitowa liczba całkowita odpowiadająca magistrali w Verilogu.
    """
    # Rozdzielenie tekstu na fragmenty
    parts = flow_str.split('-')
    ip_src_str, port_src_str = parts[0].split(':')
    ip_dst_str, port_dst_str = parts[1].split(':')
    proto_str = parts[2]

    # Konwersja na liczby naturalne
    ip_src = ip2int(ip_src_str)       # 32 bity
    ip_dst = ip2int(ip_dst_str)       # 32 bity
    port_src = int(port_src_str)      # 16 bitów
    port_dst = int(port_dst_str)      # 16 bitów
    proto = proto2int(proto_str)      # 8 bitów

    # Konkatenacja bitowa (Sklejanie drutów)
    # [ip_src: 32b][ip_dst: 32b][port_src: 16b][port_dst: 16b][proto: 8b][puste: 24b]
    flow_128 = (ip_src << 96) | (ip_dst << 64) | (port_src << 48) | (port_dst << 32) | (proto << 24)
    
    return flow_128

def hw_hash(data_in: int, out_width: int = 17, seed: int = 0x12345678) -> int:
    """
    Bit-dokładny model sprzętowego algorytmu ARX (Add-Rotate-XOR)
    kompatybilny ze zaktualizowanym modułem hw_hash.v.
    """
    # Maska wymuszająca sprzętowe zachowanie rejestru 32-bitowego (overflow)
    MASK_32 = 0xFFFFFFFF
    
    # 1. Cięcie 128-bitowego ID na cztery 32-bitowe bloki
    c0 = data_in & MASK_32
    c1 = (data_in >> 32) & MASK_32
    c2 = (data_in >> 64) & MASK_32
    c3 = (data_in >> 96) & MASK_32

    # 2. Wyliczanie mix1 (Dodawanie ARX)
    # W Verilogu: c0 + (c1 << 5) + (c1 >> 3) + SEED
    # W Pythonie każda suma i lewe przesunięcie muszą być zamaskowane!
    mix1 = (c0 + ((c1 << 5) & MASK_32) + (c1 >> 3) + seed) & MASK_32
    
    # 3. Wyliczanie mix2
    # W Verilogu: c2 + (c3 << 7) + (c3 >> 2) + (SEED ^ 32'hDEADBEEF)
    mix2 = (c2 + ((c3 << 7) & MASK_32) + (c3 >> 2) + (seed ^ 0xDEADBEEF)) & MASK_32
    
    # 4. Finalne mieszanie (tylko operacje XOR)
    # W Verilogu: mix1 ^ mix2 ^ (mix1 << 11) ^ (mix2 >> 5)
    final_mix = mix1 ^ mix2 ^ ((mix1 << 11) & MASK_32) ^ (mix2 >> 5)
    
    # 5. Obcięcie wyniku do żądanej szerokości wyjściowej (np. 17 bitów)
    out_mask = (1 << out_width) - 1
    hash_out = final_mix & out_mask
    
    return hash_out
