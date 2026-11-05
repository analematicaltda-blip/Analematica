# Godot 4.4 — Common Systems Reference

## Table of Contents
1. State Machine
2. Health / Damage Component
3. Inventory System
4. Top-down Movement + Animation
5. Platformer Movement (coyote time + jump buffer)
6. Object Pooling
7. Save / Load System
8. Smooth Camera

---

## 1. State Machine

Lightweight enum-based state machine (no node overhead):

```gdscript
# Attach to any node that needs states
class_name StateMachine extends Node

signal state_changed(old_state: int, new_state: int)

var current_state: int = -1

func transition_to(new_state: int) -> void:
    if new_state == current_state:
        return
    var old := current_state
    current_state = new_state
    state_changed.emit(old, new_state)
```

Usage in player:
```gdscript
enum State { IDLE, WALK, JUMP, FALL, ATTACK }

@onready var state_machine: StateMachine = $StateMachine

func _ready() -> void:
    state_machine.state_changed.connect(_on_state_changed)
    state_machine.transition_to(State.IDLE)

func _on_state_changed(old: int, new: int) -> void:
    match new:
        State.IDLE: sprite.play("idle")
        State.WALK: sprite.play("walk")
        State.JUMP: sprite.play("jump")
```

---

## 2. Health / Damage Component

Reusable component — add as child node to any entity:

**Scene:** `HealthComponent (Node)`

```gdscript
# HealthComponent.gd
class_name HealthComponent extends Node

signal health_changed(old_hp: int, new_hp: int)
signal died

@export var max_health: int = 100

var current_health: int:
    get: return _health
    
var _health: int

func _ready() -> void:
    _health = max_health

func take_damage(amount: int) -> void:
    if _health <= 0:
        return
    var old := _health
    _health = maxi(0, _health - amount)
    health_changed.emit(old, _health)
    if _health == 0:
        died.emit()

func heal(amount: int) -> void:
    var old := _health
    _health = mini(max_health, _health + amount)
    health_changed.emit(old, _health)

func is_alive() -> bool:
    return _health > 0
```

Usage:
```gdscript
@onready var health: HealthComponent = $HealthComponent

func _ready() -> void:
    health.died.connect(_on_died)

func _on_died() -> void:
    queue_free()
```

---

## 3. Inventory System

```gdscript
# ItemData.gd — Resource
class_name ItemData extends Resource

@export var id: String = ""
@export var display_name: String = ""
@export var max_stack: int = 99
@export var icon: Texture2D
@export var description: String = ""
```

```gdscript
# Inventory.gd — Node or Autoload
class_name Inventory extends Node

signal item_added(item: ItemData, amount: int)
signal item_removed(item: ItemData, amount: int)
signal inventory_changed

@export var capacity: int = 20

# Dict[String, int] — item id → quantity
var _items: Dictionary = {}

func add_item(item: ItemData, amount: int = 1) -> bool:
    var current: int = _items.get(item.id, 0)
    if current + amount > item.max_stack:
        return false
    _items[item.id] = current + amount
    item_added.emit(item, amount)
    inventory_changed.emit()
    return true

func remove_item(item: ItemData, amount: int = 1) -> bool:
    var current: int = _items.get(item.id, 0)
    if current < amount:
        return false
    _items[item.id] = current - amount
    if _items[item.id] == 0:
        _items.erase(item.id)
    item_removed.emit(item, amount)
    inventory_changed.emit()
    return true

func has_item(item_id: String, amount: int = 1) -> bool:
    return _items.get(item_id, 0) >= amount

func get_quantity(item_id: String) -> int:
    return _items.get(item_id, 0)
```

---

## 4. Top-down Movement + 8-dir Animation

**Scene:**
```
Player (CharacterBody2D)
├── CollisionShape2D (CapsuleShape2D or CircleShape2D)
└── AnimatedSprite2D
```

```gdscript
extends CharacterBody2D

@export var speed: float = 150.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

func _physics_process(_delta: float) -> void:
    var direction: Vector2 = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = direction * speed
    move_and_slide()
    _update_animation(direction)

func _update_animation(direction: Vector2) -> void:
    if direction == Vector2.ZERO:
        # Switch idle animation based on last facing direction
        sprite.play("idle_" + _direction_to_string(sprite.flip_h))
        return
    
    # Horizontal takes priority for flip
    if direction.x != 0:
        sprite.flip_h = direction.x < 0
    
    if absf(direction.x) > absf(direction.y):
        sprite.play("walk_side")
    elif direction.y < 0:
        sprite.play("walk_up")
    else:
        sprite.play("walk_down")

func _direction_to_string(flipped: bool) -> String:
    # Extend this for your specific idle animations
    return "side" if flipped else "side"
```

