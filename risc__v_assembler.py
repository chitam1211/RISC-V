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
}

REGISTERS = {
    f"X{i}": {
        "binary": f"{i:05b}",  # Mã nhị phân 5 bit
        "value": 0            # Giá trị mặc định ban đầu
    }
    for i in range(32)
}

REGISTER_ALIAS = {
    "X0": "X0", "X1": "X1", "X2": "X2", "X3": "X3", "X4": "X4", 
    "X5": "X5", "X6": "X6", "X7": "X7", "X8": "X8", "X9": "X9", 
    "X10": "X10", "X11": "X11", "X12": "X12", "X13": "X13", "X14": "X14", 
    "X15": "X15", "X16": "X16", "X17": "X17", "X18": "X18", "X19": "X19", 
    "X20": "X20", "X21": "X21", "X22": "X22", "X23": "X23", "X24": "X24", 
    "X25": "X25", "X26": "X26", "X27": "X27", "X28": "X28", "X29": "X29", 
    "X30": "X30", "X31": "X31", 
    "ZERO": "X0", "RA": "X1", "SP": "X2", "GP": "X3", "TP": "X4", 
    "T0": "X5", "T1": "X6", "T2": "X7", "S0": "X8", "FP": "X8", 
    "S1": "X9", "A0": "X10", "A1": "X11", "A2": "X12", "A3": "X13", 
    "A4": "X14", "A5": "X15", "A6": "X16", "A7": "X17", "S2": "X18", 
    "S3": "X19", "S4": "X20", "S5": "X21", "S6": "X22", "S7": "X23", 
    "S8": "X24", "S9": "X25", "S10": "X26", "S11": "X27", "T3": "X28", 
    "T4": "X29", "T5": "X30", "T6": "X31",
}

# Hàm ánh xạ thanh ghi

def map_register(register_name):
    if register_name in REGISTER_ALIAS:
        return REGISTER_ALIAS[register_name]
    raise ValueError(f"Thanh ghi không hợp lệ: {register_name}")

# **Bước 2: Đọc file, loại bỏ chú thích và dòng trống**
def preprocess_file(input_file, temp_file):
    with open(input_file, "r", encoding="utf-8") as infile, open(temp_file, "w", encoding="utf-8") as outfile:
        lines = []
        for line in infile:
            # Loại bỏ chú thích (phần sau dấu #)
            line = line.split("#")[0].strip()
            # Chuyển tất cả các lệnh sang viết hoa
            line = line.upper()
            # Bỏ qua các dòng trống
            if not line:
                continue
            
            # Kiểm tra nếu dòng có label và lệnh trên cùng một hàng
            if re.match(r"^[A-Z_]\w*:", line):  # Dòng bắt đầu với nhãn
                label, _, instruction = line.partition(":")
                label = label.strip() + ":"  # Đảm bảo nhãn kết thúc bằng dấu ':'
                instruction = instruction.strip()

                lines.append(label)  # Ghi nhãn vào một dòng riêng
                if instruction:  # Nếu có lệnh sau nhãn, thêm lệnh vào dòng mới
                    lines.append(instruction)
            else:
                lines.append(line)

        # Ghi các dòng đã xử lý, ngăn dòng trống cuối
        outfile.write("\n".join(lines))
    print(f"Preprocessed file written to {temp_file}")
    print("------------------------------------------------------------------------------------------------------------------------")

# **Bước 3: Tìm bảng băm LABEL và địa chỉ tương ứng**
def find_labels(temp_file, nlb_file):
    labels = {}
    with open(temp_file, "r") as infile:
        lines = infile.readlines()

    # Mở file nlb_file để ghi
    with open(nlb_file, "w") as outfile:
        for idx, line in enumerate(lines, start = 1):
            stripped_line = line.strip()
            
            # Kiểm tra xem dòng có phải là label hay không
            if stripped_line.endswith(":"):  
                label = stripped_line.split(":")[0].strip()
                labels[label] = idx  # Lưu vị trí dòng của label
                outfile.write("\n")  # Ghi dòng trống vào file nlb_file
            else:
                outfile.write(line)  # Ghi dòng lệnh vào file nlb_file
    return labels
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

