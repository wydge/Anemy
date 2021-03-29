
import cv2
import numpy as np
from PIL import Image, ImageDraw
from datetime import datetime
from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, jsonify

import os
width = 640 #larghezza standard raspberry
height = 480 # altezza standard raspberry
cam = cv2.VideoCapture(0)
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/'


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 1
}
@app.route('/')
def index():
    # rendering webpage

    return render_template('index.html')


def gen_frames():


    while True:
        dim = (width, height)
        success, frame = cam.read()  # read the camera frame
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        #cv2.rectangle(frame, (440, 140), (200, 340), (0, 255, 0), 4)
        cv2.circle(frame, (320, 240), 70, (0, 255, 0), 2)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.png', frame)


            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def bozza_test_camera(): #NON LO USO PIU

    #cv2.namedWindow("test")
    while True:
        ret, frame = cam.read()
        dim = (width,height)
        frame = cv2.resize(frame,dim,interpolation=cv2.INTER_AREA)
        #frame = cv2.copyMakeBorder(frame, 5, 5, 5, 5, cv2.BORDER_ISOLATED, value=[0, 200, 200])
        #cv2.rectangle(frame,(640,140),(0,340),(0,255,0),4)   #600 indica l'altezza destra del rettangolo 200 la base al basso del rettangolo e gli altri due i restanti
        cv2.rectangle(frame, (440, 140), (200, 340), (0, 255, 0), 4)
        if not ret:
            print("Impossibile catturare l'immagine")
            break
        #cv2.imshow("test", frame)


        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC per uscire
            print("Chiusura schermata")
            break
        elif k == ord(' '):
            # SPACE per scattare la foto
            now = datetime.now()
            date = now.strftime("%Y-%m-%d_at")

            time = now.strftime("_%H.%M.%S")#rinomino la foto in base alla data di oggi e all'orario
            mese_orario= date + time
            img_name = "analysis_of_{}.jpg".format(mese_orario)

            cv2.imwrite(img_name, frame)
            CutPhoto(img_name)

            #print("{} written!".format(img_name))
            cattura = cv2.imread("result.png")
            img_processing_image(cattura,1)#metto 1 solo perchè è un testing, poi non servirà più

            # break  mettendo questo ti scatta solo una foto e poi ti chiude la finestra direttamente, l'ho tolto cosi è possibile fare più scatti
    cam.release()
    cv2.destroyAllWindows()
def img_processing_image(img2, i):
    risultato = str(i)
    if (i == 10):
        risultato = " testing"
    lab_image = cv2.cvtColor(img2, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_image)  # Divisione di ogni riga di pixel nei 3 valore del LAB

    rows = len(a_channel)  # righe pixel valutate in cromatura a
    columns = len(a_channel[0])  # colonne pixel valutate in cromatura a
    n_pixel = rows * columns  # numero totale pixel
    i = 0

    a_filtrate = np.empty((n_pixel))
    for x in range(0, rows):
        for y in range(0, columns):

            if a_channel[x][y] < 124 or a_channel[x][y] > 132 and l_channel[x][
                y] > 5:  # filtro la a* sui valori che indicano una tonalità di pelle, bianco e tonalità di nero
                a_filtrate[i] = a_channel[x][y]
                i = i + 1

    a_palpebra = a_filtrate[0:i]  # matrice della palpebra
    a_star = np.average(a_palpebra)
    a_star = (a_star - 128)  # Valore medio di a su vettore filtrato sulla palpebra
    print(a_star)
    return a_star




def CutPhoto(src):#ritaglia il suddetto riquadro verde dell'immagine
    im = Image.open(src)
    # im1 = im.crop((204, 144, 435, 335))  # left,top,right,bottom
    im1 = im.crop((260, 178, 381, 299))
    im1.save(src)
    img = Image.open(src)

    height, width = img.size
    lum_img = Image.new('L', [height, width], 0)

    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0, 0), (height, width)], 0, 180,
                  fill=255, outline="white")  # esso permette il ritaglio circolare/semicircolare
    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)

    final_img_arr = np.dstack(
        (img_arr, lum_img_arr))  # immagine che unisce l'immagine circolare facendo una specie di matching
    a = Image.fromarray(final_img_arr)
    a.save(src)
    folder = "static/img/"
    folder_image = folder + "result.png"
    print(folder_image)
    a.save(folder_image)
    rgba = np.array(Image.open(src))

    # Make image transparent white anywhere it is transparent
    rgba[rgba[..., -1] == 0] = [255, 255, 255,
                                255]  # inserisco lo sfondo bianco e elimino la trasparenza per il calcolo del lab

    # Make back into PIL Image and save
    Image.fromarray(rgba).save('result.png')

    img_palpebra = cv2.imread("result.png")

@app.route('/video_feed') #per il response con la pagina html
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/takeimage', methods = ['POST'])
def takeimage():
    name = request.form['name']
    print(name)
    _, frame = cam.read()
    now = datetime.now()
    date = now.strftime("%Y-%m-%d_at")

    time = now.strftime("_%H.%M.%S")  # rinomino la foto in base alla data di oggi e all'orario
    mese_orario = date + time
    img_name = "analysis_of_{}.png".format(mese_orario)

    cv2.imwrite(img_name, frame)
    CutPhoto(img_name)
    risultato= cv2.imread('result.png')
    a = img_processing_image(risultato, 10)
    data= {'value':a} #data è un oggeto formato dal campo value per valutarlo su html a.value
    #print(a)
    print("{} written!".format(img_name))

    #< img src = "{{url_for('static',filename='{{ lmurt }}') }}" >

    #return url_for('Vdimseriesco', a=a)

    return jsonify( data) #jsonify metodo flask per far "tornare" valore ad una pagina html


#img2 = cv2.imread('prova1.jpg')
#img_processing_image(img2,10)
#bozza_test_camera()



if __name__ == "__main__": #per inizializzare il server locale
    app.run(debug=True)