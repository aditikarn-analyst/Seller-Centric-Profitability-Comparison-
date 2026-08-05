"""Service layer — the pure, framework-free calculation engine.

Modules here depend only on ``app.core`` (money, constants) and receive plain
values, never database sessions or HTTP objects, so they are unit-testable in
isolation and reusable across the single-product and bulk paths.
"""
