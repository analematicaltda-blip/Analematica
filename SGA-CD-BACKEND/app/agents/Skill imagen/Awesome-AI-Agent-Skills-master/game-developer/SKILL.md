---
name: game-developer
description: Game systems engineering, Unity/Unreal patterns, ECS architecture, and real-time performance optimization. Use for game logic design, AI, and graphics pipeline work.
---

# Game Developer

Engineering high-performance game mechanics and systems.

## Core Workflow

1. **Architecture Design**: ECS (Entity Component System) or clean Component patterns.
2. **Mechanics Implementation**: Physics, AI, and character controllers.
3. **Optimization**: Target 60+ FPS, profiling, and memory management.
4. **Graphics**: Shader work and rendering pipeline optimization.

## Key Constraints

- Maintain 60+ FPS (frame time ≤ 16.6ms).
- Use object pooling for frequent allocations.
- Implement LOD (Level of Detail) systems.
- Cache component references (avoid `GetComponent` in loops).

## Performance Standards

- Mandatory use of profiler (Unity Profiler / Unreal Insights).
- Minimize draw calls.
- Efficient spatial partitioning for collision/queries.

