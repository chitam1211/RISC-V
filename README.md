# RISC V

## Assembler dành cho các lệnh số nguyên 32 bit
- Thay thế 4 đường dẫn đến `input_file`, `output_file`, `temp_file`, `no lb file`, `data file` thành đường dẫn tương ứng trong máy.
- Output đang là phần `.text` (các lệnh mã máy 32 bit).
- Chạy file  `main.py` để biên dịch, kết quả mã máy được lưu ở file  `output.txt`, các biến được khai báo (.data) được lưu ở  `predeclared_data.txt`.

## Instruction Set Simulator dành cho Assembler số nguyên 32 bit
- Đầu vào chính là output của Assembler số nguyên 32 bit.
- Đầu ra là Data Memory (được lưu bằng lệnh `sw`), trong chương trình có lệnh in giá trị của register ra terminal.
- Chạy file  `simulator.py` để mô phỏng, đầu ra thể hiện ở  `DataMemory.txt` và lệnh in ra giá trị của Register.

## Assembler dành cho các lệnh matrix
- Ý tưởng: [XUANTIE-RV/riscv-matrix-extension-spec](https://github.com/XUANTIE-RV/riscv-matrix-extension-spec.git)
- Thay thế đường dẫn của `m input` và `m output` thành các đường dẫn tương ứng trong máy.
- Chạy file  `massembler.py` để biên dịch, kết quả mã máy được lưu ở  `m output.txt`.
