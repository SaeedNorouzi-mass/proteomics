"""
compare_masses_excel.py

کارکرد:
- انتخاب چند فایل Excel (هر فایل: ستون اول شامل جرم‌ها، سطر اول نادیده گرفته می‌شود)
- گروه‌بندی مقادیر بر اساس دقت 99.5% (یعنی تفاوت نسبی <= 0.5%)
- خروجی:
    1) presence_matrix.xlsx : ماتریس حضور/عدم حضور (سطرها = جرم‌های نماینده، ستون‌ها = نام فایل‌ها)
    2) common_masses.xlsx : فقط جرم‌هایی که در بیش از یک فایل وجود دارند

نکات:
- این اسکریپت سعی می‌کند مقادیر ستون اول را به float تبدیل کند و مقادیر غیرقابل تبدیل را نادیده می‌گیرد.
- اگر می‌خواهید به‌جای 0/1 از Yes/No یا سایر قالب‌ها استفاده کنید، در قسمت ساخت DataFrame تغییر دهید.
"""

import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# تنظیم: آستانه نسبی = 0.5% -> برای دقت 99.5%
REL_TOL = 0.005  # 0.5%

def read_first_column_values(path):
    # خواندن اکسل، ستون اول، حذف سطر اول
    try:
        df = pd.read_excel(path, engine="openpyxl", header=None)
    except Exception as e:
        raise RuntimeError(f"خطا در خواندن فایل {path}: {e}")
    if df.shape[0] <= 1:
        return []
    col = df.iloc[1:, 0].astype(str).str.strip()  # exclude first row
    vals = []
    for v in col.values:
        if v in (None, "", "nan", "NaN"):
            continue
        # تلاش برای تبدیل به float (ممکن است ورودی با کاما باشد)
        s = str(v).replace(",", ".")
        try:
            f = float(s)
            if not math.isfinite(f):
                continue
            vals.append(f)
        except:
            # اگر مقدار قابل تبدیل نبود، نادیده می‌گیریم
            continue
    return vals

def cluster_masses(all_values, rel_tol=REL_TOL):
    """
    خوشه‌بندی مقادیر عددی بر اساس اختلاف نسبی.
    الگوریتم سادهٔ تک‌عبوری: ابتدا مقادیر را مرتب می‌کنیم،
    سپس یکی‌یکی اضافه می‌کنیم: اگر به میانگین خوشه فعلی بخوره (<= rel_tol) اضافه می‌شود،
    در غیر این صورت خوشهٔ جدیدی ساخته می‌شود.
    خروجی: لیست خوشه‌ها، هر خوشه لیستی از مقادیر است.
    """
    if not all_values:
        return []
    vals = sorted(all_values)
    clusters = []
    # نمایندهٔ هر خوشه: میانگین فعلی
    for v in vals:
        if not clusters:
            clusters.append([v])
            continue
        # میانگین خوشهٔ فعلی آخر
        cur = clusters[-1]
        mean_cur = sum(cur) / len(cur)
        # اختلاف نسبی نسبت به میانگین فعلی
        if abs(v - mean_cur) / mean_cur <= rel_tol:
            cur.append(v)
        else:
            # احتمال دارد v با خوشهٔ قبلی نخواند؛ اما ممکن است با خوشهٔ دیگری قبل‌تر بخونه.
            # برای دقت بیشتر، بهتر است جستجو در تمام خوشه‌ها انجام دهیم:
            placed = False
            for c in clusters:
                m = sum(c) / len(c)
                if abs(v - m) / m <= rel_tol:
                    c.append(v)
                    placed = True
                    break
            if not placed:
                clusters.append([v])
    return clusters

def representative_of_cluster(cluster):
    # طبق درخواست: برای مواردی که اختلاف در آستانه 0.5% هست، میانگین بگیرید
    return sum(cluster) / len(cluster)

