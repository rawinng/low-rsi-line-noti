# Low RSI Scanner for S&P 500 Stocks

scanner RSI of S&P 500 stocks and notify via LINE if any stock has RSI < 30

### Requirements

- Python 3.11 or lower
- LINE Messaging API channel (for notifications)

### Setup

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ``` 
4. Setup Line OA channel ID & secret in `.env` file:
    ```
    LINE_CHANNEL_ID=your_channel_id
    LINE_CHANNEL_SECRET=your_channel_secret
    LINE_NOTIFY_ENABLED=true  # Set to 'true' to enable notifications
    ```

### Usage
Run the main script to scan for low RSI stocks and send notifications:
```bash
python main.py
```
