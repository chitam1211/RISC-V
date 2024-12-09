import re
# **Bước 1: Khai báo bảng băm OPCODE, REG và FUNCT**
OPCODES = {
    "ADD": "0110011",
    "SUB": "0110011",
    "ADDI": "0010011",
    "LUI": "0110111",
    "AUIPC": "0010111",
    "LB": "0000011",
    "LBU": "0000011",
    "LH": "0000011",
    "LHU": "0000011",
    "LW": "0000011",
    "SB": "0100011",
    "SH": "0100011",
    "SW": "0100011",
    "SLL": "0110011",
    "SLLI": "0010011",
    "SRL": "0110011",
    "SRLI": "0010011",
    "SRA": "0110011",
    "SRAI": "0010011",
    "XOR": "0110011",
    "XORI": "0010011",
    "OR": "0110011",
    "ORI": "0010011",
    "AND": "0110011",
    "ANDI": "0010011",
    "SLT": "0110011",
    "SLTI": "0010011",
    "SLTU": "0110011",
    "SLTIU": "0010011",
    "BEQ": "1100011",
    "BNE": "1100011",
    "BLT": "1100011",
    "BGE": "1100011",
    "BLTU": "1100011",
    "BGEU": "1100011",
    "JAL": "1101111",
    "JALR": "1100111",
    "SC.W": "0101111",
    "AMOSWAP.W": "0101111",
    "AMOADD.W": "0101111",
    "AMOXOR.W": "0101111",
    "AMOAND.W": "0101111",
    "AMOOR.W": "0101111",
    "AMOMIN.W": "0101111",
    "AMOMAX.W": "0101111",
    "AMOMINU.W": "0101111",
    "AMOMAXU.W": "0101111",

}

FUNCT3 = {
    "ADD": "000",
    "JALR": "000",
    "SUB": "000",
    "ADDI": "000",
    "LB": "000",
    "LBU": "100",
    "LH": "001",
    "LHU": "101",
    "LW": "010",
    "SB": "000",
    "SH": "001",
    "SW": "010",
    "SLL": "001",
    "SLLI": "001",
    "SRL": "101",
    "SRLI": "101",
    "SRA": "101",
    "SRAI": "101",
    "XOR": "100",
    "XORI": "100",
    "OR": "110",
    "ORI": "110",
    "AND": "111",
    "ANDI": "111",
    "SLT": "010",
    "SLTI": "010",
    "SLTU": "011",
    "SLTIU": "011",
    "BEQ": "000",
    "BNE": "001",
    "BLT": "100",
    "BGE": "101",
    "BLTU": "110",
    "BGEU": "111",
    "SC.W": "011",
    "AMOSWAP.W": "010",
    "AMOADD.W": "010",
    "AMOXOR.W": "010",
    "AMOAND.W": "010",
    "AMOOR.W": "010",
    "AMOMIN.W": "010",
    "AMOMAX.W": "010",
    "AMOMINU.W": "010",
    "AMOMAXU.W": "010",
}

FUNCT7 = {
    "ADD": "0000000",
    "SUB": "0100000",
    "SLL": "0000000",
    "SRL": "0000000",
    "SRA": "0100000",
    "AND": "0000000",
    "OR": "0000000",
    "XOR": "0000000",
    "SLT": "0000000",
    "SLTU": "0000000",
    "SC.W": "0000011",
    "AMOSWAP.W": "0000001",
    "AMOADD.W": "0000000",
    "AMOXOR.W": "0000100",
    "AMOAND.W": "0001100",
    "AMOOR.W": "0001000",
    "AMOMIN.W": "0010000",
    "AMOMAX.W": "0010100",
    "AMOMINU.W": "0011000",
    "AMOMAXU.W": "0011100"

}

REGISTERS = {
    f"x{i}": {
        "binary": f"{i:05b}",  # Mã nhị phân 5 bit
        "value": 0            # Giá trị mặc định ban đầu
    }
    for i in range(32)
}

