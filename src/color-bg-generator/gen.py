from PIL import Image, ImageDraw
from PIL import ImageFilter
import glob
import os
from PIL import ImageColor
from pathlib import Path
import random

# Settings
background_size = (1280, 1280)

# Symbols
symbol_paths = glob.glob(os.path.join("symbols", "*.png"))
symbol_paths.sort()

# Background generation
bg_colors = ["red", "green", "blue", "gray", "yellow", "purple", "black"]

for lol in range(2000):
    background = Image.new("RGBA", background_size, random.choice(bg_colors))

    # Drawing colored ellipses
    bg_draw = ImageDraw.Draw(background)
    for i in range(500):
        x = random.randint(-15, background.width)
        y = random.randint(-15, background.height)
        w = random.randint(100, 250)
        l = random.randint(100, 250)
        c = random.choice(bg_colors)
        bg_draw.ellipse((x, y, x+w, y+l), fill=c, outline=None)
    background = background.filter(ImageFilter.MedianFilter(size=9))

    # Label generation
    label_width = random.randint(int(background_size[0]*0.2), int(background_size[1]*0.4))
    label_height = random.randint(int(background_size[0]*0.5), int(background_size[1]*0.6))
    label = Image.new("RGBA", (label_width, label_height), "white")

    # Compose symbols
    num_symbols = 2
    selected_symbols = random.choices(symbol_paths, k=num_symbols)
    annotations = []
    for i, symbol_path in enumerate(selected_symbols):
        symbol = Image.open(symbol_path)
        symbol = symbol.resize((int(label_width/num_symbols), int(label_width/num_symbols)))
        x = 0 if i == 0 else int(label_width/num_symbols) * i
        y = 10
        label.paste(symbol, (x, y), mask=symbol)
        # Writing annotation
        x_center = x + (symbol.width / 2)
        y_center = y + (symbol.height / 2)
        x_center_normalized = x_center / background.width
        y_center_normalized = y_center / background.height
        width_normalized = symbol.width / background.width
        height_normalized = symbol.height / background.height
        class_number = symbol_paths.index(symbol_path)
        annotation = f"{class_number} {x_center_normalized} {y_center_normalized} {width_normalized} {height_normalized}"
        annotations.append(annotation)


    # Paste label into background
    label_x_pos = random.randint(0, background.width - label.width)
    label_y_pos = random.randint(0, background.height - label.height)
    background.paste(label, (label_x_pos, label_y_pos), mask=label)
    #background.show()
    print(lol)

    # Save to disk
    # Creating output folder structure
    images_folder = os.path.join("out", "images")
    labels_folder = os.path.join("out", "labels")
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    Path(labels_folder).mkdir(parents=True, exist_ok=True)
    background = background.convert("RGB")
    background.save(os.path.join(images_folder, f"img{lol}.jpg"))
    annotation_file = open(os.path.join(labels_folder, f"img{lol}.txt"), "w")
    for annotation in annotations:
        annotation_file.write(annotation + "\n")
    annotation_file.close()
