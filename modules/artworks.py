'''
Created on 12 nov. 2024

@author: Raymond Sagius
'''

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import csv, os.path


defaults = {
    'text'  : {
             'text'  : {'value': '', 'type': 'str'},
             'font'  : {'value': None, 'type': 'str'},
             'size'  : {'value': 10, 'type': 'int'},
             'just'  : {'value': 'left', 'type': 'str', 'list': ['left', 'right', 'center', 'centre']},
             'pos'   : {'value': [0,0], 'type': 'list', 'length': 2},
             'rot'   : {'value': 0, 'type': 'int'},
             'stroke': {'value': 0, 'type': 'int'},
             'color' : {'value': [0,0,0], 'type': 'list', 'length': 3, 'minmax': [0,255]},
             'fill'  : {'value': [255,255,255], 'type': 'list', 'length': 3, 'minmax': [0,255]},
             'drop'  : {'value': 'False', 'type': 'str', 'list': ['true', 'false']},
             'dcol'  : {'value': [0,0,0], 'type': 'list', 'length': 3, 'minmax': [0,255]}
             },
    'overlay': {
             'image' : {'value': None, 'type': 'str'},
             'pos'   : {'value': [0,0], 'type': 'list', 'length': 2},
             'zoom'  : {'value': 1.0, 'type': 'float'}
        }
    }
    
            
    
    

def check_files(arttype, job, batchtable):
    
    allowdupes = arttype in ['poster', 'square', 'banner']
    csvfiles = ''
    # Check for output folder and duplicate export filenames
    if 'fnexp' in job.keys():
        if job['fnexp'] in batchtable.keys():
            csvfiles = job['fnexp']
            filelist = []
            for fn in batchtable[csvfiles]:
                if fn not in filelist or allowdupes:
                    if os.path.isdir(os.path.dirname(fn)):
                        filelist.append(fn)
                    else:
                        return {"error": "Export folder not found. Please make sure '{0}' exists and is writable.".format(os.path.dirname(fn))}
                else:
                    return {"error": "Duplicate export filename ({0}) found in CSV, exiting, because this will result in overwritten output".format(fn)}
        else:
            if len(batchtable) > 0:
                return {"error": "Column name {0} not found in the CSV.".format(job['fnexp'])}
            if not os.path.isdir(os.path.dirname(job['fnexp'])):
                return {"error": "Export folder not found. Please make sure {0} exists and is writable.".format(os.path.dirname(job['fnexp']))}
                
    # Loop through each command and check for file availability
    if 'commands' not in job.keys():
        return {"error":"No commands in job definition. Nothing to do."}
    else:
        commands = job['commands']
        for command in commands:
            ctype = list(command)[0]
            match ctype:
                case 'overlay':
                    if not os.path.isfile(command[ctype]['image']):
                        return {"error":"Overlay file {0} not found. Make sure any referenced overlays exist.".format(command[ctype]['image'])}
                case 'boverlay':
                    if not os.path.isfile(command[ctype]['image']):
                        if not command[ctype]['image'] in batchtable.keys():
                            return {"error":"Boverlay column '{0}' not found. Exiting.".format(command[ctype]['image'])}
                        else:
                            for fp in batchtable[command[ctype]['image']]:
                                if not os.path.isfile(fp) and fp != '':
                                    return {"error":"Overlay file {0} not found. Make sure any referenced overlays exist.".format(fp)}
                    else:
                        return {"error":"Boverlay has a direct file reference to '{0}'. Use 'overlay' instead.".format(command[ctype]['image'])}
                case 'text':
                    if not os.path.isfile(command[ctype]['font']):
                        return {"error":"Font file {0} not found. Make sure any referenced fonts exist.".format(command[ctype]['font'])}    
                case 'btext':
                    if not os.path.isfile(command[ctype]['font']):
                        if not command[ctype]['image'] in batchtable.keys():
                            return {"error":"Font column or file '{0}' not found. Exiting.".format(command[ctype]['font'])}
                        else:
                            for fp in batchtable[command[ctype]['font']]:
                                if not os.path.isfile(fp) and fp != '':
                                    return {"error":"Overlay file {0} not found. Make sure any referenced overlays exist.".format(fp)}    
    return {}


def check_csv(job):
    
    batchtable = {}
    headers = []
    if 'csvfile' in job.keys():
        if os.path.isfile(job['csvfile']):
            try:
                with open(job['csvfile']) as csvfile:
                    csvdata = csv.reader(csvfile, delimiter=',', quotechar='"')
                    csvtable = []
                    for row in csvdata:
                        csvtable.append(row)
                    batchcount = len(csvtable) - 1
            except Exception as e:
                return {"error":"Error reading csv file: {0}".format(e)}
            if batchcount > 0:    
                for item in csvtable[0]:
                    batchtable[item] = []
                    headers.append(item)
                cnt = 1
                while cnt < len(csvtable):
                    rc = 0
                    while rc < len(csvtable[cnt]):
                        batchtable[headers[rc]].append(csvtable[cnt][rc])
                        rc += 1
                    cnt += 1
    return batchtable



