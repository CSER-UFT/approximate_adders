with open("./data/8bit_all.txt", "w") as f:
    f.write("\n".join(f"{a:02X} {b:02X}" for a in range(256) for b in range(256)))
