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

# eat numbers scattered around you
# win if sum of of selected numbers equal to target specified

MAXTARGETVALUE = 20 # maximum value of target
MAXMAINELEMENT = 10 # maximum number of main elements to scattered
MAXSALTELEMENT = 5  # maximum number of salt elements to scattered 

MAXTOLERANCELIPSTONUMBER = 200  # maximum distance of lips to number selected
MINSMILEDEGREE = 170 # minimum/maximum degree of angle of smile 
MINMOUTHOPENRATIO = 0.25 # minimum ratio of vertical/horizontal distance of lips

class Game:
    '''Game class to prepare game initial and control the role

    numbers:list -- random generated numbers to choose
    positions:list -- random coordinate position for numbers
    target:integer -- random target to achieve
    choices:list -- selected number has been eaten
    level:string -- game phase
    stamp_win:image array -- lips-red.png for winning stamp
    stamp_lose:image array -- foot-stamp.png for lose stamp
    '''

    def __init__(self):
        ''' init stamp '''
        self.stamp_win = PIL.Image.open('img/lips-red.resized.png')
        self.stamp_lose = PIL.Image.open('img/foot-stamp-resized.png')
        self.level = ''


    def start(self):
        ''' start game '''
        self.level = 'smile'


    def shuffle(self, w, h, maks=MAXTARGETVALUE):
        ''' shuffle game variables '''
        while True:
            # prepare generate main random numbers 
            self.numbers = []
            self.choices = []

            # set number of main elements
            nelement = random.randint(2, MAXMAINELEMENT)
            for _ in range(nelement):
                self.numbers.append(random.randint(1, 10))

            # target
            self.target = sum(self.numbers)
            if self.target <= maks:
                break

        # add salt elements
        saltelement = random.randint(1, MAXSALTELEMENT)
        for _ in range(saltelement):
            self.numbers.append(random.randint(0,10))

        # generate random position coordinate for all numbers element
        self.positions = []
        for _ in range(len(self.numbers)):
            #set position
            x = random.randint(100, w-100)
            y = random.randint(150, h-30)
            self.positions.append((x, y))


    def play_head_winlose(self, frame):
        '''show heading of win/lose'''

        if self.level not in ['win', 'lose']:
            return frame

        winlosecolor = (0,0,255) if self.level=='win' else (255,0,0)
        if random.randint(0,2):
            cv2.rectangle(frame, (0,0), (len(frame[0]), 40), winlosecolor, -1)
        else:
            cv2.rectangle(frame, (0,0), (len(frame[0]), 40), (0,0,0), -1)

        cv2.putText(frame, 
            'You {}'.format('win' if self.level=='win' else 'lose') +
            ' by collecting {} of {}'.format(sum(self.choices), self.target), 
            (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        return frame


    def play_winlose(self, image, center_lip):
        '''play win or lose'''

        if self.level not in ['win', 'lose']:
            return image

        #stamp.thumbnail((300,300), PIL.Image.ANTIALIAS)
        #stamp.resize((200,200), PIL.Image.ANTIALIAS)
        # paste stamp to image randomly
        if center_lip != (0,0) and random.randint(0,2):
            if self.level == 'win':
                stamp = self.stamp_win
            else:
                stamp = self.stamp_lose

            topleftpos = (center_lip[0] - stamp.width//2, 
                center_lip[1] - stamp.height//2)
            image.paste(stamp, topleftpos, stamp)

        return image


    def play_smile(self, frame, is_smile):
        '''play and check smile phase'''
        if self.level != 'smile':
            return None

        cv2.rectangle(frame, (0,0), (len(frame[0]), 40), (0,0,0), -1)
        cv2.putText(frame, 'Smile please, to start the game', 
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        if is_smile:
            self.level = 'eat'


    def play_eat(self, center_lip, is_mouth_open):
        '''play and check if numbers has been eaten'''

        if self.level != 'eat':
            return None

        if len(self.numbers) and is_mouth_open:
            # calculate all distance from lips center
            dist = np.sum((np.array(self.positions)-np.array(center_lip))**2, axis=1)
            mindist = min(dist)

            #print('mindistance', mindist)
            if mindist < MAXTOLERANCELIPSTONUMBER:
                idxmin = np.argmin(dist)
                # numbers eaten and drop from numbers and locations
                self.choices.append(self.numbers[idxmin])
                self.numbers.pop(idxmin)
                self.positions.pop(idxmin)

        # check sum archieved
        sumc = sum(self.choices)
        if sumc == self.target:
            # next level is win
            self.level = 'win'
            #print('Menang... Selamat')

        elif sumc > self.target:
            # next level is lose
            self.level = 'lose'
            #print('Kalah..')


    def scatter(self, frame):
        '''display current game map'''

        if self.level != 'eat':
            return frame

        # display instructions and target
        cv2.rectangle(frame, (0,0), (len(frame[0]), 40), (0,0,0), -1)
        cv2.putText(frame, 'Eat numbers by your mouth, target is {}'.format(self.target), 
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        # display choices / numbers has been eaten
        if len(self.choices):
            bottom = len(frame)-5
            cv2.rectangle(frame, (0,bottom-15), (300, bottom), (0,0,0), -1)
            p = (20, bottom)
            t = ', '.join([ str(d) for d in self.choices ])
            cv2.putText(frame, t, p, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                (255,255,0), 2)

        # scatter available choices / numbers
        for i in range(len(self.numbers)):
            p = self.positions[i]
            t = str(self.numbers[i])
            cv2.circle(frame, p, 20, (0,0,150), -1)
            cv2.putText(frame, t, p, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                (255,255,0), 2)

        return frame


class Face:
    '''Face class

    loc:list -- boundingbox face 
    mark:list -- face features / landmarks coordinate
    top_lip:list -- top lips coordinate
    bottom_lip:list -- bottom lips coordinate
    center_lip:tuple -- center of mouth coordinate
    busy:boolean -- toggle status while detecting face classification
    '''

    def __init__(self):
        self.loc = None
        self.center_lip = (0,0)
        self.busy = False


    def is_mouth_smile(self):
        ''' check if player is smiling and ready to start'''

        if type(self.loc) is type(None):
            return False

        vOA = np.array(self.center_lip) - np.array(self.top_lip[0])
        vOB = np.array(self.center_lip) - np.array(self.top_lip[-1])
        vOAB = vOA.dot(vOB)
        lenvOAB = abs(np.linalg.norm(vOA))*abs(np.linalg.norm(vOB))
        if lenvOAB:
            angle = math.degrees( math.acos( vOAB/lenvOAB ))

            #print('degree=', angle)  
            if angle < MINSMILEDEGREE :
                return True
        return False


    def is_mouth_open(self):
        ''' check if player is opening his mouth '''

        if type(self.loc) is type(None):
            return False

        # length of vertical and horizontal
        lenvert = np.linalg.norm(np.array(self.top_lip[2])-np.array(self.bottom_lip[2]))
        lenhorz = np.linalg.norm(np.array(self.top_lip[0])-np.array(self.top_lip[-1]))
        # ration vertical to hozontal
        if (lenvert / lenhorz) > MINMOUTHOPENRATIO :
            return True
        else:
            return False


    def rectangle(self, frame):
        ''' draw face rectanle '''

        if type(self.loc) is not type(None):
            (top, right, bottom, left) = self.loc
            cv2.rectangle(frame, (left,top), (right, bottom), (0,0,255), 2)

            # draw mouth position while smiling or opening 
            if self.is_mouth_open() or self.is_mouth_smile():
                for i in range(len(self.top_lip)-1):
                    cv2.line(frame, self.top_lip[i], self.top_lip[i+1],(0,255,255),1)
                for i in range(len(self.bottom_lip)-1):
                    cv2.line(frame, self.bottom_lip[i], self.bottom_lip[i+1],(0,255,255),1)

        return frame


    def detect(self, frame):
        ''' detect face classifier '''

        if self.busy:
            return self.rectangle(frame)

        self.busy = True
        rgb_frame = frame[:, :, ::-1]
        face_locs = face_recognition.face_locations(rgb_frame)
        face_marks = face_recognition.face_landmarks(rgb_frame, face_locs)

        for (top, right, bottom, left), face_mark in zip(face_locs, face_marks):
            self.loc = (top, right, bottom, left)
            #self.mark = face_mark
            self.top_lip = face_mark['top_lip'][7:12]
            self.bottom_lip = face_mark['bottom_lip'][7:12]
            lip = self.top_lip.copy()
            lip.extend(self.bottom_lip)
            self.center_lip = tuple(np.mean(lip,axis=0, dtype=int))

            # process just 1st face only, so break now
            break

        self.busy = False
        return self.rectangle(frame)


class VideoCapture:
    ''' Class VideoCapture

    vid: instance for VideoCapture
    '''

    def __init__(self, video_source=0):
        ''' init Video Capture '''

        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Command Line Parser
        args=CommandLineParser().args
     
        # 2. Video Dimension
        STD_DIMENSIONS =  {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res=STD_DIMENSIONS[args.res[0]]

        #set video sourec width and height
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])

        # Get video source width and height
        self.width,self.height=res


    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = cv2.flip(frame, 1)
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()


class CommandLineParser:
    
    def __init__(self):

        # Create object of the Argument Parser
        parser=argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement 
        # for now no required arguments 
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['480p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()


class App:
    ''' Application Class

    # vid: instance of VideoCapture 
    # video_source: video port number. try 0, 1, 2 and so on 

    # face: instance of Face

    # game: instance of Game

    
    # window: instance of root window
    # timer = 0
    # canvas: instance of canvas widget
    # btn_start: widget of button to start game
    # btn_quit: widget of button to end the application
    # delay = 10
    '''

    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
 
        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        self.face = Face()
        #self.face.start()

        self.game = Game()
        #self.game.start()

        frame1 = tk.Frame(window)
        # control start of game
        self.btn_start = tk.Button(frame1, text='START', command=self.game_start)
        self.btn_start.pack(side=tk.LEFT)

        # quit button
        self.btn_quit = tk.Button(frame1, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        frame1.pack()

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()#side=tk.LEFT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10

        self.update()
        self.window.mainloop()


    def game_start(self):
        self.game.shuffle(self.vid.width, self.vid.height)
        self.game.start()
        #self.game.level = 'smile'


    # update frame display
    def update(self):

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            frame = self.face.detect(frame)

            self.game.play_smile(frame, self.face.is_mouth_smile())
            frame = self.game.scatter(frame)
            self.game.play_eat(self.face.center_lip, self.face.is_mouth_open())
            frame = self.game.play_head_winlose(frame)
                
            image = PIL.Image.fromarray(frame)
            image = self.game.play_winlose(image, self.face.center_lip)

            self.photo = PIL.ImageTk.PhotoImage(image = image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay,self.update)


if __name__ == '__main__':
    # Create a window and pass it to the Application object
    App(tk.Tk(),'Game: Eat Number -- SimpleMath')
