import csv
import requests
import re
import os
from configparser import ConfigParser

# --- CONFIGURATION LOADER ---
def load_configuration():
    """
    Loads configuration variables from an external 'config.ini' file.
    If the file does not exist, it creates one with default values.
    """
    config_file = 'config.ini'
    config = ConfigParser()

    # Default fallback values in case the file is missing or corrupted
    defaults = {
        'CSV_FILE': 'datos.csv',
        'PLUGIN_NAME': 'elementor',
        'MIN_WP_VERSION': '6.5',
        'MIN_PLUGIN_VERSION': '6.0'
    }

    if not os.path.exists(config_file):
        # Create a friendly structure for the user
        config['SETTINGS'] = defaults
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"ℹ️ '{config_file}' not found. A new one has been created with default settings.")
        return defaults

    try:
        config.read(config_file, encoding='utf-8')
        return {
            'CSV_FILE': config.get('SETTINGS', 'CSV_FILE', fallback=defaults['CSV_FILE']),
            'PLUGIN_NAME': config.get('SETTINGS', 'PLUGIN_NAME', fallback=defaults['PLUGIN_NAME']),
            'MIN_WP_VERSION': config.get('SETTINGS', 'MIN_WP_VERSION', fallback=defaults['MIN_WP_VERSION']),
            'MIN_PLUGIN_VERSION': config.get('SETTINGS', 'MIN_PLUGIN_VERSION', fallback=defaults['MIN_PLUGIN_VERSION'])
        }
    except:
        print("⚠️ Error reading 'config.ini'. Using internal default values.")
        return defaults

# Load settings from the external file at runtime
settings = load_configuration()

CSV_FILE = settings['CSV_FILE']
PLUGIN_NAME = settings['PLUGIN_NAME']
MIN_WP_VERSION = settings['MIN_WP_VERSION']
MIN_PLUGIN_VERSION = settings['MIN_PLUGIN_VERSION']

# Global headers configured to prevent 403 Forbidden blocks on WordPress SVN
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def parse_version(version_str):
    """
    Converts a version string (e.g., "6.9.4" or "6.0") into a tuple of integers
    to allow accurate mathematical comparisons. Returns None if invalid.
    """
    try:
        cleaned = re.sub(r'[^\d\.]', '', version_str)
        if not cleaned:
            return None
        return tuple(map(int, cleaned.split('.')))
    except:
        return None

def is_outdated(current_version, min_version):
    """
    Compares the current version against the minimum required version.
    Returns True if the current version is lower than the minimum.
    """
    current_parsed = parse_version(current_version)
    min_parsed = parse_version(min_version)
    
    if not current_parsed or not min_parsed:
        return False  
        
    return current_parsed < min_parsed

