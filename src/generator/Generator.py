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
    classes = []

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
        cls.classes = [Path(x).stem for x in cls.symbol_paths]

        # Backgrounds
        backgrounds_png = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.png"))
        backgrounds_jpeg = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.jpeg"))
        backgrounds_jpg = glob.glob(os.path.join(cls.backgrounds_folder_path, "*.jpg"))
        cls.background_paths = backgrounds_png + backgrounds_jpeg + backgrounds_jpg
        cls.background_paths.sort()
        print(f"Loaded {len(cls.background_paths)} background images from {cls.backgrounds_folder_path}")

    @classmethod
    def paste_symbols_to_background(cls, symbols: list[Image.Image], background: Image.Image):
        # Sort symbols: big to small
        symbols.sort(key=lambda x: x.size, reverse=True)

        # Coords of already pasted images
        pasted_symbol_rect_coords = []

        # Create a copy of background to not modify it
        bg = background.copy()

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

                # If non-overlapping coord found, save rect and exit loop
                if not overlapping:
                    rgba_symbol = symbol.convert("RGBA")
                    bg.paste(rgba_symbol, (x1, y1), rgba_symbol)
                    pasted_symbol_rect_coords.append((x1, y1, w, h))
                    break

        return bg

    @classmethod
    def point_in_rect(cls, point, rect):
        x1, y1, w, h = rect
        x2, y2 = x1+w, y1+h
        x, y = point
        if x1 <= x <= x2:
            if y1 <= y <= y2:
                return True
        return False
