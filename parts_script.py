from tkinter_annotate import SequenceConfig

import tkinterDnD as dnd
import tkinter as tk
import customtkinter as ctk
import CTkTable as ctkTable
from PIL import Image, ImageTk
import requests

from CTkMessagebox import CTkMessagebox

from tkinter import Frame, Label, Message, StringVar, Canvas
from tkinter.ttk import Scrollbar
from tkinter.constants import *

class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, root, command=None, **kwargs):
        
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=2, minsize=300)

        label1 = ctk.CTkLabel(self, text="Part Name", padx=5, anchor="center", fg_color="#5F6368", bg_color="#5F6368", )
        label2 = ctk.CTkLabel(self, text="Operations", padx=5, anchor="center", fg_color="#5F6368", bg_color="#5F6368")
        # label2 = ctk.CTkLabel(self, text="Options", padx=5, anchor="center")
        label1.grid(row=1, column=0, pady=10, padx= (10,10), sticky="new")
        label2.grid(row=1, column=1, pady=10, padx=(10,10), sticky="new")

        self.root = root
        self.command = command

        self.part_list = []
        self.options_list = []

        add_itm = ctk.CTkButton(self,text="Add New Part", width=100, height=24, command=self.open_add_popup)
        add_itm.grid(row=0, column=0, padx=10, pady=(20,10))

    def openConfig(self, part_name):
        config = SequenceConfig(self.root, part_name)
        config.protocol("WM_DELETE_WINDOW", lambda : self.closeConfig(config))

    def closeConfig(self, config_window):
        config_window.destroy()
        self.root.deiconify()


    def add_part(self, part):
        """
        Adds a new part to the list of parts.

        Parameters:
            part (string): Name of the part to add

        """

        part_label = ctk.CTkLabel(self, text = part, padx = 10, anchor = "w")

        row = len(self.part_list) + 2

        part_label.grid(row=row, column=0, pady=(0, 10))

        btn_frame = ctk.CTkFrame(master = self)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        

        config_btn = ctk.CTkButton(master = btn_frame, text="Configure", command = lambda: self.openConfig(part))

        edit_icon = ctk.CTkImage(Image.open("./edit.png").resize((17, 17)))
        edit_btn = ctk.CTkButton(master=btn_frame, image = edit_icon, text="", width = 20, command = lambda: self.open_edit_popup(part_label))

        delete_icon = ctk.CTkImage(Image.open("./bin.png").resize((17, 17)))
        delete_btn = ctk.CTkButton(master=btn_frame, image = delete_icon, textvariable="delete", text="", width = 20, command = lambda: self.remove_part(part.title()))

        btn_frame.grid(row=row, column=1, padx=5, pady=10, sticky="nwes")
        config_btn.grid(row=0, column=0, padx=5, pady=10, sticky="nesw")
        edit_btn.grid(row=0, column=1, padx=5, pady=10, sticky="nesw")
        delete_btn.grid(row=0, column=2, padx=5, pady=10, sticky="nesw")

        self.part_list.append(part_label)
        self.options_list.append(btn_frame)

    def open_add_popup(self):
        """
        Opens a popup window to add a new part 

        """

        popup = ctk.CTkToplevel(self.root)
        popup.bind("<Button-1>", lambda event: event.widget.focus_set())
        popup.title("Enter New Part Name")
        popup.grab_set()

        new_part_label = ctk.CTkLabel(popup, text="Part Name:")
        new_part_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry_new_part = ctk.CTkEntry(popup)
        
        entry_new_part.grid(row=0, column=1, padx=10, pady=5)

        def add_item(*args):
            """
            Adds the part name as specified by user.
            """

            new_part = entry_new_part.get()
            
            r = requests.post('http://127.0.0.1:5001/create_part', json={"part_name": new_part})

            print("this is the status code : ", r.status_code)
            if r.status_code == 200:
                self.add_part(new_part.title())
                               
            popup.destroy()          

        popup.bind("<Return>", add_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=add_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    def open_edit_popup(self, old_part_label):
        """
        Opens a popup window to edit a part name

        Parameters:
            old_part_label (widget): The old part label

        """

        old_partname = old_part_label.cget("text")

        popup = ctk.CTkToplevel(self.root)
        popup.bind("<Button-1>", lambda event: event.widget.focus_set())
        popup.title("Enter New Part Name")
        popup.grab_set()

        new_part_label = ctk.CTkLabel(popup, text="Part Name:")
        new_part_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry_new_part = ctk.CTkEntry(popup, placeholder_text=old_partname)
        
        entry_new_part.grid(row=0, column=1, padx=10, pady=5)
        

        def update_item(*args):
            """
            Updates the part name as specified by user, also replaces all existing instances with the new one. 
            """

            new_part = entry_new_part.get()
            
            r = requests.patch(f'http://127.0.0.1:5001/update_part/{old_partname}', json={"new_part" : new_part})

            if r.status_code == 200:
                for part, btns in zip(self.part_list, self.options_list):
                    if part.cget("text") == old_partname:
                        part.configure(text=new_part.title())

                        for widget in btns.winfo_children():
                            if widget.cget("textvariable") == "delete":
                                widget.configure(command = lambda : self.remove_part(new_part.title()))

                                popup.destroy()          
                                break

            # r = requests.post('http://127.0.0.1:5000/edit_item', json={"old_itm_val": (old_item_label, old_thresh_label), "new_itm_val": (value_item, value_thresh)}).json()

            # if r['status_code'] == 200:
            #     item_list.remove([old_item_label, old_thresh_label])
            #     old_item.configure(text = r['result'][0])
            #     old_thresh.configure(text = r['result'][1])
            #     item_list.append([r['result'][0], r['result'][1]])
                
            #     myItems = [val[0] for val in item_list]

            #     global sortable_list
            #     sortable_list.update_dropdowns(myItems)
                
            #     # Update already selected instances
            #     for item in sortable_list._list_of_items:
            #         for widget in item.winfo_children():
            #             if isinstance(widget, ctk.CTkComboBox):
            #                 if widget.get() == old_item_label:
            #                     widget.set(value_item)
            #                     sortable_list.update_seq_entry(value_item, sortable_list._position[item])
                                

        popup.bind("<Return>", update_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=update_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)


    def remove_part(self, part_to_remove):
        """
        Removes a Part from the list 

        Args:
            part_name (str): The part to be removed.

        """
        # msg = CTkMessagebox(title="Are you sure?", message="Are you sure sure?", icon="warning", option_1="Continue", option_2="Cancel")

        # if msg.get()=="Cancel":
            # return
        
        r = requests.delete('http://127.0.0.1:5001/delete_part', json={"part_name": part_to_remove})

        if r.status_code == 200:
            for part, option in zip(self.part_list, self.options_list):
                if part_to_remove == part.cget("text"):
                    part.destroy()
                    option.destroy()

                    self.part_list.remove(part)
                    self.options_list.remove(option)

                    return
            
def main():
    root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    root.title("Parts Page")

    part_frame = ctk.CTkFrame(root)

    btnframe = ScrollableLabelButtonFrame(master=part_frame, root = root, width=500, corner_radius=0, height=540)
    btnframe.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    r = requests.get('http://127.0.0.1:5001/get_all_parts')
    if r.status_code == 200:
        parts = r.json()['extra']

        for part in parts:
            btnframe.add_part(part['part_name'])

    part_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
    part_frame.grid_columnconfigure(0, weight=4)
    part_frame.grid_rowconfigure(0, weight=1)
    # part_frame.grid_columnconfigure(1, weight=1)

    root.grid_columnconfigure(0,weight=4)
    root.grid_rowconfigure(0, weight = 1)
    root.mainloop()

if __name__ == "__main__":
    main()