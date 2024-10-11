import re
import csv
from datetime import datetime, timedelta
from collections import defaultdict

def convert_txt_to_csv(input_file, output_file):
    # Read the content of the input file
    with open(input_file, 'r') as file:
        content = file.read().strip()

    # Split the content into individual entries using regex
    # The regex captures date-time patterns like "03 Nov 2022 05:07 PM"
    pattern = r'(\d{1,2} [A-Z][a-z]{2} \d{4} \d{1,2}:\d{2} [AP]M)'
    entries = re.split(pattern, content)[1:]  # Start from index 1 to skip initial empty string

    # Pair up the dates with their corresponding data
    paired_entries = [(entries[i], entries[i+1].strip()) for i in range(0, len(entries), 2)]

    # Categorize entries
    all_entries = []
    for date_time_str, data in paired_entries:
        category = categorize_entry(data)
        if category:
            try:
                date_time = datetime.strptime(date_time_str, "%d %b %Y %I:%M %p")
            except ValueError as e:
                print(f"Error parsing date-time '{date_time_str}': {e}")
                continue  # Skip this entry if date parsing fails
            all_entries.append((date_time, category))

    # Separate AGM entries from other entries
    agm_entries = [entry for entry in all_entries if entry[1] == "AGM"]
    other_entries = [entry for entry in all_entries if entry[1] != "AGM"]

    # Filter AGM entries to retain only the latest within any 3-month window
    filtered_agm_entries = filter_agm_entries(agm_entries)

    # Combine filtered AGM entries with other entries
    combined_entries = other_entries + filtered_agm_entries

    # Define priority: "Results" (1) before "CD" (2) before others (3)
    def get_priority(category):
        if "Results" in category:
            return 1
        elif "CD" in category:
            return 2
        else:
            return 3

    # Sort combined entries
    # Primary Sort: Date descending
    # Secondary Sort: Priority ascending ("Results" before "CD" before others)
    # Tertiary Sort: Time descending within the same date and priority
    sorted_entries = sorted(
        combined_entries,
        key=lambda x: (
            -x[0].year,
            -x[0].month,
            -x[0].day,
            get_priority(x[1]),
            -x[0].hour,
            -x[0].minute
        )
    )

    # Prepare CSV rows
    csv_rows = [["Date & Time", "Title Category"]]
    for entry in sorted_entries:
        date_time = entry[0]
        category = entry[1]
        formatted_dt = f"{date_time.day}/{date_time.month}/{date_time.year} {date_time.hour:02}:{date_time.minute:02}"
        csv_rows.append([formatted_dt, category])

    # Write to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_rows)

    print(f"Conversion complete. Output saved to {output_file}")

def filter_agm_entries(agm_entries):
    """
    Filters AGM entries to retain only the latest entry within any 3-month window.

    Parameters:
        agm_entries (list): List of tuples containing (datetime, category) for AGM entries.

    Returns:
        list: Filtered list of AGM entries.
    """
    # Sort AGM entries in descending order (latest first)
    sorted_agm = sorted(agm_entries, key=lambda x: x[0], reverse=True)
    filtered = []
    last_selected_date = None

    for entry in sorted_agm:
        current_date = entry[0]
        if not last_selected_date:
            # Select the first AGM entry
            filtered.append(entry)
            last_selected_date = current_date
        else:
            # Check if the current AGM is at least 3 months apart from the last selected AGM
            # Using 90 days as an approximation for 3 months
            if (last_selected_date - current_date) > timedelta(days=90):
                filtered.append(entry)
                last_selected_date = current_date
            else:
                # Skip this AGM entry as it's within 3 months of the last selected AGM
                continue
    return filtered

def categorize_entry(data):
    """
    Categorizes the entry based on the content string.

    Parameters:
        data (str): The data string containing category information.

    Returns:
        str: The categorized title.
    """
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
