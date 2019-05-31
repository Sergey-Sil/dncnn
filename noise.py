from PIL import Image
import numpy as np

def noise_image(path, sigma = 10):
    img = load_image(path)
    noise = np.random.normal(0, sigma, img.shape)
    noise_img = img + noise
    noise_img[noise_img > 255] = 255
    noise_img[noise_img < 0] = 0
    img = noise_img.astype(np.uint8)
    save_image(img, path)

def load_image(path):
    img = Image.open(path).convert("L")
    img.load()
    data = np.asarray(img, dtype="int32")
    return data

def save_image(data, path):
    img = Image.fromarray(np.asarray(np.clip(data, 0, 255), dtype="uint8"), "L" )
    img.save(path)



