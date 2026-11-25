fallout
=======

[![Fallout Pinball](https://github.com/deathsave/fallout/actions/workflows/python-app.yml/badge.svg)](https://github.com/deathsave/fallout/actions/workflows/python-app.yml)

fallout pinball bitches

![Attract Slide](https://raw.githubusercontent.com/deathsave/fallout/refs/heads/main/images/attract_screen1.gif)

Requirements
------------

- [Mission Pinball Framework](https://missionpinball.org) 0.80 (`pip install 'mpf==0.80.*'`)
- [Godot 4](https://godotengine.org) for the display/sound (Godot MC). The GMC
  addon is vendored in `addons/mpf-gmc`. Put `godot` on your PATH or set
  `GODOT_BIN`.

Displays live in Godot scenes: `window.tscn`, `slides/` and `widgets/`. Sound
buses are in `default_bus_layout.tres` + `gmc.cfg`, keyboard mappings in `gmc.cfg`.
Open the project folder in Godot to edit slides.

Running the Game
----------------

- Production: `bin/run`
- Development: `bin/dev`
- Test Suite: `bin/test`

![fallout pinball](https://github.com/deathsave/fallout/raw/main/monitor/playfield.jpg)
