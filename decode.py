import sys
from tqdm import tqdm

import PIL.Image

# Global Variables
SILENT = False
ASPECT_RATIO = "1:1"


def main():
    if len(sys.argv) < 2:
        log("Usage: python decode.py <image_path>")
        sys.exit(1)
    else:
        image_path = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == "-q":
            global SILENT
            SILENT = True

        if SILENT:
            progress_bar = None

        log(f">>> Preparing Image: {image_path}")
        encoded_image = PIL.Image.open(image_path)
        encoded_image_x = encoded_image.size[0]
        encoded_image_y = encoded_image.size[1]
        log(f"Image Size (1 Pixel = 3 Byte): {encoded_image_x} x {encoded_image_y}")
        log("")

        pixel_matrix = list(encoded_image.getdata())

        log(">>> Reading content header")
        filename, checksum, byte_position = read_content_header(pixel_matrix)

        if SILENT:
            progress_bar = tqdm(total=checksum, unit="B", unit_scale=True)

        file = open(filename, "wb")

        log(">>> Reading content")
        byte_index = 0
        byte_count = 0
        for pixel in pixel_matrix:
            for color in pixel:
                # break if the checksum is reached
                if byte_count == checksum:
                    break
                # skip bytes that contain the content header
                if byte_index < byte_position:
                    byte_index += 1
                    continue
                byte = f"{color:02x}"
                file.write(bytes.fromhex(byte))
                if SILENT:
                    progress_bar.update(1)
                byte_index += 1
                byte_count += 1
            if byte_count == checksum:
                break

        if SILENT:
            progress_bar.close()
        log(">>> Done")


def read_content_header(pixel_matrix):
    content_header = ""
    count_delimiters = 0
    delimiter_part_found = False
    filename_delimiter_found = False
    checksum_delimiter_found = False
    byte_position = 0
    for pixel in pixel_matrix:
        for color in pixel:
            byte = f"{color:02x}"
            if count_delimiters == 2:
                break
            elif byte == "0a" and not delimiter_part_found:
                delimiter_part_found = True
            elif byte == "0d" and delimiter_part_found:
                count_delimiters += 1
                delimiter_part_found = False
                if not filename_delimiter_found:
                    filename_delimiter_found = True
                else:
                    checksum_delimiter_found = True
            elif filename_delimiter_found and not checksum_delimiter_found:
                byte_utf8 = bytes.fromhex(byte).decode("utf-8")
                if not byte_utf8.isdigit():
                    log("The checksum is not completed but a non-digit character was found.")
                    exit(1)
            if not filename_delimiter_found and len(content_header) >= 255:
                log("No filename was found and the maximum filename length was reached.")
                exit(1)
            content_header += byte
            byte_position += 1
        if count_delimiters == 2:
            break
    log(f"Content Header hex: {content_header}")
    log(f"Content Header bytes:{bytes.fromhex(content_header)}")
    filename = str(bytes.fromhex(content_header.split("0a0d")[0]).decode("utf-8"))
    checksum = int(bytes.fromhex(content_header.split("0a0d")[1]).decode("utf-8"))
    log(f"Filename: {filename}")
    log(f"Checksum: {checksum}")
    log("")
    return filename, checksum, byte_position


def log(message):
    if SILENT:
        pass
    else:
        print(message)


if __name__ == "__main__":
    main()
