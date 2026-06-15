module hw_hash #(
    parameter OUT_WIDTH = 17,       
    parameter SEED = 32'h12345678   
)(
    input  wire [127:0] data_in,
    output wire [OUT_WIDTH-1:0] hash_out
);

    // Dzielimy pakiet na 4 słowa 32-bitowe
    wire [31:0] c0 = data_in[31:0];
    wire [31:0] c1 = data_in[63:32];
    wire [31:0] c2 = data_in[95:64];
    wire [31:0] c3 = data_in[127:96];

    // ARX, brak pętli w Cuckoo
    wire [31:0] mix1 = c0 + (c1 << 5) + (c1 >> 3) + SEED;
    wire [31:0] mix2 = c2 + (c3 << 7) + (c3 >> 2) + (SEED ^ 32'hDEADBEEF);
    
    wire [31:0] final_mix = mix1 ^ mix2 ^ (mix1 << 11) ^ (mix2 >> 5);

    // Obcięcie do rozmiaru pamięci
    assign hash_out = final_mix[OUT_WIDTH-1:0];

endmodule