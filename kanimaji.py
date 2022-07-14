#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, sys, json
from lxml import etree
from lxml.builder import E
from svg.path import parse_path
from os.path import basename
from copy import deepcopy
from textwrap import dedent as d
from settings import *

def compute_path_len(path):
	return parse_path(path).length(error=1e-8)

def shescape(path):
	return "'"+re.sub(r"(?=['\\\\])","\\\\",path)+"'"

TIMING_FUNCTION = "ease-in-out"

# we will need this to deal with svg
namespaces = {'n': "http://www.w3.org/2000/svg"}
etree.register_namespace("kvg", "kvg")
etree.register_namespace("d", "d")
etree.register_namespace("style", "style")
parser = etree.XMLParser(remove_blank_text=True)

def create_animation(filename):
	print('processing %s' % filename)
	filename_noext = re.sub(r'\.[^\.]+$','',filename)
	baseid = basename(filename_noext)

	# load xml
	doc = etree.parse(filename, parser)

	# for xlink namespace introduction
	doc.getroot().set('{kvg}used','')
	doc.getroot().set('{d}used','')
	doc.getroot().set('{style}used','')

	#clear all extra elements this program may have previously added
	for g in doc.xpath("/n:svg/n:g", namespaces=namespaces):
		if re.match( r'kvg:StrokeNumbers_', g.get('id')):
			doc.getroot().remove(g)

	# create groups with a copies (references actually) of the paths
	bg_g = E.g(id = 'kvg:'+baseid+'-bg-Kanimaji',
			style = ('fill:none;stroke:%s;stroke-width:%f;'+
				'stroke-linecap:round;stroke-linejoin:round;') %
				(STOKE_UNFILLED_COLOR, STOKE_UNFILLED_WIDTH) )
	anim_g = E.g(id = 'kvg:'+baseid+'-anim-Kanimaji',
			style = ('fill:none;stroke:%s;stroke-width:%f;'+
				'stroke-linecap:round;stroke-linejoin:round;') %
				(STOKE_FILLED_COLOR, STOKE_FILLED_WIDTH) )
	if SHOW_BRUSH:
		brush_g = E.g(id = 'kvg:'+baseid+'-brush-Kanimaji',
				style = ('fill:none;stroke:%s;stroke-width:%f;'+
				'stroke-linecap:round;stroke-linejoin:round;') % 
				(BRUSH_COLOR, BRUSH_WIDTH))
		brush_brd_g = E.g(id = 'kvg:'+baseid+'-brush-brd-Kanimaji',
				style = ('fill:none;stroke:%s;stroke-width:%f;'+
				'stroke-linecap:round;stroke-linejoin:round;') % 
				(BRUSH_BORDER_COLOR, BRUSH_BORDER_WIDTH))

	# compute total length and time, at first
	tottime = 0

	for g in doc.xpath("/n:svg/n:g", namespaces=namespaces):
		for p in g.xpath(".//n:path", namespaces=namespaces):
			pathlen = compute_path_len(p.get('d'))
			duration = stroke_length_to_duration(pathlen)
			tottime += duration

	animation_time = time_rescale(tottime) #math.pow(3 * tottime, 2.0/3)
	tottime += WAIT_AFTER * tottime / animation_time
	animation_time += WAIT_AFTER

	animated_css = ''
	elapsedlen = 0
	elapsedtime = 0

	# add css elements for all strokes
	for g in doc.xpath("/n:svg/n:g", namespaces=namespaces):
		groupid = g.get('id')

		gidcss = re.sub(r':', '\\\\3a ', groupid)
		rule = d("""
			#%s {
				stroke-width: %.01fpx !important;
				stroke:	   %s !important;
			}""" % (gidcss, STOKE_BORDER_WIDTH, STOKE_BORDER_COLOR))
		animated_css += rule

		for p in g.xpath(".//n:path", namespaces=namespaces):
			pathid = p.get('id')
			dpath = p.get('d')
			pathidcss = re.sub(r':', '\\\\3a ', pathid)

			bg_pathid = pathid+'-bg'
			ref = E.path(id = bg_pathid, d=dpath)
			bg_g.append(ref)

			anim_pathid = pathid+'-anim'
			anim_pathidcss = pathidcss+'-anim'
			ref = E.path(id = anim_pathid, d=dpath)
			anim_g.append(ref)

			if SHOW_BRUSH:
				brush_pathid = pathid+'-brush'
				brush_pathidcss = pathidcss+'-brush'
				ref = E.path(id = brush_pathid, d=dpath)
				brush_g.append(ref)

				brush_brd_pathid = pathid+'-brush-brd'
				brush_brd_pathidcss = pathidcss+'-brush-brd'
				ref = E.path(id = brush_brd_pathid, d=dpath)
				brush_brd_g.append(ref)

			pathname = re.sub(r'^kvg:','',pathid)
			pathlen = compute_path_len(p.get('d'))
			duration = stroke_length_to_duration(pathlen)

			newelapsedlen = elapsedlen + pathlen
			newelapsedtime = elapsedtime + duration
			anim_start = elapsedtime/tottime*100
			anim_end = newelapsedtime/tottime*100

			# animation stroke progression
			animated_css += d("""
				@keyframes strike-%s {
					0%% { stroke-dashoffset: %.03f; }
					%.03f%% { stroke-dashoffset: %.03f; }
					%.03f%% { stroke-dashoffset: 0; }
					100%% { stroke-dashoffset: 0; }
				}""" % (pathname, pathlen, anim_start, pathlen, anim_end))

			# animation visibility
			animated_css += d("""
				@keyframes showhide-%s {
					%.03f%% { visibility: hidden; }
					%.03f%% { stroke: %s; }
				}""" % (pathname, anim_start, anim_end, STOKE_FILLING_COLOR))

			# animation progression
			animated_css += d("""
				#%s {
					stroke-dasharray: %.03f %.03f;
					stroke-dashoffset: 0;
					animation: strike-%s %.03fs %s infinite,
						showhide-%s %.03fs step-start infinite;
				}""" % (anim_pathidcss, pathlen, pathlen, 
						pathname, animation_time,
						TIMING_FUNCTION,
						pathname, animation_time))

			if SHOW_BRUSH:
				# brush element visibility
				animated_css += d("""
					@keyframes showhide-brush-%s {
						%.03f%% { visibility: hidden; }
						%.03f%% { visibility: visible; }
						100%% { visibility: hidden; }
					}""" % (pathname, anim_start, anim_end))

				# brush element progression
				animated_css += d("""
					#%s, #%s {
						stroke-dasharray: 0 %.03f;
						animation: strike-%s %.03fs %s infinite,
							showhide-brush-%s %.03fs step-start infinite;
					}""" % (brush_pathidcss, brush_brd_pathidcss,
						pathlen, 
						pathname, animation_time, TIMING_FUNCTION,
						pathname, animation_time))

			elapsedlen = newelapsedlen
			elapsedtime = newelapsedtime

	# insert groups
	if SHOW_BRUSH and not SHOW_BRUSH_FRONT_BORDER:
		doc.getroot().append(brush_brd_g)
	doc.getroot().append(bg_g)
	if SHOW_BRUSH and SHOW_BRUSH_FRONT_BORDER:
		doc.getroot().append(brush_brd_g)
	doc.getroot().append(anim_g)
	if SHOW_BRUSH:
		doc.getroot().append(brush_g)

	style = E.style(animated_css, id="style-Kanimaji")
	doc.getroot().insert(0, style)
	svgfile = filename_noext + '_anim.svg'
	doc.write(svgfile, pretty_print=True)
	doc.getroot().remove(style)
	print('written %s' % svgfile)

args = deepcopy(sys.argv)
del args[0]
for a in args:
	create_animation(a)