import serial
import serial.tools.list_ports
from threading import Thread, Event
from tkinter import StringVar

class Comm:
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.character = StringVar()
        self.BAUDRATES = ['1200', '2400', '4800', '9600', '19200', '38400', '115200']
        self.ser = serial.Serial(timeout=0.5)
        self.thread = None
        self.signal = Event()
        self.data_gived = StringVar()

    def get_ports(self) -> list:
        return [str(port) for port in serial.tools.list_ports.comports()]
    
    def set_baudrate(self, baudrate: int) -> None:
        try:
            self.ser.baudrate = baudrate
        except ValueError:
            # handle invalid baud rate
            raise ValueError('Invalid baud rate')
        except serial.SerialException as e:
            # handle error setting baud rate
            raise serial.SerialException(f'Error setting baud rate: {e}')

    def connect(self, port) -> None:
        if not port:
            raise ValueError('No COM selected')
        self.ser.port = port
        try:
            self.ser.open()
        except serial.SerialException as e:
            raise ValueError(f'Could not open COM port: {e}')

    def disconnect(self) -> None:
        self.ser.close()
        self.stop_thread()
        
    def send_data(self, data):
        if not self.ser.is_open:
            raise ValueError('COM no detected')
        self.data_to_send = str(data)
        self.ser.write(self.data_to_send.encode())

    def read_data(self) -> None:
        try:
            while(self.signal.is_set() and self.ser.is_open):
                data = self.ser.readline().decode('ascii').strip()
                if len(data) > 1:
                    self.data_gived.set(data)
                else:
                    self.character.set(data)
        except TypeError:
            raise TypeError
            
    def init_thread(self) -> None:
        self.thread = Thread(target=self.read_data)
        self.thread.setDaemon(1)
        self.signal.set()
        self.thread.start()

    def stop_thread(self) -> None:
        if (self.thread is not None):
            self.signal.clear()
            self.thread.join()
            self.thread = None