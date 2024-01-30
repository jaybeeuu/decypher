from decypher import decypher, decypher_text_with_table
from decypher.main import CypherTable

with open("./cypher-text.txt", "r") as cypher_file:
  cypher_text = cypher_file.read()

print(f"\n")

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

def make_on_cypher_table(frequency: int):
  counter: int = 0

  def on_cypher_table(cypher_table: CypherTable):
    nonlocal counter
    counter += 1

    if counter % frequency == 0:
      print_over_text(
        decypher_text_with_table(cypher_text, cypher_table)
      )

  return on_cypher_table

plain_text = decypher(
  cypher_text,
  on_cypher_table=make_on_cypher_table(5)
)

print_over_text(plain_text)


