import requests
import csv
headers = {
    "User-Agent": "Mozilla/5.0"
}
def fetch_categories(url):
    resp = requests.get(url,headers=headers)
    resp.raise_for_status()
    return resp.json()

def save_to_csv(data, csv_filename):
    # Assuming `data` is a list of objects with the same keys
    if not data:
        print("No data to save")
        return

    # Determine CSV header from the first item
    headers = list(data[0].keys())
    with open(csv_filename, mode='w', newline='', encoding='utf‑8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def main():
    url = "https://search.codal.ir/api/search/v1/categories"
    print(f"Fetching from {url} …")
    json_data = fetch_categories(url)
    # If the JSON has nested structure, e.g.,
    # { "categories": [ {...}, {...} ] }, then adjust:
    # data = json_data.get("categories", [])
    data = json_data  # change if needed
    csv_file = r"C:\Users\amirmahdi\Desktop\codal scraper\output\categories.csv"
    print(f"Saving data to {csv_file} …")
    save_to_csv(data, csv_file)
    print("Done.")

if __name__ == "__main__":
    main()
