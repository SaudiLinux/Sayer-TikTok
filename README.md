# TikTok-Sayer

![TikTok-Sayer Logo](https://img.shields.io/badge/OSINT-TikTok--Sayer-ff69b4)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

TikTok-Sayer is an OSINT (Open Source Intelligence) tool designed for analyzing TikTok accounts using their pseudonym. This tool provides an interactive user interface that allows you to extract various information from TikTok profiles.

## 🔍 Features

- **Profile Analysis**: Get detailed information about any TikTok account
- **Follower Analysis**: Extract a list of followers from target accounts
- **Following Analysis**: Get users followed by the target
- **Email Extraction**: Extract email addresses associated with target followers and following
- **Phone Number Extraction**: Get phone numbers of target followers and users followed by target
- **Tagged Users**: Get a list of users who have tagged the target
- **Export Results**: Save your findings in JSON format for further analysis

## 📋 Requirements

- Python 3.6 or higher
- Required Python packages (see requirements.txt):
  - requests
  - tkinter
  - pillow
  - customtkinter
  - tiktok-api
  - python-dotenv
  - requests-html
  - beautifulsoup4
  - fake-useragent

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SaudiLinux/TikTok-Sayer.git
   cd TikTok-Sayer
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Run the application:
   ```bash
   python tiktok_sayer.py
   ```

2. Enter a TikTok username in the input field

3. Select the information you want to extract by checking/unchecking the options

4. Click "Analyze Account" to start the analysis

5. View the results in the respective tabs

6. Export the results using the "Export Results" button

## 📊 Example

```bash
# Run the tool and analyze a TikTok account
python tiktok_sayer.py

# Enter username: example_user
# Check options: Get Followers, Get Emails
# Click "Analyze Account"
```

## 📝 Notes

- This tool is for educational and research purposes only
- Use responsibly and ethically
- Respect privacy and terms of service of TikTok
- The tool uses rate limiting to avoid being blocked by TikTok

## 🔄 Updates

Check the [GitHub repository](https://github.com/SaudiLinux/TikTok-Sayer) for updates and new features.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

- **Saudi Linux**
- Email: SayerLinux@gmail.com

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## ⭐ Show your support

Give a ⭐️ if this project helped you!

---

**Disclaimer**: This tool is for educational purposes only. The developer is not responsible for any misuse or damage caused by this tool. Use at your own risk.