import re
import json

with open('tripsit.json', 'r', encoding='utf8') as f:
		drugs = json.load(f)

for drug in drugs:
	drug = drugs[drug]
	# if no substances
	if not drug.get('sources', {}).get('_general', []):
		continue

	for substance in drug['sources']['_general']:
		if not re.match(r'([a-zA-Z0-9-_:\'"\?.,()\[\]\/\\ ]+) - http[s]?:\/\/([a-zA-Z0-9\-%.\/]+)', substance):
			print(drug['name'])
			break