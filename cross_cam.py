import cv2
import os
import time
filename = "imgExy.png"

def take_img():
    # Eğer dosya varsa sil
    if os.path.exists(filename):
        os.remove(filename)

    # Kamerayı aç
    cap = cv2.VideoCapture(0)  # 0 genellikle varsayılan kamera

    if not cap.isOpened():
        print("Kamera açılamadı!")
        exit()

    # Kameradan bir kare oku
    ret, frame = cap.read()
    time.sleep(1)

    if ret:
        # Fotoğrafı kaydet
        cv2.imwrite(filename, frame)
        #cv2.imread(filename)
        print(f"Fotoğraf {filename} olarak kaydedildi.")
    else:
        print("Fotoğraf çekilemedi!")

    # Kamerayı serbest bırak
    cap.release()

if __name__ == "__main__":
    take_img()