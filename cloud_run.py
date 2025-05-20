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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SHEET1_NAME = "Sheet1"
SHEET2_NAME = "Sheet2"
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1LPZfvogYD4_DG_6zNiEFVDhpsUSUrfQ1y0bSzf7GjNw')

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

def get_sheets_service():
    """Initialize and return a Google Sheets API service."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
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
            
        # Check if sender is the owner
        if user_email == owner_details['email']:
            random_remark = random.choice(SARCASTIC_REMARKS)
            return jsonify({
                "text": f"You are the owner of the vehicle: ({license_plate}).\n{random_remark}"
            })
            
        # Find owner's endpoint
        owner_endpoint = find_endpoint_by_email(owner_details['email'])
        
        if owner_endpoint:
            # Send message to owner
            # Implementation for sending message to owner
            return jsonify({
                "text": "Owner details found and message sent.",
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
        else:
            return jsonify({
                "text": f"The owner of the license plate ({license_plate}) does not have the chatbot added. Please request them to add the chatbot to their space to enable messaging.",
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