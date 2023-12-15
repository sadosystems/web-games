import json
from PIL import Image

color_table = {"#000000":0x0, # void
               "#00ff00":0x1, # trace
               "#ff0000":0xA} # logic high

def get_hex_color(pixel):
    return '#{:02x}{:02x}{:02x}'.format(pixel[0], pixel[1], pixel[2])

def color_to_id(pixels):
    color = get_hex_color(pixels)
    try: 
        id = color_table[color]
    except:
        id = 0
    return id

def process_image(image_path, output_json_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    pixels = img.load()
    data = []
    for y in range(img.height):
        for x in range(img.width):
            id = color_to_id(pixels[x, y])
            data.append(id)

    assert len(data) == 20 * 20, "The image size must be 1004 * 1004 pixels with the border."

    with open(output_json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

image_path = "world.png"
output_json_path = "data.json"
process_image(image_path, output_json_path)
