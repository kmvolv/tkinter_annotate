# from tkinter import ttk
import tkinterDnD as dnd
import tkinter as tk
import customtkinter as ctk
import CTkTable as ctkTable
from PIL import Image, ImageTk
import requests

from tkinter import Frame, Label, Message, StringVar, Canvas
from tkinter.ttk import Scrollbar
from tkinter.constants import *

OS = "Windows"

class Mousewheel_Support(object):    

    # implemetation of singleton pattern
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, root, horizontal_factor = 2, vertical_factor=2):
        
        self._active_area = None
        
        if isinstance(horizontal_factor, int):
            self.horizontal_factor = horizontal_factor
        else:
            raise Exception("Vertical factor must be an integer.")

        if isinstance(vertical_factor, int):
            self.vertical_factor = vertical_factor
        else:
            raise Exception("Horizontal factor must be an integer.")

        if OS == "Linux" :
            root.bind_all('<4>', self._on_mousewheel,  add='+')
            root.bind_all('<5>', self._on_mousewheel,  add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self._on_mousewheel,  add='+')

    def _on_mousewheel(self,event):
        if self._active_area:
            self._active_area.onMouseWheel(event)

    def _mousewheel_bind(self, widget):
        self._active_area = widget

    def _mousewheel_unbind(self):
        self._active_area = None

    def add_support_to(self, widget=None, xscrollbar=None, yscrollbar=None, what="units", horizontal_factor=None, vertical_factor=None):
        if xscrollbar is None and yscrollbar is None:
            return

        if xscrollbar is not None:
            horizontal_factor = horizontal_factor or self.horizontal_factor

            xscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'x', self.horizontal_factor, what)
            xscrollbar.bind('<Enter>', lambda event, scrollbar=xscrollbar: self._mousewheel_bind(scrollbar) )
            xscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        if yscrollbar is not None:
            vertical_factor = vertical_factor or self.vertical_factor

            yscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'y', self.vertical_factor, what)
            yscrollbar.bind('<Enter>', lambda event, scrollbar=yscrollbar: self._mousewheel_bind(scrollbar) )
            yscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        main_scrollbar = yscrollbar if yscrollbar is not None else xscrollbar
        
        if widget is not None:
            if isinstance(widget, list) or isinstance(widget, tuple):
                list_of_widgets = widget
                for widget in list_of_widgets:
                    widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                    widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                    widget.onMouseWheel = main_scrollbar.onMouseWheel
            else:
                widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                widget.onMouseWheel = main_scrollbar.onMouseWheel

    @staticmethod
    def _make_mouse_wheel_handler(widget, orient, factor = 1, what="units"):
        view_command = getattr(widget, orient+'view')
        
        if OS == 'Linux':
            def onMouseWheel(event):
                if event.num == 4:
                    view_command("scroll",(-1)*factor, what)
                elif event.num == 5:
                    view_command("scroll",factor, what) 
                
        elif OS == 'Windows':
            def onMouseWheel(event):        
                view_command("scroll",(-1)*int((event.delta/120)*factor), what) 
        
        elif OS == 'Darwin':
            def onMouseWheel(event):        
                view_command("scroll",event.delta, what)
        
        return onMouseWheel

class Scrolling_Area(ctk.CTkFrame, object):

    def __init__(self, master, width=None, anchor=N, height=None, mousewheel_speed = 2, scroll_horizontally=True, xscrollbar=None, scroll_vertically=True, yscrollbar=None, outer_background=None, inner_frame=Frame, **kw):
        ctk.CTkFrame.__init__(self, master, class_=self.__class__)

        if outer_background:
            self.configure(background=outer_background)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._width = width
        self._height = height

        self.canvas = Canvas(self, background=outer_background, highlightthickness=0, width=width, height=height)
        self.canvas.grid(row=0, column=0, sticky=N+E+W+S)

        if scroll_vertically:
            if yscrollbar is not None:
                self.yscrollbar = yscrollbar
            else:
                self.yscrollbar = Scrollbar(self, orient=VERTICAL)
                self.yscrollbar.grid(row=0, column=1,sticky=N+S)
        
            self.canvas.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar['command']=self.canvas.yview
        else:
            self.yscrollbar = None

        if scroll_horizontally:
            if xscrollbar is not None:
                self.xscrollbar = xscrollbar
            else:
                self.xscrollbar = Scrollbar(self, orient=HORIZONTAL)
                self.xscrollbar.grid(row=1, column=0, sticky=E+W)
            
            self.canvas.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar['command']=self.canvas.xview
        else:
            self.xscrollbar = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.innerframe = inner_frame(self.canvas, **kw)
        self.innerframe.pack(anchor=anchor)
        
        self.canvas.create_window(0, 0, window=self.innerframe, anchor='nw', tags="inner_frame")

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        Mousewheel_Support(self).add_support_to(self.canvas, xscrollbar=self.xscrollbar, yscrollbar=self.yscrollbar)

    @property
    def width(self):
        return self.canvas.winfo_width()

    @width.setter
    def width(self, width):
        self.canvas.configure(width= width)

    @property
    def height(self):
        return self.canvas.winfo_height()
        
    @height.setter
    def height(self, height):
        self.canvas.configure(height = height)
        
    def set_size(self, width, height):
        self.canvas.configure(width=width, height = height)

    def _on_canvas_configure(self, event):
        width = max(self.innerframe.winfo_reqwidth(), event.width)
        height = max(self.innerframe.winfo_reqheight(), event.height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (width, height))
        self.canvas.itemconfigure("inner_frame", width=width, height=height)

    def update_viewport(self):
        self.update()

        window_width = self.innerframe.winfo_reqwidth()
        window_height = self.innerframe.winfo_reqheight()
        
        if self._width is None:
            canvas_width = window_width
        else:
            canvas_width = min(self._width, window_width)
            
        if self._height is None:
            canvas_height = window_height
        else:
            canvas_height = min(self._height, window_height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (window_width, window_height), width=canvas_width, height=canvas_height)
        self.canvas.itemconfigure("inner_frame", width=window_width, height=window_height)

