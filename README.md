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

## How to Run the Project

To run the **SubstanceSearch.org** platform locally, follow these steps:

### Prerequisites

- **Python**: Ensure you have Python 3.8 or higher installed on your system.
- **Poetry**: A Python dependency management tool. Install it using:

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

### Steps to Run

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repo/SubstanceSearch.git
   cd SubstanceSearch
   ```

2. **Install Dependencies**
   Use Poetry to install all required dependencies:

   ```bash
   poetry install
   ```

3. **Run the Application**
   Start the Flask development server:

   ```bash
   poetry run python app.py
   ```

4. **Access the Platform**
   Open your browser and navigate to:

   ```
   http://127.0.0.1:5000
   ```

### Additional Notes

- **Data Files**: Ensure the `data/` folder contains the required files, including `final_updated_drugs.json` and `leaderboard.csv`.
- **Static and Templates**: Verify that the `static/` and `templates/` folders are populated as described in the project structure.
- **Debug Mode**: The application runs in debug mode by default, which reloads automatically on code changes.

**Website**: [SubstanceSearch.org](https://substancesearch.org)  
**Alternative URL**: [search.dedgrl.com](https://search.dedgrl.com)
