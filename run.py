import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("OSINTHUB_HOST", "127.0.0.1"),
            port=int(os.getenv("OSINTHUB_PORT", "5000")), debug=False)
