from flask import Flask, render_template, Response, stream_with_context, Request

import cv2
import numpy as np
import requests

app = Flask(__name__)



def show_images_mask1():
    img = cv2.imread('./img/img1.jpeg')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = imgGray.shape

    kernel = np.ones((37,37),np.uint8)
    elemento = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    erosion = cv2.erode(imgGray,elemento,iterations = 1, )
    dilation = cv2.dilate(imgGray,elemento,iterations = 1)
    tophat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, kernel)
    blackhat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, kernel)

    restaImgs = cv2.subtract(tophat, blackhat)
    finalImg = cv2.add(restaImgs, imgGray)

    total_image = np.zeros((height, width * 6), dtype=np.uint8)
    total_image[:, :width] = imgGray
    total_image[:, width:2*width] = erosion
    total_image[:, 2*width:3*width] = dilation
    total_image[:, 3*width:4*width] = tophat
    total_image[:, 4*width:5*width] = blackhat
    total_image[:, 5*width:6*width] = finalImg

    
    (flag, encodedImage) = cv2.imencode(".jpg", total_image)

    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


def show_images_mask2():
    img = cv2.imread('./img/img2.jpeg')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = imgGray.shape

    kernel = np.ones((35,35),np.uint8)
    elemento = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))

    erosion = cv2.erode(imgGray,elemento,iterations = 1)
    dilation = cv2.dilate(imgGray,elemento,iterations = 1)
    tophat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, kernel)
    blackhat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, kernel)

    restaImgs = cv2.subtract(tophat, blackhat)
    finalImg = cv2.add(restaImgs, imgGray)

    total_image = np.zeros((height, width * 6), dtype=np.uint8)
    total_image[:, :width] = imgGray
    total_image[:, width:2*width] = erosion
    total_image[:, 2*width:3*width] = dilation
    total_image[:, 3*width:4*width] = tophat
    total_image[:, 4*width:5*width] = blackhat
    total_image[:, 5*width:6*width] = finalImg

    
    (flag, encodedImage) = cv2.imencode(".jpg", total_image)

    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


def show_images_mask3():
    img = cv2.imread('./img/img3.jpeg')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = imgGray.shape

    kernel = np.ones((39,39),np.uint8)
    elemento = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    erosion = cv2.erode(imgGray,elemento,iterations = 1)
    dilation = cv2.dilate(imgGray,elemento,iterations = 1)
    tophat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, kernel)
    blackhat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, kernel)

    restaImgs = cv2.subtract(tophat, blackhat)
    finalImg = cv2.add(restaImgs, imgGray)

    total_image = np.zeros((height, width * 6), dtype=np.uint8)
    total_image[:, :width] = imgGray
    total_image[:, width:2*width] = erosion
    total_image[:, 2*width:3*width] = dilation
    total_image[:, 3*width:4*width] = tophat
    total_image[:, 4*width:5*width] = blackhat
    total_image[:, 5*width:6*width] = finalImg

    
    (flag, encodedImage) = cv2.imencode(".jpg", total_image)

    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')




@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/imagenes1")
def imagenes1():
    return Response(show_images_mask1(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/imagenes2")
def imagenes2():
    return Response(show_images_mask2(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/imagenes3")
def imagenes3():
    return Response(show_images_mask3(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(debug=False)