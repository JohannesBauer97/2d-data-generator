from Generator import Generator
from PIL import Image

generator = Generator(
    backgrounds_folder_path="backgrounds",
    symbols_folder_path="symbols",
)

generator.generate(
    number_of_occurence_per_symbol=1000,
    max_symbols_on_background=10
)
