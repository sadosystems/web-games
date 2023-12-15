import json
from PIL import Image

def process_image(image_path):
    # Open the original image
    bordered_image = Image.open(image_path)

    # Continue with your original processing
    blame = []
    for _ in range(bordered_image.height):
        for _ in range(bordered_image.width):
            color = "God"
            blame.append(color)

    # Ensure that we have exactly 10404 color values for a 102x102 grid
    size = 104 * 104
    assert len(blame) == size, "The image size must be 1004 * 1004 pixels with the border."

    with open(output_json_path, 'w') as json_file:
        json.dump(blame, json_file, indent=4)

output_json_path = "blame.json"
image_path = "skull_with_border.png"
process_image(image_path)


