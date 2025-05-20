const sarcasticRemarks = [
        "Come on, you're better than this.",
        "Stop WASTING MY TIME.",
        "Are you alright? Do you need water? Do you feel dizzy?",
        "Nice try, but I’ve seen it all.",
        "I’m impressed, you’ve mastered the fine art of messing with me.",
        "Did you think I wouldn’t notice?",
        "Oh, you again? I was hoping for a change of scenery.",
        "Is this your car’s way of trying to chat?",
        "You know that I know, right?",
        "Impressive attempt, but I’m not fooled.",
        "Nice try, but I’ve got better things to do.",
        "You must be bored. Let’s spice things up a bit.",
        "Are we doing this again? Really?",
        "Well, well, well. Guess who’s back?",
        "If only this was as exciting as a cat video.",
        "Is this a car or a portal to your alternate reality?",
        "Trying to slip under the radar, huh?",
        "I appreciate the effort, but I’m not biting.",
        "You can’t pull one over on me twice!",
        "Ah, the old switcheroo. Classic move!",
        "Playing mind games, huh? Game on!",
        "I’ll give you an A for effort, but a C for execution.",
        "Trying to get out of chores, I see.",
        "Back again with more license plate fun?",
        "Oh, I see. You’re testing my patience now.",
        "Do you ever get tired of this?",
        "Is this car tag or a never-ending game of hide and seek?",
        "You’ve got guts, I’ll give you that.",
        "Are you trying to pass a test or just fooling around?",
        "Nice try, but I’m too clever for that.",
        "This is starting to feel like deja vu.",
        "I thought we already did this last week.",
        "Oh, now we’re getting into the tricky stuff.",
        "Are we trying to break the record for license plate messages?",
        "You know I have a long memory, right?"
      ];
    
  
function onAddToSpace(event) 
{
  console.log("AddToSpace Event Executed");
  Logger.log("AddToSpace Event Executed");

  try 
  {
    const userEmail = event.user.email; // Email of the user adding the bot
    const userEndpoint = event.space.name; // Endpoint specific to the user

    Logger.log("Testing On Add To Space");
    Logger.log(userEmail);
    Logger.log(userEndpoint);

    if (!userEmail || !userEndpoint) 
    {
      Logger.log("User email or endpoint is missing.");
    }

    const isNewEntry = saveEmailEndpointMapping(userEmail, userEndpoint);

    const responseText = isNewEntry
      ? "Your email and space have been successfully saved by the bot."
      : "Your email and space were already saved. The endpoint has been updated.";

    notifyUser(userEndpoint, responseText);
  } catch (error) {
    Logger.log(`Error in onAddToSpace: ${error.message}`);
    console.error(`Error in onAddToSpace: ${error.message}`);
    
    // Notify user about the error
    if (event.space && event.space.name) {
      notifyUser(event.space.name, `An error occurred: ${error.message}. Please ensure the bot has the required authorization.`);
    }
  }
}

function onRemoveFromSpace()
{
  console.log("Bot Removed");
  Logger.log("Bot Removed");
}

function get_chatbot_service() {
  // Access the script properties to retrieve PRIVATE_KEY and ISSUER_EMAIL
  var properties = PropertiesService.getScriptProperties();
  var privateKey = properties.getProperty('PRIVATE_KEY');
  var issuerEmail = properties.getProperty('ISSUER_EMAIL');

  return OAuth2.createService("Bot Service")
    .setTokenUrl('https://accounts.google.com/o/oauth2/token') // Set the endpoint URL.
    .setPrivateKey(privateKey)                                // Set the private key.
    .setIssuer(issuerEmail)                                   // Set the issuer.
    .setScope('https://www.googleapis.com/auth/chat.bot');     // Set the scope.
}

