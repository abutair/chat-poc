# gen_code.py - Updated to handle index-aware table information

from dotenv import load_dotenv
from string import Template
from llm_config import client, llm_model

load_dotenv()

def load_prompt_template(file_path="prompts/prompt_template.txt"):
    with open(file_path, "r") as file:
        return Template(file.read())

def generate_sql_prompt(messages, sheets):
    sample = ""

    # Format the preview of each table with index information
    for table_name, table_info in sheets.items():
        sample += f"--- {table_name} ---\n"
        
        # Handle both old format (list of dicts) and new format (dict with metadata)
        if isinstance(table_info, dict) and 'preview' in table_info:
            # New format with index information
            rows = table_info['preview']
            row_count = table_info.get('row_count', 0)
            indexed_columns = table_info.get('indexed_columns', [])
            
            # Add table metadata
            sample += f"Table Size: {row_count:,} rows\n"
            if indexed_columns:
                sample += f"Indexed Columns: {', '.join(indexed_columns)}\n"
            sample += f"Sample Data:\n"
        else:
            # Old format - backward compatibility
            rows = table_info if isinstance(table_info, list) else []
        
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
        
        sample += "\n"  # Add space between tables

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
        max_tokens=512,
        temperature=0.1  # Lower temperature for more consistent SQL generation
    )

    return response.choices[0].message.content.strip()