---

## 5. Platformer Movement (Coyote Time + Jump Buffer)

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0
@export var coyote_time: float = 0.15
@export var jump_buffer_time: float = 0.1

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _was_on_floor: bool = false

const GRAVITY: float = 980.0

func _physics_process(delta: float) -> void:
    # Gravity
    if not is_on_floor():
        velocity.y += GRAVITY * delta

    # Coyote time
    if _was_on_floor and not is_on_floor():
        _coyote_timer = coyote_time
    _was_on_floor = is_on_floor()
    _coyote_timer = maxf(0.0, _coyote_timer - delta)

    # Jump buffer
    if Input.is_action_just_pressed("jump"):
        _jump_buffer_timer = jump_buffer_time
    _jump_buffer_timer = maxf(0.0, _jump_buffer_timer - delta)

    # Execute jump
    var can_jump: bool = is_on_floor() or _coyote_timer > 0.0
    if _jump_buffer_timer > 0.0 and can_jump:
        velocity.y = jump_velocity
        _coyote_timer = 0.0
        _jump_buffer_timer = 0.0

    # Variable jump height (release early = lower jump)
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= 0.5

    # Horizontal movement
    var dir: float = Input.get_axis("ui_left", "ui_right")
    velocity.x = dir * speed

    move_and_slide()
```

---

## 6. Object Pooling

```gdscript
# ObjectPool.gd — Autoload or child node
class_name ObjectPool extends Node

@export var scene: PackedScene
@export var initial_size: int = 10

var _pool: Array[Node] = []

func _ready() -> void:
    for i in initial_size:
        _create_instance()

func _create_instance() -> Node:
    var instance: Node = scene.instantiate()
    instance.process_mode = Node.PROCESS_MODE_DISABLED
    instance.hide()
    add_child(instance)
    _pool.append(instance)
    return instance

func get_instance() -> Node:
    for instance in _pool:
        if not instance.visible:
            instance.show()
            instance.process_mode = Node.PROCESS_MODE_INHERIT
            return instance
    # Pool exhausted — grow it
    var new_instance := _create_instance()
    new_instance.show()
    new_instance.process_mode = Node.PROCESS_MODE_INHERIT
    return new_instance

func return_instance(instance: Node) -> void:
    instance.hide()
    instance.process_mode = Node.PROCESS_MODE_DISABLED
    # Reset position etc. if needed — call a reset() method on the instance
    if instance.has_method("reset"):
        instance.reset()
```

---

## 7. Save / Load System

```gdscript
# SaveSystem.gd — Autoload named "SaveSystem"
extends Node

const SAVE_PATH: String = "user://save.json"

func save(data: Dictionary) -> void:
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if file == null:
        push_error("SaveSystem: Cannot open file for writing: %s" % SAVE_PATH)
        return
    file.store_string(JSON.stringify(data, "\t"))

func load_save() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        return {}
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if file == null:
        push_error("SaveSystem: Cannot open file for reading: %s" % SAVE_PATH)
        return {}
    var json := JSON.new()
    var err := json.parse(file.get_as_text())
    if err != OK:
        push_error("SaveSystem: JSON parse error: %s" % json.get_error_message())
        return {}
    return json.get_data()

func delete_save() -> void:
    if FileAccess.file_exists(SAVE_PATH):
        DirAccess.remove_absolute(SAVE_PATH)
```

Usage:
```gdscript
# Saving
SaveSystem.save({
    "player_position": { "x": position.x, "y": position.y },
    "health": health.current_health,
    "inventory": inventory.get_all_items()
})

# Loading
var data: Dictionary = SaveSystem.load_save()
if data.is_empty():
    return  # No save file
position = Vector2(data["player_position"]["x"], data["player_position"]["y"])
```

---

## 8. Smooth Camera

**Scene:**
```
Camera2D
```

```gdscript
extends Camera2D

@export var target: NodePath
@export var smooth_speed: float = 5.0
@export var look_ahead_distance: float = 80.0
@export var use_look_ahead: bool = true

var _target_node: Node2D
var _last_target_pos: Vector2

func _ready() -> void:
    if target:
        _target_node = get_node(target)
        _last_target_pos = _target_node.global_position
    position_smoothing_enabled = false  # We handle this manually

func _physics_process(delta: float) -> void:
    if not is_instance_valid(_target_node):
        return
    
    var target_pos: Vector2 = _target_node.global_position
    
    if use_look_ahead and _target_node.has_method("get_velocity"):
        var vel: Vector2 = _target_node.get_velocity()
        target_pos += vel.normalized() * look_ahead_distance
    
    global_position = global_position.lerp(target_pos, smooth_speed * delta)
    _last_target_pos = _target_node.global_position
```
