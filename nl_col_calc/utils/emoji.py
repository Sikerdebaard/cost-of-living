from dataclasses import dataclass

@dataclass
class Emoji:
    """Class for keeping track of standard Emojis used for the app."""
    page_emoji: str = '💸'
    notification: str = '🤖'

emoji = Emoji()
