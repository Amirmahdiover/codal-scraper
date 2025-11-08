from scraper.income_statement.normalizer import normalize_labels

def convert_df_to_record(df, source_url, announcement_id):
    record = {
        "company_name": df['company_name'].iloc[0],
        "period_ended": df['periodEndToDate'].iloc[0],
        "source_url": source_url,
        "announcement_id": announcement_id
    }

    scraped_labels = df["label"].tolist()
    mapped_results = normalize_labels(scraped_labels)

    for _, row in df.iterrows():
        original_label = row["label"]
        english_field = mapped_results.get(original_label)
        if english_field:
            record[english_field] = row["amount"]

    return record
