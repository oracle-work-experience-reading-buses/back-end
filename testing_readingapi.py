import modules.readingbusesapi as busWrapper
import datetime

from tkinter import *

busAPI = busWrapper.ReadingBusesAPI("OHYrhd9WoJ")
data = busAPI.RequestBusPositions()

def callbackFactory(self,b):
    def _callback():
        return self.menu_open(b)
    return _callback


class Window(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        count = 0
        rawr = 0
        for i in data:
            if i["service"] == "":
                continue
            def buttonClick():
                self.menu_open(i)
            quitButton = Button(self, text=i["service"], command=callbackFactory(self, i))
        # placing the button on my window
            quitButton.place(x=rawr*50, y=count * 30)
            quitButton.data = i
            count = count + 1
            if count == 10:
                count = 0
                rawr = rawr + 1
    def menu_open(self, data):
        print("Hi")
        root = Tk()

        #size of the window
        root.geometry("400x300")

        app = Timetable(root, data)
        root.mainloop()


class Timetable(Frame):

    def __init__(self, master=None, bus=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window(bus)
    def init_window(self, bus):

        # changing the title of our master widget
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        now = datetime.datetime.now()

        date = now.strftime("%Y-%m-%d")

        service = bus["service"]
        data2 = busAPI.RequestTimeTable(self, service, date)
        for i in data2:
            break

root = Tk()

#size of the window
root.geometry("400x300")

app = Window(root)
root.mainloop()
