# Pixel Art Generator: Python Scripts for Pixel Art Creation
## Overview
This repository contains Python scripts that assist in creating pixel art. By leveraging the PIL library, these scripts provide an automated process to dynamically quantise PNG source files to emphasize dominant colors then rebuild the image using coloured boxes rendered by JavaScript in an output HTML file.

## Features
- **Image Quantization**: Transform images into a reduced set of colors, retaining their essential details.
- **Dynamic Palette Generation**: Extracts the dominant colors from an image to build a dynamic color palette.
- **HTML Output**: Transforms the pixelated image data into an HTML file with embedded JavaScript for immediate web visualization.

## Requirements
- Python 3.x
- Library requirements stated at the top of each script

## Usage
All constants are stated at the top of each script:
- wh / w & h: Determines the output canvas width & height (wh if square, independent w and h variables if not).
- pixelSize: Defines the "resolution" of the pixelated effect (note that the above should be divisible by this number).
- root_folder: Directory where the resultant files will be saved.
- source_image: Path to the input image.
- output_filename: Name of the resultant HTML file.

## Run the script:
bash
Copy code
python <script_name>.py
The script will generate an HTML file (+ any others, such as PNG) in the specified root_folder with the name provided in output_filename.

## Example
Given an input image "Box 3 source.png", the script processes it to extract its primary colors, pixelates it based on the provided parameters, and then converts this pixel art representation into an interactive HTML file named "Builders Box 3.html".

## Customization
- Quantization Colors: You can modify the number of colors the image should be quantized to by changing the value in the image.quantize(colors=value) function.
- Output Dimensions: The wh / w & h constant(s) and pixelSize are key parameters to determine the granularity of the pixel effect. Play around with different values to find the best fit for your image.

## Licensing
This project is licensed under the MIT License. Feel free to use, modify, and distribute the code as you see fit, but kindly provide attribution to this repository.
