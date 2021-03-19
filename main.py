import cv2
import numpy as np
cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0
result = 0


img1= cv2.imread('Cattura.JPG')
lab_image = cv2.cvtColor(img1, cv2.COLOR_RGB2LAB)
l_channel,a_channel,b_channel = cv2.split(lab_image) #Divisione di ogni riga di pixel nei 3 valore del LAB
print(l_channel)
print (a_channel)


print( b_channel)
a = np.average(a_channel)#valore medio di a, che dovrebbe (credo) essere il valore che ci serve
print(a)
cv2.imshow("Result", img1)
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

        img_counter += 1
        # break  mettendo questo ti scatta solo una foto e poi ti chiude la finestra direttamente, l'ho tolto cosi è possibile fare più scatti
cam.release()

cv2.destroyAllWindows()
