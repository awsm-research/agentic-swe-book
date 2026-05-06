import subprocess

# VULNERABLE: Shell=True with user input
def run_analysis_bad(filename: str) -> str:
    result = subprocess.run(
        f"analyze_tool {filename}",
        shell=True,  # DANGEROUS with user input
        capture_output=True,
        text=True,
    )
    return result.stdout


# SAFE: Shell=False with argument list
def run_analysis(filename: str) -> str:
    # Validate filename first
    if not filename.replace("_", "").replace("-", "").replace(".", "").isalnum():
        raise ValueError(f"Invalid filename: {filename}")

    result = subprocess.run(
        ["analyze_tool", filename],  # List form, no shell interpretation
        shell=False,
        capture_output=True,
        text=True,
    )
    return result.stdout
