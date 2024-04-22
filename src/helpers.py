import uuid
import random
import string

def generate_unique_id():
    # Generate a UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4()

    # Convert UUID to a string and extract the first 12 characters
    id_string = str(unique_id)[:12]

    # Ensure the ID contains only alphabets
    id_string_alpha = ''.join(c for c in id_string if c.isalpha())

    # If the length is less than 12 characters, pad with random alphabets
    if len(id_string_alpha) < 12:
        id_string_alpha += ''.join(random.choice(string.ascii_uppercase) for _ in range(12 - len(id_string_alpha)))

    return id_string_alpha
