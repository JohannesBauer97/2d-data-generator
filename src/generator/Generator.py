import glob
import os
from pathlib import Path
from PIL import Image
import random


class Generator:
    # Default parameters
    backgrounds_folder_path = "backgrounds"
    symbols_folder_path = "symbols"

    # Other class members
    symbol_paths = []
    background_paths = []
    symbols = []

    def __init__(self,
                 backgrounds_folder_path: str,
                 symbols_folder_path: str):
        """
        Creates an instance of Generator.
        Each symbol in symbols_folder_path defines a class where the image name is the class name.
        Classes are indexed ascending their filename.
        :param backgrounds_folder_path: Folder path to background images (images must be PNG or JPG/JPEG)
        :param symbols_folder_path: Folder path to symbol images (images must be PNG or JPG/JPEG)
        """
        self.backgrounds_folder_path = backgrounds_folder_path
        self.symbols_folder_path = symbols_folder_path
        self.load_images()

    # noinspection DuplicatedCode
    @classmethod
    def load_images(cls):
        """
        Loads all PNG, JPG/JPEG images from the specified folders and saves the result in class members.
        Read classes from symbols folder ascending their filename and saving the result in class member "classes".
        :return:
        """
        # Symbols
        symbols_png = glob.glob(os.path.join(cls.symbols_folder_path, "*.png"))
        symbols_jpeg = glob.glob(os.path.join(cls.symbols_folder_path, "*.jpeg"))
        symbols_jpg = glob.glob(os.path.join(cls.symbols_folder_path, "*.jpg"))
        cls.symbol_paths = symbols_png + symbols_jpeg + symbols_jpg
        cls.symbol_paths.sort()
        print(f"Loaded {len(cls.symbol_paths)} symbol images from {cls.symbols_folder_path}")

        # Classes
        cls.symbols = [Path(x).stem for x in cls.symbol_paths]

        # Backgrounds
        backgrounds_png = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.png"))
        backgrounds_jpeg = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.jpeg"))
        backgrounds_jpg = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.jpg"))
        cls.background_paths = backgrounds_png + backgrounds_jpeg + backgrounds_jpg
        cls.background_paths.sort()
        print(f"Loaded {len(cls.background_paths)} background images from {cls.backgrounds_folder_path}")

    @classmethod
    def paste_symbols_to_background(cls, symbols: list[Image.Image], background: Image.Image):
        """
        Pastes an array of images into a background image and returns the result and YOLOv5 annotation format.
        The annotation class is just an index and does not refer to the classes parsed from the symbols folder.
        :param symbols: Array of symbol images
        :param background: Background image
        :return: Result Image, Annotations Array
        """

        # Sort symbols: big to small
        symbols.sort(key=lambda x: x.size, reverse=True)

        # Coords of already pasted images
        pasted_symbol_rect_coords = []

        # Create a copy of background to not modify it
        bg = background.copy()

        # Result object (to be returned)
        annotations = []

        for symbol in symbols:
            min_x, min_y = 0, 0
            max_x = bg.width - symbol.width
            max_y = bg.height - symbol.height

            if max_y <= 0 and max_y <= 0:
                # skipping when symbol is bigger than background image
                continue

            for i in range(20):  # 20 tryouts to find a fitting coordinate
                overlapping = True
                x1 = random.randint(min_x, max_x)
                y1 = random.randint(min_y, max_y)
                w = int(symbol.width)
                h = int(symbol.height)

                # First symbol - no overlapping check needed
                if len(pasted_symbol_rect_coords) <= 0:
                    overlapping = False

                # Check if symbol would overlap other symbols
                for rect in pasted_symbol_rect_coords:
                    # Check if point is in rect
                    if cls.point_in_rect((x1, y1), rect) or cls.point_in_rect((x1+w, y1+h), rect) or cls.point_in_rect((x1, y1+h), rect) or cls.point_in_rect((x1+w, y1), rect):
                        overlapping = True
                    else:
                        overlapping = False

                # If non-overlapping coord found, save rect, annotation and exit loop
                if not overlapping:
                    # Paste image
                    rgba_symbol = symbol.convert("RGBA")
                    bg.paste(rgba_symbol, (x1, y1), rgba_symbol)
                    # Save rect
                    pasted_symbol_rect_coords.append((x1, y1, w, h))
                    # Save annotation
                    x_center = x1 + (symbol.width / 2)
                    y_center = y1 + (symbol.height / 2)
                    x_center_normalized = x_center / bg.width
                    y_center_normalized = y_center / bg.height
                    width_normalized = symbol.width / bg.width
                    height_normalized = symbol.height / bg.height
                    annotation_index = len(annotations)
                    annotation = f"class{annotation_index} {x_center_normalized} {y_center_normalized} {width_normalized} {height_normalized}"
                    annotations.append(annotation)
                    # Exit loop
                    break

        return bg, annotations

    @classmethod
    def point_in_rect(cls, point, rect):
        x1, y1, w, h = rect
        x2, y2 = x1+w, y1+h
        x, y = point
        if x1 <= x <= x2:
            if y1 <= y <= y2:
                return True
        return False

    @classmethod
    def generate(cls,
                 number_of_occurence_per_symbol = 2,
                 min_symbols_on_background=1,
                 max_symbols_on_background=2,
                 relative_resize=True,
                 random_rotation=True,
                 random_background_color=True):
        # Creating an array of all symbol paths (multiplied by number of times it should occur)
        all_symbol_paths = []
        for symbol_path in cls.symbol_paths:
            for i in range(number_of_occurence_per_symbol):
                all_symbol_paths.append(symbol_path)
        # Shuffle the array to get random symbols when iterating later
        random.shuffle(all_symbol_paths)

        # Error handling
        if max_symbols_on_background > len(all_symbol_paths):
            print(f"It's not possible to set a bigger value for max_symbols_on_background ({max_symbols_on_background}) than {len(all_symbol_paths)}")
            return

        last_index = 0
        file_name_index = 0
        do_work = True
        while do_work:

            next_index = last_index + random.randint(min_symbols_on_background, max_symbols_on_background)
            symbols = [] # random batch of symbol paths
            symbol_class_indices = [] # corresponding class index
            tmp = last_index # to avoid that range() mutates while looping

            if next_index >= len(all_symbol_paths):
                next_index = len(all_symbol_paths)
                do_work = False

            for i in range(tmp - 1, next_index):
                class_index = cls.symbol_paths.index(all_symbol_paths[i])
                symbols.append(Image.open(all_symbol_paths[i]))
                symbol_class_indices.append(class_index)
                last_index = next_index + 1

            # Get a background
            background = Image.open(random.choice(cls.background_paths))

            # Resizing, Rotation
            if relative_resize or random_rotation or random_background_color:
                for i, symbol in enumerate(symbols):
                    # Size
                    if relative_resize:
                        available_sizes = [
                            (int(0.05*background.width), int(0.05*background.height)),
                            (int(0.08*background.width), int(0.08*background.height)),
                            (int(0.1*background.width), int(0.1*background.height))
                        ]
                        symbols[i] = symbol.resize(random.choice(available_sizes))

                    # Rotation
                    if random_rotation:
                        available_rotations = [0, 5, 10]
                        symbols[i] = symbol.rotate(random.choice(available_rotations))

                    # Color
                    if random_background_color:
                        available_colors = ["red", "green", "blue", "white"]
                        bg = Image.new("RGBA", symbol.size, random.choice(available_colors))
                        bg.paste(symbol, (0, 0), symbol)
                        symbols[i] = bg


            # Composite symbols into background
            composition, annotations = cls.paste_symbols_to_background(symbols, background)

            # Replace annotation class placeholder with correct class index
            for i, annotation in enumerate(annotations):
                annotations[i] = annotation.replace(f"class{i}", str(symbol_class_indices[i]))

            # Save to disk
            cls.save_to_disk(composition, annotations, f"image{file_name_index}")

            file_name_index += 1

    @classmethod
    def save_to_disk(cls, composition: Image.Image, annotations: list[str], name: str):
        # Creating output folder structure
        images_folder = os.path.join("out", "images")
        labels_folder = os.path.join("out", "labels")
        Path(images_folder).mkdir(parents=True, exist_ok=True)
        Path(labels_folder).mkdir(parents=True, exist_ok=True)

        composition.save(os.path.join(images_folder, f"{name}.jpg"))
        annotation_file = open(os.path.join(labels_folder, f"{name}.txt"), "w")
        for annotation in annotations:
            annotation_file.write(annotation + "\n")
        annotation_file.close()
