from PIL import Image

def snip(pos, img):
    img_to_crop = Image.open(img)
    img_to_crop.crop(pos).save("./cropped.jpg")

snip(((708,541,1772,1355)), r"D:\Nithish\CambridgePaperParser\img\img-05.jpg")