# Python 3 support
basestring = str

class Item(ctk.CTkFrame):
    def __init__(self, master, value, width, height, selection_handler=None, drag_handler = None, drop_handler=None, **kwargs):

        kwargs.setdefault("class_", "Item")
        ctk.CTkFrame.__init__(self, master, width = width, height = height, bg_color="#5F6368", fg_color="#5F6368")
        
        self._x = None
        self._y = None
        
        self._width = width
        self._height = height

        self._tag = "item%s"%id(self)
        self._value = value

        self._selection_handler = selection_handler
        self._drag_handler = drag_handler
        self._drop_handler = drop_handler

    @property
    def x(self):
        return self._x
        
    @property
    def y(self):
        return self._y
        
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
        
    @property
    def value(self):
        return self._value
        
    def init(self, container, x, y):
        self._x = x
        self._y = y

        self.place(in_=container, x=x, y=y)

        self.bind_class(self._tag, "<ButtonPress-1>", self._on_selection)
        self.bind_class(self._tag, "<B1-Motion>", self._on_drag)
        self.bind_class(self._tag, "<ButtonRelease-1>", self._on_drop)

        # self._add_bindtag(self)
        
        # Python3 compatibility: dict.values() return a view
        list_of_widgets = list(self.children.values())
        hamburger_widgets = [widget for widget in list_of_widgets if isinstance(widget, tk.Label) and hasattr(widget, 'tag') and widget.tag == "hamburger"]

        for widget in hamburger_widgets:
            self._add_bindtag(widget)

        bin_widgets = [widget for widget in list_of_widgets if isinstance(widget, tk.Label) and hasattr(widget, 'tag') and widget.tag == "bin"]

    def _add_bindtag(self, widget):
        bindtags = widget.bindtags()
        if self._tag not in bindtags:
            widget.bindtags((self._tag,) + bindtags)

    def modify_value(self, value):
        self._value = value  

    def _on_selection(self, event):
        self.tkraise()

        self._move_lastx = event.x_root
        self._move_lasty = event.y_root
        
        if self._selection_handler:
            self._selection_handler(self)

    def _on_drag(self, event):
        self.master.update_idletasks()
        
        cursor_x = self._x + event.x
        cursor_y = self._y + event.y

        self._x += event.x_root - self._move_lastx
        self._y += event.y_root - self._move_lasty

        self._move_lastx = event.x_root
        self._move_lasty = event.y_root

        self.place_configure(x=self._x, y=self._y)

        if self._drag_handler:
            self._drag_handler(cursor_x, cursor_y)
           
    def _on_drop(self, event):
        if self._drop_handler:
            self._drop_handler()
            
    def set_position(self, x,y):
        self._x = x
        self._y = y
        self.place_configure(x =x, y =y)
        
    def move(self, dx, dy):
        self._x += dx
        self._y += dy

        self.place_configure(x =self._x, y =self._y)

