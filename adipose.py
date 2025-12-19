import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

# تابع انتخاب فایل‌ها و مسیرها
def select_blank_file():
    path = filedialog.askopenfilename(
        title="فایل بلانک را انتخاب کنید",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    entry_blank.delete(0, tk.END)
    entry_blank.insert(0, path)

def select_sample_files():
    paths = filedialog.askopenfilenames(
        title="فایل‌های نمونه را انتخاب کنید",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    entry_samples.delete(0, tk.END)
    entry_samples.insert(0, ";".join(paths))

def select_output_folder():
    folder = filedialog.askdirectory(title="پوشه خروجی را انتخاب کنید")
    entry_output.delete(0, tk.END)
    entry_output.insert(0, folder)

# تابع بررسی شباهت با تلورانس درصدی
def is_similar(m1, m2, tolerance_percent=0.5):
    return abs(m1 - m2) / max(m1, m2) * 100 <= tolerance_percent

# تابع گروه‌بندی جرم‌ها با تلورانس ۰.۵٪ و گرفتن میانگین
def group_masses_with_mean(masses, tolerance_percent=0.5):
    masses = sorted(list(set(masses)))
    grouped = []
    current_group = [masses[0]]

    for m in masses[1:]:
        if is_similar(m, current_group[-1], tolerance_percent):
            current_group.append(m)
        else:
            grouped.append(sum(current_group) / len(current_group))
            current_group = [m]
    grouped.append(sum(current_group) / len(current_group))
    return grouped

# تابع اصلی پردازش
def process_files():
    blank_path = entry_blank.get()
    sample_paths = entry_samples.get().split(";")
    output_dir = entry_output.get()

    if not blank_path or not sample_paths or sample_paths == ['']:
        messagebox.showerror("خطا", "لطفاً فایل بلانک و فایل‌های نمونه را انتخاب کنید.")
        return
    if not output_dir:
        messagebox.showerror("خطا", "لطفاً مسیر خروجی را انتخاب کنید.")
        return

    try:
        min_count = simpledialog.askinteger(
            "تعداد حداقل فایل‌ها",
            "جرم باید در چند فایل وجود داشته باشد تا پذیرفته شود؟ (مثلاً ۵)",
            minvalue=1, maxvalue=len(sample_paths)
        )
        if not min_count:
            return

        # --- خواندن بلانک ---
        blank_df = pd.read_excel(blank_path)
        blank_masses = blank_df.iloc[:, 0].dropna().astype(float).tolist()
        blank_masses = group_masses_with_mean(blank_masses, 0.5)

        cleaned_lists = []

        for path in sample_paths:
            df = pd.read_excel(path)
            sample_masses = df.iloc[:, 0].dropna().astype(float).tolist()
            sample_masses = group_masses_with_mean(sample_masses, 0.5)

            # حذف جرم‌های مشابه با بلانک
            cleaned = []
            for m in sample_masses:
                if not any(is_similar(m, b, 0.5) for b in blank_masses):
                    cleaned.append(m)

            # دوباره میانگین‌گیری بعد از حذف بلانک
            cleaned = group_masses_with_mean(cleaned, 0.5)
            cleaned_lists.append(cleaned)

            base_name = os.path.splitext(os.path.basename(path))[0]
            out_path = os.path.join(output_dir, f"{base_name}_minus_Blank.xlsx")
            pd.DataFrame(sorted(cleaned), columns=["Mass"]).to_excel(out_path, index=False)

        # --- یافتن جرم‌های مشترک ---
        all_masses = sorted(set(sum(cleaned_lists, [])))
        grouped_masses = group_masses_with_mean(all_masses, 0.5)

        result = []
        for mean_mass in grouped_masses:
            count = 0
            for s in cleaned_lists:
                if any(is_similar(mean_mass, x, 0.5) for x in s):
                    count += 1
            if count >= min_count:
                result.append((mean_mass, count))

        out_common = os.path.join(output_dir, f"Common_Masses_99.5_mean_min{min_count}.xlsx")
        pd.DataFrame(result, columns=["Mean Mass", "Count"]).to_excel(out_common, index=False)

        messagebox.showinfo(
            "✅ انجام شد",
            f"📂 مسیر خروجی: {output_dir}\n\n"
            f"📄 فایل جرم‌های منفی بلانک و فایل نهایی ذخیره شدند.\n\n"
            f"شباهت: ±۰.۵٪ | حداقل فایل: {min_count}"
        )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در پردازش: {e}")

# --- رابط گرافیکی ---
root = tk.Tk()
root.title("مقایسه فایل‌ها با بلانک (۹۹.۵٪ شباهت + میانگین جرم‌ها + مسیر خروجی)")

tk.Label(root, text="فایل بلانک:").grid(row=0, column=0, padx=5, pady=5)
entry_blank = tk.Entry(root, width=60)
entry_blank.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="انتخاب", command=select_blank_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="فایل‌های نمونه:").grid(row=1, column=0, padx=5, pady=5)
entry_samples = tk.Entry(root, width=60)
entry_samples.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="انتخاب", command=select_sample_files).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="پوشه خروجی:").grid(row=2, column=0, padx=5, pady=5)
entry_output = tk.Entry(root, width=60)
entry_output.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="انتخاب", command=select_output_folder).grid(row=2, column=2, padx=5, pady=5)

tk.Button(root, text="شروع پردازش", command=process_files, bg="#4CAF50", fg="white", width=25).grid(row=3, column=1, pady=15)

root.mainloop()
