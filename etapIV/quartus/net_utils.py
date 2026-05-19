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

def hw_hash(data_128bit, seed, out_width):
    # Ekstrakcja 32-bitowych chunków
    chunk0 = (data_128bit) & 0xFFFFFFFF
    chunk1 = (data_128bit >> 32) & 0xFFFFFFFF
    chunk2 = (data_128bit >> 64) & 0xFFFFFFFF
    chunk3 = (data_128bit >> 96) & 0xFFFFFFFF

    # Zgodnie z Verilog: wire [31:0] mix1 = chunk0 ^ (chunk1 << 3) ^ SEED;
    mix1 = (chunk0 ^ ((chunk1 << 3) & 0xFFFFFFFF) ^ (seed & 0xFFFFFFFF)) & 0xFFFFFFFF
    
    # Zgodnie z Verilog: wire [31:0] mix2 = chunk2 ^ (chunk3 >> 2) ^ (SEED << 7);
    mix2 = (chunk2 ^ (chunk3 >> 2) ^ ((seed << 7) & 0xFFFFFFFF)) & 0xFFFFFFFF
    
    # Zgodnie z Verilog: wire [31:0] final_mix = mix1 ^ mix2 ^ (mix1 >> 11) ^ (mix2 << 5);
    final_mix = (mix1 ^ mix2 ^ (mix1 >> 11) ^ ((mix2 << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF
    
    # Obcięcie do wymaganej szerokości 
    mask = (1 << out_width) - 1
    return final_mix & mask