function fetchUserNameAndProfilePictureFromProfile() {
  const token = ScriptApp.getOAuthToken();
  console.log(token);
  const url = 'https://people.googleapis.com/v1/people/me?personFields=names,photos';
  const options = {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const data = JSON.parse(response.getContentText());
    const fullName = data.names && data.names[0] ? data.names[0].displayName : '';
    const profilePictureUrl = data.photos && data.photos[0] ? data.photos[0].url : '';
    console.log(`Name: ${fullName}, Profile Picture URL: ${profilePictureUrl}`);
    return { fullName, profilePictureUrl };
  } catch (error) {
    Logger.log(`Error fetching user profile: ${error.message}`);
    return { fullName: '', profilePictureUrl: '' };
  }
}

function getProfilePhoto() {
  // const email = "umair.khan@gosaas.io";
  const peopleApiUrl = "https://people.googleapis.com/v1/people:listDirectoryPeople";
  const token = ScriptApp.getOAuthToken();

  Logger.log("OAuth Token: " + token);  // Log the token to check if it's valid
  
  try 
  {
    const fullUrl = "https://people.googleapis.com/v1/people:listDirectoryPeople?sources=DIRECTORY_SOURCE_TYPE_DOMAIN_CONTACT&sources=DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE&readMask=names,emailAddresses,photos";

    Logger.log("Full API URL: " + fullUrl);  // Log the full URL to check for errors
    
    // Send the GET request
    const response = UrlFetchApp.fetch(fullUrl, {
      method: 'get',
      // headers: {
        // Authorization: `Bearer ${token}`
      // },
      muteHttpExceptions: true
    });

    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    Logger.log("Response Code: " + responseCode);  // Log response code for debugging
    Logger.log("Response Text: " + responseText);  // Log the response text

    if (responseCode === 200) {
      const jsonResponse = JSON.parse(responseText);
      const people = jsonResponse.people || [];

      // Search for the person matching the email
      const person = people.find(
        (p) =>
          p.emailAddresses &&
          p.emailAddresses.some((e) => e.value === email)
      );

      if (person) {
        const photo = (person.photos && person.photos[0]) || {};
        return photo.url || 'No photo available';
      } else {
        return 'The email does not exist so we could not find their profile picture';
      }
    } else {
      Logger.log(`Error: ${responseText}`);
      return `Error fetching profile photo: ${responseText}`;
    }
  } catch (error) {
    Logger.log(`Exception: ${error}`);
    return `Error: ${error.message}`;
  }
}

function testAllEndpoints() 
{
  // Get the active spreadsheet
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Sheet2");
  
  // Check if the sheet exists
  if (!sheet) {
    throw new Error("Sheet2 does not exist in the spreadsheet.");
  }

  const data = sheet.getDataRange().getValues();

  // const token = ScriptApp.getOAuthToken();
  const temp = get_chatbot_service();
  const token =  temp.getAccessToken();
  const messageText = "Endpoint works";

  for (let i = 1; i < data.length; i++) { // Skip the header row
    const endpoint = data[i][1]; // Assuming column 2 contains endpoints
    if (endpoint) {
      const url = `https://chat.googleapis.com/v1/${endpoint}/messages`;
      const payload = { text: messageText };

      const options = {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        payload: JSON.stringify(payload),
      };

      try {
        const response = UrlFetchApp.fetch(url, options);
        if (response.getResponseCode() === 200) {
          Logger.log(`Message sent successfully to endpoint: ${endpoint}`);
        } else {
          Logger.log(`Failed to send message to endpoint: ${endpoint}`);
        }
      } catch (error) {
        Logger.log(`Error sending message to endpoint: ${endpoint}. Error: ${error.message}`);
      }
    }
  }
}

function notifyUser(endpoint, messageText) {
  const temp = get_chatbot_service()
  const token = temp.getAccessToken();
  const url = `https://chat.googleapis.com/v1/${endpoint}/messages`;

  const payload = {
    text: messageText,
  };

  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    payload: JSON.stringify(payload),
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() === 200) {
      Logger.log(`Notification sent successfully to endpoint: ${endpoint}`);
    } else {
      Logger.log(`Failed to send notification to endpoint: ${endpoint}`);
    }
  } catch (error) {
    Logger.log(`Error sending notification: ${error.message}`);
  }
}

