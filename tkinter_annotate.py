# from tkinter import ttk
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

OS = "Windows"

# Class utilized for scrollbar support
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

# Scrollbar Functionality
class Scrolling_Area(ctk.CTkFrame, object):

    def __init__(self, master, width=None, anchor=N, height=None, mousewheel_speed = 2, scroll_horizontally=True, xscrollbar=None, scroll_vertically=True, yscrollbar=None, outer_background=None, inner_frame=Frame, **kw):
        ctk.CTkFrame.__init__(self, master, class_=self.__class__)

        if outer_background:
            self.configure(background=outer_background)

        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        
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

# Container for all widgets
class Item(ctk.CTkFrame):
    def __init__(self, master, value, width, height, selection_handler=None, drag_handler = None, drop_handler=None, **kwargs):

        kwargs.setdefault("class_", "Item")
        ctk.CTkFrame.__init__(self, master, width = width, height = height, bg_color="#5F6368", fg_color="#5F6368")

        self.grid(column=0, row=0, sticky="news")

        self._x = None
        self._y = None

        self._width = width
        self._height = height

        self._tag = "item%s"%id(self)
        self._value = value

        # Used to configure whether item can be dragged or not
        self.enable_drag = kwargs['seq_val'] != None
        try:
            self.enable_drag &= len(kwargs['seq_val']['item_position']) != 0
        except:
            pass

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
        
    def init(self, container, x, y, **kwargs):
        """
        Item initializtion for UI

        Args:
            container (tkinter.Widget): The container widget to place the object in.
            x (int): The x-coordinate of the object's position.
            y (int): The y-coordinate of the object's position.
            **kwargs: Additional keyword arguments.

        """
        self._x = x
        self._y = y

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.place(in_=container, x=x, y=y)

        self.bind_class(self._tag, "<ButtonPress-1>", self._on_selection)
        self.bind_class(self._tag, "<B1-Motion>", self._on_drag)
        self.bind_class(self._tag, "<ButtonRelease-1>", self._on_drop)

        list_of_widgets = list(self.children.values())
        hamburger_widgets = [widget for widget in list_of_widgets if isinstance(widget, tk.Label) and hasattr(widget, 'tag') and widget.tag == "hamburger"]

        for widget in hamburger_widgets:
            if self.enable_drag: self._add_bindtag(widget)

    def _add_bindtag(self, widget):
        """
        Used to add the drag/drop functionality to the specified widget

        Parameters:
            widget (Widget): The widget to add the tag to.

        """
        bindtags = widget.bindtags()
        if self._tag not in bindtags:
            widget.bindtags((self._tag,) + bindtags)

    def _remove_bindtag(self, widget):
        """
        Used to remove drag/drop functionality for the specified widget

        Parameters:
            widget (Widget): The widget to remove the tag from.

        """
        bindtags = widget.bindtags()
        if self._tag in bindtags:
            widget.bindtags(())

    def modify_value(self, value):
        """
        To set the value of the item to a user-defined value, used to order sequence correctly

        Parameters:
            value: The new value to assign to the item.

        """
        self._value = value  

    def _on_selection(self, event):
        """
        Handle the event when a selection is made.

        Parameters:
            event (Event): The event object containing information about the selection.

        """
        self.tkraise()

        self._move_lastx = event.x_root
        self._move_lasty = event.y_root
        
        if self._selection_handler:
            self._selection_handler(self)

    def _on_drag(self, event):
        """
        Handles the drag event triggered by the user.

        Parameters:
            event (Event): The event object containing information about the drag event.

        """
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
        """
        Handles the drop item event.

        Parameters:
            event (Event): The event object representing the drop event.

        """
        if self._drop_handler:
            self._drop_handler()
            
    def set_position(self, x,y):
        """
        Sets the position of the object.

        Parameters:
            x (int): The x-coordinate of the new position.
            y (int): The y-coordinate of the new position.

        """
        self._x = x
        self._y = y
        self.place_configure(x =x, y =y)
        
    def move(self, dx, dy):
        """
        Moves the object by the specified amount in the x and y directions.

        Parameters:
            dx (int): The amount to move in the x direction.
            dy (int): The amount to move in the y direction.

        """
        self._x += dx
        self._y += dy

        self.place_configure(x =self._x, y =self._y)

