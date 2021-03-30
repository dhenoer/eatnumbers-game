# EatNumbers - Game


![EatNumbers ScreenShoot](https://github.com/dhenoer/main/blob/img/eatnumbers-game.png)

Game ini merupakan permainan yang sangat sederhana. Pemain ditugaskan untuk memakan angka-angka yang bertebaran di layar dengan cara membuka mulut. Makanlah beberapa angka agar jumlah sesuai dengan target.    

## Cara main

1. Tekan tombol [Start]
2. Tersenyumlah agar dapat memulai
3. Jika pemain tersenyum, program akan menyebarkan angka-angka d layar
dan memasang target.
4. Pemain harus membuka mulut dan mengarahkan ke angka-angka yang dipilih satu persatu. Untuk memenagkan permainan, jumlah angka yang dimakan harus sesuai target yang ditetapkan. 
5. Tekan [Start] jika ingin memulai lagi
6. Tekan tombol [Quit] jika ingin berhenti

## Video

![Video di Youtube](https://www.youtube.com/watch?v=wYZDW0o26jA)

## Algoritma

Game dibuat dengan bahasa pemrograman Python3 berbasis GUI dengan TkInter dan menerapkan modul-modul OpenCV, Face_Detector untuk mendapatkan landmark dan fitur-fitur pada wajah pemain, sehingga dapat dianalisa apakah ybs sedang tersenyum atau sedang membuka mulut lebar-lebar.

Bagi saya, program ini media pembelajaran untuk memahami OpenCV dan melatih kemampuan algoritma pemrograman.

Berikut adalah modul-modul yang diimport oleh program:
    
    import tkinter as tk
    import cv2
    import numpy as np
    import math
    import PIL.Image, PIL.ImageTk
    import time
    import datetime as dt
    import argparse
    import face_recognition
    import threading
    import random
    

Silakan download /pull untuk dipelajari atau dikembangkan
