import sys
import yaml
from PIL import Image, ImageDraw, ImageFont

class BiBDSL:
    def __init__(self, yaml_file):
        self.data = self.load_yaml(yaml_file)
        self.boxes = {}
        self.padding = 10
        self.image = Image.new('RGB', (2480, 3508), color='white')  # A4 size at 300 DPI
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.font = ImageFont.truetype("Arial.ttf", 36)
        except IOError:
            print("Arial font not found, using default font")
            self.font = ImageFont.load_default()

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
            box = {'name': key, 'level': level, 'children': []}
            if isinstance(value, dict):
                if 'color' in value:
                    box['color'] = value['color']
                if 'children' in value:
                    children = value['children']
                    if isinstance(children, dict):
                        for child_key, child_value in children.items():
                            child_box = parse_item(child_key, child_value, key, level + 1)
                            box['children'].append(child_box)
            if parent:
                box['parent'] = parent
            self.boxes[key] = box
            return box

        for key, value in self.data.items():
            parse_item(key, value)

    def calculate_positions(self, box, x, y, available_width, available_height):
        box['x'] = x + self.padding
        box['y'] = y + self.padding
        box['width'] = available_width - 2 * self.padding
        box['height'] = available_height - 2 * self.padding

        if box['children']:
            child_height = (box['height'] - self.padding * (len(box['children']) + 1)) / len(box['children'])
            for i, child in enumerate(box['children']):
                child_y = box['y'] + self.padding + i * (child_height + self.padding)
                self.calculate_positions(child, box['x'] + self.padding, child_y, box['width'] - 2 * self.padding, child_height)

    def draw_boxes(self, box):
        self.draw.rectangle([box['x'], box['y'], box['x'] + box['width'], box['y'] + box['height']], 
                            outline='black', fill=box.get('color', 'white'))
        
        # Use textbbox instead of textsize
        left, top, right, bottom = self.draw.textbbox((0, 0), box['name'], font=self.font)
        text_width = right - left
        text_height = bottom - top
        
        text_x = box['x'] + (box['width'] - text_width) / 2
        text_y = box['y'] + self.padding
        self.draw.text((text_x, text_y), box['name'], fill='black', font=self.font)

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
        
        print("Saving image...")
        self.image.save('output.png')
        print("Image saved. Diagram generated successfully. Output saved as 'output.png'.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python bib_dsl.py <input_yaml_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    print(f"Processing input file: {input_file}")
    dsl = BiBDSL(input_file)
    dsl.generate()

if __name__ == "__main__":
    main()