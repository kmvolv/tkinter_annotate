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

class Scrolling_Area(Frame, object):

    def __init__(self, master, width=None, anchor=N, height=None, mousewheel_speed = 2, scroll_horizontally=True, xscrollbar=None, scroll_vertically=True, yscrollbar=None, outer_background=None, inner_frame=Frame, **kw):
        Frame.__init__(self, master, class_=self.__class__)

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

class Cell(Frame):
    """Base class for cells"""

class Data_Cell(Cell):
    def __init__(self, master, variable, anchor=W, bordercolor=None, borderwidth=1, padx=0, pady=0, background=None, foreground=None, font=None):
        Cell.__init__(self, master, background=background, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=borderwidth, bd= 0)

        self._message_widget = Message(self, textvariable=variable, font=font, background=background, foreground=foreground)
        self._message_widget.pack(expand=True, padx=padx, pady=pady, anchor=anchor)

class Header_Cell(Cell):
    def __init__(self, master, text, bordercolor=None, borderwidth=1, padx=0, pady=0, background=None, foreground=None, font=None, anchor=CENTER, separator=True):
        Cell.__init__(self, master, background=background, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=borderwidth, bd= 0)
        self.pack_propagate(False)

        self._header_label = Label(self, text=text, background=background, foreground=foreground, font=font)
        self._header_label.pack(padx=padx, pady=pady, expand=True)

        if separator and bordercolor is not None:
            separator = Frame(self, height=2, background=bordercolor, bd=0, highlightthickness=0, class_="Separator")
            separator.pack(fill=X, anchor=anchor)

        self.update()
        height = self._header_label.winfo_reqheight() + 2*padx
        width = self._header_label.winfo_reqwidth() + 2*pady

        self.configure(height=height, width=width)
        
