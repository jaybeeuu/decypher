import re
from decypher import decypher_text_with_table

with open("./cypher-text.txt", "r") as cypher_file:
  cypher_text = cypher_file.read()

with open("./plain-text.txt", "r") as plain_file:
  plain_text = plain_file.read()

print(f"Text:\n")

def make_print_over_text():
  last_text_lines = 0
  def print_over_text(text: str):
      nonlocal last_text_lines
      print(f"\r\033[{last_text_lines + 1}A")
      print(text)
      last_text_lines = len(text.split("\n"))

  return print_over_text

print_over_text = make_print_over_text()
print_over_text(cypher_text)

cypher_table: dict[str, str] = {}

line = 1
column = 0
for idx, letter in enumerate(cypher_text):
  column += 1
  if re.match(r"[^A-Z]", letter):
    if letter == plain_text[idx]:
      if letter == "\n":
        line += 1
        column = 0
      continue
    else:
      raise RuntimeError(f"Mismatch ({line}, {column}): {letter}, {plain_text[idx]}")

  if (letter in cypher_table):
    if plain_text[idx] != cypher_table[letter]:
      raise RuntimeError(f"Mismatch ({line}, {column}): {letter} ({cypher_table[letter]}), {plain_text[idx]}")
  else:
    cypher_table[letter] = plain_text[idx]

  print_over_text(decypher_text_with_table(cypher_text, cypher_table))
