
import cv2
import numpy as np
from PIL import Image
def bozza_test_camera():
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")

    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Impossibile catturare l'immagine")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC per uscire
            print("Chiusura schermata")
            break
        elif k == ord(' '):
            # SPACE per scattare la foto
            img_name = "foto_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)

            print("{} written!".format(img_name))
            cattura = cv2.imread(img_name)
            img_processing_image(cattura,img_counter)
            img_counter += 1
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
           if a_channel[x][y] != 42 :
               if a_channel[x][y] < 128 or a_channel[x][y] > 148:
                a_filtrate[i] = a_channel[x][y]
                i   = i + 1


    a_palpebra=a_filtrate[0:i]#matrice della palpebra
    a_star= np.average(a_palpebra)
    a_star=(a_star-128)*2

    print("VETTORE FILTRATO")
    print(a_star)
    print("N ELEMENTI FILTRATI")
    print(i)
    print("NUMERO PIXEL VALUTATI")
    print(n_pixel)
    print("A CROMATURA")
    print (a_channel)
   # print("B CROMATURA")
   # print( b_channel)
   # b=np.average(b_channel)
   # print(b)
    a = np.average(a_channel)#valore medio di a, che dovrebbe (credo) essere il valore che ci serve
    a = a - 128 #valore preciso di a*
    print(a)
    cv2.imshow("Result"+risultato, img2)

img2 = cv2.imread('result.png')
img_processing_image(img2,10)
bozza_test_camera()

"""""
img = Image.open('108.JPG')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
   if item[0] == 255 and item[1] == 255 and item[2] == 255:
       newData.append((255, 255, 255, 0))
   else:
     newData.append(item)

img.putdata(newData)
img.save("img3.png", "PNG")


# Load the image and make into Numpy array
rgba = np.array(Image.open('img3.png'))

# Make image transparent white anywhere it is transparent
rgba[rgba[...,-1]==0] = [0,255,0,255]

# Make back into PIL Image and save
Image.fromarray(rgba).save('result.png')
"""""