# Base class for Drag and Drop List
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
        """
        Create an item with the given value and additional keyword arguments.

        Args:
            value: The value to assign to the item (default: None).
            **kwargs: Additional keyword arguments to pass to the Item constructor.

        Returns:
            The created item.

        """
        item = Item(self.master, value, self._item_width, self._item_height, self._on_item_selected, self._on_item_dragged, self._on_item_dropped, **kwargs)
        return item

    def configure_items(self, **kwargs):
        """
        Configure the items in the list.

        Args:
            **kwargs: Additional keyword arguments to pass to the configure method of each item.

        """
        for item in self._list_of_items:
            item.configure(**kwargs)

    def add_item(self, item, index=None, seq_val = None):
        """
        Adds an item to the list of items in the specified index.

        Args:
            item: The item to add to the list.
            index (optional): The index at which to insert the item. If not provided, the item will be added at the end of the list.
            seq_val (optional): The sequence value to be used for the API call. If not provided, the default value will be used.

        Raises:
            ValueError: If the index is out of range.

        Returns:
            The added item.

        """
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

        item.init(self, x,y, list_of_items = self._list_of_items)

        if len(self._list_of_items) == 1:
            self._bottom += self._item_height
        else:
            self._bottom += self._item_height + self._gap
            
        self.configure(height=self._bottom + self._offset_y)

        if seq_val is None:
            global part_name
            new_order = [widget.value for widget in self._list_of_items]
            requests.post("http://127.0.0.1:5000/add_seq_entry", json={"part_name": part_name, "sequence_index": index, "parent_order" : new_order})

        return item

    def delete_item(self, index):
        """
        Delete an item from the list at the given index.

        Parameters:
            index (int or Item): The index of the item to be deleted. If an Item object
                is provided, its index will be used instead.

        Raises:
            ValueError: If the index is out of range.

        Returns:
            The value of the deleted item.

        """
        
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
        global lock_last_elem
        
        if len(self._list_of_items) == 0:
            return
        
        if self._left < x < self._right and self._top < y < self._bottom:

            quotient, remainder = divmod(y-self._offset_y, self._item_height + self._gap)

            if remainder < self._item_height:
            
                new_container = quotient

                if new_container != self._index_of_empty_container and (new_container != len(self._list_of_items)-lock_last_elem):
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
        requests.post("http://127.0.0.1:5000/update_seq_order", json={"part_name": part_name, "sequence_order": new_order})

