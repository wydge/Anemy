
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from flask import Flask, render_template, Response, request
width = 640 #larghezza standard raspberry
height = 480 # altezza standard raspberry
cam = cv2.VideoCapture(0)
app = Flask(__name__)

@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')
def gen_frames():


    while True:
        dim = (width, height)
        success, frame = cam.read()  # read the camera frame
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        cv2.rectangle(frame, (440, 140), (200, 340), (0, 255, 0), 4)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)


            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def bozza_test_camera():

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
            print("{} written!".format(img_name))
            cattura = cv2.imread(img_name)
            img_processing_image(cattura,1)#metto 1 solo perchè è un testing, poi non servirà più

            # break  mettendo questo ti scatta solo una foto e poi ti chiude la finestra direttamente, l'ho tolto cosi è possibile fare più scatti
    cam.release()
    cv2.destroyAllWindows()
def img_processing_image(img2, i):
    risultato = str(i)
    if(i == 10):
        risultato = " testing"
    lab_image = cv2.cvtColor(img2, cv2.COLOR_RGB2LAB)
    l_channel,a_channel,b_channel = cv2.split(lab_image) #Divisione di ogni riga di pixel nei 3 valore del LAB
    #print("LUCE")
    #print(l_channel)
    rows = len(a_channel) #righe pixel valutate in cromatura a
    columns = len(a_channel[0]) #colonne pixel valutate in cromatura a
    n_pixel = rows * columns  # numero totale pixel
    i=0

    a_filtrate=np.empty((n_pixel))
    for x in range(0,rows):
       for y in range(0,columns):
           if a_channel[x][y] != 42 :#42 è il colore verde sulla cromatura a* di opencv( in realta dovrebbe essere -128)
               if a_channel[x][y] < 128 or a_channel[x][y] > 148 :
                a_filtrate[i] = a_channel[x][y]
                i= i + 1


    a_palpebra=a_filtrate[0:i]#matrice della palpebra
    a_star= np.average(a_palpebra)
    a_star=a_star-128 # Valore medio di a su vettore filtrato sulla palpebra
    #print(a_star)

    a = np.average(a_channel)  # valore medio di a, che dovrebbe (credo) essere il valore che ci serve
    a = a - 128  # valore preciso di a*


    cv2.imshow("Result"+risultato, img2)
def CutPhoto(img):#ritaglia il suddetto riquadro verde dell'immagine
    im = Image.open(img)
    im1 = im.crop((204, 144, 435, 335))  # left,top,right,bottom
    im1.save(img)
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
    img_name = "analysis_of_{}.jpg".format(mese_orario)

    cv2.imwrite(img_name, frame)
    CutPhoto(img_name)
    print("{} written!".format(img_name))
    return Response(status = 200)
@app.route('/AnalisiFoto', methods = ['POST'])
def AnalisiFoto():
    return Response("Ciao")
#img2 = cv2.imread('prova1.jpg')
#img_processing_image(img2,10)
#bozza_test_camera()
if __name__ == "__main__": #per inizializzare il server locale
    app.run(debug=True)