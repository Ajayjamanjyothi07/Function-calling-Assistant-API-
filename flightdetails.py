from openai import OpenAI
import requests
import json

# Initialize OpenAI client with API key
client = OpenAI(api_key="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")

# Not used in this code snippet
assistant_id = "asst_mpnQhSytttqbhLs4TA3dfJvL"

# Function to get flight details
def get_flight_details(flight_iata):
    access_key = '11b4b5c344af246d82a9eff23680af88'
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": access_key,
        "flight_iata": flight_iata,
        "limit": 1
    }
    # Make request to AviationStack API
    resp = requests.get(url, params=params)
    # Check if request was successful
    if resp.status_code != 200:
        return f"Error: Failed to fetch data. Status code: {resp.status_code}"
    try:
        # Parse JSON response
        data = resp.json()
        print(data)
        # Check if flight data exists
        if "data" not in data or not data["data"]:
            return f"No flight data found for Flight_iata {flight_iata}"
        flight_data = data["data"][0]
        # Extract flight details from response
        airline_name = flight_data["airline"]["name"]
        flight_number = flight_data["flight"]["number"]
        departure_airport = flight_data["departure"]["airport"]
        departure_time = flight_data["departure"]["estimated"]
        arrival_airport = flight_data["arrival"]["airport"]
        arrival_time = flight_data["arrival"]["estimated"]
        # Return formatted flight details
        return f"""Details for flight {flight_iata}:\n
            - Airline Name: {airline_name}\n
            - Flight Number: {flight_number}\n
            - Departure Airport: {departure_airport}\n
            - Departure Time: {departure_time}\n
            - Arrival Airport: {arrival_airport}\n
            - Arrival Time: {arrival_time}\n"""
    except Exception as e:
        # Handle exceptions
        return f"Error processing response: {str(e)}"

# Function to run conversation
def run_conversation():
    # Define user input message
    messages = [
        {"role": "user", "content": "flight details about EY277?"}
    ]
    # Define available functions for OpenAI model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_flight_details",
                "description": "Get details about a flight",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flight_iata": {
                            "type": "string",
                            "description": "The flight IATA code",
                        },
                    },
                    "required": ["flight_iata"],
                },
            },
        }
    ]
    # Generate response from OpenAI model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    # Get response message from model
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        # Append response message
        messages.append(response_message)
        for tool_call in tool_calls:
            # Call function based on tool call
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = get_flight_details(flight_iata=function_args.get("flight_iata"))
            # Append tool response to messages
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        # Generate second response from OpenAI model
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
        )
        return second_response

# Print conversation response
print(run_conversation())
