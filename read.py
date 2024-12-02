
import sys
import PIL.Image

# Global Variables
SILENT = False

def main():

    if len(sys.argv) < 2:
        log("Usage: python decode.py <image_path>")
        sys.exit(1)
    else:
        image_path = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == "-q":
            global SILENT
            SILENT = True

        image = PIL.Image.open(image_path)
        content_hex = ""
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                pixel = image.getpixel((x, y))
                pixel_hex = f"{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
                content_hex += pixel_hex

        print(content_hex)

        

def log(message):
    if SILENT:
        pass
    else:
        print(message)
    
if __name__ == "__main__":
    main()
