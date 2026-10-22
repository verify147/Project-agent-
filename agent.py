import os
import sys
import json
import time
import urllib.request
import urllib.error
from pypdf import PdfReader

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def call_groq_api(prompt_text, api_key):
    """Sends requests safely using native urllib with auto-retry on rate limits."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": "You are a rigorous institutional academic supervisor, researcher, and senior editor."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.3
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        },
        method="POST"
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                return res_json["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_time = 15 * (attempt + 1)
                print(f"\n[!] Rate limit reached. Pausing for {wait_time}s to reset token bucket...")
                time.sleep(wait_time)
                continue
            print(f"\n[X] HTTP Error {e.code}: {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"\n[X] API Communication Error: {e}")
            sys.exit(1)

def generate_section(section_title, prompt, sample_text, department, school_name, api_key):
    print(f"\n[+] Step 1/2: Generating initial draft for {section_title}...")
    raw_draft = call_groq_api(prompt, api_key)
    
    print(f"[+] Pausing 6 seconds for token pacing...")
    time.sleep(6) 
    
    print(f"[+] Step 2/2: Applying departmental stylistic reasoning and polish...")
    refinement_prompt = f"""
You are an expert academic editor and supervisor for the Department of {department}, {school_name}. 
Below is an initial draft and an approved departmental reference sample showing the exact institutional tone and cadence.

Refine and format the draft to match the required academic standard precisely.

--- DEPARTMENTAL STYLE GUIDE (SAMPLE EXCERPT) ---
{sample_text[:1500]}
--------------------------------------------------

--- DRAFT TO REFINE ({section_title}) ---
{raw_draft}
--------------------------------------------------

