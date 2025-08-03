# 🦁 WildLens AI - Animal Identifier

WildLens AI is a Streamlit web app that uses a pre-trained **VGG16 CNN model** to identify animals from uploaded images and fetches interesting facts about them from **Wikipedia**. It’s fast, fun, and educational!

![App Demo](https://img.shields.io/badge/Built%20with-Streamlit-brightgreen?style=flat&logo=streamlit)

---

## 📸 Features

- 🔍 Upload animal image and get instant predictions
- 🧠 Uses **VGG16** deep learning model from **TensorFlow**
- 📚 Automatically fetches top **interesting facts** from Wikipedia
- 🖼️ Clean and elegant **Streamlit UI** with sidebar navigation
- 💡 Intelligent Wikipedia result filtering
- 🔒 No data is stored — everything runs locally!

---

## 🛠️ Tech Stack

- Python 3.9+
- Streamlit
- TensorFlow + VGG16
- OpenCV + PIL (Image Processing)
- Wikipedia API
- NumPy

---

## 🚀 Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/wildlens-ai.git
cd wildlens-ai
2. Create a virtual environment (recommended)
bash
Copy
Edit
python -m venv venv
source venv/bin/activate     # On Linux/Mac
venv\Scripts\activate        # On Windows
3. Install the requirements
bash
Copy
Edit
pip install -r requirements.txt
4. Run the app
bash
Copy
Edit
streamlit run app.py
📂 Folder Structure
bash
Copy
Edit
wildlens-ai/
│
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
├── .gitignore           # Ignored files
└── README.md            # This file
📸 Sample Output
Upload an image of a lion, tiger, elephant, dog, or any animal and watch AI do its magic!

sql
Copy
Edit
✅ Predicted Animal: lion (95.67% confidence)
📚 Did You Know?
1. The lion is one of the big cats in the genus Panthera.
2. Lions live in groups called prides.
...
📜 License
This project is open-source and available under the MIT License.

✨ Author
Developed with 💖 by Vinodh – Final year Diploma CME student @ Dr. BRA GMR Polytechnic College, Rajahmundry.

yaml
Copy
Edit
