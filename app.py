from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from assistant_engine import (
    analyze_task,
    call_llm_for_strategy,
    generate_class_puml,
    generate_sdlc_documents,
    generate_use_case_puml,
    validate_task_payload,
)


app = Flask(__name__)
CORS(app)

TASKS: list[dict] = []
NEXT_ID = 1


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok", service="ai-coursework-strategy-assistant"), 200


@app.get("/api/tasks")
def list_tasks():
    return jsonify(items=TASKS, count=len(TASKS)), 200


@app.post("/api/tasks")
def create_task():
    global NEXT_ID
    payload = request.get_json(silent=True) or {}
    task, error = validate_task_payload(payload)
    if error:
        return jsonify(error=error), 400

    strategy = analyze_task(task)
    item = {
        "id": NEXT_ID,
        "title": task.title,
        "deadline": task.deadline,
        "importance": task.importance,
        "complexity": task.complexity,
        "estimated_hours": task.estimated_hours,
        "notes": task.notes,
        "strategy": strategy,
    }
    NEXT_ID += 1
    TASKS.append(item)
    return jsonify(item=item), 201


@app.post("/api/strategy")
def strategy_preview():
    payload = request.get_json(silent=True) or {}
    task, error = validate_task_payload(payload)
    if error:
        return jsonify(error=error), 400
    deterministic_result = analyze_task(task)
    result = call_llm_for_strategy(task, deterministic_result)
    return jsonify(result), 200


@app.post("/api/sdlc-documents")
def sdlc_documents():
    payload = request.get_json(silent=True) or {}
    tasks = payload.get("tasks") if isinstance(payload.get("tasks"), list) else TASKS
    return jsonify(generate_sdlc_documents(tasks)), 200


@app.get("/api/uml/use-case")
def use_case_uml():
    return jsonify(format="plantuml", diagram=generate_use_case_puml()), 200


@app.get("/api/uml/class")
def class_uml():
    return jsonify(format="plantuml", diagram=generate_class_puml()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False)