# **Bước 2: Đọc file, loại bỏ chú thích và dòng trống**
def preprocess_file(input_file, temp_file):
    with open(input_file, "r", encoding="utf-8") as infile, open(temp_file, "w", encoding="utf-8") as outfile:
        lines = []
        for line in infile:
            # Loại bỏ chú thích (phần sau dấu #)
            line = line.split("#")[0].strip()
            # Bỏ qua các dòng trống
            if line:
                lines.append(line)
        # Ghi các dòng đã xử lý, ngăn dòng trống cuối
        outfile.write("\n".join(lines))
    print(f"Preprocessed file written to {temp_file}")

# **Bước 3: Tìm bảng băm LABEL và địa chỉ tương ứng**
def find_labels(temp_file):
    labels = {}
    with open(temp_file, "r") as infile:
        lines = infile.readlines()
        current_label = None

        for idx, line in enumerate(lines):
            # Kiểm tra xem dòng có phải là nhãn không (kết thúc bằng dấu :)
            if ":" in line:
                label = line.split(":")[0].strip()
                current_label = label
                labels[current_label] = {"start": idx, "end": None}  # Lưu vị trí bắt đầu nhãn
            elif current_label and (":" in line or idx == len(lines) - 1): 
                # Xác định điểm kết thúc nhãn khi gặp nhãn khác hoặc kết thúc file
                labels[current_label]["end"] = idx - 1 if ":" in line else idx
                current_label = None
        
        # Nếu nhãn cuối cùng chưa có "end", gán vị trí cuối file
        if current_label and labels[current_label]["end"] is None:
            labels[current_label]["end"] = len(lines) - 1

    return labels

def count_empty_labels_between(start_address, end_address, temp_file):
    """
    Đếm số nhãn trống giữa hai địa chỉ trong file tạm thời.
    start_address: Địa chỉ bắt đầu.
    end_address: Địa chỉ kết thúc.
    temp_file: Đường dẫn đến file tạm thời.
    """
    label_count = 0
    start = min(start_address, end_address)
    end = max(start_address, end_address)

    with open(temp_file, "r") as file:
        lines = file.readlines()

        # Lấy danh sách các địa chỉ theo thứ tự xuất hiện
        current_address = 0
        for line in lines:
            line = line.strip()
            if ":" in line and line.index(":") == len(line) - 1:  # Kiểm tra nhãn rỗng
                if start <= current_address < end:
                    label_count += 1
            current_address += 4  # Mỗi lệnh hoặc nhãn chiếm 4 byte

    return label_count

# **Bước 4: Xác định định dạng lệnh**
def get_instruction_format(instruction):
    r_format = ["ADD", "SUB", "SLL", "SRL", "SRA", "AND", "OR", "XOR", "SLT", "SLTU","SC.W","AMOSWAP.W","AMOADD.W","AMOXOR.W","AMOAND.W","AMOOR.W","AMOMIN.W","AMOMAX.W","AMOMINU.W","AMOMAXU.W"]
    i_format = ["ADDI", "SLTI", "SLTIU", "XORI", "ORI", "ANDI", "LB", "LH", "LW", "LBU", "LHU", "JALR","SLLI","SRLI","SRAI"]
    s_format = ["SB", "SH", "SW"]
    b_format = ["BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU"]
    u_format = ["LUI", "AUIPC"]
    j_format = ["JAL"]

    if instruction in r_format:
        return "R"
    elif instruction in i_format:
        return "I"
    elif instruction in s_format:
        return "S"
    elif instruction in b_format:
        return "B"
    elif instruction in u_format:
        return "U"
    elif instruction in j_format:
        return "J"
    else:
        return None
  
