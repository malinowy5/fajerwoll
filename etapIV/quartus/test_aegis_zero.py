import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly
import json
import hashlib
from net_utils import flow_to_128bit


@cocotb.test()
async def test_firewall_pipeline(dut):

    
    # 1. Odpalenie zegara 125 MHz (okres 8 ns)
    cocotb.start_soon(Clock(dut.clk, 8, units="ns").start())

    # 2. Inicjalizacja i Reset układu
    dut.rst.value = 1
    dut.valid_in.value = 0
    dut.incoming_flow_id.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)
    
    dut._log.info("Reset sprzętowy zakończony. Ładowanie danych wejściowych...")

    # 3. Pobranie paczek testowych z pliku (upewnij się, że masz test_traffic.json)
    try:
        with open("test_traffic.json", "r") as f:
            test_traffic = json.load(f)
    except FileNotFoundError:
        dut._log.error("Brak pliku test_traffic.json! Uruchom najpierw 4_generate_test_data.py")
        return

    passed = 0

    # 4. Uderzanie w FPGA symulowanym ruchem
    dut._log.info(f"Rozpoczynamy testowanie {len(test_traffic)} ramek...")
    
    for test in test_traffic:
        flow_str = test["flow"]
        expected_str = test["expected"]
        
        # Konwersja na bity sprzętowe i logikę (1 = ALLOW, 0 = DROP)
        flow_128bit = flow_to_128bit(flow_str)
        expected_bit = 1 if expected_str == "FORWARD" else 0

        # Wstrzyknięcie pakietu na wejście
        dut.valid_in.value = 1
        dut.incoming_flow_id.value = flow_128bit
        
                await RisingEdge(dut.clk)
        dut.valid_in.value = 0 
        

        timeout = 0
        while True:
            await ReadOnly() # Zczytuje stan po ustabilizowaniu się bramek
            if dut.decision_valid.value == 1:
                break
            
            await RisingEdge(dut.clk)
            timeout += 1
            if timeout > 10: # Bezpiecznik przed zawieszeniem pętli
                dut._log.error(f"Timeout rurociągu dla pakietu: {flow_str}")
                break

        # Ocena werdyktu podjętego przez druty i bramki FPGA
        actual_decision = dut.firewall_decision.value
        
        if actual_decision == expected_bit:
            passed += 1
            dut._log.info(f"[PASS] {flow_str} -> {expected_str}")
        else:
            dut._log.error(f"[FAIL] {flow_str} -> Oczekiwano {expected_bit}, otrzymano {actual_decision}")

       
        await RisingEdge(dut.clk)

    # 5. Podsumowanie
    dut._log.info(f"--- KONIEC SYMULACJI SPRZĘTOWEJ ---")
    dut._log.info(f"Przeszło: {passed} / {len(test_traffic)}")
    
    if passed == len(test_traffic):
        dut._log.info("Wszystkie testy przeszły")
