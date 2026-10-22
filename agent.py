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
            {"role": "system", "content": "You are a rigorous institutional academic supervisor and senior research editor."},
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
                wait_time = 12 * (attempt + 1)
                print(f"\n[!] Rate limit reached. Pausing for {wait_time}s to reset token bucket...")
                time.sleep(wait_time)
                continue
            print(f"\n[X] HTTP Error {e.code}: {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"\n[X] API Communication Error: {e}")
            sys.exit(1)

def main():
    clear_screen()
    print("=" * 65)
    print("      FEDERAL POLYTECHNIC AGENTIC THESIS GENERATOR")
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
                ("Computer Science", "samples/computer_science.pdf"),
                ("Science Laboratory Technology", "samples/slt.pdf")
            ]
        },
        "2": {
            "name": "School of Engineering Technology",
            "departments": [
                ("Mechanical Engineering", "samples/mechanical.pdf"),
                ("Electrical/Electronic Engineering", "samples/electrical.pdf")
            ]
        },
        "3": {
            "name": "School of Business Studies",
            "departments": [
                ("Accountancy", "samples/accountancy.pdf"),
                ("Business Administration and Management", "samples/business_admin.pdf")
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
    print(f"\n[✓] Selected School: {selected_school['name']}")

    print(f"\n--- SELECT DEPARTMENT ---")
    dept_list = selected_school["departments"]
    for idx, (dept_name, _) in enumerate(dept_list, start=1):
        print(f"{idx}. {dept_name}")

    dept_choice = input(f"\nEnter Department option number: ").strip()
    try:
        dept_index = int(dept_choice) - 1
        department, target_pdf = dept_list[dept_index]
    except Exception:
        department, target_pdf = dept_list[0]

    print(f"\n[+] Final Target Department: {department}")

    sample_text = ""
    if os.path.exists(target_pdf):
        print(f"[+] Reading approved structural sample for {department}...")
        try:
            reader = PdfReader(target_pdf)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    sample_text += text + "\n"
            print("[✓] Successfully ingested sample brain.")
        except Exception as e:
            print(f"[!] Warning: Could not parse PDF ({e}).")
    else:
        print(f"[!] Note: Specific PDF not found at '{target_pdf}'. Using general institutional standard.")

    manual_notes = input("\nEnter any specific raw data or notes (Press Enter to skip): ").strip()
    if not manual_notes:
        manual_notes = "None provided."

    # STEP 1: GENERATOR PASS
    print(f"\n[+] Step 1/2: Generating core draft for Chapter 1...")
    initial_prompt = f"""
Write comprehensive Chapter 1 content for an academic project on the topic: "{topic}" 
for the department of **{department}** under the **{selected_school['name']}**.

Cover these exact sub-headings thoroughly:
1.1 Background of the Study
1.2 Statement of the Problem
1.3 Aim and Objectives of the Study
1.4 Significance of the Study
1.5 Scope of the Study
1.6 Limitations of the Study
1.7 Definition of Technical Terms

Additional notes: {manual_notes}
"""
    raw_draft = call_groq_api(initial_prompt, api_key)

    print(f"[+] Pausing 8 seconds for token rate pacing...")
    time.sleep(8)

    # STEP 2: REFINEMENT PASS
    print(f"[+] Step 2/2: Applying departmental stylistic reasoning and polish...")
    refinement_prompt = f"""
You are an expert academic editor and supervisor for the Department of {department}, {selected_school['name']}. 
Below is an initial draft of Chapter 1, and an approved departmental reference sample showing the exact tone and cadence expected.

Rewrite and polish the raw draft so that its voice, phrasing style, and academic rigor match the departmental sample precisely. 

--- APPROVED DEPARTMENTAL SAMPLE (TONE GUIDE) ---
{sample_text[:1800]}
-------------------------------------------------------

--- RAW CHAPTER 1 DRAFT TO REVISE ---
{raw_draft}
-------------------------------------------------------

Provide the final, fully refined Chapter 1 text maintaining rigorous academic standards.
"""
    final_content = call_groq_api(refinement_prompt, api_key)

    print("\n" + "=" * 65)
    print(final_content)
    print("=" * 65)

    filename = "project_chapter_1.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"\n[✓] Agentic refinement complete! Saved to {filename}")

if __name__ == "__main__":
    main()
