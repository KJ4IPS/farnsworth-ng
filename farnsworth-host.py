
# Used by DisplayDriverDummy to wait a full second for "Vsync"
from time import sleep

import opc

class Frame:

    def __init__(self,width,height):
        self.height = height
        self.width = width
        self.framebuffer = []
        for y in range(0,height):
            self.framebuffer.append([])
            for x in range(0,width):
                self.framebuffer[y].append((0,0,0));


class FrameProvider(object):
    def __init__(self,width,height):
        self._width = width
        self._height = height
        pass

    def provide_frame(self):
        pass

    def requires_draw(self):
        return True

    def tick(self):
        # This is for non-display calculations. Called once a frame at the start of "VBLANK"
        pass


class FrameProviderDummy(FrameProvider):

    def __init__(self):
        pass

    def provide_frame(self):
        outframe = Frame(width,height)
        print("Would have provided a frame")

class FrameProviderCheckerboard(FrameProvider):
    
    def  __init__(self, width, height):
        super(FrameProviderCheckerboard, self).__init__(width, height)
        self.theFrame = Frame(width,height);
        for y in range(0,self.theFrame.height):
            for x in range(0,self.theFrame.width):
                self.theFrame.framebuffer[y][x] = ((x+y) % 2) != 0 and (255,255,255) or (0,0,0)

    def provide_frame(self):
        return self.theFrame;


class FrameProviderFlatField(FrameProvider):
    def __init__(self, width, height):
        super(FrameProviderFlatField, self).__init__(width,height)
        self.theFrame = Frame(width,height)
        for y in range(0,self.theFrame.height):
            for x in range(0,self.theFrame.width):
                self.theFrame.framebuffer[y][x] = (255,000,255)

    def provide_frame(self):
        return self.theFrame


class FrameProviderMux(FrameProvider):
    
    def __init__(self,sources):
        self.sources = sources
        self.selected_source = 0
    
    def provide_frame(self):
        return self.sources[self.selected_source].provideFrame()

    def setOutput(self,i):
        if i >= len(self.sources) or i < 0:
            raise RuntimeError("Source out of range")
        self.selected_source = i 


class DisplayDriver(object):
    
    def __init__(self, width, height):
        alwaysDraw = False
        self._width = width
        self._height = height
        pass

    def draw(self,frame):
        pass

    def wait(self):
        pass
    
    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height


class DisplayDriverDummy(DisplayDriver):

    alwaysDraw = False

    def draw(self,frame):
        print("Would have drawn a {0}x{1} frame".format(frame.width, frame.height))

    def wait(self):
        sleep(1)

class DisplayDriverOpenPixel(DisplayDriver):

    alwaysDraw = False

    def __init__(self, server, interval, width, height):
        super(DisplayDriverOpenPixel, self).__init__(width,height)
        print "OpenPixel: Connecting"
        self._interval = interval
        self._opcClient = opc.Client(server,long_connection=True)
        self._opcClient.can_connect()

    @staticmethod
    def _pixelsFromFrame(frame):
        outList = []
        for row in frame.framebuffer:
            for pixel in row:
                outList.append(pixel)
        return outList
    
    def draw(self,frame):
        self._opcClient.put_pixels(DisplayDriverOpenPixel._pixelsFromFrame(frame))
        

    def wait(self):
        sleep(self._interval)
        

class FarnsworthController:
    
    def __init__(self):
        self.ActiveDisplayDriver = DisplayDriverDummy(1,1)
        self.ActiveFrameProvider = FrameProviderCheckerboard(self.ActiveDisplayDriver.getWidth(),self.ActiveDisplayDriver.getHeight())

    def run(self):
        while 1:
            frame = self.ActiveFrameProvider.provide_frame()
            #if(self.ActiveDisplayDriver.alwaysDraw or self.ActiveFrameProvider.requires_draw()):
            #    self.ActiveDisplayDriver.draw(frame)
            self.ActiveDisplayDriver.draw(frame)
            self.ActiveFrameProvider.tick()
            self.ActiveDisplayDriver.wait()

    @staticmethod
    def main():
        pfc = FarnsworthController()
        pfc.ActiveDisplayDriver = DisplayDriverOpenPixel("localhost:7890",1,95,16)
        pfc.ActiveFrameProvider = FrameProviderCheckerboard(
                pfc.ActiveDisplayDriver.getWidth(),
                pfc.ActiveDisplayDriver.getHeight()
                )
        pfc.run()


FarnsworthController.main();