def normalize_operands(line):
    """
    Chuẩn hóa toán hạng: thêm dấu phẩy giữa các toán hạng nếu thiếu.
    Ví dụ: "LI A7 1" -> "LI A7, 1"
    """
    # Tìm lệnh và toán hạng
    match = re.match(r"^(\w+)\s+(.*)$", line)
    if not match:
        return line  # Trả về dòng gốc nếu không khớp

    instruction, operands = match.groups()
    
    # Thêm dấu phẩy nếu giữa các toán hạng chỉ có khoảng trắng
    normalized_operands = re.sub(r"\s+", ", ", operands.strip())
    return f"{instruction} {normalized_operands}"

# **Bước 5: Phân tách lệnh thành các trường**
def parse_instruction(nlb_file, line, labels, current_address):
    """
    Phân tích lệnh và trả về mã nhị phân.
    - line: dòng lệnh cần phân tích.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    - current_address: địa chỉ hiện tại của lệnh, dùng cho tính toán offset.
    """
    line = normalize_operands(line)

    parts = line.split(maxsplit=1)  # Tách chỉ instruction và phần còn lại
    instruction = parts[0]
    
    if len(parts) < 2:
        if instruction == "NOP":
            return "00000000000000000000000000010011"  # NOP mã máy
        raise ValueError(f"Lệnh {instruction} không hợp lệ hoặc thiếu toán hạng.")
    
    # Xử lý toán hạng: loại bỏ khoảng trắng và kiểm tra dấu phẩy
    operands = [op.strip() for op in parts[1].split(",") if op.strip()]
    
    # Xử lý lệnh giả
    if instruction == "LI":  # Load Immediate
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng.")
    
        rd = map_register(operands[0])
        imm = int(operands[1], 0)  # Chuyển immediate từ mọi định dạng
    
        if -2048 <= imm <= 2047:  # Immediate trong khoảng 12 bit
            # LI chuyển thành ADDI rd, x0, imm
            return parse_instruction(nlb_file, f"ADDI {rd}, ZERO, {imm}", labels, current_address)
        else:
            # LI với giá trị lớn hơn 12 bit cần LUI và ADDI
            upper = (imm + (1 << 11)) >> 12  # Làm tròn giá trị upper
            lower = imm - (upper << 12)     # Lấy phần còn lại (bù 2 đúng)

            # Kiểm tra nếu lower là số âm
            if lower < 0:
                lower &= 0xFFF  # Biểu diễn lower dưới dạng bù 2 (12 bit)
        
            instructions = [
                f"LUI {rd}, {upper}",
                f"ADDI {rd}, {rd}, {lower}"
            ]
            print(current_address)
            return [parse_instruction(nlb_file, instr, labels, current_address - idx * 4) 
                for idx, instr in enumerate(instructions)]

    elif instruction == "MV":  # Move (MV rd, rs) -> ADDI rd, rs, 0
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng.")
        rd = map_register(operands[0])
        rs = map_register(operands[1])
        return parse_instruction(f"ADDI {rd}, {rs}, 0", labels, current_address)
    # Xử lý lệnh BGT
    elif instruction == "BGT":  # Branch if Greater Than
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng.")
        
        rs1 = map_register(operands[0])
        rs2 = map_register(operands[1])
        label = operands[2]

        # Tính toán offset
        if label not in labels:
            raise ValueError(f"Nhãn {label} không được định nghĩa.")
        # Thay thế BGT bằng BLT với thanh ghi đảo ngược
        return parse_instruction(nlb_file, f"BLT {rs2}, {rs1}, {label}", labels, current_address)
    fmt = get_instruction_format(instruction)

    # Xử lý lệnh theo định dạng
    if fmt == "R":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[map_register(operands[0])]["binary"]
        rs1 = REGISTERS[map_register(operands[1])]["binary"]
        rs2 = REGISTERS[map_register(operands[2])]["binary"]
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        funct7 = FUNCT7[instruction]
        print(f"Lệnh: {instruction} | funct7: {funct7} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
        return f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "I":
        if instruction == "JALR":
            # Kiểm tra số lượng toán hạng và thiết lập giá trị mặc định
            rd, rs1, imm = "X1", None, 0  # Mặc định: rd = X1 (RA), imm = 0

            if len(operands) == 3:
                # Trường hợp đầy đủ: jalr rd, rs1, imm
                rd = map_register(operands[0].strip())
                rs1 = map_register(operands[1].strip())
                imm = int(operands[2].strip(), 0)
            elif len(operands) == 2:
                if "(" in operands[1]:
                # Trường hợp: jalr rd, imm(rs1)
                    rd = map_register(operands[0].strip())
                    imm_str, rs1_str = operands[1].split("(")
                    imm = int(imm_str.strip(), 0)
                    rs1 = map_register(rs1_str.strip(" )"))
                elif operands[1].isdigit() or (operands[1][0] == '-' and operands[1][1:].isdigit()):
                    # Trường hợp: jalr rs1, imm
                    rs1 = map_register(operands[0].strip())
                    imm = int(operands[1].strip(), 0)
            elif len(operands) == 1:
                # Trường hợp: jalr rs1 (chỉ có rs1, mặc định rd = X1, imm = 0)
                rs1 = map_register(operands[0].strip())
            else:
                raise ValueError(f"Lệnh {instruction} yêu cầu từ 1 đến 3 toán hạng nhưng có {len(operands)}.")

            # Kiểm tra giá trị immediate
            if imm < -2048 or imm > 2047:
                raise ValueError(f"Giá trị immediate vượt quá phạm vi: {imm} (phải trong [-2048, 2047])")
            imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển thành nhị phân 12 bit

            # Lấy mã nhị phân cho rd và rs1
            rd_bin = REGISTERS[rd]["binary"]
            rs1_bin = REGISTERS[rs1]["binary"]

            # Lấy opcode và funct3
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]

            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1_bin} | funct3: {funct3} | rd: {rd_bin} | opcode: {opcode}")
            return f"{imm_bin}{rs1_bin}{funct3}{rd_bin}{opcode}"
        elif instruction in ["LB", "LH", "LW", "LBU", "LHU"]:  # Lệnh dạng I với offset
            if len(operands) != 2:
                raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")

            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích

            # Tách offset và base trước khi ánh xạ
            operand_pattern = r"^\s*(-?\d+)\s*\(\s*(\w+)\s*\)$"
            match = re.match(operand_pattern, operands[1])

            if not match:
                raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")

            offset, base_alias = match.groups()

            # Ánh xạ base từ alias (ví dụ: A2 -> x12)
            base_register = map_register(base_alias)
            if base_register not in REGISTERS:
                raise ValueError(f"Thanh ghi {base_alias} không hợp lệ.")

            rs1 = REGISTERS[base_register]["binary"]

            # Xử lý offset và kiểm tra phạm vi
            try:
                imm = int(offset)
            except ValueError:
                raise ValueError(f"Offset không hợp lệ: {offset} phải là một số nguyên.")

            if not -2048 <= imm <= 2047:
                raise ValueError(f"Offset {imm} vượt quá phạm vi 12 bit: -2048 đến 2047.")

            imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển offset thành 12 bit

            # Lấy opcode và funct3
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]

            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

        elif instruction in ["SLLI", "SRLI", "SRAI"]:  # Lệnh dịch bit
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[map_register(operands[1])]["binary"]  # Đăng ký nguồn
            shamt = int(operands[2])  # Giá trị dịch
            shamt_bin = f"{shamt & 0x1F:05b}"  # 5 bit dịch (dành cho RV32I)
        
            if instruction == "SRAI":
                funct7 = "0100000"  # Giá trị cho SRAI
            else:
                funct7 = "0000000"  # Giá trị cho SLLI và SRLI
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            print(f"Lệnh: {instruction} | funct7: {funct7} | shamt_bin: {shamt_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{funct7}{shamt_bin}{rs1}{funct3}{rd}{opcode}"

        else:  # Lệnh I-format dạng hằng số
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[map_register(operands[1])]["binary"]  # Đăng ký nguồn
            imm = int(operands[2], 0)  # Chấp nhận cả số thập phân và hexa
            imm_bin = f"{imm & 0xFFF:012b}"  # Mask để đảm bảo chỉ 12 bit
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "S":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")

        # Lấy rs2 từ toán hạng thứ nhất
        rs2_alias = operands[0]
        rs2 = REGISTERS[map_register(rs2_alias)]["binary"]  # Đăng ký nguồn 2

        # Phân tích offset và base từ toán hạng thứ hai
        operand_pattern = r"^\s*(-?\d+)\s*\(\s*(\w+)\s*\)$"
        match = re.match(operand_pattern, operands[1])

        if not match:
            raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")

        offset, base_alias = match.groups()

        # Ánh xạ base alias sang dạng xN
        rs1 = map_register(base_alias)
        if rs1 not in REGISTERS:
            raise ValueError(f"Thanh ghi {base_alias} không hợp lệ.")

        rs1 = REGISTERS[rs1]["binary"]  # Đăng ký base đã chuyển đổi

        # Xử lý offset và phân chia thành 7 bit cao và 5 bit thấp
        try:
            imm = int(offset)
        except ValueError:
            raise ValueError(f"Offset không hợp lệ: {offset} phải là một số nguyên.")

        if not -2048 <= imm <= 2047:
            raise ValueError(f"Offset {imm} vượt quá phạm vi 12 bit: -2048 đến 2047.")

        imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển offset thành 12 bit nhị phân
        imm_high = imm_bin[:7]  # 7 bit cao
        imm_low = imm_bin[7:]   # 5 bit thấp

        # Lấy opcode và funct3
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]

        print(f"Lệnh: {instruction} | imm_high: {imm_high} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | imm_low: {imm_low} | opcode: {opcode}")
        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif fmt == "B":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
    
        # Lấy thông tin thanh ghi rs1 và rs2
        rs1 = REGISTERS[map_register(operands[0].strip())]["binary"]
        rs2 = REGISTERS[map_register(operands[1].strip())]["binary"]

        # Lấy thông tin nhãn và tính toán offset
        label = operands[2].strip()

        # Kiểm tra nhãn có tồn tại trong labels hay không
        if label not in labels:
            raise ValueError(f"Nhãn '{label}' không tồn tại trong bảng labels: {labels}")
        # Địa chỉ mục tiêu (target address) tính bằng byte
        target_address = labels[label] * 4  # Nhân với 4 để chuyển từ dòng sang byte
        # Tìm số dòng trống (nhãn) giữa current và target
        start = min(current_address // 4, target_address // 4)  # Lấy dòng nhỏ hơn
        end = max(current_address // 4, target_address // 4)    # Lấy dòng lớn hơn
        bts = 0
        with open(nlb_file, "r") as f:
            lines = f.readlines()
            for i in range(start, end):
                if not lines[i].strip():  # Dòng trống là nhãn
                    bts += 1
        # Kiểm tra hiu
        hiu = False
        if target_address // 4 < len(lines) - 1:  # Nếu nhãn không phải dòng cuối
            next_line = lines[target_address // 4 + 1].strip()
            if next_line:  # Nếu ngay sau nhãn có lệnh
                hiu = True
        # Tính offset
        if target_address > current_address:
            offset = (target_address - current_address)  - (bts * 4) + 4
        else:
            offset = (target_address - current_address)  + (bts * 4) + 4
        if offset < -4096 or offset > 4095:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^12 đến 2^12-1).")
        # Chuyển offset thành nhị phân (13 bit)
        imm_bin = f"{offset & 0x1FFF:013b}"
        print(f"Label to find: {label} | hiu: {hiu} | bts: {bts} | current_address: {current_address} | target_address: {target_address} | offset: {offset} | imm_bin: {imm_bin}")
        if offset < 0:
            imm_bin = imm_bin[:-1] + '1'  # Thay bit cuối thành 1
        # Sắp xếp lại các bit theo định dạng B
        imm_high = imm_bin[0] + imm_bin[2:8]  # Bit [12], [10:5]
        imm_low = imm_bin[8:]                # Bit [4:1], [11]
        # Tạo mã máy theo định dạng B
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        print(f"Lệnh: {instruction} | imm_high: {imm_high} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | imm_low: {imm_low} | opcode: {opcode}")
        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif fmt == "U":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[map_register(operands[0])]["binary"]
        imm = int(operands[1], 0)  # Immediate được lấy trực tiếp từ operands
        if imm >= 2**20 or imm < -(2**19):  # Kiểm tra giá trị immediate hợp lệ
            raise ValueError(f"Immediate {imm} vượt quá phạm vi 20 bit cho lệnh {instruction}.")
        imm_bin = f"{imm & 0xFFFFF:020b}"  # Mask để đảm bảo chỉ lấy 20 bit cao nhất
        opcode = OPCODES[instruction]
        print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rd: {rd} | opcode: {opcode}")
        return f"{imm_bin}{rd}{opcode}"

    elif fmt == "J":
        if len(operands) == 2:
            # Trường hợp đầy đủ: jal rd, label
            rd = REGISTERS[map_register(operands[0].strip())]["binary"]
            label_operand = operands[1].strip()
        elif len(operands) == 1:
            # Trường hợp thiếu rd: jal label (mặc định rd = RA hoặc X1)
            rd = REGISTERS[map_register("RA")]["binary"]  # RA là alias của X1
            label_operand = operands[0].strip()
        else:
            raise ValueError(f"Lệnh {instruction} yêu cầu 1 hoặc 2 toán hạng nhưng có {len(operands)}.")
        # Lấy thông tin nhãn
        label_info = labels.get(label_operand)
        if label_info is None:
            raise ValueError(f"Nhãn {label_operand} không tìm thấy.")
        target_address = label_info * 4  # Nhân với 4 để tính địa chỉ byte
        temp_file = r"E:\NCKH\risc  v assembler\temp.txt"
        # Tìm số dòng trống (nhãn) giữa current và target
        start = min(current_address // 4, target_address // 4)  # Lấy dòng nhỏ hơn
        end = max(current_address // 4, target_address // 4)    # Lấy dòng lớn hơn
        bts = 0
        with open(nlb_file, "r") as f:
            lines = f.readlines()
            for i in range(start, end):
                if not lines[i].strip():  # Dòng trống là nhãn
                    bts += 1
        if target_address > current_address:
            offset = (target_address - current_address)  - (bts * 4) + 4
        else:
            offset = (target_address - current_address)  + (bts * 4) + 4
        if offset < -1048576 or offset > 1048575:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^20 đến 2^20-1).")
        # Chuyển đổi offset thành nhị phân (20 bit)
        if offset < 0:
        # Nếu offset âm, thực hiện bù 2 với 21 bit (giữ bit dấu đúng ở đầu)
            offset_bin = f"{(offset + (1 << 21)) & 0x1FFFFF:021b}"
        else:
        # Nếu offset dương, trực tiếp chuyển thành 21 bit nhị phân
            offset_bin = f"{offset & 0x1FFFFF:021b}"
        print(f"offset: {offset}|current_address: {current_address} | target_address: {target_address} | label_info: {label_info} | bts: {bts} | offset_bin: {offset_bin}")
        imm20 = offset_bin[0]        # Bit thứ 20 (MSB)
        imm19_12 = offset_bin[1:9]   # Bit từ 19 đến 12 (8 bit)
        imm11 = offset_bin[9]        # Bit thứ 11
        imm10_1 = offset_bin[10:20]  # Bit từ 10 đến 1 (10 bit, bao gồm index 10 đến 19)
        opcode = OPCODES[instruction]
        print(f"Lệnh: {instruction} | imm20: {imm20} | imm10_1: {imm10_1} | imm11: {imm11} | imm19_12: {imm19_12} | rd: {rd} | opcode: {opcode}")
        return f"{imm20}{imm10_1}{imm11}{imm19_12}{rd}{opcode}"
    else:
        raise ValueError(f"Định dạng lệnh {instruction} không được hỗ trợ.")
# **Bước 6: Chuyển các trường thành chuỗi bit và lưu file**
def assemble(nlb_file, output_file, labels):
    """
    Dịch file assembler thành mã máy và lưu vào file output.
    - temp_file: file chứa các lệnh assembler đã xử lý (file nlb, có dòng trống cho labels).
    - output_file: file đầu ra chứa mã máy dưới dạng hex.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    """
    with open(nlb_file, "r") as infile, open(output_file, "w") as outfile:
        lines = infile.readlines()
        pc = 4  # Program counter (địa chỉ hiện tại, tính bằng byte, bắt đầu từ 0)

        for line in lines:
            line = line.strip()
            if not line:  # Nếu dòng trống, chỉ tăng PC, không xử lý lệnh
                pc += 4
                continue
            try:
                binary_instruction = parse_instruction(nlb_file, line, labels, pc)
                if isinstance(binary_instruction, list):  # Kiểm tra nếu kết quả là danh sách
                    for instr in binary_instruction:
                        outfile.write(instr + "\n")
                    pc += 4  # Tăng PC cho mỗi lệnh
                else:  # Nếu kết quả là chuỗi
                    outfile.write(binary_instruction + "\n")
                    pc += 4  # Tăng PC sau mỗi lệnh
            except ValueError as e:
                raise ValueError(f"Lỗi khi xử lý lệnh '{line}': {e}")
# **Bước 7: Chạy chương trình**
def main():
    input_file = r"E:\NCKH\risc  v assembler\input.txt"
    temp_file = r"E:\NCKH\risc  v assembler\temp.txt"
    nlb_file = r"E:\NCKH\risc  v assembler\no lb.txt"
    output_file = r"E:\NCKH\risc  v assembler\output.txt"
    # Xử lý file
    preprocess_file(input_file, temp_file)
    labels = find_labels(temp_file,nlb_file)
    print("Labels found:", labels)
    assemble(nlb_file, output_file, labels)
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Program has finished executing...")
if __name__ == "__main__":
    main()
