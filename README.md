# Hey-Bentley
A personal voice assistant for your desktop that can handle tasks and transcribe text.

## Project Structure
bentley-voice/
├── .env.example
├── requirements.txt
├── config.py
├── bentley.py          ← main entry point
├── voice.py            ← speech I/O
├── search.py           ← web search
├── file_manager.py     ← markdown read/write
├── notion_mcp.py       ← Notion integration
├── actions.py          ← command router + confirm/auto mode
├── logs/
└── files/

## 1. Clone this repo
git clone https://github.com/CreativLogic/Hey-Bentley &&
cd Hey-Bentley

## 2. Create a virtual environment:
python -m venv .venv
### Windows:
.venv\Scripts\activate
### Mac/Linux:
source .venv/bin/activate

## 3. Install Dependencies
pip install -r requirements.txt

## If PyAudio fails on Windows:
pip install pipwin && pipwin install pyaudio

## 4. Set up your .env
cp .env.example .env

**Open .env and paste in your NOTION_API_KEY and NOTION_DEFAULT_DATABASE_ID**

To get Notion credentials:

Go to notion.so/my-integrations

Click New Integration, give it a name, click Submit

Copy the Internal Integration Secret → that is your NOTION_API_KEY

Open a Notion database, click ··· menu → Add Connection → select your integration

Copy the database ID from the URL: notion.so/workspace/[THIS-PART]?v=...

## 5. Run Bentley
python bentley.py

# How Bentley Behaves:
| Mode              | Trigger                                       | What happens                                                               |
| ----------------- | --------------------------------------------- | -------------------------------------------------------------------------- |
| Confirm (default) | "hey bentley, search for social patter leads" | Bentley describes the action and asks "should I go ahead?" before doing it |
| Auto              | "hey bentley, switch to auto mode"            | Bentley acts immediately on every command with no confirmation prompt      |

**You can switch modes at any point mid-conversation. Sensitive actions like deleting files or writing to Notion will still always describe what they are about to do so you know what is happening.**
