import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections
from ttkthemes import ThemedStyle
from communication.serial_com import Comm


class DataLoggerGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.sample = 100
        self.data_collection1 = collections.deque([0]*self.sample, maxlen=self.sample)
        self.data_collection2 = collections.deque([0]*self.sample, maxlen=self.sample)
        # setup
        self.setup_window()
        # frames
        self.config_frames()
        self.styles()
        # plots
        self.canvas()
        # serial communication
        self.comm = Comm()
        # create GUI elements for selecting a serial port and connecting/disconnecting
        self.selectors()
        self.buttons()

    def setup_window(self) -> None:
        """ Setup the initial size of the main window
        """
        
        # tittle
        self.title("DattaLogger App")
        self.iconbitmap('./assets/logo_ecci.ico')
        # Window
        self.__screen_width = self.winfo_screenwidth()
        self.__screen_height = self.winfo_screenheight()
        self._center_x = int(self.__screen_width/2 - 1280/2)
        self._center_y = int(self.__screen_height/2 - 720/2)
        self.geometry(f'1280x720+{self._center_x}+{self._center_y}')
        self.resizable(False, False)
        self.configure(bg='#464646')

    def config_frames(self) -> None:
        self.frame_canva = ttk.Frame(self, style='Custom.TFrame', padding=(0, 0.5, 3, 6))
        self.frame_canva.pack(fill='both', expand=True, side='left')
        self.frame_buttons = ttk.Frame(self, style='Custom.TFrame', padding=(3, 6, 5, 8))
        self.frame_buttons.pack(fill='x', pady=(0, 10))
        self.frame_selector = ttk.Frame(self, style='Custom.TFrame', padding=(3, 6, 3, 6))
        self.frame_selector.pack(fill='both', expand=True, side='right')
        
    def styles(self):
        self.style = ThemedStyle()
        self.style.set_theme('equilux')
        self.style.configure('Custom.TFrame')
        self.style.configure(
            'TButton', font=('Arial', 12, 'bold'),
            fg='white'
        )
        self.style.configure(
            'TCombobox', font=('Arial', 12, 'bold'),
            fg='white'
        )
        self.style.configure(
            'TLabel', font=('Arial', 12, 'bold'),
            fg='white'
        )

    def canvas(self) -> None:
        self.fig = plt.Figure(figsize=(10, 10))
        self.ax1 = self.fig.add_subplot()
        self.ax1.set_facecolor('#5f5f5f')
        self.ax1.set_title('Sensors', fontdict={'fontname': 'Arial', 'fontsize': 14, 'color': 'white'})
        self.set_border_color(self.ax1, '#dddddd')
        
        # Plot the first signal on ax1
        self.line1,= self.ax1.plot([], [], color='blue')
        self.ax1.set_ylabel('Signal 1', color='blue')
        
        # Create a second Axes object that shares the x-axis with ax1
        self.ax2 = self.ax1.twinx()
        
        # Plot the second signal on ax2
        self.line2, = self.ax2.plot([], [], color='red')
        self.ax2.set_ylabel('Signal 2', color='red')
        
        # Change the font and axis colors to white
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')
        self.ax1.xaxis.label.set_color('white')
        self.ax1.yaxis.label.set_color('white')
        
        self.ax2.tick_params(axis='y', colors='white')
        self.ax2.yaxis.label.set_color('white')
        
        # Change the background color of the figure to '#464646'
        self.fig.patch.set_facecolor('#464646')
        
        # Create an animation that updates the data of the plot at regular intervals
        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=100)
        
        self.canva = FigureCanvasTkAgg(self.fig, master=self.frame_canva)
        self.canva.get_tk_widget().pack(padx=0, pady=0)
        
    def set_border_color(self, ax, color):
        for spine in ax.spines.values():
            spine.set_color(color)

    def selectors(self) -> None:
        self.ports_label = ttk.Label(
            text="Select Port:",
            master=self.frame_selector,
            style='TLabel'
        )
        self.ports_label.pack(pady=2)

        self.ports_combobox = ttk.Combobox(
            values=self.comm.get_ports(), master=self.frame_selector,
            style='TCombobox',
            state='readonly'
        )
        self.ports_combobox.current(0)
        self.ports_combobox.pack(pady=2)

        self.baud_label = ttk.Label(
            text="Select Baudrate:",
            master=self.frame_selector,
            style='TLabel'
        )
        self.baud_label.pack(pady=2)
        
        self.baudrate_combobox = ttk.Combobox(
            values=self.comm.BAUDRATES, master=self.frame_selector,
            style='TCombobox',
            state='readonly'
        )
        self.baudrate_combobox.bind('<<ComboboxSelected>>', self.set_baudrate)
        self.baudrate_combobox.current(3)
        self.baudrate_combobox.pack(pady=2)
        
        # Create a label to display the received character
        self.char_label = ttk.Label(
            text="Receive Character:",
            master=self.frame_selector,
            style='TLabel'
        )
        self.char_label.pack(pady=2)
        self.character_label = ttk.Label(
            textvariable=self.comm.character,
            master=self.frame_selector,
            style='TLabel'
        )
        self.character_label.pack(pady=2)

    def buttons(self) -> None:
        self.connect_button = ttk.Button(
            master=self.frame_buttons,
            text="Connect", command=self.connect,
            style='TButton'
        )
        self.connect_button.pack(pady=2)
        self.disconnect_button = ttk.Button(
            master=self.frame_buttons, text="Disconnect", command=self.disconnect, style='TButton')
        self.disconnect_button.pack(pady=2)
        
        # Create the ASCII buttons
        self.ascii_button_1 = ttk.Button(
            master=self.frame_selector,
            text="LED 1", command=lambda: self.comm.send_data('A'),
            style='TButton'
        )
        self.ascii_button_1.pack(pady=2)

        self.ascii_button_2 = ttk.Button(
            master=self.frame_selector,
            text="LED 2", command=lambda: self.comm.send_data('B'),
            style='TButton'
        )
        self.ascii_button_2.pack(pady=2)

        self.ascii_button_3 = ttk.Button(
            master=self.frame_selector,
            text="LED 3", command=lambda: self.comm.send_data('C'),
            style='TButton'
        )
        self.ascii_button_3.pack(pady=2)

    def set_baudrate(self, event=None):
        try:
            baudrate: int = int(self.baudrate_combobox.get())
            self.comm.set_baudrate(baudrate)
        except ValueError as e:
            # handle invalid baud rate
            print(e)

    def animate(self, i):
        self.data = (self.comm.data_gived.get())
        _data = self.data.split(',')
        signal1 = float(_data[0])
        signal2 = float(_data[1])
        
        self.data_collection1.append(signal1)
        self.data_collection2.append(signal2)
        
        self.line1.set_data(range(self.sample), self.data_collection1)
        self.line2.set_data(range(self.sample), self.data_collection2)
        self.ax1.relim()
        self.ax1.autoscale_view()
        return [self.line1, self.line2]
        
    
    def connect(self):
        try:
            port = self.ports_combobox.get()
            self.comm.connect(port)
        except ValueError:
            raise

    def disconnect(self):
        try:
            self.comm.disconnect()
        except ValueError:
            raise
