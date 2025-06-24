from langchain_together import ChatTogether
from langchain_core.prompts import  PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv # type: ignore
from pathlib import Path
import json 
import os
from tqdm import tqdm

load_dotenv()
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")
langchain_tracking = os.getenv("LANGCHAIN_TRACKING")
langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")

llm = ChatTogether(
    model = "mistralai/Mistral-7B-Instruct-v0.3",
    together_api_key= os.getenv("TOGETHER_API_KEY"), # type: ignore
    temperature=0
)

prompt = PromptTemplate(
    input_variables=["path", "content"],
    template="""
    You are an expert in SketchyBar configuration.

Given the following FILE:

Path: {path}

Content:
{content}

Your task is:

1. State the main PURPOSE of this file.
2. Provide a concise CONTENT SUMMARY.

Respond in JSON format:

{{
    "purpose": "...",
    "content_summary": "..."
}}
    """
)

parser = JsonOutputParser()

def annotate():
    parsed_path = Path("/Users/krishiv/Desktop/Projects/config-assistant/data/configs/parsed_json")
    out_path = Path("/Users/krishiv/Desktop/Projects/config-assistant/data/configs/annotated_json")
    out_path.mkdir(parents=True, exist_ok=True)

    for json_file in parsed_path.glob("*.json"):
        print(f"[📄] Annotating: {json_file.name}")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for file_key in tqdm(data["structure"]):
            entry = data["structure"][file_key]

            if not entry.get("purpose"):  # If empty — annotate
                try:
                    chain_input = {
                        "path": entry["path"],
                        "content": entry["content"]
                    }

                    # Run chain
                    output = llm.invoke(prompt.format(**chain_input))
                    result = parser.parse(output.content) # type: ignore

                    # Update entry
                    entry["purpose"] = result["purpose"]
                    entry["content_summary"] = result["content_summary"]

                except Exception as e:
                    print(f"[!] Error on {file_key}: {e}")

        # Save updated
        out_file = out_path / json_file.name
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[✅] Saved annotated: {out_file}")

# Run
if __name__ == "__main__":
    annotate()