class DDListWithLabels(DDList):
    def __init__(self, master, root, item_width, item_height, **kwargs):
        super().__init__(master, item_width, item_height, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.root = root
        self.values = []

    def create_item(self, value=None, **kwargs):
        """
        Create an item with an optional value and additional keyword arguments.

        Parameters:
            value (any, optional): The value of the item. Defaults to None.
            **kwargs (dict): Additional keyword arguments to pass to the super().create_item method.

        Returns:
            item (Item): The created item.

        """

        item = super().create_item(value, **kwargs)
        # item.grid_columnconfigure(0, weight = 1)
        # item.grid_rowconfigure(0, weight = 1)
        self.add_labels_and_dropdown(item, **kwargs)

        return item

    def _get_mex(self, order):
        """
        Get the first missing number in a given list of integers.

        Args:
            order (List[int]): The list of integers to search for the missing number.

        Returns:
            int: The missing number in the list of integers.

        """
        # sort order
        sorted_list = order.copy()
        sorted_list.sort()
        for i in range(len(sorted_list)):
            if i != sorted_list[i]:
                return i
        
        return len(sorted_list)

    def delete_row(self, row, prompt=True):
        """
        Delete a row from the table and update the sequence order

        Parameters:
            row (int): The index of the row to be deleted.

        """
        if prompt:
            msg = CTkMessagebox(title="Are you sure?", message="The entries below the deleted entry will automatically be moved up by one level!", icon="warning", option_1="Continue", option_2="Cancel")

            if msg.get() == "Cancel":
                return
        
        row_index = self._position[row]
        self.delete_item(row_index)

        new_order = [widget.value for widget in self._list_of_items]
        
        mex_value = self._get_mex(new_order)
        for widget in self._list_of_items:
            if widget.value > mex_value:
                widget.modify_value(widget.value - 1)

        new_order = [widget.value for widget in self._list_of_items]

        global new_seq_btn

        if len(new_order) == 0 or len(new_order) == row_index:
            new_seq_btn.configure(state = ctk.NORMAL)

        global lock_last_elem, is_item_selected

        try:
            if is_item_selected:
                lock_last_elem = 0
        except:
            lock_last_elem = 1

        requests.post("http://127.0.0.1:5000/delete_seq_entry", json={"part_name": part_name, "sequence_index": row_index, "parent_order": new_order})

    def update_seq_entry(self, event, idx):
        """
        Updates collection with the new sequence order

        Args:
            event (str): The event to update the sequence entry with.
            idx (int): The index of the sequence entry to update.

        """
        r = requests.post("http://127.0.0.1:5000/update_seq_item", json={"part_name": part_name, "selected_item": event, "sequence_index": idx})
        global set_regions
        set_regions.configure(state = ctk.NORMAL)
        
    def _create_new_window(self, item):
        """
        Creates a new window based on the given item.

        Parameters:
            item (Tkinter widget): Obtaining the details of the item to make changes to

        """
        for widget in item.winfo_children():
            if(isinstance(widget, ctk.CTkComboBox)):
                dd_val = widget.get()  
                break
        
        # get the index of item 
        newwindow = NewWindow(master = self.root, item_details =(dd_val, self._position[item]), selected_item = item, item_index = self._position[item])
        newwindow.protocol("WM_DELETE_WINDOW", lambda: self._close_new_window(newwindow))

    def _close_new_window(self, newwindow):
        """
        Closes the window created for setting regions
        
        Args:
            newwindow: The new window to be closed.

        """
        newwindow.destroy()
        self.root.deiconify()

    def add_labels_and_dropdown(self, item, **kwargs):
        """
        Adds the desired widgets to the given item

        Args:
            item: The item to create the labels and dropdown menus for.
            **kwargs: Additional keyword arguments.

        """
        item.grid_columnconfigure(0, weight = 1)
        combo_items = ctk.CTkLabel(item, text="Items", font=("Roboto", 14))
        # combo_items.pack(side="left", padx=10)
        combo_items.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        global item_list
        self.values = [val[0] for val in item_list]

        combo = ctk.CTkComboBox(item, state="readonly", values=self.values, command=lambda event:self.update_seq_entry(event=event,idx=self._position[item]))
        is_item_selected = False

        try:
            combo.set(kwargs['seq_val']['item_id'])
        except:
            pass
        else:
            is_item_selected = True

        if not is_item_selected:
            global new_seq_btn
            new_seq_btn.configure(state = ctk.DISABLED)

        # combo.pack(side="left", padx=10, expand = True)
        combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        qty_label = ctk.CTkLabel(item, text="Quantity", font=("Roboto", 14))
        # qty_label.pack(side="left")
        qty_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        qty = ctk.CTkEntry(item, width=50, state=ctk.DISABLED)

        qty_val = tk.StringVar()

        global lock_last_elem
        try:
            qty_val.set(len(kwargs['seq_val']['item_position']))

            if len(kwargs['seq_val']['item_position']) == 0:
                lock_last_elem = 1
                new_seq_btn.configure(state = ctk.DISABLED)

        except:
            qty_val.set("0")

            lock_last_elem = 1
            new_seq_btn.configure(state = ctk.DISABLED)
            
        finally:
            qty.configure(textvariable = qty_val)

        # qty.pack(side="left", padx=10, expand = True)
        qty.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        global set_regions
        set_regions = ctk.CTkButton(item, text="Set Regions", command= lambda:self._create_new_window(item), state = ctk.NORMAL if is_item_selected else ctk.DISABLED)
        # set_regions.pack(side="left", padx=10, expand = True)
        set_regions.grid(row=0, column=4, padx=10, pady=5, sticky="w")

        image_label = tk.Label(item)
        # image_label.pack(side="left", padx=10, expand = True)
        image_label.grid(row=0, column=5, padx=10, pady=5, sticky="w")
        image_label.tag = "hamburger"

        image = Image.open("./hamburger.png").resize((17, 17))
        photo = ImageTk.PhotoImage(image=image)
        image_label.config(image=photo)
        image_label.image = photo

        delete_img = Image.open("./bin.png").resize((17, 17))
        delete_icon = ImageTk.PhotoImage(image=delete_img)
        delete_button = tk.Button(item, image = delete_icon, command = lambda row = item: self.delete_row(row))
        delete_button.image = delete_icon
        # delete_button.pack(side="left", padx=10, pady=12)
        delete_button.grid(row=0, column=6, padx=10, pady=5, sticky="w")

    def update_dropdowns(self, newDropdown):
        """
        Update the dropdown menus with new values.

        Parameters:
            newDropdown (list): The new values to be set for the dropdown menus.

        """
        for item in self._list_of_items:
            for widget in item.winfo_children():
                if isinstance(widget, ctk.CTkComboBox):
                    # Access the selected value of the dropdown
                    widget.configure(values = newDropdown)

    def get_new_order(self):
        """
        Get a new order by retrieving the selected values from a list of ComboBox widgets.
        
        Returns:
            list: A list of the selected values from the ComboBox widgets.

        """
        new_order = []
        for item in self._list_of_items:
            for widget in item.winfo_children():
                if isinstance(widget, ctk.CTkComboBox):
                    # Access the selected value of the dropdown
                    dropdown_value = widget.get()
            
            new_order.append(dropdown_value)
        return new_order

# Utilized by the frame that gives a scrollable list of the items currently in database
class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, root, command=None, **kwargs):
        
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        label1 = ctk.CTkLabel(self, text="Item", padx=5, anchor="center", fg_color="#5F6368", bg_color="#5F6368")
        label2 = ctk.CTkLabel(self, text="Threshold", padx=5, anchor="center", fg_color="#5F6368", bg_color="#5F6368")

        label1.grid(row=1, column=0, pady=10, padx= (10,10), sticky="nsew")
        label2.grid(row=1, column=1, pady=10, padx=(10,10), sticky="nsew")

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
        add_itm.grid(row=0, column=2, padx=10, pady=(20,10))

    def open_add_popup(self):
        """
        Opens a popup window to add a new item with its threshold.

        """
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
            """
            Adds the item entered by user after confirmation
            """
            global item_list, new_seq_btn, sortable_list
            value_item = entry_item.get()
            value_thresh = entry_thresh.get()

            item_list.append([value_item, value_thresh])
            popup.destroy()

            self.add_item(value_item, value_thresh)

            myItems = [val[0] for val in item_list]
            sortable_list.update_dropdowns(myItems)
            if(len(item_list) == 1): new_seq_btn.configure(state=ctk.NORMAL)
            
            r = requests.post('http://127.0.0.1:5000/add_items', json={"itm_val": (value_item, value_thresh)})
            

        popup.bind("<Return>", add_new_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=add_new_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    def open_edit_popup(self, old_item, old_thresh):
        """
        Opens a popup window to edit an item and its threshold.

        Parameters:
            old_item (Widget): The old item widget.
            old_thresh (Widget): The old threshold widget.

        """

        old_item_label = old_item.cget("text")
        old_thresh_label = old_thresh.cget("text")

        global item_list, new_seq_btn

        popup = ctk.CTkToplevel(self.root)
        popup.bind("<Button-1>", lambda event: event.widget.focus_set())
        popup.title("Enter New Values")
        popup.grab_set()

        label_warning = ctk.CTkLabel(popup, text="WARNING: This will overwrite all existing instances of the item with the new values.")
        label_warning.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        label_item = ctk.CTkLabel(popup, text="Item:")
        label_thresh = ctk.CTkLabel(popup, text="Threshold:")
        label_item.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        label_thresh.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        entry_item = ctk.CTkEntry(popup, placeholder_text=old_item_label)
        entry_thresh = ctk.CTkEntry(popup, placeholder_text=old_thresh_label)
        entry_item.grid(row=1, column=1, padx=10, pady=5)
        entry_thresh.grid(row=2, column=1, padx=10, pady=5)

        def update_item(*args):
            """
            Updates the item configuration as specified by user, also replaces all existing instances with the new one. 
            """
            global item_list, new_seq_btn
            value_item = entry_item.get()
            value_thresh = entry_thresh.get()

            r = requests.post('http://127.0.0.1:5000/edit_item', json={"old_itm_val": (old_item_label, old_thresh_label), "new_itm_val": (value_item, value_thresh)}).json()
            if r['status_code'] == 200:
                item_list.remove([old_item_label, old_thresh_label])

                value_item = r['result'][0]
                value_thresh = r['result'][1]

                old_item.configure(text = value_item)
                old_thresh.configure(text = value_thresh)
                item_list.append([value_item, value_thresh])

                myItems = [val[0] for val in item_list]

                global sortable_list
                sortable_list.update_dropdowns(myItems)

                # Update already selected instances
                for item in sortable_list._list_of_items:
                    for widget in item.winfo_children():
                        if isinstance(widget, ctk.CTkComboBox):
                            if widget.get() == old_item_label:
                                widget.set(value_item)
                                sortable_list.update_seq_entry(value_item, sortable_list._position[item])
                                
            popup.destroy()          

        popup.bind("<Return>", update_item)
        ok_button = ctk.CTkButton(popup, text="OK", command=update_item)
        ok_button.grid(row=3, column=1, columnspan=2, pady=10)


    def add_item(self, item1, item2):
        """
        Adds an item to the list of items.

        Parameters:
            item1 (object): The first item to add.
            item2 (object): The second item to add.

        """
        label1 = ctk.CTkLabel(self, text=item1, padx=10, anchor="w")
        label2 = ctk.CTkLabel(self, text=item2, padx=10, anchor="w")

        row = len(self.label1_list) + 2  # Start from row 1 for data rows, also is 1-indexed
        
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
        """
        Edit an item by opening an edit popup with the current labels, which are used as placeholders
        If corresponding entry is empty then their placeholder is used instead

        Parameters:
            label1 (str): The first label placeholder for the edit popup. 
            label2 (str): The second label placeholder for the edit popup.
        """
        self.open_edit_popup(label1, label2)

    def remove_item(self, item1):
        """
        Removes an item from the list and deletes every associated sequence entry.

        Args:
            item1 (str): The item to be removed.

        """
        msg = CTkMessagebox(title="Are you sure?", message="Removing this item will also delete every sequence entry associated with it!", icon="warning", option_1="Continue", option_2="Cancel")

        if msg.get()=="Cancel":
            return
        
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
                
                global part_name, sortable_list, item_list

                old_order = [widget.value for widget in sortable_list._list_of_items]
                r = requests.post('http://127.0.0.1:5000/delete_item', json={"item": item1, "part_name": part_name, "old_order": old_order}).json()

                if r['status_code'] == 200:
                    del_idx = r['del_idx']

                    item_list = [item for item in item_list if item[0] != item1]
                    myItems = [val[0] for val in item_list]
                    sortable_list.update_dropdowns(myItems)

                    offset = 0
                    for idx_to_delete in del_idx:
                        sortable_list.delete_row(sortable_list._list_of_items[idx_to_delete-1-offset], False)
                        offset+=1

                if not len(self.label1_list):
                    global new_seq_btn
                    new_seq_btn.configure(state=ctk.DISABLED)
                return

# Used by the frame to specify bounding boxes for a given image and item.
class NewWindow(ctk.CTkToplevel):
    def __init__(self, master, item_details, selected_item, item_index):
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
        self.item_index = item_index

        self.image = self.get_realtime_image()
        photo = ImageTk.PhotoImage(image=self.image)

        self.IMG_WIDTH = self.image.size[0]
        self.IMG_HEIGHT = self.image.size[1]

        self.canvas = tk.Canvas(master=self, width=self.IMG_WIDTH, height=self.IMG_HEIGHT, highlightthickness=0, bd=0)
        self.canvas.pack(padx=10, pady= 10)

        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

        r = requests.post('http://127.0.0.1:5000/get_coordinates', json={"part_name": self.part_name, "item_details" : self.item_details}).json()

        if r['status_code'] == 200:
            if r['result'] != {}:
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
        """
        Save and exit the "Set Regions" frame. Destroys the current frame and restores the root frame.

        Args:
            root (Tk): The root window of the application.

        """
        if len(self.coordinates_list) == 0:
            msg = CTkMessagebox(title="ALERT", message="You cannot have zero bounding boxes! ", icon="warning", option_1="Rectify")
            if msg.get():
                return

        root.deiconify()
        self.destroy()

    def _update_selected_item(self):
        """
        Updates the selected item.

        This function iterates over the children of the selected item widget and performs the following actions:
        - If the child widget is an instance of ctk.CTkEntry, it sets the value of the text variable to the length of the coordinates list.
        - If the child widget is an instance of tk.Label and has a tag attribute equal to "hamburger", it either adds or removes a bindtag depending on the length of the coordinates list.

        Parameters:
            self (object): The instance of the class calling the function.
            
        """
        for widget in self.selected_item.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                qty_val = tk.StringVar()
                qty_val.set(len(self.coordinates_list))

                global new_seq_btn, lock_last_elem
                if len(self.coordinates_list):
                    new_seq_btn.configure(state=ctk.NORMAL)
                    # lock_last_elem = 0
                    
                else:
                    new_seq_btn.configure(state=ctk.DISABLED)
                    # lock_last_elem = 1
                widget.configure(textvariable=qty_val)
            
            elif isinstance(widget, tk.Label) and hasattr(widget, 'tag') and widget.tag == "hamburger":
                if len(self.coordinates_list):
                    self.selected_item._add_bindtag(widget)
                else:
                    self.selected_item._remove_bindtag(widget)

    def get_realtime_image(self):
        """
        Retrieves a realtime image. Uses a static image for now

        Returns:
            Image: The realtime image.
        """
        return Image.open("./a.jpg")  # Replace with your image source

    def draw_box(self, x1, y1, x2, y2):
        """
        Draw a semi-transparent box on the canvas.

        Args:
            x1 (int): The x-coordinate of the top-left corner of the box.
            y1 (int): The y-coordinate of the top-left corner of the box.
            x2 (int): The x-coordinate of the bottom-right corner of the box.
            y2 (int): The y-coordinate of the bottom-right corner of the box.

        """
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="blue", stipple="gray25")

    def check_overlap(self, mybox, last_coords = None):
            """
            Check if the given box overlaps with any other drawn box (excluding itself)

            Parameters:
            - mybox: A tuple representing the coordinates of the box to be checked.
            - last_coords (optional): A tuple representing the coordinates of the last box drawn. Defaults to None.

            Returns:
            - True if the given box overlaps with any other drawn box.
            - False otherwise.
            """
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
        """
        Draw a rectangle on the canvas.

        Parameters:
            x1 (int): The x-coordinate of the top-left corner of the rectangle.
            y1 (int): The y-coordinate of the top-left corner of the rectangle.
            x2 (int): The x-coordinate of the bottom-right corner of the rectangle.
            y2 (int): The y-coordinate of the bottom-right corner of the rectangle.
            **kwargs: Additional keyword arguments to be passed to the create_rectangle method.

        Returns:
            int: The ID of the created rectangle on the canvas.
        """
        return self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def delete_selected_box(self):
        """
        Deletes the selected box (if any) from the canvas.

        """
        if not self.coordinates_list:
            tk.messagebox.showerror("WARNING","There are no more boxes to delete")
            return
        
        try:
            self.canvas.delete(self.box_to_delete[0])
            self.coordinates_list.remove(self.box_to_delete[1])
        except:
            tk.messagebox.showerror("WARNING","You haven't selected any box")
        else:
            requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
            self._update_selected_item()

    def reset_boxes(self):
        """
        Removes all boxes drawn in canvas and updates changes to database
        """
        for box in self.canvas.find_withtag("user_box"):
            self.canvas.delete(box)

        self.box_to_delete = None
        self.coordinates_list = []

        requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
        self._update_selected_item()


    # ============================ EVENT HANDLING FUNCTIONS ============================ 
    def on_lmb_press(self, event):
        """
        Handles the left mouse button press event on the canvas containing the image

        Parameters:
            event (Event): The event object containing information about the mouse button press.

        """

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
            self.selected_box = None
            self.start_x = event.x
            self.start_y = event.y
            self.canvas.delete("temp_box")
            self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=2, tags="temp_box")

    def on_lmb_drag(self, event):
        """
        Handle the left mouse button drag event on canvas.

        Args:
            event (Event): The event object containing information about the event.

        """
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
        """
        Handles the event when the left mouse button is released on the canvas

        Parameters:
            event (Event): The event object containing information about the mouse release.

        """
        if not self.selected_box:
            # No selected box, so all boxes should have green fill :
            try:
                self.canvas.itemconfig(self.box_to_delete[0], fill = "green")
            except:
                pass
            
            if(abs(self.last_click[0] - event.x) <= 2 and abs(self.last_click[1] - event.y) <= 2):
                self.box_to_delete = None

            # Draw the final rectangle if the user was drawing a new one
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y

            min_width = 5
            min_height = 5

            # Check Overflow 
            if abs(x1-x0) < min_width or abs(y1-y0) < min_height or (x1 >= self.IMG_WIDTH or x1 < 0) or (y1 >= self.IMG_HEIGHT or y1 < 0) or (x0 >= self.IMG_WIDTH or x0 < 0) or (y0 >= self.IMG_HEIGHT or y0 < 0):
                pass
            # Checking for overlap
            elif self.check_overlap([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)], [-1,-1,-1,-1]):
                pass
            else:
                self.last_coords = [x0, y0, x1, y1]
                self.draw_rectangle(x0, y0, x1, y1, outline="blue", width=2, fill="green",stipple="gray25",tags="user_box")
                self.coordinates_list.append([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)])

                requests.post('http://127.0.0.1:5000/update_coordinates', json={'coord_list' : self.coordinates_list, 'item_details' : self.item_details, 'part_name' : self.part_name})
                self._update_selected_item()


        else:
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
                    # Restore previous state
                    self.canvas.coords(self.selected_box, self.last_coords[0], self.last_coords[1], self.last_coords[2], self.last_coords[3])
                # Checking for overlap
                elif(self.check_overlap([x0, y0, x1, y1])):
                    # Restore previous state
                    self.canvas.coords(self.selected_box, self.last_coords[0], self.last_coords[1], self.last_coords[2], self.last_coords[3])
                else:
                    # Update new coordinates after drag and drop
                    try:
                        del self.coordinates_list[self.coordinates_list.index(self.last_coords)]
                    except:
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

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480


