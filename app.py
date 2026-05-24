import os
import json
import re
import chromadb
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile
from datetime import datetime
from nepali.datetime import nepalidate as nepali_date_module

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection(name="nepal_laws")

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# RAG RETRIEVAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━
def search_laws(query, n=5):
    results = collection.query(query_texts=[query], n_results=n)
    chunks = results["documents"][0]
    sources = results["metadatas"][0]
    return chunks, sources

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENT 1 — ROUTER AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━
def router_agent(user_problem):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are a routing agent.
            Classify the user's problem into ONE of these categories:
            - LABOUR (salary, firing, working hours, leave, employer issues)
            - CITIZENSHIP (citizenship certificate, documents, nationality)
            - LAND (land registration, disputes, ownership)
            - CONSUMER (cheating, fraud, product issues, shop disputes)
            - RIGHTS (fundamental rights, police, discrimination, freedom)

            Respond ONLY with JSON:
            {
                "category": "LABOUR",
                "confidence": "high",
                "reason": "User mentions salary not paid"
            }"""},
            {"role": "user", "content": user_problem}
        ]
    )
    try:
        content = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        result = json.loads(json_match.group())
    except:
        result = {"category": "RIGHTS", "confidence": "low", "reason": "unclear"}
    return result

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENT 2 — SPECIALIST AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━
def specialist_agent(user_problem, category):
    search_queries = {
        "LABOUR": ["labour act worker rights salary", "employment termination notice"],
        "CITIZENSHIP": ["citizenship certificate requirements documents", "nationality nepali"],
        "LAND": ["land registration ownership rights", "land act nepal"],
        "CONSUMER": ["consumer protection rights cheating", "fraud complaint nepal"],
        "RIGHTS": ["fundamental rights constitution nepal", "citizen rights freedom"]
    }

    queries = search_queries.get(category, ["nepal citizen rights"])
    all_chunks = []
    all_sources = []

    for query in queries:
        chunks, sources = search_laws(query)
        all_chunks.extend(chunks)
        all_sources.extend(sources)

    seen = set()
    unique_chunks = []
    for chunk in all_chunks:
        if chunk not in seen:
            seen.add(chunk)
            unique_chunks.append(chunk)

    context = "\n\n---\n\n".join(unique_chunks[:6])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are a specialist Nepal {category} law expert agent.
            Analyze the citizen's problem deeply using the provided Nepal law context.

            Respond in JSON format ONLY:
            {{
                "laws_violated": ["Labour Act Section 34", "..."],
                "case_strength": "Strong/Medium/Weak",
                "explanation": "Clear explanation in simple Nepali or English",
                "action_steps": ["Step 1...", "Step 2...", "Step 3..."],
                "office_to_visit": "Which government office to go to",
                "documents_needed": ["Document 1", "Document 2"],
                "deadline": "Any deadline to be aware of"
            }}"""},
            {"role": "user", "content": f"""
            Citizen Problem: {user_problem}
            Category: {category}
            Relevant Nepal Laws:
            {context}
            """}
        ]
    )

    try:
        content = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        result = json.loads(json_match.group())
    except:
        result = {
            "laws_violated": ["See explanation below"],
            "case_strength": "Strong",
            "explanation": response.choices[0].message.content,
            "action_steps": ["File complaint at Department of Labour"],
            "office_to_visit": "Department of Labour",
            "documents_needed": ["Employment contract", "ID"],
            "deadline": "As soon as possible"
        }

    return result, all_sources

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENT 3 — LETTER GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━
def letter_generator_agent(user_problem, analysis, user_name="[Your Name]", user_address="[ठेगाना]"):
    today = nepali_date_module.today()
    NEPALI_MONTHS = [
        "बैशाख", "जेठ", "असार", "साउन",
        "भदौ", "असोज", "कार्तिक", "मंसिर",
        "पुष", "माघ", "फागुन", "चैत"
    ]
    nepali_date = f"{today.year} {NEPALI_MONTHS[today.month - 1]} {today.day}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are an official complaint letter
            drafting agent for Nepal government offices.

            Write a formal complaint letter in Nepali language.
            Follow official Nepal government letter format.
            Include:
            - Date (use exact BS date provided)
            - Sender name and address (top left)
            - To: office name and [कार्यालयको ठेगाना] as placeholder
            - Subject line
            - Formal greeting
            - Clear description of problem
            - Laws violated
            - What action is requested
            - Formal closing with name

            IMPORTANT RULES:
            - NEVER invent company names, places, or any details
            - If company name unknown write: [कम्पनीको नाम]
            - If office address unknown write: [कार्यालयको ठेगाना]
            - If amount unknown write: [रकम]
            - Only use information explicitly given by user
            - Return ONLY the letter text, nothing else."""},
            {"role": "user", "content": f"""
            Write complaint letter for:
            Problem: {user_problem}
            Laws Violated: {analysis.get('laws_violated', [])}
            Office to send to: {analysis.get('office_to_visit', 'District Office')}
            Person name: {user_name}
            Person address: {user_address}
            Today's Nepali Date: {nepali_date}
            """}
        ]
    )
    return response.choices[0].message.content

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# PDF GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_pdf(letter_text, user_name):
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4

    # Register Nepali font
    pdfmetrics.registerFont(TTFont('Mukta', 'Mukta-Regular.ttf'))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

    c = canvas.Canvas(tmp.name, pagesize=A4)
    width, height = A4

    # Header
    c.setFont('Mukta', 16)
    c.drawCentredString(width / 2, height - 50, "SarkaarSathi - Official Complaint Letter")
    c.setFont('Mukta', 10)
    c.drawCentredString(width / 2, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Letter content
    c.setFont('Mukta', 11)
    y = height - 110
    margin = 50

    for line in letter_text.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont('Mukta', 11)
            y = height - 50
        if line.strip():
            # Handle long lines
            words = line
            c.drawString(margin, y, words)
            y -= 20
        else:
            y -= 10

    c.save()
    return tmp.name

# ━━━━━━━━━━━━━━━━━━━━━━━━━
# STREAMLIT UI
# ━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="SarkaarSathi",
    page_icon="🇳🇵",
    layout="wide"
)

st.title("🇳🇵 SarkaarSathi")
st.subheader("Nepal को AI सरकारी सहायक — Your AI Government Assistant")
st.markdown("Describe your problem and our AI agents will analyze it, find relevant laws, and generate an official complaint letter.")
st.divider()

# Example buttons
st.markdown("**Try these examples:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💰 Salary not paid"):
        st.session_state.problem = "My employer has not paid my salary for 3 months. I work at a company in Pokhara. What can I do?"
        st.rerun()
with col2:
    if st.button("🏠 Landlord kept deposit"):
        st.session_state.problem = "My landlord is not returning my house deposit of Rs 50,000 even after I vacated 2 months ago."
        st.rerun()
with col3:
    if st.button("👮 Unfair police arrest"):
        st.session_state.problem = "Police kept me in jail for 5 days without any charges or court order. What are my rights?"
        st.rerun()

st.divider()

# User inputs
if "problem" not in st.session_state:
    st.session_state.problem = ""

user_name = st.text_input("Your Name / तपाईंको नाम:", placeholder="Ram Bahadur Thapa")
user_address = st.text_input("Your Address / तपाईंको ठेगाना:", placeholder="Waling-5, Syangja, Gandaki Pradesh")
user_problem = st.text_area(
    "Describe your problem in detail (Nepali or English):",
    placeholder="Example: My employer hasn't paid my salary for 2 months...",
    height=150,
    value=st.session_state.problem
)
st.session_state.problem = user_problem

if st.button("🚀 Analyze My Problem", type="primary"):
    if not user_problem or len(user_problem.strip()) < 10:
        st.error("Please describe your problem first!")
    else:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━
        # INPUT VALIDATION AGENT
        # ━━━━━━━━━━━━━━━━━━━━━━━━━
        validation = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are an input validator for a Nepal government legal assistant.

                Classify the user input into ONE of these:
                - VALID: genuine legal, government, rights, employment, land, citizenship problem
                - EMOTIONAL: relationship, heartbreak, personal feelings, family fights
                - NONSENSE: random text, abuse, gibberish, spam
                - MEDICAL: health, sickness, hospital (not our domain)
                - OTHER: anything else not related to Nepal government/legal

                Respond ONLY in JSON:
                {
                    "type": "VALID/EMOTIONAL/NONSENSE/MEDICAL/OTHER"
                }"""},
                {"role": "user", "content": user_problem}
            ]
        )

        try:
            content = validation.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            val_result = json.loads(json_match.group())
            input_type = val_result.get("type", "VALID")
        except:
            input_type = "VALID"

        if input_type == "EMOTIONAL":
            st.warning("""
            💔 **SarkaarSathi यसमा मद्दत गर्न सक्दैन!**

            हामी सरकारी र कानूनी समस्याहरूको लागि मात्र छौं।

            Heartbreak को लागि आफ्नो साथीहरूसँग कुरा गर्नुहोस् 😅
            """)

        elif input_type == "NONSENSE":
            st.error("""
            🙏 **कृपया वास्तविक समस्या लेख्नुहोस्!**

            SarkaarSathi नेपाली नागरिकहरूको
            सरकारी र कानूनी समस्या समाधान गर्न बनाइएको हो।

            Example: "मेरो तलब ३ महिनादेखि आएको छैन"
            """)

        elif input_type == "MEDICAL":
            st.info("""
            🏥 **यो स्वास्थ्य सम्बन्धी समस्या हो!**

            SarkaarSathi कानूनी समस्याहरूको लागि मात्र हो।

            स्वास्थ्य समस्याको लागि नजिकको अस्पताल वा
            **१०४** (Health Helpline) मा सम्पर्क गर्नुहोस्।
            """)

        elif input_type == "OTHER":
            st.warning("""
            🤔 **यो SarkaarSathi को दायरामा पर्दैन!**

            हामी यी समस्याहरूमा मद्दत गर्छौं:
            - 💰 तलब सम्बन्धी समस्या
            - 🪪 नागरिकता सम्बन्धी
            - 🏠 घर/जग्गा सम्बन्धी
            - 👮 अधिकार उल्लङ्घन
            - 🛒 उपभोक्ता समस्या
            """)

        else:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            # AGENT 1 — ROUTER
            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            with st.status("🤖 Agent 1: Classifying your problem...", expanded=True) as status:
                route = router_agent(user_problem)
                st.write(f"✅ Category identified: **{route['category']}**")
                st.write(f"📝 Reason: {route['reason']}")
                status.update(label="✅ Agent 1 Done!", state="complete")

            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            # AGENT 2 — SPECIALIST
            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            with st.status("⚖️ Agent 2: Analyzing Nepal laws...", expanded=True) as status:
                analysis, sources = specialist_agent(user_problem, route['category'])
                st.write(f"✅ Laws analyzed from {len(sources)} sources")
                status.update(label="✅ Agent 2 Done!", state="complete")

            # Show Analysis
            st.divider()
            st.subheader("📊 Legal Analysis")

            col1, col2 = st.columns(2)
            with col1:
                strength = analysis.get('case_strength', 'Unknown')
                color = "🟢" if strength == "Strong" else "🟡" if strength == "Medium" else "🔴"
                st.metric("Case Strength", f"{color} {strength}")

                st.markdown("**⚖️ Laws Violated:**")
                for law in analysis.get('laws_violated', []):
                    st.write(f"• {law}")

                st.markdown("**🏢 Office to Visit:**")
                st.info(analysis.get('office_to_visit', 'District Office'))

            with col2:
                st.markdown("**📋 Action Steps:**")
                for i, step in enumerate(analysis.get('action_steps', []), 1):
                    st.write(f"{i}. {step}")

                st.markdown("**📄 Documents Needed:**")
                for doc in analysis.get('documents_needed', []):
                    st.write(f"• {doc}")

                if analysis.get('deadline'):
                    st.warning(f"⏰ Deadline: {analysis.get('deadline')}")

            st.markdown("**💡 Explanation:**")
            st.write(analysis.get('explanation', ''))

            with st.expander("📚 Sources from Nepal Laws"):
                seen = set()
                for s in sources:
                    src = f"{s['source']} — Page {s['page']}"
                    if src not in seen:
                        st.write(f"• {src}")
                        seen.add(src)

            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            # AGENT 3 — LETTER GENERATOR
            # ━━━━━━━━━━━━━━━━━━━━━━━━━
            st.divider()
            with st.status("✉️ Agent 3: Drafting complaint letter...", expanded=True) as status:
                letter = letter_generator_agent(
                    user_problem,
                    analysis,
                    user_name if user_name else "[Your Name]",
                    user_address if user_address else "[ठेगाना]"
                )
                status.update(label="✅ Agent 3 Done!", state="complete")

            st.subheader("📝 Official Complaint Letter")
            st.info("✏️ You can edit the letter below before downloading!")
            edited_letter = st.text_area(
                "Your complaint letter (edit if needed):",
                letter,
                height=400
            )

            st.markdown("**Download as PDF:**")
            pdf_path = generate_pdf(edited_letter, user_name)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Complaint Letter PDF",
                    data=f,
                    file_name=f"complaint_letter_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

            st.success("✅ SarkaarSathi has analyzed your problem and generated your complaint letter!")
            st.info("⚠️ This is AI generated guidance. For serious legal matters, consult a qualified lawyer.")