import csv
from datetime import datetime

def process_priced_csv(input_file):
    processed_rows = []
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            date_time, title = row
            dt = datetime.strptime(date_time, '%d/%m/%Y %H:%M')
            
            if 17 <= dt.hour <= 23:
                title += " (PM)"
            elif 0 <= dt.hour < 17:
                title += " (AM)"
            
            # Preserve original date format
            date = f"{dt.day}/{dt.month}/{dt.year}"
            processed_rows.append([date, title])
    return processed_rows

def merge_and_sort_data(formatted_file, processed_rows):
    with open(formatted_file, 'r') as file:
        formatted_data = list(csv.reader(file))
    
    # header = formatted_data[0]
    # formatted_data = formatted_data[1:]  # Remove header
    
    # Combine all rows
    all_rows = formatted_data + processed_rows
    
    # Custom sorting key function
    def sort_key(row):
        date = datetime.strptime(row[0], '%d/%m/%Y')
        # Sort by date (descending), then by AM/PM (AM first, then no indicator, then PM)
        time_order = 0 if '(AM)' in row[1] else (2 if '(PM)' in row[1] else 1)
        return (-date.timestamp(), time_order)
    
    # Sort rows
    sorted_rows = sorted(all_rows, key=sort_key)
    
    # # Add header back
    # sorted_rows.insert(0, header)
    
    return sorted_rows

def write_output(output_file, data):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Main execution
priced_file = 'hksort.csv'
formatted_file = 'formatted.csv'
output_file = 'formatted2.csv'

processed_rows = process_priced_csv(priced_file)
final_data = merge_and_sort_data(formatted_file, processed_rows)
write_output(output_file, final_data)

print(f"Processing complete. Output written to {output_file}")