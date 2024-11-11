
# Author: vlarobbyk
# Version: 1.0
# Date: 2024-10-20
# Description: A simple example to process video captured by the ESP32-XIAO-S3 or ESP32-CAM-MB in Flask.


from flask import Flask, render_template, Response, stream_with_context, Request, request, jsonify
from io import BytesIO

import cv2
import numpy as np
import requests
import time

app = Flask(__name__)
# IP Address
#_URL = 'http://192.168.18.182'
# Default Streaming Port
#_PORT = '81'
# Default streaming route
#_ST = '/stream'
#SEP = ':'

stream_url = "http://192.168.18.182:81/stream"


limite = 40
gamma = 1.5

sal = 0.0
pimienta = 0.0


background = None


def update_background(current_frame, prev_bg, alpha):
    bg = alpha * current_frame + (1 - alpha) * prev_bg
    bg = np.uint8(bg)  
    return bg

def deteccionMovimiento():
    t=0
    
    prev_time = time.time() 

    res = requests.get(stream_url, stream=True)
    
    for chunk in res.iter_content(chunk_size=100000):
        
        if len(chunk) > 100:

            try:
                img_data = BytesIO(chunk)
                
                cv_img = cv2.imdecode(np.frombuffer(img_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)

                if cv_img is None:
                    print("Error al decodificar la imagen.")
                    continue

                #***************** OPENCV *****************

                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                gray = cv2.resize(gray, None, fx=0.7, fy=0.7)

                if t == 0:
                    background = gray
                    t=1
                else:
                    diff = cv2.absdiff(background, gray)
                    ret, motion_mask = cv2.threshold(diff, 60, 255, cv2.THRESH_BINARY)
                    background = update_background(gray, background, alpha = 0.1)

                height, width = gray.shape
                
                # Calcular los FPS
                curr_time = time.time()  # Obtenemos el tiempo actual
                fps = 1 / (curr_time - prev_time)  # FPS = 1 / (tiempo por frame)
                prev_time = curr_time  # Actualizamos el tiempo previo

                fps_text = f"FPS: {int(fps)}"


                total_image = np.zeros((height, width * 2), dtype=np.uint8)
                total_image[:, :width] = gray
                total_image[:, width:] = motion_mask

                cv2.putText(total_image, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                (flag, encodedImage) = cv2.imencode(".jpg", total_image)
                if not flag:
                    continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')

            except Exception as e:
                print(e)
                continue

def problemasIluminacion():
    
    res = requests.get(stream_url, stream=True)

    inv_gamma = 1.0 / gamma
    tabla = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)], dtype='uint8')
    
    for chunk in res.iter_content(chunk_size=100000):
        
        # Asegurarnos de que el fin está después del inicio
        if len(chunk) > 100:

            try:
                img_data = BytesIO(chunk)
                
                cv_img = cv2.imdecode(np.frombuffer(img_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)

                if cv_img is None:
                    print("Error al decodificar la imagen.")
                    continue

                #***************** OPENCV *****************

                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                gray = cv2.resize(gray, None, fx=0.7, fy=0.7)

                videoEcualizado = cv2.equalizeHist(gray)
                
                clahe = cv2.createCLAHE(clipLimit=limite, tileGridSize=(8,8))
                videoClahe = clahe.apply(gray)

                videoGamma = cv2.LUT(gray, tabla)

                height, width = gray.shape
                
                total_image = np.zeros((height, width * 4), dtype=np.uint8)
                total_image[:, :width] = gray
                total_image[:, width:width * 2] = videoEcualizado
                total_image[:, width * 2:width * 3] = videoClahe
                total_image[:, width * 3:] = videoGamma 
                #total_image[:, width:] = videoClahe

                (flag, encodedImage) = cv2.imencode(".jpg", total_image)
                if not flag:
                    continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')

            except Exception as e:
                print(e)
                continue

def generarSalPimienta():
    global sal, pimienta

    sal = request.form.get('trackbarSal', type=int) / 100.0
    pimienta = request.form.get('trackbarPimienta', type=int) / 100.0

def salPimienta():
    
    global sal, pimienta

    res = requests.get(stream_url, stream=True)

    for chunk in res.iter_content(chunk_size=100000):

        if len(chunk) > 100:

            try:
                img_data = BytesIO(chunk)
                
                cv_img = cv2.imdecode(np.frombuffer(img_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)

                if cv_img is None:
                    print("Error al decodificar la imagen.")
                    continue

                #***************** OPENCV *****************
            
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                gray = cv2.resize(gray, None, fx=0.7, fy=0.7)

                height, width = gray.shape

                noise_image = np.copy(gray)

                # Generamos el ruido de sal
                num_salt = np.ceil(sal * height * width).astype(int)
                num_pepper = np.ceil(pimienta * height * width).astype(int)
                
                coords = [np.random.randint(0, i - 1, num_salt) for i in gray.shape]
                noise_image[coords[0], coords[1]] = 255

                coords = [np.random.randint(0, i - 1, num_pepper) for i in gray.shape]
                noise_image[coords[0], coords[1]] = 0

                imgFiltros = filtrosSalPimienta(noise_image)


                total_image = np.zeros((height, width * 5), dtype=np.uint8)

                total_image[:, :width] = gray
                total_image[:, width:width*2] = noise_image
                total_image[:, width*2:width*3] = imgFiltros[0]
                total_image[:, width*3:width*4] = imgFiltros[1]
                total_image[:, width*4:] = imgFiltros[2]
                

                (flag, encodedImage) = cv2.imencode(".jpg", total_image)
                if not flag:
                    continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
                
            except Exception as e:
                print(e)
                continue

def filtrosSalPimienta(imgSalPimienta):

    mediana = cv2.medianBlur(imgSalPimienta, 5)
    imagen_blur = cv2.blur(imgSalPimienta, (5, 5))
    imagen_gaussian_blur = cv2.GaussianBlur(imgSalPimienta, (5, 5), 0)

    return [mediana, imagen_blur, imagen_gaussian_blur]    

def deteccionBordes():
    res = requests.get(stream_url, stream=True)

    inv_gamma = 1.0 / gamma
    tabla = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)], dtype='uint8')

    for chunk in res.iter_content(chunk_size=100000):
            
        if len(chunk) > 100:

            try:
                img_data = BytesIO(chunk)
                
                cv_img = cv2.imdecode(np.frombuffer(img_data.getvalue(), np.uint8), cv2.IMREAD_COLOR)

                if cv_img is None:
                    print("Error al decodificar la imagen.")
                    continue

                #***************** OPENCV *****************

                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                gray = cv2.resize(gray, None, fx=0.7, fy=0.7)


                videoGamma = cv2.LUT(gray, tabla)
                
                gray = videoGamma

                height, width = gray.shape
                
                imagen_gaussian_blur = cv2.GaussianBlur(gray, (5, 5), 0)
                imgGx = cv2.Sobel(imagen_gaussian_blur, cv2.CV_16S, 1, 0, ksize=3)
                imgGy = cv2.Sobel(imagen_gaussian_blur, cv2.CV_16S, 0, 1, ksize=3)

                imgGxAbs = cv2.convertScaleAbs(imgGx)
                imgGyAbs = cv2.convertScaleAbs(imgGy)
                grad = cv2.addWeighted(imgGxAbs, 0.5, imgGyAbs, 0.5, 0)
                canny = cv2.Canny(imagen_gaussian_blur, 100, 100*1.3, 3)


                imgGxSinSuavisado = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
                imgGySinSuavisado = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)

                imgGxAbsSinSuavisado = cv2.convertScaleAbs(imgGxSinSuavisado)
                imgGyAbsSinSuavisado = cv2.convertScaleAbs(imgGySinSuavisado)
                gradSinSuavisado = cv2.addWeighted(imgGxAbsSinSuavisado, 0.5, imgGyAbsSinSuavisado, 0.5, 0)
                cannySinSuavisado = cv2.Canny(gray, 100, 100*1.3, 3)


                total_image = np.zeros((height * 2, width * 4), dtype=np.uint8)

                total_image[:height, :width] = gray
                total_image[:height, width:width * 2] = imagen_gaussian_blur
                total_image[:height, width * 2:width * 3] = grad
                total_image[:height, width * 3:] = canny

                total_image[height:, :width] = gray
                total_image[height:, width:width * 2] = gradSinSuavisado
                total_image[height:, width * 2:width * 3] = cannySinSuavisado

                #total_image[:, width:] = videoClahe

                (flag, encodedImage) = cv2.imencode(".jpg", total_image)
                if not flag:
                    continue

                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')

            except Exception as e:
                print(e)
                continue




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/problemas_iluminacion")
def problemas_iluminacion():
    return Response(problemasIluminacion(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/deteccion_movimiento")
def deteccion_movimiento():
    return Response(deteccionMovimiento(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/sal_pimienta", methods=['GET'])
def sal_pimienta():
    return Response(salPimienta(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/get_sal_pimienta', methods=['POST'])
def get_sal_pimienta():
    return Response(generarSalPimienta(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/deteccion_bordes')
def deteccion_bordes():
    return Response(deteccionBordes(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(debug=False)