class DDList(ctk.CTkFrame):
    def __init__(self, master, item_width, item_height, item_relief=None, item_background=None, item_borderwidth=None, offset_x=0, offset_y=0, gap=0, **kwargs):
        kwargs["width"] = item_width+offset_x*2
        kwargs["height"] = offset_y*2

        ctk.CTkFrame.__init__(self, master)

        self._item_borderwidth = item_borderwidth
        self._item_relief = item_relief
        self._item_background = item_background
        self._item_width = item_width
        self._item_height = item_height
        
        self._offset_x = offset_x
        self._offset_y = offset_y
               
        self._left = offset_x
        self._top = offset_y
        self._right = self._offset_x + self._item_width
        self._bottom = self._offset_y

        self._gap = gap

        self._index_of_selected_item = None
        self._index_of_empty_container = None

        self._list_of_items = []
        self._position = {}

        self._new_y_coord_of_selected_item = None

    def create_item(self, value=None, **kwargs):
        item = Item(self.master, value, self._item_width, self._item_height, self._on_item_selected, self._on_item_dragged, self._on_item_dropped)   
        return item

    def configure_items(self, **kwargs):
        for item in self._list_of_items:
            item.configure(**kwargs)

    def add_item(self, item, index=None, seq_val = None):
        if index is None:
            index = len(self._list_of_items)
        else:
            if not -len(self._list_of_items) < index < len(self._list_of_items):
                raise ValueError("Item index out of range")

            for i in range(index, len(self._list_of_items)):
                _item = self._list_of_items[i]
                _item.move(0,  self._item_height + self._gap)
                
                self._position[_item] += 1
        
        x = self._offset_x
        y = self._offset_y + index * (self._item_height + self._gap)

        self._list_of_items.insert(index, item)
        self._position[item] = index

        item.init(self, x,y)

        if len(self._list_of_items) == 1:
            self._bottom += self._item_height
        else:
            self._bottom += self._item_height + self._gap
            
        self.configure(height=self._bottom + self._offset_y)

        if seq_val is None:
            global part_name
            new_order = [widget.value for widget in self._list_of_items]
            print("This is the new order : ", new_order)
            requests.post("http://127.0.0.1:5000/add_seq_entry", json={"part_name": part_name, "sequence_index": index, "parent_order" : new_order})

        return item

    def delete_item(self, index):
        
        if isinstance(index, Item):
            index = self._position[index]
        else:
            if not -len(self._list_of_items) < index < len(self._list_of_items):
                raise ValueError("Item index out of range")

        item = self._list_of_items.pop(index)
        value = item.value

        del self._position[item]

        item.destroy()
        
        for i in range(index, len(self._list_of_items)):
            _item = self._list_of_items[i]
            _item.move(0,  -(self._item_height+self._gap))
            self._position[_item] -= 1
        
        if len(self._list_of_items) == 0:
            self._bottom -= self._item_height
        else:
            self._bottom -= self._item_height + self._gap

        self.configure(height=self._bottom + self._offset_y)
        
        return value

    del_item = delete_item
    
    def pop(self):
        return self.delete_item(-1)
        
    def shift(self):
        return self.delete_item(0)
        
    def append(self, item):
        self.add_item(item)
        
    def unshift(self, item):
        self.add_item(0, item)
        
    def get_item(self, index):
        return self._list_of_items[index]

    def get_value(self, index):
        return self._list_of_items[index].value

    def _on_item_selected(self, item):        
        self._index_of_selected_item = self._position[item]
        self._index_of_empty_container = self._index_of_selected_item

    def _on_item_dragged(self, x, y):

        if self._left < x < self._right and self._top < y < self._bottom:

            quotient, remainder = divmod(y-self._offset_y, self._item_height + self._gap)

            if remainder < self._item_height:
            
                new_container = quotient

                if new_container != self._index_of_empty_container:
                    if new_container > self._index_of_empty_container:
                        for index in range(self._index_of_empty_container+1, new_container+1, 1):
                            item = self._get_item_of_virtual_list(index)                            

                            item.move(0,-(self._item_height+self._gap))
                    else:
                        for index in range(self._index_of_empty_container-1, new_container-1, -1):
                            item = self._get_item_of_virtual_list(index)

                            item.move(0,self._item_height+self._gap)

                    self._index_of_empty_container = new_container
                    
    def _get_item_of_virtual_list(self, index):
        if self._index_of_empty_container == index:
            raise Exception("No item in index: %s"%index)
        else:
            if self._index_of_empty_container != self._index_of_selected_item:
                if index > self._index_of_empty_container:
                    index -= 1

                if index >= self._index_of_selected_item:
                    index += 1
            item = self._list_of_items[index]
            return item

    def _on_item_dropped(self):
        item = self._list_of_items.pop(self._index_of_selected_item)
        self._list_of_items.insert(self._index_of_empty_container, item)
        
        x = self._offset_x
        y = self._offset_y + self._index_of_empty_container *(self._item_height + self._gap)
        
        item.set_position(x,y)
        
        for i in range(min(self._index_of_selected_item, self._index_of_empty_container),max(self._index_of_selected_item, self._index_of_empty_container)+1):
            item = self._list_of_items[i]
            self._position[item] = i
            
        self._index_of_empty_container = None
        self._index_of_selected_item = None

        new_order = [widget.value for widget in self._list_of_items]
        print("This is the new order : ", new_order)
        requests.post("http://127.0.0.1:5000/update_seq_order", json={"part_name": part_name, "sequence_order": new_order})

