
# Used by DisplayDriverDummy to wait a full second for "Vsync"
from time import sleep

# Used by FrameProviderSHM to access shared memory
import posix_ipc
import mmap

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

class FrameProviderSHM(FrameProvider):
    def __init__(self,width,height,name):
        super(FrameProviderSHM, self).__init__(width,height)
        self._shm = posix_ipc.SharedMemory(name,size=(width*height*3), flags=posix_ipc.O_CREAT)
        self._shmmap = mmap.mmap(self._shm.fd, self._shm.size)
        self._frame = Frame(width,height)

    def destroy(self):
        self._shm.unlink()

    def provide_frame(self):
        shmPos = 0
        for y in range(0,self._frame.height):
            for x in range(0,self._frame.width):
                self._frame.framebuffer[y][x] = (
                        ord(self._shmmap[shmPos]),
                        ord(self._shmmap[shmPos+1]),
                        ord(self._shmmap[shmPos+2]))
                shmPos += 3;
        return self._frame;
        

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
        print("OpenPixel: Connecting")
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
    
    @staticmethod
    def handleDbg(fc,message):
        print("|".join(message))

    def handleHaltCmd(fc,message):
        fc._halted = bool(message[0])

    def __init__(self):
        self.ActiveDisplayDriver = DisplayDriverDummy(1,1)
        self.ActiveFrameProvider = FrameProviderCheckerboard(self.ActiveDisplayDriver.getWidth(),self.ActiveDisplayDriver.getHeight())
        self.MQ = posix_ipc.MessageQueue("/farnsworth_mq",read=True,write=False,flags=posix_ipc.O_CREAT)
        self.halted = False
        self._halt_interval = 1
        self._message_handlers = {}
        self.registerHandler('dbg',FarnsworthController.handleDbg)
        self.registerHandler('halt',FarnsworthController.handleHaltCmd)

    def registerHandler(self,command,fn):
        if command in self._message_handlers:
            raise RuntimeError("Command %s already registered" % command)
        self._message_handlers[command] = fn

    def run(self):
        while 1:
            if(self.halted):
                sleep(self._halt_interval)
            else:
                frame = self.ActiveFrameProvider.provide_frame()
                #if(self.ActiveDisplayDriver.alwaysDraw or self.ActiveFrameProvider.requires_draw()):
                #    self.ActiveDisplayDriver.draw(frame)
                self.ActiveDisplayDriver.draw(frame)
                self.ActiveFrameProvider.tick()
                self.ActiveDisplayDriver.wait()
            try:
                queueMessage = self.MQ.receive(0)
                self.handleMessage(queueMessage[0])
            except posix_ipc.BusyError:
                # BusyError is expected if the queue has no messages
                pass

    def handleMessage(self,message):
        spl = message.split('|')
        print(spl)
        msgCommand = spl.pop(0)
        if msgCommand in self._message_handlers:
            self._message_handlers[msgCommand](self,spl)
        else:
            print("Unknown command: %s" % msgCommand)


    @staticmethod
    def main():
        pfc = FarnsworthController()
        pfc.ActiveDisplayDriver = DisplayDriverOpenPixel("localhost:7890",1,95,16)
        pfc.ActiveFrameProvider = FrameProviderSHM(
                pfc.ActiveDisplayDriver.getWidth(),
                pfc.ActiveDisplayDriver.getHeight(),
                "/farnsworth_fb_0"
                )
        pfc.run()


FarnsworthController.main();