# **Bước 5: Phân tách lệnh thành các trường**
def parse_instruction(line, labels, current_address):
    """
    Phân tích lệnh và trả về mã nhị phân.
    - line: dòng lệnh cần phân tích.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    - current_address: địa chỉ hiện tại của lệnh, dùng cho tính toán offset.
    """
    parts = line.split(maxsplit=1)  # Tách chỉ instruction và phần còn lại
    instruction = parts[0]
    
    if len(parts) < 2:
        if instruction == "NOP":
            return "00000000000000000000000000000011"  # NOP mã máy
        raise ValueError(f"Lệnh {instruction} không hợp lệ hoặc thiếu toán hạng.")
    
    # Xử lý toán hạng: loại bỏ khoảng trắng và kiểm tra dấu phẩy
    operands = [op.strip() for op in parts[1].split(",") if op.strip()]
    
    fmt = get_instruction_format(instruction)

    # Xử lý lệnh theo định dạng
    if fmt == "R":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[operands[0]]["binary"]
        rs1 = REGISTERS[operands[1]]["binary"]
        rs2 = REGISTERS[operands[2]]["binary"]
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        funct7 = FUNCT7[instruction]
        return f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "I":
        if instruction == "JALR":
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            # Kiểm tra định dạng và chuyển đổi toán hạng
            try:
                rd = REGISTERS[operands[0]]["binary"]  # Đăng ký đích
                rs1 = REGISTERS[operands[1]]["binary"]  # Đăng ký nguồn
                imm = int(operands[2], 0)  # Giá trị hằng số (có thể là thập phân hoặc hexa)
            except KeyError as e:
                raise ValueError(f"Đăng ký không hợp lệ: {e}")
            except ValueError as e:
                raise ValueError(f"Giá trị immediate không hợp lệ: {e}")

            # Đảm bảo immediate chỉ trong phạm vi 12 bit
            if imm < -2048 or imm > 2047:
                raise ValueError(f"Giá trị immediate vượt quá phạm vi: {imm} (phải trong [-2048, 2047])")
            imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển thành nhị phân 12 bit

            # Lấy opcode và funct3
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]

            # Mã hóa lệnh dạng I
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"
        elif instruction in ["LB", "LH", "LW", "LBU", "LHU"]:  # Lệnh dạng I với offset
            if len(operands) != 2:
                raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[operands[0]]["binary"]  # Đăng ký đích
            # Xử lý offset và base từ cú pháp offset(base)
            match = re.match(r"(-?\d+)\((x\d+)\)", operands[1])
            if not match:
                raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")
        
            imm = int(match.group(1))  # Lấy offset
            rs1 = REGISTERS[match.group(2)]["binary"]  # Lấy base
            imm_bin = f"{imm & 0xFFF:012b}"  # Mask để đảm bảo chỉ 12 bit
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"
        elif instruction in ["SLLI", "SRLI", "SRAI"]:  # Lệnh dịch bit
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[operands[0]]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[operands[1]]["binary"]  # Đăng ký nguồn
            shamt = int(operands[2])  # Giá trị dịch
            shamt_bin = f"{shamt & 0x1F:05b}"  # 5 bit dịch (dành cho RV32I)
        
            if instruction == "SRAI":
                funct7 = "0100000"  # Giá trị cho SRAI
            else:
                funct7 = "0000000"  # Giá trị cho SLLI và SRLI
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            return f"{funct7}{shamt_bin}{rs1}{funct3}{rd}{opcode}"

        else:  # Lệnh I-format dạng hằng số
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[operands[0]]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[operands[1]]["binary"]  # Đăng ký nguồn
            imm = int(operands[2], 0)  # Chấp nhận cả số thập phân và hexa
            imm_bin = f"{imm & 0xFFF:012b}"  # Mask để đảm bảo chỉ 12 bit
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "S":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")
    
        rs2 = REGISTERS[operands[0]]["binary"]  # Đăng ký nguồn 2
        # Xử lý offset và base từ cú pháp offset(base)
        match = re.match(r"(-?\d+)\((x\d+)\)", operands[1])
        if not match:
            raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")
    
        imm = int(match.group(1))  # Lấy offset
        rs1 = REGISTERS[match.group(2)]["binary"]  # Lấy base
        imm_bin = f"{imm & 0xFFF:012b}"  # Mask để đảm bảo chỉ 12 bit
        imm_high = imm_bin[:7]  # 7 bit cao của imm
        imm_low = imm_bin[7:]   # 5 bit thấp của imm
    
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif fmt == "B":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")

        rs1 = REGISTERS[operands[0].strip()]["binary"]
        rs2 = REGISTERS[operands[1].strip()]["binary"]

        # Lấy thông tin nhãn và tính toán offset
        label_info = labels.get(operands[2].strip())
        if label_info is None:
            raise ValueError(f"Nhãn {operands[2]} không tìm thấy.")

        target_address = label_info["start"] * 4  # Nhân với 4 để tính địa chỉ byte
        temp_file = r"E:\NCKH\risc  v assembler\temp.txt"  # Đảm bảo sử dụng raw string
        bts = count_empty_labels_between(current_address, target_address, temp_file)
        offset = (target_address - current_address) - bts * 4

        if offset < -4096 or offset > 4095:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^12 đến 2^12-1).")

        # Chuyển đổi offset thành nhị phân (13 bit)
        imm_bin = f"{offset & 0x1FFF:013b}"

        # Sắp xếp lại các bit theo định dạng B
        imm_high = imm_bin[0] + imm_bin[2:8]  # Bit [12], [10:5]
        imm_low = imm_bin[8:]   # Bit [4:1], [11]

        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]

        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"


    elif fmt == "U":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[operands[0]]["binary"]
        imm = int(operands[1], 0)  # Immediate được lấy trực tiếp từ operands
        if imm >= 2**20 or imm < -(2**19):  # Kiểm tra giá trị immediate hợp lệ
            raise ValueError(f"Immediate {imm} vượt quá phạm vi 20 bit cho lệnh {instruction}.")
        imm_bin = f"{imm & 0xFFFFF:020b}"  # Mask để đảm bảo chỉ lấy 20 bit cao nhất
        opcode = OPCODES[instruction]
        return f"{imm_bin}{rd}{opcode}"

    elif fmt == "J":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")

        rd = REGISTERS[operands[0].strip()]["binary"]
        label_info = labels.get(operands[1].strip())
        if label_info is None:
            raise ValueError(f"Nhãn {operands[1]} không tìm thấy.")

        target_address = label_info["start"] * 4  # Nhân với 4 để tính địa chỉ byte
        temp_file = r"E:\NCKH\risc  v assembler\temp.txt"
        bts = count_empty_labels_between(current_address, target_address, temp_file)
        offset = (target_address - current_address) - bts * 4 - 4


        if offset < -1048576 or offset > 1048575:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^20 đến 2^20-1).")

        # Chuyển đổi offset thành nhị phân (20 bit)
        offset_bin = f"{offset & 0xFFFFF:020b}"
        imm20 = offset_bin[0]        # Bit thứ 20 (MSB)
        imm19_12 = offset_bin[1:9]   # Bit từ 19 đến 12 (8 bit)
        imm11 = offset_bin[9]        # Bit thứ 11
        imm10_1 = offset_bin[10:20]  # Bit từ 10 đến 1 (10 bit, bao gồm index 10 đến 19)

        opcode = OPCODES[instruction]
        return f"{imm20}{imm10_1}{imm11}{imm19_12}{rd}{opcode}"
    else:
        raise ValueError(f"Định dạng lệnh {instruction} không được hỗ trợ.")

