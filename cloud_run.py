import functions_framework
import json
from flask import jsonify
import os
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
import random
from googleapiclient.discovery import build
from google.oauth2 import service_account
import traceback
import logging
import requests
import google.auth.transport.requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SHEET1_NAME = "Sheet1"
SHEET2_NAME = "Sheet2"
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1LPZfvogYD4_DG_6zNiEFVDhpsUSUrfQ1y0bSzf7GjNw')
DELEGATED_USER = 'ITassist@gosaas.io'
SHEETS_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
DIRECTORY_SCOPE = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

# Sarcastic remarks list
SARCASTIC_REMARKS = [
    "Come on, you're better than this.",
    "Stop WASTING MY TIME.",
    "Are you alright? Do you need water? Do you feel dizzy?",
    "Nice try, but I've seen it all.",
    "I'm impressed, you've mastered the fine art of messing with me.",
    "Did you think I wouldn't notice?",
    "Oh, you again? I was hoping for a change of scenery.",
    "Is this your car's way of trying to chat?",
    "You know that I know, right?",
    "Impressive attempt, but I'm not fooled.",
    "Nice try, but I've got better things to do.",
    "You must be bored. Let's spice things up a bit.",
    "Are we doing this again? Really?",
    "Well, well, well. Guess who's back?",
    "If only this was as exciting as a cat video.",
    "Is this a car or a portal to your alternate reality?",
    "Trying to slip under the radar, huh?",
    "I appreciate the effort, but I'm not biting.",
    "You can't pull one over on me twice!",
    "Ah, the old switcheroo. Classic move!",
    "Playing mind games, huh? Game on!",
    "I'll give you an A for effort, but a C for execution.",
    "Trying to get out of chores, I see.",
    "Back again with more license plate fun?",
    "Oh, I see. You're testing my patience now.",
    "Do you ever get tired of this?",
    "Is this car tag or a never-ending game of hide and seek?",
    "You've got guts, I'll give you that.",
    "Are you trying to pass a test or just fooling around?",
    "Nice try, but I'm too clever for that.",
    "This is starting to feel like deja vu.",
    "I thought we already did this last week.",
    "Oh, now we're getting into the tricky stuff.",
    "Are we trying to break the record for license plate messages?",
    "You know I have a long memory, right?"
]

