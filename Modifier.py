import os
import pandas as pd
from tkinter import Tk, filedialog

# Create a Tkinter root window
root = Tk()
root.withdraw()

# Open a file browse dialog to select the CSV file
file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])

# Load data from CSV file
data = pd.read_csv(file_path)

# List the columns of the CSV file
columns = data.columns
print("Columns in the CSV file:")
for i, col in enumerate(columns):
    print(f"{i+1}. {col}")

# Prompt the user to select the target column (Y)
target_column_index = int(input("Select The Target Column: "))

# Get the target column name
target_column = columns[target_column_index - 1]

# Create a list to store the results
results = []

# For each original value, create pairs (original_value, modified_value)
for original_value in data[target_column]:
    # Original value is stored without any modification
    results.append(['Original', original_value, f'{original_value} + 1', original_value + 1])
    results.append(['Original', original_value, f'({original_value} + 2) / 2', (original_value + 2) / 2])
    results.append(['Original', original_value, f'{original_value} - 130', original_value - 130])
    results.append(['Original', original_value, f'({original_value} - 129) / 2', (original_value - 129) / 2])
    results.append(['Original', original_value, f'{original_value} + 44', original_value + 44])
    results.append(['Original', original_value, f'({original_value} + 45) / 2', (original_value + 45) / 2])

# Create DataFrame from results
result_df = pd.DataFrame(results, columns=['Criminal/Mass Type', 'Original Mass', 'Formula', 'Calculated Value'])

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Ask the user to select the output directory
output_dir = filedialog.askdirectory()
if not output_dir:
    print("No directory selected. Exiting.")
    exit()

# Construct the output file path
output_file_path = os.path.join(output_dir, f'{target_column}_with_original.csv')

os.system("cls" if os.name == "nt" else "clear")

# Save the data as a CSV file
result_df.to_csv(output_file_path, index=False)
print(f"✅ {target_column} Calculations Saved Successfully.")
print(f"✅ Data Saved In {output_file_path}")

input("\n❌ Press Any Key For Exit")