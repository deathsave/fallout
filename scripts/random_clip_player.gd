extends VideoStreamPlayer
## Plays the video clips in a folder in random order, one after another,
## for as long as the slide is up. Godot only plays Ogg Theora (.ogv):
## convert other formats with tools/convert_clips.sh.

## Folder holding the .ogv clips.
@export_dir var clip_dir: String = "res://videos/rads_multiball"

var _clips: Array[String] = []
var _last: String = ""

func _ready() -> void:
	# list_directory sees through the .import/.remap files in an export
	for f in ResourceLoader.list_directory(clip_dir):
		if f.get_extension().to_lower() == "ogv":
			_clips.append(clip_dir.path_join(f))
	if _clips.is_empty():
		push_warning("random_clip_player: no .ogv clips in %s" % clip_dir)
		return
	finished.connect(_play_next)
	_play_next()

func _play_next() -> void:
	var pick := _clips.pick_random() as String
	# don't repeat the clip that just played when there's a choice
	while _clips.size() > 1 and pick == _last:
		pick = _clips.pick_random()
	_last = pick
	stream = load(pick)
	play()
