import csv
import os
import sys

cust_id = sys.argv[1]

# Specify the directory path and column name
directory_path = f'/app/tmp_files/{cust_id}'  # Replace with the actual directory path
column_name_to_remove_list = ['Memcached-Server-Reflect']

def remove_column(csv_file_path, column_name):
    # Read the CSV file into a list of dictionaries
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # Check if the column exists
    if column_name in rows[0]:
        # Remove the column from the header
        header = reader.fieldnames
        header.remove(column_name)

        # Remove the entire column from each row
        for row in rows:
            del row[column_name]

        # Write the modified data (with updated header) back to the CSV file
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Column '{column_name}' removed in {csv_file_path}, including the header, and file updated.")
    else:
        print(f"Column '{column_name}' not found in the {csv_file_path} file.")

def process_files_in_directory(directory_path, column_name):
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv') and (filename == 'epm_chart_alltimehigh.csv' or filename == 'epm_chart_lm.csv' or filename == 'events_per_day_chart_alltimehigh.csv'):
            file_path = os.path.join(directory_path, filename)
            remove_column(file_path, column_name)


# Call the function to process files in the specified directory
for column_name_to_remove in column_name_to_remove_list:    
    process_files_in_directory(directory_path, column_name_to_remove)