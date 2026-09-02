from pathlib import Path
from PIL import Image, ImageDraw

source = Path('/Users/atharva/Desktop/Physicode/Final Physicode Logo copy.png')
target = Path(__file__).resolve().parents[1] / 'assets' / 'physicode-logo-transparent.png'
target.parent.mkdir(parents=True, exist_ok=True)
image = Image.open(source).convert('RGBA')
draw = ImageDraw.Draw(image)
for point in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)):
    ImageDraw.floodfill(image, point, (255, 255, 255, 0), thresh=24)
bounds = image.getchannel('A').getbbox()
if bounds:
    image = image.crop(bounds)
    padded = Image.new('RGBA', (image.width + 24, image.height + 24), (255, 255, 255, 0))
    padded.alpha_composite(image, (12, 12))
    image = padded
image.save(target, optimize=True)
print(target)
