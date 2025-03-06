# The SportsDB Art Generator

A simple tool that generates artwork for TheSportsDB.com using provided Art Elements to create
series of Posters, Banners, Thumbnails, and Square Posters as used on TSDB.

## Basic Usage

Artgen.py takes a single argument: A _filename_ to a valid .json file that defines jobs for ArtGen to do.

## Purpose

ArtGen was created to simplify the creation of lots of posters and thumbnails to be used in media servers like Plex,
or media players like Kodi. One could use Photoshop or GIMP to do batch processing, but different designs require different 
batches in different places, making the whole process cumbersome at best. ArtGen uses design elements in the form of image files
and uses a simple command system to place each element on the final image, either by directly using filenames in the command, or
by reading the filenames from a csv batch file column and using that. It then saves the finished artwork in a specified filename.

This enables users to create a structured design system that can be used and reused to rapidly create entire seasons worth of artwork.

## Requirements

While the script is simple enough, working with graphics is not. For that reason the script makes heavy use of the Pillow framework.
Before using it, make sure that you have it installed either by using pip, or manually installing it into your Python Environment.
Needless to say, it being a Python 3 script, it requires a Python 3 interpreter.

You can install it by following the instructions here:
https://pypi.org/project/pillow/


## Job files

Creation jobs are provided using simple JSON files consisting of groups of commands to build an image one design element at a time.
There are basically two commands; Overlay and Text. With each having a direct function and a batch function (Overlay vs BOverlay and Text vs BText)
The difference between the two is that the direct function has a filename as its data source, and the batch function has a column name
as its data source. 

The structure of the commands are detailed below:

### Overlay commands

This command simply takes an image file (I recommend using PNG because it's lossless and handles transparency) and places it onto the canvas.

It looks like this:
```
{"overlay": 
    {
        "order" : "1",                        <- The order of the command (to stack the layers correctly, first come first serve if equal)
        "image" : "path/to/filename.ext",     <- The path to the layer image, or the name of the image column in the csv for BOverlay
        "pos" : [0,0]                         <- The [x,y] coordinates of the top left pixel in the resulting image.
        "zoom": 1.0                           <- The Zoom factor of the image. default 1.0. 0.5 = half size, 2.0 double size.
    }
}
```
That's all. There may be a rotation option added, but I haven't found a need for it at this time. It's not that difficult to do, but it requires a
bit of a rethink of how the layers are manipulated. If any part of the image is outside of the canvas before rotation, it is cut off and won't be visible.
The 'image' value is simply either the filename of the image to be pasted onto the canvas, or the name of the csv column containing the filename of the
image to be pasted onto the canvas.

### Text commands

This command is a little more complicated. Still pretty simple though. It writes text onto the canvas.

It has quite a few more parameters:
```
{"text":
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
}
```
Some things may be altered. As of now you can only set the actual text to write in the batch file. Every other parameter is fixed. This includes
the font size. This means that in some cases, some trial and error is required to see what text size fits the image. I might add size to the csv
file so it can be changed on a per line basis, but this creates difficulties in text placement. I might also have an extra option to use adaptive
sizes, with the default size being whatever the 'size' parameter says, which would increase/decrease text sizes if they grow longer than 'X' pixels.

### Job Definitions

As stated, the jobs are json structures meaning they are made up of arrays of key/value pairs.
Each file has a single 'job' definition, under which all the separate jobs are defined.
A job consists of one or more types, which can be 'poster', 'thumb', 'square', or 'banner' (each creating artwork of different sizes as defined on The Sports DB),
which each are made up of up to three key/value pairs, 2 of which are mandatory. The 'csvfile' key/value pair is optional, although you probably won't use
a job without it save for quickly testing a job definition without batching. The other two ('fnexp' and 'commands') are mandatory because they define what to
do and where to finally store the result of what it did.

The simplest Job definition then comes down to a single job type, creating a single file, with a single image and some text.
It would look like this:

```
{
  "job":
      {"poster":
          {"fnexp": "C:\\temp\\exp.jpg",
           "commands":
              [{
                "overlay":
                    {"order": 1,
                     "image": "C:\\temp\\imp.png",
                     "pos": [0,0],
                     "zoom": 1
                     }
               },{
                "text":
                    {"order" : 2,
					           "text"	: "SAMPLE TEXT",
					           "font"  : "C:\\temp\\font.ttf",
					           "size"  : 50,
					           "just"  : "right",
					           "pos"   : [100, 100],
					           "rot"	: 0,
					           "stroke": 3,
					           "color"	: [0,0,0],
					           "fill"  : [255,255,255],
					           "drop"	: "False",
					           "dcol"	: [0,0,0]
                     }
                }
            ]
        }
    }
} 
```           
          
The above job definition creates a transparent poster file (600x1000 pixels).
It reads the file C:\temp\imp.png and places it onto the poster at position 0,0 (top left).
It then writes "SAMPLE TEXT" using the font in c:\temp\font.ttf in size 50. Right justified from position 100,100.
No rotation, using a black outline of 3 pixels, using a white fill color without a drop shadow.
(the values that aren't used can also be omitted, they were added for explanatory purposes).

**Also note that backslashes in strings (filenames) need to be escaped using a backslash. That means you need to double them in the Job definition.**


## CSV files

The batch files are simple CSV (Comma Separated Values) files. Make sure the first line is made up of headers as they are
used by the job definition to reference values in batch processing.

You can use any tool to create them, but I recommended using a spreadsheet application to make use of functions to quickly
fill lines with meaningful data. Open Office Calc works fine.

Mind you that the whole thing is case sensitive, so a header "Racelogo" is different from "racelogo".

## Example files

I have included some example files for the NASCAR Cup Series artwork.
You can find them in the Artwork folder. There is a batch folder that has the JSON and CSV files, and then a template folder that has all the used elements.
