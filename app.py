import streamlit as st
import re

SYMBOLS = {
    'alpha': ('α', 'alpha'), 'beta': ('β', 'beta'), 'gamma': ('γ', 'gamma'),
    'delta': ('δ', 'delta'), 'vartheta': ('ϑ', 'vartheta'), 'epsilon': ('ε', 'epsilon'),
    'zeta': ('ζ', 'zeta'), 'eta': ('η', 'eta'), 'theta': ('θ', 'theta'),
    'iota': ('ι', 'iota'), 'kappa': ('κ', 'kappa'), 'lambda': ('λ', 'lambda'),
    'mu': ('μ', 'mu'), 'nu': ('ν', 'nu'), 'xi': ('ξ', 'xi'),
    'omicron': ('ο', 'omicron'), 'pi': ('π', 'pi'), 'rho': ('ρ', 'rho'),
    'sigma': ('σ', 'sigma'), 'tau': ('τ', 'tau'), 'upsilon': ('υ', 'upsilon'),
    'phi': ('φ', 'phi'), 'chi': ('χ', 'chi'), 'psi': ('ψ', 'psi'), 'omega': ('ω', 'omega'),
    'infty': ('∞', 'infinity'), 'pm': ('±', '+-'), 'mp': ('∓', '−+'),
    'leq': ('≤', '<='), 'geq': ('≥', '>='), 'neq': ('≠', '!='), 'approx': ('≈', '~='),
    'times': ('×', '*'), 'div': ('÷', '/'), 'cdot': ('·', '*'),
    'rightarrow': ('→', '->'), 'leftarrow': ('←', '<-'), 'leftrightarrow': ('↔', '<->'),
    'sum': ('∑', 'sum'), 'prod': ('∏', 'prod'), 'int': ('∫', 'integral'),
    'partial': ('∂', 'partial'), 'nabla': ('∇', 'nabla'), 'forall': ('∀', 'forall'),
    'exists': ('∃', 'exists'), 'in': ('∈', 'in'), 'notin': ('∉', 'notin'),
    'subset': ('⊂', 'subset'), 'subseteq': ('⊆', 'subseteq'), 'supset': ('⊃', 'supset'),
    'supseteq': ('⊇', 'supseteq'), 'emptyset': ('∅', 'emptyset'),
    'angle': ('∠', 'angle'), 'degree': ('°', 'degree'), 'prime': ("′", "prime"),
}

def remove_dollar_signs(text):
    text = re.sub(r'\$\$(.+?)\$\$', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\$(.+?)\$', r'\1', text, flags=re.DOTALL)
    return text

def replace_tex_symbols(text, symbol_dict, use_unicode=True):
    def symbol_replacer(match):
        name = match.group(1)
        return symbol_dict.get(name, (match.group(0), name))[0 if use_unicode else 1]
    return re.sub(r'\\([a-zA-Z]+)', symbol_replacer, text)

def clean_latex(text, symbol_dict, use_unicode=True):
    text = remove_dollar_signs(text)

    math_blocks = {}
    def preserve_math_block(match):
        key = f"__MATHBLOCK_{len(math_blocks)}__"
        content = match.group(1)
        math_blocks[key] = content  # Preserve content inside \[...\]
        return key

    # Replace \[...\] with placeholders
    text = re.sub(r'\\\[(.*?)\\\]', preserve_math_block, text, flags=re.DOTALL)

    blocks = re.split(r'(\\begin\{.*?\}.*?\\end\{.*?\})', text, flags=re.DOTALL)
    processed = []

    for block in blocks:
        if re.match(r'\\begin\{.*?\}.*?\\end\{.*?\}', block, flags=re.DOTALL):
            processed.append(block.strip())
        else:
            block = block.replace(r'\sqrt', 'SQRTPLACEHOLDER')
            block = block.replace('\\\\', '\n')
            block = re.sub(r'\\\((.*?)\\\)', r'\1', block)
            block = re.sub(r'\\text\{(.*?)\}', r'\1', block)
            block = re.sub(r'\\left', '', block)
            block = re.sub(r'\\right', '', block)
            block = re.sub(r'^\s*#{1,6}\s*', '', block, flags=re.MULTILINE)
            block = re.sub(r'^\s*[-_]{3,}\s*$', '', block, flags=re.MULTILINE)
            block = replace_tex_symbols(block, symbol_dict, use_unicode)
            block = block.replace('SQRTPLACEHOLDER', r'\sqrt')
            processed.append(block.strip())

    result = "\n".join(processed).strip()

    # Reinsert preserved math blocks
    for key, original in math_blocks.items():
        result = result.replace(key, original.strip())

    return result

def format_output(text, fmt):
    text = re.sub(r'^\s*-\s+', '• ', text, flags=re.MULTILINE)
    if fmt == "Markdown":
        return text
    elif fmt == "Plain Text":
        return re.sub(r'[`*_]', '', text)
    elif fmt == "HTML":
        return text.replace('\n', '<br>').replace('`', '')
    return text

# Streamlit App
st.set_page_config(page_title="LaTeX to Markdown/Text Converter", layout="centered")
st.title("🧠 LaTeX to Markdown/Text Converter")

dark_mode = st.checkbox("Enable Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        .stTextArea textarea { background-color: #222; color: white; }
        .stButton button { background-color: #333; color: white; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background-color: white; color: black; }
        .stTextArea textarea { background-color: white; color: black; }
        .stButton button { background-color: #f0f0f0; color: black; }
        </style>
    """, unsafe_allow_html=True)

latex_input = st.text_area(
    "Enter LaTeX Expression:",
    height=200,
    placeholder=r"Example: \frac{a^2 + b^2}{a + b} or \[ \rho(r) = \begin{cases} 4A \epsilon_0 r & \text{for } r < a, \\ 0 & \text{for } a < r < b \end{cases} \]",
    key="latex_area"
)

use_unicode = st.checkbox("Use Unicode (e.g., α, β, x²)", value=True)
output_format = st.radio("Select Output Format:", ["Markdown", "Plain Text", "HTML"])

def process_conversion():
    if latex_input.strip() == "":
        st.warning("Please enter a LaTeX expression to convert.")
        return None
    else:
        result = clean_latex(latex_input, SYMBOLS, use_unicode)
        return format_output(result, output_format)

if st.button("Convert"):
    converted_output = process_conversion()
    if converted_output:
        st.session_state["converted_output"] = converted_output
        st.success("✅ Converted Output:")
        if output_format == "HTML":
            st.markdown(converted_output, unsafe_allow_html=True)
        else:
            st.code(converted_output, language="markdown" if output_format == "Markdown" else "")

if 'converted_output' in st.session_state:
    file_ext = {"Markdown": "md", "Plain Text": "txt", "HTML": "html"}[output_format]
    mime_type = {"Markdown": "text/markdown", "Plain Text": "text/plain", "HTML": "text/html"}[output_format]
    st.download_button(
        f"📄 Download as .{file_ext}",
        data=st.session_state["converted_output"],
        file_name=f"converted_output.{file_ext}",
        mime=mime_type
    )
