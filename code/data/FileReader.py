from langchain.document_loaders import UnstructuredFileLoader, UnstructuredImageLoader
import pandas as pd
from os import walk
import os
from PIL import Image
import PyPDF2
import re
import pytesseract
from pdf2image import convert_from_path
import requests
from urllib.parse import urlparse
import tempfile


class FileReader:
    """This class is created to read PDF files including machine-readable and non machine-readable."""

    def __init__(self) -> None:
        self.pdf_file_types = [".pdf", ".PDF"]
        self.image_file_types = [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"]

    def read_pdf(self, path):
        """Reads PDF files using Langchain's UnstructuredFileLoader

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        loader = UnstructuredFileLoader(path)
        pages = loader.load()

        if len(pages) > 1:
            print("Many pages!")

        return pages[0].page_content

    def read_contract(self, filepath):
        """
        Reads a contract file from the specified sub-folder path and filename.

        Args:
            filepath (str): The path to the contract file.

        Returns:
            The content of the contract file.

        Raises:
            ValueError: If the file type is not supported or if a PDF file requires rotating.
        """
        if any(filepath.endswith(file_type) for file_type in self.pdf_file_types):
            orients = self.detect_pdf_orientation(filepath)
            if 180 in orients:
                raise ValueError("Rotation for PDF not supported: " + filepath)
            return self.read_pdf(filepath)
        elif any(filepath.endswith(file_type) for file_type in self.image_file_types):
            orients = self.detect_image_orientation(filepath)
            if 180 in orients:
                print(
                    "Upside down document detected! Following image be rotated: ",
                    filepath,
                )
                filepath = self.rotate_image_180(filepath)
            return self.read_image(filepath)
        else:
            raise ValueError("File type not supported: " + filepath)

    def read_image(self, filepath):
        """Reads image files using Langchain's UnstructuredImageLoader
            UnstructuredImageLoader
        Args:
            filepath (str): path of the image file
        """
        loader = UnstructuredImageLoader(filepath)
        pages = loader.load()

        if len(pages) > 1:
            print("Many pages!")

        return pages[0].page_content

    def rotate_image_180(self, file_path):
        """Rotates an image and saves it (180 degrees clockwise).
        Args:
            file_path (str): path to file
        """

        img = Image.open(file_path)
        rotated_img = img.rotate(180)  # Rotate the image 90 degrees clockwise
        rotated_img.save(file_path)
        return file_path

    def rotate_pdf(self, filepath):
        """Rotate a PDF page and save it.
            NOT TESTED YET, No pdf is upside down
        Args:
            filepath (str): path to file
        """

        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            writer = PyPDF2.PdfFileWriter()

            page = reader.getPage(0)
            page.rotateClockwise(90)
            writer.addPage(page)

            with open(filepath, "wb") as output:
                writer.write(output)
        return filepath

    def detect_image_orientation(self, file_path):
        """Returns the orientation of the image as 1 element list
        Args:
            file_path (str): path to file
        """
        im = Image.open(file_path)
        osd = pytesseract.image_to_osd(im)
        return [int(re.search("(?<=Rotate: )\d+", osd).group(0))]

    def detect_pdf_orientation(self, file_path):
        """Returns the orientation of the pdf file as a list

        Args:
            file_path (str): path to file

        Returns:
            list: list of orientations of each page
        """
        images = convert_from_path(file_path)

        orients = []
        for image in images:
            image = image.convert("RGB")
            image = image.crop((0, 0, image.size[0], image.size[1] // 2))

            # Detect the orientation of the image using pytesseract
            osd = pytesseract.image_to_osd(image)
            orients.append(int(re.search("(?<=Rotate: )\d+", osd).group(0)))
        return orients

    def delete_local_file(self, filepath):
        """
        Deletes a local file.

        Args:
            filepath (str): The path to the file to delete.

        Returns:
            None
        """
        os.remove(filepath)

    def read_url(self, url):
        # Get URL
        response = requests.get(url)

        # Create a temporary file in the system's temp directory
        # temp_file = tempfile.NamedTemporaryFile(delete=False)
        # temp_file.write(response.content)
        # temp_file.close()
        # return temp_file.name

        # Extract filename from URL
        a = urlparse(url)
        filename = os.path.basename(a.path)

        # Save file
        if not os.path.exists("./tmp"):
            os.makedirs("./tmp")
        filepath = "./tmp/" + filename
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath

    def read_contract_from_url(self, url):
        temp_file_path = self.read_url(url)
        contract = self.read_contract(temp_file_path)
        os.remove(temp_file_path)  # Delete the temp file
        return contract
