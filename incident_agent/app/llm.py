import os
from typing import List, Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _simple_summarize(incident: Dict[str, Any], similar: List[Dict[str, Any]]) -> Dict[str, str]:
    # Fallback summarizer when no LLM is configured.
    title = incident.get("title", "")
    desc = incident.get("description", "")
    # pick common root_causes from similar incidents
    causes = [s.get("root_cause") for s in similar if s.get("root_cause")]
    cause = causes[0] if causes else (incident.get("root_cause") or "Unknown")
    # aggregate resolutions
    resolutions = [s.get("resolution") for s in similar if s.get("resolution")]
    resolution = resolutions[0] if resolutions else (incident.get("resolution") or "Investigate and follow runbook")
    runbook_steps = [f"- {resolution}"]
    return {
        "summary": f"Suggested root cause: {cause}\nQuick summary: {title} — {desc[:200]}",
        "runbook": "\n".join(runbook_steps),
        "resolution": resolution,
    }


def suggest_resolution(incident: Dict[str, Any], similar: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate a suggested root cause, runbook and resolution text.

    If `OPENAI_API_KEY` is set, this will call OpenAI ChatCompletion (gpt-3.5/4 family);
    otherwise it uses a simple rule-based fallback.
    """
    if not OPENAI_API_KEY:
        return _simple_summarize(incident, similar)

    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        # Compose prompt
        prompt = [
            {
                "role": "system",
                "content": "You are an incident response assistant. Given an incident and similar past incidents, propose a concise root cause, a short resolution summary, and a 3-step runbook to resolve and prevent recurrence."
            },
            {
                "role": "user",
                "content": (
                    f"Incident:\nTitle: {incident.get('title')}\nDescription: {incident.get('description')}\n"
                    f"Similar incidents:\n" + "\n".join([
                        f"- {s.get('title')}: root_cause={s.get('root_cause')}; resolution={s.get('resolution')}" for s in similar[:5]
                    ])
                ),
            },
        ]

        resp = openai.ChatCompletion.create(model=os.getenv("OPENAI_MODEL", "gpt-4o"), messages=prompt, max_tokens=400)
        text = resp["choices"][0]["message"]["content"].strip()
        # naive parsing: return the text as 'summary' and empty runbook/resolution if not structured
        return {"summary": text, "runbook": "", "resolution": ""}
    except Exception:
        return _simple_summarize(incident, similar)
