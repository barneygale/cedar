# cedar

cedar will generate a new minecraft map, then cartograph it.

## usage

cedar requires python 2.7 and java

run `python cedar.py --help` for a list of options

## examples

cartograph a random seed:

    python cedar.py

cartograph a given seed, using an existing server jar

    python cedar.py --seed gargamel --jar /path/to/minecraft_server.jar

cartograph a random seed around (350, -500), radius 500

    python cedar.py --center 350,-500 --radius 500

## upcoming features

* biome tints
* terrain shading
* terrain undulation (edge detection)
* semitransparent water (iterate down)
* semitransparent blocks (iterate up)
* option to hide snow

## thanks

* Tyler Kennedy for [PyNBT](https://github.com/TkTech/PyNBT)
* David Jones for [pypng](https://github.com/drj11/pypng)