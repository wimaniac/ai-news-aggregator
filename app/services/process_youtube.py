from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrappers.youtube import YoutubeScraper
from app.database.repository import Repository