class Table(Frame):
    def __init__(self, master, columns, column_weights=None, column_minwidths=None, height=500, minwidth=20, minheight=20, padx=5, pady=5, cell_font=None, cell_foreground="black", cell_background="white", cell_anchor=W, header_font=None, header_background="white", header_foreground="black", header_anchor=CENTER, bordercolor = "#999999", innerborder=True, outerborder=True, stripped_rows=("#EEEEEE", "white"), on_change_data=None, mousewheel_speed = 2, scroll_horizontally=False, scroll_vertically=True):
        outerborder_width = 1 if outerborder else 0

        Frame.__init__(self,master, bd= 0)

        self._cell_background = cell_background
        self._cell_foreground = cell_foreground
        self._cell_font = cell_font
        self._cell_anchor = cell_anchor
        
        self._stripped_rows = stripped_rows

        self._padx = padx
        self._pady = pady
        
        self._bordercolor = bordercolor
        self._innerborder_width = 1 if innerborder else 0

        self._data_vars = []

        self._columns = columns
        
        self._number_of_rows = 0
        self._number_of_columns = len(columns)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._head = Frame(self, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
        self._head.grid(row=0, column=0, sticky=E+W)

        header_separator = False if outerborder else True

        for j in range(len(columns)):
            column_name = columns[j]

            header_cell = Header_Cell(self._head, text=column_name, borderwidth=self._innerborder_width, font=header_font, background=header_background, foreground=header_foreground, padx=padx, pady=pady, bordercolor=bordercolor, anchor=header_anchor, separator=header_separator)
            header_cell.grid(row=0, column=j, sticky=N+E+W+S)

        add_scrollbars = scroll_horizontally or scroll_vertically
        if add_scrollbars:
            if scroll_horizontally:
                xscrollbar = Scrollbar(self, orient=HORIZONTAL)
                xscrollbar.grid(row=2, column=0, sticky=E+W)
            else:
                xscrollbar = None

            if scroll_vertically:
                yscrollbar = Scrollbar(self, orient=VERTICAL)
                yscrollbar.grid(row=1, column=1, sticky=N+S)
            else:
                yscrollbar = None

            scrolling_area = Scrolling_Area(self, width=self._head.winfo_reqwidth(), height=height, scroll_horizontally=scroll_horizontally, xscrollbar=xscrollbar, scroll_vertically=scroll_vertically, yscrollbar=yscrollbar)
            scrolling_area.grid(row=1, column=0, sticky=E+W)

            self._body = Frame(scrolling_area.innerframe, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
            self._body.pack()
            
            def on_change_data():
                scrolling_area.update_viewport()

        else:
            self._body = Frame(self, height=height, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
            self._body.grid(row=1, column=0, sticky=N+E+W+S)

        if column_weights is None:
            for j in range(len(columns)):
                self._body.grid_columnconfigure(j, weight=1)
        else:
            for j, weight in enumerate(column_weights):
                self._body.grid_columnconfigure(j, weight=weight)

        if column_minwidths is not None:
            for j, minwidth in enumerate(column_minwidths):
                if minwidth is None:
                    header_cell = self._head.grid_slaves(row=0, column=j)[0]
                    minwidth = header_cell.winfo_reqwidth()

                self._body.grid_columnconfigure(j, minsize=minwidth)
        else:
            for j in range(len(columns)):
                header_cell = self._head.grid_slaves(row=0, column=j)[0]
                minwidth = header_cell.winfo_reqwidth()

                self._body.grid_columnconfigure(j, minsize=minwidth)

        self._on_change_data = on_change_data

    def _append_n_rows(self, n):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns

        global item_list

        # def coolfunc(idx):
        #     print(item_list)
        #     print("this is idx", idx)
        #     del item_list[idx]

        for i in range(number_of_rows, number_of_rows+n):
            list_of_vars = []
            for j in range(number_of_columns):
                var = StringVar()
                list_of_vars.append(var)

                if self._stripped_rows:
                    cell = Data_Cell(self._body, borderwidth=self._innerborder_width, variable=var, bordercolor=self._bordercolor, padx=self._padx, pady=self._pady, background=self._stripped_rows[i%2], foreground=self._cell_foreground, font=self._cell_font, anchor=self._cell_anchor)
                else:
                    cell = Data_Cell(self._body, borderwidth=self._innerborder_width, variable=var, bordercolor=self._bordercolor, padx=self._padx, pady=self._pady, background=self._cell_background, foreground=self._cell_foreground, font=self._cell_font, anchor=self._cell_anchor)

                cell.grid(row=i, column=j, sticky=N+E+W+S)
            # print("This is the value of i : ", i)
            # del_box = ctk.CTkButton(self._body, text="Del", command= lambda idx=i: coolfunc(idx))
            # del_box.grid(row=i, column=number_of_columns, sticky=N+E+W+S)
            self._data_vars.append(list_of_vars)
            
        if number_of_rows == 0:
            for j in range(self.number_of_columns):
                header_cell = self._head.grid_slaves(row=0, column=j)[0]
                data_cell = self._body.grid_slaves(row=0, column=j)[0]
                data_cell.bind("<Configure>", lambda event, header_cell=header_cell: header_cell.configure(width=event.width), add="+")

        self._number_of_rows += n

    def _pop_n_rows(self, n):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns
        
        for i in range(number_of_rows-n, number_of_rows):
            for j in range(number_of_columns):
                self._body.grid_slaves(row=i, column=j)[0].destroy()
            
            self._data_vars.pop()
    
        self._number_of_rows -= n

    def set_data(self, data):
        n = len(data)
        m = len(data[0])

        number_of_rows = self._number_of_rows

        if number_of_rows > n:
            self._pop_n_rows(number_of_rows-n)
        elif number_of_rows < n:
            self._append_n_rows(n-number_of_rows)

        for i in range(n):
            for j in range(m):
                self._data_vars[i][j].set(data[i][j])

        if self._on_change_data is not None: self._on_change_data()

    def get_data(self):
        number_of_rows = self._number_of_rows
        number_of_columns = self.number_of_columns
        
        data = []
        for i in range(number_of_rows):
            row = []
            row_of_vars = self._data_vars[i]
            for j in range(number_of_columns):
                cell_data = row_of_vars[j].get()
                row.append(cell_data)
            
            data.append(row)
        return data

    @property
    def number_of_rows(self):
        return self._number_of_rows

    @property
    def number_of_columns(self):
        return self._number_of_columns

    def row(self, index, data=None):
        if data is None:
            row = []
            row_of_vars = self._data_vars[index]

            for j in range(self.number_of_columns):
                row.append(row_of_vars[j].get())
                
            return row
        else:
            number_of_columns = self.number_of_columns
            
            if len(data) != number_of_columns:
                raise ValueError("data has no %d elements: %s"%(number_of_columns, data))

            row_of_vars = self._data_vars[index]
            for j in range(number_of_columns):
                row_of_vars[index][j].set(data[j])
                
            if self._on_change_data is not None: self._on_change_data()

    def column(self, index, data=None):
        number_of_rows = self._number_of_rows

        if data is None:
            column= []

            for i in range(number_of_rows):
                column.append(self._data_vars[i][index].get())
                
            return column
        else:      
            number_of_columns = self.number_of_columns

            if len(data) != number_of_rows:
                raise ValueError("data has no %d elements: %s"%(number_of_rows, data))

            for i in range(number_of_columns):
                self._data_vars[i][index].set(data[i])

            if self._on_change_data is not None: self._on_change_data()

    def clear(self):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns

        for i in range(number_of_rows):
            for j in range(number_of_columns):
                self._data_vars[i][j].set("")

        if self._on_change_data is not None: self._on_change_data()

    def delete_row(self, index):
        i = index

        while i < self._number_of_rows:
            row_of_vars_1 = self._data_vars[i]
            row_of_vars_2 = self._data_vars[i+1]
            
            j = 0
            while j <self.number_of_columns:
                row_of_vars_1[j].set(row_of_vars_2[j])

            i += 1

        self._pop_n_rows(1)

        if self._on_change_data is not None: self._on_change_data()

    def insert_row(self, data, index=END):
        self._append_n_rows(1)

        if index == END:
            index = self._number_of_rows - 1
        
        i = self._number_of_rows-1
        while i > index:
            row_of_vars_1 = self._data_vars[i-1]
            row_of_vars_2 = self._data_vars[i]

            j = 0
            while j < self.number_of_columns:
                row_of_vars_2[j].set(row_of_vars_1[j])
                j += 1
            i -= 1

        list_of_cell_vars = self._data_vars[index]
        for cell_var, cell_data in zip(list_of_cell_vars, data):
            cell_var.set(cell_data)

        if self._on_change_data is not None: self._on_change_data()

    def cell(self, row, column, data=None):
        """Get the value of a table cell"""
        if data is None:
            return self._data_vars[row][column].get()
        else:
            self._data_vars[row][column].set(data)
            if self._on_change_data is not None: self._on_change_data()

    def __getitem__(self, index):
        if isinstance(index, tuple):
            row, column = index
            return self.cell(row, column)
        else:
            raise Exception("Row and column indices are required")
        
    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            row, column = index
            self.cell(row, column, value)
        else:
            raise Exception("Row and column indices are required")

    def on_change_data(self, callback):
        self._on_change_data = callback

class DeletableTable(Table):
    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns, **kwargs)
        self._add_delete_buttons()

    def _add_delete_buttons(self):
        for i in range(self.number_of_rows):
            delete_button = tk.Button(self._body, text="Delete", command=lambda i=i: self._delete_row(i))
            delete_button.grid(row=i, column=self.number_of_columns, padx=5, pady=2)
            self._body.grid_columnconfigure(self.number_of_columns, minsize=60)  # Adjust column width

    def _delete_row(self, index):
        result = tk.messagebox.askquestion("Delete Row", "Are you sure you want to delete this row?", icon='warning')
        if result == 'yes':
            self.delete_row(index)
            self._refresh_delete_buttons()

    def _refresh_delete_buttons(self):
        for widget in self._body.winfo_children():
            widget.grid_forget()
        self._add_delete_buttons()
        self.set_data(self.get_data())  # Refresh table data

# Python 3 support
basestring = str

class Item(Frame):
    def __init__(self, master, value, width, height, selection_handler=None, drag_handler = None, drop_handler=None, **kwargs):

        kwargs.setdefault("class_", "Item")
        Frame.__init__(self, master, **kwargs)
        
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

        self.place(in_=container, x=x, y=y, width=self._width, height=self._height)

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

    # def delete_elem(self, event, idx):
    #     print("This is my idx", idx)
    #     print(self.__dict__)
    #     print("I delet")

    def _add_bindtag(self, widget):
        bindtags = widget.bindtags()
        if self._tag not in bindtags:
            widget.bindtags((self._tag,) + bindtags)

        

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

class DDList(Frame):
    def __init__(self, master, item_width, item_height, item_relief=None, item_background=None, item_borderwidth=None, offset_x=0, offset_y=0, gap=0, **kwargs):
        kwargs["width"] = item_width+offset_x*2
        kwargs["height"] = offset_y*2

        Frame.__init__(self, master, **kwargs)

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
        
        if self._item_relief is not None:
            kwargs.setdefault("relief", self._item_relief)
        
        if self._item_borderwidth is not None:
            kwargs.setdefault("borderwidth", self._item_borderwidth)
            
        if self._item_background is not None:
            kwargs.setdefault("background", self._item_background)

        item = Item(self.master, value, self._item_width, self._item_height, self._on_item_selected, self._on_item_dragged, self._on_item_dropped, **kwargs)   
        return item

    def configure_items(self, **kwargs):
        for item in self._list_of_items:
            item.configure(**kwargs)

    def add_item(self, item, index=None):
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

class DDListWithLabels(DDList):
    def __init__(self, master, item_width, item_height, **kwargs):
        super().__init__(master, item_width, item_height, **kwargs)

    def create_item(self, value=None, **kwargs):
        item = super().create_item(value, **kwargs)
        self.add_labels_and_dropdown(item)
        # delete_icon = tk.PhotoImage(file="./bin.png")  
        # delete_button = tk.Button(item, image=delete_icon, command=lambda row=item: self.delete_row(row))
        # delete_button.image = delete_icon
        # delete_button.pack(side="right")
        return item

    def delete_row(self, row):
        row_index = self._position[row]
        self.delete_item(row_index)

    def add_labels_and_dropdown(self, item):
        combo_items = tk.Label(item, text="Items", font=('Calibri 10'))
        combo_items.pack(side="left")
        combo = tk.ttk.Combobox(item, state="readonly", values=["Python", "C++", "The rest..."])
        combo.pack(side="left", padx=5, expand = True)

        # thresh_label = tk.Label(item, text="Threshold", font=('Calibri 10'))
        # thresh_label.pack(side="left")
        # thresh = tk.Entry(item, width=10)
        # thresh.pack(side="left", padx=5, expand = True)

        qty_label = tk.Label(item, text="Quantity", font=('Calibri 10'))
        qty_label.pack(side="left")
        qty = tk.Entry(item, width=10)
        qty.pack(side="left", padx=5, expand = True)

        cool_button = ctk.CTkButton(item, text="Set Regions", command=lambda: tk.messagebox.showerror("ALERT!", "This is WIP!"))
        cool_button.pack(side="left", padx=5, expand = True)
        
        image_label = tk.Label(item)
        image_label.pack(side="left", padx=5, expand = True)
        image_label.tag = "hamburger"

        image = Image.open("./hamburger.png").resize((15, 15))
        photo = ImageTk.PhotoImage(image=image)
        image_label.config(image=photo)
        image_label.image = photo

        # del_label = tk.Label(item)
        # del_label.pack(side="left", padx=5)
        # del_label.tag = "bin"

        # del_image = Image.open("./bin.png").resize((15, 15))
        # photo = ImageTk.PhotoImage(image=del_image)
        # del_label.config(image=photo)
        # del_label.image = photo

        delete_img = Image.open("./bin.png").resize((15, 15))
        delete_icon = ImageTk.PhotoImage(image=delete_img)
        delete_button = tk.Button(item, image = delete_icon, command = lambda row = item: self.delete_row(row))
        delete_button.image = delete_icon
        delete_button.pack(side="left")

        # label1 = tk.Label(item, text=self._label_text_1)
        # label1.pack(anchor=tk.W, padx=(4, 0), pady=(4, 0))

        # label2 = tk.Label(item, text=self._label_text_2)
        # label2.pack(anchor=tk.W, padx=(4, 0))

        # combo = tk.ttk.Combobox(item, state="readonly", values=self._dropdown_values)
        # combo.pack(anchor=tk.W, padx=(4, 0), pady=(0, 4))

class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, root, command=None, **kwargs):
        
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        label1 = ctk.CTkLabel(self, text="Item", padx=5, anchor="center")
        label2 = ctk.CTkLabel(self, text="Threshold", padx=5, anchor="w")
        label1.grid(row=1, column=0, pady=(0, 10), sticky="nsew")
        label2.grid(row=1, column=1, pady=(0, 10), sticky="w")

        self.root = root
        self.command = command

        self.label1_list = []  # List to store the first label in each row
        self.label2_list = []  # List to store the second label in each row
        self.button1_list = []  # List to store the first button in each row
        self.button2_list = []  # List to store the second button in each row
        
        # self.label1_list.append(label1)
        # self.label2_list.append(label2)

        add_itm = ctk.CTkButton(self,text="Add New Item", width=100, height=24,command = self.open_popup)
        add_itm.grid(row=0, column=2, padx=5, pady=10)

        del_itm = ctk.CTkButton(self,text="Delete Item", width=100, height=24,command = self.remove_item)
        del_itm.grid(row=0, column=3, padx=5, pady=10)

    def open_popup(self):
        global item_list

        popup = tk.Toplevel(self.root)
        popup.title("Enter Values")
        popup.grab_set()

        label_item = tk.ttk.Label(popup, text="Item:")
        label_thresh = tk.ttk.Label(popup, text="Threshold:")
        label_item.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        label_thresh.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        entry_item = tk.ttk.Entry(popup)
        entry_thresh = tk.ttk.Entry(popup)
        entry_item.grid(row=0, column=1, padx=10, pady=5)
        entry_thresh.grid(row=1, column=1, padx=10, pady=5)

        def add_new_item():
            global item_list 
            value_item = entry_item.get()
            value_thresh = entry_thresh.get()

            item_list.append((value_item, value_thresh))
            popup.destroy()

            # table.insert_row([value_item, value_thresh])
            self.add_item(value_item, value_thresh)

        popup.bind("<Return>", lambda event: add_new_item())
        ok_button = ctk.CTkButton(popup, text="OK", command=add_new_item)
        ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    def add_item(self, item1, item2):
        print(item1, item2)
        label1 = ctk.CTkLabel(self, text=item1, padx=5, anchor="w")
        label2 = ctk.CTkLabel(self, text=item2, padx=5, anchor="w")

        row = len(self.label1_list) + 2  # Start from row 1 for data rows
        
        label1.grid(row=row, column=0, pady=(0, 10))
        label2.grid(row=row, column=1, pady=(0, 10))
    
        button1 = ctk.CTkButton(self, text="Edit", width=100, height=24)
        button2 = ctk.CTkButton(self, text="Delete", width=100, height=24, command=lambda item=item1: self.remove_item(item1))
        if self.command is not None:
            button1.configure(command=lambda: self.command(item1, "Edit"))
            button2.configure(command=lambda: self.command(item1, "Delete"))
        button1.grid(row=row, column=2, pady=(0, 10), padx=5)
        button2.grid(row=row, column=3, pady=(0, 10), padx=5)
        self.button1_list.append(button1)
        self.button2_list.append(button2)

        self.label1_list.append(label1)
        self.label2_list.append(label2)

    def remove_item(self, item1):
        for label1, label2, button1, button2 in zip(self.label1_list, self.label2_list, self.button1_list, self.button2_list):
            if item1 == label1.cget("text"):
                print(item1, " is removed : ) ")
                label1.destroy()
                label2.destroy()
                button1.destroy()
                button2.destroy()
                self.label1_list.remove(label1)
                self.label2_list.remove(label2)
                self.button1_list.remove(button1)
                self.button2_list.remove(button2)
                return

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480

# Replace this with your streaming http response logic
# For this example, I'll use a static image

# ======================== HELPER FUNCTIONS ========================
def get_realtime_image():
    return Image.open("./a.jpg")  # Replace with your image source

def draw_box(canvas, x1, y1, x2, y2):
    # Draw a semi-transparent box on the canvas
    canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="blue", stipple="gray25")

