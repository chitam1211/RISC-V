# RISC V

## Assembler dành cho các lệnh số nguyên 32 bit
- Thay thế các đường dẫn đến các file thành các đường dẫn trong máy:  
`input_file = r"E:\AI accelerator\Assembler\input.txt"`  
`data_file = r"E:\AI accelerator\Assembler\data.txt"`  
`temp_file = r"E:\AI accelerator\Assembler\temp.txt"`  
`nlb_file = r"E:\AI accelerator\Assembler\no lb.txt"`  
`output_file = r"E:\AI accelerator\Assembler\output.txt"`  
`data_memory_file = r"E:\AI accelerator\Assembler\DataMemory.txt"`
- Chạy file  `main.py` để biên dịch, kết quả mã máy được lưu ở file  `output.txt`, các biến được khai báo (.data) được lưu ở  `predeclared_data.txt`.

## Instruction Set Simulator dành cho Assembler số nguyên 32 bit
- Đầu vào chính là output của Assembler số nguyên 32 bit.
- Đầu ra là Data Memory (được lưu bằng lệnh `sw`), trong chương trình có lệnh in giá trị của register ra terminal.
- Chạy file  `simulator.py` để mô phỏng, đầu ra thể hiện ở  `DataMemory.txt` và lệnh in ra giá trị của Register.

## Assembler dành cho các lệnh matrix
- Ý tưởng: [XUANTIE-RV/riscv-matrix-extension-spec](https://github.com/XUANTIE-RV/riscv-matrix-extension-spec.git)
- Thay thế đường dẫn của `m input` và `m output` thành các đường dẫn tương ứng trong máy.
- Chạy file  `massembler.py` để biên dịch, kết quả mã máy được lưu ở  `m output.txt`.
