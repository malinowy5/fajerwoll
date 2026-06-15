module layer1_bloom (
    input wire clk,
    input wire valid_in,
    input wire [16:0] hash0, hash1, hash2, hash3, hash4,
    
    output wire hint_verify,
    output wire valid_out
);

    // 5x RAM
    (* ramstyle = "M9K" *) reg bloom_0 [0:131071];
    (* ramstyle = "M9K" *) reg bloom_1 [0:131071];
    (* ramstyle = "M9K" *) reg bloom_2 [0:131071];
    (* ramstyle = "M9K" *) reg bloom_3 [0:131071];
    (* ramstyle = "M9K" *) reg bloom_4 [0:131071];

    initial begin
        $readmemb("bloom_init.mem", bloom_0);
        $readmemb("bloom_init.mem", bloom_1);
        $readmemb("bloom_init.mem", bloom_2);
        $readmemb("bloom_init.mem", bloom_3);
        $readmemb("bloom_init.mem", bloom_4);
    end

    reg b0, b1, b2, b3, b4;
    reg valid_delay;

    always @(posedge clk) begin
        b0 <= bloom_0[hash0];
        b1 <= bloom_1[hash1];
        b2 <= bloom_2[hash2];
        b3 <= bloom_3[hash3];
        b4 <= bloom_4[hash4];
        
        valid_delay <= valid_in; // Opoznienie
    end

    // Weryfikacja wyniku z RAM
    assign hint_verify = b0 & b1 & b2 & b3 & b4;
    assign valid_out = valid_delay;

endmodule