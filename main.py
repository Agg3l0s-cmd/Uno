def hex_to_wireshark_hexdump(hex_data):
    # Split the hex data into a list of bytes
    hex_bytes = hex_data.split()
    
    # Initialize variables for formatting
    hexdump = ""
    ascii_repr = ""
    row_size = 16  # Wireshark typically shows 16 bytes per row
    
    for i in range(0, len(hex_bytes), row_size):
        # Get the current offset
        offset = f"{i:04x}"
        
        # Get the current row of bytes
        row_bytes = hex_bytes[i:i + row_size]
        
        # Create the hex part of the row (pad with spaces for shorter rows)
        hex_part = " ".join(row_bytes).ljust(row_size * 3)
        
        # Create the ASCII part of the row
        for byte in row_bytes:
            # Convert each byte to its ASCII equivalent, or '.' if non-printable
            char = chr(int(byte, 16))
            ascii_repr += char if 32 <= ord(char) <= 126 else "."
        
        # Append the formatted row to the hexdump
        hexdump += f"{offset}  {hex_part}  {ascii_repr}\n"
        ascii_repr = ""  # Reset ASCII representation for the next row
    
    return hexdump.strip()


# Input hex data
hex_data = """
e4 77 23 a0 c8 cc f8 59 71 f1 26 9c 08 00 45 00
00 42 eb 70 00 00 80 11 cb e5 c0 a8 01 03 c0 a8
01 01 cf 81 00 35 00 2e 8e 98 a5 26 01 00 00 01
00 00 00 00 00 00 07 74 65 73 74 62 65 64 02 69
74 06 74 65 69 74 68 65 02 67 72 00 00 01 00 01
"""

# Generate and print the Wireshark-style hexdump
hexdump_output = hex_to_wireshark_hexdump(hex_data)
print(hexdump_output)
