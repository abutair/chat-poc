# gen_code.py

from dotenv import load_dotenv
from string import Template
from llm_config import client, llm_model

load_dotenv()

def load_prompt_template(file_path="prompts/prompt_template.txt"):
    with open(file_path, "r") as file:
        return Template(file.read())

def generate_sql_prompt(messages, sheets):
    sample = ""

    # Format the preview of each table (up to 3 rows) from the list of dicts
    for table_name, rows in sheets.items():
        sample += f"--- {table_name} ---\n"
        if not rows:
            sample += "(no data available)\n"
            continue

        # Get column names from the first row
        columns = list(rows[0].keys())
        # Create a tabular preview string manually
        header_line = " | ".join(columns)
        sample += header_line + "\n"
        sample += "-" * len(header_line) + "\n"

        for row in rows:
            line = " | ".join(str(row.get(col, "")) for col in columns)
            sample += line + "\n"

    prompt_template = load_prompt_template()

    try:
        latest_question = messages[-1]["content"]
        formatted_prompt = prompt_template.substitute(
            sheet_names=", ".join(sheets.keys()),
            sample_data=sample.strip(),
            user_input=latest_question
        )
        messages[-1]["content"] = formatted_prompt
    except KeyError as e:
        raise ValueError(f"Prompt template is missing a placeholder: {e}")
    except ValueError as e:
        raise ValueError(f"String substitution error in prompt template: {e}")

    response = client.chat.completions.create(
        model=llm_model,
        messages=messages,
        max_tokens=512
    )

    return response.choices[0].message.content.strip()