def add_item(sortable_list, seq_val = None):
    """
    Adds a new item to the draggable list.

    Args:
        sortable_list (SortableList): The sortable list to add the item to.
        seq_val (Any, optional): The value to use for sorting the item. Defaults to None.

    """
    index = len(sortable_list._list_of_items)
    item = sortable_list.create_item(value = index, seq_val = seq_val)
    sortable_list.add_item(item, seq_val = seq_val)


class SequenceConfig(ctk.CTkToplevel):
    def __init__(self, master, selected_part):
        super().__init__(master = master)
        master.withdraw()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0,weight=1)


        global part_name
        part_name = selected_part
        r = requests.post('http://127.0.0.1:5000/get_part_id', json={"part_name": part_name})

        regions_frame = ctk.CTkScrollableFrame(master=self, width = 700, height=700)
        items_frame = ctk.CTkFrame(master = self)

        global item_list, new_seq_btn
        r = requests.get('http://127.0.0.1:5000/get_items').json()
        if r['status_code'] != 200:
            item_list = []
        else:
            item_list = r['result']

        # Creating a frame for item list
        btnframe = ScrollableLabelButtonFrame(master=items_frame, root = self, width=500, corner_radius=0, height=700)
        btnframe.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # btnframe.grid_columnconfigure(0, weight=1)
        # btnframe.grid_rowconfigure(0, weight=1)

        global new_seq_btn
        new_seq_btn = ctk.CTkButton(regions_frame, text="Add New Region", state=ctk.DISABLED if len(item_list) == 0 else ctk.NORMAL, command=lambda: add_item(sortable_list))
        
        global lock_last_elem
        lock_last_elem = 0

        # Making it global so that ALL the dropdown values can be updated when a new item is added 
        global sortable_list
        sortable_list = DDListWithLabels(regions_frame, self, 650, 50, offset_x=10, offset_y=10, gap=10, item_borderwidth=1, item_relief="groove")
        
        sortable_list.grid(row=1, column=0, sticky="new")
        sortable_list.grid_rowconfigure(0, weight=1)
        # sortable_list.columnconfigure(0, weight=1)

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

        new_seq_btn.grid(row=0, column=0, columnspan=2, sticky="n", padx=10, pady=(20,10))

        regions_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(20,10))
        regions_frame.grid_columnconfigure(0, weight=1)
        regions_frame.grid_rowconfigure(0, weight=1)

        # regions_frame.grid_rowconfigure(0,weight=1)

        items_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=20)
        items_frame.grid_columnconfigure(0, weight=1)
        # btnframe.grid_rowconfigure(0, weight=1)
        # items_frame.grid_rowconfigure(0, weight=1)



