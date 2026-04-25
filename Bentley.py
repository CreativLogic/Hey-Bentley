"""
Hey-Bentley — Main
Your personal AI voice agent. Say 'Hey Bentley' to wake him.
"""

import sys
import logging
from rich.console import Console
from rich.panel   import Panel

from config  import BENTLEY_NAME, WAKE_PHRASE, LOG_LEVEL, LOGS_DIR
from voice   import speak, listen
from actions import ActionRouter

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level    = getattr(logging, LOG_LEVEL, logging.INFO),
    format   = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler(LOGS_DIR / "bentley.log"),
        logging.StreamHandler(sys.stdout),
    ]
)
logger  = logging.getLogger("bentley")
console = Console()


def boot_screen():
    console.print(Panel.fit(
        f"[bold cyan]BENTLEY VOICE AGENT[/bold cyan]\n"
        f"[dim]Say '[bold]{WAKE_PHRASE}[/bold]' to wake him up.[/dim]\n"
        f"[dim]Say 'auto mode' or 'confirm mode' to change behaviour.[/dim]\n"
        f"[dim]Say 'exit' or 'goodbye' to shut down.[/dim]",
        border_style="cyan",
        title="🎙 Bentley",
    ))


def main():
    boot_screen()
    router = ActionRouter()

    speak(f"Hello. I'm {BENTLEY_NAME}, your voice assistant. "
          f"I'm currently in {router.mode} mode. "
          f"Say hey Bentley to get my attention.")

    running = True

    while running:
        # ── Wait for wake word ─────────────────────────────────────────
        phrase = listen(timeout=10)
        if not phrase:
            continue

        if WAKE_PHRASE not in phrase:
            # Allow commands without wake word while already awake
            # (useful for rapid fire interaction)
            command = phrase
        else:
            # Strip the wake word, get the rest
            command = phrase.replace(WAKE_PHRASE, "").strip()
            if not command:
                speak("Yes? What would you like?")
                command = listen(timeout=8)
                if not command:
                    continue

        if command:
            try:
                running = router.handle(command)
            except Exception as e:
                logger.exception("Unhandled error in action router")
                speak("Something went wrong. Check the logs for details.")


if __name__ == "__main__":
    main()
