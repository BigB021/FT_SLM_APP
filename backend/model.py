# Author : Youssef Aitbouddroub
import torch
from peft import PeftModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

#----------------------------------------------- Check CUDA availability and GPU properties -----------------------------------------------
print(f"torch version: {torch.__version__}")
print(f"CUDA version: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    # Warning message
    print("[!] Warning: Torch version doesnt support gpu or no gpu was found!")


#----------------------------------------------- Load the Model -----------------------------------------------
def load_fine_tuned_model():
    """
    Loads the local FLAN-T5 base model together with the
    fine-tuned LoRA adapter
    Automatically loads onto the GPU if CUDA is available.
    Sets the model to evaluation mode.

    Returns: tuple(model, tokenizer)
    
    """
    base_model = AutoModelForSeq2SeqLM.from_pretrained("./models/flan-t5-base-local", device_map="auto", trust_remote_code=True, dtype=torch.bfloat16)

    fine_tuned_model = PeftModel.from_pretrained(
        base_model,
        "./models/flan-t5-base-totto-lora-finetuned"
    )


    tokenizer = AutoTokenizer.from_pretrained("./models/flan-t5-base-local")

    fine_tuned_model.eval()
    fine_tuned_model.cuda()

    print("[+] Model Loaded sucessfully")
    return fine_tuned_model, tokenizer

#----------------------------------------------- Prompt Construction -----------------------------------------------
def coerce_table(table):
    """Convert raw string tables from JSON into row/cell objects expected by the prompt builder."""
    if isinstance(table, str):
        rows = []
        for line in table.splitlines():
            line = line.strip()
            if not line:
                continue
            cells = [{"value": cell.strip(), "is_header": False} for cell in line.split("\t")]
            rows.append(cells)
        if rows:
            for cell in rows[0]:
                cell["is_header"] = True
        return rows
    return table


def get_header_block_end(table):
    """The header block is the maximal prefix of rows where EVERY cell is
    is_header=True. This correctly excludes tables where only the first
    COLUMN is marked as a row-label inside data rows (e.g. Chicago Bears'
    'Year' column) - those rows are only partially header-marked, so they
    fail the 'every cell' test and the block stops before them."""
    table = coerce_table(table)
    end = 0
    for row in table:
        if row and all(cell.get("is_header") for cell in row):
            end += 1
        else:
            break
    return end


def expand_header_row(row):
    """Expands a header row's cells across their column_span so position i
    lines up with actual column i, matching data-row layout."""
    expanded = []
    for cell in row:
        expanded.extend([cell["value"]] * max(cell.get("column_span", 1), 1))
    return expanded


def is_locally_uniform(table, header_block_end, target_row_idx, header_width):
    """Only require rows BETWEEN the header and the target to match the
    header's width. A width change AFTER the target row (e.g. a second
    inline sub-table starting later) doesn't make the target's own column
    position untrustworthy."""
    table = coerce_table(table)
    for row in table[header_block_end:target_row_idx + 1]:
        if len(row) != header_width:
            return False
    return True


def get_column_header(table, target_row_idx, target_col_idx):
    table = coerce_table(table)
    header_block_end = get_header_block_end(table)
    if header_block_end == 0 or target_row_idx < header_block_end:
        return ""
    if not is_locally_uniform(table, header_block_end, target_row_idx, len(table[header_block_end - 1])):
        return ""  # can't trust positional alignment in this table - skip, don't guess

    parts = []
    for row in table[:header_block_end]:
        expanded = expand_header_row(row)
        if target_col_idx >= len(expanded):
            return ""
        val = expanded[target_col_idx].strip()
        if val and (not parts or parts[-1] != val):
            parts.append(val)
    return " ".join(parts)


WINDOW = 3  # rows of context kept on each side of a highlighted row


def select_rows(table, highlighted_cells, window=WINDOW):
    """Returns a sorted list of row indices to keep: the header block, plus
    a window of rows around every highlighted row."""
    table = coerce_table(table)
    header_end = get_header_block_end(table)
    keep = set(range(header_end))
    for r, _ in highlighted_cells:
        keep.update(range(max(0, r - window), min(len(table), r + window + 1)))
    return sorted(keep)


def build_table_str(table, keep_indices, highlighted_cells):
    """Serializes only the kept rows. Each row keeps a cheap [i] row-index
    prefix (proven sufficient for row lookup on its own - see Section 4's
    intro). Only the specific highlighted cell(s) get the heavier (r,c)
    tag, wrapped around their value in place - not every cell in the row.

    This is a deliberate revision: tagging EVERY cell (the first version of
    this fix) roughly doubled average token length, because T5's tokenizer
    splits mixed letter+digit+bracket patterns like "[R123C45]" into many
    small tokens, and tagging every column of every row scales that cost by
    (rows x columns) instead of just (rows). Tagging only the highlighted
    cells keeps the same literal-lookup benefit where it's actually needed,
    at a cost of roughly (rows) + (a handful of highlighted cells), not
    (rows x columns)."""
    table = coerce_table(table)
    highlighted_set = {(r, c) for r, c in highlighted_cells}
    lines = []
    prev = None
    for i in keep_indices:
        if prev is not None and i != prev + 1:
            lines.append("...")
        cell_strs = []
        for j, cell in enumerate(table[i]):
            if (i, j) in highlighted_set:
                cell_strs.append(f"({i},{j}){cell['value']}")
            else:
                cell_strs.append(cell["value"])
        lines.append(f"[{i}] " + " | ".join(cell_strs))
        prev = i
    return "\n".join(lines)

def build_prompt(sample):
    """ 
    Constructs the final prompt sent to the language model.

    The prompt consists of:

    - Task description
    - Page title
    - Section title
    - Additional context
    - Highlighted cells
    - Windowed table
     """
    table = sample["table"]
    highlighted_cells = sample["highlighted_cells"]

    keep_indices = select_rows(table, highlighted_cells)
    table_str = build_table_str(table, keep_indices, highlighted_cells)

    highlighted_lines = []
    for row, col in highlighted_cells:
        header = get_column_header(table, row, col)
        label = f" ({header})" if header else ""
        highlighted_lines.append(f"({row},{col}){label}")
    highlighted_str = "\n".join(highlighted_lines)

    prompt = f"""Task:
Generate a single factual sentence describing the information contained in the highlighted cells.
Use only information provided below.
Do not invent facts.\n"""
    if "table_page_title" in sample and sample["table_page_title"]:
        prompt += f"Page Title:\n{sample['table_page_title']}\n"
    if "table_section_title" in sample and sample["table_section_title"]:
        prompt += f"Section Title:\n{sample['table_section_title']}\n"
    if "table_section_text" in sample and sample["table_section_text"]:
        prompt += f"Additional Context:\n{sample['table_section_text']}\n"
    if highlighted_cells:
        prompt += f"Highlighted Cells:\n{highlighted_str}\n"

    prompt += f"Table:\n{table_str}\nAnswer:\n"
    return prompt

#----------------------------------------------- Inference -----------------------------------------------
def generate_summary(model, tokenizer, prompt, max_new_tokens=64, num_beams=4):
    """
    Runs inference using the fine-tuned language model.

    Parameters:model, tokenizer, prompt

    Returns: Generated natural language summary :str

    Generation Settings
    -------------------
    Beam Search
    No Sampling
    64 Maximum Tokens
    """
    inputs = tokenizer(
        prompt,
        truncation=True,
        max_length=384,          
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            do_sample=False,      # matches quantitative eval settings
        )

    return tokenizer.decode(output[0], skip_special_tokens=True)

#----------------------------------------------- Module Testing -----------------------------------------------

def test_module():
    sales_mock_data = {
        "table": "Product_ID\tSale_Date\tSales_Rep\tRegion\tSales_Amount\tQuantity_Sold\tProduct_Category\tUnit_Cost\tUnit_Price\tCustomer_Type\tDiscount\tPayment_Method\tSales_Channel\tRegion_and_Sales_Rep\n1052\t2023-02-03\tBob\tNorth\t5053.97\t18\tFurniture\t152.75\t267.22\tReturning\t0.09\tCash\tOnline\tNorth-Bob\n1093\t2023-04-21\tBob\tWest\t4384.02\t17\tFurniture\t3816.39\t4209.44\tReturning\t0.11\tCash\tRetail\tWest-Bob\n1015\t2023-09-21\tDavid\tSouth\t4631.23\t30\tFood\t261.56\t371.4\tReturning\t0.2\tBank Transfer\tRetail\tSouth-David\n1072\t2023-08-24\tBob\tSouth\t2167.94\t39\tClothing\t4330.03\t4467.75\tNew\t0.02\tCredit Card\tRetail\tSouth-Bob\n",
        "table_page_title": "Sales Sample Data",
        "table_section_title": "Sales Data",
        "table_section_text": "This dataset represents synthetic sales data generated for practice purposes only. It is not real-time or based on actual business operations, and should be used solely for educational or testing purposes. The dataset contains information that simulates sales transactions across different products, regions, and customers. Each row represents an individual sale event with various details associated with it.",
        "highlighted_cells": [[2,2],[2,4],[2,6],[2,7]]
    }

    sales_prompt = build_prompt(sales_mock_data)
    ft_model,tokenizer = load_fine_tuned_model()
    summary = generate_summary(ft_model,tokenizer, sales_prompt)
    print(summary)

if __name__ == "__main__":
    print("Summary generated:")
    test_module()