# def main():
#     root = ctk.CTk()
#     ctk.set_appearance_mode("Dark")
#     root.title("Real-time Video Feed")

#     global part_name
#     # FIXME: HARD CODED PART SELECTION
#     part_name = "Parta"
#     r = requests.post('http://127.0.0.1:5000/get_part_id', json={"part_name": part_name})

#     annot_frame = tk.Frame()
#     regions_frame = ctk.CTkScrollableFrame(master=root, width = 700)
#     items_frame = ctk.CTkFrame(master = root)

#     global item_list, new_seq_btn
#     r = requests.get('http://127.0.0.1:5000/get_items').json()
#     if r['status_code'] != 200:
#         item_list = []
#     else:
#         item_list = r['result']

#     # Creating a frame for item list
#     btnframe = ScrollableLabelButtonFrame(master=items_frame, root = root, width=500, corner_radius=0, height=540)
#     btnframe.grid(row=0, column=4, padx=0, pady=0, sticky="nsew")

#     global new_seq_btn
#     new_seq_btn = ctk.CTkButton(regions_frame, text="Add New Region", state=ctk.DISABLED if len(item_list) == 0 else ctk.NORMAL, command=lambda: add_item(sortable_list))
    
#     global lock_last_elem
#     lock_last_elem = False

#     # Making it global so that ALL the dropdown values can be updated when a new item is added 
#     global sortable_list
#     sortable_list = DDListWithLabels(regions_frame, root, 650, 50, offset_x=10, offset_y=10, gap=10, item_borderwidth=1, item_relief="groove")

#     sortable_list.grid(row=1, column=0, columnspan=2, sticky="news")
    
#     r = requests.post('http://127.0.0.1:5000/get_sequence', json={"part_name": part_name}).json()
#     if r['status_code'] == 200:
#         curr_seq = r['result']
#         parent_order = r['parent_order']
#         for seq in curr_seq:
#             add_item(sortable_list, seq)
#         idx = 0
#         for widget in sortable_list._list_of_items:
#             widget.modify_value(parent_order[idx])
#             idx+=1

#     new_seq_btn.grid(row=0, column=0, columnspan=2, sticky="n", padx=10, pady=(20,10))

#     regions_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
#     items_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
#     items_frame.update()
#     root.mainloop()

# if __name__ == "__main__":
#     main()
