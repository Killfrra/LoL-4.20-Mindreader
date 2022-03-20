extends Node2D

"""
class Circle:
	var position: Vector2
	var radius: float
	func _init(pos, rad):
		position = pos
		radius = rad
"""

var records: Dictionary

export var game_time: float = -1.0 #1647611294
export var game_time_offset: float = 4
export(String, FILE, "*.json") var record_file := "res://records_4_config_2.json"
const Z := 2
export var speed := 1
export var draw_off_course := true
export var draw_speeds := true
export var draw_tails := true

func _ready():
	var file = File.new()
	file.open(record_file, file.READ)
	var text = file.get_as_text()
	var result := JSON.parse(text)
	records = result.result
	file.close()
	print('loaded ', text.length(), ' chars')
	if result.error:
		print('error at ', result.error_line, ': ', result.error_string)
		return
	
	if game_time == -1:
		for netid in records:
			var obj = records[netid]
			var type = obj.get('type', 'unknown')
			if type != 'lane_minion':
				continue
				
			var time = obj['positions'][0][0]
			if game_time == -1 or time < game_time:
				game_time = time + game_time_offset

		print(game_time)

	for netid in records:
		var obj = records[netid]
		var type = obj.get('type', 'unknown')
		var radius := 35.7437
		
		if type != 'lane_minion':
			continue
		
		if 'positions' in obj:
			
			var positions = obj['positions']
			
			var converted = []
			for i in range(positions.size()):
				converted.append({ 'time': positions[i][0], 'pos': Vector2(positions[i][1][0], positions[i][1][Z]) })
			
			var velocities = []
			for i in range(1, converted.size()):
				var prev_time = converted[i - 1]['time']
				var prev_pos = converted[i - 1]['pos']
				var time = converted[i]['time']
				var pos = converted[i]['pos']
				var del = (time - prev_time)
				var vel = (pos - prev_pos) * 25 #/ del
				velocities.append({ 'vel': vel, 'del': del })
				
			var accelerations = []
			for i in range(1, velocities.size()):
				var prev_vel = velocities[i - 1]['vel']
				var vel = velocities[i]['vel']
				var del = velocities[i]['del']
				var acc = (vel - prev_vel) * 25 #/ del
				accelerations.append(acc)
				
			var max_acc = 0
			for i in range(accelerations.size() - 1):
				var acc = accelerations[i]
				var acc_len = acc.length()
				if acc_len > max_acc:
					max_acc = acc_len
			print('max acceleration for ', netid, ' = ', max_acc)
			
			var max_vel = 0
			for dict in velocities:
				var vel = dict['vel']
				var vel_len = vel.length()
				if vel_len > max_vel:
					max_vel = vel_len
			print('max velocity for ', netid, ' = ', max_vel)


var window_size := 884.0
func get_scale():
	return window_size / 16000.0 * zoom

func to_screen(v):
	var _scale = get_scale()
	var offset := (window_size - window_size * zoom) * 0.5
	return Vector2(v.x * _scale + offset - pad.x, window_size - (v.y * _scale + offset + pad.y))

func from_screen(v):
	var _scale = get_scale()
	var offset := (window_size - window_size * zoom) * 0.5
	return Vector2((v.x + pad.x - offset) / _scale, (window_size - v.y - pad.y - offset) / _scale)

var type2color = {
	'unknown': Color.white,
	'lane_minion': Color.red,
	'champion': Color.orangered,
	'monster': Color.orange,
	'minion': Color.green,
	'region': Color.blue
}

func dist_to_segment_squared(p: Vector2, v: Vector2, w: Vector2):
	if v == w:
		return p.distance_squared_to(v)
	var l2 = v.distance_squared_to(w)
	var t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
	t = clamp(t, 0, 1)
	return p.distance_squared_to(Vector2(v.x + t * (w.x - v.x), v.y + t * (w.y - v.y)))

