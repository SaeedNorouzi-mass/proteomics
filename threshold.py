import csv
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def main():
    # Hide the root tkinter window
    root = tk.Tk()
    root.withdraw()

    # 1. Ask for input file
    input_file = filedialog.askopenfilename(
        title="Select the input text file (router file)",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not input_file:
        messagebox.showerror("Error", "No input file selected. Exiting.")
        return

    # 2. Ask for output CSV location
    output_file = filedialog.asksaveasfilename(
        title="Save filtered CSV as",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not output_file:
        messagebox.showerror("Error", "No output location selected. Exiting.")
        return

    # 3. Ask for starting row
    try:
        start_row = simpledialog.askinteger(
            "Starting row",
            "Enter the row number where the data starts (e.g., 2 or 3):",
            minvalue=1
        )
        if start_row is None:
            messagebox.showerror("Error", "Starting row not provided. Exiting.")
            return
    except Exception:
        messagebox.showerror("Error", "Invalid starting row.")
        return

    # 4. Ask for intensity threshold
    try:
        threshold = simpledialog.askfloat(
            "Intensity threshold",
            "Enter the intensity threshold (keep rows with intensity >= this value):",
            minvalue=0
        )
        if threshold is None:
            messagebox.showerror("Error", "Threshold not provided. Exiting.")
            return
    except Exception:
        messagebox.showerror("Error", "Invalid threshold.")
        return

    # Read and filter the file
    kept_rows = []
    current_row = 0

    try:
        with open(input_file, 'r') as infile:
            for line in infile:
                current_row += 1
                if current_row < start_row:
                    continue

                line = line.strip()
                if not line:
                    continue

                # Split by whitespace (space/tab) – adjust if needed
                parts = line.split()
                if len(parts) < 2:
                    print(f"Warning: Row {current_row} has fewer than 2 columns, skipping.")
                    continue

                try:
                    mass = float(parts[0])
                    intensity = float(parts[1])
                except ValueError:
                    print(f"Warning: Row {current_row} contains non-numeric data, skipping.")
                    continue

                if intensity >= threshold:
                    kept_rows.append([mass, intensity])

    except Exception as e:
        messagebox.showerror("File error", f"Could not read file:\n{e}")
        return

    # Write CSV output
    try:
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            # Uncomment next line if you want a header row:
            # writer.writerow(["Mass", "Intensity"])
            writer.writerows(kept_rows)
        messagebox.showinfo("Success", f"Saved {len(kept_rows)} rows to:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Write error", f"Could not save CSV:\n{e}")

if __name__ == "__main__":
    main()