def sort_commands(commandlist):
    
    results = []
    for command in commandlist:
        name = list(command)[0]
        if len(results) == 0:
            results.append(command)
            continue
        else:
            for result in results:
                resname = list(result)[0]
                if int(command[name]['order']) < int(result[resname]['order']):
                    results.insert(results.index(result), command)
                    break
            if command not in results:
                results.append(command)
    return results


# Add an image on top of the artwork
def add_overlay(art, img, pos, zoom):
    
    if img == '': # Image value is empty for this overlay, skip it.
        return art
    # print("Adding image {0} to artwork at position ({1}, {2})".format(img, pos[0], pos[1]))
    result = art
    ol = Image.open(img).convert("RGBA")
    if zoom != 1.0:
        ol = ol.resize([int(ol.width * zoom), int(ol.height * zoom)], resample=Image.Resampling.LANCZOS)
    result.paste(ol, pos.copy(), ol)
    return result



# Add text on top of the artwork
def add_text(art, text, font, size, just, pos, rotation, stroke, color, fill, dropshadow, dropcolor):
    
    dropshadow = dropshadow == "True"
    if text == '': # Text value is empty for this layer, skip it.
        return art
    #print("Adding '{0}' to the artwork.".format(text))
    result = art
    textimage = Image.new('RGBA', art.size)
    ol = ImageDraw.Draw(textimage)
    font = ImageFont.truetype(font, size)
    match just:
        case "left":
            anchor = 'ls'
        case "right":
            anchor = 'rs'
        case "center" | "centre":
            anchor = 'ms'
        case _:
            anchor = 'ls'
    # Create the drop shadow first if true:
    if dropshadow:
        drop = drop_shadow(result, pos, text, dropcolor, font, anchor, rotation)
        
        result.paste(drop, drop)
    
    # Now place the text
    ol.text(pos, text, fill=tuple(fill), font=font, anchor=anchor, stroke_width=stroke, stroke_fill=tuple(color))
    textimage = textimage.rotate(angle=rotation, center=pos)
    textimage = textimage.resize([textimage.width * 2, textimage.height * 2], resample=Image.Resampling.LANCZOS)
    textimage = textimage.resize([textimage.width // 2, textimage.height // 2], resample=Image.Resampling.LANCZOS)
    result.paste(textimage, textimage)
    return result

# Create an image containing the drop shadow of the text.
def drop_shadow(art, pos, text, color, font, anchor, rotation):
    
    drop = Image.new('RGBA', art.size)
    draw = ImageDraw.Draw(drop)
    draw.text(pos, text, fill=tuple(color), font=font, anchor=anchor)
    for i in range(7):
        drop = drop.filter(ImageFilter.BLUR)
    drop = drop.rotate(angle=rotation, center=pos)
    return drop
    

# Validate the values of the command, fill in the default value if illegal value or not present
def build_record(inp, ctype):
    
    result = {}
    for var in defaults[ctype]:
        if var not in inp.keys():
            result[var] = defaults[ctype][var]['value']
            continue
        if defaults[ctype][var]['type'] == 'float':
            if type(inp[var]).__name__ == 'int':
                inp[var] = float(inp[var])
        if type(inp[var]).__name__ != defaults[ctype][var]['type']:
            result[var] = defaults[ctype][var]['value']
            if 'errors' not in result.keys():
                result['errors'] = []
            result['errors'].append("Value for {0} is the wrong type: Expected {1}, but found {2}.".format(var, defaults[ctype][var]['type'], type(inp[var]).__name__ ))
            continue
        if defaults[ctype][var]['type'] == 'str':
            if 'list' in defaults[ctype][var].keys():
                if inp[var].lower() not in defaults[ctype][var]['list']:
                    result[var] = defaults[ctype][var]['value']
                    if 'errors' not in result.keys():
                        result['errors'] = []
                    result['errors'].append("Value for {0} is illegal. {1} is not one of {2}.".format(var, inp[var], defaults[ctype][var]['list']))
                    continue
            result[var] = inp[var]
            continue
        if defaults[ctype][var]['type'] == 'list':
            if 'length' in defaults[ctype][var].keys():
                if len(inp[var]) != defaults[ctype][var]['length']:
                    result[var] = defaults[ctype][var]['value']
                    if 'errors' not in result.keys():
                        result['errors'] = []
                    result['errors'].append("Length of list {0} not allowed. Should be length {1}".format(inp[var], defaults[ctype][var]['length']))
                    continue
            if 'minmax' in defaults[ctype][var].keys():
                for val in inp[var]:
                    if val < defaults[ctype][var]['minmax'][0]:
                        if 'errors' not in result.keys():
                            result['errors'] = []
                        result['errors'].append("Increased {0} value {1} to minimum of {2}".format(var, val, defaults[ctype][var]['minmax'][0]))
                    
                        val = defaults[ctype][var]['minmax'][0]
                    if val > defaults[ctype][var]['minmax'][1]:
                        if 'errors' not in result.keys():
                            result['errors'] = []
                        result['errors'].append("Decreased {0} value {1} to maximum of {2}".format(var, val, defaults[ctype][var]['minmax'][1]))
                        val = defaults[ctype][var]['minmax'][1]
            result[var] = inp[var]
            continue
        result[var] = inp[var]            
    return result

# This checks the job descriptions for validity and ultimately renders the image to return.
def generate_art(job):
    
    print("------------------------------------------------------------")
    result = {}
    artsize = [0,0] # start with a 0-size canvas
    arttype = list(job)[0].lower()
    
    # Determine the type of artwork we're creating
    match arttype:
        case "poster":
            artsize = [680, 1000]
        case "thumb":
            artsize = [1280, 720]
        case "banner":
            artsize = [1000, 185]
        case "square":
            artsize = [700, 700]
        case _:
            return {'error': "'{0}' is not a valid art type".format(arttype)}
    result['artsize'] = artsize
    
    # If there is a csvfile for batch execution, try to read it. 
    batchtable = check_csv(job[arttype])
    if 'error' in batchtable.keys():
        return batchtable
    
    # Determine where the exports go. Make sure we can export the file(s).
    chk = check_files(arttype, job[arttype], batchtable)
    if 'error' in chk.keys():
        return chk
    
    # Sort the list of commands by order. This is to fix the order, in case the list isn't ordered on a system.
    job[arttype]['commands'] = sort_commands(job[arttype]['commands'])
    
    # Determine the runcounts
    if len(batchtable) > 0:
        batchcount = len(batchtable[list(batchtable)[0]])
    else:
        batchcount = 0
        
    # Start running each image export
    runcount = 0
    while True:
        art = Image.new("RGBA", artsize, "black")
        for command in job[arttype]['commands']:
            func = list(command)[0]
            match func:
                case "overlay":
                    inp = {}
                    inp = command[func].copy()
                    inp = build_record(inp, 'overlay')
                    if 'errors' in inp.keys():
                        print("The following errors occurred while checking parameters for command with order {0}:".format(command[func]['order']))
                        for error in inp['errors']:
                            print(error)
                    art = add_overlay(
                        art, 
                        inp['image'], 
                        inp['pos'],
                        inp['zoom'])
                case "boverlay":
                    inp = {}
                    inp = command[func].copy()
                    inp['image'] = batchtable[inp['image']][runcount]
                    inp = build_record(inp, 'overlay')
                    if 'errors' in inp.keys():
                        print("The following errors occurred while checking parameters for command with order {0}:".format(command[func]['order']))
                        for error in inp['errors']:
                            print(error)
                    art = add_overlay(
                        art, 
                        inp['image'], 
                        inp['pos'],
                        inp['zoom'])
                case "text":
                    inp = {}
                    inp = command[func].copy()
                    inp = build_record(inp, 'text')
                    if 'errors' in inp.keys():
                        print("The following errors occurred while checking parameters for command with order {0}:".format(command[func]['order']))
                        for error in inp['errors']:
                            print(error)
                    art = add_text(
                        art, 
                        inp['text'], 
                        inp['font'],
                        inp['size'],
                        inp['just'],
                        inp['pos'], 
                        inp['rot'],
                        inp['stroke'],
                        inp['color'],
                        inp['fill'],
                        inp['drop'],
                        inp['dcol'])
                case "btext":
                    inp = {}
                    inp = command[func].copy()
                    inp['text'] = batchtable[inp['text']][runcount]
                    inp = build_record(inp, 'text')
                    if 'errors' in inp.keys():
                        print("The following errors occurred while checking parameters for command with order {0}:".format(command[func]['order']))
                        for error in inp['errors']:
                            print(error)
                    art = add_text(
                        art, 
                        inp['text'], 
                        inp['font'], 
                        inp['size'],
                        inp['just'],
                        inp['pos'], 
                        inp['rot'],
                        inp['stroke'],
                        inp['color'],
                        inp['fill'],
                        inp['drop'],
                        inp['dcol'])
        if batchcount == 0:
            print("Exporting to {0}".format(job[arttype]['fnexp']))
            art = art.convert("YCbCr")
            with open(job[arttype]['fnexp'], 'wb') as fp:
                art.save(fp, "JPEG", quality=95, optimize=True)
                if 'art' not in result.keys():
                    result['art'] = []
                result['art'].append(job[arttype]['fnexp'])
        else:
            print("Exporting to {0}".format(batchtable[job[arttype]['fnexp']][runcount]))
            art = art.convert("YCbCr")
            with open(batchtable[job[arttype]['fnexp']][runcount], 'wb') as fp:
                art.save(fp, "JPEG", quality=95, optimize=True)
                if 'art' not in result.keys():
                    result['art'] = []
                result['art'].append(batchtable[job[arttype]['fnexp']][runcount])
        if runcount >= batchcount - 1:
            break
        runcount += 1
    print("------------------------------------------------------------")    
    return result

    
    
    