import json

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def convert_dose_format(dose_data):
    if not dose_data or not isinstance(dose_data, dict):
        return {}
    
    result = {}
    for substance in dose_data.get('substances', []):
        for roa in substance.get('roas', []):
            if not roa:
                continue
                
            route = roa.get('name', '').capitalize()
            if not route:
                continue
                
            dose = roa.get('dose')
            if not dose or not isinstance(dose, dict):
                continue
                
            units = dose.get('units', '')
            
            formatted_doses = {}
            
            light = dose.get('light', {})
            if isinstance(light, dict) and 'min' in light and 'max' in light:
                formatted_doses['Light'] = f"{light['min']}-{light['max']}{units}"
            
            common = dose.get('common', {})
            if isinstance(common, dict) and 'min' in common and 'max' in common:
                formatted_doses['Common'] = f"{common['min']}-{common['max']}{units}"
            
            strong = dose.get('strong', {})
            if isinstance(strong, dict) and 'min' in strong and 'max' in strong:
                formatted_doses['Strong'] = f"{strong['min']}-{strong['max']}{units}"
            
            heavy = dose.get('heavy')
            if heavy is not None:
                formatted_doses['Heavy'] = f"{heavy}{units}+"
            
            if formatted_doses:
                result[route] = formatted_doses
                
    return result

def convert_duration_format(duration_data):
    if not duration_data or not isinstance(duration_data, dict):
        return {}
    
    for substance in duration_data.get('substances', []):
        for roa in substance.get('roas', []):
            duration = roa.get('duration', {})
            if duration and duration.get('total'):
                return {
                    "_unit": duration['total'].get('units', 'hours'),
                    "value": f"{duration['total']['min']}-{duration['total']['max']}"
                }
    return {}

def convert_onset_format(duration_data):
    if not duration_data or not isinstance(duration_data, dict):
        return {}
    
    for substance in duration_data.get('substances', []):
        for roa in substance.get('roas', []):
            duration = roa.get('duration', {})
            if duration and duration.get('onset'):
                return {
                    "_unit": duration['onset'].get('units', 'minutes'),
                    "value": f"{duration['onset']['min']}-{duration['onset']['max']}"
                }
    return {}

def convert_aftereffects_format(duration_data):
    if not duration_data or not isinstance(duration_data, dict):
        return {}
    
    for substance in duration_data.get('substances', []):
        for roa in substance.get('roas', []):
            duration = roa.get('duration', {})
            if duration and duration.get('afterglow'):
                return {
                    "_unit": duration['afterglow'].get('units', 'hours'),
                    "value": f"{duration['afterglow']['min']}-{duration['afterglow']['max']}"
                }
    return {}

def convert_effects_list(effects_data):
    if not effects_data or not isinstance(effects_data, dict):
        return []
    
    effects = []
    for substance in effects_data.get('substances', []):
        effects.extend([effect['name'] for effect in substance.get('effects', [])])
    return effects

def convert_psychonaut_to_tripsit(psychonaut_data):
    tripsit_format = {}
    
    for substance_name, substance_data in psychonaut_data.items():
        substance_info = substance_data.get('data', {})
        
        converted_substance = {
            "name": substance_name.lower(),
            "pretty_name": substance_name.upper(),
            "aliases": [],
            "categories": [],
            "properties": {
                "summary": "",
                "categories": [],
                "aliases": [],
            }
        }
        
        converted_substance["formatted_dose"] = convert_dose_format(substance_info)
        
        converted_substance["formatted_duration"] = convert_duration_format(substance_info)
        
        converted_substance["formatted_onset"] = convert_onset_format(substance_info)
        
        converted_substance["formatted_aftereffects"] = convert_aftereffects_format(substance_info)
        
        converted_substance["formatted_effects"] = convert_effects_list(substance_info)
        
        if converted_substance["formatted_onset"]:
            converted_substance["properties"]["onset"] = (
                f"{converted_substance['formatted_onset']['value']} "
                f"{converted_substance['formatted_onset']['_unit']}"
            )
        
        if converted_substance["formatted_duration"]:
            converted_substance["properties"]["duration"] = (
                f"{converted_substance['formatted_duration']['value']} "
                f"{converted_substance['formatted_duration']['_unit']}"
            )
        
        if converted_substance["formatted_aftereffects"]:
            converted_substance["properties"]["after-effects"] = (
                f"{converted_substance['formatted_aftereffects']['value']} "
                f"{converted_substance['formatted_aftereffects']['_unit']}"
            )
        
        tripsit_format[substance_name.lower()] = converted_substance
    
    return tripsit_format

def main():
    psychonaut_data = load_json_file("data/raw_psychonaut.json")
    
    tripsit_format = convert_psychonaut_to_tripsit(psychonaut_data)
    
    save_json_file(tripsit_format, "data/psychonaut.json")

if __name__ == "__main__":
    main()