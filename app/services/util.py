import re
from markdown_it import MarkdownIt


def clean_text(text: str) -> str:
  # Remove code blocks (```...```)
  no_code_blocks = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

  # Convert markdown to plain text
  md = MarkdownIt()
  parsed = md.render(no_code_blocks)
  
  # Remove Markdown artifacts (extra newlines or HTML tags if any)
  plain_text = re.sub(r"\n{2,}", "\n", parsed)
  plain_text = re.sub(r"<[^>]+>", "", plain_text)

  # Remove standalone numbers (e.g., bullet numbers, headings, dates)
  plain_text = re.sub(r"\b\d{1,5}\b", "", plain_text)

  # Remove urls
  plain_text = re.sub(r"http\S+", "", plain_text)

  # Optional: collapse extra spaces
  plain_text = re.sub(r"\s+", " ", plain_text).strip()

  return plain_text