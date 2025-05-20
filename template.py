import functions_framework
import json
from flask import jsonify

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function for Google Chat bot.
    Args:
        request (flask.Request): The request object from Google Chat.
    Returns:
        A JSON response object formatted for Google Chat.
    """
    request_json = request.get_json(silent=True)

    # --- Debugging: Print the incoming request to logs ---
    print(f"Incoming request: {request_json}")
    # --- End Debugging ---

    if request_json and request_json.get('type') == 'MESSAGE':
        print("Received MESSAGE event.") # Debugging
        response_message = {
            "text": "Hello World!"
        }
        return jsonify(response_message)
    elif request_json and request_json.get('type') == 'ADDED_TO_SPACE':
        print("Received ADDED_TO_SPACE event.") # Debugging
        response_message = {
            "text": "Thanks for adding me! I'm ready to say hello."
        }
        return jsonify(response_message)
    elif request_json and request_json.get('type') == 'REMOVED_FROM_SPACE':
        print("Received REMOVED_FROM_SPACE event.") # Debugging
        return '', 200  # Acknowledge the removal without sending a message
    else:
        print(f"Received unknown or malformed event: {request_json}") # Debugging
        return 'Invalid request type or format.', 400