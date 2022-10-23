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

        # Paste big symbols first
        # Generate random x1, y1 coords, calculate based on width, height the x2, y2 coord
        #
        # Overlapping Check: (case: overlapping)
        #   Have a list (pastedSymbols) of all already pasted symbol coords: [[x1,y1,x2,y2],...]
        #   overlapping = false
        #   ForEach p in pastedSymbols:
        #     if x1 >= px1 and x1 <= px2 and y1 >= py1 and y2 <= py2:
        #       overlapping = true
        #

        # Sort symbols: big to small
        symbols.sort(key=lambda x: x.size, reverse=True)

        # Coords of already pasted images
        pasted_symbol_coords = []

        # Create a copy of background to not modify it
        bg = background.copy()

        for symbol in symbols:
            min_x, min_y = 0, 0
            max_x = bg.width - symbol.width
            max_y = bg.height - symbol.height

            for i in range(20):  # 20 tryouts to find a fitting coordinate
                overlapping = True
                x1 = random.randint(min_x, max_x)
                y1 = random.randint(min_y, max_y)
                x2 = x1 + symbol.width
                y2 = y1 + symbol.height
                x3 = x1
                y3 = y2
                x4 = x2
                y4 = y1

                """
                (x1,y1) --------- (x4, y4)
                        |       |
                        |       |
                        |       |
                (x3,y3) --------- (x2, y2)
                """

                # First symbol - no overlapping check needed
                if len(pasted_symbol_coords) <= 0:
                    overlapping = False

                # Check if symbol would overlap other symbols
                for p in pasted_symbol_coords:
                    px1, py1, px2, py2, px3, py3, px4, py4 = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]

                    # Check top left point and bottom right point if they are outside
                    if ((x1 < px1 or x1 > px2) and (y1 < py1 or y1 > py2)) and ((x2 < px1 or x2 > px2) and (y2 < py1 or y2 > py2)):
                        if ((x3 < px3 or x3 > px4) and (y3 < py3 or y3 > py4)) and ((x4 < px3 or x4 > px4) and (y4 < py3 or y4 > py4)):
                            overlapping = False
                        else:
                            overlapping = True
                    else:
                        overlapping = True

                # If non-overlapping coord found, save coords and exit loop
                if not overlapping:
                    rgba_symbol = symbol.convert("RGBA")
                    bg.paste(rgba_symbol, (x1, y1), rgba_symbol)
                    pasted_symbol_coords.append([x1, y1, x2, y2, x3, y3, x4, y4])
                    break

        return bg
