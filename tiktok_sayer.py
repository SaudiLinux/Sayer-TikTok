#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TikTok-Sayer - TikTok OSINT Tool
Developed by: Saudi Linux
Email: SayerLinux@gmail.com

This tool provides an interactive user interface for analyzing TikTok accounts
using their pseudonym. It allows you to extract various information including
followers, following, emails, phone numbers, and tagged users.
"""

import os
import sys
import json
import time
import random
import threading
import webbrowser
import re
import logging
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ratelimit import limits, sleep_and_retry
from retrying import retry
from urllib.parse import urlparse

# Import customtkinter for modern UI
try:
    import customtkinter as ctk
except ImportError:
    messagebox.showerror("Error", "CustomTkinter is not installed. Please install it using 'pip install customtkinter'")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tiktok_sayer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TikTok-Sayer")

# TikTok URLs and constants
TIKTOK_BASE_URL = "https://www.tiktok.com/@{}"
TIKTOK_API_URL = "https://www.tiktok.com/node/share/user/@{}"
REQUEST_DELAY = 2  # Seconds between requests to avoid rate limiting
MAX_RETRIES = 3    # Maximum number of retries for failed requests

# Rate limit: 10 calls per minute (conservative to avoid blocking)
@sleep_and_retry
@limits(calls=10, period=60)
def rate_limited_request(url, headers=None):
    """Make a rate-limited request to avoid TikTok blocking"""
    ua = UserAgent()
    default_headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.tiktok.com/',
        'DNT': '1',
    }
    
    if headers:
        default_headers.update(headers)
    
    return requests.get(url, headers=default_headers, timeout=10)

@retry(stop_max_attempt_number=MAX_RETRIES, wait_fixed=2000)
def retry_request(url, headers=None):
    """Retry a request multiple times if it fails"""
    return rate_limited_request(url, headers)

def setup_webdriver():
    """Set up a headless Chrome WebDriver for scraping"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Add random user agent
    ua = UserAgent()
    options.add_argument(f"--user-agent={ua.random}")
    
    # Create and return the WebDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Constants
TIKTOK_BASE_URL = "https://www.tiktok.com/@{}"
TIKTOK_API_URL = "https://www.tiktok.com/api/user/detail/?uniqueId={}"
REQUEST_DELAY = 2  # Seconds between requests to avoid rate limiting
MAX_RETRIES = 3

# Rate limiting decorator - 10 calls per minute
@sleep_and_retry
@limits(calls=10, period=60)
def rate_limited_request(url, headers=None, params=None):
    """Make a rate-limited request to avoid TikTok blocking"""
    try:
        if headers is None:
            headers = {
                'User-Agent': UserAgent().random,
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.tiktok.com/',
            }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise

# Retry decorator for failed requests
@retry(stop_max_attempt_number=MAX_RETRIES, wait_fixed=2000)
def retry_request(url, headers=None, params=None):
    """Retry failed requests"""
    return rate_limited_request(url, headers, params)

