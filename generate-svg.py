import sys
import os
import json
from types import SimpleNamespace

if len(sys.argv) != 2:
	print("One argument expected, got some other number.")
	print('Provide absolute path to "Semantic Location History" directory from Google download.')
	quit()

root = sys.argv[1]
root = os.path.join("/", root)

if not os.path.isdir(root):
	print('Path appears to not be a valid directory. Make sure you have submitted the absolute path to the file "Takeout/Location History/Semantic Location History"')
	print('This will require putting quotes around the argument as there are spaces in the path')
	quit()

years = os.listdir(root)
vectors = []

for year in years:
	year_root = os.path.join(root, year)
	months = os.listdir(year_root)
	for month in months:
		month_path = os.path.join(year_root, month)
		f = open(month_path, 'r')
		try:
			#decoding fails on rare occasion and I have no idea what encoding google used
			month_obj = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d)).timelineObjects
		except:
			continue
		for event in month_obj:
			if not hasattr(event, "activitySegment"):
				continue
			activity = event.activitySegment
			if not hasattr(activity, "waypointPath"):
				continue
			#we divide all the values by 10,000,000 because google is storing floats as ints
			line_path = f'<path style="fill:none;stroke:#000000;stroke-width:0.264583px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" d="m {activity.startLocation.latitudeE7/10000000}, {activity.startLocation.longitudeE7/10000000}'
			for waypoint in activity.waypointPath.waypoints:
				line_path += f' {waypoint.latE7/10000000}, {waypoint.lngE7/10000000}'
			line_path += f' {activity.endLocation.latitudeE7/10000000}, {activity.endLocation.longitudeE7/10000000}">\n'
			vectors.append(line_path)

def generate_svg(vectors):
	f = open("goog-maps-plotted.svg", 'w')
	boiler = [
		'<?xml version="1.0" encoding="utf-8"?>\n',
		'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n',
		#-180 and 180 'cause we live on a sphere
		'viewBox="-180 -180 180 180" xml:space="preserve">\n',
		'<style type="text/css">\n',
		'	.waypointPath{fill:#FFFFFF;stroke:#000000;stroke-miterlimit:10;}\n',
		'</style>\n'
	]
	f.writelines(boiler)
	f.writelines(vectors)
	f.writelines(['</svg>'])
	f.close()

generate_svg(vectors)