def draw_saved_boxes(coordinates_list,canvas):
    # Logic to draw saved boxes with some color
    # Here, you can draw rectangles using the coordinates list and a specific color
    for coords in coordinates_list:
        x1, y1, x2, y2 = coords
        draw_box(canvas, x1, y1, x2, y2)

def check_overlap(coordinates_list, last_coords, mybox):
        # Logic to check if the box is overlapping with any other drawn box
        for coord in coordinates_list:
            # print("This is box cord : ", coord)
            # print("This is the last coord : ", last_coords)
            if(coord == last_coords):
                continue

            x1, y1, x2, y2 = coord
            if mybox[0] < x2 and mybox[1] < y2 and mybox[2] > x1 and mybox[3] > y1:
                return True
            
        return False

def add_item(sortable_list):
    index = len(sortable_list._list_of_items)
    item = sortable_list.create_item(value = index)
    sortable_list.add_item(item)

def main():
    root = ctk.CTk()
    ctk.set_appearance_mode("Dark")
    root.title("Real-time Video Feed")

    annot_frame = tk.Frame()
    regions_frame = ctk.CTkScrollableFrame(master=root, width = 700)
    items_frame = ctk.CTkFrame(master = root)

    global item_list
    item_list = []

    # Create a button to add a new item
    # cool = ItemTable(master = items_frame, root = root, width=500, corner_radius=10)
    btnframe = ScrollableLabelButtonFrame(master=items_frame, root = root, width=500, corner_radius=0, height=540)
    btnframe.grid(row=0, column=4, padx=0, pady=0, sticky="nsew")


    for i in range(len(item_list)):  # add items with images
        print("Im cool")
        btnframe.add_item(f"image and item {i}", "BObo")


    # add_button = ctk.CTkButton(items_frame, text="Add New Item")
    # add_button.pack(pady=(20,10), padx=10)
    # table = DeletableTable(master = items_frame, columns = ["Item", "Threshold", "Dumbo"])
    # data = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [15, 16, 18], [19, 20, 21]]
    # table.set_data(data)

    # add_button = ctk.CTkButton(items_frame, text="Add New Item", command = lambda table=table: open_popup(table))
    # add_button.pack(pady=(20,10), padx=10)

    # lol = ctk.CTkButton(items_frame, text="Del", command = lambda: table.delete_row(1))
    # lol.pack(pady=(20,10), padx=10)

    # table.pack(padx=10, pady = 10, fill=tk.BOTH, anchor=tk.CENTER)

    print(item_list)
    # table = ctk.CTkTable(master=items_frame, row =2, column=2, values=dum_vals)
    # table.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # sortable_list = DDList(regions_frame, 200, 100, offset_x=10, offset_y=10, gap =10, item_borderwidth=1, item_relief="groove")
    sortable_list = DDListWithLabels(regions_frame, 650, 50, offset_x=10, offset_y=10, gap=10, item_borderwidth=1, item_relief="groove")
    # sortable_list.pack(expand=True, fill=tk.BOTH)
    sortable_list.grid(row=1, column=0, columnspan=2, sticky="news")
    
    # ctk.CTkButton(regions_frame, text="Add New Region", command=lambda lst=sortable_list: add_item(sortable_list)).pack(side=tk.LEFT, padx=(3,0))
    ctk.CTkButton(regions_frame, text="Add New Region", command=lambda lst=sortable_list: add_item(sortable_list)).grid(row=0, column=0, columnspan=2, sticky="n", padx=10, pady=(20,10))

    # Create a sub-frame to hold the widgets in a row
    def create_row(regions_frame):
        widget_row = tk.Frame(regions_frame, bg="light grey", padx=10, pady=10)
        widget_row.pack(fill="x", padx=10, pady=5)

        combo_items = tk.Label(widget_row, text="Items", font=('Calibri 10'))
        combo_items.pack(side="left")
        combo = tk.ttk.Combobox(widget_row, state="readonly", values=["Python", "Python", "ONLY PYTHON"])
        combo.pack(side="left", padx=5)

        thresh_label = tk.Label(widget_row, text="Threshold", font=('Calibri 10'))
        thresh_label.pack(side="left")
        thresh = tk.Entry(widget_row, width=10)
        thresh.pack(side="left", padx=5)

        qty_label = tk.Label(widget_row, text="Quantity", font=('Calibri 10'))
        qty_label.pack(side="left")
        qty = tk.Entry(widget_row, width=10)
        qty.pack(side="left", padx=5)

        cool_button = ctk.CTkButton(widget_row, text="Set Regions", command=lambda: tk.messagebox.showerror("ALERT!", "This is WIP!"))
        cool_button.pack(side="left", padx=5)
        
        image_label = tk.Label(widget_row)
        image_label.pack(side="left", padx=5)

        image = Image.open("./hamburger.png").resize((15, 15))
        photo = ImageTk.PhotoImage(image=image)
        image_label.config(image=photo)
        image_label.image = photo

        # image_label.bind("<Button-1>", lambda event: start_drag(event, image_label))
        # image_label.bind("<B1-Motion>", lambda event: on_drag(event, image_label))
        # image_label.bind("<ButtonRelease-1>", lambda event: end_drag(event, image_label))

        return widget_row
        # photoimage = ImageTk.PhotoImage(image="hamburger.png")
        # canvas.create_image(20, 20, image=photoimage)

        # image = Image.open("./hamburger.png")
        # image = image.resize((20, 20))
        # photo = ImageTk.PhotoImage(image)

        # image_label = tk.Label(widget_row, image=photo)
        # image_label.image = photo  # Keep a reference to the PhotoImage to prevent garbage collection
        # image_label.pack(side="left", padx=5)
        
    # for i in range(3):
    #     item = sortable_list.create_item(value = i)
    #     # label = tk.Label(item, text=f"this is the label {i}")
    #     # label.pack(anchor=tk.W, padx=(4,0), pady=(4,0))
    #     # get values from entry fields

    #     sortable_list.add_item(item)
    #     print("This is the length of the list : ", len(sortable_list._list_of_items))

    # frame = Frame(root)
    # frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
    
    # indexVar = tk.IntVar()
    # label = tk.Label(frame, text="Entry index of item to delete:")
    # label.pack(side=tk.LEFT, padx=(10,6))
    # entry_of_index = tk.Entry(frame,textvariable= indexVar, width=3)
    
    # def delete_item():
    #     try:
    #         index = indexVar.get()
    #     except ValueError:
    #         tk.messagebox.showerror("Error", "Not a valid integer")
    #         return

    #     entry_of_index.delete(0, tk.END)
    #     sortable_list.delete_item(index)
    # entry_of_index.bind('<Return>', delete_item)

    # entry_of_index.pack(side=tk.LEFT)
    
    # ctk.CTkButton(frame, text="Delete", command=delete_item).pack(side=tk.LEFT, padx=(3,0))


    global coordinates_list, selected_box, selected_resize_handle, start_x, start_y, box_to_delete
    coordinates_list = []
    selected_box = None
    box_to_delete = None
    selected_resize_handle = None
    start_x = 0
    start_y = 0

    canvas = tk.Canvas(master=annot_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack()
    
    #v2 - box + drag if already exist

    # def add_row(info_list):
    #     row_frame = tk.Frame(regions_frame)
    #     for info in info_list:
    #         label = tk.Label(row_frame, text=info, borderwidth=1, relief="solid")
    #         label.pack(side="left")
    #     row_frame.pack(fill="x", padx=10, pady=5)

    # data = [
    #     ["Name", "Age", "Country"],
    #     ["John", "25", "USA"],
    #     ["Emily", "30", "Canada"],
    #     ["Michael", "22", "Australia"],
    #     ["Sophia", "28", "UK"]
    # ]

    # for row_data in data:
    #     add_row(row_data)

    # ============================ CANVAS HELPER FUNCTIONS ============================ 
    def draw_rectangle(canvas, x1, y1, x2, y2, **kwargs):
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def delete_selected_box(box_to_delete, coordinates_list):
        if not coordinates_list:
            tk.messagebox.showerror("WARNING","There are no more boxes to delete")
            return
        
        try:
            print("I want to delete this box : ")
            print(box_to_delete)
            print(" ========================== ")
            canvas.delete(box_to_delete[0])
            coordinates_list.remove(box_to_delete[1])
        except:
            tk.messagebox.showerror("WARNING","You haven't selected any box")

    def reset_boxes():
        global coordinates_list, box_to_delete
        for box in canvas.find_withtag("user_box"):
            canvas.delete(box)

        box_to_delete = None
        coordinates_list = []

    # ============================ EVENT HANDLING FUNCTIONS ============================ 
    def on_lmb_press(event):
        global start_x, start_y, selected_box, selected_box_offset_x, selected_box_offset_y, selected_box_width, selected_box_height, last_coords, last_click, box_to_delete
        
        last_click = (event.x, event.y)

        for box in canvas.find_withtag("user_box"):
            x1, y1, x2, y2 = canvas.coords(box)
            if x1 < event.x < x2 and y1 < event.y < y2:
                # Inside an existing box, enable dragging
                selected_box = box
                selected_box_offset_x = event.x - x1
                selected_box_offset_y = event.y - y1

                selected_box_width = x2 - x1
                selected_box_height = y2 - y1

                last_coords = (min(x1, x1 + selected_box_width), y1, max(x1, x1 + selected_box_width), y1 + selected_box_height)
                break
        else:
            # Not inside an existing box, start drawing a new rectangle
            canvas.itemconfig(selected_box, fill="green")
            start_x = event.x
            selected_box = None
            start_y = event.y
            canvas.delete("temp_box")
            canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="blue", width=2, tags="temp_box")

    def on_lmb_drag(event):
        if selected_box:
            # Move the selected box if it exists
            x = event.x - selected_box_offset_x
            y = event.y - selected_box_offset_y
            x1, y1, x2, y2 = canvas.coords(selected_box)
            canvas.coords(selected_box, x, y, x + (x2 - x1), y + (y2 - y1))
        else:
            # Update the temporary rectangle while the user is drawing
            canvas.coords("temp_box", start_x, start_y, event.x, event.y)

    def on_lmb_release(event):
        global selected_box, last_coords, last_click, box_to_delete
        # print("On click, this was my cords : ", last_click)
        # print("On clicking, this is my cord : ", (event.x, event.y))

        print("This is the selected box : ", selected_box)

        if not selected_box:
            print("No selected box")
            # No selected box, so all boxes should have green fill :
            try:
                canvas.itemconfig(box_to_delete[0], fill = "green")
            except:
                pass
            
            print("No BOX SELECTED!")

            if(abs(last_click[0] - event.x) <= 2 and abs(last_click[1] - event.y) <= 2):
                print("I am setting selected box to none : )")
                box_to_delete = None

            # Draw the final rectangle if the user was drawing a new one
            x0, y0 = start_x, start_y
            x1, y1 = event.x, event.y

            min_width = 5
            min_height = 5

            # Check Overflow
            if abs(x1-x0) < min_width or abs(y1-y0) < min_height or (x1 >= IMG_WIDTH or x1 < 0) or (y1 >= IMG_HEIGHT or y1 < 0) or (x0 >= IMG_WIDTH or x0 < 0) or (y0 >= IMG_HEIGHT or y0 < 0):
                pass
            # Checking for overlap
            elif check_overlap(coordinates_list, (-1,-1,-1,-1), (min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1))):
                pass
            else:
                last_coords = (x0, y0, x1, y1)
                draw_rectangle(canvas, x0, y0, x1, y1, outline="blue", width=2, fill="green",stipple="gray25",tags="user_box")
                coordinates_list.append((min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)))
        else:
            # This means that the user is trying to SELECT a box, and not drag it
            print("I weant to selecta box :")
            if(abs(last_click[0] - event.x) == 0 and abs(last_click[1] - event.y) == 0):
                if selected_box:
                    try:
                        canvas.itemconfig(box_to_delete[0], fill = "green")
                    except:
                        pass

                    cursor_x, cursor_y = event.x, event.y

                    x0 = cursor_x - selected_box_offset_x
                    y0 = cursor_y - selected_box_offset_y

                    x1 = x0 + selected_box_width
                    y1 = y0 + selected_box_height
                    box_to_delete = [selected_box,(x0,y0,x1,y1)]

            # User is DRAGGING the box     
            else:
                print("I am dragging the box ")
                cursor_x, cursor_y = event.x, event.y
                
                x0 = cursor_x - selected_box_offset_x
                y0 = cursor_y - selected_box_offset_y

                x1 = x0 + selected_box_width
                y1 = y0 + selected_box_height

                # Checking for boundary exceeded
                if(x0 < 0 or x1 > IMG_WIDTH or y0 < 0 or y1 > IMG_HEIGHT):
                    print("Boundary exceeded!")
                    # Restore previous state
                    canvas.coords(selected_box, last_coords[0], last_coords[1], last_coords[2], last_coords[3])
                # Checking for overlap
                elif(check_overlap(coordinates_list, last_coords, (x0, y0, x1, y1))):
                    print("Overlap detected!")
                    # Restore previous state
                    canvas.coords(selected_box, last_coords[0], last_coords[1], last_coords[2], last_coords[3])
                else:
                    # Update new coordinates after drag and drop
                    print("I need to delete this cord : ", last_coords)
                    try:
                        del coordinates_list[coordinates_list.index(last_coords)]
                    except:
                        print("I couldn't delete this cord")
                        pass
                    else:
                        if box_to_delete:
                            if box_to_delete[1] == last_coords:
                                box_to_delete[1] = (x0, y0, x1, y1)
                        coordinates_list.append((x0, y0, x1, y1))


        selected_box = None
        try:
            canvas.itemconfig(box_to_delete[0], fill = "red")
        except:
            pass
        canvas.delete("temp_box")

        # Fail-safe

        # coordinates_list = []
        for box in canvas.find_withtag("user_box"):
            print("OBHOBHOBOB BODXXXX")
            # print(canvas.coords(box))
            # coordinates_list.append(canvas.coords(box))

        print(coordinates_list)
        
    image = get_realtime_image()
    photo = ImageTk.PhotoImage(image=image)
    IMG_WIDTH = min(image.size[0], CANVAS_WIDTH)
    IMG_HEIGHT = min(image.size[1], CANVAS_HEIGHT)
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo

    remove_box_button = ctk.CTkButton(master=annot_frame, text="Delete Box", command=lambda: delete_selected_box(box_to_delete, coordinates_list))
    reset_button = ctk.CTkButton(master=annot_frame, text="Reset", command=lambda: reset_boxes())

    remove_box_button.pack()
    reset_button.pack()

    # Bind the mouse click event to the on_draw function
    canvas.bind("<ButtonPress-1>", on_lmb_press)
    canvas.bind("<B1-Motion>", on_lmb_drag)
    canvas.bind("<ButtonRelease-1>", on_lmb_release)

    regions_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    annot_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    items_frame.pack(expand = True, fill = tk.BOTH, side= tk.LEFT)
    items_frame.update()
    root.mainloop()

if __name__ == "__main__":
    main()
