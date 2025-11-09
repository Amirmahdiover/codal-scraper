import json
import os
from typing import Dict, List, Set
from ..utils import normalize_persian_text
# Path to the JSON-based knowledge file
LABEL_MAP_PATH = os.path.join(os.path.dirname(__file__), "label_map.json")


def load_label_map() -> Dict[str, str]:
    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_label_map(label_map: Dict[str, str]) -> None:
    with open(LABEL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2, ensure_ascii=False)



def map_labels(scraped_labels: List[str], label_map: Dict[str, str]) -> (Dict[str, str], Set[str]):
    final_results = {}
    unknown_labels = set()

    for label in scraped_labels:
        normalized = normalize_persian_text(label)
        if normalized in label_map:
            mapped = label_map[normalized]
        else:

            mapped = normalized
            unknown_labels.add(normalized)
        final_results[label] = mapped

    return final_results, unknown_labels


from dotenv import load_dotenv
load_dotenv()
import os
import json
import requests
from typing import Set, Dict

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")  # Set this in your environment

def query_llm_for_labels(unknown_labels: Set[str], existing_label_map: Dict[str, str]) -> Dict[str, str]:
    # Construct the prompt
    prompt = (
        "You are a financial data normalization assistant.\n"
        "You will receive a list of Persian financial labels (Farsi text) that must be mapped to standardized English financial terms.\n\n"
        "You are provided with a dictionary of known label mappings from Persian labels to standardized English labels.\n"
        "Use this dictionary as your reference knowledge.\n\n"
        "👉 Your job:\n"
        "1. If a Persian label has a meaning that is close or identical to one of the known labels, return the **exact same English label** from the dictionary — do NOT change it.\n"
        "2. If there is no close or relevant match, create a **new standardized English label** that clearly expresses the Persian term’s meaning.\n"
        "   - Use lowercase English words.\n"
        "   - Use snake_case (e.g., 'gross_profit', 'retained_earnings', 'investment_income').\n"
        "3. Do not repeat existing keys in new names if they already mean the same thing.\n"
        "4. Output must be a valid JSON object — no extra text, comments, or explanations.\n\n"
        "📘 Known label mappings:\n"
        f"{json.dumps(existing_label_map, ensure_ascii=False, indent=2)}\n\n"
        "📝 Persian labels to normalize:\n"
        f"{list(unknown_labels)}\n\n"
        "💡 Example format:\n"
        "{\n"
        "  'سود هر سهم بعد از کسر مالیات': 'eps_net',\n"
        "  'سود انباشته پایان دوره': 'retained_earnings'\n"
        "}\n\n"
        "⚠️ Respond ONLY with the JSON object. Do not add explanations, quotes, or commentary."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-4o",  # or other OpenRouter-supported models
        "messages": [
            {"role": "system", "content": "You are a financial data normalization assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result_text = response.json()['choices'][0]['message']['content']
        label_mapping = json.loads(result_text)
        return label_mapping
    except Exception as e:
        print(f"❌ Error communicating with OpenRouter or parsing response: {e}")
        return {label: "other_income" for label in unknown_labels}

def update_label_map_with_llm(label_map: Dict[str, str], llm_results: Dict[str, str]):
    label_map.update(llm_results)
    save_label_map(label_map)

from db.models import sync_income_statement_columns
from db.base import engine

def normalize_labels(scraped_labels: List[str]) -> Dict[str, str]:
    label_map = load_label_map()
    mapped_labels, unknown_labels = map_labels(scraped_labels, label_map)
    sync_income_statement_columns(engine, label_map)
    if unknown_labels:
        llm_results = query_llm_for_labels(unknown_labels=unknown_labels, existing_label_map=label_map)
        update_label_map_with_llm(label_map, llm_results)

        # ✅ re-map after adding new labels
        mapped_labels, _ = map_labels(scraped_labels, label_map)

        # ✅ create engine and sync schema
        sync_income_statement_columns(engine, label_map)

    return mapped_labels


if __name__ == "__main__":
    import json

    # Load test labels from file
    with open("test_scraped_labels.json", "r", encoding="utf-8") as f:
        test_labels = json.load(f)

    # Normalize labels using your main orchestrator
    result = normalize_labels(test_labels)

    # Print results
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Optionally save the output to a file
    with open("mapped_labels_output.json", "w", encoding="utf-8") as f_out:
        json.dump(result, f_out, indent=2, ensure_ascii=False)
