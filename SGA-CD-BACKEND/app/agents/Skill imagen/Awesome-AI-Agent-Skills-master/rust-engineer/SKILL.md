---
name: rust-engineer
description: Idiomatic Rust 2021 engineering, focusing on memory safety, zero-cost abstractions, and robust error handling. Use for Rust system design, debugging, and optimization.
---

# Rust Engineer

Expert guidance for writing high-performance, safe, and idiomatic Rust code.

## Core Workflow

1. **Ownership Analysis**: Clearly define data ownership and lifetimes.
2. **Trait-based Design**: Use traits for abstraction and polymorphism.
3. **Explicit Error Handling**: Use `Result` and `Option` with `thiserror` or `anyhow`.
4. **Performance**: Zero-cost abstractions and careful use of allocations.

## Constraints

- Use Rust 2021 edition features.
- Mandatory use of `cargo clippy` and `cargo fmt`.
- `unwrap()` and `expect()` are prohibited in production code (use proper error handling).
- Prefer `stack` over `heap` where possible.

## Best Practices

- Use `match` and `if let` for pattern matching.
- Leverage the type system to enforce invariants.
- Keep `unsafe` blocks minimal and well-documented.
- Write unit and integration tests for all modules.

