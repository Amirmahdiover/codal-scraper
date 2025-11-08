import json
import os
from typing import Dict, List, Set

# Path to the JSON-based knowledge file
LABEL_MAP_PATH = os.path.join(os.path.dirname(__file__), "label_map.json")


# ✅ 1️⃣ Load or initialize label_map
def load_label_map() -> Dict[str, str]:
    if os.path.exists(LABEL_MAP_PATH):
        with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "revenue": "revenue",
            "sales": "revenue",
            "cost of goods sold": "cogs",
            "cogs": "cogs",
            "operating profit": "operating_income",
            "net income": "net_income"
        }


def save_label_map(label_map: Dict[str, str]) -> None:
    with open(LABEL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2, ensure_ascii=False)


# ✅ 2️⃣ Normalize scraped labels
def normalize_label(label: str, label_map: Dict[str, str]) -> str:
    label = label.lower().strip()
    label = label.replace(":", "").replace(",", "").replace("_", " ")
    label = " ".join(label.split())
    if label.endswith("s") and label[:-1] in label_map:
        label = label[:-1]
    return label


# ✅ 3️⃣ Rule-based + unknown collection
def map_labels(scraped_labels: List[str], label_map: Dict[str, str]) -> (Dict[str, str], Set[str]):
    final_results = {}
    unknown_labels = set()

    for label in scraped_labels:
        normalized = normalize_label(label, label_map)
        if normalized in label_map:
            mapped = label_map[normalized]
        else:
            mapped = normalized
            unknown_labels.add(normalized)
        final_results[label] = mapped

    return final_results, unknown_labels


# ✅ 4️⃣ Placeholder LLM call (replace with OpenAI later)
def query_llm_for_labels(unknown_labels: Set[str]) -> Dict[str, str]:
    # You can replace this with an OpenAI API call later.
    print(f"[LLM] Mapping unknowns: {unknown_labels}")
    fake_response = {
        "turnover": "revenue",
        "profit before tax": "operating_income"
    }
    return {label: fake_response.get(label, "other_income") for label in unknown_labels}


# ✅ 5️⃣ Update map with new knowledge
def update_label_map_with_llm(label_map: Dict[str, str], llm_results: Dict[str, str]):
    label_map.update(llm_results)
    save_label_map(label_map)


# ✅ 6️⃣ Orchestrator
def normalize_labels(scraped_labels: List[str]) -> Dict[str, str]:
    label_map = load_label_map()
    mapped_labels, unknown_labels = map_labels(scraped_labels, label_map)

    if unknown_labels:
        llm_results = query_llm_for_labels(unknown_labels)
        update_label_map_with_llm(label_map, llm_results)
        # re-map after learning
        mapped_labels, _ = map_labels(scraped_labels, label_map)

    return mapped_labels
