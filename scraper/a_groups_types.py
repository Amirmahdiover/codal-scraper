import csv
import ast
import pandas as pd
import os

# Input CSV
input_file = r"C:\Users\amirmahdi\Desktop\codal scraper\output\categories.csv"

# Output files
groups_output = "announcement_groups.csv"
types_output = "announcement_types.csv"
output_dir = 'output'
# Storage for clean records
group_rows = []
type_rows = set()  # using set to prevent duplicates

# Step 1: Read and parse
with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        group_id = int(row["Code"])
        group_name = row["Name"]
        group_rows.append({"id": group_id, "name": group_name})

        # Parse PublisherTypes (convert string to list of dicts)
        try:
            publishers = ast.literal_eval(row["PublisherTypes"])
        except Exception as e:
            print(f"Failed to parse PublisherTypes for group {group_name}: {e}")
            continue

        for publisher in publishers:
            letter_types = publisher.get("LetterTypes", [])
            for lt in letter_types:
                letter_id = int(lt["Id"])
                letter_name = lt["Name"]
                type_rows.add((letter_id, letter_name, group_id))

# Step 2: Save groups
df_groups = pd.DataFrame(group_rows)
df_groups.to_csv(os.path.join(output_dir, groups_output), index=False, encoding="utf-8")

# Step 3: Save types
df_types = pd.DataFrame(list(type_rows), columns=["id", "name", "group_id"])
df_types.sort_values(by=["group_id", "id"], inplace=True)
df_types.to_csv(os.path.join(output_dir, types_output), index=False, encoding="utf-8")

print("✔️ Done! Saved to:")
print(" -", groups_output)
print(" -", types_output)
