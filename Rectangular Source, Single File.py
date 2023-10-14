from PIL import Image
import json

# Constants defined in the python script
output_width = 4640 #output sizes should be relative to input to avoid distortion
output_height = 6160
pixelSize = 40  #should be a common factor of the above & a round number
root_folder = '[ROOT FOLDER PATH FOR OUTPUT HERE]'
source_image = '[SOURCE IMAGE PATH HERE]'
output_filename = '[OUTPUT FILE NAME]'
num_cols = 150 #how many colours in output image?

def quantize_image(image_path):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        
        # Resize the image according to the constants
        new_width, new_height = output_width // pixelSize, output_height // pixelSize
        image = image.resize((new_width, new_height))
        
        # Increase the number of colors to quantize to. Set it to a desired value, e.g. 20.
        image_quantized = image.quantize(colors=num_cols)
        image_quantized = image_quantized.convert('RGB')
        
        width, height = image_quantized.size
        
        # Convert image data to list for easier processing
        image_data_list = list(image_quantized.getdata())
        
        # Generate the color palette dynamically from the quantized image
        unique_colors = list(set(image_data_list))
        palette = sorted(unique_colors, key=image_data_list.count, reverse=True)  # Removed slice operation
        
        # Convert image to 2D array format
        image_array = [[palette.index(image_quantized.getpixel((x, y))) for x in range(width)] for y in range(height)]
        
        return image_array, palette, output_width, output_height

def generate_html(image_array, palette, canvas_width, canvas_height):
    html_template = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                canvas {{
                    display: block;
                    position: absolute;
                }}
            </style>
        </head>
    <body>
        <canvas id="canvas" width="{canvas_width}" height="{canvas_height}" style='object-fit: contain; width: 100vw; height: 100vh;'></canvas>
        <script>
            const colors = {{
                {palette}
            }};
            const fig = {image_data};
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            ctx.imageSmoothingEnabled = false;
            for (let y = 0; y < fig.length; y++) {{
                for (let x = 0; x < fig[y].length; x++) {{
                    ctx.fillStyle = colors[fig[y][x]];
                    ctx.fillRect(x * {pixelSize}, y * {pixelSize}, {pixelSize}, {pixelSize});  //Use pixelSize for drawing
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    palette_str = ",\n".join([f"{i}: 'rgb({palette[i][0]},{palette[i][1]},{palette[i][2]})'"for i in range(len(palette))])

    # Convert the 2D array (image_array) to a string where each list is on its own line
    image_data_str = '[\n' + ',\n'.join(['[' + ', '.join(map(str, row)) + ']' for row in image_array]) + '\n]'

    html_output = html_template.format(palette=palette_str, image_data=image_data_str, canvas_width=canvas_width, canvas_height=canvas_height, pixelSize=pixelSize)
    
    with open(root_folder+output_filename+'.html', 'w') as file:
        file.write(html_output)
    print(output_filename+'.html created')

if __name__ == '__main__':
    image_path = source_image
    image_array, palette, canvas_width, canvas_height = quantize_image(image_path)
    generate_html(image_array, palette, canvas_width, canvas_height)
