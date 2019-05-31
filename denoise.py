from scipy import ndimage
from PIL import Image
import numpy as np
from keras.models import model_from_json

def denoise(method, path_img):
    img = Image.open(path_img).convert("L")
    img.load()
    img = np.asarray(img, dtype="int32")
    if method == 'Median filter':
        img = ndimage.median_filter(img, 3)
    else:
        img = run_keras_model(method, img)
    img = Image.fromarray(img)
    img = Image.fromarray(np.asarray(np.clip(img, 0, 255), dtype="uint8"), "L")
    img.save(path_img)

def run_keras_model(method, img):
    img = np.array(img, dtype='float32') / 255.0
    json_file = open('./model/' + method+'.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    model = model_from_json(loaded_model_json)

    model.load_weights('./model/' + method + '.h5')
    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

    x_test = img.reshape(1, img.shape[0], img.shape[1], 1)
    y_predict = model.predict(x_test)
    img_out = y_predict.reshape(img.shape)
    img_out = np.clip(img_out, 0, 1)
    img_out = img_out * 255
    return img_out
