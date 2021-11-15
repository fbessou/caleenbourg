import sys

in_file_name = sys.argv[1]  # input .srt file
out_file_name = sys.argv[2]  # output .txt file

print(f"In: {in_file_name}, Out: {out_file_name}")

with open(in_file_name, encoding = "ISO-8859-1") as in_f:
    with open(out_file_name, "w") as out_f:
        state = 0
        text = []
        lines_count = 0
        while True:
            line = in_f.readline()
            lines_count += 1
            if not line:
                break
            line = line[:-1]
            if state < 2:
                state += 1
            else:
                if not line:
                    if state != 3:
                        print(f"Invalid state at line {lines_count}")
                    out_f.write("\n".join(text) + "\n")
                    text = []
                    state = 0
                else:
                    line = line.replace("<i>", "").replace("</i>", "")
                    if line[0] == '-':
                        text.append(line[1:])
                    else:
                        if len(text) == 0:
                            text.append("")
                        text[-1] += " "+line
                    state = 3
