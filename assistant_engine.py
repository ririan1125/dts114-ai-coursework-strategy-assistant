"""Core planning logic for the AI Coursework Strategy Assistant.

The deterministic engine keeps the application useful without an API key. When
DEEPSEEK_API_KEY is available, the Flask API can request an LLM critique and
merge it into the same response structure.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover - optional dependency guard
    requests = None


@dataclass
class CourseworkTask:
    title: str
    deadline: str
    importance: int
    complexity: int
    estimated_hours: float
    notes: str = ""


def _parse_deadline(value: str) -> datetime | None:
    if not value:
        return None
    clean = value.strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(clean[:16] if "T" in clean else clean, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        parsed = datetime.fromisoformat(clean)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def validate_task_payload(payload: dict[str, Any]) -> tuple[CourseworkTask | None, str | None]:
    title = str(payload.get("title", "")).strip()
    deadline = str(payload.get("deadline", "")).strip()
    notes = str(payload.get("notes", "")).strip()

    if not title:
        return None, "title is required"
    if not _parse_deadline(deadline):
        return None, "deadline must be a valid date or datetime"

    try:
        importance = int(payload.get("importance", 3))
        complexity = int(payload.get("complexity", 3))
        estimated_hours = float(payload.get("estimated_hours", 2))
    except (TypeError, ValueError):
        return None, "importance, complexity, and estimated_hours must be numeric"

    if not 1 <= importance <= 5:
        return None, "importance must be between 1 and 5"
    if not 1 <= complexity <= 5:
        return None, "complexity must be between 1 and 5"
    if estimated_hours <= 0 or estimated_hours > 200:
        return None, "estimated_hours must be between 0 and 200"

    return CourseworkTask(title, deadline, importance, complexity, estimated_hours, notes), None


def analyze_task(task: CourseworkTask) -> dict[str, Any]:
    deadline = _parse_deadline(task.deadline)
    now = datetime.now(timezone.utc)
    hours_left = max(0.0, (deadline - now).total_seconds() / 3600) if deadline else 0.0
    days_left = hours_left / 24

    urgency = 100 if hours_left <= 24 else max(5, int(100 - min(days_left, 30) * 3))
    workload_pressure = min(100, int(task.estimated_hours / max(hours_left, 1) * 100))
    priority_score = min(
        100,
        int(task.importance * 13 + task.complexity * 9 + urgency * 0.35 + workload_pressure * 0.25),
    )

    if priority_score >= 82:
        priority_label = "critical"
    elif priority_score >= 66:
        priority_label = "high"
    elif priority_score >= 45:
        priority_label = "medium"
    else:
        priority_label = "low"

    risk_flags: list[str] = []
    if hours_left <= 24:
        risk_flags.append("Deadline is within 24 hours; reduce scope and protect submission time.")
    if workload_pressure >= 70:
        risk_flags.append("Estimated workload is high compared with remaining time.")
    if task.complexity >= 4:
        risk_flags.append("Complexity is high; define acceptance criteria before coding.")
    if task.importance >= 4:
        risk_flags.append("High mark impact; schedule an independent review pass.")
    if not risk_flags:
        risk_flags.append("No immediate risk detected; keep routine progress checkpoints.")

    return {
        "title": task.title,
        "priority_label": priority_label,
        "priority_score": priority_score,
        "hours_left": round(hours_left, 1),
        "estimated_hours": task.estimated_hours,
        "recommended_sdlc": "Agile iterative delivery with AI-assisted inception, construction, testing, and operation checkpoints",
        "strategy": build_action_strategy(task, priority_label),
        "milestones": build_milestones(task, hours_left),
        "risk_flags": risk_flags,
        "acceptance_criteria": build_acceptance_criteria(task),
        "user_story": f"As a student, I want a clear action strategy for {task.title} so that I can submit high-quality work before the deadline.",
    }


def build_action_strategy(task: CourseworkTask, priority_label: str) -> list[str]:
    base = [
        "Clarify the marking criteria and convert them into a checklist.",
        "Break the task into deliverable slices: evidence, implementation, testing, and final packaging.",
        "Start with the highest-mark and highest-risk item before cosmetic improvements.",
        "Run a short verification cycle after every major change.",
        "Reserve final time for screenshots, references, naming, and upload checks.",
    ]
    if priority_label in {"critical", "high"}:
        base.insert(0, "Freeze optional scope and complete the minimum high-mark evidence first.")
    return base


def build_milestones(task: CourseworkTask, hours_left: float) -> list[dict[str, str]]:
    if hours_left <= 24:
        windows = ["0-2h", "2-6h", "6-10h", "10-14h", "final 2h"]
    elif hours_left <= 72:
        windows = ["today", "next session", "midpoint", "day before deadline", "final upload"]
    else:
        windows = ["inception", "prototype", "implementation", "validation", "release"]
    names = [
        "Rubric checklist",
        "Working prototype",
        "Complete implementation",
        "Testing and evidence",
        "Submission package",
    ]
    return [{"window": window, "goal": name} for window, name in zip(windows, names)]


def build_acceptance_criteria(task: CourseworkTask) -> list[str]:
    return [
        f"The plan names the deadline and priority for {task.title}.",
        "The next action is concrete enough to start within 15 minutes.",
        "The task is split into testable milestones.",
        "Risk flags are visible before the student commits to a schedule.",
        "The output can be saved and reviewed later.",
    ]


def generate_sdlc_documents(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    titles = [str(item.get("title", "Untitled task")) for item in tasks] or ["Coursework planning task"]
    return {
        "problem_statement": (
            "Students often know their deadlines but struggle to convert coursework constraints, "
            "marking criteria, and available time into an executable study or development strategy."
        ),
        "personas": [
            {"role": "Student", "needs": "Prioritised coursework actions and risk warnings."},
            {"role": "AI Strategy Service", "needs": "Structured task data to produce reliable plans."},
            {"role": "Module Tutor", "needs": "Evidence that the system follows SDLC, testing, and deployment practices."},
        ],
        "functional_requirements": [
            "The system shall accept coursework title, deadline, importance, complexity, and estimated effort.",
            "The system shall calculate priority, risks, milestones, and acceptance criteria.",
            "The system shall expose Flask API endpoints and a browser-based interface.",
            "The system shall generate SDLC documentation and UML artifacts from the same project context.",
        ],
        "non_functional_requirements": [
            "The API shall validate malformed input and return clear JSON errors.",
            "The interface shall remain readable on desktop and mobile screens.",
            "The design shall avoid storing API keys or sensitive coursework data in the repository.",
            "The project shall include automated tests and CI workflow evidence.",
        ],
        "user_stories": [
            {
                "id": index + 1,
                "role": "Student",
                "goal": f"receive an action strategy for {title}",
                "benefit": "I can focus on the next best step instead of guessing.",
            }
            for index, title in enumerate(titles[:5])
        ],
        "api_endpoints": [
            "GET /health",
            "GET /api/tasks",
            "POST /api/tasks",
            "POST /api/strategy",
            "POST /api/sdlc-documents",
            "GET /api/uml/use-case",
        ],
    }


def generate_use_case_puml() -> str:
    return """@startuml