# Setup Selenium WebDriver
def setup_webdriver():
    """Setup and return a configured Chrome WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"user-agent={UserAgent().random}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {str(e)}")
        raise

class TikTokSayer(ctk.CTk):
    """Main application class for TikTok-Sayer"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("TikTok-Sayer - TikTok OSINT Tool")
        self.geometry("900x600")
        self.minsize(800, 600)
        
        # Initialize variables
        self.target_username = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Ready")
        self.result_data = {}
        self.is_running = False
        
        # Create UI elements
        self.create_ui()
        
        # Set icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
    
    def create_ui(self):
        """Create the user interface"""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title and description
        title_label = ctk.CTkLabel(
            header_frame, 
            text="TikTok-Sayer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 0))
        
        description_label = ctk.CTkLabel(
            header_frame, 
            text="An OSINT tool for analyzing TikTok accounts",
            font=ctk.CTkFont(size=14)
        )
        description_label.pack(pady=(0, 10))
        
        # Input frame
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Username input
        username_label = ctk.CTkLabel(input_frame, text="TikTok Username:")
        username_label.pack(side="left", padx=(10, 5))
        
        username_entry = ctk.CTkEntry(input_frame, textvariable=self.target_username, width=200)
        username_entry.pack(side="left", padx=5)
        username_entry.focus()
        
        # Analyze button
        analyze_button = ctk.CTkButton(
            input_frame, 
            text="Analyze Account", 
            command=self.start_analysis
        )
        analyze_button.pack(side="left", padx=10)
        
        # Options frame
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        # Checkboxes for options
        self.get_followers = ctk.BooleanVar(value=True)
        followers_check = ctk.CTkCheckBox(options_frame, text="Get Followers", variable=self.get_followers)
        followers_check.pack(side="left", padx=10, pady=10)
        
        self.get_following = ctk.BooleanVar(value=True)
        following_check = ctk.CTkCheckBox(options_frame, text="Get Following", variable=self.get_following)
        following_check.pack(side="left", padx=10, pady=10)
        
        self.get_emails = ctk.BooleanVar(value=True)
        emails_check = ctk.CTkCheckBox(options_frame, text="Get Emails", variable=self.get_emails)
        emails_check.pack(side="left", padx=10, pady=10)
        
        self.get_phones = ctk.BooleanVar(value=True)
        phones_check = ctk.CTkCheckBox(options_frame, text="Get Phone Numbers", variable=self.get_phones)
        phones_check.pack(side="left", padx=10, pady=10)
        
        self.get_tagged = ctk.BooleanVar(value=True)
        tagged_check = ctk.CTkCheckBox(options_frame, text="Get Tagged Users", variable=self.get_tagged)
        tagged_check.pack(side="left", padx=10, pady=10)
        
        # Create tabview for results
        self.results_tabview = ctk.CTkTabview(self.main_frame)
        self.results_tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.results_tabview.add("Profile")
        self.results_tabview.add("Followers")
        self.results_tabview.add("Following")
        self.results_tabview.add("Emails")
        self.results_tabview.add("Phone Numbers")
        self.results_tabview.add("Tagged Users")
        self.results_tabview.add("Log")
        
        # Profile tab content
        profile_frame = ctk.CTkFrame(self.results_tabview.tab("Profile"))
        profile_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Profile info will be populated dynamically
        self.profile_info_frame = ctk.CTkScrollableFrame(profile_frame)
        self.profile_info_frame.pack(fill="both", expand=True)
        
        # Followers tab content
        followers_frame = ctk.CTkFrame(self.results_tabview.tab("Followers"))
        followers_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.followers_text = ctk.CTkTextbox(followers_frame)
        self.followers_text.pack(fill="both", expand=True)
        
        # Following tab content
        following_frame = ctk.CTkFrame(self.results_tabview.tab("Following"))
        following_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.following_text = ctk.CTkTextbox(following_frame)
        self.following_text.pack(fill="both", expand=True)
        
        # Emails tab content
        emails_frame = ctk.CTkFrame(self.results_tabview.tab("Emails"))
        emails_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.emails_text = ctk.CTkTextbox(emails_frame)
        self.emails_text.pack(fill="both", expand=True)
        
        # Phone Numbers tab content
        phones_frame = ctk.CTkFrame(self.results_tabview.tab("Phone Numbers"))
        phones_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.phones_text = ctk.CTkTextbox(phones_frame)
        self.phones_text.pack(fill="both", expand=True)
        
        # Tagged Users tab content
        tagged_frame = ctk.CTkFrame(self.results_tabview.tab("Tagged Users"))
        tagged_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tagged_text = ctk.CTkTextbox(tagged_frame)
        self.tagged_text.pack(fill="both", expand=True)
        
        # Log tab content
        log_frame = ctk.CTkFrame(self.results_tabview.tab("Log"))
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = ctk.CTkTextbox(log_frame)
        self.log_text.pack(fill="both", expand=True)
        
        # Status bar
        status_frame = ctk.CTkFrame(self.main_frame, height=30)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var)
        status_label.pack(side="left", padx=10)
        
        # Export button
        export_button = ctk.CTkButton(
            status_frame, 
            text="Export Results", 
            command=self.export_results
        )
        export_button.pack(side="right", padx=10)
        
        # About button
        about_button = ctk.CTkButton(
            status_frame, 
            text="About", 
            command=self.show_about,
            width=80
        )
        about_button.pack(side="right", padx=10)
    
    def log(self, message):
        """Add message to log with timestamp and log to file"""
        # Log to file using the configured logger
        logger.info(message)
        
        # Display in UI
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.update_idletasks()
    
    def start_analysis(self):
        """Start the analysis process in a separate thread"""
        username = self.target_username.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a TikTok username")
            return
        
        if self.is_running:
            messagebox.showinfo("Info", "Analysis is already running")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Start analysis in a separate thread
        self.is_running = True
        threading.Thread(target=self.analyze_account, daemon=True).start()
    
    def clear_results(self):
        """Clear all result fields"""
        # Clear all text widgets
        for widget in [self.followers_text, self.following_text, self.emails_text, 
                      self.phones_text, self.tagged_text, self.log_text]:
            widget.delete("0.0", "end")
        
        # Clear profile info
        for widget in self.profile_info_frame.winfo_children():
            widget.destroy()
        
        # Reset result data
        self.result_data = {}
    
    def analyze_account(self):
        """Main analysis function"""
        try:
            username = self.target_username.get().strip()
            self.update_status(f"Analyzing @{username}...")
            self.log(f"Starting analysis for user: @{username}")
            
            # Get profile information
            self.log("Fetching profile information...")
            profile_info = self.get_profile_info(username)
            
            if not profile_info:
                self.update_status("Error: Could not retrieve profile information")
                self.log("Failed to retrieve profile information")
                self.is_running = False
                return
            
            self.result_data['profile'] = profile_info
            self.display_profile_info(profile_info)
            
            # Get followers if selected
            if self.get_followers.get():
                self.log("Fetching followers...")
                self.update_status("Fetching followers...")
                followers = self.get_user_followers(username)
                self.result_data['followers'] = followers
                self.display_followers(followers)
            
            # Get following if selected
            if self.get_following.get():
                self.log("Fetching following...")
                self.update_status("Fetching following...")
                following = self.get_user_following(username)
                self.result_data['following'] = following
                self.display_following(following)
            
            # Get emails if selected
            if self.get_emails.get():
                self.log("Extracting emails...")
                self.update_status("Extracting emails...")
                emails = self.extract_emails(username)
                self.result_data['emails'] = emails
                self.display_emails(emails)
            
            # Get phone numbers if selected
            if self.get_phones.get():
                self.log("Extracting phone numbers...")
                self.update_status("Extracting phone numbers...")
                phones = self.extract_phone_numbers(username)
                self.result_data['phones'] = phones
                self.display_phone_numbers(phones)
            
            # Get tagged users if selected
            if self.get_tagged.get():
                self.log("Finding tagged users...")
                self.update_status("Finding tagged users...")
                tagged = self.get_tagged_users(username)
                self.result_data['tagged'] = tagged
                self.display_tagged_users(tagged)
            
            self.update_status(f"Analysis completed for @{username}")
            self.log("Analysis completed successfully")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log(f"Error during analysis: {str(e)}")
        finally:
            self.is_running = False
    
    def get_profile_info(self, username):
        """Get profile information for the given username using web scraping"""
        self.log(f"Fetching profile information for @{username}...")
        profile_data = {}
        
        try:
            # Try using TikTok API first
            api_url = TIKTOK_API_URL.format(username)
            self.log("Attempting to fetch data from TikTok API...")
            
            try:
                response = retry_request(api_url)
                if response.status_code == 200:
                    data = response.json()
                    if 'userInfo' in data:
                        user_info = data['userInfo']
                        stats = user_info.get('stats', {})
                        
                        profile_data = {
                            'username': username,
                            'display_name': user_info.get('user', {}).get('nickname', f"{username}"),
                            'bio': user_info.get('user', {}).get('signature', ""),
                            'follower_count': stats.get('followerCount', 0),
                            'following_count': stats.get('followingCount', 0),
                            'likes': stats.get('heartCount', 0),
                            'video_count': stats.get('videoCount', 0),
                            'verified': user_info.get('user', {}).get('verified', False),
                            'private': user_info.get('user', {}).get('privateAccount', False),
                            'join_date': datetime.now().strftime("%Y-%m-%d")  # API doesn't provide join date
                        }
                        self.log("Successfully fetched data from TikTok API")
                        return profile_data
            except Exception as e:
                self.log(f"API request failed: {str(e)}. Falling back to web scraping.")
            
            # Fallback to web scraping if API fails
            self.log("Using web scraping to fetch profile data...")
            profile_url = TIKTOK_BASE_URL.format(username)
            
            # Use Selenium for JavaScript-rendered content
            driver = setup_webdriver()
            driver.get(profile_url)
            
            try:
                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2, .user-info, .profile-info"))
                )
                
                # Extract profile information
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract display name (updated selectors for 2023-2024 TikTok UI)
                display_name_elem = soup.select_one("h1, h2, .user-info h1, .nickname, .profile-name, .tiktok-1d3irth-H2ShareTitle, [data-e2e='user-subtitle'], .css-1r3ljid-H2ShareTitle")
                
                # Data validation: Ensure we have a valid display name
                if display_name_elem and display_name_elem.text.strip():
                    display_name = display_name_elem.text.strip()
                else:
                    display_name = username
                    self.log("Warning: Could not extract display name, using username instead")
                
                # Extract bio (updated selectors)
                bio_elem = soup.select_one(".user-bio, .signature, .profile-bio, .tiktok-1n8z9r7-H2ShareDesc, [data-e2e='user-bio'], .css-1aq6wh4-H2ShareDesc")
                bio = bio_elem.text.strip() if bio_elem else ""
                
                # Data validation: Log if bio is empty
                if not bio:
                    self.log("Note: User bio is empty or could not be extracted")
                
                # Extract stats (followers, following, likes) with updated selectors
                stats_elems = soup.select(".count-infos span, .user-stats span, .profile-stats span, .tiktok-7k173h-StrongText, [data-e2e='followers-count'], [data-e2e='following-count'], [data-e2e='likes-count'], .css-1aq6wh4-StrongText")
                stats_text = [elem.text.strip() for elem in stats_elems if elem and elem.text.strip()]
                
                # Data validation: Check if we found any stats
                if not stats_text:
                    self.log("Warning: Could not extract user statistics, values may be incorrect")
                    # Try alternative selectors for stats
                    stats_containers = soup.select(".tiktok-xeexlu-DivNumber, .tiktok-1kd69pk-DivNumber")
                    stats_text.extend([elem.text.strip() for elem in stats_containers if elem and elem.text.strip()])
                
                # Parse stats (handle K, M abbreviations) with improved data validation
                follower_count = 0
                following_count = 0
                likes = 0
                video_count = 0
                
                # Try to find stats by looking for text patterns
                for i, text in enumerate(stats_text):
                    try:
                        # Check for data-e2e attributes first (more reliable)
                        if any(keyword in text.lower() for keyword in ['follower', 'fans', 'متابع', 'مشترك']):
                            value = stats_text[i+1] if i+1 < len(stats_text) else "0"
                            follower_count = self._parse_count(value)
                            # Data validation: Log suspicious values
                            if follower_count > 500000000:  # Unlikely to have more than 500M followers
                                self.log(f"Warning: Suspicious follower count detected: {value} -> {follower_count}")
                                follower_count = 0
                        elif any(keyword in text.lower() for keyword in ['following', 'متابَع', 'يتابع']):
                            value = stats_text[i+1] if i+1 < len(stats_text) else "0"
                            following_count = self._parse_count(value)
                            # Data validation: Log suspicious values
                            if following_count > 10000:  # TikTok limits following to around 10,000
                                self.log(f"Warning: Suspicious following count detected: {value} -> {following_count}")
                        elif any(keyword in text.lower() for keyword in ['like', 'إعجاب']):
                            value = stats_text[i+1] if i+1 < len(stats_text) else "0"
                            likes = self._parse_count(value)
                        elif any(keyword in text.lower() for keyword in ['video', 'فيديو']):
                            value = stats_text[i+1] if i+1 < len(stats_text) else "0"
                            video_count = self._parse_count(value)
                    except Exception as e:
                        self.log(f"Error parsing stat value: {str(e)}")
                        continue
                
                # Data validation: Check for missing values
                if follower_count == 0 and following_count == 0 and likes == 0:
                    self.log("Warning: Could not parse any user statistics, values may be incorrect")
                
                # Check for verification badge
                verified = bool(soup.select_one(".verified-badge, .verify-badge"))
                
                # Check for private account indicator
                private = bool(soup.select_one(".private-account, .lock-icon"))
                
                # Data validation using the validate_data method
                # Validate username (required field)
                username = self.validate_data(username, 'username', default_value="unknown")
                
                # Validate display name (use username as fallback)
                display_name = self.validate_data(display_name, 'string', default_value=username)
                
                # Validate bio (can be empty)
                bio = self.validate_data(bio, 'string', default_value="")
                
                # Validate counts with minimum value of 0 and reasonable maximum values
                follower_count = self.validate_data(follower_count, 'int', default_value=0, min_value=0, max_value=1000000000)
                following_count = self.validate_data(following_count, 'int', default_value=0, min_value=0, max_value=10000)
                likes = self.validate_data(likes, 'int', default_value=0, min_value=0, max_value=10000000000)
                video_count = self.validate_data(video_count, 'int', default_value=0, min_value=0, max_value=10000)
                
                # Return the profile data with validated values
                profile_data = {
                    'username': username,
                    'display_name': display_name,
                    'bio': bio,  # Already validated to never be None
                    'follower_count': follower_count,
                    'following_count': following_count,
                    'likes': likes,
                    'video_count': video_count,
                    'verified': bool(verified),  # Ensure boolean type
                    'private': bool(private),    # Ensure boolean type
                    'join_date': datetime.now().strftime("%Y-%m-%d"),  # Join date not easily available
                    'data_source': 'web_scraping',  # Indicate data source for transparency
                    'extraction_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
                }
                
                self.log("Successfully scraped profile data")
            except Exception as e:
                self.log(f"Error during web scraping: {str(e)}")
            finally:
                driver.quit()
                
        except Exception as e:
            self.log(f"Failed to get profile info: {str(e)}")
            # Return basic profile with username if all methods fail
            # Validate username using the validate_data method
            username = self.validate_data(username, 'username', default_value="unknown")
                
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            profile_data = {
                'username': username,
                'display_name': username,  # Use username as display name in fallback
                'bio': "",
                'follower_count': 0,
                'following_count': 0,
                'likes': 0,
                'video_count': 0,
                'verified': False,
                'private': False,
                'join_date': datetime.now().strftime("%Y-%m-%d"),
                'data_source': 'fallback',  # Indicate this is fallback data
                'extraction_timestamp': current_time,
                'error': self.validate_data(str(e), 'string', default_value="Unknown error")[:200]  # Include truncated error message for debugging
            }
            self.log("Returning fallback profile data due to extraction failure")
            
        return profile_data
        
    def validate_data(self, data, data_type, default_value=None, min_value=None, max_value=None):
        """General data validation function for different types of data
        
        Args:
            data: The data to validate
            data_type: Type of data ('string', 'int', 'float', 'url', 'email', 'username')
            default_value: Default value to return if validation fails
            min_value: Minimum value for numeric types
            max_value: Maximum value for numeric types
            
        Returns:
            Validated data or default value
        """
        if data is None:
            return default_value
            
        try:
            if data_type == 'string':
                # Validate string
                if not isinstance(data, str):
                    data = str(data)
                data = data.strip()
                if not data:
                    return default_value
                return data
                
            elif data_type == 'int':
                # Validate integer
                if isinstance(data, str):
                    # Try to parse string as int
                    data = self._parse_count(data)
                else:
                    data = int(data)
                    
                # Apply min/max constraints
                if min_value is not None and data < min_value:
                    self.log(f"Warning: Value {data} is below minimum {min_value}, using minimum")
                    return min_value
                if max_value is not None and data > max_value:
                    self.log(f"Warning: Value {data} exceeds maximum {max_value}, using maximum")
                    return max_value
                return data
                
            elif data_type == 'float':
                # Validate float
                if isinstance(data, str):
                    data = float(data.replace(',', ''))
                else:
                    data = float(data)
                    
                # Apply min/max constraints
                if min_value is not None and data < min_value:
                    return min_value
                if max_value is not None and data > max_value:
                    return max_value
                return data
                
            elif data_type == 'url':
                # Validate URL
                if not isinstance(data, str):
                    return default_value
                    
                data = data.strip()
                if not data:
                    return default_value
                    
                # Basic URL validation
                if not data.startswith(('http://', 'https://')):
                    self.log(f"Warning: Invalid URL format: {data}")
                    return default_value
                    
                # More thorough validation
                try:
                    result = urlparse(data)
                    if not all([result.scheme, result.netloc]):
                        self.log(f"Warning: Invalid URL structure: {data}")
                        return default_value
                except Exception:
                    return default_value
                    
                return data
                
            elif data_type == 'email':
                # Validate email
                if not isinstance(data, str):
                    return default_value
                    
                data = data.strip()
                if not data:
                    return default_value
                    
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data):
                    self.log(f"Warning: Invalid email format: {data}")
                    return default_value
                    
                return data
                
            elif data_type == 'username':
                # Validate TikTok username
                if not isinstance(data, str):
                    return default_value
                    
                data = data.strip()
                if not data:
                    return default_value
                    
                # Remove @ if present
                if data.startswith('@'):
                    data = data[1:]
                    
                # Basic username validation (alphanumeric, underscore, period)
                username_pattern = r'^[a-zA-Z0-9_.]+$'
                if not re.match(username_pattern, data):
                    self.log(f"Warning: Invalid username format: {data}")
                    return default_value
                    
                return data
            
            else:
                # Unknown data type
                self.log(f"Warning: Unknown data type for validation: {data_type}")
                return default_value
                
        except Exception as e:
            self.log(f"Error validating {data_type} data: {str(e)}")
            return default_value
    
    def _parse_count(self, count_str):
        """Parse count string with K, M, B abbreviations and improved data validation"""
        if not count_str:
            return 0
            
        try:
            # Clean the input string
            count_str = str(count_str).strip()
            
            # Handle Arabic/Persian numbers
            arabic_to_english = {
                '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
            }
            
            for ar, en in arabic_to_english.items():
                count_str = count_str.replace(ar, en)
            
            # Remove commas, spaces, and other non-numeric characters
            count_str = count_str.replace(',', '').replace(' ', '')
            
            # Handle different abbreviations including localized ones
            if any(k in count_str.upper() for k in ['K', 'K+', 'ألف', 'الف']):
                # Extract the numeric part
                numeric_part = re.search(r'([\d.]+)', count_str)
                if numeric_part:
                    return int(float(numeric_part.group(1)) * 1000)
                return 0
            elif any(m in count_str.upper() for m in ['M', 'M+', 'مليون']):
                numeric_part = re.search(r'([\d.]+)', count_str)
                if numeric_part:
                    return int(float(numeric_part.group(1)) * 1000000)
                return 0
            elif any(b in count_str.upper() for b in ['B', 'B+', 'مليار']):
                numeric_part = re.search(r'([\d.]+)', count_str)
                if numeric_part:
                    return int(float(numeric_part.group(1)) * 1000000000)
                return 0
            else:
                # Try to extract any numeric value
                numeric_part = re.search(r'([\d.]+)', count_str)
                if numeric_part:
                    return int(float(numeric_part.group(1)))
                return 0
        except (ValueError, TypeError, AttributeError) as e:
            self.log(f"Error parsing count value '{count_str}': {str(e)}")
            return 0
    
    def get_user_followers(self, username):
        """Get followers for the given username using web scraping"""
        self.log(f"Fetching followers for @{username}...")
        followers = []
        
        try:
            # TikTok doesn't have a public API for followers, so we need to use web scraping
            profile_url = TIKTOK_BASE_URL.format(username)
            
            # Use Selenium for JavaScript-rendered content
            driver = setup_webdriver()
            driver.get(profile_url)
            
            try:
                # Wait for the page to load with updated selectors
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info, .profile-info, .tiktok-1g04lal-DivShareLayoutHeader, [data-e2e='user-page']"))
                )
                
                # Check if we can access the followers list
                # Note: TikTok often restricts access to followers list for privacy reasons
                # We'll try to find a followers link/button with updated selectors
                followers_link = None
                try:
                    # Try multiple selector strategies for better reliability
                    selectors = [
                        # XPATH selectors
                        (By.XPATH, "//a[contains(@href, '/followers') or contains(text(), 'Followers') or contains(text(), 'followers') or contains(text(), 'متابعين')]"),
                        # Data attribute selectors (more reliable)
                        (By.CSS_SELECTOR, "[data-e2e='followers-count'], .tiktok-xeexlu-DivNumber a, .tiktok-1kd69pk-DivNumber a"),
                        # Class-based selectors
                        (By.CSS_SELECTOR, ".followers-link, .tiktok-1xiuanb-ButtonFollowTabs")
                    ]
                    
                    # Try each selector strategy
                    for selector_type, selector in selectors:
                        try:
                            followers_link = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            if followers_link:
                                self.log(f"Found followers link using selector: {selector}")
                                break
                        except Exception:
                            continue
                    
                    # Data validation: Check if we found a valid link
                    if not followers_link:
                        self.log("Followers link not found using any selector strategy")
                except Exception as e:      
                    self.log(f"Error finding followers link: {str(e)}")
                    followers_link = None
                
                if followers_link:
                    # Click on the followers link
                    followers_link.click()
                    
                    # Wait for followers modal to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".follower-list, .followers-list, .user-list"))
                    )
                    
                    # Scroll to load more followers (TikTok uses infinite scrolling)
                    for _ in range(5):  # Scroll 5 times to load more followers
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)  # Wait for content to load
                    
                    # Extract followers information
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Find follower items
                    follower_items = soup.select(".follower-item, .user-item, .user-card")
                    
                    for item in follower_items:
                        try:
                            # Extract username
                            username_elem = item.select_one(".username, .user-username, .unique-id")
                            username_text = username_elem.text.strip() if username_elem else ""
                            username_text = username_text.replace("@", "")  # Remove @ if present
                            
                            # Extract display name
                            display_name_elem = item.select_one(".nickname, .user-nickname, .display-name")
                            display_name = display_name_elem.text.strip() if display_name_elem else ""
                            
                            # Extract follower and following counts if available
                            stats_elems = item.select(".user-stats span, .count span")
                            follower_count = 0
                            following_count = 0
                            
                            for stat in stats_elems:
                                stat_text = stat.text.strip().lower()
                                if 'follower' in stat_text:
                                    follower_count = self._parse_count(stat_text.split()[0])
                                elif 'following' in stat_text:
                                    following_count = self._parse_count(stat_text.split()[0])
                            
                            if username_text:  # Only add if we have a username
                                followers.append({
                                    'username': username_text,
                                    'display_name': display_name or username_text,
                                    'follower_count': follower_count,
                                    'following_count': following_count,
                                })
                        except Exception as e:
                            self.log(f"Error parsing follower item: {str(e)}")
                else:
                    self.log("Could not access followers list. TikTok restricts this information.")
                    # Try to get at least the follower count from the profile
                    profile_data = self.get_profile_info(username)
                    self.log(f"User has approximately {profile_data['follower_count']} followers")
            except Exception as e:
                self.log(f"Error during followers scraping: {str(e)}")
            finally:
                driver.quit()
                
        except Exception as e:
            self.log(f"Failed to get followers: {str(e)}")
        
        # If we couldn't get any followers, return an empty list
        if not followers:
            self.log("Could not retrieve followers. TikTok restricts access to this information.")
        else:
            self.log(f"Retrieved {len(followers)} followers")
            
        return followers
    
    def get_user_following(self, username):
        """Get users followed by the given username using web scraping"""
        self.log(f"Fetching following for @{username}...")
        following = []
        
        try:
            # TikTok doesn't have a public API for following, so we need to use web scraping
            profile_url = TIKTOK_BASE_URL.format(username)
            
            # Use Selenium for JavaScript-rendered content
            driver = setup_webdriver()
            driver.get(profile_url)
            
            try:
                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info, .profile-info"))
                )
                
                # Check if we can access the following list
                # Note: TikTok often restricts access to following list for privacy reasons
                # We'll try to find a following link/button
                following_link = None
                try:
                    following_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following') or contains(text(), 'Following') or contains(text(), 'following')]"))
                    )
                except Exception:
                    self.log("Following link not found or not accessible")
                    following_link = None
                
                if following_link:
                    # Click on the following link
                    following_link.click()
                    
                    # Wait for following modal to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".following-list, .user-list"))
                    )
                    
                    # Scroll to load more following (TikTok uses infinite scrolling)
                    for _ in range(5):  # Scroll 5 times to load more following
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)  # Wait for content to load
                    
                    # Extract following information
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Find following items
                    following_items = soup.select(".following-item, .user-item, .user-card")
                    
                    for item in following_items:
                        try:
                            # Extract username
                            username_elem = item.select_one(".username, .user-username, .unique-id")
                            username_text = username_elem.text.strip() if username_elem else ""
                            username_text = username_text.replace("@", "")  # Remove @ if present
                            
                            # Extract display name
                            display_name_elem = item.select_one(".nickname, .user-nickname, .display-name")
                            display_name = display_name_elem.text.strip() if display_name_elem else ""
                            
                            # Extract follower and following counts if available
                            stats_elems = item.select(".user-stats span, .count span")
                            follower_count = 0
                            following_count = 0
                            
                            for stat in stats_elems:
                                stat_text = stat.text.strip().lower()
                                if 'follower' in stat_text:
                                    follower_count = self._parse_count(stat_text.split()[0])
                                elif 'following' in stat_text:
                                    following_count = self._parse_count(stat_text.split()[0])
                            
                            if username_text:  # Only add if we have a username
                                following.append({
                                    'username': username_text,
                                    'display_name': display_name or username_text,
                                    'follower_count': follower_count,
                                    'following_count': following_count,
                                })
                        except Exception as e:
                            self.log(f"Error parsing following item: {str(e)}")
                else:
                    self.log("Could not access following list. TikTok restricts this information.")
                    # Try to get at least the following count from the profile
                    profile_data = self.get_profile_info(username)
                    self.log(f"User is following approximately {profile_data['following_count']} accounts")
            except Exception as e:
                self.log(f"Error during following scraping: {str(e)}")
            finally:
                driver.quit()
                
        except Exception as e:
            self.log(f"Failed to get following: {str(e)}")
        
        # If we couldn't get any following, return an empty list
        if not following:
            self.log("Could not retrieve following. TikTok restricts access to this information.")
        else:
            self.log(f"Retrieved {len(following)} following")
            
        return following
    
    def extract_contact_info(self, username):
        """Extract contact information (emails and phone numbers) from user profile and content"""
        self.log(f"Extracting contact information for @{username}...")
        
        # Validate username first
        username = self.validate_data(username, 'username', default_value="unknown")
        
        contact_info = {
            'emails': [],
            'phone_numbers': [],
            'social_links': [],
            'websites': [],
            'extraction_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': 'web_scraping'
        }
        
        try:
            # Get profile information first
            profile_data = self.get_profile_info(username)
            bio = profile_data.get('bio', '')
            
            # Use Selenium to get more detailed profile information
            profile_url = TIKTOK_BASE_URL.format(username)
            driver = setup_webdriver()
            
            try:
                driver.get(profile_url)
                
                # Wait for the page to load with updated selectors
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info, .profile-info, .tiktok-avatar, .tiktok-1g04lal-DivShareLayoutHeader, [data-e2e='user-page']"))
                )
                
                # Get the page source
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                
                # Data validation: Check if page loaded correctly
                if "Page not found" in html or "Couldn't find this account" in html or "لم يتم العثور على هذا الحساب" in html:
                    self.log("Warning: TikTok returned a 'Page not found' or 'Account not found' message")
                    return contact_info
                
                # Extract from bio text with validation
                bio = self.validate_data(bio, 'string', default_value="")
                if bio:
                    # Extract emails from bio
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = re.findall(email_pattern, bio)
                    # Validate each email
                    for email in emails:
                        validated_email = self.validate_data(email, 'email')
                        if validated_email and validated_email not in contact_info['emails']:
                            contact_info['emails'].append(validated_email)
                            self.log(f"Found email in bio: {validated_email}")
                    
                    # Extract phone numbers from bio
                    phone_pattern = r'\+?\d[\d\s-]{7,}\d'
                    phones = re.findall(phone_pattern, bio)
                    # Basic validation for phone numbers
                    for phone in phones:
                        # Clean the phone number (remove spaces, dashes)
                        cleaned_phone = re.sub(r'[\s-]', '', phone)
                        if cleaned_phone and cleaned_phone not in contact_info['phone_numbers']:
                            contact_info['phone_numbers'].append(cleaned_phone)
                            self.log(f"Found phone number in bio: {cleaned_phone}")
                    
                    # Extract websites from bio
                    website_pattern = r'https?://[\w\.-]+\.[a-zA-Z]{2,}[\w\./\-~?=%&#+:]*'
                    websites = re.findall(website_pattern, bio)
                    # Validate each website
                    for website in websites:
                        validated_website = self.validate_data(website, 'url')
                        if validated_website and validated_website not in contact_info['websites']:
                            contact_info['websites'].append(validated_website)
                            self.log(f"Found website in bio: {validated_website}")
                
                # Look for social links in the profile with updated selectors
                social_selectors = [
                    # Standard link selectors
                    'a[href*="instagram"], a[href*="facebook"], a[href*="twitter"], a[href*="youtube"], a[href*="linkedin"], a[href*="snapchat"]',
                    # TikTok 2023-2024 UI selectors
                    '.tiktok-1b4xcc5-DivShareLinks a, [data-e2e="user-social-link"], .css-1b4xcc5-DivShareLinks a',
                    # Instagram specific
                    'a[href*="instagram.com"], a[data-e2e="instagram-link"]',
                    # YouTube specific
                    'a[href*="youtube.com"], a[data-e2e="youtube-link"]',
                    # Twitter/X specific
                    'a[href*="twitter.com"], a[href*="x.com"], a[data-e2e="twitter-link"]'
                ]
                
                # Try each selector
                for selector in social_selectors:
                    social_links = soup.select(selector)
                    for link in social_links:
                        href = link.get('href')
                        # Validate URL using validate_data method
                        validated_url = self.validate_data(href, 'url')
                        if validated_url and validated_url not in contact_info['social_links']:
                            # Normalize the URL (remove tracking parameters)
                            try:
                                parsed_url = urlparse(validated_url)
                                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                                
                                # Check if this base URL is already in our list
                                base_urls = [urlparse(x).netloc + urlparse(x).path for x in contact_info['social_links']]
                                if base_url not in base_urls:
                                    contact_info['social_links'].append(validated_url)
                                    
                                    # Identify the social platform
                                    platform = "unknown"
                                    if "instagram" in validated_url.lower():
                                        platform = "Instagram"
                                    elif "facebook" in validated_url.lower():
                                        platform = "Facebook"
                                    elif "twitter" in validated_url.lower() or "x.com" in validated_url.lower():
                                        platform = "Twitter/X"
                                    elif "youtube" in validated_url.lower():
                                        platform = "YouTube"
                                    elif "linkedin" in validated_url.lower():
                                        platform = "LinkedIn"
                                    elif "snapchat" in validated_url.lower():
                                        platform = "Snapchat"
                                        
                                    self.log(f"Found {platform} link: {validated_url}")
                            except Exception as e:
                                self.log(f"Error normalizing URL {validated_url}: {str(e)}")
                                continue
                
                # Check for website links in the profile with updated selectors
                website_selectors = [
                    'a[href^="http"]',
                    '.tiktok-1b4xcc5-DivShareLinks a[href^="http"]:not([href*="tiktok"]), [data-e2e="user-website"]',
                    '.link-in-bio, .website-link'
                ]
                
                for selector in website_selectors:
                    website_links = soup.select(selector)
                    for link in website_links:
                        href = link.get('href')
                        
                        # Skip social media links
                        if href and any(social in href.lower() for social in ['tiktok', 'instagram', 'facebook', 'twitter', 'youtube', 'linkedin', 'snapchat']):
                            continue
                            
                        # Validate URL using validate_data method
                        validated_url = self.validate_data(href, 'url')
                        if validated_url and validated_url not in contact_info['websites']:
                            # Normalize the URL
                            try:
                                parsed_url = urlparse(validated_url)
                                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                                
                                # Check if this base URL is already in our list
                                base_urls = [urlparse(x).netloc + urlparse(x).path for x in contact_info['websites']]
                                if base_url not in base_urls:
                                    contact_info['websites'].append(validated_url)
                                    self.log(f"Found website link: {validated_url}")
                            except Exception as e:
                                self.log(f"Error processing URL {validated_url}: {str(e)}")
                                continue
                
                # Try to find contact info in video descriptions
                # TikTok loads videos dynamically, so we need to scroll to load more
                self.log("Checking video descriptions for contact information...")
                for _ in range(3):  # Scroll a few times to load videos
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for content to load
                
                # Get updated page source after scrolling
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                
                # Find video descriptions
                video_descriptions = soup.select('.video-description, .video-caption, .video-meta-caption')
                for desc in video_descriptions:
                    # Validate description text
                    desc_text = self.validate_data(desc.text, 'string', default_value="")
                    if not desc_text:
                        continue
                    
                    # Extract emails from description
                    emails = re.findall(email_pattern, desc_text)
                    for email in emails:
                        # Validate email
                        validated_email = self.validate_data(email, 'email')
                        if validated_email and validated_email not in contact_info['emails']:
                            contact_info['emails'].append(validated_email)
                            self.log(f"Found email in video description: {validated_email}")
                    
                    # Extract phone numbers from description
                    phones = re.findall(phone_pattern, desc_text)
                    for phone in phones:
                        # Clean the phone number
                        cleaned_phone = re.sub(r'[\s-]', '', phone)
                        if cleaned_phone and cleaned_phone not in contact_info['phone_numbers']:
                            contact_info['phone_numbers'].append(cleaned_phone)
                            self.log(f"Found phone number in video description: {cleaned_phone}")
                    
                    # Extract websites from description
                    websites = re.findall(website_pattern, desc_text)
                    for website in websites:
                        # Validate website URL
                        validated_website = self.validate_data(website, 'url')
                        if validated_website and validated_website not in contact_info['websites']:
                            # Skip social media links
                            if any(social in validated_website.lower() for social in ['tiktok', 'instagram', 'facebook', 'twitter', 'youtube', 'linkedin', 'snapchat']):
                                continue
                                
                            contact_info['websites'].append(validated_website)
                            self.log(f"Found website in video description: {validated_website}")
            
            except Exception as e:
                self.log(f"Error during contact info extraction: {str(e)}")
            finally:
                driver.quit()
            
            # Deduplicate results
            contact_info['emails'] = list(set(contact_info['emails']))
            contact_info['phone_numbers'] = list(set(contact_info['phone_numbers']))
            contact_info['social_links'] = list(set(contact_info['social_links']))
            contact_info['websites'] = list(set(contact_info['websites']))
            
            self.log(f"Found {len(contact_info['emails'])} emails, {len(contact_info['phone_numbers'])} phone numbers, "
                     f"{len(contact_info['social_links'])} social links, and {len(contact_info['websites'])} websites")
            
        except Exception as e:
            self.log(f"Failed to extract contact information: {str(e)}")
        
        return contact_info
        
    def extract_emails(self, username):
        """Extract emails related to the given username"""
        # Validate username
        username = self.validate_data(username, 'username', default_value="unknown")
        self.log(f"Extracting emails for @{username}...")
        
        # Use the contact_info extraction function
        contact_info = self.extract_contact_info(username)
        
        # Format the results in the expected structure
        emails = {
            'profile_email': "",
            'follower_emails': [],  # We don't extract emails from followers
            'following_emails': [],  # We don't extract emails from following
            'extraction_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': 'web_scraping'
        }
        
        # Validate and add primary email if available
        if contact_info['emails']:
            primary_email = self.validate_data(contact_info['emails'][0], 'email')
            if primary_email:
                emails['profile_email'] = primary_email
        
        # Add any additional emails to the list with validation
        if len(contact_info['emails']) > 1:
            for email in contact_info['emails'][1:]:
                validated_email = self.validate_data(email, 'email')
                if validated_email and validated_email not in emails['follower_emails']:
                    emails['follower_emails'].append(validated_email)
        
        return emails
    
    def extract_phone_numbers(self, username):
        """Extract phone numbers related to the given username"""
        # Validate username
        username = self.validate_data(username, 'username', default_value="unknown")
        self.log(f"Extracting phone numbers for @{username}...")
        
        # Use the contact_info extraction function
        contact_info = self.extract_contact_info(username)
        
        # Format the results in the expected structure
        phones = {
            'profile_phone': "",
            'follower_phones': [],  # We don't extract phone numbers from followers
            'following_phones': [],  # We don't extract phone numbers from following
            'extraction_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': 'web_scraping'
        }
        
        # Validate and add primary phone if available
        if contact_info['phone_numbers']:
            # Basic validation for phone number (just ensure it's not empty)
            primary_phone = contact_info['phone_numbers'][0]
            if primary_phone and len(primary_phone) >= 7:  # Most phone numbers are at least 7 digits
                # Clean the phone number (remove spaces, dashes)
                primary_phone = re.sub(r'[\s-]', '', primary_phone)
                phones['profile_phone'] = primary_phone
        
        # Add any additional phone numbers to the list with validation
        if len(contact_info['phone_numbers']) > 1:
            for phone in contact_info['phone_numbers'][1:]:
                # Basic validation
                if phone and len(re.sub(r'[\s-]', '', phone)) >= 7:
                    # Clean the phone number
                    cleaned_phone = re.sub(r'[\s-]', '', phone)
                    if cleaned_phone and cleaned_phone not in phones['follower_phones']:
                        phones['follower_phones'].append(cleaned_phone)
        
        return phones
    
    def get_tagged_users(self, username):
        """Get users who tagged the given username using web scraping"""
        self.log(f"Searching for users who tagged @{username}...")
        tagged = []
        
        try:
            # TikTok doesn't have a public API for tagged users, so we need to use web scraping
            # We'll search for mentions of the username
            search_url = f"https://www.tiktok.com/search?q=%40{username}"
            
            # Use Selenium for JavaScript-rendered content
            driver = setup_webdriver()
            driver.get(search_url)
            
            try:
                # Wait for search results to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".video-feed, .search-results, .video-card"))
                )
                
                # Scroll to load more results
                for _ in range(3):  # Scroll a few times to load more results
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for content to load
                
                # Extract video information
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                
                # Find video cards/items
                video_items = soup.select(".video-feed .video-item, .search-results .video-card, .video-feed-item")
                
                # Process each video to extract the creator who tagged the user
                for item in video_items:
                    try:
                        # Extract username of video creator
                        username_elem = item.select_one(".author-uniqueId, .video-username, .creator-username, .author-username")
                        tagger_username = username_elem.text.strip() if username_elem else ""
                        tagger_username = tagger_username.replace("@", "")  # Remove @ if present
                        
                        # Skip if the tagger is the same as the user we're analyzing
                        if tagger_username.lower() == username.lower():
                            continue
                        
                        # Extract display name
                        display_name_elem = item.select_one(".author-nickname, .video-author, .creator-nickname")
                        display_name = display_name_elem.text.strip() if display_name_elem else tagger_username
                        
                        # Extract post date if available
                        date_elem = item.select_one(".video-date, .video-timestamp, .video-time")
                        post_date = date_elem.text.strip() if date_elem else datetime.now().strftime("%Y-%m-%d")
                        
                        # Check if this user is already in our list
                        existing_user = next((user for user in tagged if user['username'] == tagger_username), None)
                        
                        if existing_user:
                            # Update post count for existing user
                            existing_user['post_count'] += 1
                            # Update last_tagged if this post is more recent
                            if post_date > existing_user['last_tagged']:
                                existing_user['last_tagged'] = post_date
                        else:
                            # Add new user to the list
                            tagged.append({
                                'username': tagger_username,
                                'display_name': display_name,
                                'post_count': 1,
                                'last_tagged': post_date
                            })
                    except Exception as e:
                        self.log(f"Error parsing video item: {str(e)}")
                
                # If we found no tagged users, try an alternative approach
                if not tagged:
                    self.log("No tagged users found in search results, trying alternative approach...")
                    
                    # Try to search for hashtags with the username
                    hashtag_search_url = f"https://www.tiktok.com/tag/{username}"
                    driver.get(hashtag_search_url)
                    
                    # Wait for hashtag results to load with updated selectors
                        try:
                            # Try multiple selectors for better reliability
                            selectors = [
                                ".video-feed, .challenge-feed",
                                ".tiktok-x6y88p-DivItemContainerV2, .tiktok-1qb12g8-DivThreeColumnContainer",
                                "[data-e2e='challenge-item'], [data-e2e='search-card-item']",
                                ".css-x6y88p-DivItemContainerV2, .css-1qb12g8-DivThreeColumnContainer"
                            ]
                            
                            # Try each selector
                            for selector in selectors:
                                try:
                                    WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                    )
                                    self.log(f"Found hashtag results using selector: {selector}")
                                    break
                                except Exception:
                                    continue
                            
                            # Scroll to load more results with improved strategy
                            scroll_attempts = 0
                            max_scroll_attempts = 3
                            last_height = driver.execute_script("return document.body.scrollHeight")
                            
                            while scroll_attempts < max_scroll_attempts:
                                # Scroll down
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(2)  # Wait for content to load
                                
                                # Calculate new scroll height and compare with last scroll height
                                new_height = driver.execute_script("return document.body.scrollHeight")
                                if new_height == last_height:
                                    # If heights are the same, we've reached the bottom or content isn't loading
                                    break
                                last_height = new_height
                                scroll_attempts += 1
                            
                            # Extract video information
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'lxml')
                            
                            # Data validation: Check if we got any results
                            if "No results found" in html or "لم يتم العثور على نتائج" in html:
                                self.log(f"Warning: No results found for hashtag #{hashtag}")
                                continue
                            
                            # Find video cards/items with updated selectors
                            video_items = soup.select(".video-feed .video-item, .challenge-feed .video-card, .tiktok-x6y88p-DivItemContainerV2, [data-e2e='challenge-item'], [data-e2e='search-card-item'], .css-x6y88p-DivItemContainerV2")
                            
                            # Data validation: Check if we found any videos
                            if not video_items:
                                self.log(f"Warning: Could not extract video items for hashtag #{hashtag}")
                                continue
                            else:
                                self.log(f"Found {len(video_items)} videos for hashtag #{hashtag}")
                            
                            # Process each video to extract the creator
                            for item in video_items:
                                try:
                                    # Extract username of video creator with updated selectors
                                    username_selectors = [
                                        ".author-uniqueId, .video-username, .creator-username",
                                        ".tiktok-arkop9-DivCreatorTag span, [data-e2e='video-author-uniqueid']",
                                        ".css-arkop9-DivCreatorTag span"
                                    ]
                                    
                                    tagger_username = ""
                                    for selector in username_selectors:
                                        username_elem = item.select_one(selector)
                                        if username_elem and username_elem.text.strip():
                                            tagger_username = username_elem.text.strip()
                                            tagger_username = tagger_username.replace("@", "")  # Remove @ if present
                                            break
                                    
                                    # Data validation: Ensure we have a username
                                    if not tagger_username:
                                        continue
                                    
                                    # Skip if the tagger is the same as the user we're analyzing
                                    if tagger_username.lower() == username.lower():
                                        continue
                                    
                                    # Extract display name with updated selectors
                                    display_name_selectors = [
                                        ".author-nickname, .video-author, .creator-nickname",
                                        ".tiktok-2zn17h-PAuthorName, [data-e2e='video-author-nickname']",
                                        ".css-2zn17h-PAuthorName"
                                    ]
                                    
                                    display_name = tagger_username  # Default to username if display name not found
                                    for selector in display_name_selectors:
                                        display_name_elem = item.select_one(selector)
                                        if display_name_elem and display_name_elem.text.strip():
                                            display_name = display_name_elem.text.strip()
                                            break
                                    
                                    # Extract post date if available with updated selectors
                                    date_selectors = [
                                        ".video-date, .video-timestamp, .video-time",
                                        ".tiktok-1wrhn5c-PTime, [data-e2e='video-publish-time']",
                                        ".css-1wrhn5c-PTime"
                                    ]
                                    
                                    post_date = datetime.now().strftime("%Y-%m-%d")  # Default to current date
                                    for selector in date_selectors:
                                        date_elem = item.select_one(selector)
                                        if date_elem and date_elem.text.strip():
                                            post_date = date_elem.text.strip()
                                
                                # Check if this user is already in our list
                                existing_user = next((user for user in tagged if user['username'] == tagger_username), None)
                                
                                if existing_user:
                                    # Update post count for existing user
                                    existing_user['post_count'] += 1
                                    # Update last_tagged if this post is more recent
                                    if post_date > existing_user['last_tagged']:
                                        existing_user['last_tagged'] = post_date
                                else:
                                    # Add new user to the list
                                    tagged.append({
                                        'username': tagger_username,
                                        'display_name': display_name,
                                        'post_count': 1,
                                        'last_tagged': post_date
                                    })
                            except Exception as e:
                                self.log(f"Error parsing hashtag video item: {str(e)}")
                    except Exception as e:
                        self.log(f"Error during hashtag search: {str(e)}")
            except Exception as e:
                self.log(f"Error during tagged users search: {str(e)}")
            finally:
                driver.quit()
        except Exception as e:
            self.log(f"Failed to get tagged users: {str(e)}")
        
        # Sort tagged users by post count (descending)
        tagged.sort(key=lambda x: x['post_count'], reverse=True)
        
        if not tagged:
            self.log("No users found who tagged this username")
        else:
            self.log(f"Found {len(tagged)} users who tagged @{username}")
            
        return tagged
    
    def display_profile_info(self, profile):
        """Display profile information in the UI"""
        # Clear previous info
        for widget in self.profile_info_frame.winfo_children():
            widget.destroy()
        
        # Create profile header
        header_frame = ctk.CTkFrame(self.profile_info_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Username and display name
        username_label = ctk.CTkLabel(
            header_frame, 
            text=f"@{profile['username']}", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        username_label.pack(pady=(5, 0))
        
        display_name_label = ctk.CTkLabel(
            header_frame, 
            text=profile['display_name'],
            font=ctk.CTkFont(size=16)
        )
        display_name_label.pack(pady=(0, 5))
        
        # Verification badge if verified
        if profile.get('verified', False):
            verified_label = ctk.CTkLabel(
                header_frame, 
                text="✓ Verified Account",
                font=ctk.CTkFont(size=14),
                text_color="#1DA1F2"
            )
            verified_label.pack(pady=(0, 5))
        
        # Bio
        if profile.get('bio'):
            bio_frame = ctk.CTkFrame(self.profile_info_frame)
            bio_frame.pack(fill="x", padx=10, pady=5)
            
            bio_label = ctk.CTkLabel(
                bio_frame, 
                text="Bio:",
                font=ctk.CTkFont(weight="bold")
            )
            bio_label.pack(anchor="w", padx=10, pady=(5, 0))
            
            bio_text = ctk.CTkLabel(
                bio_frame, 
                text=profile['bio'],
                wraplength=400
            )
            bio_text.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self.profile_info_frame)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Stats grid
        stats = [
            ("Followers", f"{profile['follower_count']:,}"),
            ("Following", f"{profile['following_count']:,}"),
            ("Likes", f"{profile['likes']:,}"),
            ("Videos", f"{profile['video_count']:,}"),
            ("Account Type", "Private" if profile.get('private', False) else "Public"),
            ("Joined", profile.get('join_date', 'Unknown'))
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_frame = ctk.CTkFrame(stats_frame)
            stat_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            stats_frame.grid_columnconfigure(col, weight=1)
            
            stat_label = ctk.CTkLabel(
                stat_frame, 
                text=label,
                font=ctk.CTkFont(size=12)
            )
            stat_label.pack(pady=(5, 0))
            
            stat_value = ctk.CTkLabel(
                stat_frame, 
                text=value,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            stat_value.pack(pady=(0, 5))
    
    def display_followers(self, followers):
        """Display followers in the UI"""
        self.followers_text.delete("0.0", "end")
        
        if not followers:
            self.followers_text.insert("end", "No followers found.")
            return
        
        self.followers_text.insert("end", f"Found {len(followers)} followers:\n\n")
        
        for i, follower in enumerate(followers, 1):
            self.followers_text.insert("end", f"{i}. @{follower['username']} - {follower['display_name']}\n")
            self.followers_text.insert("end", f"   Followers: {follower['follower_count']:,} | Following: {follower['following_count']:,}\n\n")
    
    def display_following(self, following):
        """Display following in the UI"""
        self.following_text.delete("0.0", "end")
        
        if not following:
            self.following_text.insert("end", "No following found.")
            return
        
        self.following_text.insert("end", f"Found {len(following)} following:\n\n")
        
        for i, follow in enumerate(following, 1):
            self.following_text.insert("end", f"{i}. @{follow['username']} - {follow['display_name']}\n")
            self.following_text.insert("end", f"   Followers: {follow['follower_count']:,} | Following: {follow['following_count']:,}\n\n")
    
    def display_emails(self, emails):
        """Display emails in the UI"""
        self.emails_text.delete("0.0", "end")
        
        if not emails:
            self.emails_text.insert("end", "No emails found.")
            return
        
        # Profile email
        if emails.get('profile_email'):
            self.emails_text.insert("end", "Profile Email:\n")
            self.emails_text.insert("end", f"{emails['profile_email']}\n\n")
        
        # Follower emails
        if emails.get('follower_emails'):
            self.emails_text.insert("end", f"Follower Emails ({len(emails['follower_emails'])}):\n")
            for i, email in enumerate(emails['follower_emails'], 1):
                self.emails_text.insert("end", f"{i}. {email}\n")
            self.emails_text.insert("end", "\n")
        
        # Following emails
        if emails.get('following_emails'):
            self.emails_text.insert("end", f"Following Emails ({len(emails['following_emails'])}):\n")
            for i, email in enumerate(emails['following_emails'], 1):
                self.emails_text.insert("end", f"{i}. {email}\n")
    
    def display_phone_numbers(self, phones):
        """Display phone numbers in the UI"""
        self.phones_text.delete("0.0", "end")
        
        if not phones:
            self.phones_text.insert("end", "No phone numbers found.")
            return
        
        # Profile phone
        if phones.get('profile_phone'):
            self.phones_text.insert("end", "Profile Phone Number:\n")
            self.phones_text.insert("end", f"{phones['profile_phone']}\n\n")
        
        # Follower phones
        if phones.get('follower_phones'):
            self.phones_text.insert("end", f"Follower Phone Numbers ({len(phones['follower_phones'])}):\n")
            for i, phone in enumerate(phones['follower_phones'], 1):
                self.phones_text.insert("end", f"{i}. {phone}\n")
            self.phones_text.insert("end", "\n")
        
        # Following phones
        if phones.get('following_phones'):
            self.phones_text.insert("end", f"Following Phone Numbers ({len(phones['following_phones'])}):\n")
            for i, phone in enumerate(phones['following_phones'], 1):
                self.phones_text.insert("end", f"{i}. {phone}\n")
    
    def display_tagged_users(self, tagged):
        """Display tagged users in the UI"""
        self.tagged_text.delete("0.0", "end")
        
        if not tagged:
            self.tagged_text.insert("end", "No tagged users found.")
            return
        
        self.tagged_text.insert("end", f"Found {len(tagged)} users who tagged @{self.target_username.get()}:\n\n")
        
        for i, user in enumerate(tagged, 1):
            self.tagged_text.insert("end", f"{i}. @{user['username']} - {user['display_name']}\n")
            self.tagged_text.insert("end", f"   Tagged {user['post_count']} times | Last tagged: {user['last_tagged']}\n\n")
    
    def export_results(self):
        """Export results to a file"""
        if not self.result_data:
            messagebox.showinfo("Info", "No results to export")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Results"
        )
        
        if not file_path:
            return
        
        try:
            # Add timestamp and metadata
            export_data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'target_username': self.target_username.get(),
                'data': self.result_data
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4)
            
            self.log(f"Results exported to {file_path}")
            messagebox.showinfo("Success", f"Results exported to {file_path}")
            
        except Exception as e:
            self.log(f"Error exporting results: {str(e)}")
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("About TikTok-Sayer")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.grab_set()  # Make the window modal
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # About content
        frame = ctk.CTkFrame(about_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            frame, 
            text="TikTok-Sayer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 5))
        
        version_label = ctk.CTkLabel(
            frame, 
            text="Version 1.0.0",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=(0, 20))
        
        description_label = ctk.CTkLabel(
            frame, 
            text="An OSINT tool for analyzing TikTok accounts",
            wraplength=350
        )
        description_label.pack(pady=5)
        
        developer_label = ctk.CTkLabel(
            frame, 
            text="Developed by: Saudi Linux",
            font=ctk.CTkFont(size=12)
        )
        developer_label.pack(pady=(20, 0))
        
        email_label = ctk.CTkLabel(
            frame, 
            text="Email: SayerLinux@gmail.com",
            font=ctk.CTkFont(size=12)
        )
        email_label.pack(pady=(0, 20))
        
        # GitHub link
        def open_github():
            webbrowser.open("https://github.com/SaudiLinux/TikTok-Sayer")
        
        github_button = ctk.CTkButton(
            frame, 
            text="GitHub Repository", 
            command=open_github,
            width=150
        )
        github_button.pack(pady=10)
        
        # Close button
        close_button = ctk.CTkButton(
            frame, 
            text="Close", 
            command=about_window.destroy,
            width=100
        )
        close_button.pack(pady=10)


def main():
    app = TikTokSayer()
    app.mainloop()


if __name__ == "__main__":
    main()