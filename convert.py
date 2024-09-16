import csv
from datetime import datetime

def convert_date(month, day, year):
    day = day.rstrip(',')  # Remove trailing comma
    date_str = f"{month} {day} {year}"
    date_obj = datetime.strptime(date_str, "%b %d %Y")
    return date_obj.strftime("%-d/%-m/%Y")  # Use %-d and %-m to remove leading zeros

def convert_volume(volume_str):
    return volume_str.replace(',', '') if volume_str != '-' else '0'

def convert_data(input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            csv_writer = csv.writer(outfile)
            
            content = infile.read().strip()
            fields = content.split()
            
            i = 0
            while i < len(fields):
                if i + 8 < len(fields) and not fields[i+3].startswith('*'):  # Regular stock data
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    open_price, high, low, close, adj_close, volume = fields[i+3:i+9]
                    volume = convert_volume(volume)
                    
                    row = [date, open_price, high, low, close, adj_close, volume]
                    print(f"Writing stock data: {row}")
                    csv_writer.writerow(row)
                    i += 9
                elif i + 4 < len(fields) and fields[i+3].startswith('*'):  # Dividend data
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    dividend = float(fields[i+3].strip('*'))  # Convert to float
                    
                    row = [date] + [''] * 6 + [f"{dividend:.3f}"]  # Format dividend to 3 decimal places
                    print(f"Writing dividend data: {row}")
                    csv_writer.writerow(row)
                    i += 5
                else:
                    print(f"Warning: Unexpected data format at index {i}")
                    print(f"Remaining fields: {fields[i:]}")
                    break
        
        print(f"Conversion complete. Data written to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = "new.txt"
    output_file = "output.csv"
    convert_data(input_file, output_file)