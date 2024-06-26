# Box-in-Box DSL (Domain-Specific Language)

## Description
Box-in-Box DSL is a Python-based tool that generates hierarchical box diagrams from YAML input. It's designed to visualize nested structures such as business capability maps, organizational charts, or any hierarchical data that can be represented in a nested box format.

## Features
- Generates high-resolution (A4 size, 300 DPI) PNG images
- Supports up to 3 levels of nesting
- Customizable colors for each box
- Automatic text sizing and positioning
- Flexible output naming

## Requirements
- Python 3.6+
- PIL (Pillow)
- PyYAML

## Installation
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/box-in-box-dsl.git
   cd box-in-box-dsl
   ```

2. Install the required packages:
   ```
   pip install pillow pyyaml
   ```

## Usage
1. Create a YAML file with your hierarchical structure. Example:
   ```yaml
   Root:
     color: "#FFFFFF"
     children:
       Child1:
         color: "#E0E0E0"
         children:
           Grandchild1:
             color: "#C0C0C0"
           Grandchild2:
             color: "#D0D0D0"
       Child2:
         color: "#F0F0F0"
   ```

2. Run the script:
   ```
   python bib_dsl.py input.yaml [output.png]
   ```
   If you don't specify an output file name, it will default to `output.png`.

## Disclaimer
This program was co-created with the assistance of AI. The creators and contributors of this software assume no liability for its use or any consequences arising from its use. The software is provided "as is", without warranty of any kind, express or implied.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements
- This project uses the Pillow library for image processing.
- PyYAML is used for parsing YAML files.