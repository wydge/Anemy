import sys
import os
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
import cv2
from datetime import datetime
import numpy as np
from PIL import Image
from skimage.measure import regionprops


camera_Width  = 640 # 480 # 640 # 1024 # 1280
camera_Heigth = 480 # 320 # 480 # 780  # 960
frameSize = (camera_Width, camera_Heigth)
video_capture = cv2.VideoCapture(0)


def img_processing(img2): #Metodo di processing dell'immagine che da come valore di ritorno il valore medio a* dell'immagine passata


    lab_image = cv2.cvtColor(img2, cv2.COLOR_RGB2LAB)
    l_channel,a_channel,b_channel = cv2.split(lab_image) #Divisione di ogni riga di pixel nei 3 valore del LAB
    rows = len(a_channel) #righe pixel valutate in cromatura a
    columns = len(a_channel[0]) #colonne pixel valutate in cromatura a
    n_pixel = rows * columns  # numero totale pixel
    i=0

    a_filtrate=np.empty((n_pixel))
    for x in range(0,rows):
       for y in range(0,columns):

               if a_channel[x][y] < 124 or a_channel[x][y] > 132 and  l_channel[x][y] > 5  : #filtro la a* sui valori che indicano una tonalità di pelle, bianco e tonalità di nero
                a_filtrate[i] = a_channel[x][y]
                i= i + 1


    a_palpebra=a_filtrate[0:i]#matrice della palpebra
    a_star= np.average(a_palpebra)
    a_star=(a_star-128) # Valore medio di a su vettore filtrato sulla palpebra

    return a_star

def CutPhoto(src):#ritaglia la parte inferiore del riquadro verde dello stream


    im = Image.open(src)
    #im1 = im.crop((204, 144, 435, 335))  # left,top,right,bottom
    im1 = im.crop((260, 178, 381, 299))
    im1.save(src)





def AnalysisWindow(src):#sorgente immagine da analizzare
    img1 = cv2.imread(src)
    slic = cv2.ximgproc.createSuperpixelSLIC(img1, region_size=40, ruler=70.0)
    slic.iterate(10)  # Number of iterations, the greater the better
    mask_slic = slic.getLabelContourMask()  # Get Mask, Super pixel edge Mask==1

    label_slic = slic.getLabels()  # height x width matrix. Each component indicates the superpixel index of the corresponding pixel position

    number_slic = slic.getNumberOfSuperpixels()  # Get the number of super pixels

    mask_inv_slic = cv2.bitwise_not(mask_slic)
    img = cv2.bitwise_and(img1, img1, mask=mask_inv_slic)  # Draw the superpixel boundary on the original image
    img_superpixel= "SUPERPIXEL_"+src
    cv2.imwrite(img_superpixel, img)

    sg.ChangeLookAndFeel('Reddit')

    # define the window layout
    layout1 = [[sg.Image(filename='icona-web-analysis.png',pad=((260,260),3))],
               [sg.Graph((650, 490), (0, 480), (640, 0), key='-GRAPH-',
                         change_submits=True, drag_submits=False)],
               [sg.Text('', key="anemia", size=(40, 1), justification='center', font='Helvetica 20')],
               [sg.ReadButton('Exit', size=(10, 1), pad=((200, 0), 3), font='Helvetica 14',button_color="Red"),
                sg.RButton('Analyze', size=(10, 1), font='Any 14',button_color="Red"),
                ]]
    window1 = sg.Window("Analysis", layout1,location=(400, 200),finalize=True)

    #window.Layout(layout1).Finalize()
    g = window1['-GRAPH-']
    cx=0
    cy=0
    a_star_totale = 0
    tot_superpixel = 0
    superpixels_selezionati = []
    a_star_superpixel_selezionati = []
    g.draw_image(img_superpixel, "", (0, 0))
    sg.Popup("Selezionare manualmente le porzioni di pixel che identificano la palpebra,\nCERCHIO BLU : regione selezionata, \nCERCHIO GIALLO: regione deselezionata ", keep_on_top=True,
        text_color="Red", font="Sans-Serif")
    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    while True:


        event, values = window1.read()
        mouse = values['-GRAPH-']
        if event == '-GRAPH-':
            if mouse == (None, None):
                continue
            box_x = mouse[0]
            box_y = mouse[1]
            letter_location = (box_x, box_y)
            print("coordinate")
            print(box_x, box_y)
            matrice_pixel = label_slic[box_y]
            result = np.array(matrice_pixel).flatten()
            superpixel_selected = matrice_pixel[box_x]
            f=-1


            if  superpixel_selected in superpixels_selezionati:
                f=superpixels_selezionati.index(superpixel_selected)
                superpixels_selezionati.remove(superpixel_selected)
            if(f!=-1):
                a_star_deleted= a_star_superpixel_selezionati[f]
                a_star_superpixel_selezionati.remove(a_star_deleted)
                a_star_totale=a_star_totale-a_star_deleted
                regions = regionprops(label_slic,
                                      intensity_image=img[..., 1])
                x = 0

                for props in regions:  # for per gestire ogni regione, e andare alla regione cercata

                    if (x == superpixel_selected - 1):
                        cxi, cyi = props.centroid  # centroid coordinates
                        cx = int(cxi)
                        cy = int(cyi)
                        v = props.label  # value of label
                        print("COORDINATEE")
                        print(cx)
                        print(cy)
                        print(v)

                    x = x + 1

                g.draw_circle((cy-8, cx-5), 7, fill_color='yellow', line_color='white')
                print("Centroide")
                print(cx)
            else:
                superpixels_selezionati.append(superpixel_selected)
                print("Superpixel selezionato")
                print(superpixel_selected)

                # for nel quale viene tagliata la regione scelta e salvata in 'output.png'
                for i, segVal in enumerate(np.unique(label_slic)):

                    mask1 = np.zeros(img.shape[:2], dtype="uint8")

                    if (segVal == superpixel_selected):  # valore del superpixel scelto
                        mask1[label_slic == segVal] = 255

                        cv2.imwrite('output.png', cv2.bitwise_and(img1, img1, mask=mask1))
                        image_superpixel = cv2.imread("output.png")
                        media_a = img_processing(image_superpixel)
                        a_star_superpixel_selezionati.append(media_a)
                        a_star_totale = a_star_totale + media_a

                        tot_superpixel = tot_superpixel + 1


                    # cv2.imshow("Applied", cv2.bitwise_and(img1, img1, mask=mask1))
                    # cv2.waitKey(1)


                regions = regionprops(label_slic,
                                      intensity_image=img[..., 1])
                x = 0

                for props in regions:  # for per gestire ogni regione, e andare alla regione cercata

                    if (x == superpixel_selected - 1):
                        cxi, cyi = props.centroid  # centroid coordinates
                        cx = int(cxi)
                        cy = int(cyi)
                        v = props.label  # value of label
                        print("COORDINATEE")
                        print(cx)
                        print(cy)
                        print(v)

                    x = x + 1
                g.draw_circle((cy-8, cx-5), 7, fill_color='blue', line_color='white')
                print("Centroide")
                print(cx)
        if event == 'Exit':
            sys.exit(0)

        elif event == 'Analyze':
            if(tot_superpixel==0):
                a_star_media=0
            else:
                a_star_media = a_star_totale / tot_superpixel

            a_star_media= float("{:.3f}".format(a_star_media))
            if(a_star_media < 20):
                risultato = str(a_star_media) + "  Paziente anemico"
                window1.FindElement("anemia").Update(value=risultato)
                window1.FindElement("anemia").Update(text_color='Red')
            elif(a_star_media<30):
                risultato= str(a_star_media)+ "  Paziente nella norma"
                window1.FindElement("anemia").Update(value=risultato)
                window1.FindElement("anemia").Update(text_color='Orange')
            else:
                risultato=str(a_star_media)+ "  Paziente in ottimo stato"
                window1.FindElement("anemia").Update(value=risultato)
                window1.FindElement("anemia").Update(text_color='Green')




