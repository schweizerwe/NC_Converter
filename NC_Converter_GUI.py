import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def get_axis_value(line, axis):
    match = re.search(rf'\b{axis}([-+]?\d+(?:\.\d*)?|[-+]?\.\d+)', line, re.IGNORECASE)
    return float(match.group(1)) if match else None

def has_g2_g3(line):
    return bool(re.search(r'\bG[23]\b', line, re.IGNORECASE))

def remove_g0_g1(line):
    return re.sub(r'\bG[01]\b', '', line, flags=re.IGNORECASE).strip()

def convert_nc_file(input_file):
    input_path = Path(input_file)
    output_file = input_path.with_suffix(".TAP")

    current_x = None
    current_z = None
    active_mode = None

    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8") as fout:

        for line in fin:
            raw = line.rstrip("\n")
            stripped = raw.strip()

            if not stripped:
                fout.write("\n")
                continue

            if stripped.startswith("(") or stripped == "%":
                fout.write(raw + "\n")
                continue

            if has_g2_g3(stripped):
                x = get_axis_value(stripped, "X")
                z = get_axis_value(stripped, "Z")
                if x is not None: current_x = x
                if z is not None: current_z = z
                fout.write(raw + "\n")
                continue

            x = get_axis_value(stripped, "X")
            z = get_axis_value(stripped, "Z")

            motion = None

            if z is not None and current_z is not None:
                if z > current_z:
                    motion = "G0"
                elif z < current_z:
                    motion = "G1"
            elif z is not None and current_z is None:
                motion = "G1"
            elif x is not None:
                motion = active_mode

            if motion:
                cleaned = remove_g0_g1(raw)

                if motion != active_mode:
                    parts = cleaned.split(maxsplit=1)
                    new_line = f"{parts[0]} {motion} {parts[1]}" if len(parts) == 2 else f"{motion} {cleaned}"
                    active_mode = motion
                else:
                    new_line = cleaned

                fout.write(new_line + "\n")
            else:
                fout.write(raw + "\n")

            if x is not None: current_x = x
            if z is not None: current_z = z

def start_gui():
    file_path = filedialog.askopenfilename(
        title="NC-Datei auswählen",
        filetypes=[("NC Dateien", "*.nc"), ("Alle Dateien", "*.*")]
    )

    if file_path:
        out = convert_nc_file(file_path)
        messagebox.showinfo("Fertig", f"TAP erstellt:\n{out}")

root = tk.Tk()
root.title("NC → TAP Konverter")
root.geometry("350x150")

btn = tk.Button(root, text="NC Datei auswählen", command=start_gui, height=2, width=25)
btn.pack(pady=40)

root.mainloop()