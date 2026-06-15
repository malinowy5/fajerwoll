module layer2_cuckoo #(
    parameter DATA_WIDTH = 128,
    parameter ADDR_WIDTH = 13 
)(
    input wire clk,
    input wire valid_in,
    input wire hint_in,               
    input wire [DATA_WIDTH-1:0] flow_id_in,
    
    input wire [ADDR_WIDTH-1:0] addr_bank0, addr_bank1, addr_bank2,
    
    output reg final_allow,
    output reg valid_out
);

    (* ramstyle = "M9K" *) reg [DATA_WIDTH-1:0] cuckoo_bank_0 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg [DATA_WIDTH-1:0] cuckoo_bank_1 [0:(1<<ADDR_WIDTH)-1];
    (* ramstyle = "M9K" *) reg [DATA_WIDTH-1:0] cuckoo_bank_2 [0:(1<<ADDR_WIDTH)-1];

    initial begin
        $readmemh("cuckoo_bank0.mem", cuckoo_bank_0);
        $readmemh("cuckoo_bank1.mem", cuckoo_bank_1);
        $readmemh("cuckoo_bank2.mem", cuckoo_bank_2);
    end

    // STAGE 1: Rejestracja wejść
    reg [ADDR_WIDTH-1:0] r_a0, r_a1, r_a2;
    reg [DATA_WIDTH-1:0] r_flow;
    reg r_hint, r_valid;
    always @(posedge clk) begin
        r_a0 <= addr_bank0; r_a1 <= addr_bank1; r_a2 <= addr_bank2;
        r_flow <= flow_id_in; r_hint <= hint_in; r_valid <= valid_in;
    end

    // STAGE 2: Odczyt z RAM
    reg [DATA_WIDTH-1:0] mem0, mem1, mem2, r_flow_d1;
    reg r_hint_d1, r_valid_d1;
    always @(posedge clk) begin
        mem0 <= cuckoo_bank_0[r_a0];
        mem1 <= cuckoo_bank_1[r_a1];
        mem2 <= cuckoo_bank_2[r_a2];
        r_flow_d1 <= r_flow; r_hint_d1 <= r_hint; r_valid_d1 <= r_valid;
    end

    // STAGE 3: Bufory dla grubych 128-bitowych szyn danych
    reg [DATA_WIDTH-1:0] mem0_r, mem1_r, mem2_r, flow_r;
    reg hint_r, valid_r;
    always @(posedge clk) begin
        mem0_r <= mem0; mem1_r <= mem1; mem2_r <= mem2; flow_r <= r_flow_d1;
        hint_r <= r_hint_d1; valid_r <= r_valid_d1;
    end

    // STAGE 4: Oddzielne 128-bitowe komparatory (ratuje Setup Time!)
    reg match0, match1, match2;
    reg hint_r2, valid_r2;
    always @(posedge clk) begin
        match0 <= (mem0_r == flow_r);
        match1 <= (mem1_r == flow_r);
        match2 <= (mem2_r == flow_r);
        hint_r2 <= hint_r; valid_r2 <= valid_r;
    end

    // STAGE 5: Ostateczna lekka decyzja logiczna
    always @(posedge clk) begin
        valid_out <= valid_r2;
        if (valid_r2 && hint_r2) begin
            final_allow <= match0 | match1 | match2;
        end else begin
            final_allow <= 1'b0;
        end
    end

endmodule