def main():
    file_types = [("PNG (*.png", "*.png")]

    sg.ChangeLookAndFeel('Reddit')


    # define the window layout
    layout = [[sg.Image(filename='icona-web.png',pad=((260,260),3))],
              [sg.Image(filename='', key='image')],
              [sg.Input(size=(22, 1), key="-FILE-", background_color="White", border_width=3,font='Helvetica 14'),
              sg.FileBrowse(file_types=file_types, size=(10, 1), font='Helvetica 14',button_color="Red"),
              sg.Button("Load Image", size=(10, 1), font='Helvetica 14',button_color="Red")],
              [sg.RButton('Scatta', size=(10, 2), pad=((265, 265), 3), font='Any 14', button_color="Red")],
              [sg.ReadButton('Exit', size=(10, 1),  font='Helvetica 14',button_color="Red")]]


    # creazione finestra  GUI
    window = sg.Window('Anemy',
                       location=(400, 200))
    window.Layout(layout).Finalize()
    sg.Popup("Scattare una foto assicurandosi di mettere a fuoco l'immagine ! "
             "\nAssicurarsi di tenere ben visibile la palpebra!", keep_on_top=True, text_color="Red",font="Sans-Serif")


    while True: #In attesa di click di un bottone

            ret, frameOrig = video_capture.read()
            frame = cv2.resize(frameOrig, frameSize)
            #cv2.circle(frame, (320, 240), 70, (0, 255, 0), 2)
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            window["image"].update(data=imgbytes)
            button, values = window.read(timeout=20)

            if button == 'Exit' or values is None:
                sys.exit(0)
            elif button == 'Scatta':
                now = datetime.now()
                date = now.strftime("%Y-%m-%d_at")

                time = now.strftime("_%H.%M.%S")  # rinomino la foto in base alla data di oggi e all'orario
                mese_orario = date + time
                img_name = 'analysis_of_{}.png'.format(mese_orario)
                cv2.imwrite(img_name, frame)
                video_capture.release()
                #CutPhoto(img_name)
                window.close()
                AnalysisWindow(img_name)
            elif button == "Load Image":
                filename = values["-FILE-"]



                if os.path.exists(filename):
                    image = cv2.imread(values["-FILE-"])

                    path = os.path.basename(filename)
                    cv2.imwrite(path, image)
                    print(path)
                    window.close()
                    AnalysisWindow(path)







main()
