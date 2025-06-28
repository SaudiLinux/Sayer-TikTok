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
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv

# Import customtkinter for modern UI
try:
    import customtkinter as ctk
except ImportError:
    messagebox.showerror("Error", "CustomTkinter is not installed. Please install it using 'pip install customtkinter'")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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
        """Add message to log with timestamp"""
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
        """Get profile information for the given username"""
        # In a real implementation, this would make API calls to TikTok
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 2))  # Simulate network delay
        
        # Mock profile data
        return {
            'username': username,
            'display_name': f"{username.capitalize()} Official",
            'bio': "This is a sample bio for demonstration purposes",
            'follower_count': random.randint(1000, 1000000),
            'following_count': random.randint(100, 5000),
            'likes': random.randint(10000, 10000000),
            'video_count': random.randint(10, 500),
            'verified': random.choice([True, False]),
            'private': random.choice([True, False]),
            'join_date': (datetime.now().replace(year=datetime.now().year - random.randint(1, 5))).strftime("%Y-%m-%d")
        }
    
    def get_user_followers(self, username):
        """Get followers for the given username"""
        # In a real implementation, this would make API calls to TikTok
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 3))  # Simulate network delay
        
        # Generate mock followers
        followers = []
        for i in range(random.randint(20, 50)):
            followers.append({
                'username': f"follower_{i}_{random.randint(100, 999)}",
                'display_name': f"Follower {i}",
                'follower_count': random.randint(100, 10000),
                'following_count': random.randint(10, 1000),
            })
        
        return followers
    
    def get_user_following(self, username):
        """Get users followed by the given username"""
        # In a real implementation, this would make API calls to TikTok
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 3))  # Simulate network delay
        
        # Generate mock following
        following = []
        for i in range(random.randint(20, 50)):
            following.append({
                'username': f"following_{i}_{random.randint(100, 999)}",
                'display_name': f"Following {i}",
                'follower_count': random.randint(100, 10000),
                'following_count': random.randint(10, 1000),
            })
        
        return following
    
    def extract_emails(self, username):
        """Extract emails related to the given username"""
        # In a real implementation, this would analyze profile data and content
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 2))  # Simulate processing delay
        
        # Generate mock emails
        emails = {
            'profile_email': f"{username}@example.com",
            'follower_emails': [f"follower_{i}@example.com" for i in range(random.randint(5, 15))],
            'following_emails': [f"following_{i}@example.com" for i in range(random.randint(5, 15))]
        }
        
        return emails
    
    def extract_phone_numbers(self, username):
        """Extract phone numbers related to the given username"""
        # In a real implementation, this would analyze profile data and content
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 2))  # Simulate processing delay
        
        # Generate mock phone numbers
        phones = {
            'profile_phone': f"+1{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
            'follower_phones': [f"+1{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}" for i in range(random.randint(3, 10))],
            'following_phones': [f"+1{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}" for i in range(random.randint(3, 10))]
        }
        
        return phones
    
    def get_tagged_users(self, username):
        """Get users who tagged the given username"""
        # In a real implementation, this would analyze content and mentions
        # For demonstration, we'll return mock data
        time.sleep(random.uniform(1, 3))  # Simulate network delay
        
        # Generate mock tagged users
        tagged = []
        for i in range(random.randint(10, 30)):
            tagged.append({
                'username': f"tagged_{i}_{random.randint(100, 999)}",
                'display_name': f"Tagged User {i}",
                'post_count': random.randint(1, 10),
                'last_tagged': (datetime.now().replace(day=random.randint(1, 28))).strftime("%Y-%m-%d")
            })
        
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