import base64

def string_to_base64(input_string):
    # Convert string to bytes and encode to Base64
    encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
    # Convert bytes to a string for display
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

def base64_to_string(encoded_string):
    # Convert Base64 string to bytes and decode back to original string
    decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
    # Convert bytes back to string
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def main():
    # Get input from user
    original_string = input("Enter a string to convert to Base64: ")
    
    # Convert to Base64
    base64_result = string_to_base64(original_string)
    print(f"Base64 encoded string: {base64_result}")
    
    # Convert back to original string
    decoded_result = base64_to_string(base64_result)
    print(f"Decoded back to original: {decoded_result}")
    
    # Verify it matches
    if original_string == decoded_result:
        print("Success! The original and decoded strings match.")
    else:
        print("Something went wrong. The strings don’t match.")

if __name__ == "__main__":
    main()



@echo off
REM Get current date and time in a consistent format
set "datetime=%date% %time%"

REM Append the datetime to a text file (>> appends instead of overwriting)
echo %datetime% >> "C:\path\to\your_file.txt"

REM Optional: Display a message to confirm it ran
echo Appended date and time to your_file.txt
