# Backend Contribution Guidelines

## Code Style

-   Follow **PEP 8** standards for Python code.
-   Use **Type Hints** where possible to improve readability.
-   Use `snake_case` for variables, functions, and database column names.
-   Use `PascalCase` for Class names (Models).

## Database Changes

-   **Models**: If you modify `models.py`, ensure you check if a migration validation is needed (currently using direct SQLite handling, so you may need to recreate the DB or use a migration script if added).
-   **Seeding**: If you add new models, update `seed.py` to include sample data for them.

## API Design

-   Follow **RESTful** principles.
-   Use appropriate HTTP status codes (200 for OK, 201 for Created, 400 for Bad Request, 500 for Server Error).
-   Return responses in JSON format.

## Error Handling

-   Use `try/except` blocks for database operations.
-   Ensure API errors return a consistent JSON structure, e.g., `{"error": "Description"}`.
