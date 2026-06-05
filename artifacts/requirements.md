# Requirements

## Functional Requirements

1. The system shall allow a student to enter a coursework task with deadline, importance, complexity, estimated hours, and notes.
2. The system shall return an action strategy with priority score, risk flags, milestones, and acceptance criteria.
3. The system shall expose a Flask API for task creation, strategy preview, SDLC document generation, and UML retrieval.
4. The system shall provide a website that consumes the Flask API.
5. The website shall display at least one automatically generated image.
6. The notebook shall generate SDLC artifacts, UML artifacts, code, tests, and deployment configuration.

## Non-Functional Requirements

1. The API shall validate invalid input and return clear JSON errors.
2. The interface shall be responsive on desktop and mobile.
3. The project shall not commit real API keys.
4. The software shall be testable through automated pytest tests.
5. The deployment route shall support Render, Docker, and local execution.

