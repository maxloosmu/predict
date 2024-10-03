import re
import csv
from datetime import datetime, timedelta
from collections import defaultdict

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
    date_entries = defaultdict(list)
    agm_entries = []
    results_entries = []

    for date_time, data in paired_entries:
        category = categorize_entry(data)
        if category:
            date = datetime.strptime(date_time, "%d %b %Y %I:%M %p")
            if category == "AGM":
                agm_entries.append((date, date_time, category))
            elif "Yearly Results" in category or "Half Yearly Results" in category:
                results_entries.append((date, date_time, category))
            else:
                date_entries[date.date()].append((date_time, category))

    # Process AGM entries
    agm_entries.sort(key=lambda x: x[0], reverse=True)  # Sort by date, latest first
    filtered_agm_entries = []
    current_group = []

    for entry in agm_entries:
        if not current_group or (current_group[0][0] - entry[0]) <= timedelta(days=90):
            current_group.append(entry)
        else:
            filtered_agm_entries.append(current_group[0])  # Add the latest entry from the group
            current_group = [entry]  # Start a new group

    if current_group:
        filtered_agm_entries.append(current_group[0])  # Add the latest entry from the last group

    # Process Results entries
    results_entries.sort(key=lambda x: x[0])  # Sort by date, earliest first
    filtered_results_entries = []
    current_group = []

    for entry in results_entries:
        if not current_group or (entry[0] - current_group[0][0]) <= timedelta(days=90):
            current_group.append(entry)
        else:
            filtered_results_entries.append(current_group[0])  # Add the earliest entry from the group
            current_group = [entry]  # Start a new group

    if current_group:
        filtered_results_entries.append(current_group[0])  # Add the earliest entry from the last group

    # Add filtered AGM and Results entries to date_entries
    for _, date_time, category in filtered_agm_entries + filtered_results_entries:
        date = datetime.strptime(date_time, "%d %b %Y %I:%M %p").date()
        date_entries[date].append((date_time, category))

    # Process entries for each date
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

    # Write to CSV file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_rows)

    print(f"Conversion complete. Output saved to {output_file}")

def categorize_entry(data):
    if "Minutes" in data:
        return ""
    elif "Annual General Meeting" in data:
        return "AGM"
    elif "REPL" in data:
        return ""
    elif "Full Yearly Results" in data:
        return "Full Yearly Results"
    elif "Half Yearly Results" in data:
        return "Half Yearly Results"
    elif "First Quarter Results" in data:
        return "Q1 Results"
    elif "Third Quarter Results" in data:
        return "Q3 Results"
    elif "Notification of Results" in data:
        return "Notification of Results"
    elif "Profit Guidance" in data:
        return "Profit Guidance"
    elif "Cash Dividend" in data:
        return "CD"
    elif re.search(r"Notification .+ Business Performance Update", data):
        return "Notification of Update"
    elif "BUSINESS UPDATE" in data or "Business Performance Update" in data or "Business Update" in data:
        return "Business Update"
    elif "Preferential Offering" in data:
        return "Pref Offering"
    elif "Placements" in data or "PLACEMENT" in data:
        return "Placement"
    return ""

# Usage
input_file = 'price.txt'
output_file = 'priced.csv'
convert_txt_to_csv(input_file, output_file)