Provide the final polished text for {section_title}.
"""
    refined_text = call_groq_api(refinement_prompt, api_key)
    print(f"[✓] Successfully completed: {section_title}")
    return refined_text

def main():
    clear_screen()
    print("=" * 65)
    print("    FEDERAL POLYTECHNIC STEP-BY-STEP THESIS GENERATOR")
    print("=" * 65)

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        api_key = input("Please enter your Groq API Key: ").strip()
        if not api_key:
            print("[X] Error: API key is required.")
            sys.exit(1)

    topic = input("\nEnter the project topic: ").strip()
    if not topic:
        print("[X] Error: Topic cannot be blank.")
        sys.exit(1)

    schools = {
        "1": {
            "name": "School of Applied Sciences",
            "departments": [
                ("Computer Science", "computer_science.pdf"),
                ("Science Laboratory Technology", "slt.pdf")
            ]
        },
        "2": {
            "name": "School of Engineering Technology",
            "departments": [
                ("Mechanical Engineering", "mechanical.pdf"),
                ("Electrical/Electronic Engineering", "electrical.pdf")
            ]
        },
        "3": {
            "name": "School of Business Studies",
            "departments": [
                ("Accountancy", "accountancy.pdf"),
                ("Business Administration and Management", "business_admin.pdf")
            ]
        }
    }

    print("\n--- SELECT FACULTY / SCHOOL ---")
    for key, school_info in schools.items():
        print(f"{key}. {school_info['name']}")

    school_choice = input("\nEnter School option number: ").strip()
    if school_choice not in schools:
        school_choice = "2"

    selected_school = schools[school_choice]
    dept_list = selected_school["departments"]

    print(f"\n--- SELECT DEPARTMENT ---")
    for idx, (dept_name, _) in enumerate(dept_list, start=1):
        print(f"{idx}. {dept_name}")

    dept_choice = input(f"\nEnter Department option number: ").strip()
    try:
        dept_index = int(dept_choice) - 1
        department, target_pdf = dept_list[dept_index]
    except Exception:
        department, target_pdf = dept_list[0]

    print(f"\n[+] Target Department: {department} ({selected_school['name']})")

    sample_text = ""
    if os.path.exists(target_pdf):
        print(f"[+] Ingesting institutional DNA from {target_pdf}...")
        try:
            reader = PdfReader(target_pdf)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    sample_text += text + "\n"
            print("[✓] Institutional sample successfully loaded.")
        except Exception as e:
            print(f"[!] Warning: Could not parse PDF ({e}).")
    else:
        print(f"[!] Note: PDF '{target_pdf}' not found. Using baseline academic standards.")

    manual_notes = input("\nEnter any specific raw data, dimensions, or custom notes (Press Enter to skip): ").strip()
    if not manual_notes:
        manual_notes = "Standard project implementation parameters."

    # Full Section Roadmap
    sections_to_generate = [
        ("Title Page & Certification", f"Draft the Title Page, Approval/Certification page for a thesis titled '{topic}' in the Department of {department}, {selected_school['name']}."),
        ("Dedication", "Draft a formal academic Dedication page."),
        ("Acknowledgements", "Draft comprehensive academic Acknowledgements expressing gratitude to supervisors, family, and the institution."),
        ("Abstract", f"Draft a concise, high-impact Academic Abstract (approx. 300 words) summarizing the background, methodology, results, and conclusion for: '{topic}'."),
        ("Chapter One - Introduction", f"Write Chapter 1 covering: 1.1 Background of the Study, 1.2 Statement of the Problem, 1.3 Objectives of Study, 1.4 Justification of Study, 1.5 Scope of Study. Context: {manual_notes}"),
        ("Chapter Two - Literature Review", f"Write Chapter 2 covering: 2.1 Overview of Production, 2.2 Agro-ecological Zones / Technical Background, 2.3 Value Chain, 2.4-2.7 Technical Review of Prior Work and Machines related to '{topic}'."),
        ("Chapter Three - Materials and Methods", f"Write Chapter 3 covering: 3.1 Materials and Equipment Used, 3.2 Machine Description and Working Principle, 3.3 Design Considerations, 3.4 Design Calculations, 3.5 Fabrication Procedure, 3.6 Performance Evaluation Procedure."),
        ("Chapter Four - Results and Discussion", f"Write Chapter 4 covering: 4.1 Results Presentation, 4.2 Statistical Analysis of Results, 4.4 Discussion of findings for '{topic}'."),
        ("Chapter Five - Summary, Conclusion and Recommendations", f"Write Chapter 5 covering: 5.1 Summary of findings, 5.2 Conclusion, 5.3 Recommendations based on '{topic}'."),
        ("References", "Generate a comprehensive list of academic references in APA format supporting this engineering/technical research project.")
    ]

    print("\n" + "=" * 65)
    print("      SETUP COMPLETE. READY FOR STEP-BY-STEP GENERATION")
    print("=" * 65)

    for idx, (title, prompt_instruction) in enumerate(sections_to_generate, start=1):
        print(f"\n[{idx}/{len(sections_to_generate)}] Next up: **{title}**")
        user_command = input("Press [Enter] to generate this section (or type 'skip' to pass, 'exit' to quit): ").strip().lower()
        
        if user_command == 'exit':
            print("\n[!] Exiting generator session. All previously saved sections are safe.")
            break
        if user_command == 'skip':
            print(f"[!] Skipped {title}.")
            continue

        # Generate and refine section
        section_content = generate_section(title, prompt_instruction, sample_text, department, selected_school['name'], api_key)

        # Save individually right away
        safe_filename = f"section_{idx}_{title.lower().replace(' ', '_').replace('-', '').replace('/', '_')}.txt"
        with open(safe_filename, "w", encoding="utf-8") as f:
            f.write(f"{title.upper()}\n{'='*70}\n\n{section_content}")
        
        print(f"[✓] Saved section securely to file: `{safe_filename}`")
        print("-" * 65)
        
        # Safe cooldown pause between sections
        time.sleep(3)

    print("\n" + "=" * 65)
    print("[✓] Session complete! Check your Colab folder for your individual section files.")
    print("=" * 65)

if __name__ == "__main__":
    main()
