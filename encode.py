import sys
import os
import tqdm
import PIL.Image

# Global Variables
SILENT = False
ASPECT_RATIO = "1:1"

def main():

    if len(sys.argv) < 2:
        log("Usage: python encode.py <filepath>")
        sys.exit(1)
    else:
        filepath = sys.argv[1]
        if len(sys.argv) > 2:
            for arg in sys.argv:
                if arg == "-q":
                    global SILENT
                    SILENT = True
                if arg.split(":"):
                    global ASPECT_RATIO
                    ASPECT_RATIO = arg

        if SILENT:
            progress_bar = tqdm.tqdm(total=os.path.getsize(filepath), unit="byte", unit_scale=True)

        filename = os.path.basename(filepath)
        filename_hex = filename.encode("utf-8").hex()
        log(">>> Preparing filename")
        log(f"Filename: {filename}")
        log(f"Filename as utf-8 hex: {filename_hex}")
        log(f"Filename bytes: {len(filename)}")
        log(f"Filename 3 byte blocks = pixel: {len(filename) / 3}")
        log("")

        # checksum is the size of the filecontent
        # decoding will read the checksum and knows when the filecontent ends
        filecontent_checksum = str(os.path.getsize(filepath))
        filecontent_checksum_hex = filecontent_checksum.encode("utf-8").hex()
        log(">>> Preparing filecontent-checksum")
        log(f"Checksum: {filecontent_checksum}")
        log(f"Checksum as utf-8 hex: {filecontent_checksum_hex}")
        log(f"Checksum bytes: {len(filecontent_checksum)}")
        log(f"Checksum 3 byte blocks = pixel: {len(filecontent_checksum) / 3}")
        log("")

        filename_hex += "0a0d" # delimiter between filename and checksum
        filecontent_checksum_hex += "0a0d" # delimiter between checksum and filecontent
        file_header_hex = filename_hex + filecontent_checksum_hex
        log(">>> Appending delimiters to filename and checksum")
        log(f"content-header: {file_header_hex}")
        log(f"content-header bytes: {len(file_header_hex) / 2}")
        log("")

        filename_byte_count = len(filename_hex) / 2
        filecontent_checksum_byte_count = len(filecontent_checksum_hex) / 2
        filecontent_byte_count = os.path.getsize(filepath)
        merged_byte_count = filename_byte_count + filecontent_checksum_byte_count + filecontent_byte_count
        log(">>> Preparing file")
        log(f"Merged byte count: {merged_byte_count}")
        log(f"Merged 3 byte blocks: {merged_byte_count / 3}")
        while merged_byte_count % 3 != 0:
            merged_byte_count += 1
        log(f"Optimized byte count: {merged_byte_count}")
        log(f"Optimized 3 byte blocks = pixel: {merged_byte_count / 3}")
        log("")

        # open encoded image_file with the needed size to receive the stream
        encoded_image = open("encoded.png", "wb")
        encoded_image_x, encoded_image_y = calculate_encoded_image_size(merged_byte_count, ASPECT_RATIO)
        encoded_image = PIL.Image.new("RGB", (encoded_image_x, encoded_image_y))
        encoded_image_size = encoded_image_x * encoded_image_y
        log(">>> Creating Image")
        log(f"Image X Size: {encoded_image_x}")
        log(f"Image Y Size: {encoded_image_y}")
        log(f"Image Pixel Size (1 Pixel = 3 Byte): {encoded_image_size}")
        log("")

        # write file to image
        # the image is already created so missing content is filled with black pixels (content is smaller than image size)
        # each pixel is filled with 3 bytes of the origin file
        log(">>> Writing File to Image")
        file_header_hex_bytes = bytes.fromhex(file_header_hex)
        file = open(filepath, "rb")
        filecontent = file.read()
        file_merged = file_header_hex_bytes + filecontent

        pixel_pos = (0, 0)
        pixel_max_x_pos = encoded_image_x - 1

        pixel_current = 1
        pixel_needed = merged_byte_count / 3

        buffer_3_byte_index = 0 # 1 pixel = 3 byte
        buffer = file_merged[buffer_3_byte_index:buffer_3_byte_index+3]
        while buffer:
            log(f"Pixel index: {pixel_current}")
            log(f"Pixel needed: {pixel_needed}")
            pixel_pos = handle_byte_buffer(encoded_image, buffer, pixel_pos, pixel_max_x_pos)
            buffer_3_byte_index += 3
            pixel_current += 1
            buffer = file_merged[buffer_3_byte_index:buffer_3_byte_index+3]
            if SILENT: progress_bar.update(3)
            log("----------")
        log(">>> Content written")
        log("")
        remaining_pixels = encoded_image_size - pixel_current
        log(f">>> Filling remaining Pixels: {remaining_pixels}")
        while remaining_pixels > 0:
            log(f"Pixel index: {pixel_current}")
            log(f"Remaining Pixels: {remaining_pixels}")
            pixel_pos = convert_byte_block(encoded_image, os.urandom(3), pixel_pos, pixel_max_x_pos)
            remaining_pixels -= 1
            log("----------")
        log(">>> Remaining Pixels written")
        file.close()
        encoded_image.save("encoded.png")
        if SILENT: progress_bar.close()

