import os
import frontmatter
from openai import OpenAI
import json
import re

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing required environment variable: OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# Define note categories
NOTE_CATEGORIES = [
    "fleeting", "literature", "permanent", "reference", 
    "project", "meeting", "other"
]

# Directories to exclude from processing
EXCLUDED_DIRECTORIES = {"Daily", "Clippings", "Books"}

def parse_json(response_text, filename):
    cleaned_text = response_text.strip()
    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if match:
        cleaned_text = match.group(1)

    try:
      parsed_json = json.loads(cleaned_text)
      return parsed_json
    except json.JSONDecodeError as e:
      print(f"Error parsing JSON for {filename}")
      print(e)
      # print(result)
      print(f"Raw LLM response: '{response_text}'")
      return None

# Function to classify note content
def classify_note(content):
    prompt = f"""
    You are an AI assistant that classifies personal notes in an Obsidian vault.
    The possible categories are: {", ".join(NOTE_CATEGORIES)}.
    If none fit, suggest a new category.
    
    Here is the note content:
    ---
    {content}
    ---
    
    Return a JSON object that contains two fields - one named category that contains the best-fitting category, a,and the other named category_reason that contains a brief reason for how you determined the category.
    """

    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    return result

# Function to process notes in the Obsidian Vault recursively
def process_vault(vault_path):
    for root, dirs, files in os.walk(vault_path):  # Walk through all subdirectories
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]
        
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                
                with open(filepath, "r", encoding="utf-8") as file:
                    post = frontmatter.load(file)

                content = post.content
                result = classify_note(content)

                # handle empty response from LLM
                if not result:
                  print(f"Invalid response from LLM for file {filename}")
                  continue

                result_json = parse_json(result, filename)

                # handle invalid JSON response from LLM
                if not result_json:
                  print(f"Invalid JSON response from LLM for file {filename}")
                  print(result)
                  continue
    
                category = result_json.get("category", "other")
                category_reason = result_json.get("category_reason")

                print(f"File: '{filename}'")
                print(f"Category: {category}")
                print(f"Explanation: {category_reason}\n")               

                # update frontmatter section in the MD file with data from the LLM
                post.metadata["type"] = category
                post.metadata["type_reason"] = category_reason
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(frontmatter.dumps(post))

# Set the path to your Obsidian vault
vault_path = "./test_data/obsidian"
process_vault(vault_path)
