module layer1_bloom #(
    parameter ADDR_WIDTH = 17 
)(
    input wire clk,
    input wire valid_in,
    input wire [ADDR_WIDTH-1:0] hash0, hash1, hash2, hash3, hash4,
    
    output reg hint_verify,
    output reg valid_out
);

    (* ramstyle = "M9K" *) reg bloom_ram_0 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg bloom_ram_1 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg bloom_ram_2 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg bloom_ram_3 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg bloom_ram_4 [0:(1<<ADDR_WIDTH)-1];

    initial begin
        $readmemb("bloom_init.mem", bloom_ram_0);
        $readmemb("bloom_init.mem", bloom_ram_1);
        $readmemb("bloom_init.mem", bloom_ram_2);
        $readmemb("bloom_init.mem", bloom_ram_3);
        $readmemb("bloom_init.mem", bloom_ram_4);
    end

    // STAGE 1: Rejestracja adresów (Odcięcie od reszty logiki)
    reg [ADDR_WIDTH-1:0] r_h0, r_h1, r_h2, r_h3, r_h4;
    reg r_v1;
    always @(posedge clk) begin
        r_h0 <= hash0; r_h1 <= hash1; r_h2 <= hash2; r_h3 <= hash3; r_h4 <= hash4;
        r_v1 <= valid_in;
    end

    // STAGE 2: Odczyt z pamięci RAM
    reg b0, b1, b2, b3, b4;
    reg r_v2;
    always @(posedge clk) begin
        b0 <= bloom_ram_0[r_h0];
        b1 <= bloom_ram_1[r_h1];
        b2 <= bloom_ram_2[r_h2];
        b3 <= bloom_ram_3[r_h3];
        b4 <= bloom_ram_4[r_h4];
        r_v2 <= r_v1;
    end

    // STAGE 3: Bufor routingowy (pozwala sygnałom z różnych końców FPGA dojechać do bramki)
    reg b0_r, b1_r, b2_r, b3_r, b4_r;
    reg r_v3;
    always @(posedge clk) begin
        b0_r <= b0; b1_r <= b1; b2_r <= b2; b3_r <= b3; b4_r <= b4;
        r_v3 <= r_v2;
    end

    // STAGE 4: Bramka decyzyjna
    always @(posedge clk) begin
        hint_verify <= b0_r & b1_r & b2_r & b3_r & b4_r;
        valid_out <= r_v3;
    end

endmodule