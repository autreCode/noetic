from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
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
        
        # Convert image data to a 2D numpy array
        image_data = np.array(image)
        flattened_data = image_data.reshape((-1, 3))
        
        unique_colors = len(np.unique(flattened_data, axis=0))
        
        if unique_colors > num_cols:
            # Use KMeans to find the most dominant colors only if necessary
            kmeans = KMeans(n_clusters=num_cols)
            kmeans.fit(flattened_data)
            labels = kmeans.predict(flattened_data)
            centers = kmeans.cluster_centers_
        
            # Convert the centroids back to 8-bit values
            centers = np.uint8(centers)
        else:
            centers = np.unique(flattened_data, axis=0)
        
        # Convert the centroids to HEX values for palette
        palette = [f'#{center[0]:02X}{center[1]:02X}{center[2]:02X}' for center in centers]
        
        # Map the labels to the centroids
        quantized_flattened = centers[labels]
        
        # Reshape back to the original image shape
        image_quantized = quantized_flattened.reshape(image_data.shape)
        
        # Convert the quantized data to an image
        image_quantized = Image.fromarray(image_quantized)
        
        width, height = image_quantized.size
        image_array = [[palette.index(f'#{pixel[0]:02X}{pixel[1]:02X}{pixel[2]:02X}') for pixel in [image_quantized.getpixel((x, y)) for x in range(width)]] for y in range(height)]
        
        return image_array, palette, output_width, output_height

def hex_to_rgb(value):
    # Converts HEX to RGB tuple
    value = value.lstrip('#')
    length = len(value)
    return tuple(int(value[i:i + length // 3], 16) for i in range(0, length, length // 3))

def generate_html_without_compression(image_array, palette, canvas_width, canvas_height, filename):
    p_str = ",\n".join([f"{i}: '{color}'" for i, color in enumerate(palette)])
    data_str = ",".join([str(color) for row in image_array for color in row])
    
    html_output = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <style>
                body, html {{ margin: 0; padding: 0; overflow: hidden; }}
                canvas {{ display: block; position: absolute; }}
            </style>
        </head>
    <body>
        <canvas id="c" width="{canvas_width}" height="{canvas_height}" style='object-fit: contain; width: 100vw; height: 100vh;'></canvas>
        <script>
            const p = {{
                {p_str}
            }};
            const fig = [{data_str}];
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            ctx.imageSmoothingEnabled = false;
            let x = 0, y = 0;
            for (i = 0; i < fig.length; i++) {{
                let ci = fig[i];
                ctx.fillStyle = p[ci];
                ctx.fillRect(x * {pixelSize}, y * {pixelSize}, {pixelSize}, {pixelSize});
                x++;
                if (x >= {canvas_width} / {pixelSize}) {{ x = 0; y++; }}
            }}
        </script>
    </body>
    </html>
    """

    with open(filename, 'w') as file:
        file.write(html_output)
    print(os.path.basename(filename) + ' created')

def generate_thumbnail(image_array, palette, canvas_width, canvas_height, filename):
    thumb_image = Image.new('RGB', (canvas_width, canvas_height))
    for y, row in enumerate(image_array):
        for x, color_index in enumerate(row):
            hex_color = palette[color_index]
            rgb_color = hex_to_rgb(hex_color)  # Convert HEX to RGB tuple
            thumb_image.paste(rgb_color, (x * pixelSize, y * pixelSize, (x + 1) * pixelSize, (y + 1) * pixelSize))
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

        generate_html_without_compression(image_array, palette, canvas_width, canvas_height, output_filename_html)
        generate_thumbnail(image_array, palette, canvas_width, canvas_height, output_filename_thumb)