left to right direction
actor Student
actor "AI Strategy Service" as AI
actor "Deployment Engineer" as DevOps

rectangle "AI Coursework Strategy Assistant" {
  usecase "Add Coursework Task" as UC1
  usecase "Analyse Priority" as UC2
  usecase "Generate Action Plan" as UC3
  usecase "Create SDLC Documents" as UC4
  usecase "Review UML Artifacts" as UC5
  usecase "Run CI Tests" as UC6
  usecase "Deploy Website" as UC7
}

Student -- UC1
Student -- UC2
Student -- UC3
Student -- UC4
Student -- UC5
AI -- UC2
AI -- UC3
AI -- UC4
DevOps -- UC6
DevOps -- UC7
UC3 ..> UC2 : <<include>>
UC4 ..> UC1 : <<include>>
@enduml
"""


def generate_class_puml() -> str:
    return """@startuml
class CourseworkTask {
  +title: str
  +deadline: str
  +importance: int
  +complexity: int
  +estimated_hours: float
  +notes: str
}

class StrategyEngine {
  +validate_task_payload(payload)
  +analyze_task(task)
  +generate_sdlc_documents(tasks)
}

class FlaskAPI {
  +GET /health
  +POST /api/tasks
  +POST /api/strategy
  +POST /api/sdlc-documents
}

class BrowserUI {
  +submitTask()
  +renderStrategy()
  +renderDocuments()
}

BrowserUI --> FlaskAPI
FlaskAPI --> StrategyEngine
StrategyEngine --> CourseworkTask
@enduml
"""


def call_llm_for_strategy(task: CourseworkTask, deterministic_result: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or requests is None:
        return deterministic_result | {"llm_used": False, "llm_note": "Deterministic fallback used."}

    prompt = {
        "task": asdict(task),
        "deterministic_strategy": deterministic_result,
        "instruction": (
            "Critique the strategy for feasibility. Return compact JSON with keys: "
            "llm_summary, improvement, caution. Do not include private data."
        ),
    }
    try:
        response = requests.post(
            os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com").rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "messages": [
                    {"role": "system", "content": "You are a concise software-engineering study planner."},
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
                "temperature": 0.2,
                "max_tokens": 350,
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        try:
            llm_json = json.loads(content)
        except json.JSONDecodeError:
            llm_json = {"llm_summary": content[:500], "improvement": "", "caution": ""}
        return deterministic_result | {"llm_used": True, "llm_review": llm_json}
    except Exception as exc:
        return deterministic_result | {
            "llm_used": False,
            "llm_note": f"LLM unavailable, deterministic fallback used: {type(exc).__name__}",
        }

