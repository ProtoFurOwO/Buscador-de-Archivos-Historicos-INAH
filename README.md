# 🏛️ INAH Historical Archives Finder

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
A simple and efficient desktop application built with Python, Tkinter and SQLite to index and search for PDF documents within a nested folder structure. The tool is designed to easily navigate historical archives, assuming a hierarchy of `Municipality/Building/Document.pdf`.
---
<img width="1235" height="907" alt="image" src="https://github.com/user-attachments/assets/081ca0e8-8d8a-4c73-a8cc-e128b7ad5141" />
---

## ✨ Key Features
* **Fast Search**: Find files by municipality, building/place, or document name.
* **Simple GUI**: A clean and user-friendly interface created with Tkinter.
* **Dynamic Folder Selection**: Choose the root folder of your files directly from the application.
* **Efficient Indexing**: Recursively scans folders and saves paths to an SQLite database for instant searches.
* **Clean Re-indexing**: Deletes the old index before starting a new one to ensure only existing files appear in the results.
* **Sortable Results**: Sort the search results by clicking on the column headers (Municipality, Building, Document).
* **Direct File Access**: Open any PDF directly from the results table with a double-click.

## 🛠️ Installation & Usage
Follow these simple steps to get the application up and running:
1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/ProtoFurOwO/Buscador-de-Archivos-Historicos-INAH.git](https://github.com/ProtoFurOwO/Buscador-de-Archivos-Historicos-INAH.git)
    ```

2.  **Navigate to the Directory**:
    ```bash
    cd Buscador-de-Archivos-Historicos-INAH
    ```

3.  **Run the Application**:
    ```bash
    python buscador_inah.py
    ```
4.  **Select Folder**: When the app opens, click the `📁 Select Folder` button and choose the main directory containing all your files.

5.  **Index the Files**: Click on `🔄 Re-Index Files`. Wait for the process to finish. You will be notified when it's complete, and all files will appear in the table.

6.  **Search**: Type a term in the search bar and press `Enter` or click the `🔎 Search` button.

7.  **Open a File**: Double-click on any row in the table to open the corresponding PDF.

## 📁 Expected Folder Structure

For proper indexing, the application expects your files to be organized as follows:

<img width="450" height="403" alt="image" src="https://github.com/user-attachments/assets/8a7d7e79-3d18-4b0d-8db1-39ae42b81f25" />
