extends Window
## Hosts display2 in its own OS window on the second monitor.
##
## Slides are laid out at 1920x1080 and scaled to fit the monitor. On the
## Linux cabinet the window goes fullscreen on the second screen (if there
## is one); elsewhere (the dev Mac) it stays a normal resizable window.

## Screen index of the second monitor (0 = primary).
@export var target_screen: int = 1

func _ready() -> void:
	content_scale_size = Vector2i(1920, 1080)
	content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	# Only take over a whole screen when the second monitor is really there;
	# otherwise a fullscreen window would land on (and hide) monitor 1.
	if OS.get_name() == "Linux" and DisplayServer.get_screen_count() > target_screen:
		current_screen = target_screen
		borderless = true
		mode = Window.MODE_FULLSCREEN
	# keyboard input (dev switch keys) should still reach GMC from this window
	window_input.connect(func(event): get_tree().root.push_input(event))