def handle_byte_buffer(image, buffer, pixel_pos, pixel_pos_max_x):
    # image: the image to write data to
    # buffer: contains 3 bytes of the source file (filename + filecontent)
    # pixel_pos: current position in the image
    # pixel_pos_max_x: maximum x position in the image
    log(f"- Buffer: {buffer}")
    log(f"- Buffer Hex: {buffer.hex()}")
    if len(buffer) < 3:
        log(f">>> Buffer with empty color slots: {buffer}")
        empty_color_slots = 3 - len(buffer)
        buffer += b'\x00' * empty_color_slots
        log(f"- Buffer filled with null-bytes: {buffer}")
        pixel_pos = convert_byte_block(image, buffer, pixel_pos, pixel_pos_max_x)
        return pixel_pos
    pixel_pos = convert_byte_block(image, buffer, pixel_pos, pixel_pos_max_x)
    return pixel_pos

def convert_byte_block(image, byte_block, pixel_pos, pixel_pos_max_x):
    color = byte_block_into_color(byte_block)
    image.putpixel(pixel_pos, color)
    pixel_pos = move_to_next_pixel(pixel_pos, pixel_pos_max_x)
    return pixel_pos

# convert 3 byte-block into rgb color
def byte_block_into_color(byte_block):
    byte_block_hex = byte_block.hex()
    color = tuple(int(byte_block_hex[i:i+2], 16) for i in (0, 2, 4))
    log(f"- Pixel Color: {color}")
    return color

def move_to_next_pixel(pixel_pos, pixel_pos_max_x):
    if pixel_pos[0] == pixel_pos_max_x:
        pixel_pos = (0, pixel_pos[1] + 1)
    else:
        pixel_pos = (pixel_pos[0] + 1, pixel_pos[1])
    log(f"- Pixel Coordinate: {pixel_pos}")
    return pixel_pos

# Gets selected aspect ratio and calculates x and y size of the image.
# Size x * y will be bigger or equal to merged_byte_count / 3.
def calculate_encoded_image_size(merged_byte_count: int, aspect_ratio: str) -> tuple:
    global SILENT
    global ASPECT_RATIO
    log(f"Aspect Ratio: {aspect_ratio}")
    x = 0
    y = 0
    aspect_ratio = aspect_ratio.split(":")
    ratio_x = int(aspect_ratio[0])
    ratio_y = int(aspect_ratio[1])
    while x * y < merged_byte_count / 3:
        x += ratio_x
        y += ratio_y
    return (x, y)


def log(message):
    if SILENT:
        pass
    else:
        print(message)
    
if __name__ == "__main__":
    main()
