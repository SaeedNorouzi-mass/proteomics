import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Define the amino acid masses
amino_acid_masses = {
    'A': {'monoisotopic': 71.03711, 'average': 71.0788},
    'R': {'monoisotopic': 156.10111, 'average': 156.1875},
    'N': {'monoisotopic': 114.04293, 'average': 114.1038},
    'D': {'monoisotopic': 115.02694, 'average': 115.0886},
    'C': {'monoisotopic': 103.00919, 'average': 103.1388},
    'E': {'monoisotopic': 129.04259, 'average': 129.1155},
    'Q': {'monoisotopic': 128.05858, 'average': 128.1307},
    'G': {'monoisotopic': 57.02146, 'average': 57.0519},
    'H': {'monoisotopic': 137.05891, 'average': 137.1411},
    'I': {'monoisotopic': 113.08406, 'average': 113.1594},
    'L': {'monoisotopic': 113.08406, 'average': 113.1594},
    'K': {'monoisotopic': 128.09496, 'average': 128.1741},
    'M': {'monoisotopic': 131.04049, 'average': 131.1926},
    'F': {'monoisotopic': 147.06841, 'average': 147.1766},
    'P': {'monoisotopic': 97.05276, 'average': 97.1167},
    'S': {'monoisotopic': 87.03203, 'average': 87.0782},
    'T': {'monoisotopic': 101.04768, 'average': 101.1051},
    'W': {'monoisotopic': 186.07931, 'average': 186.2132},
    'Y': {'monoisotopic': 163.06333, 'average': 163.1760},
    'V': {'monoisotopic': 99.06841, 'average': 99.1326},
    'O': {'monoisotopic': 237.1483, 'average': 237.303},
    'U': {'monoisotopic': 132.4936, 'average': 150.054}
}

# Define the mass of water
water_mass = {'monoisotopic': 18.01056, 'average': 18.01528}

# Function to calculate monoisotopic and average mass
def calculate_mass(sequence):
    monoisotopic_mass = 0
    average_mass = 0
    for aa in sequence:
        if aa in amino_acid_masses:
            monoisotopic_mass += amino_acid_masses[aa]['monoisotopic']
            average_mass += amino_acid_masses[aa]['average']
        else:
            print(f"Unknown amino acid '{aa}' in sequence: {sequence}")
    # Add the mass of water
    monoisotopic_mass += water_mass['monoisotopic']
    average_mass += water_mass['average']
    return monoisotopic_mass, average_mass

# Create a Tkinter root window (hidden)
root = Tk()
root.withdraw()  # Hide the root window

# Open a file dialog to select the input Excel file
input_file_path = askopenfilename(
    title="Select an Excel file",
    filetypes=[("Excel Files", "*.xlsx *.xls")]  # Filter for Excel files
)

# Check if the user canceled the file selection
if not input_file_path:
    print("No file selected. Exiting.")
    exit()

# Load the Excel file
try:
    df = pd.read_excel(input_file_path, header=None)  # Load without assuming headers
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    exit()

# Ask the user if the first row is a header
has_header = input("Does the first row contain headers? (yes/no): ").strip().lower()
if has_header in ['yes', 'y']:
    df.columns = df.iloc[0]  # Set the first row as the header
    df = df[1:]  # Drop the first row from the data

# Display available columns and ask the user to select one
print("Available columns:")
for i, col in enumerate(df.columns):
    print(f"{i + 1}: {col}")

try:
    col_index = int(input("Enter the number of the column containing amino acid sequences: ")) - 1
    if col_index < 0 or col_index >= len(df.columns):
        raise ValueError("Invalid column index.")
except ValueError:
    print("Invalid input. Please enter a valid column number.")
    exit()

# Extract the first column and the selected column
first_column = df.iloc[:, 0]  # First column
sequences = df.iloc[:, col_index]  # Selected column

# Calculate monoisotopic and average masses
results = []
for seq in sequences:
    if isinstance(seq, str):  # Ensure the cell contains a valid string
        mono_mass, avg_mass = calculate_mass(seq.upper())
        results.append({'Sequence': seq, 'Monoisotopic Mass': mono_mass, 'Average Mass': avg_mass})
    else:
        results.append({'Sequence': seq, 'Monoisotopic Mass': None, 'Average Mass': None})

# Create a DataFrame from the results
results_df = pd.DataFrame(results)

# Add the first column from the input file to the results
results_df.insert(0, 'First Column', first_column.reset_index(drop=True))

# Open a file dialog to select the output file path
output_file_path = asksaveasfilename(
    title="Save Output File",
    defaultextension=".xlsx",
    filetypes=[("Excel Files", "*.xlsx")]
)

# Check if the user canceled the save dialog
if not output_file_path:
    print("Output file not specified. Exiting.")
    exit()

# Save the results to the specified output file
try:
    results_df.to_excel(output_file_path, index=False)
    print(f"Mass calculations completed. Results saved to '{output_file_path}'.")
except Exception as e:
    print(f"Error saving the output file: {e}")