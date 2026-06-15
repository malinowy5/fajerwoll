module fajerwoll (
    input wire clk,
    input wire valid_in,
    input wire [127:0] incoming_flow_id,
    
    output wire firewall_decision,
    output wire decision_valid
);

    
    wire [16:0] b_h0, b_h1, b_h2, b_h3, b_h4;
    wire [12:0] c_h0, c_h1, c_h2;

    // Obliczanie adresów

    hw_hash #(.OUT_WIDTH(17), .SEED(32'hCAFEBABE)) hb0(.data_in(incoming_flow_id), .hash_out(b_h0));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'hDEADBEEF)) hb1(.data_in(incoming_flow_id), .hash_out(b_h1));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'h8BADF00D)) hb2(.data_in(incoming_flow_id), .hash_out(b_h2));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'h0DEFACED)) hb3(.data_in(incoming_flow_id), .hash_out(b_h3));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'hBADDCAFE)) hb4(.data_in(incoming_flow_id), .hash_out(b_h4));

    hw_hash #(.OUT_WIDTH(13), .SEED(32'hFEEDFACE)) hc0(.data_in(incoming_flow_id), .hash_out(c_h0));
    hw_hash #(.OUT_WIDTH(13), .SEED(32'hC0FFEE00)) hc1(.data_in(incoming_flow_id), .hash_out(c_h1));
    hw_hash #(.OUT_WIDTH(13), .SEED(32'h1CEB00DA)) hc2(.data_in(incoming_flow_id), .hash_out(c_h2));

    // L1 i opoznienie o 1 cykl dla L2
    wire l1_hint, l1_valid;
    
    layer1_bloom u_l1 (
        .clk(clk),
        .valid_in(valid_in),
        .hash0(b_h0), .hash1(b_h1), .hash2(b_h2), .hash3(b_h3), .hash4(b_h4),
        .hint_verify(l1_hint),
        .valid_out(l1_valid)
    );

    // Opoznienie
    reg [127:0] flow_id_sync;
    reg [12:0] c_h0_sync, c_h1_sync, c_h2_sync;

    always @(posedge clk) begin
        flow_id_sync <= incoming_flow_id;
        c_h0_sync <= c_h0;
        c_h1_sync <= c_h1;
        c_h2_sync <= c_h2;
    end

    // L2
    layer2_cuckoo u_l2 (
        .clk(clk),
        .valid_in(l1_valid),
        .hint_in(l1_hint),
        .flow_id_in(flow_id_sync),
        .addr0(c_h0_sync), .addr1(c_h1_sync), .addr2(c_h2_sync),
        .final_allow(firewall_decision),
        .valid_out(decision_valid)
    );

endmodule