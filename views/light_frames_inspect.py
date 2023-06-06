import math
import os
from tkinter import  Tk
from utils.utils import calculateExposureTimes, formatExposureTime
from widgets.status_bar import StatusBar

import tkinter as tk
import numpy as np

from PIL import ImageTk, Image, ImageEnhance
from astropy.io import fits

class LightFramesInspectWindow(Tk):
    def __init__(self, objectPath:str, selectedObject:str, selectedDates:list):
        super().__init__()
        self.objectPath = objectPath
        self.selectedDates = selectedDates
        self.autostretchImage = tk.IntVar()
        self.currentImageIsBad = tk.IntVar()
        self.imageName = tk.StringVar()
        
        self.title("AstroGenie - Inspect light frames")
        self.geometry("1920x1080")
        self.iconbitmap("assets/icon.ico") # type: ignore

        self.topBar(self)

        totalLights, totalExposureTime, self.lightFramePaths = calculateExposureTimes(self.selectedDates, self.objectPath)
        self.textLeft = tk.StringVar()
        self.textRight = tk.StringVar()
        self.statusBar = StatusBar(self, selectedItem=selectedObject, path=objectPath, textLeft=self.textLeft, textRight=self.textRight)

        self.textLeft.set(f"Selected object {selectedObject} | Path: {objectPath}")
        self.textRight.set(f"Total lights: {totalLights} | Total exposure time: {formatExposureTime(totalExposureTime)}")

        self.listLightFrames(self.lightFramePaths)
        self.imageContainer()
        self.createImagePreview()
        self.showImagePreview(self)

    def proceedBtnClick(self):
        pass

    def markCurrentImage(self):
        selectedImage = len(self.lightFrames.curselection()) > 0 and self.lightFrames.get(self.lightFrames.curselection()[0]) or ""
        imagePath = ""

        for lightFrame in self.lightFramePaths:
            if selectedImage in lightFrame:
                imagePath = os.path.dirname(lightFrame)
                break

        if imagePath == "" or selectedImage == "":
            print("Error: Image and/or path not found!")
            return

        if self.currentImageIsBad.get() == 1:
            # If selectedImage doesn't start with "BAD_" add it
            if not selectedImage.startswith("BAD_"):
                print(f"Marking {selectedImage} as bad. {os.path.join(imagePath, selectedImage)} -> {os.path.join(imagePath, 'BAD_' + selectedImage)}")
                os.rename(os.path.join(imagePath, selectedImage), os.path.join(imagePath, f"BAD_{selectedImage}"))
        else:
            # If selectedImage starts with "BAD_" remove it
            if selectedImage.startswith("BAD_"):
                print(f"Marking {selectedImage} as good. {os.path.join(imagePath, selectedImage)} -> {os.path.join(imagePath, selectedImage[4:])}")
                os.rename(os.path.join(imagePath, selectedImage), os.path.join(imagePath, selectedImage[4:]))

        # Clear and reload light frames and select the previously selected image again
        self.lightFrames.delete(0, tk.END)

        totalLights, totalExposureTime, self.lightFramePaths = calculateExposureTimes(self.selectedDates, self.objectPath)
        for lightFrame in self.lightFramePaths:
            self.lightFrames.insert(tk.END, os.path.basename(lightFrame))

        for i in range(self.lightFrames.size()):
            if selectedImage in self.lightFrames.get(i):
                self.lightFrames.selection_set(i)
                break

        self.showImagePreview(self)
        pass

    def selectDifferentDatesBtnClick(self):
        self.destroy()

        # Split object path into path and object name
        objectPath, selectedObject = os.path.split(self.objectPath)
        import views.dates_select as dates_select
        dates_select.DatesSelectWindow(objectPath, selectedObject)
        pass

    def showImagePreview(self, event):
        image_path = ""
        selectedImage = len(self.lightFrames.curselection()) > 0 and self.lightFrames.get(self.lightFrames.curselection()[0]) or None

        if selectedImage == None:
            selectedImage = os.path.basename(self.lightFramePaths[0])

        for lightFrame in self.lightFramePaths:
            if selectedImage in lightFrame:
                image_path = lightFrame
                break

        self.imageName.set(selectedImage)
        if os.path.isfile(image_path):
            with fits.open(image_path) as hdul:
                image_data = hdul[0].data

            # Normalize the image data
            image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))

            # Apply an auto-stretch to enhance visibility
            if self.autostretchImage.get() == 1:
                p_low, p_high = np.percentile(image_data, (1, 99))  # Adjust the percentiles as needed
                image_data = np.clip((image_data - p_low) / (p_high - p_low), 0, 1)

            # Convert the image data to a PIL Image
            image = Image.fromarray(np.uint8(image_data * 255), 'L')

            # # Resize the image to 75 % its original size
            image = image.resize((int(image.width), int(image.height)), Image.BILINEAR)

            self.pil_image = image
            self.zoom_fit(self.pil_image.width, self.pil_image.height)
            self.draw_image(self.pil_image)

            self.label_image_info["text"] = f"{self.imageName.get()} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

            # Update image is bad checkbox based on file name suffix
            if "BAD_" in image_path: # TODO: Make this a setting that can be changed in the settings window
                self.currentImageIsBad.set(1)
            else:
                self.currentImageIsBad.set(0)

    def previous_image(self, event):
        index = self.lightFrames.curselection()[0] if self.lightFrames.curselection() != () else 0
        if index == 0:
            self.lightFrames.selection_set(self.lightFrames.size() - 1)
        else:
            self.lightFrames.selection_clear(index)
            self.lightFrames.selection_set(index - 1)
        self.showImagePreview(self)
        
    def next_image(self, event):
        index = self.lightFrames.curselection()[0] if self.lightFrames.curselection() != () else 0
        if index == self.lightFrames.size() - 1:
            self.lightFrames.selection_set(0)
        else:
            self.lightFrames.selection_clear(index)
            self.lightFrames.selection_set(index + 1)
        self.showImagePreview(self)
        
    def createImagePreview(self):
        frame_statusbar = tk.Frame(self.image_frame, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas fit the rest of the window
        self.canvas = tk.Canvas(self.image_frame, background="black")
        self.canvas.pack(expand=1, fill=tk.BOTH, side=tk.TOP)

        # Set the canvas dimensions to screen size
        self.canvas.config(width=self.winfo_screenwidth(), height=self.winfo_screenheight())

        self.canvas.bind("<Button-1>", self.mouse_down_left)
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)

        # Arrow keys for previous/next image
        self.bind("<Left>", self.previous_image)
        self.bind("<Right>", self.next_image)

    def mouse_down_left(self, event):
        self.__old_event = event

    def mouse_move_left(self, event):
        if (self.pil_image == None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        self.__old_event = event

    def mouse_move(self, event):
        if (self.pil_image == None):
            return
        
        image_point = self.to_image_point(event.x, event.y)
        if image_point != []:
            self.label_image_pixel["text"] = (f"({image_point[0]:.2f}, {image_point[1]:.2f})")
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouse_double_click_left(self, event):
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()

    def mouse_wheel(self, event):
        if self.pil_image == None:
            return

        if event.state != 9:
            if (event.delta < 0):
                self.scale_at(1.25, event.x, event.y)
            else:
                self.scale_at(0.8, event.x, event.y)
        else:
            if (event.delta < 0):
                self.rotate_at(-5, event.x, event.y)
            else:
                self.rotate_at(5, event.x, event.y)     
        self.redraw_image()
        
    def reset_transform(self):
        self.mat_affine = np.eye(3)

    def translate(self, offset_x, offset_y):
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def rotate(self, deg:float):
        mat = np.eye(3)
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def rotate_at(self, deg:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.rotate(deg)
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            scale = canvas_height / image_height
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            scale = canvas_width / image_width
            offsety = (canvas_height - image_height * scale) / 2

        self.scale(scale)
        self.translate(offsetx, offsety)

    def to_image_point(self, x, y):
        if self.pil_image == None:
            return []
        
        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.pil_image.width or image_point[1] > self.pil_image.height:
            return []

        return image_point

    def draw_image(self, pil_image):
        
        if pil_image == None:
            return

        self.pil_image = pil_image

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        mat_inv = np.linalg.inv(self.mat_affine)

        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
        )

        dst = self.pil_image.transform(
            (canvas_width, canvas_height),
            Image.AFFINE,
            affine_inv, 
            Image.BILINEAR,
        )

        im = ImageTk.PhotoImage(image=dst)

        item = self.canvas.create_image(
            0, 0,
            anchor='nw',
            image=im 
        )

        self.image = im

    def redraw_image(self):
        if self.pil_image == None:
            return
        
        self.draw_image(self.pil_image)

    def imageContainer(self):
        # Create a frame for the image preview
        self.image_frame = tk.Frame(self)
        button_frame = tk.Frame(self.image_frame)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        marker_checkbox = tk.Checkbutton(button_frame, text="Image is marked as bad", variable=self.currentImageIsBad, command=self.markCurrentImage)
        marker_checkbox.pack(side=tk.LEFT, padx=5)

        autostretchChk = tk.Checkbutton(button_frame, text="Autostretch", variable=self.autostretchImage, command=lambda: self.showImagePreview(self))
        autostretchChk.select()
        autostretchChk.pack(side=tk.LEFT, padx=5)

        openFrameInFolderBtn = tk.Button(button_frame, text="Open in folder", command=lambda: os.startfile(os.path.dirname(self.lightFramePaths[0])) if len(self.lightFramePaths) > 0 else None)
        openFrameInFolderBtn.pack(side=tk.LEFT, padx=5)
        
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        pass

    def topBar(self, window):
        self = tk.Frame(self, bd=1, relief=tk.SUNKEN)
        self.pack(side=tk.TOP, fill=tk.X)
        
        optionsFrame = tk.LabelFrame(self, text="Options")
        optionsFrame.pack(fill=tk.X, padx=8, pady=8, expand=1, side=tk.TOP)

        selectDifferentDatesBtn = tk.Button(optionsFrame, text="Select different dates", command=window.selectDifferentDatesBtnClick)
        selectDifferentDatesBtn.pack(fill=tk.Y, padx=8, pady=8, expand=0, side=tk.LEFT)

        calibrationFramesBtn = tk.Button(optionsFrame, text="Select calibration frames", command=window.proceedBtnClick)
        calibrationFramesBtn.pack(fill=tk.Y, padx=8, pady=8, expand=0, side=tk.LEFT)

        proceedBtn = tk.Button(optionsFrame, text="Proceed", command=window.proceedBtnClick)
        proceedBtn.pack(fill=tk.Y, padx=8, pady=8, expand=0, side=tk.RIGHT)

        pass

    def listLightFrames(self, lightFrames:list):
        self.lightFramesFrame = tk.LabelFrame(self, text="Light frames")

        screen_width = self.winfo_screenwidth()
        listbox_width = int(screen_width * 0.15 / 8)  # Dividing by 8 to convert pixels to equivalent character width

        self.lightFrames = tk.Listbox(self.lightFramesFrame, width=listbox_width, selectmode=tk.SINGLE)
                
        self.lightFramesScrollbarHorizontal = tk.Scrollbar(self.lightFramesFrame, orient=tk.HORIZONTAL)
        self.lightFramesScrollbarHorizontal.config(command=self.lightFrames.xview)
                
        self.lightFramesScrollbarVertical = tk.Scrollbar(self.lightFramesFrame, orient=tk.VERTICAL)
        self.lightFramesScrollbarVertical.config(command=self.lightFrames.yview)

        self.lightFrames.config(yscrollcommand=self.lightFramesScrollbarVertical.set)
        self.lightFrames.config(xscrollcommand=self.lightFramesScrollbarHorizontal.set)        
        
        self.lightFramesScrollbarHorizontal.pack(fill=tk.X, padx=8, pady=8, expand=0, side=tk.BOTTOM)
        self.lightFramesScrollbarVertical.pack(fill=tk.Y, padx=8, pady=8, expand=0, side=tk.RIGHT)
        self.lightFrames.pack(fill=tk.BOTH, padx=8, pady=8, expand=1, side=tk.LEFT)
        self.lightFramesFrame.pack(fill=tk.Y, padx=8, pady=8, expand=1, side=tk.LEFT, anchor=tk.W)

        # Add light frames to list
        for lightFrame in lightFrames:
            self.lightFrames.insert(tk.END, os.path.basename(lightFrame))

        self.lightFrames.bind("<<ListboxSelect>>", self.showImagePreview)


