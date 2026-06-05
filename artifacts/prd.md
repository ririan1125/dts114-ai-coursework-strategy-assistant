# Product Requirements Document

## Overview

The AI Coursework Strategy Assistant helps students convert coursework tasks, deadlines, importance, complexity, and available effort into an actionable strategy. It is a meta-software development tool because the system assists planning, requirements reasoning, risk control, and delivery decisions for other coursework or software tasks.

## Goals

- Convert vague coursework pressure into structured actions.
- Demonstrate AI-assisted SDLC artifact generation.
- Provide a working Flask API and browser interface.
- Support testing, version control, CI/CD, and deployment evidence.

## Non-Goals

- Replace the student's own academic judgement.
- Store private coursework data permanently.
- Guarantee grades or make decisions without human review.

## Personas

- Student: needs a clear and realistic plan before a deadline.
- AI Strategy Service: analyses structured task data and produces planning outputs.
- Module Tutor: evaluates whether SDLC, UML, AI tooling, testing, and deployment have been applied appropriately.

## Functional Requirements

- Accept task title, deadline, importance, complexity, estimated effort, and notes.
- Calculate priority score, risk flags, action strategy, milestones, and acceptance criteria.
- Generate SDLC documentation and PlantUML diagrams from the project context.
- Expose JSON API endpoints and a responsive website.

## Non-Functional Requirements

- Validate malformed user input.
- Avoid committing API keys or private data.
- Remain usable without an LLM API by falling back to deterministic logic.
- Include automated tests and CI workflow configuration.

## Success Metrics

- All required API endpoints return valid JSON.
- Tests pass locally and in GitHub Actions.
- The deployed website is accessible and displays the generated strategy image.
- The report can clearly justify SDLC, UML, CI/CD, deployment, and AI-tool decisions.