class DDListWithLabels(DDList):
    def __init__(self, master, root, item_width, item_height, **kwargs):
        super().__init__(master, item_width, item_height, **kwargs)
        self.root = root
        self.values = []

    def create_item(self, value=None, **kwargs):
        item = super().create_item(value)
        self.add_labels_and_dropdown(item, **kwargs)

        return item

    def _get_mex(self, order):
        # sort order
        sorted_list = order.copy()
        sorted_list.sort()
        for i in range(len(sorted_list)):
            if i != sorted_list[i]:
                return i
        
        return len(sorted_list)

    def delete_row(self, row):
        row_index = self._position[row]
        self.delete_item(row_index)

        # self.view_updated_vals(self)
        
        # for widget in self._list_of_items:
        #     widget.modify_value(69)

        new_order = [widget.value for widget in self._list_of_items]
        print("this is new previous order : ", new_order)
        
        mex_value = self._get_mex(new_order)
        for widget in self._list_of_items:
            if widget.value > mex_value:
                widget.modify_value(widget.value - 1)

        new_order = [widget.value for widget in self._list_of_items]
        print("this is updated order : ", new_order)

        requests.post("http://127.0.0.1:5000/delete_seq_entry", json={"part_name": part_name, "sequence_index": row_index, "parent_order": new_order})
        # requests.post("http://127.0.0.1:5000/update_seq_order", json={"part_name": part_name, "sequence_order": new_order})

    def update_seq_entry(self, event, idx):
        r = requests.post("http://127.0.0.1:5000/update_seq_item", json={"part_name": part_name, "selected_item": event, "sequence_index": idx})
        
    def _create_new_window(self, item):
        for widget in item.winfo_children():
            if(isinstance(widget, ctk.CTkComboBox)):
                dd_val = widget.get()  
                break

        newwindow = NewWindow(master = self.root, item_details =(dd_val, self._position[item]), selected_item = item)
        # newwindow.mainloop()
        newwindow.protocol("WM_DELETE_WINDOW", lambda: self._close_new_window(newwindow))

    def _close_new_window(self, newwindow):
        newwindow.destroy()
        self.root.deiconify()

    def add_labels_and_dropdown(self, item, **kwargs):
        combo_items = ctk.CTkLabel(item, text="Items", font=("Roboto", 14))
        combo_items.pack(side="left", padx=10)

        global item_list
        self.values = [val[0] for val in item_list]
        
        # print("This is kwargs : ",kwargs['seq_val'])

        combo = ctk.CTkComboBox(item, state="readonly", values=self.values, command=lambda event:self.update_seq_entry(event=event,idx=self._position[item]))
        try:
            combo.set(kwargs['seq_val']['item_id'])
        except:
            pass
        combo.pack(side="left", padx=10, expand = True)

        qty_label = ctk.CTkLabel(item, text="Quantity", font=("Roboto", 14))
        # print("This is supposed to be item quantity : ", len(kwargs['seq_val']['item_position']))
        qty_label.pack(side="left")
        qty = ctk.CTkEntry(item, width=50, state=ctk.DISABLED)

        qty_val = tk.StringVar()
        try:
            qty_val.set(len(kwargs['seq_val']['item_position']))
        except:
            qty_val.set("0")
        finally:
            qty.configure(textvariable = qty_val)

        qty.pack(side="left", padx=10, expand = True)

        # cool_button = ctk.CTkButton(item, text="Set Regions", command=lambda: NewWindow(self.root))
        cool_button = ctk.CTkButton(item, text="Set Regions", command= lambda:self._create_new_window(item))
        cool_button.pack(side="left", padx=10, expand = True)
        
        # hamburger_img = ctk.CTkImage(Image.open("./hamburger.png"), size=(15, 15))
        # hamburger_btn = ctk.CTkButton(master=item, text = "", image = hamburger_img, width=30)
        # hamburger_btn.pack(side="left", padx=5, expand=True)

        # ham_label = ctk.CTkLabel(item)
        # ham_label.pack(side="left", padx=5, expand = True)
        # ham_label.tag = "hamburger"

        # ham_label.configure(image=hamburger_img)

        image_label = tk.Label(item)
        image_label.pack(side="left", padx=10, expand = True)
        image_label.tag = "hamburger"

        image = Image.open("./hamburger.png").resize((17, 17))
        photo = ImageTk.PhotoImage(image=image)
        image_label.config(image=photo)
        image_label.image = photo

        delete_img = Image.open("./bin.png").resize((17, 17))
        delete_icon = ImageTk.PhotoImage(image=delete_img)
        delete_button = tk.Button(item, image = delete_icon, command = lambda row = item: self.delete_row(row))
        delete_button.image = delete_icon
        delete_button.pack(side="left", padx=10, pady=12)

    def update_dropdowns(self, newDropdown):
        for item in self._list_of_items:
            for widget in item.winfo_children():
                if isinstance(widget, ctk.CTkComboBox):
                    # Access the selected value of the dropdown
                    widget.configure(values = newDropdown)

    def get_new_order(self):
        new_order = []
        for item in self._list_of_items:
            for widget in item.winfo_children():
                if isinstance(widget, ctk.CTkComboBox):
                    # Access the selected value of the dropdown
                    dropdown_value = widget.get()
            
            new_order.append(dropdown_value)
            # print(f"This is the dropdown value : {dropdown_value}, and this is the entry value : {entry_value}")
        return new_order

