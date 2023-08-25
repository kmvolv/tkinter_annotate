import tkinter as tk
from PIL import Image, ImageTk
import requests

# Replace this with your streaming http response logic
# For this example, I'll use a static image
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



def main():

    root = tk.Tk()
    root.title("Real-time Video Feed")

    global coordinates_list, selected_box, selected_resize_handle, start_x, start_y
    coordinates_list = []
    selected_box = None
    selected_resize_handle = None
    start_x = 0
    start_y = 0

    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()
    
    #v2 - box + drag if already exist

    def draw_rectangle(canvas, x1, y1, x2, y2, **kwargs):
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def on_button_press(event):
        global start_x, start_y, selected_box, selected_box_offset_x, selected_box_offset_y

        for box in canvas.find_withtag("user_box"):
            x1, y1, x2, y2 = canvas.coords(box)
            if x1 < event.x < x2 and y1 < event.y < y2:
                # Inside an existing box, enable dragging
                selected_box = box
                selected_box_offset_x = event.x - x1
                selected_box_offset_y = event.y - y1
                break
        else:
            # Not inside an existing box, start drawing a new rectangle
            selected_box = None
            start_x = event.x
            start_y = event.y
            canvas.delete("temp_box")
            canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="blue", width=2, tags="temp_box")

    def on_mouse_drag(event):
        if selected_box:
            # Move the selected box if it exists
            x = event.x - selected_box_offset_x
            y = event.y - selected_box_offset_y
            x1, y1, x2, y2 = canvas.coords(selected_box)
            canvas.coords(selected_box, x, y, x + (x2 - x1), y + (y2 - y1))
        else:
            # Update the temporary rectangle while the user is drawing
            canvas.coords("temp_box", start_x, start_y, event.x, event.y)

    def on_button_release(event):
        global selected_box
        if not selected_box:
            # Draw the final rectangle if the user was drawing a new one
            x0, y0 = start_x, start_y
            x1, y1 = event.x, event.y

            min_width = 5
            min_height = 5
            if abs(x1 - x0) >= min_width and abs(y1 - y0) >= min_height:
                draw_rectangle(canvas, x0, y0, x1, y1, outline="blue", width=2, fill="green",stipple="gray25",tags="user_box")
        selected_box = None
        canvas.delete("temp_box")
        # Save the coordinates of the rectangle

        
        
        print(coordinates_list)

        #check if box is in inside
        #r = requests.post('http://http:localhost:5000/check_bbox_inside_image', json={"current_bbox": (x0, y0, x1, y1), "image_width":})
        #if r.status_code != 200:
        #    print("nah ")

        coordinates_list.append((x0, y0, x1, y1))
        

        


    image = get_realtime_image()
    photo = ImageTk.PhotoImage(image=image)
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo


    # Bind the mouse click event to the on_draw function
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_button_release)


    root.mainloop()

if __name__ == "__main__":
    main()
