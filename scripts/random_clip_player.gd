extends VideoStreamPlayer
## Plays the clips in a folder in random order, one after another, for as
## long as the slide is up. A clip is a video (Ogg Theora .ogv - convert
## other formats with tools/convert_clips.sh) or a still image, which is
## shown on the sibling "Still" node for image_seconds with a slow sway
## and a green radiation pulse.

## Folder holding the clips.
@export_dir var clip_dir: String = "res://videos/rads_multiball"
## How long a still image stays up before the next clip.
@export var image_seconds: float = 6.0

const VIDEO_EXTS := ["ogv"]
const IMAGE_EXTS := ["png", "jpg", "jpeg", "webp"]

var _clips: Array[String] = []
var _last: String = ""
var _image_left: float = 0.0
var _t: float = 0.0
@onready var _still: TextureRect = get_node_or_null("../Still")

func _ready() -> void:
	# list_directory sees through the .import/.remap files in an export
	for f in ResourceLoader.list_directory(clip_dir):
		var ext := f.get_extension().to_lower()
		if ext in VIDEO_EXTS or (_still and ext in IMAGE_EXTS):
			_clips.append(clip_dir.path_join(f))
	if _clips.is_empty():
		push_warning("random_clip_player: no clips in %s" % clip_dir)
		return
	var fallback := get_node_or_null("../Fallback")
	if fallback:
		fallback.visible = false
	finished.connect(_play_next)
	_play_next()

func _process(delta: float) -> void:
	if not _still or not _still.visible:
		return
	_t += delta
	_still.pivot_offset = _still.size / 2.0
	_still.rotation = sin(_t * 1.3) * 0.05
	var glow := 0.5 + 0.5 * sin(_t * 4.0)
	_still.modulate = Color(1.0 - 0.25 * glow, 1.0, 1.0 - 0.25 * glow)
	if _clips.size() > 1:
		_image_left -= delta
		if _image_left <= 0.0:
			_play_next()

func _play_next() -> void:
	var pick := _clips.pick_random() as String
	# don't repeat the clip that just played when there's a choice
	while _clips.size() > 1 and pick == _last:
		pick = _clips.pick_random()
	_last = pick
	if pick.get_extension().to_lower() in IMAGE_EXTS:
		stop()
		visible = false
		_still.texture = load(pick)
		_still.visible = true
		_image_left = image_seconds
	else:
		if _still:
			_still.visible = false
		visible = true
		stream = load(pick)
		play()