class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, root, command=None, **kwargs):
        
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        label1 = ctk.CTkLabel(self, text="Item", padx=5, anchor="center", fg_color="#5F6368", bg_color="#5F6368")
        label2 = ctk.CTkLabel(self, text="Threshold", padx=5, anchor="w")
        label1.grid(row=1, column=0, pady=10, padx= (10,10), sticky="nsew")
        label2.grid(row=1, column=1, pady=10, padx=(10,10), sticky="w")

        self.root = root
        self.command = command


        self.label1_list = []  # List to store the first label in each row
        self.label2_list = []  # List to store the second label in each row
        self.button1_list = []  # List to store the first button in each row
        self.button2_list = []  # List to store the second button in each row
        
        global item_list
        for item in item_list:
            self.add_item(item[0], item[1])

        add_itm = ctk.CTkButton(self,text="Add New Item", width=100, height=24,command = self.open_add_popup)
        add_itm.grid(row=0, column=2, padx=5, pady=10)

    def open_add_popup(self):
        global item_list, new_seq_btn

        popup = ctk.CTkToplevel(self.root)
        popup.bind("<Button-1>", lambda event: event.widget.focus_set())
        popup.title("Enter Values")
        popup.grab_set()

        label_item = ctk.CTkLabel(popup, text="Item:")
        label_thresh = ctk.CTkLabel(popup, text="Threshold:")
        label_item.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        label_thresh.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        entry_item = ctk.CTkEntry(popup)
        entry_thresh = ctk.CTkEntry(popup)
        entry_item.grid(row=0, column=1, padx=10, pady=5)
        entry_thresh.grid(row=1, column=1, padx=10, pady=5)

        def add_new_item(*args):
            global item_list, new_seq_btn, sortable_list
            value_item = entry_item.get()
            value_thresh = entry_thresh.get()

            item_list.append([value_item, value_thresh])
            popup.destroy()

            self.add_item(value_item, value_thresh)

            myItems = [val[0] for val in item_list]
            sortable_list.update_dropdowns(myItems)
            new_seq_btn.configure(state=ctk.NORMAL)
            
            r = requests.post('http://127.0.0.1:5000/add_items', json={"itm_val": (value_item, value_thresh)})
            

        popup.bind("<Return>", add_new_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=add_new_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    def open_edit_popup(self, old_item, old_thresh):
        old_item_label = old_item.cget("text")
        old_thresh_label = old_thresh.cget("text")

        global item_list, new_seq_btn

        popup = ctk.CTkToplevel(self.root)
        popup.bind("<Button-1>", lambda event: event.widget.focus_set())
        popup.title("Enter New Values")
        popup.grab_set()

        label_item = ctk.CTkLabel(popup, text="Item:")
        label_thresh = ctk.CTkLabel(popup, text="Threshold:")
        label_item.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        label_thresh.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        entry_item = ctk.CTkEntry(popup, placeholder_text=old_item_label)
        entry_thresh = ctk.CTkEntry(popup, placeholder_text=old_thresh_label)
        entry_item.grid(row=0, column=1, padx=10, pady=5)
        entry_thresh.grid(row=1, column=1, padx=10, pady=5)

        def update_item(*args):
            global item_list, new_seq_btn
            value_item = entry_item.get()
            value_thresh = entry_thresh.get()

            r = requests.post('http://127.0.0.1:5000/edit_item', json={"old_itm_val": (old_item_label, old_thresh_label), "new_itm_val": (value_item, value_thresh)}).json()

            if r['status_code'] == 200:
                print("This is item list : ", item_list)
                print("I want to remove : ", [old_item_label, old_thresh_label])
                item_list.remove([old_item_label, old_thresh_label])
                old_item.configure(text = r['result'][0])
                old_thresh.configure(text = r['result'][1])
                item_list.append([r['result'][0], r['result'][1]])
                

                print(f"The new item is {r['result'][0]} and the new threshold is {r['result'][1]}")
                myItems = [val[0] for val in item_list]

                # print("These are my updated items ; )", myItems)
                global sortable_list
                sortable_list.update_dropdowns(myItems)
                
                # Update already selected instances
                for item in sortable_list._list_of_items:
                    for widget in item.winfo_children():
                        if isinstance(widget, ctk.CTkComboBox):
                            if widget.get() == old_item_label:
                                widget.set(value_item)
                                print("This is the position", sortable_list._position[item])
                                sortable_list.update_seq_entry(value_item, sortable_list._position[item])
                            


            popup.destroy()          

        popup.bind("<Return>", update_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=update_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)


    def add_item(self, item1, item2):
        label1 = ctk.CTkLabel(self, text=item1, padx=10, anchor="w")
        label2 = ctk.CTkLabel(self, text=item2, padx=10, anchor="w")

        row = len(self.label1_list) + 2  # Start from row 1 for data rows
        
        label1.grid(row=row, column=0, pady=(0, 10))
        label2.grid(row=row, column=1, pady=(0, 10))
    
        button1 = ctk.CTkButton(self, text="Edit", width=100, height=24, command = lambda: self.edit_item(label1,label2))
        button2 = ctk.CTkButton(self, text="Delete", width=100, height=24, command=lambda: self.remove_item(item1))
        if self.command is not None:
            button1.configure(command=lambda: self.command(item1, "Edit"))
            button2.configure(command=lambda: self.command(item1, "Delete"))
        button1.grid(row=row, column=2, pady=(0, 10), padx=5)
        button2.grid(row=row, column=3, pady=(0, 10), padx=5)
        self.button1_list.append(button1)
        self.button2_list.append(button2)

        self.label1_list.append(label1)
        self.label2_list.append(label2)

    def edit_item(self, label1, label2):
        updated_val = self.open_edit_popup(label1, label2)

        # for label1, label2 in zip(self.label1_list, self.label2_list):
        #     if item1 == label1.cget("text"):
        #         print("This is the new and updated value : ", updated_val)
        #         return


    def remove_item(self, item1):
        for label1, label2, button1, button2 in zip(self.label1_list, self.label2_list, self.button1_list, self.button2_list):
            if item1 == label1.cget("text"):
                label1.destroy()
                label2.destroy()
                button1.destroy()
                button2.destroy()
                self.label1_list.remove(label1)
                self.label2_list.remove(label2)
                self.button1_list.remove(button1)
                self.button2_list.remove(button2)
                
                global part_name
                
                #FIXME: Give a warning to the user that all sequence values with this item will be deleted
                global sortable_list

                old_order = [widget.value for widget in sortable_list._list_of_items]
                r = requests.post('http://127.0.0.1:5000/delete_item', json={"item": item1, "part_name": part_name, "old_order": old_order}).json()
                
                if r['status_code'] == 200:
                    del_idx = r['del_idx']
                    print("this is the del idx i got : ", del_idx)

                    offset = 0
                    for idx_to_delete in del_idx:
                        # print("I will delete this index in order : ", idx_to_delete-1-offset)
                        sortable_list.delete_row(sortable_list._list_of_items[idx_to_delete-1-offset])
                        offset+=1

                    # for item in sortable_list._list_of_items:
                        
                    #     if item.value+offset in del_idx:
                    #     #     print("I have removed the item present at this index : ", item.value, "  and this is the offset : ", offset)
                    #     #     sortable_list.delete_row(item)
                    #         offset+=1
                    #     idx+=1

                if not len(self.label1_list):
                    global new_seq_btn
                    new_seq_btn.configure(state=ctk.DISABLED)
                return

class NewWindow(ctk.CTkToplevel):
    def __init__(self, master, item_details, selected_item):
        super().__init__(master = master)
        master.withdraw()

        self.item_details = item_details

        self.coordinates_list = []
        self.selected_box = None
        self.start_x = 0
        self.start_y = 0
        self.box_to_delete = None
        self.last_click = None
        self.last_coords = [-1,-1,-1,-1]
        global part_name
        self.part_name = part_name

        self.selected_item = selected_item
                    
        self.image = self.get_realtime_image()
        photo = ImageTk.PhotoImage(image=self.image)
        # self.IMG_WIDTH = min(self.image.size[0], CANVAS_WIDTH)
        self.IMG_WIDTH = self.image.size[0]
        # self.IMG_HEIGHT = min(self.image.size[1], CANVAS_HEIGHT)
        self.IMG_HEIGHT = self.image.size[1]

        self.canvas = tk.Canvas(master=self, width=self.IMG_WIDTH, height=self.IMG_HEIGHT, highlightthickness=0, bd=0)
        self.canvas.pack(padx=10, pady= 10)

        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

        r = requests.post('http://127.0.0.1:5000/get_coordinates', json={"part_name": self.part_name, "item_details" : self.item_details}).json()

        if r['status_code'] == 200:
            if r['result'] != {}:
                print("This is the result obtained from the api : ", r['result'])
                self.coordinates_list = r['result']

                for coord in r['result']:
                    self.draw_rectangle(coord[0], coord[1], coord[2], coord[3], outline="blue", width=2, fill="green",stipple="gray25",tags="user_box")

        remove_box_button = ctk.CTkButton(master=self, text="Delete Box", command=self.delete_selected_box)
        reset_button = ctk.CTkButton(master=self, text="Reset", command=self.reset_boxes)

        remove_box_button.pack(side="bottom", padx=10, pady=10)
        reset_button.pack(side="bottom", padx=10, pady=10)

        # Bind the mouse click event to the on_draw function
        self.canvas.bind("<ButtonPress-1>", self.on_lmb_press)
        self.canvas.bind("<B1-Motion>", self.on_lmb_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_lmb_release)

        save_exit = ctk.CTkButton(self, text="Save and Exit", command= lambda root = master: self._save_and_exit(root))
        save_exit.pack(side="bottom", padx=10, pady=10)

    def _save_and_exit(self, root):
        root.deiconify()
        self.destroy()

    def _update_selected_item(self):
        for widget in self.selected_item.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                qty_val = tk.StringVar()
                qty_val.set(len(self.coordinates_list))
                widget.configure(textvariable=qty_val)
                break

    def get_realtime_image(self):
        return Image.open("./a.jpg")  # Replace with your image source

    def draw_box(self, x1, y1, x2, y2):
        # Draw a semi-transparent box on the canvas
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="blue", stipple="gray25")

    def draw_saved_boxes(self):
        # Logic to draw saved boxes with some color
        # Here, you can draw rectangles using the coordinates list and a specific color
        for coords in self.coordinates_list:
            x1, y1, x2, y2 = coords
            self.draw_box(x1, y1, x2, y2)

    def check_overlap(self, mybox, last_coords = None):
            # Logic to check if the box is overlapping with any other drawn box
            for coord in self.coordinates_list:
                if(coord == (last_coords if last_coords else self.last_coords)):
                    continue

                x1, y1, x2, y2 = coord
                if mybox[0] < x2 and mybox[1] < y2 and mybox[2] > x1 and mybox[3] > y1:
                    return True
                
            return False

    # ============================ CANVAS HELPER FUNCTIONS ============================ 
    def draw_rectangle(self, x1, y1, x2, y2, **kwargs):
        return self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def delete_selected_box(self):
        if not self.coordinates_list:
            tk.messagebox.showerror("WARNING","There are no more boxes to delete")
            return
        
        try:
            print("I want to delete this box : ")
            print(self.box_to_delete)
            print(" ========================== ")
            self.canvas.delete(self.box_to_delete[0])
            self.coordinates_list.remove(self.box_to_delete[1])
        except:
            tk.messagebox.showerror("WARNING","You haven't selected any box")
        else:
            requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
            self._update_selected_item()

    def reset_boxes(self):
        for box in self.canvas.find_withtag("user_box"):
            self.canvas.delete(box)

        self.box_to_delete = None
        self.coordinates_list = []

        requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
        self._update_selected_item()


    # ============================ EVENT HANDLING FUNCTIONS ============================ 
    def on_lmb_press(self, event):
        # print("This is box to delete : ", self.box_to_delete)

        self.last_click = (event.x, event.y)

        for box in self.canvas.find_withtag("user_box"):
            x1, y1, x2, y2 = self.canvas.coords(box)
            if x1 < event.x < x2 and y1 < event.y < y2:
                # Inside an existing box, enable dragging
                self.selected_box = box
                self.selected_box_offset_x = event.x - x1
                self.selected_box_offset_y = event.y - y1

                self.selected_box_width = x2 - x1
                self.selected_box_height = y2 - y1

                self.last_coords = [min(x1, x1 + self.selected_box_width), y1, max(x1, x1 + self.selected_box_width), y1 + self.selected_box_height]
                break
        else:
            # Not inside an existing box, start drawing a new rectangle
            print("Drawing new box")
            self.canvas.itemconfig(self.selected_box, fill="green")
            self.selected_box = None
            self.start_x = event.x
            self.start_y = event.y
            self.canvas.delete("temp_box")
            self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=2, tags="temp_box")

    def on_lmb_drag(self, event):
        if self.selected_box:
            # Move the selected box if it exists
            x = event.x - self.selected_box_offset_x
            y = event.y - self.selected_box_offset_y
            x1, y1, x2, y2 = self.canvas.coords(self.selected_box)
            self.canvas.coords(self.selected_box, x, y, x + (x2 - x1), y + (y2 - y1))
        else:
            # Update the temporary rectangle while the user is drawing
            self.canvas.coords("temp_box", self.start_x, self.start_y, event.x, event.y)

    def on_lmb_release(self, event):
        if not self.selected_box:
            print("I am in if")
            # No selected box, so all boxes should have green fill :
            try:
                self.canvas.itemconfig(self.box_to_delete[0], fill = "green")
            except:
                pass
            
            print("No BOX SELECTED!")

            if(abs(self.last_click[0] - event.x) <= 2 and abs(self.last_click[1] - event.y) <= 2):
                print("I am setting selected box to none : )")
                self.box_to_delete = None

            # Draw the final rectangle if the user was drawing a new one
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y

            min_width = 5
            min_height = 5

            # Check Overflow 
            if abs(x1-x0) < min_width or abs(y1-y0) < min_height or (x1 >= self.IMG_WIDTH or x1 < 0) or (y1 >= self.IMG_HEIGHT or y1 < 0) or (x0 >= self.IMG_WIDTH or x0 < 0) or (y0 >= self.IMG_HEIGHT or y0 < 0):
                print("overflow detected")
                pass
            # Checking for overlap
            elif self.check_overlap([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)], [-1,-1,-1,-1]):
                print("overlap detected ")
                pass
            else:
                print(" i draw ")
                self.last_coords = [x0, y0, x1, y1]
                self.draw_rectangle(x0, y0, x1, y1, outline="blue", width=2, fill="green",stipple="gray25",tags="user_box")
                self.coordinates_list.append([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)])

                requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
                self._update_selected_item()


        else:
            print("I am in else ")
            # This means that the user is trying to SELECT a box, and not drag it
            if(abs(self.last_click[0] - event.x) == 0 and abs(self.last_click[1] - event.y) == 0):
                if self.selected_box:
                    try:
                        self.canvas.itemconfig(self.box_to_delete[0], fill = "green")
                    except:
                        pass

                    cursor_x, cursor_y = event.x, event.y

                    x0 = cursor_x - self.selected_box_offset_x
                    y0 = cursor_y - self.selected_box_offset_y

                    x1 = x0 + self.selected_box_width
                    y1 = y0 + self.selected_box_height
                    self.box_to_delete = [self.selected_box,[x0,y0,x1,y1]]

            # User is DRAGGING the box     
            else:
                cursor_x, cursor_y = event.x, event.y
                
                x0 = cursor_x - self.selected_box_offset_x
                y0 = cursor_y - self.selected_box_offset_y

                x1 = x0 + self.selected_box_width
                y1 = y0 + self.selected_box_height

                # Checking for boundary exceeded
                if(x0 < 0 or x1 > self.IMG_WIDTH or y0 < 0 or y1 > self.IMG_HEIGHT):
                    print("Boundary exceeded!")
                    # Restore previous state
                    self.canvas.coords(self.selected_box, self.last_coords[0], self.last_coords[1], self.last_coords[2], self.last_coords[3])
                # Checking for overlap
                elif(self.check_overlap([x0, y0, x1, y1])):
                    print("Overlap detected!")
                    # Restore previous state
                    self.canvas.coords(self.selected_box, self.last_coords[0], self.last_coords[1], self.last_coords[2], self.last_coords[3])
                else:
                    # Update new coordinates after drag and drop
                    print("I need to delete this cord : ", self.last_coords)
                    try:
                        del self.coordinates_list[self.coordinates_list.index(self.last_coords)]
                    except:
                        print("I couldn't delete this cord")
                        pass
                    else:
                        if self.box_to_delete:
                            if self.box_to_delete[1] == self.last_coords:
                                self.box_to_delete[1] = [x0, y0, x1, y1]
                        self.coordinates_list.append([x0, y0, x1, y1])
                    finally:
                        requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
                        self._update_selected_item()


        try:
            self.canvas.itemconfig(self.box_to_delete[0], fill = "red")
        except:
            pass
        self.canvas.delete("temp_box")

        print(self.coordinates_list)

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480

