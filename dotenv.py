import os
import dotenv

dotenv.load_dotenv(dotenv_path='/Users/seanmacdonald/Documents/Lighthouse_Labs/Projects/.env',verbose=True)

KEY = os.getenv("XKEY")

print(KEY)