def get_wp_release_date(version):
    """Downloads the official WordPress releases page and extracts the launch date."""
    url = "https://wordpress.org/download/releases/"
    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            html_text = response.text
            pattern = rf'<th[^>]*scope="row"[^>]*>{re.escape(version)}</th>\s*<td[^>]*class="[^"]*date"[^>]*>([^<]+)</td>'
            
            match = re.search(pattern, html_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    except:
        pass
    return "Date not found"

def get_plugin_svn_date(plugin, version):
    """Queries the specific plugin version directory from the WP SVN to get its date."""
    url = f"https://plugins.svn.wordpress.org/{plugin}/tags/{version}/"
    try:
        response = requests.head(url, timeout=7, headers=headers)
        if response.status_code == 200:
            return response.headers.get('Last-Modified', 'Date not available')
    except:
        pass
    return "Not found"

def detect_wordpress_version(html_text):
    """Scans the HTML to find the WordPress version via generator tags or native scripts."""
    match_meta = re.search(r'<meta[^>]*name=["\']generator["\'][^>]*content=["\']WordPress\s+([\d\.]+)["\']', html_text, re.IGNORECASE)
    if match_meta:
        return match_meta.group(1)
    
    match_script = re.search(r'wp-includes/.*?ver=([\d\.]+)', html_text, re.IGNORECASE)
    if match_script:
        return match_script.group(1)
        
    return "WP Detected (Hidden Version)"

def detect_plugin_version(base_wp_url, plugin):
    """Fetches the plugin's readme.txt and extracts its stable version tag."""
    readme_url = f"{base_wp_url}/wp-content/plugins/{plugin}/readme.txt"
    try:
        response = requests.get(readme_url, timeout=5, headers=headers)
        if response.status_code == 200:
            match = re.search(r'Stable tag:\s*([\w\.]+)', response.text, re.IGNORECASE)
            if match:
                return match.group(1)
    except:
        pass
    return "Not installed / Protected"

def audit_client(url):
    """Performs a full audit on the site: verifies WP, identifies its version and the plugin version."""
    if not url or not isinstance(url, str): return None
    if not url.startswith('http'): url = 'http://' + url
    
    try:
        response_home = requests.get(url, timeout=5, headers=headers)
        if response_home.status_code != 200: return None
        
        html_text = response_home.text
        if "wp-content" not in html_text and "wp-includes" not in html_text:
            return None 
            
        wp_version = detect_wordpress_version(html_text)
        
        match_path = re.search(r'(https?://[^/]+/[^"\'>]*?)(?:wp-content|wp-includes)', html_text, re.IGNORECASE)
        if match_path:
            base_wp_url = match_path.group(1).rstrip('/')
        else:
            base_wp_url = response_home.url.rstrip('/')
        
        plugin_version = detect_plugin_version(base_wp_url, PLUGIN_NAME)
                
        return {
            'url': response_home.url, 
            'wp_version': wp_version,
            'plugin_version': plugin_version
        }
    except:
        pass
    return None

# --- MAIN EXECUTION ---
audit_results = []
print("🚀 Starting automated audit process...")
print(f"📊 Loaded Criteria -> WP Min: {MIN_WP_VERSION} | Plugin Min: {MIN_PLUGIN_VERSION}")

try:
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            site_url = row.get('site') or row.get('website')
            if not site_url: continue
            
            print(f"🔎 Analyzing: {site_url}")
            audit_data = audit_client(site_url)
            
            if audit_data:
                current_wp = audit_data['wp_version']
                current_plugin = audit_data['plugin_version']
                
                wp_needs_update = is_outdated(current_wp, MIN_WP_VERSION)
                plugin_needs_update = is_outdated(current_plugin, MIN_PLUGIN_VERSION)
                
                if wp_needs_update or plugin_needs_update:
                    status_flag = "⚠️ Outdated"
                else:
                    status_flag = "✅ OK"
                    
                wp_date = "N/A"
                if current_wp != "WP Detected (Hidden Version)":
                    print(f"   ℹ️ WordPress v{current_wp} found. Fetching official release date...")
                    wp_date = get_wp_release_date(current_wp)
                
                plugin_date = "N/A"
                if current_plugin != "Not installed / Protected":
                    print(f"   ℹ️ Plugin v{current_plugin} found. Fetching SVN release date...")
                    plugin_date = get_plugin_svn_date(PLUGIN_NAME, current_plugin)
                    
                audit_results.append({
                    'url': audit_data['url'],
                    'wp_version': current_wp,
                    'wp_date': wp_date,
                    'plugin_version': current_plugin,
                    'plugin_date': plugin_date,
                    'status': status_flag
                })
except FileNotFoundError:
    print(f"❌ Critical Error: The CSV file '{CSV_FILE}' was not found. Please check your config.ini.")
    exit(1)

# --- GENERATE MARKDOWN REPORT ---
with open('detectiu-audit-report.md', 'w', encoding='utf-8') as file:
    file.write(f"# 🎯 Lead Audit Report (WordPress & {PLUGIN_NAME.capitalize()})\n\n")
    file.write(f"**Audit Criteria:** WP Min Version: `{MIN_WP_VERSION}` | Plugin Min Version: `{MIN_PLUGIN_VERSION}`\n\n")
    file.write("| Website | Status | WP Version | WP Release Date | Plugin Version | Plugin Release Date |\n")
    file.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    
    for result in audit_results:
        file.write(f"| {result['url']} | {result['status']} | `{result['wp_version']}` | {result['wp_date']} | `{result['plugin_version']}` | {result['plugin_date']} |\n")

print("\n✅ Complete audit report successfully generated in 'informe_auditoria_completa.md'.")