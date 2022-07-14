# Kanimaji #

## Generation of animations ##

This is a small utility for transforming KanjiVG images into animated SVGs.

 * SVG samples (animated via CSS, no SMIL/<animate> element):

![084b8 SVG](http://maurimo.github.io/kanimaji/samples/084b8_anim.svg)
![08972 SVG](http://maurimo.github.io/kanimaji/samples/08972_anim.svg)

## Dependencies ##

Kanimaji depends on
 * [Python 3]() with lxml support.
 * [svg.path](https://pypi.python.org/pypi/svg.path) Python library, for approximating path lengths.

## Usage ##

Just run
```
./kanimaji.py file1.svg file2.svg ...
```
where the files are KanjiVG SVG files (could work with other SVG files, but it hasn't been tested).

## Settings ##

Just edit the settings.py file, all settings are explained there.

## License ##

This software is formally released under MIT/BSD (at your option).
You are free to do what you want with this program, please credit my work if you use it.
If you find it useful and feel like, you may give a donation on my github page!
