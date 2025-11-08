import requests
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0"
}

def industry_group_scraper(api_url: str = "https://search.codal.ir/api/search/v1/IndustryGroup") -> pd.DataFrame:
    """
    Fetches industry group data from Codal API and returns it as a DataFrame.

    Args:
        api_url (str): The API endpoint.

    Returns:
        pd.DataFrame: A DataFrame with columns 'id' and 'name'.
    """
    try:
        response = requests.get(api_url,headers=headers)
        response.raise_for_status()  # Raise error for bad status

        data = response.json()
        # Normalize into DataFrame
        df = pd.DataFrame(data)
        df.rename(columns={"Id": "id", "Name": "name"}, inplace=True)

        # Save to CSV
        df.to_csv("output/industry_groups.csv", index=False, encoding="utf-8-sig")
        print("✅ Saved as industry_groups.csv")

        return df

    except Exception as e:
        print(f"❌ Failed to fetch or parse industry groups: {e}")
        return pd.DataFrame(columns=["id", "name"])

# Run it
if __name__ == "__main__":
    df = industry_group_scraper()
    print(df.head())
