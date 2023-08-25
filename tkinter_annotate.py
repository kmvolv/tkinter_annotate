import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import requests

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


def main():

    root = tk.Tk()
    root.title("Real-time Video Feed")

    global coordinates_list, selected_box, selected_resize_handle, start_x, start_y, box_to_delete
    coordinates_list = []
    selected_box = None
    box_to_delete = None
    selected_resize_handle = None
    start_x = 0
    start_y = 0

    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    canvas.pack()
    
    #v2 - box + drag if already exist

    # ============================ CANVAS HELPER FUNCTIONS ============================ 
    def draw_rectangle(canvas, x1, y1, x2, y2, **kwargs):
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def make_all_green(canvas):
        for box in canvas.find_withtag("user_box"):
            canvas.itemconfig(box, fill="green")

    def delete_selected_box(box_to_delete, coordinates_list):
        if not coordinates_list:
            tk.messagebox.showerror("ARE YOU DUMB??","Hi you don't even have boxes to delete")
            return
        
        try:
            canvas.delete(box_to_delete[0])
            coordinates_list.remove(box_to_delete[1])
        except:
            tk.messagebox.showerror("ARE YOU DUMB??","You didn't even select a box dumbo")

    
    # ============================ EVENT HANDLING FUNCTIONS ============================ 
    def on_lmb_press(event):
        global start_x, start_y, selected_box, selected_box_offset_x, selected_box_offset_y, selected_box_width, selected_box_height, last_coords, last_click
        
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
            # No selected box, so all boxes should have green fill :
            try:
                canvas.itemconfig(box_to_delete[0], fill = "green")
            except:
                pass
            
            print("No BOX SELECTED!")

            if(abs(last_click[0] - event.x) <= 2 and abs(last_click[1] - event.y) <= 2):
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
            if(abs(last_click[0] - event.x) <= 2 and abs(last_click[1] - event.y) <= 2):
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
                        pass
                    coordinates_list.append((x0, y0, x1, y1))


        selected_box = None
        try:
            canvas.itemconfig(box_to_delete[0], fill = "red")
        except:
            pass
        canvas.delete("temp_box")
        print(coordinates_list)
        


    image = get_realtime_image()
    photo = ImageTk.PhotoImage(image=image)
    IMG_WIDTH = min(image.size[0], CANVAS_WIDTH)
    IMG_HEIGHT = min(image.size[1], CANVAS_HEIGHT)
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo

    remove_box_button = ctk.CTkButton(root, text="Delete Box", command=lambda: delete_selected_box(box_to_delete, coordinates_list))
    remove_box_button.pack()

    # Bind the mouse click event to the on_draw function
    canvas.bind("<ButtonPress-1>", on_lmb_press)
    canvas.bind("<B1-Motion>", on_lmb_drag)
    canvas.bind("<ButtonRelease-1>", on_lmb_release)

    root.mainloop()

if __name__ == "__main__":
    main()
