# ImageToPDF

## About
An app which combines multiple Images to one single PDF file by using Python.

## 🚀 Features
- 📁 Batch Process Subfolders: Automatically scans each subfolder and creates a separate PDF for each.
- 📐 Customizable Page Margins / Padding: Tailor the layout to your needs.
- 🖥️ Cross-Platform Support: Available on both macOS and Windows.
- 🖼️ One Image per Page (No Stitching): Keeps memory usage low and maintains image quality.
- 📊 Progress Bar Display: Know exactly how far along the conversion is.

## 📦 Installation

| Windows (X86)          | macOS (ARM64)           |
|------------------------|-------------------------|
| [Portable ZIP][latest] | [DMG Installer][latest] |

[latest]: https://github.com/SMH642800/ImageToPDF/releases/latest

## 📝 Notes
- Ensure images are in common formats like PNG or JPG and are sorted by filename.
- If conversion fails, double-check the folder structure and image formats.
  ```bash
  # Data structure tree
	
	main_folder/
	├── sub_folder1/
	│   ├── image01.jpg  
	│   ├── image02.jpg  
	│   └── ...  
	├── sub_folder2/
	│   ├── image01.jpg  
	│   ├── image02.jpg  
	│   └── ...  
  ```

## ⚠ macOS Gatekeeper Notice
- This app is not signed or notarized, so macOS may block it the first time you open it.

## 🚧 How to Open the App:
- If you see a message saying the app “can’t be opened because it is from an unidentified developer,” follow these steps:
	1.	Go to System Settings > Privacy & Security
	2.	Scroll down to the section that says: “ImageToPDF was blocked from use because it is not from an identified developer”
	3.	Click the “Open Anyway” button
	4.	A confirmation dialog will appear – click “Open” again

- You only need to do this once. Afterward, the app will launch normally.

---

## Python Versions
Compatible Python version: >=3.13, <3.14

## Python Package
```bash
pyqt6
pillow
img2pdf
```
