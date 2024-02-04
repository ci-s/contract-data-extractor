from langchain.document_loaders import UnstructuredFileLoader, UnstructuredImageLoader
import pandas as pd
from os import walk
from PIL import Image
import PyPDF2
import re
import pytesseract
from pdf2image import convert_from_path


class FileReader:
    """This class is created to read PDF files including machine-readable and non machine-readable."""

    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.pdf_file_types = [".pdf", ".PDF"]
        self.image_file_types = [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"]

    def read_pdf(self, subfolder, filename):
        """Reads PDF files using Langchain's UnstructuredFileLoader

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        path = self.data_path + "/" + subfolder + "/" + filename
        loader = UnstructuredFileLoader(path)
        pages = loader.load()

        if len(pages) > 1:
            print("Many pages!")

        return pages[0].page_content

    # def read_all_contracts(self, contract_path):
    #     """Works within the contract folder

    #     Args:
    #         contract_path (str): _description_

    #     Returns:
    #         dict: key = filename, value = contract content
    #     """
    #     filenames = self.get_all_filenames(contract_path)
    #     contracts = {}
    #     for filename in filenames:
    #         path = self.data_path + contract_path + filename
    #         contract = self.read_contract(path)
    #         contracts[filename] = contract
    #     return contracts

    def get_all_filenames(self, sub_folder_path):
        f = []
        for dirpath, dirnames, filenames in walk(
            self.data_path + "/" + sub_folder_path
        ):
            f.extend(filenames)
        return f

    def read_contract(self, sub_folder_path, filename):
        """
        Reads a contract file from the specified sub-folder path and filename.

        Args:
            sub_folder_path (str): The path to the sub-folder containing the contract file.
            filename (str): The name of the contract file.

        Returns:
            The content of the contract file.

        Raises:
            ValueError: If the file type is not supported or if a PDF file requires rotating.
        """
        if any(filename.endswith(file_type) for file_type in self.pdf_file_types):
            orients = self.detect_pdf_orientation(sub_folder_path, filename)
            if 180 in orients:
                raise ValueError("Rotation for PDF not supported: " + filename)
            return self.read_pdf(sub_folder_path, filename)
        elif any(filename.endswith(file_type) for file_type in self.image_file_types):
            orients = self.detect_image_orientation(sub_folder_path, filename)
            if 180 in orients:
                print(
                    "Upside down document detected! Following image be rotated: ",
                    filename,
                )
                filename = self.rotate_image_180(sub_folder_path, filename)
            return self.read_image(sub_folder_path, filename)
        else:
            raise ValueError("File type not supported: " + filename)

    def read_all_contracts(self, sub_folder_path):


        filename_list = self.get_all_filenames(sub_folder_path)

        contracts = {}

        for filename in filename_list:
            if any(filename.endswith(file_type) for file_type in self.pdf_file_types):
                orients = self.detect_pdf_orientation(sub_folder_path, filename)
                if 180 in orients:
                    raise ValueError("Rotation for PDF not supported: " + filename)
                contracts[filename] = self.read_pdf(sub_folder_path, filename)
            elif any(filename.endswith(file_type) for file_type in self.image_file_types):
                orients = self.detect_image_orientation(sub_folder_path, filename)
                if 180 in orients:
                    print(
                        "Upside down document detected! Following image be rotated: ",
                        filename,
                    )
                    filename = self.rotate_image_180(sub_folder_path, filename)
                contracts[filename] = self.read_image(sub_folder_path, filename)
            else:
                raise ValueError("File type not supported: " + filename)
        return contracts

    def process_contract(self, contract):
        contract = contract.replace("\n", " ")
        contract = contract.replace("  ", " ")
        return contract

    def fix_image_orientation_alternative(self, path):
        img = Image.open(self.data_path + path)
        # mirror in two directions
        img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def read_image(self, subfolder, filename):
        """Reads image files using Langchain's UnstructuredImageLoader
            UnstructuredImageLoader
        Args:
            subfolder (str): subfolder name
            filename (str): filename
        """
        path = self.data_path + "/" + subfolder + "/" + filename
        loader = UnstructuredImageLoader(path)
        pages = loader.load()

        if len(pages) > 1:
            print("Many pages!")

        return pages[0].page_content

    def rotate_image_180(self, subfolder, filename):
        """Rotates an image and saves it (180 degrees clockwise).
        Args:
            subfolder (str): subfolder name
            filename (str): filename
        """
        file_path_name = filename.split(".")[0]
        if "_rotated" in file_path_name:
            output_filename = file_path_name
        else:
            output_filename = file_path_name + "_rotated.jpg"

        path = self.data_path + "/" + subfolder + "/" + filename
        img = Image.open(path)
        rotated_img = img.rotate(180)  # Rotate the image 90 degrees clockwise
        output_path = self.data_path + "/" + subfolder + "/" + output_filename
        rotated_img.save(output_path)
        return output_filename

    def rotate_pdf(self, subfolder, filename):
        """Rotate a PDF page and save it.
            NOT TESTED YET, No pdf is upside down
        Args:
            subfolder (str): subfolder name
            filename (str): filename
        """
        path = self.data_path + "/" + subfolder + "/" + filename
        file_path_name = path.split(".")[0]
        output_path = file_path_name + "_rotated.pdf"
        output_path = self.data_path + "/" + subfolder + "/" + output_path

        with open(path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            writer = PyPDF2.PdfFileWriter()

            page = reader.getPage(0)
            page.rotateClockwise(90)
            writer.addPage(page)

            with open(output_path, "wb") as output:
                writer.write(output)
        return output_path

    def detect_image_orientation(self, subfolder, filename):
        """Returns the orientation of the image as 1 element list
        Args:
            subfolder (str): subfolder name
            filename (str): filename
        """
        file_path = self.data_path + "/" + subfolder + "/" + filename
        im = Image.open(file_path)
        osd = pytesseract.image_to_osd(im)
        return [int(re.search("(?<=Rotate: )\d+", osd).group(0))]

    def detect_pdf_orientation(self, subfolder, filename):
        """Returns the orientation of the pdf file as a list

        Args:
            subfolder (str): subfolder name
            filename (str): filename

        Returns:
            list: list of orientations of each page
        """
        file_path = self.data_path + "/" + subfolder + "/" + filename
        images = convert_from_path(file_path)

        orients = []
        for image in images:
            image = image.convert("RGB")
            image = image.crop((0, 0, image.size[0], image.size[1] // 2))

            # Detect the orientation of the image using pytesseract
            osd = pytesseract.image_to_osd(image)
            orients.append(int(re.search("(?<=Rotate: )\d+", osd).group(0)))
        return orients
