from PIL import Image

# Constants defined in the python script
wh = 4096  #output canvas width & height
pixelSize = 24  #ie wh 4096 & pixelSize 32 = 128 x 128 'pixels'
root_folder = '[ROOT FOLDER PATH FOR OUTPUT HERE]'
source_image = '[SOURCE IMAGE PATH HERE]'
output_filename = 'Builders Box 3'

def quantize_image(image_path):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        
        # Resize the image according to the constants
        new_width, new_height = wh // pixelSize, wh // pixelSize
        image = image.resize((new_width, new_height))
        
        # Increase the number of colors to quantize to. Set it to a desired value, e.g. 20.
        image_quantized = image.quantize(colors=200)
        image_quantized = image_quantized.convert('RGB')
        
        width, height = image_quantized.size
        
        # Convert image data to list for easier processing
        image_data_list = list(image_quantized.getdata())
        
        # Generate the color palette dynamically from the quantized image
        unique_colors = list(set(image_data_list))
        palette = sorted(unique_colors, key=image_data_list.count, reverse=True) 
        
        # Convert image to 2D array format
        image_array = [[palette.index(image_quantized.getpixel((x, y))) for x in range(width)] for y in range(height)]
        
        return image_array, palette, wh, wh

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
            const fig = [
                {image_data}
            ];
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
    
    palette_str = ",\n".join([f"{i}: 'rgb({palette[i][0]},{palette[i][1]},{palette[i][2]})'" for i in range(len(palette))])
    image_data_str = ',\n'.join([str(row) for row in image_array])
    html_output = html_template.format(palette=palette_str, image_data=image_data_str, canvas_width=canvas_width, canvas_height=canvas_height, pixelSize=pixelSize)
    
    with open(root_folder+output_filename+'.html', 'w') as file:
        file.write(html_output)
    print(output_filename+'.html created')

if __name__ == '__main__':
    image_path = source_image
    image_array, palette, canvas_width, canvas_height = quantize_image(image_path)
    generate_html(image_array, palette, canvas_width, canvas_height)
