# 📊 MGF Dataset Explorer (Shiny App)

An interactive **Shiny for Python** web app for browsing and analyzing climate-related policy actions by central banks and financial regulators — developed by the **Macro and Green Finance Lab at Peking University (MGF@PKU)**.

This tool is designed as a **template** for research, presentation, and educational purposes. It is not intended for local hosting by the general public — instead, it showcases how one might integrate real-time GitHub-hosted datasets into a Shiny app.

<!-- ![screenshot](docs/screenshot.png) -->

---

## 🔍 Overview

This app visualizes a curated dataset of climate and sustainability-related regulatory measures from **major economies (G20, EU, etc.) since 2021**. Features include:

- 🔎 Filtering by region, policy type, year, and keyword
- 🧾 Structured detail view for each policy
- 🔗 Links to original sources
- 📥 Export of filtered results (CSV)

Powered by:
- [`shiny`](https://shiny.posit.co/py/) for interactivity
- [`polars`](https://pola.rs/) for fast data wrangling
- GitHub API for real-time data retrieval
- Custom CSS + JS enhancements

---

## 📦 Features

- Paginated and stylized data table
- Clickable rows with detailed policy views
- CSV export of current filtered results
- Integrated GitHub data sync (via authenticated API)
- Modern UI with iconography, tooltips, and layout styling

---

## 🧪 Setup (For Contributors Only)

This app uses GitHub as a remote data backend. If you're customizing or extending the app:

### 1. Clone the repo

```bash
git clone https://github.com/MGFPKU/MGF_dataset_shiny.git
cd MGF_dataset_shiny
```

### 2. Install dependencies

We use `uv` for fast dependency resolution:

```bash
uv sync
```

### 3. Authentication

> ⚠️ We do not publish a GitHub token in this repo.
If you need access for development or testing, contact the maintainers for a personal access token (PAT) with read-only access to the dataset repository.

You’ll need to set the token in a `.env` file like:

```env
GITHUB_TOKEN=ghp_...
```

### 4. Run the app

```bash
python -m shiny run --reload  app.py
```

Then open your browser to:

```bash
http://localhost:8000
```

Or more conveniently, install the `shiny` extension to Positron/VS Code and press the Run button.

---

## 📁 Data Source

The dataset is hosted in a *private* public GitHub repository along with our scraping scripts. We apologize for the inconvenience. But the dataset provided through the app is updated in real-time and contains most information available on the original source.

---

## 🏛️ Credits


Developed by the **[Macro and Green Finance Lab](https://mgflab.nsd.pku.edu.cn/en/AboutUs/OurTeam/index.htm)**, Peking University (MGF@PKU).

For academic use, adaptation, or inquiries, please contact us directly.