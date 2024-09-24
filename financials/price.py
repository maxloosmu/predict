import re
import csv

def convert_txt_to_csv(input_file, output_file):
    # Read the content of the input file
    with open(input_file, 'r') as file:
        content = file.read().strip()

    # Split the content into individual entries
    pattern = r'(\d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2} [AP]M)'
    entries = re.split(pattern, content)[1:]  # Start from index 1 to skip initial empty string
    
    # Pair up the dates with their corresponding data
    paired_entries = [(entries[i], entries[i+1].strip()) for i in range(0, len(entries), 2)]

    # Process entries and create rows for CSV
    csv_rows = [["Date & Time", "Title Category"]]  # Header row
    for date_time, data in paired_entries:
        category = ""
        if "DRP" in data:
            category = "DRP"
        elif "Full Yearly Results" in data:
            category = "Full Yearly Results"
        elif "Notification of Results" in data:
            category = "Notification of Results"
        elif "Cash Dividend" in data:
            category = "CD"
        elif "Half Yearly Results" in data:
            category = "Half Yearly Results"
        elif "Annual General Meeting" in data:
            category = "AGM"
        
        csv_rows.append([date_time, category])

    # Write to CSV file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_rows)

    print(f"Conversion complete. Output saved to {output_file}")

# Usage
input_file = 'price.txt'
output_file = 'priced.csv'
convert_txt_to_csv(input_file, output_file)