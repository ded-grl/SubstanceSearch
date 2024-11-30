# SubstanceSearch.org / search.dedgrl.com

**SubstanceSearch.org** is a harm reduction-focused platform designed to provide accurate, accessible, and up-to-date information about psychoactive substances. Built with community contributions and evidence-based resources, it serves as a tool to empower users to make informed decisions, promote safety, and reduce risks associated with substance use.

## Key Features
- 🔍 **Search Functionality**: Quickly search for detailed information on substances, including their effects, dosage guidelines, onset and duration, and potential risks.
- 📚 **Resource Database**: A curated collection of research papers, studies, and data to deepen understanding of various substances.
- 💊 **Dosage Information**: Visual charts and detailed tables outlining dosage levels for different routes of administration.
- 🛡️ **Harm Reduction**: Focused on minimizing risks by providing warnings, interactions, and combination guidelines.
- 🌐 **Community-Driven**: Contributors from various fields (feedback, research, and development) help keep the platform accurate and up-to-date.

## Why We Exist
SubstanceSearch.org was created to fill a crucial gap in harm reduction education by providing:
1. **Accurate Information**: Combat misinformation and myths around substance use.
2. **Accessibility**: Make research-backed substance data easy to understand for everyone.
3. **Community Support**: Foster a collaborative environment where contributors can share insights and help others stay informed.

Visit the [Discord Server](https://discord.gg/wFPB9xYRBN) to get started and select your contribution role! 💕

## How It Works
1. **Search**: Enter a substance name to find detailed information.
2. **Explore**: Browse substances by category or use our interactive tools for dosage and effects.
3. **Contribute**: Join our community to submit resources, give feedback, or contribute code.

## Acknowledgments
- 💕 **Data Powered by TripSit**: Leveraging TripSit's expertise to enhance the quality and reliability of our substance information.
- 🌟 Supported by an amazing community of harm reduction advocates and contributors.

**Website**: [SubstanceSearch.org](https://substancesearch.org)  
**Alternative URL**: [search.dedgrl.com](https://search.dedgrl.com)

---
## **How to run Substance Search Locally**
Follow these instructions to run the app locally on your machine.

### **Prerequisites**

1. **Python**: Install Python 3.7 or higher from [python.org](https://www.python.org/downloads/).
   - During installation, ensure you check the box **"Add Python to PATH"**.
   - Verify the installation by running:
     ```bash
     python --version
     ```

2. **Pip**: Pip is included with Python installations. Verify by running:
     ```bash
     pip --version
     ```

---

### **Installation**

1. **Install Required Libraries**
    Run the following command to install all dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. **Directory Structure**
    Ensure your project folder is structured like this:
    ```
    SubstanceSearch/
    ├── app.py
    ├── requirements.txt
    ├── data/
    │  ├── final_updated_drugs.json
    │  └── leaderboard.csv
    ├── templates/
    │   ├── index.html
    │   ├── leaderboard.html
    │   ├── category.html
    │   └── substance.html
    └── static/
        ├── styles.css
        ├── favicon.ico
        ├── SubstanceSearchPill.png
        └── autocomplete.js
    ```

---

### **Running the App**

1. **Start the Flask Server**
    Navigate to the project directory and run:
    ```bash
    python app.py
    ```

2. **Access the App**
    Open your browser and visit:
    ```
    http://127.0.0.1:5000/
    ```

---

### **Stopping the App**

To stop the app, press `CTRL+C` in the terminal where the app is running.

---

### **Troubleshooting**

1. **Missing Libraries**: If you see a `ModuleNotFoundError`, install the missing library:
    ```bash
    pip install <library_name>
    ```

2. **Flask Not Installed**: Install Flask using:
    ```bash
    pip install flask
    ```
    
3. **Port in Use**: If the port `5000` is already in use, specify a different port when running the app:
    ```bash
    python app.py --port=5001
    ```
