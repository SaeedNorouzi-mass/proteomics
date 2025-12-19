import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

def process_excel_files():
    root = tk.Tk()
    root.withdraw()

    # مرحله ۱: انتخاب چند فایل اکسل
    file_paths = filedialog.askopenfilenames(
        title="فایل‌های اکسل را انتخاب کنید",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_paths:
        messagebox.showinfo("لغو شد", "هیچ فایلی انتخاب نشد.")
        return

    # مرحله ۲: گرفتن آستانه شدت از کاربر
    try:
        threshold = simpledialog.askinteger("ورود مقدار", "شدت کمتر از چه عددی حذف شود؟ (مثلاً 500):", minvalue=0)
        if threshold is None:
            messagebox.showinfo("لغو شد", "مقداری وارد نشد.")
            return
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ورودی عدد: {e}")
        return

    # مرحله ۳: انتخاب مسیر خروجی
    output_dir = filedialog.askdirectory(title="مسیر ذخیره خروجی را انتخاب کنید")
    if not output_dir:
        messagebox.showinfo("لغو شد", "مسیر خروجی انتخاب نشد.")
        return

    # مرحله ۴: پردازش هر فایل
    for file_path in file_paths:
        try:
            df = pd.read_excel(file_path, header=None)

            if df.shape[1] < 2:
                messagebox.showwarning("خطا در فایل", f"فایل {os.path.basename(file_path)} حداقل دو ستون ندارد.")
                continue

            # تبدیل ستون دوم به عدد (number)
            df[1] = pd.to_numeric(df[1], errors='coerce')

            # حذف سطرهایی که شدت کمتر از threshold دارند
            df = df[df[1] >= threshold]

            # مرتب‌سازی از بیشترین به کمترین شدت
            df = df.sort_values(by=1, ascending=False)

            # تولید نام فایل خروجی
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(output_dir, f"{name}_{threshold}{ext}")

            # ذخیره فایل خروجی
            df.to_excel(output_path, index=False, header=False)

        except PermissionError:
            messagebox.showerror("خطا", f"فایل {os.path.basename(file_path)} باز است. لطفاً آن را ببندید و دوباره تلاش کنید.")
        except Exception as e:
            messagebox.showerror("خطا", f"در پردازش فایل {os.path.basename(file_path)} خطایی رخ داد:\n{e}")

    messagebox.showinfo("پایان", "همه فایل‌ها با موفقیت پردازش و ذخیره شدند.")

if __name__ == "__main__":
    process_excel_files()