function saveEmailEndpointMapping(email, endpoint) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Sheet2");
  const data = sheet.getDataRange().getValues();

  // Check if the email already exists in the sheet
  for (let i = 1; i < data.length; i++) { // Skip the header row
    if (data[i][0] === email) {
      sheet.getRange(i + 1, 2).setValue(endpoint); // Update the endpoint if email exists
      Logger.log(`Updated endpoint for email: ${email}`);
      return false; // Indicates that the email was updated, not newly added
    }
  }

  // Add a new row if the email is not found
  sheet.appendRow([email, endpoint]);
  Logger.log(`Added new mapping: ${email} -> ${endpoint}`);
  return true; // Indicates a new entry was added
}

function onMessage(event) 
{
  try 
  {
    // Validate that the message is a string
    if (typeof event.message.text !== 'string') {
      throw new Error("Invalid input format");
    }

    const userMessage = event.message.text.trim(); // Message text

    // Additional validation to detect non-text inputs such as links, media, etc.
    const invalidPatterns = [
      /https?:\/\//i, // URL pattern (e.g., Google Drive or Meet links)
      /\.(jpg|jpeg|png|gif|mp4|avi|mkv)$/i, // Image, video, and GIF file extensions
      /voice\s*message/i, // Voice message keyword
      /file\s*attachment/i // File attachment keyword
    ];

    if (invalidPatterns.some((pattern) => pattern.test(userMessage))) {
      throw new Error("Invalid input format");
    }

    const licensePlate = userMessage.toUpperCase(); // Normalize the input for consistent matching
    const userEmail = event.user.email; // Sender's email
    const userEndpoint = event.space.name; // Sender's endpoint
    const { fullName, profilePictureUrl } = fetchUserNameAndProfilePictureFromProfile();

    console.log(`Name: ${fullName}`);
    console.log(`Profile Picture URL: ${profilePictureUrl}`);

    // Save sender's email and endpoint if not already saved
    if (userEmail && userEndpoint) {
      saveEmailEndpointMapping(userEmail, userEndpoint);
    }

    const ownerDetails = findOwner(licensePlate);
    var ownerPfp = "";
    if (ownerDetails) {
      ownerPfp = getProfilePhoto(ownerDetails.email);
    }

    if (
      ownerPfp === "No photo available" ||
      ownerPfp === "The email does not exist so we could not find their profile picture"
    ) {
      ownerPfp = "";
    }

    if (ownerDetails) {
      if (ownerDetails.email === "haseebmahmood@gosaas.io") {
        ownerDetails.name = "Father";
      }

      // Check if the sender is the owner
      if (userEmail === ownerDetails.email) {
        var randomRemark = sarcasticRemarks[Math.floor(Math.random() * sarcasticRemarks.length)];
        if (ownerDetails.name == "Father") {
          randomRemark = "I am a failure, just like you, Father.";
        }
        return {
          text: `You are the owner of the vehicle: (${licensePlate}).\n${randomRemark}`
        };
      }

      // Check if the owner's email has an endpoint saved
      const ownerEndpoint = findEndpointByEmail(ownerDetails.email);

      if (ownerEndpoint) {
        // Send a direct message to the owner
        sendMessageToOwnerByEmail(
          ownerDetails.email,
          `${fullName} is requesting you to kindly move your vehicle (${licensePlate}).`
        );

        // Create a response card with owner details and profile picture
        return {
          text: "Owner details found and message sent.",
          cards: [
            {
              sections: [
                {
                  widgets: [
                    {
                      image: {
                        imageUrl: ownerPfp,
                        altText: "Owner's Profile Picture",
                        width: 100, // Adjust the width of the image
                        height: 100 // Adjust the height of the image
                      }
                    },
                    {
                      keyValue: {
                        topLabel: `License Plate: ${licensePlate}`,
                        content: `Owner: ${ownerDetails.name}`,
                        bottomLabel: `Email: ${ownerDetails.email}`,
                        button: {
                          textButton: {
                            text: ownerDetails.contact,
                            onClick: {
                              openLink: {
                                url: `tel:${ownerDetails.contact}`
                              }
                            }
                          }
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        };
      } else {
        // Create a response card with owner details and profile picture
        return {
          text: `The owner of the license plate (${licensePlate}) does not have the chatbot added. Please request them to add the chatbot to their space to enable messaging.`,
          cards: [
            {
              sections: [
                {
                  widgets: [
                    {
                      image: {
                        imageUrl: ownerPfp,
                        altText: "Owner's Profile Picture",
                        width: 100, // Adjust the width of the image
                        height: 100 // Adjust the height of the image
                      }
                    },
                    {
                      keyValue: {
                        topLabel: `License Plate: ${licensePlate}`,
                        content: `Owner: ${ownerDetails.name}`,
                        bottomLabel: `Email: ${ownerDetails.email}`,
                        button: {
                          textButton: {
                            text: ownerDetails.contact,
                            onClick: {
                              openLink: {
                                url: `tel:${ownerDetails.contact}`
                              }
                            }
                          }
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        };
      }
    } else {
      // No owner details found
      return { text: "License plate not found in the records." };
    }
  } catch (error) 
  {
    // Handle invalid input format or other errors
    console.error(error.message);
    return { text: "Invalid input format" };
  }
}

function normalizeLicensePlate(plate) {
  const normalizedPlate = plate.replace(/[-\s]/g, '').toUpperCase(); // Remove spaces and hyphens, convert to uppercase
  const letters = normalizedPlate.match(/[A-Z]+/g) || []; // Extract letters
  const numbers = normalizedPlate.match(/\d+/g) || []; // Extract numbers
  return letters.join('') + numbers.join(''); // Combine letters first, then numbers
}

function findOwner(licensePlate) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Sheet1");
  const data = sheet.getDataRange().getValues();

  // Normalize user input
  const normalizedLicensePlate = normalizeLicensePlate(licensePlate);

  for (let i = 1; i < data.length; i++) { // Skip header row
    const vehicles = data[i][2].toString(); // Column C: Vehicle Numbers
    const vehicleList = vehicles.split('/')
      .map(v => normalizeLicensePlate(v)); // Normalize each vehicle number

    // Check if any of the normalized vehicle numbers match the input
    if (vehicleList.includes(normalizedLicensePlate)) {
      return {
        name: data[i][1], // Owner Name
        contact: data[i][3].toString(), // Contact Number
        email: data[i][4] // Email ID
      };
    }
  }
  return null;
}

function findEndpointByEmail(email) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName("Sheet2");
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) { // Skip the header row
    if (data[i][0] === email) {
      return data[i][1]; // Return the endpoint if email matches
    }
  }
  return null; // Return null if no endpoint is found
}

function sendMessageToOwnerByEmail(email, messageText) {
  const userDetails = fetchUserNameAndProfilePictureFromProfile();
  const senderName = userDetails.fullName;
  const senderPhotoUrl = userDetails.profilePictureUrl;

  // Get the endpoint for the email
  const userEndpoint = findEndpointByEmail(email);

  if (!userEndpoint) {
    Logger.log(`Could not find endpoint for email: ${email}`);
    return;
  }

  const temp = get_chatbot_service();
  const token = temp.getAccessToken();
  const url = `https://chat.googleapis.com/v1/${userEndpoint}/messages`;

  // Construct the message with the sender's name, text, and photo URL
  const payload = {
  cardsV2: 
  [
    {
      card: 
      {
        header: 
        {
          title: senderName,
          imageUrl: senderPhotoUrl // Attach the profile picture URL directly
        },
        sections: 
        [
          {
            widgets:
            [
              {
                textParagraph: 
                {
                  text: messageText
                }  
              }
            ]
          }
        ]
      }
    }]
  };

  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    payload: JSON.stringify(payload),
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() === 200) {
      Logger.log(`Message sent successfully to email: ${email}`);
    } else {
      Logger.log(`Failed to send message to email: ${email}`);
    }
  } catch (error) {
    Logger.log(`Error sending message: ${error.message}`);
  }
}

function check_permissions()
{
  console.log("HAAHA");
}