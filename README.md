# ⛽ Local Fuel Price Tracker & Analyzer

This project is a Python-based web application designed to help users track daily petrol and diesel prices for New Delhi (and easily extensible to other cities), analyze trends, and receive data-driven suggestions for optimal refueling times. The application leverages web scraping for data collection, a Streamlit interface for visualization, and GitHub Actions for automated daily updates and continuous deployment.

## ✨ Live Demo

[**View the Live Application on Streamlit Cloud**](https://fuel-price-tracker.streamlit.app/)

## 🚀 Features

* **Daily Fuel Price Tracking:** Automatically fetches the latest petrol and diesel prices for New Delhi.

* **Historical Data Visualization:** Displays interactive line charts showing price trends over the last 30 days.

* **Trend Analysis & Suggestions:** Provides a concise summary of recent price movements and offers actionable advice on when to refuel.

* **Automated Updates:** Data is automatically updated daily via a scheduled GitHub Actions workflow.

* **Continuous Deployment:** The application is hosted on Streamlit Cloud and automatically redeploys with fresh data.

## ⚙️ How It Works

1. **Data Fetching (`fetch_fuel_data.py`):**

   * The `fetch_fuel_data.py` script uses `requests` to fetch HTML content from `goodreturns.in` (and other fallback sources like `acko.com`, `bankbazaar.com`, `iocl.com`).

   * `BeautifulSoup` is then used to parse the HTML and extract the current petrol and diesel prices for New Delhi.

   * This data is appended to `fuel_prices.csv`.

2. **Automated Workflow (GitHub Actions):**

   * A GitHub Actions workflow (`.github/workflows/daily_update.yml`) is scheduled to run daily at 00:00 UTC.

   * This workflow executes `fetch_fuel_data.py`.

   * After the data is updated, the workflow commits the new `fuel_prices.csv` back to the repository.

3. **Web Application (`app.py`):**

   * The `app.py` script, built with Streamlit, reads the `fuel_prices.csv` file.

   * It displays the latest prices, a historical chart, and a trend analysis.

   * `@st.cache_data(ttl=3600)` ensures the app periodically reloads data from the updated CSV.

4. **Deployment (Streamlit Cloud):**

   * The Streamlit application is deployed on Streamlit Cloud, which automatically detects changes in the GitHub repository (including updates to `fuel_prices.csv`) and redeploys the app.

## 💻 Setup & Installation (Local)

To run this project on your local machine:

1. **Clone the Repository:**
   * git clone https://github.com/your-username/fuel-price-tracker.git
   * cd fuel-price-tracker

*(Replace `your-username` with your actual GitHub username)*

2. **Create a Virtual Environment (Recommended):**
   * python -m venv venv
   * source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies:**
   * pip install -r requirements.txt
  
4. **Fetch Initial Data:**
  Run the data fetching script once to populate `fuel_prices.csv`:
   * python fetch_fuel_data.py
*(Check the console output for success messages and any scraping errors. You might need to manually inspect the target websites if scraping fails due to HTML changes.)*

5. **Run the Streamlit App:**
   * streamlit run app.py

This will open the application in your web browser.

## ☁️ Deployment (Streamlit Cloud & GitHub Actions)

This project is designed for free, automated deployment:

1. **GitHub Repository:** Ensure your project is pushed to a public GitHub repository.

2. **Streamlit Cloud:** Deploy your `app.py` to [Streamlit Cloud](https://share.streamlit.io/) by connecting it to your GitHub repository. Streamlit Cloud handles the hosting and automatic redeployment on new commits.

3. **GitHub Actions:** The `.github/workflows/daily_update.yml` file configures a GitHub Action that:

* Runs `fetch_fuel_data.py` daily.

* Commits any changes to `fuel_prices.csv` back to your repository.

* This commit then triggers Streamlit Cloud to redeploy your app with the latest data.

## 🤝 Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to improve the scraping logic for other cities/sources, feel free to:

1. Fork the repository.

2. Create a new branch (`git checkout -b feature/your-feature`).

3. Make your changes.

4. Commit your changes (`git commit -m 'feat: Add new feature'`).

5. Push to the branch (`git push origin feature/your-feature`).

6. Open a Pull Request.

## 📄 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).
