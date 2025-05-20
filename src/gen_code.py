from dotenv import load_dotenv
import os
from llm_config import client, llm_model

load_dotenv()

def load_prompt_template(file_path="prompts/prompt_template.txt"):
    with open(file_path, "r") as file:
        template_content = file.read()
        return template_content


def generate_pandas_code(messages, sheets):
    # print("gen_code.py run success")
    sample = ""

    # Take a preview from each sheet in the Excel file
    for sheet_name, df in sheets.items():
        sample += f"--- {sheet_name} ---\n"
        sample += df.head(3).to_string(index=False) + "\n"

    sheet_names = list(sheets.keys())
    prompt_template = load_prompt_template()

    # NOTE TO SELF: Be very careful editing this prompt. I have to modify it a lot so that the chatbot understands things better
    # Generate the actual prompt by replacing placeholders
    try:
        # Format the latest message (i.e., current question) with full Excel context
        latest_question = messages[-1]["content"]
        
        # Use format() instead of Template.substitute() for safer string formatting
        formatted_prompt = prompt_template.replace("$sheet_names", str(sheet_names))
        formatted_prompt = formatted_prompt.replace("$sample_data", sample)
        formatted_prompt = formatted_prompt.replace("$user_input", latest_question)
        
        messages[-1]["content"] = formatted_prompt
    except Exception as e:
        raise ValueError(f"Error formatting prompt template: {e}")

    response = client.chat.completions.create(
        model=llm_model,
        messages=messages,
        max_tokens=512
        # ⚠️ Change this to be dynamic later or configurable in .env
    )
    return response.choices[0].message.content.strip()