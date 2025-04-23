import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Function to open file dialog and get file path
def get_file_path(title, filetypes):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()  # Ensure the root window is destroyed
    return file_path

try:
    # Prompt the user to select the first Excel file
    print("Selecting the first Excel file...")
    file1_path = get_file_path("Select the first Excel file", [("Excel files", "*.xlsx"), ("All files", "*.*")])
    if not file1_path:
        raise ValueError("No first Excel file selected.")
    print(f"Selected first Excel file: {file1_path}")

    # Load the first Excel file with the first row as the header
    file1 = pd.read_excel(file1_path, header=0)
    print("First Excel file loaded successfully.")

    # Display the column names to the user
    print("Available columns in first Excel file:")
    for idx, column in enumerate(file1.columns, start=1):
        print(f"{idx}. {column}")

    # Ask the user to choose a column by index
    column_index = int(input("Enter the number corresponding to the column you want to extract: ")) - 1
    print(f"Selected column index: {column_index}")

    # Get the selected column name
    if 0 <= column_index < len(file1.columns):
        column_name = file1.columns[column_index]
        print(f"Selected column name: {column_name}")

        # Extract the text from the selected column
        extracted_text = file1[column_name].dropna().tolist()
        print(f"Extracted text: {extracted_text}")

        # Prompt the user to select the second file (text file)
        print("Selecting the text file to search in...")
        file2_path = get_file_path("Select the text file", [("Text files", "*.txt"), ("All files", "*.*")])
        if not file2_path:
            raise ValueError("No text file selected.")
        print(f"Selected text file: {file2_path}")

        # Read the text file into a DataFrame (assuming one item per line)
        with open(file2_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # Create a DataFrame with one column
        file2 = pd.DataFrame(lines, columns=['Text'])
        print("Text file loaded successfully.")

        # Initialize a list to store results
        results = []

        # Search for each item in the text file
        for item in extracted_text:
            print(f"Searching for item: {item}")
            mask = file2['Text'].str.strip().str.contains(str(item).strip(), case=False, na=False)
            matching_rows = file2[mask].copy()
            print(f"Matching rows for {item}:\n{matching_rows}")
            if not matching_rows.empty:
                # Get the index of the last matching row
                last_match_idx = matching_rows.index[-1]
                # Start collecting sequence from the next line
                if last_match_idx + 1 < len(file2):
                    sequence_lines = []
                    # Collect lines until the next '>' or end of file
                    for idx in range(last_match_idx + 1, len(file2)):
                        line = file2.loc[idx, 'Text'].strip()
                        if line.startswith('>'):
                            break
                        if line:  # Only include non-empty lines
                            sequence_lines.append(line)
                    # Concatenate the sequence lines into a single string
                    concatenated_text = ''.join(sequence_lines)
                    # Append the result with the searched item and concatenated text
                    results.append([item, concatenated_text])
                else:
                    print(f"No lines after last match for {item}")
                    results.append([item, ""])
            else:
                print(f"No matches found for {item}")
                results.append([item, ""])

        # Create a DataFrame from the results, maintaining the order of extracted_text
        if results:
            result_df = pd.DataFrame(results, columns=['Searched Item', 'Extracted Sequence'])
            print("Result DataFrame created.")
            print(result_df)

            # Save the results to a new Excel file
            print("Selecting the output file path for results...")
            output_file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if output_file_path:
                result_df.to_excel(output_file_path, index=False)
                print(f"Results saved to {output_file_path}")
            else:
                print("Save operation cancelled.")
        else:
            print("No results to save.")
    else:
        print("Invalid column index.")

except Exception as e:
    print(f"An error occurred: {e}")