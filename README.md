# SEC Financial Extractor

The SEC Financial Extractor is a user interface form application that allows users to extract financial information from publicly listed companies in the SEC exchange. Users can select companies from a list with a search feature and choose to download the data in either database format (SQL Lite) or Excel format.

## Features

- User-friendly interface with company selection and search functionality.
- Extraction of Company Facts using the unique CIK number for each company.
- Data extraction in JSON format from SEC APIs.
- Conversion of JSON data into tables containing financial information.
- Table of contents page for easy navigation (available in Excel version).
- Hyperlinks in the Excel version for convenient access to specific sections.
- Conversion of text values meant to be in USD into an accounting format with a dollar sign.

## Note

This application is currently in Phase 1 and may not be fully robust or include extensive unit testing. The primary goal of Phase 1 is to provide a basic extraction and presentation of financial information. In Phase 2, the application will be further improved and enhanced based on identified data needs and data cleanup requirements.

## Usage

1. Clone or download the repository.
2. Install the required dependencies mentioned in the installation section.
3. Run the Python application.
4. Select companies, choose the desired download format, and provide necessary information.
5. Click the "Submit" button to initiate the API extract and download process.
6. Monitor the progress in the debugger console or text widget.
7. Once the extraction is complete, a message box will appear indicating the success.
8. Access the downloaded files in the specified folder.

## Installation

1. Download Dist File & run the .exe file (version 1.0).
2. Install the required dependencies:

## Contributing

Contributions to the SEC Financial Extractor project are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the [ALI ALTAJJAR](LICENSE).
