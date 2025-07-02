![LabBuddy](assets/banner_512x128.png)

LabBuddy is a physics lab assistant tool designed to help with lab works that require a computer software.

---

## 🔍 Overview
The application helps automating:
- **Object tracking** via video analysis
- **Uncertainty computations**, especially on the slope of data curves
- **Export data** in various formats

---

## 🛠️ Key Features
| Feature | Implementation Details |
|---------|-----------------------|
| **Object detection** | OpenCV-based tracking using HSV masks. |
| **Slope Uncertainty Tool** | Implements min-max slope method. |
| **Data Export** | CSV/ODS/XLSX exports for integration with LibreOffice, Excel, or Python workflows. |

---

## ⚙️ Installation and usage

1. Clone the repository:
    ```bash
    git clone https://github.com/clement-marty/labbuddy.git
    cd labbuddy
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3. Start the application:
    ```bash
    python main.py
    ```
    
## ⚙️ Compiling

```bash
pip install pyinstaller
pyinstaller main.spec
```
The compiled application's files will be located in `dist/main`.

## 🤝 Contributing

Contributions are welcome! Please open issues, submit pull request or suggest new features in the discussions.

## License

This project is licensed under the MIT License.

#### 💡 Need Help? Open an issue or contact @clement-marty.