var first_update := true
func _draw():
	var _scale = get_scale()
	
	for netid in records:
		
		var obj = records[netid]
		var type = obj.get('type', 'unknown')
		var color = type2color.get(type, Color.white)
		var radius := 35.7437
		
		if type != 'lane_minion':
			continue
		
		if 'waypoints' in obj:
			var groups = obj['waypoints']
			for i in range(groups.size() - 1, -1, -1):
				var group = groups[i]
				var time: float = group[0]
				if time <= game_time:
					var prev_pos = null
					for wp in group[1]:
						var pos = Vector2(wp[0], wp[1])
						if prev_pos != null:
							draw_line(to_screen(prev_pos), to_screen(pos), Color.darkslategray)
						prev_pos = pos
					break
					
		if 'positions' in obj:
			var prev_time = null
			var prev_pos  = null
			for waypoint in obj['positions']:
				var time: float = waypoint[0]
				var pos := Vector2(waypoint[1][0], waypoint[1][Z])

				if time >= game_time:
					if prev_time != null and prev_pos != null:
						var t: float = (game_time - prev_time) / (time - prev_time)
						var lerped_pos: Vector2 = lerp(prev_pos, pos, t)
						#draw_circle(to_screen(lerped_pos), radius * _scale, color)
						if draw_tails:
							draw_line(to_screen(prev_pos), to_screen(lerped_pos), Color.white)
						if 'waypoints' in obj:
							var group1 = obj['waypoints'][0][1]
							var wp2 = Vector2(group1[1][0], group1[1][1])
							draw_line(to_screen(lerped_pos), to_screen(lerped_pos + 100 * (wp2 - lerped_pos).normalized()), Color.red)
							
							#var vel: Vector2 = (pos - prev_pos).normalized()
							#var seek: Vector2 = (wp2 - prev_pos).normalized()
							#draw_line(to_screen(lerped_pos), to_screen(lerped_pos + 100 * (vel - seek)), Color.blue)
						
						if draw_speeds:
							var vel: Vector2 = pos - prev_pos
							var vel_norm := vel.normalized()
							draw_line(to_screen(lerped_pos), to_screen(lerped_pos + 100 * vel_norm), Color.darkgreen)
							var delta := 1.0 / 25.0 #(time - prev_time)
							draw_line(to_screen(lerped_pos), to_screen(lerped_pos + 100 * vel_norm * (vel.length() / (325.0 * delta))), Color.green)
						
						draw_arc(to_screen(lerped_pos), radius * _scale, 0, TAU, 36, color)
						
					break
					
				if draw_tails and prev_pos != null:
					draw_line(to_screen(prev_pos), to_screen(pos), Color.white)
				
				prev_time = time
				prev_pos = pos
				
		if draw_off_course and 'positions' in obj and 'waypoints' in obj:
			var group1 = obj['waypoints'][0][1]
			if group1.size() > 1:
				var wp1 := Vector2(group1[0][0], group1[0][1])
				var wp2 := Vector2(group1[1][0], group1[1][1])
				var prev_pos = null
				var off_the_path := false
				for position in obj['positions']:
					var pos := Vector2(position[1][0], position[1][Z])
					if prev_pos != null && off_the_path != (dist_to_segment_squared(pos, wp1, wp2) > 0.005):
						draw_arc(to_screen(prev_pos), 10 * _scale, 0, TAU, 36, Color.green)
						off_the_path = !off_the_path
						if first_update && off_the_path:
							print("Went off the path at ", prev_pos)
							var mid := Vector2(6991.43408203125, 7223.34375)
							var dist := mid.distance_squared_to(prev_pos)
							print('Dist to mid ', sqrt(dist), '^2 = ', dist)
					prev_pos = pos
				
	first_update = false

var just_paused := true
func _process(delta):
	if !_paused:
		just_paused = true
		game_time += delta * speed
		$"../Time".text = str(floor(game_time))
		_update()
	elif just_paused:
		just_paused = false
		$"../Time".text = str(game_time)
		
signal update()
func _update():
	update()
	emit_signal("update")

# https://www.gdquest.com/tutorial/godot/2d/camera-zoom/
# https://www.braindead.bzh/entry/godot-interactive-camera2d

export var zoom := 8.0
export var pad := Vector2(-480, 379)

#export
var min_zoom := 1.0
#export
var max_zoom := INF
# Controls how much we increase or decrease the `_zoom_level` on every turn of the scroll wheel.
#export
var zoom_factor := 0.1
# Duration of the zoom's tween animation.
#export
var zoom_duration := 0.2

# The camera's target zoom level.
var _zoom_level := zoom setget _set_zoom_level

# We store a reference to the scene's tween node.
onready var tween: Tween = $Tween

func _set_zoom_level(value: float) -> void:
	_zoom_level = clamp(value, min_zoom, max_zoom)
	tween.interpolate_property(
		self, "zoom", zoom,
		_zoom_level,
		zoom_duration, tween.TRANS_SINE, tween.EASE_OUT
	)
	tween.start()
	
func _set_pad(value: Vector2):
	pad = value
	"""
	tween.interpolate_property(
		self,
		"pad",
		pad,
		value,
		zoom_duration,
		tween.TRANS_SINE,
		tween.EASE_OUT
	)
	tween.start()
	"""

var _drag := false
var _paused := false
func _unhandled_input(event):
	
	if event.is_action_pressed("cam_drag"):
		_drag = true
	elif event.is_action_released("cam_drag"):
		_drag = false
	
	elif event.is_action_pressed("zoom_in"):
		_set_zoom_level(_zoom_level - zoom_factor * _zoom_level)
		_set_pad(pad - zoom_factor * pad)
		if _paused:
			_update()
	elif event.is_action_pressed("zoom_out"):
		_set_zoom_level(_zoom_level + zoom_factor * _zoom_level)
		_set_pad(pad + zoom_factor * pad)
		if _paused:
			_update()

	elif event.is_action_pressed("toggle_playback"):
		_paused = !_paused
	
	elif event is InputEventMouseMotion:
		$"../Position".text = str(from_screen(event.position))
		if _drag:
			_set_pad(pad - event.relative)
			if _paused:
				_update()
		
