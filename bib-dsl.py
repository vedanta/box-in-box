"""
MIT License

Copyright (c) 2023 [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import yaml
from PIL import Image, ImageDraw, ImageFont

class BiBDSL:
    def __init__(self, yaml_file):
        self.data = self.load_yaml(yaml_file)
        self.boxes = {}
        self.padding = 20
        self.text_margin = 10
        self.min_box_size = 80
        self.max_depth = 3
        self.image = Image.new('RGB', (2480, 3508), color='white')  # A4 size at 300 DPI
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.fonts = {
                0: ImageFont.truetype("Arial.ttf", 48),
                1: ImageFont.truetype("Arial.ttf", 36),
                2: ImageFont.truetype("Arial.ttf", 24)
            }
        except IOError:
            print("Arial font not found, using default font")
            default_font = ImageFont.load_default()
            self.fonts = {0: default_font, 1: default_font, 2: default_font}

    def load_yaml(self, yaml_file):
        try:
            with open(yaml_file, 'r') as file:
                print(f"Reading YAML file: {yaml_file}")
                content = file.read()
                print("YAML file content:")
                print(content)
                print("Parsing YAML content...")
                data = yaml.safe_load(content)
                print("YAML parsing successful")
                return data
        except FileNotFoundError:
            print(f"Error: The file '{yaml_file}' was not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred while reading the YAML file: {e}")
            sys.exit(1)

    def parse_data(self):
        def parse_item(key, value, parent=None, level=0):
            if level >= self.max_depth:
                return None
            print(f"Parsing item: {key} at level {level}")
            box = {'name': key, 'level': level, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0}
            if isinstance(value, dict):
                if 'color' in value:
                    box['color'] = value['color']
                if 'children' in value:
                    children = value['children']
                    if isinstance(children, dict):
                        for child_key, child_value in children.items():
                            child_box = parse_item(child_key, child_value, key, level + 1)
                            if child_box:
                                box['children'].append(child_box)
            if parent:
                box['parent'] = parent
            self.boxes[key] = box
            return box

        for key, value in self.data.items():
            parse_item(key, value)

    def calculate_positions(self, box, x, y, available_width, available_height):
        print(f"Calculating position for box: {box['name']}")
        box['x'] = x + self.padding
        box['y'] = y + self.padding
        box['width'] = max(available_width - 2 * self.padding, self.min_box_size)
        box['height'] = max(available_height - 2 * self.padding, self.min_box_size)

        if box['children']:
            # Reserve space for the parent box label
            font = self.fonts[min(box['level'], 2)]
            _, _, _, label_height = self.draw.textbbox((0, 0), box['name'], font=font)
            label_height += 2 * self.text_margin
            remaining_height = box['height'] - label_height - self.padding

            num_children = len(box['children'])
            child_height = max((remaining_height - self.padding * (num_children + 1)) / num_children, self.min_box_size)
            
            for i, child in enumerate(box['children']):
                child_y = box['y'] + label_height + self.padding + i * (child_height + self.padding)
                child_height = min(child_height, box['height'] - (child_y - box['y']) - self.padding)
                if child_height >= self.min_box_size:
                    self.calculate_positions(child, box['x'] + self.padding, child_y, box['width'] - 2 * self.padding, child_height)

    def draw_boxes(self, box):
        print(f"Drawing box: {box['name']}")
        if box['width'] < self.min_box_size or box['height'] < self.min_box_size:
            print(f"Box {box['name']} is too small to draw. Skipping.")
            return

        self.draw.rectangle([box['x'], box['y'], box['x'] + box['width'], box['y'] + box['height']], 
                            outline='black', fill=box.get('color', 'white'))
        
        font = self.fonts[min(box['level'], 2)]  # Use the smallest font for levels 2 and beyond
        left, top, right, bottom = self.draw.textbbox((0, 0), box['name'], font=font)
        text_width = right - left
        text_height = bottom - top
        
        text_x = box['x'] + (box['width'] - text_width) / 2
        text_y = box['y'] + self.text_margin

        if text_width < box['width'] - 2 * self.text_margin and text_height < box['height'] - 2 * self.text_margin:
            self.draw.text((text_x, text_y), box['name'], fill='black', font=font)

        for child in box['children']:
            self.draw_boxes(child)

    def generate(self):
        print("Starting generate method")
        print("Parsing data...")
        self.parse_data()
        print("Data parsed")
        
        root_boxes = [box for box in self.boxes.values() if 'parent' not in box]
        print(f"Found {len(root_boxes)} root boxes")
        
        if len(root_boxes) == 1:
            print("Calculating positions...")
            self.calculate_positions(root_boxes[0], 0, 0, 2480, 3508)
            print("Positions calculated")
            
            print("Drawing boxes...")
            self.draw_boxes(root_boxes[0])
            print("Boxes drawn")
        else:
            print("Multiple root boxes found, not implemented")

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python bib_dsl.py <input_yaml_file> [output_png_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else 'output.png'

    print(f"Processing input file: {input_file}")
    print(f"Output will be saved as: {output_file}")

    dsl = BiBDSL(input_file)
    dsl.generate()
    dsl.image.save(output_file)
    print(f"Image saved. Diagram generated successfully. Output saved as '{output_file}'.")

if __name__ == "__main__":
    main()