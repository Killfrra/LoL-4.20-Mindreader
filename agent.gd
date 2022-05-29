class_name SteeringAgent
extends Node2D

export var pos: Vector2
export var radius: float = 35.7437
export var color: Color
export var obstacle: bool = false
export var target_pos: Vector2
export var speed_max: float = 325.0
export var accel_max: float = 190.39032
export(float, 0, 1) var drag: float = 0
export var _neighbor: NodePath
onready var neighbor: SteeringAgent = get_node(_neighbor)

onready var parent = get_parent()
func _ready():
	parent.connect("update", self, "_update")

var velocity := Vector2.ZERO
var accel := Vector2.ZERO

var positions = []
var first_frame := true
func _physics_process(delta: float):
	if obstacle:
		return

#	accel = seeking()
#	accel += avoidance()
#	velocity = (velocity + accel * delta).clamped(speed_max)

	if first_frame:
		first_frame = false
		velocity = (target_pos - pos).normalized() * speed_max
	else:
		#accel = seeking()
		accel = avoidance()
		if accel.length_squared() == 0:
			accel = seeking()
		
		velocity = (velocity + accel * delta).clamped(speed_max)
		#velocity = (velocity + accel * delta).normalized() * speed_max
		velocity = velocity.linear_interpolate(Vector2.ZERO, drag)
	
	pos += velocity * delta
	
	positions.append(pos)

func _update():
	update()

func _draw():

	var prev_pos = null
	for pos in positions:
		if prev_pos != null:
			draw_line(parent.to_screen(pos), parent.to_screen(prev_pos), Color.darkgray)
		prev_pos = pos
	
	var scale = parent.get_scale()
	draw_arc(parent.to_screen(pos), radius * scale, 0, TAU, 36, color)

func seeking() -> Vector2:
	var acceleration := Vector2.ZERO
	acceleration = (target_pos - pos).normalized() * accel_max
	return acceleration

func avoidance() -> Vector2:
	var acceleration := Vector2.ZERO
	
	var dist_to_mid_sq := 16606.912109
	if pos.distance_squared_to(neighbor.pos) >= dist_to_mid_sq:
		return acceleration
	
	var _first_neighbor: SteeringAgent = null
	var _shortest_time: float = INF
	var _first_minimum_separation: float = 0
	var _first_distance: float = 0
	var _first_relative_position: Vector2
	var _first_relative_velocity: Vector2
	
	var relative_position := neighbor.pos - pos
	var relative_velocity := neighbor.velocity - velocity
	var relative_speed_squared := relative_velocity.length_squared()

	if relative_speed_squared == 0:
		pass #return false
	else:
		var time_to_collision := -relative_position.dot(relative_velocity) / relative_speed_squared

		if time_to_collision <= 0 or time_to_collision >= _shortest_time:
			pass #return false
		else:
			var distance := relative_position.length()
			var minimum_separation: float = distance - sqrt(relative_speed_squared) * time_to_collision
			if minimum_separation > radius + neighbor.radius:
				pass #return false
			else:
				_shortest_time = time_to_collision
				_first_neighbor = neighbor
				_first_minimum_separation = minimum_separation
				_first_distance = distance
				_first_relative_position = relative_position
				_first_relative_velocity = relative_velocity
				pass #return true
	
	if _first_neighbor:
		if (
			_first_minimum_separation <= 0
			or _first_distance < radius + _first_neighbor.radius
		):
			acceleration = _first_neighbor.pos - pos
		else:
			acceleration = _first_relative_position + (_first_relative_velocity * _shortest_time)

	acceleration = acceleration.normalized() * -accel_max
	
	return acceleration
