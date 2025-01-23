import json
import re

_SOURCE_REGEX_PATTERN = (
    r'([a-zA-Z0-9-_:\'"\?.,()\[\]\/\\ ]+) - http[s]?:\/\/([a-zA-Z0-9\-%.\/]+)',
)

with open("final_updated_drugs.json", "r", encoding="utf8") as f:
    drugs = json.load(f)

for drug in drugs:
    drug = drugs[drug]
    # if no substances
    if not drug.get("sources", {}).get("_general", []):
        continue

    for substance in drug["sources"]["_general"]:
        if not re.match(
            _SOURCE_REGEX_PATTERN,
            substance,
        ):
            print(drug["name"])
            break
