import json
import os
import random
import hashlib


# AI

try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

GEMINI_API_KEY = "ВСТАВЬ_СЮДА_СВОЙ_НОВЫЙ_КЛЮЧ"

def get_ai_explanation(question_text, student_answer, correct_answer):
    if not AI_AVAILABLE or len(GEMINI_API_KEY) < 20:
        return None
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Act as a friendly high school teacher.
        Question: {question_text}
        Student's incorrect answer: {student_answer}
        Correct answer: {correct_answer}
        Explain briefly (1-2 sentences) why their answer is wrong and why the correct answer is right.
        Make sure the explanation is accurate for the context of the question (Math or History).
        Return ONLY plain text. No markdown, no bold words.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"\n[AI TUTOR ERROR]: {e}")
        return None

def generate_ai_question(subject):
    if not AI_AVAILABLE or len(GEMINI_API_KEY) < 20:
        return None
        
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Generate 1 high-school level multiple-choice question for the subject: {subject}. 
        Return ONLY a raw JSON object. Do NOT use markdown code blocks (like ```json).
        Format:
        {{
            "text": "The question text",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "answer": "The exact correct option",
            "explanation": "A short 1-sentence explanation of the answer."
        }}
        """
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"\n[AI GENERATION ERROR]: {e}")
        return None


# UTILITIES & FILE HANDLING


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

DB_USERS = "users.json"
DB_QUESTIONS = "questions.json"

DEFAULT_QUESTIONS = {
    "Math": [
        {"text": "What is 2 + 2 * 2?", "options": ["4", "6", "8", "10"], "answer": "6", "explanation": "PEMDAS rule: multiplication before addition. 2*2=4, then 2+4=6."},
        {"text": "Find x if 3x = 27", "options": ["7", "8", "9", "10"], "answer": "9", "explanation": "Divide both sides by 3. 27 / 3 = 9."}
    ],
    "History of Kazakhstan": [
        {"text": "In what year was the Kazakh Khanate established?", "options": ["1455", "1465", "1475", "1485"], "answer": "1465", "explanation": "It was founded in 1465 by Zhanibek and Kerey Khans in the Zhetysu region."},
        {"text": "Who was the founder of the Golden Horde?", "options": ["Genghis Khan", "Batu Khan", "Jochi", "Berke Khan"], "answer": "Batu Khan", "explanation": "Batu Khan, the grandson of Genghis Khan, founded the Golden Horde after his western campaigns."}
    ]
}

def load_questions():
    if not os.path.exists(DB_QUESTIONS):
        with open(DB_QUESTIONS, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_QUESTIONS, f, indent=4, ensure_ascii=False)
        return DEFAULT_QUESTIONS
    try:
        with open(DB_QUESTIONS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_QUESTIONS

def save_questions(questions_data):
    with open(DB_QUESTIONS, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, indent=4, ensure_ascii=False)

questions_db = load_questions()


# USER CLASSES (OOP)

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return self.__dict__

class Student(User):
    def __init__(self, username, password, subscription="Basic", scores=None):
        super().__init__(username, password, role="Student")
        self.subscription = subscription
        self.scores = scores if scores else {}

    def show_profile(self):
        clear_screen()
        print(f"--- Student Profile ---")
        print(f"Name: {self.username}")
        print(f"Subscription Tier: {self.subscription}")
        print("Academic Progress:")
        if not self.scores:
            print("  No tests taken yet.")
        else:
            for k, v in self.scores.items():
                print(f"  - {k}: {v} points/tests")
        print("-----------------------\n")
        input("Press Enter to continue...")

    def upgrade_subscription(self):
        clear_screen()
        if self.subscription == "Premium":
            print("[!] You already have a Premium subscription!")
        else:
            self.subscription = "Premium"
            print("*** Payment Successful! ***")
            print("*** You unlocked INFINITE AI GENERATED TESTS! ***")
        input("\nPress Enter to continue...")

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, role="Admin")

    def view_all_students(self, users_list):
        clear_screen()
        print("--- System Database: Registered Students ---")
        students = [u for u in users_list if u.role == "Student"]
        if not students:
            print("No students found.")
        else:
            for i, s in enumerate(students, 1):
                print(f"{i}. {s.username} | Tier: {s.subscription} | Scores: {s.scores}")
        input("\nPress Enter to return...")

    def add_question(self):
        clear_screen()
        print("--- Add New Static Question ---")
        print("1. Math")
        print("2. History of Kazakhstan")
        subj_choice = input("Select subject (1-2): ")
        subject = "Math" if subj_choice == '1' else "History of Kazakhstan"
        
        text = input(f"Enter the new {subject} question text: ")

        options = []
        for i in range(4):
            options.append(input(f"Enter option {i + 1}: "))

        answer = input("Enter the CORRECT option exactly as typed above: ")
        if answer not in options:
            print("Error: The answer must match one of the options.")
            input("Press Enter to return...")
            return

        explanation = input("Enter the explanation: ")
        if subject not in questions_db:
            questions_db[subject] = []

        questions_db[subject].append({"text": text, "options": options, "answer": answer, "explanation": explanation})
        save_questions(questions_db)
        print(f"\nSuccess! Question added to {subject} database.")
        input("Press Enter to continue...")

def save_users(users_list):
    with open(DB_USERS, "w", encoding="utf-8") as f:
        json.dump([user.to_dict() for user in users_list], f, indent=4, ensure_ascii=False)

def load_users():
    if not os.path.exists(DB_USERS): return []
    try:
        with open(DB_USERS, "r", encoding="utf-8") as f:
            data = json.load(f)
            users = []
            for item in data:
                if item['role'] == "Student":
                    users.append(Student(item['username'], item['password'], item.get('subscription', 'Basic'),
                                         item.get('scores', {})))
                elif item['role'] == "Admin":
                    users.append(Admin(item['username'], item['password']))
            return users
    except:
        return []

users_db = load_users()


# EXAM ENGINES


def execute_question_ui(q_data, use_ai_tutor=False):
    print(f"\nQuestion: {q_data['text']}")
    options = q_data['options'].copy()
    random.shuffle(options)

    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")

    try:
        choice = int(input("\nYour answer (number): "))
        selected = options[choice - 1]

        if selected == q_data['answer']:
            print("\n✅ Correct! Great job.")
            return True
        else:
            print(f"\n❌ Incorrect. The correct answer was: {q_data['answer']}")
            print("-" * 50)
            if use_ai_tutor:
                print("Thinking... 🤔")
                ai_exp = get_ai_explanation(q_data['text'], selected, q_data['answer'])
                if ai_exp:
                    print("🤖 AI TUTOR SAYS:")
                    print(ai_exp)
                else:
                    print("💡 STATIC EXPLANATION:\n" + q_data.get('explanation', 'No explanation provided.'))
            else:
                print("💡 EXPLANATION:\n" + q_data.get('explanation', 'No explanation provided.'))
            print("-" * 50)
            return False
    except (ValueError, IndexError):
        print("\n⚠️ Invalid input! Answer not counted.")
        return False

def take_static_test(student, subject):
    clear_screen()
    questions = questions_db.get(subject, [])
    if not questions:
        print(f"No static questions available for {subject}.")
        input("Press Enter to return...")
        return

    print(f"=== Static Test: {subject} ===")
    test_q = random.choice(questions)

    if execute_question_ui(test_q, use_ai_tutor=True):
        student.scores[f"{subject}_Static_Best"] = student.scores.get(f"{subject}_Static_Best", 0) + 1
        save_users(users_db)

    input("\nPress Enter to return to Dashboard...")

def take_ai_infinite_test(student, subject):
    clear_screen()
    if student.subscription != "Premium":
        print("🔒 ACCESS DENIED: Premium Feature.")
        print(f"Please upgrade to Premium to unlock Infinite AI {subject} Tests.")
        input("\nPress Enter to return...")
        return

    print(f"🤖 Generating a unique {subject} question via AI...")
    print("Please wait a few seconds...")
    q = generate_ai_question(subject)

    if not q:
        print("\n⚠️ Failed to connect to AI (Check API Key or Internet).")
        input("Press Enter to return...")
        return

    clear_screen()
    print(f"=== 🧠 AI Infinite Exam: {subject} ===")

    execute_question_ui(q, use_ai_tutor=False)

    student.scores[f'AI_{subject}_Tests_Taken'] = student.scores.get(f'AI_{subject}_Tests_Taken', 0) + 1
    save_users(users_db)
    input("\nPress Enter to return to Dashboard...")


# DASHBOARDS & MAIN MENU


def student_dashboard(student):
    while True:
        clear_screen()
        print(f"=== Dashboard: {student.username} | Tier: {student.subscription} ===")
        print("1. 👤 My Profile")
        print("2. 📚 Take Static Math Test (Free)")
        print("3. 📚 Take Static History of Kazakhstan Test (Free)")
        print("4. 🤖 Take Infinite AI Math Test (Premium)")
        print("5. 🤖 Take Infinite AI History of Kazakhstan Test (Premium)")
        print("6. 💎 Upgrade to Premium")
        print("7. 🚪 Log Out")

        choice = input("Select an option: ")
        if choice == '1':
            student.show_profile()
        elif choice == '2':
            take_static_test(student, "Math")
        elif choice == '3':
            take_static_test(student, "History of Kazakhstan")
        elif choice == '4':
            take_ai_infinite_test(student, "Math")
        elif choice == '5':
            take_ai_infinite_test(student, "History of Kazakhstan")
        elif choice == '6':
            student.upgrade_subscription()
            save_users(users_db)
        elif choice == '7':
            break

def admin_dashboard(admin):
    while True:
        clear_screen()
        print(f"=== Admin Control Panel: {admin.username} ===")
        print("1. View All Students Data")
        print("2. Add New Static Question")
        print("3. Log Out")

        choice = input("Select an option: ")
        if choice == '1':
            admin.view_all_students(users_db)
        elif choice == '2':
            admin.add_question()
        elif choice == '3':
            break

def register():
    clear_screen()
    print("--- Registration ---")
    username = input("Create a username: ")
    if any(user.username == username for user in users_db):
        print("Error: Username is already taken!")
        input("\nPress Enter to continue...")
        return
    password = input("Create a password: ")
    new_student = Student(username, hash_password(password))
    users_db.append(new_student)
    save_users(users_db)
    print(f"Success! Account '{username}' created.")
    input("\nPress Enter to continue...")

def login():
    clear_screen()
    print("--- Login ---")
    username = input("Username: ")
    password = input("Password: ")
    hashed_pass = hash_password(password)

    for user in users_db:
        if user.username == username and user.password == hashed_pass:
            return user
    print("Error: Invalid credentials!")
    input("\nPress Enter to try again...")
    return None

def main_menu():
    while True:
        clear_screen()
        print("=== 🎓 UBT Hero ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            register()
        elif choice == '2':
            logged_user = login()
            if logged_user:
                if isinstance(logged_user, Student):
                    student_dashboard(logged_user)
                elif isinstance(logged_user, Admin):
                    admin_dashboard(logged_user)
        elif choice == '3':
            clear_screen()
            print("Goodbye! Good luck with your exams!")
            break

if __name__ == "__main__":
    if not any(isinstance(user, Admin) for user in users_db):
        users_db.append(Admin("admin", hash_password("admin123")))
        save_users(users_db)
    main_menu()
