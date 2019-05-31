from PIL import Image
import numpy as np

def ssim(img1, img2):
    mean_x = np.mean(img1)
    mean_y = np.mean(img2)

    std_x = np.std(img1)
    std_y = np.std(img2)

    cov = np.cov(img1.flatten(), img2.flatten())[0][1]

    c1 = (0.01*255)**2
    c2 = (0.04*255)**2

    value = ((2*mean_x*mean_y + c1)*(2*cov + c2))/((mean_x**2 + mean_y**2 + c1)*(std_x**2 + std_y**2 + c2))
    return value


def psnr(img1, img2):
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * np.log10(PIXEL_MAX / np.sqrt(mse))

def mse(img1, img2):
    return np.mean((img1 - img2)**2)

def load_image(path):
    img = Image.open(path).convert("L")
    img.load()
    img = np.asarray(img, dtype="int32")
    return img

def stat(path_clean, path_noise, path_denoised):
    img_clean = load_image(path_clean)
    img_noise = load_image(path_noise)
    img_denoised = load_image(path_denoised)
    s = get_stat(img_clean, img_noise, img_denoised)
    return s


def get_stat(img_clean, img_noise, img_denoised):
    result = ""
    psnr_noise, psnr_denoised = psnr(img_clean, img_noise), psnr(img_clean, img_denoised)
    ssim_noise, ssim_denoised = ssim(img_clean, img_noise), ssim(img_clean, img_denoised)
    mse_noise, mse_denoised = mse(img_clean, img_noise), mse(img_clean, img_denoised)

    result += '\nPSNR noise image: ' + str(psnr_noise)
    result += '\nSSIM noise image: ' + str(ssim_noise)
    result += '\nMSE noise image: ' + str(mse_noise)

    result += '\n\nPSNR denoise image: ' + str(psnr_denoised)
    result += '\nSSIM denoise image: ' + str(ssim_denoised)
    result += '\nMSE denoise image: ' + str(mse_denoised)

    return result