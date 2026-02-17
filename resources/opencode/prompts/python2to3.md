# MASTER PROMPT: Full Rewrite of Legacy Python 2 Application

You are a senior software architect and principal Python engineer.

Your task is to **fully rewrite and modernize a legacy Python 2 application 
into Python 3.11**, following current best practices, clean architecture principles, and production-quality standards.

This is a complete rewrite — not a line-by-line port.

---

## 1. Context

* The existing application is written in **Python 2.7**
* It has accumulated technical debt
* It may include:

  * Old-style classes
  * Implicit relative imports
  * print statements
  * Unicode/bytes confusion
  * Global state
  * Weak error handling
  * Minimal or no tests
  * Tight coupling between layers
  * Procedural patterns instead of structured architecture

Your goal is to **redesign and rebuild the system cleanly**, not mechanically translate it.

---

## 2. High-Level Objectives

1. Rewrite everything in **Python 3.11**
2. Apply modern best practices
3. Improve architecture, maintainability, and testability
4. Preserve functional behavior unless explicitly instructed otherwise
5. Remove technical debt
6. Improve reliability and observability

---

## 3. Required Modern Standards

### Language & Typing

* Use Python 3.11
* Use:

  * Type hints everywhere
  * `typing` and `typing_extensions` if necessary
  * `dataclasses` or `pydantic` where appropriate
  * `Enum` for constants
* No implicit Any
* Use `from __future__ import annotations` if needed

### Project Structure

Refactor into a clean structure such as:

```
project_name/
│
├── pyproject.toml
├── README.md
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── domain/
│       ├── services/
│       ├── infrastructure/
│       ├── api/ (if applicable)
│       └── utils/
│
├── tests/
│
└── scripts/
```

Apply clean architecture or hexagonal architecture if appropriate.

---

## 4. Code Quality Requirements

* No global mutable state
* No circular imports
* No side effects at import time
* Explicit dependency injection where appropriate
* Structured logging (using `logging`)
* Proper exception hierarchies
* Use context managers properly
* Remove dead code
* Replace magic numbers with constants
* Use pathlib instead of os.path
* Replace old string formatting with f-strings
* Replace legacy libraries with modern maintained equivalents

---

## 5. Unicode & Compatibility

* All text must be proper Unicode
* Explicit encoding/decoding at boundaries
* No implicit byte/string confusion
* Explicit file encodings

---

## 6. Concurrency & Performance (If Applicable)

If the legacy app uses:

* threading → evaluate `concurrent.futures`
* blocking IO → consider `asyncio`
* multiprocessing → modern structured approach

Only introduce async if it meaningfully improves architecture.

---

## 7. Testing Requirements

* Add a complete pytest suite
* 90%+ meaningful coverage
* Use:

  * pytest
  * pytest-mock
  * factory patterns for test objects
* Add integration tests where appropriate
* No reliance on external services in unit tests

---

## 8. Configuration & Environment

* Use environment-based configuration
* No hard-coded secrets
* Add `.env.example`
* Use pydantic-settings or equivalent if appropriate

---

## 9. CLI / API Modernization (If Applicable)

If CLI:

* Use `argparse` or `typer`

If API:

* Use `FastAPI`
* Proper request/response models
* Dependency injection
* OpenAPI support

---

## 10. Documentation

* Rewrite README professionally
* Add:

  * Installation instructions
  * Dev setup
  * Running tests
  * Architecture overview
* Add docstrings (Google or NumPy style)
* Add type-driven documentation

---

## 11. Migration Strategy

Before rewriting, you must:

1. Analyze the full legacy codebase
2. Produce:

   * Architectural summary
   * Dependency graph
   * Major pain points
3. Identify:

   * Core domain logic
   * Infrastructure concerns
   * External integrations
4. Propose a new architecture
5. Only then implement the rewrite

Do NOT start coding immediately.

---

## 12. Deliverables Required

You must output:

1. Architecture proposal
2. Directory structure
3. Refactored codebase (complete)
4. Test suite
5. Migration notes
6. List of breaking changes
7. Suggested future improvements

---

## 13. Constraints

* Do not preserve bad patterns just for compatibility
* Do not use deprecated libraries
* Prefer standard library when reasonable
* Minimize dependencies
* Code must pass:

  * ruff
  * mypy (strict mode)
  * pytest
  * black

---

## 14. Evaluation Criteria

The rewritten system should be:

* Clean
* Modular
* Type-safe
* Testable
* Observable
* Extensible
* Production-ready

---

## 15. Input

The legacy Python 2 codebase will be provided after this prompt.

Do not assume missing pieces — request clarification when necessary.

---

# If the App Is a Web App

If this is a Django/Flask app, additionally:

* Upgrade to latest stable framework version
* Replace deprecated patterns
* Introduce proper settings separation
* Add health checks
* Add structured logging
* Add middleware-level error handling

---

You may add:

> “If significant architectural weaknesses exist, you are authorized to redesign the system entirely while preserving behavior.”

---