# Replace this with your streaming http response logic
# For this example, I'll use a static image

# ======================== HELPER FUNCTIONS ========================
# def get_realtime_image():
#     return Image.open("./a.jpg")  # Replace with your image source

# def draw_box(canvas, x1, y1, x2, y2):
#     # Draw a semi-transparent box on the canvas
#     canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="blue", stipple="gray25")

# def draw_saved_boxes(coordinates_list,canvas):
#     # Logic to draw saved boxes with some color
#     # Here, you can draw rectangles using the coordinates list and a specific color
#     for coords in coordinates_list:
#         x1, y1, x2, y2 = coords
#         draw_box(canvas, x1, y1, x2, y2)

# def check_overlap(coordinates_list, last_coords, mybox):
#         # Logic to check if the box is overlapping with any other drawn box
#         for coord in coordinates_list:
#             if(coord == last_coords):
#                 continue

#             x1, y1, x2, y2 = coord
#             if mybox[0] < x2 and mybox[1] < y2 and mybox[2] > x1 and mybox[3] > y1:
#                 return True
            
#         return False

def add_item(sortable_list, seq_val = None):
    index = len(sortable_list._list_of_items)
    item = sortable_list.create_item(value = index, seq_val = seq_val)
    sortable_list.add_item(item, seq_val = seq_val)

