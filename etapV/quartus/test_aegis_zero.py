import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.queue import Queue
import json
from net_utils import flow_to_128bit


async def scoreboard(dut, expected_queue, total_packets):
    received = 0
    while received < total_packets:
        await RisingEdge(dut.clk)
        
        # Jeśli FPGA wystawia werdykt
        if dut.decision_valid.value == 1:
            actual_decision = int(dut.firewall_decision.value)
            expected_decision = await expected_queue.get()
            
            # Porównujemy wynik
            assert actual_decision == expected_decision, \
                f"FAIL [Pakiet {received}]: Oczekiwano {expected_decision}, FPGA zwróciło {actual_decision}"
            
            received += 1
            
    dut._log.info(f"Scoreboard: Zweryfikowano bezbłędnie {total_packets} pakietów!")


@cocotb.test()
async def test_main_throughput(dut):
    
    cocotb.start_soon(Clock(dut.clk, 8, unit="ns").start())
    
    dut.valid_in.value = 0
    dut.incoming_flow_id.value = 0
    await ClockCycles(dut.clk, 5)
    
    dut._log.info("Wczytywanie wygenerowanego ruchu testowego...")
    with open("test_traffic.json", "r") as f:
        traffic_data = json.load(f)
        
    # Jak chcemy szybciej można wziąć mniej testów
    # traffic_subset = traffic_data[:10000]
    traffic_subset = traffic_data
    total_packets = len(traffic_subset)
    expected_queue = Queue()
    
    # Uruchomienie Scoreboarda w tle
    cocotb.start_soon(scoreboard(dut, expected_queue, total_packets))
    
    dut._log.info("Rozpoczęcie testu...")
    for item in traffic_subset:
        flow_int = flow_to_128bit(item["flow"])
        expected_val = 1 if item["expected"] == "FORWARD" else 0
        
        # Rejestrujemy w Scoreboardzie, czego ma się spodziewać
        await expected_queue.put(expected_val)
        
        # Wpychamy do FPGA
        dut.valid_in.value = 1
        dut.incoming_flow_id.value = flow_int
        await RisingEdge(dut.clk)
        
    # Zatrzymanie nadawania i czekanie na opróżnienie potoku (pipeline flush)
    dut.valid_in.value = 0
    await ClockCycles(dut.clk, 10)


@cocotb.test()
async def test_corner_cases(dut):
    cocotb.start_soon(Clock(dut.clk, 8, unit="ns").start())
    dut.valid_in.value = 0
    dut.incoming_flow_id.value = 0
    await ClockCycles(dut.clk, 5)
    
    expected_queue = Queue()
    
    # Testy brzegowe
    edge_cases = [
        0x00000000000000000000000000000000,
        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
        0xDEADDEADDEADDEADDEADDEADDEADDEAD 
    ]
    
    cocotb.start_soon(scoreboard(dut, expected_queue, len(edge_cases)))
    
    dut._log.info("Testowanie pakietów brzegowych i przerw w ruchu...")
    
    for pkt in edge_cases:
        await expected_queue.put(0) # Spodziewamy się DROP (0)
        
        dut.valid_in.value = 1
        dut.incoming_flow_id.value = pkt
        await RisingEdge(dut.clk)
        
        # Zatrzymujemy ruch na 5 cykli zegara
        dut.valid_in.value = 0
        await ClockCycles(dut.clk, 5) 
        
    await ClockCycles(dut.clk, 10)