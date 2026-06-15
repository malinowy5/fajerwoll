module layer2_cuckoo (
    input wire clk,
    input wire valid_in,
    input wire hint_in,
    input wire [127:0] flow_id_in,
    input wire [12:0] addr0, addr1, addr2,
    
    output wire final_allow,
    output wire valid_out
);

    // 3x RAM
    (* ramstyle = "M9K" *) reg [127:0] bank_0 [0:8191];
    (* ramstyle = "M9K" *) reg [127:0] bank_1 [0:8191];
    (* ramstyle = "M9K" *) reg [127:0] bank_2 [0:8191];

    initial begin
        $readmemh("cuckoo_bank0.mem", bank_0);
        $readmemh("cuckoo_bank1.mem", bank_1);
        $readmemh("cuckoo_bank2.mem", bank_2);
    end

    reg [127:0] rdata_0, rdata_1, rdata_2;
    reg [127:0] flow_id_reg;
    reg hint_reg;
    reg valid_delay;

    always @(posedge clk) begin
        rdata_0 <= bank_0[addr0];
        rdata_1 <= bank_1[addr1];
        rdata_2 <= bank_2[addr2];
        
        // Opoznienie
        flow_id_reg <= flow_id_in;
        hint_reg <= hint_in;
        valid_delay <= valid_in;
    end

    // Decyzje L2
    wire match0 = (rdata_0 == flow_id_reg);
    wire match1 = (rdata_1 == flow_id_reg);
    wire match2 = (rdata_2 == flow_id_reg);

    // Koncowa decyzja
    assign final_allow = hint_reg & (match0 | match1 | match2);
    assign valid_out = valid_delay;

endmodule