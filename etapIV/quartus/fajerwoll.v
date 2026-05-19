module fajerwoll #(
    parameter FLOW_WIDTH = 128
)(
    input wire clk,
    input wire rst,
    input wire valid_in,
    input wire [FLOW_WIDTH-1:0] incoming_flow_id,
    
    output wire firewall_decision,
    output wire decision_valid
);

    // STAGE 0: Zabezpieczenie przed opóźnieniami z samych pinów wejściowych FPGA
    reg [FLOW_WIDTH-1:0] in_flow;
    reg in_valid;
    always @(posedge clk) begin
        in_flow <= incoming_flow_id;
        in_valid <= valid_in;
    end

    // HASZE DLA L1 (Błyskawiczne)
    wire [16:0] b0, b1, b2, b3, b4;
    hw_hash #(.OUT_WIDTH(17), .SEED(32'hCAFEBABE)) h_b0 (.data_in(in_flow), .hash_out(b0));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'hDEADBEEF)) h_b1 (.data_in(in_flow), .hash_out(b1));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'h8BADF00D)) h_b2 (.data_in(in_flow), .hash_out(b2));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'h0DEFACED)) h_b3 (.data_in(in_flow), .hash_out(b3));
    hw_hash #(.OUT_WIDTH(17), .SEED(32'hBADDCAFE)) h_b4 (.data_in(in_flow), .hash_out(b4));

    // WARSTWA 1 (4 cykle latencji)
    wire l1_hint;
    wire l1_valid;
    layer1_bloom u_layer1 (
        .clk(clk), .valid_in(in_valid),
        .hash0(b0), .hash1(b1), .hash2(b2), .hash3(b3), .hash4(b4),
        .hint_verify(l1_hint), .valid_out(l1_valid)
    );

    // KASKADA OPÓŹNIAJĄCA DLA PAKIETU (Wyrównanie z 4-cyklowym Bloome'm)
    reg [FLOW_WIDTH-1:0] flow_d1, flow_d2, flow_d3, flow_d4;
    always @(posedge clk) begin
        flow_d1 <= in_flow;
        flow_d2 <= flow_d1;
        flow_d3 <= flow_d2;
        flow_d4 <= flow_d3; // Gotowe idealnie na czas werdyktu z L1
    end

    // HASZE DLA L2 (Liczone z opóźnionego pakietu!)
    wire [12:0] c0, c1, c2;
    hw_hash #(.OUT_WIDTH(13), .SEED(32'hFEEDFACE)) h_c0 (.data_in(flow_d4), .hash_out(c0));
    hw_hash #(.OUT_WIDTH(13), .SEED(32'hC0FFEE00)) h_c1 (.data_in(flow_d4), .hash_out(c1));
    hw_hash #(.OUT_WIDTH(13), .SEED(32'h1CEB00DA)) h_c2 (.data_in(flow_d4), .hash_out(c2));

    // WARSTWA 2 (5 cykli latencji)
    wire final_verdict;
    wire l2_valid;
    layer2_cuckoo u_layer2 (
        .clk(clk), .valid_in(l1_valid), .hint_in(l1_hint),        
        .flow_id_in(flow_d4), 
        .addr_bank0(c0), .addr_bank1(c1), .addr_bank2(c2),
        .final_allow(final_verdict), .valid_out(l2_valid)
    );

    assign firewall_decision = final_verdict;
    assign decision_valid = l2_valid;

endmodule