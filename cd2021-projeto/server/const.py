"""Server constants, can change during project lifetime."""
import os

# Value in ms
BANNED_TIME = 2400
COOLDOWN_TIME = 600
NEW_PENALTY = 300

# Time it takes to validate a password in ms
MIN_VALIDATE = 10
MAX_VALIDATE = 100

MIN_TRIES = 10
MAX_TRIES = 20

PASSWORD_SIZE = int(os.environ.get('PASSWORD_SIZE', default =1))

if __name__ == "__main__":
	print(PASSWORD_SIZE) 
