# main.py

import argparse
from weather_api_client import WeatherApiClient
from temperature_converter import TemperatureConverter
from data_manager import DataManager
from settings.ini import load_settings

def main():
    # Load settings from settings.ini
    settings = load_settings()
    
    # Initialize clients for API calls and temperature conversion
    api_client = WeatherApiClient(settings['api_key'])
    converter = TemperatureConverter(settings['temperature_unit'])
    data_manager = DataManager(settings['database_type'])
    
    # Handle user input or commands
    parser = argparse.ArgumentParser(description='Weather App')
    subparsers = parser.add_subparsers(dest='command')
    
    # Subparser for managing API calls
    api_call_parser = subparsers.add_parser('api-call', help='Manages weather data through the API')
    api_call_parser.add_argument('--city', required=True, help='City name to fetch weather data for')
    api_call_parser.set_defaults(func=handle_api_call)
    
    # Subparser for temperature conversion
    temp_conversion_parser = subparsers.add_parser('temp-conversion', help='Converts temperatures between Celsius and Fahrenheit')
    temp_conversion_parser.add_argument('--temperature', type=float, required=True, help='Temperature to convert')
    temp_conversion_parser.add_argument('--from-unit', choices=['Celsius', 'Fahrenheit'], required=True, help='Unit of the input temperature')
    temp_conversion_parser.add_argument('--to-unit', choices=['Celsius', 'Fahrenheit'], required=True, help='Unit to convert to')
    temp_conversion_parser.set_defaults(func=handle_temp_conversion)
    
    # Subparser for managing data storage
    data_management_parser = subparsers.add_parser('data-management', help='Manages weather data in the database or file')
    data_management_parser.add_argument('--action', choices=['add', 'remove', 'update'], required=True, help='Action to perform on data')
    data_management_parser.add_argument('--city', required=True, help='City name for action')
    data_management_parser.set_defaults(func=handle_data_management)
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Execute the appropriate function based on user input
    if args.command == 'api-call':
        args.func(api_client.get_weather(city=args.city))
    elif args.command == 'temp-conversion':
        result = converter.convert_temperature(temp=args.temperature, from_unit=args.from_unit, to_unit=args.to_unit)
        print(f'{args.temperature} {args.from_unit} is equal to {result:.2f} {args.to_unit}')
    elif args.command == 'data-management':
        action = args.action
        city = args.city
        
        if action == 'add':
            data_manager.add_weather(city=city, temperature=args.temperature)
        elif action == 'remove':
            data_manager.remove_weather(city=city)
        elif action == 'update':
            data_manager.update_weather(city=city, temperature=args.temperature)
        
        print(f'Weather data for {city} updated successfully.')

if __name__ == '__main__':
    main()