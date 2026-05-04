import json, base64, requests
from src.config import LM_STUDIO_URL, MODEL

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def evaluate_single_image(image_path: str, prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_path)}"}
                },
                {"type": "text", "text": prompt}
            ]
        }],
        "temperature": 0.2,
        "max_tokens": 200
    }
    response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload)
    raw = response.json()["choices"][0]["message"]["content"]

    try:
        clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"passed": None, "confidence": 0.0, "reasoning": raw}


def evaluate_with_voting(image_paths: list[str], prompt: str) -> dict:
    results = [evaluate_single_image(path, prompt) for path in image_paths]
    valid = [r for r in results if r.get("passed") is not None]

    if not valid:
        return {"passed": None, "certainty": 0.0, "reasoning": "Could not determine"}

    best = max(valid, key=lambda r: r.get("certainty", 0))
    
    passes = sum(1 for r in valid if r["passed"])

    return {
        "passed": best["passed"],
        "certainty": best["certainty"],
        "reasoning": f"{passes}/{len(valid)} images passed. {best['reasoning']}"
    }
