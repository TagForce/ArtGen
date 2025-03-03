'''
Created on 12 nov. 2024

@author: Raymond Sagius

The SportsDB Art Generator

A simple tool that generates artwork for TheSportsDB.com using provided Art Elements to create
series of Posters, Banners, Thumbnails, and Square Posters as used on TSDB.

Art Elements consist of PNG or JPG images, TrueType Font files (.ttf), and CSV files containing batch information.
Creation jobs are provided using simple JSON files consisting of groups of layering commands to build an image layer
by layer. The following commands are recognised:
'Overlay': Simply places an image provided using 'name' on the layer.
'BOverlay': Simply places an image provided using 'csv header column' on the layer.
'Text': Simply writes 'text' using a font provided.
'BText': Simply writes 'text in csv header column' using a font provided.

The JSON structure is as follows:
{"Job":[{ <- Job is an array of jobtypes. You can place as many jobs as you want in the json, each is handled sequentially.
    "Jobtype": { <- Jobtype is one of "Poster", "Thumb", "Banner", or "Square" to create files of this type.
        "csvfile": "x" <- Name of the csvfile for batch processing. Optional. Treats BOverlay as Overlay if ommitted.
        "fnexp"  : "y" <- Name of the exported file or name of the column for the filename in the csv if csvfile above is used.
        "commands": [{ <- One of the commands mentioned above. Each command has a structure as explained below.
        }]
    }]
}

Command structures are as follows:
Overlay and BOverlay:
    {
        "order" : "1",                        <- The order of the command (to stack the layers correctly, first come first serve if equal)
        "image" : "path/to/filename.ext",     <- The path to the layer image, or the name of the image column in the csv for BOverlay
        "pos" : [0,0]                         <- The [x,y] coordinates of the top left pixel in the resulting image.
        "zoom": 1.0                           <- The Zoom factor of the image. default 1.0. 0.5 = half size, 2.0 double size.
    }

Text and BText:
    {
        "order"   : "3",                        <- The order of the command (to stack the layers correctly, first come first server if equal)    
        "font"    : "path/to/ttf/file.ttf",     <- The path to the font file.
        "text"    : "text to add",              <- The text to add, or the name of the column containing the text if BText.
        "pos"     : [0,0],                      <- The (x,y) coordinates of the justification point (bottom-left, bottom-right or bottom-center)
        "size"    : 10                          <- Size of the font (in points, default 10)
        "just"    : "left",                     <- The justification (left, right, center)
        "rot"     : 0,                          <- The rotation of the text (counter-clockwise rotation from the horizontal) around the pos pivot.
        "stroke"  : 0,                          <- The width of the outline of the text. Defaults to 0.  
        "color"   : [0,0,0],                    <- The color of the outline in the format [r,g,b]. Defaults to [0,0,0] which is black.
        "fill"    : [0,0,0],                    <- The fill color of the text. White (255,255,255) is the default.
        "drop"    : "true",                     <- Should the text contain a drop shadow?
        "dcol"    : [0,0,0],                    <- Color of the drop shadow. Black (0,0,0) is the default.
    }
    
'''

import os, os.path, argparse, csv, json, sys
import modules.artworks as artworks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A simple tool to generate artwork for TheSportsDB.com")
    parser.add_argument('filename', help="Filename for the json file (required)")
    args = parser.parse_args()
    # Parse the arguments.
    if not os.path.isfile(args.filename): # If the argument isn't a file.
        parser.error("{0} is not a valid file.".format(args.filename))
        sys.exit(0)
    try:
        with open(args.filename, 'r') as fp:
            data = json.load(fp) # Try to read the JSON object
    except Exception as e:
        parser.error("{0} is not a valid json file".format(args.filename)) # It's not a JSON object.
        sys.exit(1)
    if 'job' not in data.keys():
        parser.error("{0} is not a valid job file".format(args.filename)) # It's not a valid Job Object.
        sys.exit(1)
    if not (isinstance(data['job'], list)): # Make sure there's a list of output types. 
        data['job'] = [data['job']] # If it's a single type, make it a list anyway.
    for arttype in data['job']:
        print('Processing {0}s'.format(list(arttype)[0].lower()))
        art = artworks.generate_art(arttype)
        if 'error' in art.keys():
            print("Error while parsing job file {0} for job {1}:".format(args.filename, list(arttype)[0]))
            print(art['error'])
            continue
        print('Finished exporting {0}s'.format(list(arttype)[0].lower()))
    print("Done processing.")
    sys.exit(0)
                    