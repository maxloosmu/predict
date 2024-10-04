import re
import csv
from datetime import datetime, timedelta
from collections import defaultdict

# Dictionary for categorizing entries based on specific keywords
CATEGORY_LOOKUP = {
    "Annual General Meeting": "AGM",
    "Full Yearly Results": "Full Yearly Results",
    "Half Yearly Results": "Half Yearly Results",
    "First Quarter Results": "Q1 Results",
    "Third Quarter Results": "Q3 Results",
    "Notification of Results": "Notification of Results",
    "Profit Guidance": "Profit Guidance",
    "Cash Dividend": "CD",
    "Preferential Offering": "Pref Offering",
    "Placements": "Placement",
}

def read_file(input_file):
    # Read the content of the input file and strip any leading/trailing whitespace
    with open(input_file, 'r') as file:
        return file.read().strip()

def parse_entries(content):
    # Split the content into individual entries using regex to match the date pattern
    pattern = r'(\d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2} [AP]M)'
    entries = re.split(pattern, content)[1:]  # Skip the initial empty string if present
    # Pair up the dates with their corresponding data
    return [(entries[i], entries[i + 1].strip()) for i in range(0, len(entries), 2)]

def categorize_entry(data):
    # Direct lookup from CATEGORY_LOOKUP dictionary
    for key, value in CATEGORY_LOOKUP.items():
        if key in data:
            return value

    # Additional conditional checks for specific categories
    if "Minutes" in data or "REPL" in data:
        return ""  # Ignore entries containing "Minutes" or "REPL"
    elif re.search(r"Notification .+ Business Performance Update", data):
        return "Notification of Update"
    elif re.search(r"BUSINESS UPDATE|Business Performance Update|Business Update", data):
        return "Business Update"
    
    return ""  # Return empty string if no category matches

def filter_entries(entries, interval_days, reverse=False):
    # Sort entries by date, either ascending or descending based on reverse flag
    entries.sort(key=lambda x: x[0], reverse=reverse)
    filtered_entries, current_group = [], []

    # Group entries based on the interval_days condition
    for entry in entries:
        if not current_group or abs((entry[0] - current_group[0][0]).days) <= interval_days:
            current_group.append(entry)
        else:
            # Select the appropriate entry from the group based on the reverse flag
            selected_entry = current_group[0] if reverse else current_group[-1]
            filtered_entries.append(selected_entry)
            current_group = [entry]

    # Add the last group if it exists
    if current_group:
        selected_entry = current_group[0] if reverse else current_group[-1]
        filtered_entries.append(selected_entry)

    return filtered_entries

def write_to_csv(output_file, rows):
    # Write the rows to a CSV file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def convert_txt_to_csv(input_file, output_file):
    # Read content from the input file
    content = read_file(input_file)
    # Parse the content into date-data pairs
    paired_entries = parse_entries(content)

    # Initialize lists for different categories of entries
    agm_entries, results_entries, date_entries = [], [], defaultdict(list)
    for date_time, data in paired_entries:
        # Categorize each entry
        category = categorize_entry(data)
        if category:
            date = datetime.strptime(date_time, "%d %b %Y %I:%M %p")
            if category == "AGM":
                agm_entries.append((date, date_time, category))
            elif "Yearly Results" in category or "Half Yearly Results" in category:
                results_entries.append((date, date_time, category))
            else:
                date_entries[date.date()].append((date_time, category))

    # Filter AGM entries based on a 90-day interval, keeping the latest entry in each group
    agm_entries.sort(key=lambda x: x[0], reverse=True)
    filtered_agm_entries = []
    current_group = []
    for entry in agm_entries:
        if not current_group or (current_group[0][0] - entry[0]) <= timedelta(days=90):
            current_group.append(entry)
        else:
            filtered_agm_entries.append(current_group[0])  # Keep the latest entry
            current_group = [entry]
    if current_group:
        filtered_agm_entries.append(current_group[0])

    # Filter Results entries based on a 90-day interval, keeping the earliest entry in each group
    results_entries.sort(key=lambda x: x[0])
    filtered_results_entries = []
    current_group = []
    for entry in results_entries:
        if not current_group or (entry[0] - current_group[0][0]) <= timedelta(days=90):
            current_group.append(entry)
        else:
            filtered_results_entries.append(current_group[0])  # Keep the earliest entry
            current_group = [entry]
    if current_group:
        filtered_results_entries.append(current_group[0])

    # Add filtered AGM and Results entries to date_entries dictionary
    for _, date_time, category in filtered_agm_entries + filtered_results_entries:
        date = datetime.strptime(date_time, "%d %b %Y %I:%M %p").date()
        date_entries[date].append((date_time, category))

    # Prepare rows for CSV output
    csv_rows = [["Date & Time", "Title Category"]]  # Header row
    for date in sorted(date_entries.keys(), reverse=True):
        entries = date_entries[date]
        entries.sort(key=lambda x: x[0], reverse=True)  # Sort by time, latest first
        processed_entries = []
        cd_added = False
        for date_time, category in entries:
            if category == "CD":
                if not cd_added:
                    processed_entries.append((date_time, category))
                    cd_added = True
            else:
                processed_entries.append((date_time, category))
        # Swap CD and Results if necessary
        if len(processed_entries) >= 2 and processed_entries[0][1] == "CD" and "Results" in processed_entries[1][1]:
            processed_entries[0], processed_entries[1] = processed_entries[1], processed_entries[0]
        csv_rows.extend(processed_entries)

    # Convert date and time to the desired format (DD/MM/YYYY HH:MM)
    formatted_rows = [(datetime.strptime(e[0], "%d %b %Y %I:%M %p").strftime("%d/%m/%Y %H:%M"), e[1]) for e in csv_rows[1:]]
    csv_rows = [csv_rows[0]] + formatted_rows

    # Write the rows to the output CSV file
    write_to_csv(output_file, csv_rows)
    print(f"Conversion complete. Output saved to {output_file}")

# Usage
input_file = 'price.txt'
output_file = 'priced.csv'
convert_txt_to_csv(input_file, output_file)