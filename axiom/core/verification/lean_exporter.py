import os
import re
from typing import Dict, List, Optional

class LeanExporter:
    def __init__(self):
        pass

    def sanitize_name(self, name: str) -> str:
        """Converts human names to valid Lean snake_case identifiers."""
        # Replace spaces/hyphens and remove non-alphanumeric chars
        clean = re.sub(r"[^a-zA-Z0-9_\s]", "", name)
        clean = clean.replace(" ", "_").replace("-", "_").lower()
        # Prepend 'thm_' if it starts with a number
        if clean and clean[0].isdigit():
            clean = "thm_" + clean
        return clean or "theorem_identifier"

    def auto_generate_tactic(self, statement: str, variables: Dict[str, str]) -> str:
        """
        Analyse the theorem statement and variables to generate the best Mathlib tactic.
        """
        stmt = statement.strip()
        
        # Check if any variables are referenced in the statement
        has_vars = False
        for var in variables:
            # Match variable name as whole word
            if re.search(r"\b" + re.escape(var) + r"\b", stmt):
                has_vars = True
                break
                
        # If no variables are present, it is purely numerical
        if not has_vars:
            return "norm_num"
            
        # If it is an equality
        if "=" in stmt:
            parts = stmt.split("=")
            if len(parts) == 2 and parts[0].strip() == parts[1].strip():
                return "rfl"
            # Polynomial/ring identities are solved by ring / ring_nf
            return "ring"
            
        # If it is an inequality
        if any(op in stmt for op in ["<", ">", "≤", "≥", "<=", ">="]):
            return "linarith"
            
        return "sorry"

    def export_theorem(
        self, 
        name: str, 
        statement: str, 
        variables: Dict[str, str], 
        imports: Optional[List[str]] = None,
        proof_body: Optional[str] = None
    ) -> str:
        """
        Generate Lean 4 code string for a theorem.
        
        Args:
            name: The title/identifier of the theorem.
            statement: The formal mathematical statement.
            variables: Dict mapping variable names to types (e.g., {"x": "Int", "m": "Nat"}).
            imports: Optional list of Mathlib library paths.
            proof_body: Lean proof tactics (defaults to auto-generated tactic).
        """
        import_list = imports or [
            "Mathlib.Data.Nat.Basic",
            "Mathlib.Data.Int.Basic",
            "Mathlib.Tactic.Ring"
        ]
        
        # Add Linarith and NormNum to imports if they are needed
        if "Mathlib.Tactic.Linarith" not in import_list:
            import_list.append("Mathlib.Tactic.Linarith")
            
        lean_code = ""
        for imp in import_list:
            lean_code += f"import {imp}\n"
        lean_code += "\n"
        
        # Format variables block: e.g. (x y z : ℤ) (m : ℕ)
        # Group variables of same type
        type_groups: Dict[str, List[str]] = {}
        for var_name, var_type in variables.items():
            # Standardize common scientific types to Lean notations
            lean_type = var_type
            if var_type.lower() in ("int", "integer", "z"):
                lean_type = "ℤ"
            elif var_type.lower() in ("nat", "natural", "n"):
                lean_type = "ℕ"
            elif var_type.lower() in ("real", "r"):
                lean_type = "ℝ"
                
            type_groups.setdefault(lean_type, []).append(var_name)
            
        var_string = ""
        for l_type, vars_list in type_groups.items():
            var_string += f"({' '.join(vars_list)} : {l_type}) "
            
        clean_name = self.sanitize_name(name)
        
        # Decide proof body if not provided or set to default sorry
        if not proof_body or proof_body == "sorry":
            proof_body = self.auto_generate_tactic(statement, variables)
            
        # Construct the theorem block
        lean_code += f"theorem {clean_name} {var_string.strip()} :\n"
        # Shift statement for correct formatting
        lean_code += f"  {statement} := by\n"
        lean_code += f"  {proof_body}\n"
        
        return lean_code

    def save_lean_file(self, target_path: str, code: str) -> None:
        """Save the Lean code to target path, creating parent dirs if missing."""
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(code)