# **Bước 6: Chuyển các trường thành chuỗi bit và lưu file**

def assemble(temp_file, output_file, labels):
    """
    Dịch file assembler thành mã máy và lưu vào file output.
    - temp_file: file chứa các lệnh assembler đã xử lý.
    - output_file: file đầu ra chứa mã máy dưới dạng bin.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    """
    with open(temp_file, "r") as infile, open(output_file, "w") as outfile:
        lines = infile.readlines()
        pc = 0  # Program counter (địa chỉ hiện tại, tính bằng byte)

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.endswith(":"):  # Bỏ qua dòng trống hoặc nhãn
                continue

            parts = line.split(maxsplit=1)
            instruction = parts[0].upper()
            operands = parts[1].split(",") if len(parts) > 1 else []

            try:
                binary_instruction = parse_instruction(line, labels, pc)
                outfile.write(binary_instruction + "\n")
                pc += 4  # Tiến tới lệnh tiếp theo
            except ValueError as e:
                raise ValueError(f"Lỗi khi xử lý lệnh '{line}': {e}")

# **Bước 7: Chạy chương trình**
def main():
    input_file = r"E:\NCKH\risc  v assembler\input.txt"
    temp_file = r"E:\NCKH\risc  v assembler\temp.txt" 
    output_file = r"E:\NCKH\risc  v assembler\output.txt"
    # Xử lý file
    preprocess_file(input_file, temp_file)
    labels = find_labels(temp_file)
    assemble(temp_file, output_file, labels)

if __name__ == "__main__":
    main()