def get_directory_service():
    """Initialize and return a Google Directory API service with domain-wide delegation."""
    try:
        print(f"Initializing Directory API service with delegated user: {DELEGATED_USER}")
        credentials = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=DIRECTORY_SCOPE
        ).with_subject(DELEGATED_USER)
        
        service = build('admin', 'directory_v1', credentials=credentials)
        print("Directory API service initialized successfully")
        return service
    except Exception as e:
        print(f"Error creating directory service: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        logger.error(f"Error creating directory service: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_profile_photo(email):
    """Fetch profile photo for a given email using Directory API."""
    try:
        print(f"Attempting to fetch profile photo for email: {email}")
        service = get_directory_service()
        
        # Fetch user details from Directory API
        print(f"Making API call to get user details for: {email}")
        result = service.users().get(
            userKey=email,
            projection='full'
        ).execute()
        
        print(f"API response received for {email}")
        print(f"Response keys: {result.keys()}")
        
        # Return the photo URL if available
        photo_url = result.get('thumbnailPhotoUrl')
        if photo_url:
            print(f"Found photo URL for {email}: {photo_url}")
            return photo_url
        else:
            print(f"No photo URL found for {email}")
            return None
    except Exception as e:
        print(f"Error fetching profile photo for {email}: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        logger.error(f"Error fetching profile photo: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_sheets_service():
    """Initialize and return a Google Sheets API service."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=SHEETS_SCOPE
        )
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        logger.error(f"Error creating sheets service: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_sheet_data(sheet_name):
    """Fetch data from Google Sheets."""
    try:
        service = get_sheets_service()
        if sheet_name == SHEET1_NAME:
            range_name = f"{sheet_name}!A:E"  # Sr#, Owner Name, Vehicle Number, Contact Number, Email ID
        else:
            range_name = f"{sheet_name}!A:B"  # Email, Endpoint
            
        logger.info(f"Fetching data from sheet: {sheet_name}, range: {range_name}")
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning(f"No data found in sheet: {sheet_name}")
            return pd.DataFrame()
            
        # Handle different header positions for each sheet
        if sheet_name == SHEET1_NAME:
            # Sheet1: Skip first row, use second row as headers, data from third row
            if len(values) < 2:
                logger.warning(f"Sheet1 has insufficient rows: {len(values)}")
                return pd.DataFrame()
            headers = values[1]  # Second row as headers
            data = values[2:]    # Data starts from third row
        else:
            # Sheet2: First row is headers, data from second row
            headers = values[0]  # First row as headers
            data = values[1:]    # Data starts from second row
        
        logger.info(f"Headers: {headers}")
        logger.info(f"Number of data rows: {len(data)}")
        
        # Ensure all rows have the same number of columns as headers
        padded_data = []
        for row in data:
            # Pad the row with None values if it's shorter than headers
            padded_row = row + [None] * (len(headers) - len(row))
            # Truncate if longer than headers
            padded_row = padded_row[:len(headers)]
            padded_data.append(padded_row)
            
        # Convert to DataFrame
        df = pd.DataFrame(padded_data, columns=headers)
        logger.info(f"DataFrame created with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error fetching sheet data: {str(e)}")
        logger.error(traceback.format_exc())
        return pd.DataFrame()

def normalize_license_plate(plate):
    """Normalize license plate format."""
    normalized_plate = plate.replace('-', '').replace(' ', '').upper()
    letters = ''.join(filter(str.isalpha, normalized_plate))
    numbers = ''.join(filter(str.isdigit, normalized_plate))
    return letters + numbers

def find_owner(license_plate):
    """Find owner details for a given license plate."""
    sheet_data = get_sheet_data(SHEET1_NAME)
    normalized_plate = normalize_license_plate(license_plate)
    
    for _, row in sheet_data.iterrows():
        vehicles = str(row['Vehicle Number']).split('/')
        vehicle_list = [normalize_license_plate(v.strip()) for v in vehicles]
        
        if normalized_plate in vehicle_list:
            return {
                'name': row['Owner Name'],
                'contact': str(row['Contact Number']),
                'email': row['Email ID']
            }
    return None

def find_endpoint_by_email(email):
    """Find endpoint for a given email."""
    sheet_data = get_sheet_data(SHEET2_NAME)
    for _, row in sheet_data.iterrows():
        if row['Email'] == email:
            return row['Endpoints']
    return None

def save_email_endpoint_mapping(email, endpoint):
    """Save or update email-endpoint mapping."""
    try:
        service = get_sheets_service()
        sheet_data = get_sheet_data(SHEET2_NAME)
        
        # Check if email exists
        email_exists = False
        row_index = None
        
        for i, row in sheet_data.iterrows():
            if row['Email'] == email:
                email_exists = True
                row_index = i + 2  # +2 because first row is header, data starts from second row
                break
        
        if email_exists:
            # Update existing row
            range_name = f"{SHEET2_NAME}!B{row_index}"
            body = {
                'values': [[endpoint]]
            }
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return False
        else:
            # Append new row
            range_name = f"{SHEET2_NAME}!A:B"
            body = {
                'values': [[email, endpoint]]
            }
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return True
            
    except Exception as e:
        print(f"Error saving email-endpoint mapping: {str(e)}")
        return False

def send_message_to_owner(owner_endpoint, user_name, user_photo, license_plate):
    """Send a message to the owner using Google Chat API."""
    try:
        print(f"Sending message to owner at endpoint: {owner_endpoint}")
        
        # Get access token for Google Chat API
        credentials = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=['https://www.googleapis.com/auth/chat.bot']
        )
        
        # Get the access token using a simple request
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # Construct the message URL
        url = f"https://chat.googleapis.com/v1/{owner_endpoint}/messages"
        
        # Construct the message payload
        payload = {
            "cardsV2": [{
                "card": {
                    "header": {
                        "title": user_name,
                        "imageUrl": user_photo
                    },
                    "sections": [{
                        "widgets": [{
                            "textParagraph": {
                                "text": f"{user_name} is requesting you to kindly move your vehicle ({license_plate})."
                            }
                        }]
                    }]
                }
            }]
        }
        
        # Send the message
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("Message sent successfully to owner")
            return True
        else:
            print(f"Failed to send message to owner. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending message to owner: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        return False

@functions_framework.http
def gocar_bot(request):
    """Main entry point for the Google Chat bot."""
    try:
        request_json = request.get_json(silent=True)
        logger.info(f"Received request: {request_json}")
        
        if not request_json:
            logger.error("Invalid request format - no JSON data")
            return jsonify({
                "text": "Invalid request format"
            }), 400
            
        event_type = request_json.get('type')
        logger.info(f"Event type: {event_type}")
        
        if event_type == 'MESSAGE':
            return on_message(request)
        elif event_type == 'ADDED_TO_SPACE':
            return on_add_to_space(request)
        elif event_type == 'REMOVED_FROM_SPACE':
            return jsonify({
                "text": ""
            }), 200
        else:
            logger.error(f"Invalid event type: {event_type}")
            return jsonify({
                "text": "Invalid event type"
            }), 400
    except Exception as e:
        logger.error(f"Error in main handler: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "text": f"An error occurred: {str(e)}"
        }), 500

def on_message(request):
    """Handle incoming messages."""
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or request_json.get('type') != 'MESSAGE':
            return jsonify({
                "text": "Invalid request type"
            }), 400
            
        user_message = request_json.get('message', {}).get('text', '').strip()
        user_email = request_json.get('user', {}).get('email')
        user_endpoint = request_json.get('space', {}).get('name')
        user_name = request_json.get('user', {}).get('displayName', 'Unknown User')
        
        # Validate input
        if not user_message or not user_email or not user_endpoint:
            return jsonify({
                "text": "Missing required fields"
            }), 400
            
        # Check for invalid patterns
        invalid_patterns = [
            r'https?://',
            r'\.(jpg|jpeg|png|gif|mp4|avi|mkv)$',
            r'voice\s*message',
            r'file\s*attachment'
        ]
        
        if any(pattern in user_message.lower() for pattern in invalid_patterns):
            return jsonify({
                "text": "Invalid input format"
            }), 400
            
        # Process license plate
        license_plate = user_message.upper()
        owner_details = find_owner(license_plate)
        
        if not owner_details:
            return jsonify({
                "text": "License plate not found in the records."
            })
            
        # Get profile photos
        user_photo = get_profile_photo(user_email)
        owner_photo = get_profile_photo(owner_details['email'])
        
        print(f"User photo URL: {user_photo}")
        print(f"Owner photo URL: {owner_photo}")
            
        # Check if sender is the owner
        if user_email == owner_details['email']:
            random_remark = random.choice(SARCASTIC_REMARKS)
            return jsonify({
                "text": f"You are the owner of the vehicle: ({license_plate}).\n{random_remark}",
                "cards": [{
                    "sections": [{
                        "widgets": [{
                            "keyValue": {
                                "topLabel": f"License Plate: {license_plate}",
                                "content": f"Owner: {owner_details['name']}",
                                "bottomLabel": f"Email: {owner_details['email']}",
                                "button": {
                                    "textButton": {
                                        "text": owner_details['contact'],
                                        "onClick": {
                                            "openLink": {
                                                "url": f"tel:{owner_details['contact']}"
                                            }
                                        }
                                    }
                                }
                            }
                        }]
                    }]
                }]
            })
            
        # Find owner's endpoint
        owner_endpoint = find_endpoint_by_email(owner_details['email'])
        print(f"Owner endpoint: {owner_endpoint}")
        print(f"User photo: {user_photo}")
        print(f"Owner photo: {owner_photo}")
        
        if owner_endpoint:
            # Send message to owner
            message_sent = send_message_to_owner(owner_endpoint, user_name, user_photo, license_plate)
            
            # Send response back to user
            return jsonify({
                "text": "Owner details found and message sent." if message_sent else "Owner details found but message could not be sent.",
                "cards": [{
                    "sections": [{
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": f"License Plate: {license_plate}",
                                    "content": f"Owner: {owner_details['name']}",
                                    "bottomLabel": f"Email: {owner_details['email']}",
                                    "button": {
                                        "textButton": {
                                            "text": owner_details['contact'],
                                            "onClick": {
                                                "openLink": {
                                                    "url": f"tel:{owner_details['contact']}"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "image": {
                                    "imageUrl": owner_photo if owner_photo else None
                                }
                            }
                        ]
                    }]
                }]
            })
        else:
            return jsonify({
                "text": f"The owner of the license plate ({license_plate}) does not have the chatbot added. Please request them to add the chatbot to their space to enable messaging.",
                "cards": [{
                    "sections": [{
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": f"License Plate: {license_plate}",
                                    "content": f"Owner: {owner_details['name']}",
                                    "bottomLabel": f"Email: {owner_details['email']}",
                                    "button": {
                                        "textButton": {
                                            "text": owner_details['contact'],
                                            "onClick": {
                                                "openLink": {
                                                    "url": f"tel:{owner_details['contact']}"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "image": {
                                    "imageUrl": owner_photo if owner_photo else None
                                }
                            }
                        ]
                    }]
                }]
            })
            
    except Exception as e:
        logger.error(f"Error in message handler: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "text": f"An error occurred: {str(e)}"
        }), 500

def on_add_to_space(request):
    """Handle when bot is added to a space."""
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or request_json.get('type') != 'ADDED_TO_SPACE':
            return jsonify({
                "text": "Invalid request type"
            }), 400
            
        user_email = request_json.get('user', {}).get('email')
        user_endpoint = request_json.get('space', {}).get('name')
        
        if not user_email or not user_endpoint:
            return jsonify({
                "text": "Missing required fields"
            }), 400
            
        is_new_entry = save_email_endpoint_mapping(user_email, user_endpoint)
        
        response_text = (
            "Your email and space have been successfully saved by the bot."
            if is_new_entry else
            "Your email and space were already saved. The endpoint has been updated."
        )
        
        return jsonify({
            "text": response_text
        })
        
    except Exception as e:
        logger.error(f"Error in add to space handler: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "text": f"An error occurred: {str(e)}"
        }), 500