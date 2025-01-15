# **Bước 2: Đọc file, loại bỏ chú thích và dòng trống**
import re
def preprocess_file(input_file, temp_file):
    with open(input_file, "r", encoding="utf-8") as infile, open(temp_file, "w", encoding="utf-8") as outfile:
        lines = []
        for line in infile:
            # Loại bỏ chú thích (phần sau dấu #)
            stripped_line = line.strip()
            
            # Nếu dòng chỉ chứa chú thích
            if stripped_line.startswith("#"):
                lines.append("")  # Thêm một dòng trống
                continue
            
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
print("------------------------------------------------------------------------------------------------------------------------")