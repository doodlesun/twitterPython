import json

def toJson(raw):
    return json.dumps(raw, indent=4, ensure_ascii=False)

def sanitizeText(text):
    return text.replace('\n', '')
