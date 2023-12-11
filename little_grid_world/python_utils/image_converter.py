import json
from PIL import Image

def get_hex_color(pixel):
    return '#{:02x}{:02x}{:02x}'.format(pixel[0], pixel[1], pixel[2])

def process_image(image_path, output_json_path, output_image_path):
    # Open the original image
    img = Image.open(image_path)
    img = img.convert('RGB')

    # Create a new image with a 2-pixel border
    border_size = 2
    new_width = img.width + border_size * 2
    new_height = img.height + border_size * 2
    bordered_image = Image.new('RGB', (new_width, new_height), "#2d3640")
    
    # Paste the original image onto the center of the new image
    bordered_image.paste(img, (border_size, border_size))
    
    # Save the image with the border
    bordered_image.save(output_image_path)

    # Continue with your original processing
    pixels = bordered_image.load()
    colored_squares = []
    for y in range(bordered_image.height):
        for x in range(bordered_image.width):
            color = get_hex_color(pixels[x, y])
            colored_squares.append(color)

    # Ensure that we have exactly 10404 color values for a 102x102 grid
    size = 104 * 104
    assert len(colored_squares) == size, "The image size must be 1004 * 1004 pixels with the border."

    with open(output_json_path, 'w') as json_file:
        json.dump(colored_squares, json_file, indent=4)

image_path = "skull.png"
output_json_path = "data.json"
output_image_path = "skull_with_border.png"
process_image(image_path, output_json_path, output_image_path)
