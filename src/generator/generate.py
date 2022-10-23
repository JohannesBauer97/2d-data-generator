from Generator import Generator
from PIL import Image

generator = Generator(
    backgrounds_folder_path="backgrounds",
    symbols_folder_path="symbols"
)

bg = Image.open("backgrounds/large.jpg")
s1 = Image.open("symbols/C150.png")
s2 = Image.open("symbols/A300.png")
s3 = Image.open("symbols/B500.png")

bg = generator.paste_symbols_to_background([s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3, s3], bg)
bg.show()