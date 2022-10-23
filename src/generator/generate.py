from Generator import Generator
from PIL import Image

generator = Generator(
    backgrounds_folder_path="backgrounds",
    symbols_folder_path="symbols"
)

generator.generate()
