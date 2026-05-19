module hw_hash #(
    parameter OUT_WIDTH = 17,
    parameter SEED = 32'h12345678
)(
    input  wire [127:0] data_in,
    output wire [OUT_WIDTH-1:0] hash_out
);
    wire [31:0] chunk0 = data_in[31:0];
    wire [31:0] chunk1 = data_in[63:32];
    wire [31:0] chunk2 = data_in[95:64];
    wire [31:0] chunk3 = data_in[127:96];

    wire [31:0] mix1 = chunk0 ^ (chunk1 << 3) ^ SEED;
    wire [31:0] mix2 = chunk2 ^ (chunk3 >> 2) ^ (SEED << 7);
    wire [31:0] final_mix = mix1 ^ mix2 ^ (mix1 >> 11) ^ (mix2 << 5);

    assign hash_out = final_mix[OUT_WIDTH-1:0];
endmodule