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

# Create new columns for the desired calculations
data['plus1'] = data[target_column] + 1
data['plus2'] = (data[target_column] + 2) / 2
data['met loss1'] = data[target_column] - 130
data['met loss2'] = (data[target_column] - 129) / 2
data['ace1'] = data[target_column] + 44
data['ace2'] = (data[target_column] + 45) / 2

# Keep only the desired columns
desired_columns = ['plus1', 'plus2', 'met loss1', 'met loss2', 'ace1', 'ace2']
data = data[desired_columns]

# Transpose the DataFrame (convert rows to columns)
data = data.transpose()

# Reset the index of the DataFrame
data = data.reset_index()

# Assemble all columns into a single column
data = data.melt(id_vars='index', var_name='Column', value_name='Value')

# Keep only 'index' and 'Value' columns
data = data[['index', 'Value']]

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Ask the user to select the output directory
output_dir = filedialog.askdirectory()
if not output_dir:
    print("No directory selected. Exiting.")
    exit()

# Construct the output file path in the same directory as the script
# output_file_path = os.path.join(script_directory, f'{target_column}.csv')

os.system("cls" if os.name == "nt" else "clear")

# Save the data as a CSV file
data.to_csv(output_file_path, index=False)
print(f"✅ {target_column} Calculations Saved Successfully.")
print(f"✅ Data Saved In {output_file_path}")

input("\n❌ Press Any Key For Exit")