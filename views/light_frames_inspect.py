import os
from tkinter import  Tk
from utils.settings import Settings
from utils.utils import calculateExposureTimes, formatExposureTime
from widgets.status_bar import StatusBar

import views.fits_details as fits_details
import tkinter as tk
import numpy as np

from PIL import ImageTk, Image
from astropy.io import fits

class LightFramesInspectWindow(Tk):
    def __init__(self, objectPath:str, selectedObject:str, selectedDates:list):
        super().__init__()
        self.settings = Settings()
        self.detailsWindow = None
        self.imageName = tk.StringVar()
        self.showFitDetailChk = tk.IntVar()
        self.autostretchImage = tk.IntVar()
        self.currentImageIsBad = tk.IntVar()

        self.selectedObject = selectedObject
        self.objectPath = objectPath
        self.selectedDates = selectedDates
        
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
        if self.detailsWindow != None:
            self.detailsWindow.destroy()
            self.detailsWindow = None

        self.destroy()
        import views.create_process as create_process
        create_process.CreateProcessWindow(self.selectedDates, self.objectPath, self.selectedObject)
        pass

    def selectDifferentDatesBtnClick(self):
        if self.detailsWindow != None:
            self.detailsWindow.destroy()
            self.detailsWindow = None

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

            # If the image is a .fit file, open it and extract the image data
            if image_path.endswith(".fit") or image_path.endswith(".fits"):
                with fits.open(image_path) as hdul:
                    image_data = hdul[0].data

                if self.detailsWindow != None:
                    self.detailsWindow.fitsHeader = hdul[0].header
                    self.detailsWindow.refresh()

            # If the image is CR2 or CR3 (Canon RAW), open it and extract the image data
            elif image_path.endswith(".cr2") or image_path.endswith(".cr3") or image_path.endswith(".CR2") or image_path.endswith(".CR3"):
                import rawpy
                raw = rawpy.imread(image_path)
                bayer = raw.raw_image
                image_data = np.array(bayer)

            # If the image is a .jpg or .png file, open it and extract the image data
            elif image_path.endswith(".jpg") or image_path.endswith(".png") or image_path.endswith(".JPG") or image_path.endswith(".PNG"):
                image_data = np.array(Image.open(image_path))

            # If the image is none of the above, print an error message and return
            else:
                print("Error: Unsupported file format!")
                return

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
            self.zoomToFit(self.pil_image.width, self.pil_image.height)
            self.drawImage(self.pil_image)

            self.label_image_info["text"] = f"{self.imageName.get()} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

            # Update image is bad checkbox based on file name suffix
            if self.settings.badImagePrefix in image_path:
                self.currentImageIsBad.set(1)
            else:
                self.currentImageIsBad.set(0)

    def prevImage(self, event):
        index = self.lightFrames.curselection()[0] if self.lightFrames.curselection() != () else 0
        if index == 0:
            self.lightFrames.selection_set(self.lightFrames.size() - 1)
        else:
            self.lightFrames.selection_clear(index)
            self.lightFrames.selection_set(index - 1)
        self.showImagePreview(self)
        
    def nextImage(self, event):
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
        self.canvas.bind("<Motion>", self.mouseMoveEvent)
        self.canvas.bind("<Double-Button-1>", self.mouseDoubleClickEvent)
        self.canvas.bind("<MouseWheel>", self.mouseWheelEvent)

        # Arrow keys for previous/next image
        self.bind("<Left>", self.prevImage)
        self.bind("<Right>", self.nextImage)

    def mouse_down_left(self, event):
        self.__old_event = event

    def mouse_move_left(self, event):
        if (self.pil_image == None):
            return
        
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.drawImage(self.pil_image)
        self.__old_event = event

    def mouseMoveEvent(self, event):
        if (self.pil_image == None):
            return
        
        image_point = self.toImagePoint(event.x, event.y)
        if image_point != []:
            self.label_image_pixel["text"] = (f"({image_point[0]:.2f}, {image_point[1]:.2f})")
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouseDoubleClickEvent(self, event):
        if self.pil_image == None:
            return
        
        self.zoomToFit(self.pil_image.width, self.pil_image.height)
        self.drawImage(self.pil_image)

    def mouseWheelEvent(self, event):
        if self.pil_image == None:
            return

        if (event.delta < 0):
            self.scaleImage(1.25, event.x, event.y)
        else:
            self.scaleImage(0.8, event.x, event.y)

        self.drawImage(self.pil_image)
        
    def resetZoom(self):
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

    def scaleImage(self, scale:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def zoomToFit(self, image_width, image_height):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        self.resetZoom()

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

    def toImagePoint(self, x, y):
        if self.pil_image == None:
            return []
        
        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.pil_image.width or image_point[1] > self.pil_image.height:
            return []

        return image_point

    def drawImage(self, pil_image):
        
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

    def imageContainer(self):
        self.image_frame = tk.Frame(self)        
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        pass

    def topBar(self, window):
        # Add top bar with file, edit, view, etc.
        self.menuBar = tk.Menu(window)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Settings", command=self.settingsMenuClick)
        self.fileMenu.add_command(label="Open object folder", command=lambda: os.startfile(self.objectPath))
        self.fileMenu.add_command(label="Select different dates", command=self.selectDifferentDatesBtnClick)
        self.fileMenu.add_command(label="Exit", command=self.destroy)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.processMenu = tk.Menu(self.menuBar, tearoff=0)
        self.processMenu.add_command(label="Create process folder", command=self.proceedBtnClick)
        self.processMenu.add_command(label="Calibration frames", command=self.proceedBtnClick)
        self.menuBar.add_cascade(label="Process", menu=self.processMenu)

        self.viewMenu = tk.Menu(self.menuBar, tearoff=0)
        self.viewMenu.add_checkbutton(label="Show image info (If available)", variable=self.showFitDetailChk, command=self.showFitDetails)
        self.viewMenu.add_checkbutton(label="Auto-stretch image", variable=self.autostretchImage, command=lambda: self.showImagePreview(self))
        self.menuBar.add_cascade(label="View", menu=self.viewMenu)

        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="About", command=lambda: tk.messagebox.showinfo("About", "AstroGenie is a tool for astrophotographers to help them sort and process their images."))
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

        # Set default checkbutton values
        self.autostretchImage.set(1)

        self.config(menu=self.menuBar)

        pass

    def showFitDetails(self):
        # If we're supposed to show the FITs details, show them
        if self.showFitDetailChk.get() == 1:
            if self.detailsWindow != None:
                self.detailsWindow.destroy()
                self.detailsWindow = None

            self.detailsWindow = fits_details.FitsDetailsWindow()
            return
        
        # If we're not supposed to show the window check if it's open and close it if it is
        if self.showFitDetailChk.get() == 0:
            if self.detailsWindow != None:
                self.detailsWindow.destroy()
                self.detailsWindow = None
            return

    def settingsMenuClick(self):
        import views.settings as settings
        settings.SettingsWindow()

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


