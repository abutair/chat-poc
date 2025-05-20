from dotenv import load_dotenv
from string import Template
from llm_config import client, llm_model

load_dotenv()

def load_prompt_template(file_path="prompts/prompt_template.txt"):
    with open(file_path, "r") as file:
        template_content = file.read()
        # Replace single braces within code examples with double braces to escape them
        processed_content = template_content.replace('"{value}"', '"{{value}}"')
        return Template(processed_content)


def generate_pandas_code(messages, sheets):
    # print("gen_code.py run success")
    sample = ""

    # Take a preview from each sheet in the Excel file
    for sheet_name, df in sheets.items():
        sample += f"--- {sheet_name} ---\n"
        sample += df.head(3).to_string(index=False) + "\n"

    prompt_template = load_prompt_template()

    # NOTE TO SELF: Be very careful editing this prompt. I have to modify it a lot so that the chatbot understands things better
    # Generate the actual prompt by replacing placeholders
    try:
        # Format the latest message (i.e., current question) with full Excel context
        latest_question = messages[-1]["content"]
        formatted_prompt = prompt_template.substitute(
            sheet_names=list(sheets.keys()),
            sample_data=sample,
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
        # ⚠️ Change this to be dynamic later or configurable in .env
    )
    return response.choices[0].message.content.strip()