import tkinter as tk
import threading
import time as t
from python_banyan.banyan_base import BanyanBase

class EchoServer(BanyanBase):
    def __init__(self):
        super(EchoServer, self).__init__(process_name='Server')
        self.set_subscriber_topic('echo')
        self.time = 0
        self.data_list = [] 
        self.setup_gui()

        threading.Thread(target=self.receive_loop).start()
        threading.Thread(target=self.timer_countdown).start()

        self.main.mainloop()

    def setup_gui(self):
        self.main = tk.Tk()
        self.main.title("SERVER")
        self.main.resizable(False, False)

        self.main_textbox = tk.Text(self.main, width=40, height=25, state=tk.DISABLED)
        self.main_textbox.grid(row=0, column=0, padx=3, pady=5, columnspan=4)

        self.main_label = tk.Label(self.main, text="Countdown (Seconds):")
        self.main_label.grid(row=1, column=0, padx=1, pady=10)

        self.main_entry = tk.Entry(self.main, width=10)
        self.main_entry.grid(row=1, column=1, padx=1, pady=10)

        self.main_button_start = tk.Button(self.main, text="Start", command=self.start_countdown, width=20)
        self.main_button_start.grid(row=1, column=2, pady=10)

        self.main_button_close = tk.Button(self.main, text="Close", command=self.close_countdown, width=20, state=tk.DISABLED)
        self.main_button_close.grid(row=1, column=3, padx=1, pady=10)


    def start_countdown(self):
        self.time = int(self.main_entry.get())
        self.main_entry.configure(state=tk.DISABLED)
        self.main_button_start.configure(state=tk.DISABLED)
        self.main_button_close.configure(state=tk.NORMAL)
        threading.Thread(target=self.countdown).start()

    def close_countdown(self):
        self.time = 1
        self.main_button_close.configure(state=tk.DISABLED)

    def countdown(self):
        while True:
            self.publish_payload({'time': self.time}, 'reply')
            if self.time == 0:
                self.main_entry.configure(state=tk.NORMAL)
                self.main_button_start.configure(state=tk.NORMAL)
                break
            t.sleep(1)
            self.time -= 1

    def timer_countdown(self):
        while True:
            if self.time > 0:
                self.publish_payload({'time': self.time}, 'reply')
                t.sleep(1)
                self.time -= 0
            else:
                t.sleep(1)
                
        self.publish_payload(payload={'timer': 0}, topic='echo')

    def incoming_message_processing(self, topic, payload):
        if 'client_name' in payload:
            self.append_to_textbox(f"{payload['client_name']} is ready...")

        if all(key in payload for key in ['sell_item_name', 'sell_item_price', 'seller_name']):
            self.data_list.append({'item': payload['sell_item_name'], 'seller': payload['seller_name'], 'price': payload['sell_item_price'], 'bidders': []})
            message = f"Selling: {payload['sell_item_name']}, Php{payload['sell_item_price']} [{payload['seller_name']}]"
            self.append_to_textbox(message)
            self.publish_payload(payload, 'reply')

        if all(key in payload for key in ['bid_item_name', 'bid_item_price', 'bidder_name']):
            for data in self.data_list:
                  if data['item'] == payload['bid_item_name']:
                      data['bidders'].append((payload['bidder_name'], payload['bid_item_price']))
                      break
            message = f"Bidding: {payload['bid_item_name']}, Php{payload['bid_item_price']} [{payload['bidder_name']}]"
            self.append_to_textbox(message)
    
    def append_to_textbox(self, message):
        self.main_textbox.configure(state=tk.NORMAL)
        self.main_textbox.insert(tk.END, f"{message}\n")
        self.main_textbox.configure(state=tk.DISABLED)


def echo_server():
    EchoServer()


if __name__ == '__main__':
    echo_server()