# DEBUG 
def view_updated_vals(sortable_list):
    for item in sortable_list._list_of_items:
        for widget in item.winfo_children():
            if isinstance(widget, tk.ttk.Combobox):
                # Access the selected value of the dropdown
                dropdown_value = widget.get()
            elif isinstance(widget, tk.Entry):
                # Access the text entered in the entry widget
                entry_value = widget.get()

        print(f"This is the dropdown value : {dropdown_value}, and this is the entry value : {entry_value}")

def main():
    root = ctk.CTk()
    ctk.set_appearance_mode("Dark")
    root.title("Real-time Video Feed")

    global part_name
    # HARD CODED PART SELECTION
    part_name = "PartA"
    r = requests.post('http://127.0.0.1:5000/get_part_id', json={"part_name": part_name})

    annot_frame = tk.Frame()
    regions_frame = ctk.CTkScrollableFrame(master=root, width = 700)
    items_frame = ctk.CTkFrame(master = root)

    global item_list, new_seq_btn
    r = requests.get('http://127.0.0.1:5000/get_items').json()
    if r['status_code'] != 200:
        item_list = []
    else:
        item_list = r['result']

    # Create a button to add a new item
    btnframe = ScrollableLabelButtonFrame(master=items_frame, root = root, width=500, corner_radius=0, height=540)
    btnframe.grid(row=0, column=4, padx=0, pady=0, sticky="nsew")

    # Making it global so that ALL the dropdown values can be updated when a new item is added 
    global sortable_list
    sortable_list = DDListWithLabels(regions_frame, root, 650, 50, offset_x=10, offset_y=10, gap=10, item_borderwidth=1, item_relief="groove")

    sortable_list.grid(row=1, column=0, columnspan=2, sticky="news")
    
    r = requests.post('http://127.0.0.1:5000/get_sequence', json={"part_name": part_name}).json()
    if r['status_code'] == 200:
        curr_seq = r['result']
        parent_order = r['parent_order']
        for seq in curr_seq:
            add_item(sortable_list, seq)
        idx = 0
        for widget in sortable_list._list_of_items:
            widget.modify_value(parent_order[idx])
            idx+=1

        # new_order = [widget.value for widget in sortable_list._list_of_items]
        
    new_seq_btn = ctk.CTkButton(regions_frame, text="Add New Region", state=ctk.DISABLED if len(item_list) == 0 else ctk.NORMAL, command=lambda: add_item(sortable_list))
    new_seq_btn.grid(row=0, column=0, columnspan=2, sticky="n", padx=10, pady=(20,10))

    regions_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    # annot_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    items_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    items_frame.update()
    root.mainloop()

if __name__ == "__main__":
    main()
