# GoCar Chat Bot

A Google Chat bot that helps users find vehicle owners by their license plate numbers. The bot integrates with Google Sheets to store and retrieve vehicle and owner information.

## Features

- License plate lookup
- Owner information display
- Contact information with clickable phone numbers
- Sarcastic responses for self-messages
- Automatic endpoint management for messaging

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gocar
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create a service account and download the credentials as `service-account.json`
   - Deploy to Google Cloud Run

4. Configure environment variables:
   - `SPREADSHEET_ID`: Your Google Sheet ID

## Deployment

1. Build and deploy to Google Cloud Run:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/gocar
gcloud run deploy gocar --image gcr.io/PROJECT_ID/gocar --platform managed
```

2. Configure the Google Chat bot:
   - Go to Google Chat API configuration
   - Set the App URL to your Cloud Run service URL
   - Enable the bot in your Google Chat space

## Usage

1. Add the bot to a Google Chat space
2. Send a license plate number as a message
3. The bot will respond with owner information or a sarcastic message if you're the owner

## License

MIT License 