def build_presence_matrix(clusters, file_values_dict, rel_tol=REL_TOL):
    # clusters: list of clusters (list of floats)
    # file_values_dict: {filename: [vals]}
    rows = []
    file_names = list(file_values_dict.keys())
    for cl in clusters:
        rep = representative_of_cluster(cl)
        row = {"mass": rep}
        for fn in file_names:
            vals = file_values_dict[fn]
            present = any(abs(v - rep) / rep <= rel_tol for v in vals)
            row[fn] = 1 if present else 0
        rows.append(row)
    df = pd.DataFrame(rows)
    # سطر اول باید نام فایل‌ها (در فایل اکسل header) — DataFrame همینطوری خواهد بود
    return df

def select_files_and_output_dir():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("انتخاب فایل‌ها", "در پنجره بعدی چند فایل اکسل انتخاب کنید (Ctrl/Shift برای انتخاب چندگانه). سطر اول هر فایل نادیده گرفته می‌شود.")
    file_paths = filedialog.askopenfilenames(title="Select Excel files", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_paths:
        raise SystemExit("هیچ فایلی انتخاب نشد. اجرا متوقف شد.")
    out_dir = filedialog.askdirectory(title="Select output folder")
    if not out_dir:
        raise SystemExit("هیچ پوشهٔ خروجی انتخاب نشد. اجرا متوقف شد.")
    return list(file_paths), out_dir

def main():
    try:
        files, out_dir = select_files_and_output_dir()
    except SystemExit as e:
        print(e)
        return
    except Exception as e:
        print("خطا در انتخاب فایل‌ها/پوشه:", e)
        return

    file_values = {}
    all_vals = []
    for f in files:
        try:
            vals = read_first_column_values(f)
        except Exception as e:
            print(f"خطا در خواندن {f}: {e}")
            vals = []
        file_values[os.path.basename(f)] = vals
        all_vals.extend(vals)

    if not all_vals:
        print("هیچ مقدار عددی‌ای در ستون اول فایل‌ها پیدا نشد.")
        return

    clusters = cluster_masses(all_vals, rel_tol=REL_TOL)

    presence_df = build_presence_matrix(clusters, file_values, rel_tol=REL_TOL)

    # مرتب‌سازی سطرها بر اساس جرم نماینده
    presence_df = presence_df.sort_values(by="mass").reset_index(drop=True)

    # نام فایل خروجی ها
    presence_path = os.path.join(out_dir, "presence_matrix.xlsx")
    common_path = os.path.join(out_dir, "common_masses.xlsx")

    # ساخت شیت خلاصه (presence). سطر اول: header با نام فایل‌ها؛ ستون اول: جرم
    # برای خوانایی بهتر، ستون جرم تا 6 رقم اعشار فرمت کنیم
    presence_df_display = presence_df.copy()
    presence_df_display["mass"] = presence_df_display["mass"].round(6)

    # ذخیره presence matrix
    try:
        with pd.ExcelWriter(presence_path, engine="openpyxl") as writer:
            presence_df_display.to_excel(writer, index=False, sheet_name="presence")
        print(f"فایل حضور/عدم حضور ذخیره شد: {presence_path}")
    except Exception as e:
        print("خطا در ذخیره presence matrix:", e)
        return

    # ایجاد فایل جدا برای جرم‌های مشترک (present in >= 2 files)
    file_cols = [c for c in presence_df.columns if c != "mass"]
    presence_df["n_files_present"] = presence_df[file_cols].sum(axis=1)
    common_df = presence_df[presence_df["n_files_present"] >= 2].copy()
    if not common_df.empty:
        common_df_display = common_df.drop(columns=["n_files_present"]).copy()
        common_df_display["mass"] = common_df_display["mass"].round(6)
        try:
            with pd.ExcelWriter(common_path, engine="openpyxl") as writer:
                common_df_display.to_excel(writer, index=False, sheet_name="common_masses")
            print(f"فایل جرم‌های مشترک ذخیره شد: {common_path}")
        except Exception as e:
            print("خطا در ذخیره common_masses:", e)
    else:
        print("هیچ جرمی که در بیش از یک فایل مشترک باشد پیدا نشد. فایل مشترک تولید نشد.")

if __name__ == "__main__":
    main()
