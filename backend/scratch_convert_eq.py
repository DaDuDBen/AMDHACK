import json
import re

def convert_to_latex(eq: str) -> str:
    # 1. replace arrows and symbols
    eq = eq.replace('→', '\\rightarrow')
    eq = eq.replace('↑', '\\uparrow')
    eq = eq.replace('↓', '\\downarrow')
    eq = eq.replace('·', '\\cdot ')
    
    # 2. replace subscripts
    eq = eq.replace('₀', '_0').replace('₁', '_1').replace('₂', '_2').replace('₃', '_3')
    eq = eq.replace('₄', '_4').replace('₅', '_5').replace('₆', '_6').replace('₇', '_7')
    eq = eq.replace('₈', '_8').replace('₉', '_9')
    
    # 3. Handle text-heavy equations
    if "litmus" in eq or "solution" in eq or "Phenolphthalein" in eq or "Methyl orange" in eq or "Universal indicator" in eq or "color" in eq:
        # Don't try to mathrm these, just text wrap the parts if needed, or simply text wrap the whole thing
        parts = eq.split('\\rightarrow')
        left = parts[0].strip()
        right = parts[1].strip() if len(parts) > 1 else ""
        return f"\\text{{{left}}} \\rightarrow \\text{{{right}}}"
        
    # 4. wrap text parts in \text{}
    eq = eq.replace('(heat)', '\\text{ (heat)}')
    
    # tokenize
    tokens = re.split(r'(\s+|\+|\\rightarrow|\\uparrow|\\downarrow|\\cdot|\\text\{[^}]+\})', eq)
    out = []
    for t in tokens:
        if not t: continue
        if t.startswith('\\') or t.isspace() or t == '+':
            out.append(t)
        else:
            # wrap letters in mathrm
            t_mod = re.sub(r'[A-Za-z]+', r'\\mathrm{\g<0>}', t)
            t_mod = re.sub(r'\\mathrm{x}', r'x', t_mod) # x is usually variable
            out.append(t_mod)
    
    return "".join(out)

def main():
    path = r'c:\Users\Pranav\Downloads\amd\AMDHACK\backend\data\reactions.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for k, v in data.items():
        orig = v.get('balanced_equation', '')
        if orig:
            new_eq = convert_to_latex(orig)
            v['balanced_equation'] = new_eq

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
