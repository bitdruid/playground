import os
import urllib.parse
from pathlib import Path

from PIL import Image, ImageOps
import img2pdf

from playwright.sync_api import sync_playwright, Playwright

from datetime import datetime

def screenshot_to_pdf(screenshot_path):

    def split_image_to_a4(image_path, output_folder):
        img = Image.open(image_path)
        img_width, img_height = img.size

        # a4 aspect ratio calculation
        a4_aspect_ratio = 1.414
        max_img_height = img_width * a4_aspect_ratio
        last_img_height_cut = 0

        partial_images_paths = []

        while last_img_height_cut < img_height:
            # size of the partial image in pixels
            # max_img_height is the maximum height of the partial image to match A4 aspect ratio
            # last_img_height_cut is the height of the original image that has been cut so far
            crop_height = min(max_img_height, img_height - last_img_height_cut)
            partial_img = img.crop((0, last_img_height_cut, img_width, last_img_height_cut + crop_height))

            # if the last partial image is smaller than max_img_height, fill the rest with white
            if crop_height < max_img_height:
                partial_img = ImageOps.expand(partial_img, (0, 0, 0, int(max_img_height - crop_height)), fill='white')

            # save partial image
            partial_img_path = os.path.join(output_folder, f"partial_{len(partial_images_paths)}.jpeg")
            partial_img.save(partial_img_path)
            partial_images_paths.append(partial_img_path)

            last_img_height_cut += max_img_height

        img.close()

        return partial_images_paths

    def images_to_pdf(image_paths, pdf_path):
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(img2pdf.convert(image_paths))
        for partial_img_path in image_paths:
            os.remove(partial_img_path)

    output_folder = os.path.dirname(screenshot_path)
    pdf_path = os.path.join(output_folder, f"{os.path.basename(screenshot_path).rsplit('.', 1)[0]}.pdf")
    partial_images_paths = split_image_to_a4(screenshot_path, output_folder)
    images_to_pdf(partial_images_paths, pdf_path)
    return pdf_path


def check_install():
    if not os.path.exists(os.path.join(Path.home(), ".cache", "ms-playwright")):
        print("Playwright executables not found. Installing...")
        os.system("playwright install firefox --with-deps")


def sanitize_url_to_filename(url: str):
    disallowed = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for char in disallowed:
        url = url.replace(char, ".")
    url = ".".join(filter(None, url.split(".")))
    return url


def screenshot(playwright: Playwright, url: str, path: str = None):
    firefox = playwright.firefox
    browser = firefox.launch(headless=True)
    browser = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        viewport={"width": 1600, "height": 900}
    )
    page = browser.new_page()
    page.goto(url)
    page.waitforloadstate('domcontentloaded')
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{sanitize_url_to_filename(url)}.jpeg"
    if path:
        screenshot_path = os.path.join(path, f"{filename}.jpeg")
    else:
        screenshot_path = os.path.join(os.getcwd(), f"{filename}")
    page.screenshot(path=screenshot_path, full_page=True, type="jpeg", quality=80)
    browser.close()
    
    return screenshot_path


def request(input):
    if not urllib.parse.urlparse(input).scheme:
        input = f"http://{input}"
        # return f"Could not recognize valid URL to screenshot: {input}"
    #check_install()
    with sync_playwright() as playwright:
        try:
            screenshot_path = screenshot(playwright, input)
            pdf_path = screenshot_to_pdf(screenshot_path)
        except Exception as e:
            return f"Error: {e}"
    return [screenshot_path, pdf_path]


if __name__ == "__main__":
    from osintkit.main import main_template

    main_template(request)
