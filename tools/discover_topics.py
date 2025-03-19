from bertopic import BERTopic
from pathlib import Path

docs = []

# directory = Path("test_data/obsidian")
directory = Path("test_data/Obsidian Main Copy")
file_type = "*.md"

# for file in directory.rglob(file_type):
for file in directory.glob(file_type):
  print(file)
  with open(file, "r", encoding="utf-8") as f:
    docs.append(f.read())

# print(docs)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(docs)
print(topics)
