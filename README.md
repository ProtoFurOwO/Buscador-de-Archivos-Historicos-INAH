# Buscador-de-Archivos-Historicos-INAH
A simple and efficient desktop application built with Python and Tkinter to index and search for PDF documents within a nested folder structure. The tool is designed to easily navigate historical archives, assuming a hierarchy of Municipality/Building/Document.pdf

Requirements
Python 3.x
The Tkinter library (usually included in the standard Python installation).

How It Works
The application assumes that the PDF files are organized in a hierarchical folder structure:

<img width="450" height="403" alt="image" src="https://github.com/user-attachments/assets/53eb7c7f-6602-49ac-9f1a-36370ae5daa6" />

When you click "Re-Index", the program scans all these folders, extracts the Municipality and Building/Place from the path, and saves this information along with the filename into an inah_documentos.db database.

Usage Instructions
1.- Clone the repository:
git clone https://github.com/ProtoFurOwO/Buscador-de-Archivos-Historicos-INAH
cd Buscador-de-Archivos-Historicos-INAH
2.- Run the application:
python buscador_inah.py
3.- Select the Root Folder: Click the 📁 Select Folder button and choose the main directory containing all your files.
4.- Index the Files: Click 🔄 Re-Index Files. Wait for the process to complete. You will be notified when it's finished.
5.- Search: Type a term in the search bar and press Enter or click the 🔎 Search button.
6.- Open a File: Double-click on any row in the results table to open the corresponding PDF document.
