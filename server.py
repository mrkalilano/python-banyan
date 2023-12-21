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
        self.winners = {} 
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
                
                # Determine highest bidder and winner for each item
                for data in self.data_list:
                    if data['bidders']:
                        highest_bidder, winning_bid = max(data['bidders'], key=lambda x: x[1])
                        winner_name = highest_bidder
                        data['winner'] = {'item_name': data['item'], 'winner_name': winner_name, 'winning_bid': winning_bid}

                        # Store winner in the dictionary
                        self.winners[data['item']] = data['winner']

                # Send winner information to clients
                for data in self.data_list:
                    if 'winner' in data:
                        self.publish_payload({'winner': data['winner']}, 'reply')

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
            
    def display_winner_window(self):
        winner_window = tk.Toplevel(self.main)
        winner_window.title("Winner")
        winner_window.geometry("300x200")

        winner_textbox = tk.Text(winner_window, width=40, height=10, state=tk.NORMAL)
        winner_textbox.grid(row=0, column=0, padx=10, pady=10)

        for item, winner_data in self.winners.items():
            item_name = winner_data['item_name']
            winner_name = winner_data['winner_name']
            winning_bid = winner_data['winning_bid']
            winner_textbox.insert(tk.END, f"Item: {item_name}, Winner: {winner_name}, Winning Bid: Php{winning_bid}\n")

    def incoming_message_processing(self, topic, payload):
        if 'client_name' in payload:
            self.append_to_textbox(f"{payload['client_name']} is ready...")

        if 'sell_item_name' in payload and 'sell_item_price' in payload and 'seller_name' in payload:
            self.data_list.append({'item': payload['sell_item_name'], 'seller': payload['seller_name'], 'price': payload['sell_item_price'], 'bidders': []})
            message = f"Selling: {payload['sell_item_name']}, Php{payload['sell_item_price']} [{payload['seller_name']}]"
            self.append_to_textbox(message)
            self.publish_payload(payload, 'reply')

        if 'bid_item_name' in payload and 'bid_item_price' in payload and 'bidder_name' in payload:
            for data in self.data_list:
                  if data['item'] == payload['bid_item_name']:
                      data['bidders'].append((payload['bidder_name'], payload['bid_item_price']))
                      break
            message = f"Bidding: {payload['bid_item_name']}, Php{payload['bid_item_price']} [{payload['bidder_name']}]"
            self.append_to_textbox(message)
            self.publish_payload({'bid_item_name':payload['bid_item_name'], 'bid_item_price':payload['bid_item_price'], 'bidder_name':payload['bidder_name']}, 'reply')
    
        if 'winner' in payload and 'item_name' in payload and 'winner_name' in payload and 'winning_bid' in payload:
            winner_data = payload['winner']
            item_name = winner_data['item_name']
            winner_name = winner_data['winner_name']
            winning_bid = winner_data['winning_bid']
            message = f"Item: {item_name}, Winner: {winner_name}, Winning Bid: Php{winning_bid}"
            self.append_to_textbox(message)

    def append_to_textbox(self, message):
        self.main_textbox.configure(state=tk.NORMAL)
        self.main_textbox.insert(tk.END, f"{message}\n")
        self.main_textbox.configure(state=tk.DISABLED)


def echo_server():
    EchoServer()


if __name__ == '__main__':
    echo_server()
