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
                # Check for dividend data
                if i + 4 < len(fields) and fields[i+4] == "Dividend":
                    # Process dividend record
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    dividend_value = f"{fields[i+3]} Dividend"  # Concatenate to form "0.0450 Dividend"
                    
                    # Write dividend row as a single string in one column
                    dividend_row = [date, dividend_value]
                    csv_writer.writerow(dividend_row)
                    
                    # Skip the processed dividend fields
                    i += 5
                    
                    # Check if next fields contain stock data for the same date
                    if i + 8 < len(fields):
                        # Ensure there are enough fields for stock data
                        next_month = fields[i]
                        next_day = fields[i+1]
                        next_year = fields[i+2]
                        
                        # Convert the next date
                        next_date = convert_date(next_month, next_day, next_year)
                        
                        if next_date == date:
                            open_price, high, low, close, adj_close, volume = fields[i+3:i+9]
                            stock_row = [
                                next_date,
                                open_price,
                                high,
                                low,
                                close,
                                adj_close,
                                convert_volume(volume)
                            ]
                            csv_writer.writerow(stock_row)
                            i += 9  # Move past the stock data
                            continue
                
                # Process regular stock data
                elif i + 8 < len(fields):
                    date = convert_date(fields[i], fields[i+1], fields[i+2])
                    open_price, high, low, close, adj_close, volume = fields[i+3:i+9]
                    row = [
                        date,
                        open_price,
                        high,
                        low,
                        close,
                        adj_close,
                        convert_volume(volume)
                    ]
                    csv_writer.writerow(row)
                    i += 9
                else:
                    # Not enough fields to process further
                    break
        
        print(f"Conversion complete. Data written to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    input_file = "new.txt"
    output_file = "output.csv"
    convert_data(input_file, output_file)
