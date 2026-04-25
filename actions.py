"""
Bentley Voice — Action Router
Parses spoken commands and dispatches to the correct handler.
Supports 'confirm' mode (ask before each action) and 'auto' mode.
"""
import webbrowser
import os
import datetime
from rich.console import Console

from voice import speak, confirm
from search import web_search, format_search_summary, format_search_markdown
from file_manager import write_file, read_file, list_files, delete_file
import notion_mcp
from config import DEFAULT_MODE, BENTLEY_NAME

console = Console()


class ActionRouter:
    def __init__(self):
        self.mode = DEFAULT_MODE  # "confirm" or "auto"

    # ── Mode toggle ──────────────────────────────────────────────────────
    def set_mode(self, mode: str):
        self.mode = mode
        speak(f"Got it. I'm now in {mode} mode.")

    def _should_proceed(self, description: str) -> bool:
        """In confirm mode, ask before acting. In auto mode, just do it."""
        if self.mode == "auto":
            return True
        return confirm(description)

    # ── Core dispatch ─────────────────────────────────────────────────────
    def handle(self, command: str) -> bool:
        """
        Route a command string to the right action.
        Returns False when the user wants to quit, True otherwise.
        """
        c = command.lower().strip()

        # ── Mode switching ────────────────────────────────────────────
        if "switch to auto mode" in c or "auto mode" in c:
            self.set_mode("auto")
            return True
        if "switch to confirm mode" in c or "confirm mode" in c:
            self.set_mode("confirm")
            return True

        # ── Status / help ─────────────────────────────────────────────
        if "what mode" in c or "current mode" in c:
            speak(f"I'm in {self.mode} mode.")
            return True
        if "help" in c or "what can you do" in c:
            self._say_help()
            return True

        # ── Time / date ───────────────────────────────────────────────
        if "time" in c:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}.")
            return True
        if "date" in c or "today" in c:
            today = datetime.datetime.now().strftime("%A, %B %d %Y")
            speak(f"Today is {today}.")
            return True

        # ── Web search ────────────────────────────────────────────────
        if "search" in c or "look up" in c or "find" in c:
            query = (c.replace("search for", "")
                      .replace("search", "")
                      .replace("look up", "")
                      .replace("find", "")
                      .strip())
            if not query:
                speak("What would you like me to search for?")
                return True
            if self._should_proceed(f"Search the web for '{query}'"):
                results = web_search(query)
                summary = format_search_summary(results)
                speak(summary)
                # Offer to save results
                speak("Would you like me to save those results as a markdown file?")
                from voice import listen
                save_resp = listen(timeout=6)
                if any(w in save_resp for w in ["yes", "yeah", "sure", "save"]):
                    md_content = format_search_markdown(query, results)
                    path = write_file(f"search-{query[:30]}", md_content)
                    speak(f"Saved search results to {path}")
            return True

        # ── Open browser ──────────────────────────────────────────────
        if "open" in c:
            site_map = {
                "google":   "https://google.com",
                "youtube":  "https://youtube.com",
                "linkedin": "https://linkedin.com",
                "notion":   "https://notion.so",
                "github":   "https://github.com",
            }
            target = None
            url    = None
            for name, link in site_map.items():
                if name in c:
                    target, url = name, link
                    break
            if url and self._should_proceed(f"Open {target} in your browser"):
                webbrowser.open(url)
                speak(f"Opening {target}.")
            elif not url:
                speak("I'm not sure which site you want me to open.")
            return True

        # ── Markdown file: write ──────────────────────────────────────
        if "write" in c or "create file" in c or "save file" in c or "new note" in c:
            from voice import listen
            speak("What should I call this file?")
            filename = listen(timeout=8)
            if not filename:
                speak("I didn't catch a filename.")
                return True
            speak("Go ahead — dictate your note. Say 'done' when finished.")
            lines = []
            while True:
                line = listen(timeout=10, phrase_time_limit=20)
                if "done" in line or "that's all" in line:
                    break
                if line:
                    lines.append(line)
            content = f"# {filename.title()}\n\n" + "\n\n".join(lines)
            if self._should_proceed(f"Write a markdown file called '{filename}'"):
                path = write_file(filename, content)
                speak(f"Done. File saved.")
            return True

        # ── Markdown file: read ───────────────────────────────────────
        if "read file" in c or "open file" in c or "read note" in c:
            from voice import listen
            speak("Which file should I read?")
            filename = listen(timeout=6)
            if not filename:
                speak("I didn't get a filename.")
                return True
            if self._should_proceed(f"Read the file '{filename}'"):
                content = read_file(filename)
                # Speak a trimmed version (first 500 chars) to avoid very long playback
                preview = content[:500].replace("#", "").strip()
                speak(preview if preview else "The file appears to be empty.")
                speak("I've also printed the full content to the terminal.")
                console.print(content)
            return True

        # ── List files ────────────────────────────────────────────────
        if "list files" in c or "what files" in c or "show files" in c:
            files = list_files()
            if not files:
                speak("There are no saved files yet.")
            else:
                speak(f"You have {len(files)} file{'s' if len(files) != 1 else ''}.")
                for f in files:
                    speak(f)
            return True

        # ── Delete file ───────────────────────────────────────────────
        if "delete file" in c or "remove file" in c:
            from voice import listen
            speak("Which file should I delete?")
            filename = listen(timeout=6)
            if filename and self._should_proceed(f"Permanently delete '{filename}'"):
                result = delete_file(filename)
                speak(result)
            return True

        # ── Notion: search ────────────────────────────────────────────
        if "notion" in c and ("find" in c or "search" in c):
            from voice import listen
            query = c.replace("notion", "").replace("find", "").replace("search", "").strip()
            if not query:
                speak("What should I search for in Notion?")
                query = listen(timeout=6)
            if query and self._should_proceed(f"Search Notion for '{query}'"):
                try:
                    results = notion_mcp.search_notion(query)
                    if not results:
                        speak("I didn't find anything in Notion for that.")
                    else:
                        speak(f"Found {len(results)} result{'s' if len(results) != 1 else ''}.")
                        for r in results[:3]:
                            speak(r["title"])
                        console.print(results)
                except Exception as e:
                    speak(f"Notion search failed. {str(e)}")
            return True

        # ── Notion: read page ─────────────────────────────────────────
        if "read notion" in c or "notion page" in c:
            from voice import listen
            speak("Give me the Notion page ID.")
            page_id = listen(timeout=6)
            if page_id and self._should_proceed(f"Read Notion page {page_id}"):
                try:
                    content = notion_mcp.read_page(page_id)
                    speak("Here's a preview.")
                    speak(content[:400].replace("#", "").strip())
                    console.print(content)
                except Exception as e:
                    speak(f"Couldn't read that page. {str(e)}")
            return True

        # ── Notion: create page ───────────────────────────────────────
        if "create notion" in c or "new notion" in c or "save to notion" in c:
            from voice import listen
            speak("What should I title the Notion page?")
            title = listen(timeout=6)
            if not title:
                speak("I didn't catch a title.")
                return True
            speak("Dictate the page content. Say 'done' when finished.")
            lines = []
            while True:
                line = listen(timeout=10, phrase_time_limit=20)
                if "done" in line:
                    break
                if line:
                    lines.append(line)
            content = "\n\n".join(lines)
            if self._should_proceed(f"Create a Notion page titled '{title}'"):
                try:
                    url = notion_mcp.create_page(title, content)
                    speak(f"Notion page created. URL printed to the terminal.")
                    console.print(f"[green]Notion page URL:[/green] {url}")
                except Exception as e:
                    speak(f"Couldn't create the Notion page. {str(e)}")
            return True

        # ── Goodbye ───────────────────────────────────────────────────
        if any(w in c for w in ["exit", "quit", "goodbye", "shut down",
                                  "stop", "bye"]):
            speak("Goodbye. I'll be here when you need me.")
            return False

        # ── Fallback ──────────────────────────────────────────────────
        speak("I heard you, but I'm not sure how to handle that yet. Say 'help' for a list of things I can do.")
        return True

    def _say_help(self):
        speak(f"Here's what I can do. "
              f"Search the web for anything you ask. "
              f"Write, read, list, and delete markdown files. "
              f"Create and read Notion pages. "
              f"Open websites like Google, YouTube, LinkedIn, or GitHub. "
              f"Tell you the time and date. "
              f"And I can switch between confirm mode and auto mode anytime.")
