import requests
import json
import re

def handler(request):
    url = "https://elvebredd.com/values.js"
    response = requests.get(url)
    
    if response.status_code == 200:
        match = response.text
        json_data = match.split('var petsData = ')[1].split(';')[0]
        json_data = json_data.replace("'", '"')
        json_data = re.sub(r'(\w+):', r'"\1":', json_data)
        json_data = re.sub(r',\s*([\]}])', r'\1', json_data)
        
        try:
            pets_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "JSON decode error", "message": str(e)})
            }
        
        # Create Lua string representation
        lua_string = "database = {\n"
        for index, pet in enumerate(pets_data):
            pet_name = pet['name']
            lua_string += f'    ["{pet_name}"] = {{\n'
            for key, value in pet.items():
                lua_string += f'        {key} = "{value}",\n'
            lua_string = lua_string[:-2] + '\n'  # Remove last comma and add newline
            lua_string += '    },\n' if index < len(pets_data) - 1 else '    }\n'
        lua_string += "}\nreturn database"

        # Return the Lua table as plain text
        return {
            "statusCode": 200,
            "body": lua_string,
            "headers": {
                "Content-Type": "text/plain"
            }
        }
    else:
        return {
            "statusCode": response.status_code,
            "body": json.dumps({"error": "Data fetch failed", "status_code": response.status_code})
        }
