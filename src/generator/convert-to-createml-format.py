import os
import json
from PIL import Image, ImageDraw


def yolo_to_create_ml(yolo_dir, create_ml_file):
    # Initialize an empty list to store the new annotation data
    create_ml_data = []

    # Iterate through all files in the YOLO annotation directory
    for filename in os.listdir(yolo_dir):
        # Check if the file is a txt file
        if filename.endswith(".txt"):
            # Open the txt file
            with open(os.path.join(yolo_dir, filename), 'r') as f:
                # Read the contents of the file
                contents = f.read().strip()
                lines = contents.split("\n")
                for line in lines:
                    # Split the line by space
                    values = line.split(" ")
                    # Get the image path
                    image_path = os.path.splitext(filename)[0] + ".jpg"
                    image = Image.open("./out/images/" + image_path)
                    # Extract the label, x, y, width and height
                    label = values[0]
                    x_center = float(values[1])# * image.width
                    y_center = float(values[2])# * image.height
                    width = float(values[3])# * image.width
                    height = float(values[4])# * image.height
                    # calculate xmin, ymin, xmax and ymax
                    xmin = x_center - width / 2
                    ymin = y_center - height / 2
                    xmax = x_center + width / 2
                    ymax = y_center + height / 2

                    # Append the new annotation data to the list
                    create_ml_data.append({
                        'image': image_path,
                        'annotations': [{
                            'type': 'rectangle',
                            'coordinates': {
                                'x': x_center * image.width,
                                'y': y_center * image.height,
                                'width': width * image.width,
                                'height': height * image.height,
                            },
                            'label': label
                        }]
                    })

    # Write the new annotation data to the Create ML file
    with open(create_ml_file, 'w') as f:
        json.dump(create_ml_data, f)


yolo_dir = "./out/labels"
create_ml_file = './create_ml_annotations.json'
yolo_to_create_ml(yolo_dir, create_ml_file)
