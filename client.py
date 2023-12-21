import tkinter as tk
import threading
from python_banyan.banyan_base import BanyanBase

class EchoClient(BanyanBase):
    def __init__(self):
        super(EchoClient, self).__init__(process_name='Client')
        self.set_subscriber_topic('reply')
        self.client_name = ''
        
        self.data_list = []

        self.setup_name_entry()

    def setup_name_entry(self):
        self.main = tk.Tk()
        self.main.title("ENTER YOUR NAME")
        self.main.resizable(False, False)

        self.main_entry = tk.Entry(self.main, width=30)
        self.main_entry.grid(row=0, column=0, padx=20, pady=20)

        self.main_button = tk.Button(self.main, text="Accept", command=self.accept_name, width=10)
        self.main_button.grid(row=0, column=1, padx=10, pady=10)

        threading.Thread(target=self.receive_loop).start()

        self.main.mainloop()

    def accept_name(self):
        self.client_name = self.main_entry.get()
        self.publish_payload({'client_name': self.client_name}, 'echo')
        self.main.destroy()
        self.setup_client_window()

    def setup_client_window(self):
        self.client = tk.Tk()
        self.client.title(f"CLIENT {self.client_name}")
        self.client.resizable(False, False)

        self.setup_top_section()
        self.setup_item_bidding_section()
        self.setup_item_selling_section()
        self.setup_highest_bidder_section()

        self.client.mainloop()

    def setup_top_section(self):
        self.client_button_bid = tk.Button(self.client, text="Bid", command=self.bid_window, width=7, state=tk.DISABLED)
        self.client_button_bid.grid(row=0, column=0, padx=2, pady=2)

        self.client_button_sell = tk.Button(self.client, text="Sell", command=self.sell_window, width=7, state=tk.DISABLED)
        self.client_button_sell.grid(row=0, column=1, padx=5, pady=2)

        self.client_label_time = tk.Label(self.client, text="Time Left:")
        self.client_label_time.grid(row=0, column=2, padx=1, pady=2)

        self.client_text_time = tk.Text(self.client, width=15, height=1, state=tk.DISABLED)
        self.client_text_time.grid(row=0, column=3, padx=2, pady=2)

    def setup_item_bidding_section(self):
        self.client_label_bidding = tk.Label(self.client, text="BIDDING ITEMS:")
        self.client_label_bidding.grid(row=1, columnspan=4, pady=2)

        self.client_listbox_bidding = tk.Listbox(self.client, width=40, height=10)
        self.client_listbox_bidding.grid(row=2, columnspan=4, padx=5, pady=5)

    def setup_item_selling_section(self):
        self.client_label_selling = tk.Label(self.client, text="SELLING ITEMS:")
        self.client_label_selling.grid(row=3, columnspan=4, pady=2)

        self.client_listbox_selling = tk.Listbox(self.client, width=40, height=10)
        self.client_listbox_selling.grid(row=4, columnspan=4, padx=5, pady=5)
    
    def setup_highest_bidder_section(self):
        self.client_label_highest = tk.Label(self.client, text="HIGHEST BIDDER:")
        self.client_label_highest.grid(row=5, columnspan=4, pady=2)

        self.client_button_show_winner = tk.Button(self.client, text="Winner", command=self.display_winner_window, width=8)
        self.client_button_show_winner.grid(row=7, column=0, padx=5, pady=5)

        self.client_listbox_highest = tk.Listbox(self.client, width=40, height=10)
        self.client_listbox_highest.grid(row=6, columnspan=4, padx=5, pady=5)
        
        
    def bid_window(self):
        self.bid = tk.Tk()
        self.bid.title("BIDDING...")
        self.bid.resizable(True, True)

        self.bidder_name = self.client_name
        index = self.client_listbox_bidding.curselection()[0]
        print(index)
        self.bid_item_name = self.data_list[index]['item_name']
        self.bid_item_price = 0

        def accept_bid():
            self.bid_item_price = self.bid_entry_price.get()

            self.publish_payload({'bid_item_name': self.bid_item_name, 'bid_item_price': self.bid_item_price,
                                  'bidder_name': self.bidder_name}, 'echo')

            self.bid.destroy()

        self.bid_label_item = tk.Label(self.bid, text=f"{self.bid_item_name}:")
        self.bid_label_item.grid(row=0, column=0, padx=5, pady=5)

        self.bid_entry_price = tk.Entry(self.bid, width=10)
        self.bid_entry_price.grid(row=0, column=1, pady=5)

        self.bid_button_accept = tk.Button(self.bid, text='Accept', command=accept_bid, width=5)
        self.bid_button_accept.grid(row=0, column=2, padx=5, pady=5)

        self.bid.mainloop()

    def sell_window(self):
        self.sell = tk.Tk()
        self.sell.title("SELLING AN ITEM...")
        self.sell.resizable(True, True)

        self.seller_name = self.client_name
        self.sell_item_name = ''
        self.sell_item_price = 0

        def accept_sell():
            self.sell_item_name = self.sell_entry_item.get()
            self.sell_item_price = int(self.sell_entry_price.get())

            self.client_listbox_selling.insert(tk.END, f"{self.sell_item_name} Php{self.sell_item_price}")

            self.publish_payload({'sell_item_name': self.sell_item_name, 'sell_item_price': self.sell_item_price,
                                  'seller_name': self.seller_name}, 'echo')

            self.sell.destroy()

        self.sell_label_item = tk.Label(self.sell, text='Item:')
        self.sell_label_item.grid(row=0, column=0, padx=10, pady=10)

        self.sell_entry_item = tk.Entry(self.sell, width=40)
        self.sell_entry_item.grid(row=0, column=1)

        self.sell_label_price = tk.Label(self.sell, text='Price:')
        self.sell_label_price.grid(row=0, column=2, padx=10, pady=10)

        self.sell_entry_price = tk.Entry(self.sell, width=20)
        self.sell_entry_price.grid(row=0, column=3)

        self.sell_button_accept = tk.Button(self.sell, text='Accept', command=accept_sell, width=20)
        self.sell_button_accept.grid(row=0, column=4, padx=10, pady=10)

        self.sell.mainloop()

    def display_winner_window(self):
        self.winner = tk.Tk()
        self.winner.title("WINNER")
        self.publish_payload({'show_winner': True}, 'echo')
    
    def incoming_message_processing(self, topic, payload):
        if 'time' in payload:
            self.client_text_time.configure(state=tk.NORMAL)
            self.client_text_time.delete('1.0', tk.END)
            self.client_text_time.insert(tk.END, payload['time'])
            self.client_text_time.configure(state=tk.DISABLED)
            self.client_button_bid.configure(state=tk.NORMAL)
            self.client_button_sell.configure(state=tk.NORMAL)
            if payload['time'] == 0:
                self.client_button_bid.configure(state=tk.DISABLED)
                self.client_button_sell.configure(state=tk.DISABLED)

        if 'sell_item_name' in payload and 'sell_item_price' in payload and  'seller_name' in payload:
            if payload['seller_name'] == self.client_name:
                pass
            else:
                item_name = payload['sell_item_name']
                item_price = payload['sell_item_price']
                seller_name = payload['seller_name']
                self.data_list.append({'item_name': item_name, 'item_price': item_price, 'seller_name': seller_name})
                
                self.client_listbox_bidding.insert(tk.END, f"{item_name}, Php{item_price} [{seller_name}]")
        
        if 'bid_item_name' in payload and 'bid_item_price' in payload and 'bidder_name' in payload:
            item_name = payload['bid_item_name']
            bid_item_price = payload['bid_item_price']
            bidder_name = payload['bidder_name']
            self.client_listbox_highest.insert(tk.END, f"BIDDING: {item_name} ==> {bid_item_price} ==> [{bidder_name}]")
            
        if 'winner' in payload: 
            winner_data = payload['winner']
            item_name = winner_data['item_name']
            winner_name = winner_data['winner_name']
            winning_bid = winner_data['winning_bid']
            self.client_listbox_highest.insert(tk.END, f"{winner_name} : {[item_name]}, Winning Bid: Php{winning_bid}")
            self.publish_payload({'winner':winner_data, 'item_name':item_name, 'winner_name':winner_name, 'winning_bid':winning_bid}, 'echo')
            
        if 'show_winner' in payload and payload['show_winner']:
            self.display_winner_window(self.client_listbox_highest)

def echo_client():
    EchoClient()


if __name__ == '__main__':
    echo_client()
