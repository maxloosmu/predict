import csv
from datetime import datetime

def convert_date(month, day, year):
    day = day.rstrip(',')  # Remove trailing comma
    date_str = f"{month} {day} {year}"
    date_obj = datetime.strptime(date_str, "%b %d %Y")
    return date_obj.strftime("%-d/%-m/%Y")  # Use %-d and %-m to remove leading zeros

def convert_volume(volume_str):
    return volume_str.replace(',', '') if volume_str != '-' else '0'

def convert_data(input_file, output_file, formatted_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile, open(formatted_file, 'w', newline='') as formatted_outfile:
            csv_writer = csv.writer(outfile)
            formatted_csv_writer = csv.writer(formatted_outfile)
            
            content = infile.read().strip()
            fields = content.split()
            
            i = 0
            previous_row = None
            while i < len(fields):
                if i + 8 < len(fields) and not fields[i+3].startswith('*'):  # Regular stock data
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    open_price, high, low, close, adj_close, volume = fields[i+3:i+9]
                    volume = convert_volume(volume)
                    
                    row = [date, open_price, high, low, close, adj_close, volume]
                    print(f"Writing stock data: {row}")
                    csv_writer.writerow(row)
                    
                    if previous_row and previous_row[0] == date and 'Dividend' in previous_row[1]:
                        formatted_csv_writer.writerow(previous_row)
                        formatted_csv_writer.writerow(row)
                        previous_row = None
                    else:
                        if previous_row:
                            formatted_csv_writer.writerow(previous_row)
                        previous_row = row
                    
                    i += 9
                elif i + 4 < len(fields) and fields[i+3].startswith('*'):  # Dividend data
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    dividend = float(fields[i+3].strip('*'))  # Convert to float
                    
                    output_row = [date] + [''] * 6 + [f"{dividend}"]
                    formatted_row = [date, f"{dividend} Dividend"] + [''] * 5
                    print(f"Writing dividend data: {output_row}")
                    csv_writer.writerow(output_row)
                    
                    if previous_row and previous_row[0] == date:
                        formatted_csv_writer.writerow(formatted_row)
                        formatted_csv_writer.writerow(previous_row)
                        previous_row = None
                    else:
                        if previous_row:
                            formatted_csv_writer.writerow(previous_row)
                        previous_row = formatted_row
                    
                    i += 5
                else:
                    print(f"Warning: Unexpected data format at index {i}")
                    print(f"Remaining fields: {fields[i:]}")
                    break
            
            # Write the last row if it exists
            if previous_row:
                formatted_csv_writer.writerow(previous_row)
        
        print(f"Conversion complete. Data written to {output_file} and {formatted_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = "new.txt"
    output_file = "output.csv"
    formatted_file = "formatted.csv"
    convert_data(input_file, output_file, formatted_file)