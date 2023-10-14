import os
import io
import json
import base64
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

# Constants
output_side = 104 #this is the size of the base64 image being output
thumb_multiplier = 10 #this is applied to output_side to define the output size of the PNG thumb
thumb_side = output_side * thumb_multiplier
pixelSize = 1
root_folder = '[ROOT FOLDER PATH FOR OUTPUT HERE]'
thumbs_folder = '[FILEPATH FOR SAVING THE IMAGE THUMBNAIL]'
output_prefix = '[OUTPUT FILE PREFIX]' #Files will be saved with consecutive numbering and this prefix
num_cols = 20
json_folder = '[FILEPATH FOR SAVING THE JSON]'  # Define path to save JSON files

def quantize_image(image_path, desired_size=output_side):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        
        # Resize the image according to the desired size
        new_width, new_height = desired_size // pixelSize, desired_size // pixelSize
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
        
        return image_array, palette

def hex_to_rgb(value):
    # Converts HEX to RGB tuple
    value = value.lstrip('#')
    length = len(value)
    return tuple(int(value[i:i + length // 3], 16) for i in range(0, length, length // 3))

if __name__ == '__main__':
    image_files = [f for f in os.listdir(root_folder) if f.endswith('.png') or f.endswith('.jpg')]
    total_images = len(image_files)

    number_of_digits = len(str(total_images))
    format_string = "{:0" + str(number_of_digits) + "}"

    for index, image_name in enumerate(image_files, 1):
        print(f"Processing {image_name}...")
        image_path = os.path.join(root_folder, image_name)
        
        # Quantize only once for output_side
        image_array, palette = quantize_image(image_path, desired_size=output_side)
        
        # Generate base64 from the generated pixel-art image
        pixel_art_image_base64 = generate_base64(image_array, palette, output_side)
        with io.BytesIO(base64.b64decode(pixel_art_image_base64)) as buffered:
            pixel_art_image = Image.open(buffered).copy()

        # Upscale the pixel-art image to create the thumbnail
        upscale_factor = thumb_side // output_side
        thumbnail = pixel_art_image.resize((thumb_side, thumb_side), Image.NEAREST)
        
        # Save the thumbnail
        formatted_index = format_string.format(index)
        output_filename_thumb = os.path.join(thumbs_folder, f"{output_prefix} {formatted_index}.png")
        thumbnail.save(output_filename_thumb)

        # Derive the sequential name without spaces or underscores for the JSON structure
        img_name_without_ext = f"{output_prefix}{formatted_index}".replace(" ", "").replace("_", "")
        
        # Derive the name with spaces from the source PNG
        img_name_with_spaces = os.path.splitext(image_name)[0].replace("_", " ")

        # JSON filename should be formatted with spaces
        json_filename_with_spaces = f"{output_prefix} {formatted_index}.json"
        json_filename = os.path.join(json_folder, json_filename_with_spaces)

        data = {
            "721": {
                "1cba2915a5c259ee50841f1b297b752df3e172dd9444faf169e3b934": {
                    img_name_without_ext: {
                        "collection": "The Horror",
                        "artist": "NOETIC",
                        "copyright": "2023 NOETIC. All Rights Reserved.",
                        "name": img_name_with_spaces,
                        "files": [
                            {
                                "mediaType": "image/png",
                                "src": ["data:image/png;base64,"] + [pixel_art_image_base64[i:i+64] for i in range(0, len(pixel_art_image_base64), 64)]
                            }
                        ],
                        "image": "[thumbnail ipfs address here]",
                        "mediaType": "image/png"
                    }
                }
            }
        }

        with open(json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=2)

        print(f"Thumbnail and JSON saved for {image_name}\n")
