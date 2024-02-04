import boto3
import time
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
import os


# BEGIN: 9d8f7g6h5j4k
class TextractHelper:
    def __init__(self, profile_name, bucket_name):
        """
        Initializes a TextractHelper object with the specified AWS profile name.

        Args:
            profile_name (str): The name of the AWS profile to use for authentication.
            bucket_name (str): The name of the S3 bucket to use for storing the extracted text.

        Returns:
            None
        """
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self.session.client("textract", region_name="eu-central-1")
        self.bucket = bucket_name

    def async_query_document(self, document, questions):
        """
        Asynchronously analyzes a document in an S3 bucket and returns the results of the specified queries.
        Required for multipage documents.

        Args:
            client (boto3.client): A low-level client representing AWS services.
            bucket (str): The name of the S3 bucket containing the document to analyze.
            document (str): The name of the document to analyze in the S3 bucket.
            questions (list[str]): The list of queries to run on the document.

        Returns:
            dict: A dictionary containing the response metadata and the results of the queries.
        """

        # Analyze the document
        response = self.client.start_document_analysis(
            DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": document}},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [{"Text": "{}".format(question)} for question in questions]
            },
        )

        return response

    def sync_query_document(self, document, questions):
        """
        Analyzes a ONE-PAGE document in an S3 bucket for the specified questions and returns the query and answer.

        Args:
            client (boto3.client): The AWS Textract client.
            bucket (str): The name of the S3 bucket containing the document.
            document (str): The name of the document in the S3 bucket.
            questions (list[str]): The list of queries to run on the document.

        Returns:
            dict: The AWS Textract response containing the query and answer.
        """

        # Analyze the document
        response = self.client.analyze_document(
            Document={"S3Object": {"Bucket": self.bucket, "Name": document}},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [{"Text": "{}".format(question)} for question in questions]
            },
        )

        return response

    def query_local_image(self, image_path, questions):
        """
        Analyzes a local image file using Amazon Textract and returns the results of running the specified
        OCR queries on the image.

        Args:
            image_path (str): The path to the local image file to analyze.
            questions (List[str]): A list of OCR queries to run on the image.

        Returns:
            dict: A dictionary containing the OCR query results returned by Amazon Textract.
        """

        with open(image_path, "rb") as img_file:
            ## To display image using PIL ###
            # image = Image.open()
            ## Read bytes ###
            img_bytes = img_file.read()

            response = self.client.analyze_document(
                Document={"Bytes": img_bytes},
                FeatureTypes=["QUERIES"],
                QueriesConfig={
                    "Queries": [
                        {"Text": "{}".format(question)} for question in questions
                    ]
                },
            )
            return response

    def analyze_id(self, document):
        # Analyze document
        # process using S3 object
        response = self.client.analyze_id(
            DocumentPages=[{"S3Object": {"Bucket": self.bucket, "Name": document}}]
        )

        for doc_fields in response["IdentityDocuments"]:
            for id_field in doc_fields["IdentityDocumentFields"]:
                for key, val in id_field.items():
                    if "Type" in str(key):
                        print("Type: " + str(val["Text"]))
                for key, val in id_field.items():
                    if "ValueDetection" in str(key):
                        print("Value Detection: " + str(val["Text"]))
                print()

    def download_s3_file(self, document, filename):
        """
        Downloads a file from an S3 bucket.

        Args:
            document (str): The S3 document to download.
            filename (str): The local filename to save the downloaded file as.

        Returns:
            str: The filename of the downloaded file.
        """
        s3 = boto3.resource("s3")

        s3.meta.client.download_file(document, filename)
        return filename

    def multipage_pdf_to_local_images(self, document, file_prefix, tmp_folder):
        """
        Converts a multipage PDF document to a list of PNG images, saving them to disk with the given file prefix.
        Args:
            :param document: The path to the PDF document to convert.
            :type document: str
            :param file_prefix: The prefix to use for the output PNG files.
            :type file_prefix: str
            :return: A list of paths to the output PNG files.
            :rtype: List[str]
        """
        images = convert_from_path(document)
        output_filenames = []
        for i, image in enumerate(images):
            out_img_name = file_prefix + str(i) + ".png"
            image.save(tmp_folder + "/" + out_img_name, "PNG")
            output_filenames.append(out_img_name)
        return output_filenames

    def multipage_pdf_to_pdfs_in_s3(self, document, file_prefix, tmp_folder):
        """
        Converts a multipage PDF file to individual PDF files, and uploads them to an S3 bucket.

        Args:
            document (str): The path to the input PDF file.
            file_prefix (str): The prefix to use for the output PDF files.

        Returns:
            List[str]: A list of the names of the output PDF files that were uploaded to S3.
        """

        inputpdf = PdfReader(open(document, "rb"))

        s3_client = boto3.client("s3")
        output_filenames = []

        for i in range(len(inputpdf.pages)):
            output = PdfWriter()
            output.add_page(inputpdf.pages[i])
            output_filename = file_prefix + str(i) + ".pdf"
            with open(output_filename, "wb") as outputStream:
                output.write(outputStream)
            try:
                s3_client.upload_file(
                    output_filename, self.bucket, tmp_folder + "/" + output_filename
                )
                output_filenames.append(output_filename)
            except:
                print("problem uploading file to s3")
        return output_filenames

    def delete_local_file(self, filename):
        """
        Deletes a local file.

        Args:
            filename (str): The path to the file to delete.

        Returns:
            None
        """
        os.remove(filename)

    def delete_s3_file(self, filenames):
        """
        Deletes the given list of files from the S3 bucket associated with this TextractHelper instance.

        Args:
            :param filenames: A list of filenames to delete from the S3 bucket.
            :type filenames: list(str)
        """
        s3 = boto3.resource("s3")
        for filename in filenames:
            s3.Object(self.bucket_name, filename).delete()

    def get_query_results(self, response):
        """
        Extracts query and query result from the response and returns them as a dictionary.

        Args:
            response (dict): The response from AWS Textract.

        Returns:
            dict: A dictionary containing the query and query result extracted from the response.
        """
        query_dict = {}
        query = ""
        query_result = ""
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY":
                query = block["Query"]["Text"]
            elif block["BlockType"] == "QUERY_RESULT":
                query_result = block["Text"]
            if query and query_result:
                query_dict[query] = query_result
                query = ""
                query_result = ""
        return query_dict

    def query_each_page_pdf(self, document, file_prefix, tmp_folder, questions):
        """
        Queries a PDF document by converting it to local images and running OCR on each page.

        Args:
            document (bytes): The PDF document to query.
            file_prefix (str): A prefix to use for the output image files.
            tmp_folder (str): The path to a temporary folder where the image files will be stored.
            questions (List[str]): A list of questions to ask about the document.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, one for each page of the document, where each key is a question
            and each value is the corresponding answer found in the OCR output.
        """
        output_filenames = self.multipage_pdf_to_local_images(
            document, file_prefix, tmp_folder
        )

        pages = []
        for output_filename in output_filenames:
            query_dict = {}
            response = self.query_local_image(
                tmp_folder + "/" + output_filename, questions
            )
            query_dict = self.get_query_results(response)
            pages.append(query_dict)

        for filename in output_filenames:
            self.delete_local_file(tmp_folder + "/" + filename)
        return pages

    # try sync for one page if error , go for multipage. pricing? makes sense?
    def query_pdf(self, document, file_prefix, tmp_folder, questions):
        pass
