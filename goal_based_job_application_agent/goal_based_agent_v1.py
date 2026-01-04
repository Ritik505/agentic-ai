from dotenv import load_dotenv
import os
import re

load_dotenv()





# Lightweight CLI fallback (no external LLM or LangChain required)
memory = None


application_info = {
    "name": None,
    "email": None,
    "skills": None
}




def extract_application_info(text: str) -> str: 
    name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE) 
    email_match = re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", text)  
    skills_match = re.search(r"(?:skills are|i know|i can use)\s+(.+)", text, re.IGNORECASE) 

    response = [] 

    if name_match: 
        application_info["name"] = name_match.group(1).title()
        response.append("✅ Name saved.") 


    if email_match:
        application_info["email"] = email_match.group(0)
        response.append("✅ Email saved.")
    if skills_match:
        application_info["skills"] = skills_match.group(1).strip()
        response.append("✅ Skills saved.")

    if not any([name_match, email_match, skills_match]):
        return "❓ I couldn't extract any info. Could you please provide your name, email, or skills?"

    return " ".join(response) + " Let me check what else I need."



def check_application_goal(_: str) -> str:
    if all(application_info.values()):
        return f"✅ You're ready! Name: {application_info['name']}, Email: {application_info['email']}, Skills: {application_info['skills']}."
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still need: {', '.join(missing)}. Please ask the user to provide this."




print("📝 Hi! I'm your job application assistant. Please tell me your name, email, and skills.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Bye! Good luck.")
        break

    # Use local extractor and checker
    bot_reply = extract_application_info(user_input)
    print("Bot:", bot_reply)

    goal_status = check_application_goal("check")
    print("Status:", goal_status)

    if "you're ready" in goal_status.lower():
        print("🎉 Application info complete!")
        break
