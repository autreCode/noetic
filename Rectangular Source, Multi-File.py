from PIL import Image
import os

# Constants
output_width = 4640
output_height = 6160
pixelSize = 40
root_folder = '[ROOT FOLDER PATH FOR OUTPUT HERE]'
output_html = '[FILEPATH FOR SAVING THE HTML]'
thumbs_folder = '[FILEPATH FOR SAVING THE IMAGE THUMBNAIL]'
output_prefix = '[OUTPUT FILE PREFIX]' #Files will be saved with consecutive numbering and this prefix
num_cols = 150 #number of colours to use in the output image

def quantize_image(image_path):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        
        # Resize the image according to the constants
        new_width, new_height = output_width // pixelSize, output_height // pixelSize
        image = image.resize((new_width, new_height))
        
        # Increase the number of colors to quantize to
        image_quantized = image.quantize(colors=num_cols)
        image_quantized = image_quantized.convert('RGB')
        
        width, height = image_quantized.size
        
        # Convert image data to list for easier processing
        image_data_list = list(image_quantized.getdata())
        
        # Generate the color palette dynamically from the quantized image
        unique_colors = list(set(image_data_list))
        palette = sorted(unique_colors, key=image_data_list.count, reverse=True)
        
        # Convert image to 2D array format
        image_array = [[palette.index(image_quantized.getpixel((x, y))) for x in range(width)] for y in range(height)]
        
        return image_array, palette, output_width, output_height

def generate_html(image_array, palette, canvas_width, canvas_height, filename):
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
                    ctx.fillRect(x * {pixelSize}, y * {pixelSize}, {pixelSize}, {pixelSize});
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    palette_str = ",\n".join([f"{i}: 'rgb({palette[i][0]},{palette[i][1]},{palette[i][2]})'"for i in range(len(palette))])
    image_data_str = '[\n' + ',\n'.join(['[' + ', '.join(map(str, row)) + ']' for row in image_array]) + '\n]'
    
    html_output = html_template.format(palette=palette_str, image_data=image_data_str, canvas_width=canvas_width, canvas_height=canvas_height, pixelSize=pixelSize)
    
    with open(filename, 'w') as file:
        file.write(html_output)
    print(os.path.basename(filename) + ' created')

def generate_thumbnail(image_array, palette, canvas_width, canvas_height, filename):
    thumb_image = Image.new('RGB', (canvas_width, canvas_height))
    for y, row in enumerate(image_array):
        for x, color_index in enumerate(row):
            color = palette[color_index]
            thumb_image.paste(color, (x * pixelSize, y * pixelSize, (x + 1) * pixelSize, (y + 1) * pixelSize))
    thumb_image.save(filename)
    print("Thumbnail " + os.path.basename(filename) + " saved")

if __name__ == '__main__':
    image_files = [f for f in os.listdir(root_folder) if f.endswith('.png') or f.endswith('.jpg')]
    total_images = len(image_files)

    number_of_digits = len(str(total_images))
    format_string = "{:0" + str(number_of_digits) + "}"

    for index, image_name in enumerate(image_files, 1):
        image_path = os.path.join(root_folder, image_name)
        image_array, palette, canvas_width, canvas_height = quantize_image(image_path)

        formatted_index = format_string.format(index)
        output_filename_html = os.path.join(output_html, f"{output_prefix} {formatted_index}.html")
        output_filename_thumb = os.path.join(thumbs_folder, f"{output_prefix} {formatted_index}.png")

        generate_html(image_array, palette, canvas_width, canvas_height, output_filename_html)
        generate_thumbnail(image_array, palette, canvas_width, canvas_height, output_filename_thumb)
