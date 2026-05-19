# 🎯 DETECTIU MAPS: WordPress Lead Auditor

An automated, lightweight Python script designed for digital agencies and freelancers to audit potential leads. It parses a list of source websites from a CSV file, detects if they are running WordPress, identifies the core and target plugin versions, and generates a structured Markdown compatibility report based on customizable criteria.

## 🚀 Features

- **Dynamic WP Path Detection:** Automatically handles protocol upgrades (HTTP to HTTPS) and subdirectory installations (e.g., `https://example.com/wp/`).
- **Smart Version Comparison:** Parses version strings (e.g., `6.9.4`, `6.0`) into integer tuples to perform mathematically accurate version comparisons.
- **Automated Metadata Extraction:** Fetches official core release dates from WordPress.org and plugin version release timestamps from the official SVN repository.
- **Anti-Bot Bypass:** Utilizes optimized browser headers to prevent `403 Forbidden` firewall blocks on remote repositories.
- **External Configuration:** Simple `config.ini` architecture allowing non-technical users to change audit targets instantly without touching the code.
- **Zero Heavy Dependencies:** Built entirely using Python standard libraries and the `requests` package.



## 🛠️ Installation & Setup

### 1. Prerequisites
Before running the script, you need to ensure that Python and its package manager (pip) are installed on your system:

- **Python 3.x:** Download and install it from [python.org](https://www.python.org/). Make sure to check the box that says **"Add Python to PATH"** during the installation process.
- **pip:** This is usually bundled automatically with modern Python installers. You can verify both installations by running these commands in your terminal/command prompt:
  ```bash
  python3 --version
  pip3 --version
  ```

### 2. Project Installation

1. **Clone or download** this repository to your local machine:
```bash
git clone [https://github.com/your-username/detectiu-maps.git](https://github.com/your-username/detectiu-maps.git)
cd detectiu-maps

```


2. **Install the required package:** The script relies on the third-party `requests` library to fetch web data. Install it using pip:

```bash
pip3 install requests
```


*(Note: Built-in modules like `csv`, `re`, `os`, and `configparser` used in the script do not require manual installation).*
3. **Prepare your data:** Ensure you have your list of target domains in a file named `datos.csv` (or the custom name specified in your configuration) containing a `site` or `website` column.


## ⚙️ Configuration (`config.ini`)

On its first execution, the script automatically generates a default `config.ini` file in the root directory. You can easily edit this file using any text editor to modify the audit rules:

```ini
[SETTINGS]
csv_file = data.csv
plugin_name = contact-form-7
min_wp_version = 6.9
min_plugin_version = 6.1.5

```

### Configuration Fields:

* `csv_file`: Name or path of your target CSV lead file.
* `plugin_name`: The technical slug of the WordPress plugin you want to audit (e.g., `contact-form-7`, `elementor`, or `woocommerce`).
* `min_wp_version`: The minimum acceptable WordPress core version. Anything below this flags the site as `⚠️ Outdated`.
* `min_plugin_version`: The minimum acceptable version for the chosen plugin.


## 🖥️ Usage

Simply run the script from your terminal:

```bash
python3 detectiu.py
```

### Console Output Example:

```text
🚀 Starting automated audit process...
📊 Loaded Criteria -> WP Min: 6.5 | Plugin Min: 6.0
🔎 Analyzing: [http://www.example.com/](http://www.example.com/)
   ℹ️ WordPress v6.4.2 found. Fetching official release date...
   ⚠️ Plugin v5.8.7 found. Fetching SVN release date...
   
✅ Complete audit report successfully generated in 'detectiu-audit-report.md'.

```


## 📊 Output Report

The script outputs a comprehensive markdown file named `detectiu-audit-report.md`. It includes a summary table indicating whether the targets are up to date or require technical maintenance:

| Website | Status | WP Version | WP Release Date | Plugin Version | Plugin Release Date |
| --- | --- | --- | --- | --- | --- |
| `https://example-ok.com/` | ✅ OK | `6.6.1` | July 23, 2024 | `6.1.2` | Date not available |
| `https://example-old.org/` | ⚠️ Outdated | `6.2.0` | March 29, 2023 | `5.9.1` | Wed, 12 Feb 2025... |


## 🛡️ License

This project is open-source and available under the [MIT License](LICENSE).
