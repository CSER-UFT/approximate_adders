# gerar_dados_8bits.py
with open("8bits_entries.txt", "w") as f:
    for a in range(256):
        for b in range(256):
            f.write(f"{a:02X} {b:02X}\n")