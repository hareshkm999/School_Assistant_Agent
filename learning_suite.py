# Interactive Learning Systems Suite
import time
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# =====================================================================
# SYSTEM 1: LEITNER BOX FLASHCARD SYSTEM (Spaced Repetition)
# =====================================================================
def run_leitner_system():
    # Card pool: Question, Answer
    card_pool = [
        {"q": "What is the primary function of the Feynman Technique?", "a": "To identify gaps in understanding by explaining a concept in simple terms."},
        {"q": "What curve does Spaced Repetition actively combat?", "a": "The Ebbinghaus Forgetting Curve."},
        {"q": "What is the core practice of Interleaving?", "a": "Mixing different topics or problem types within a single study session."},
        {"q": "How does Active Recall differ from Passive Review?", "a": "It forces the brain to retrieve information from memory rather than recognizing it from an outside source."}
    ]
    
    # 3 Boxes: Box 1 (Every day), Box 2 (Every 3 days), Box 3 (Every 5 days)
    boxes = {1: card_pool.copy(), 2: [], 3: []}
    
    while True:
        clear_screen()
        print("==================================================")
        print("    SYSTEM 1: LEITNER BOX FLASHCARD SIMULATOR     ")
        print("==================================================")
        print(f"📦 Box 1 (Review Daily): {len(boxes[1])} cards")
        print(f"📦 Box 2 (Review 3 Days): {len(boxes[2])} cards")
        print(f"📦 Box 3 (Review 5 Days): {len(boxes[3])} cards")
        print("--------------------------------------------------")
        
        if not boxes[1] and not boxes[2] and not boxes[3]:
            print("🏆 Mastered! All flashcards are completely cleared.")
            input("\nPress Enter to return to main menu...")
            break
            
        print("Which box would you like to review?")
        print("1. Review Box 1")
        print("2. Review Box 2")
        print("3. Review Box 3")
        print("4. Return to Main Menu")
        
        choice = input("\nSelect an option (1-4): ").strip()
        if choice == '4':
            break
        if choice not in ['1', '2', '3']:
            print("Invalid selection!")
            time.sleep(1)
            continue
            
        box_num = int(choice)
        current_box = boxes[box_num]
        
        if not current_box:
            print(f"\nBox {box_num} is currently empty!")
            time.sleep(1)
            continue
            
        print(f"\nStarting review of Box {box_num}... ({len(current_box)} items)")
        time.sleep(1)
        
        # Iterate over a copy to safely mutate boxes during loops
        for card in list(current_box):
            clear_screen()
            print(f"--- Box {box_num} Review ---")
            print(f"📝 CARD QUESTION:\n{card['q']}\n")
            input("Press Enter when ready to see the answer...")
            print(f"\n💡 CORRECT ANSWER:\n{card['a']}\n")
            
            while True:
                response = input("Did you get it right? (Y/N): ").strip().upper()
                if response in ['Y', 'N']:
                    break
                print("Please enter Y or N.")
            
            if response == 'Y':
                current_box.remove(card)
                next_box = min(box_num + 1, 3)
                boxes[next_box].append(card)
                print(f"✨ Success! Card promoted to Box {next_box}.")
            else:
                current_box.remove(card)
                boxes[1].append(card)
                print("❌ Incorrect. Card demoted back to Box 1.")
            time.sleep(1.5)

# =====================================================================
# SYSTEM 2: INTERLEAVED DRILL APP (Context Switching)
# =====================================================================
def run_interleaved_drill():
    # Problems across entirely separate domains
    pool = [
        {"cat": "Python Programming", "q": "What is the output of print(2 ** 3)?", "a": "8"},
        {"cat": "Data Science Math", "q": "What is the median of the dataset: [1, 3, 3, 6, 7, 8, 9]?", "a": "6"},
        {"cat": "Python Programming", "q": "Which keyword is used to define a function in Python?", "a": "def"},
        {"cat": "Data Science Math", "q": "What is the derivative of a constant value?", "a": "0"},
        {"cat": "Study Mechanics", "q": "Which technique relies on structured visual mapping?", "a": "Mind Mapping"}
    ]
    
    random.shuffle(pool)
    score = 0
    
    clear_screen()
    print("==================================================")
    print("      SYSTEM 2: INTERLEAVED PRACTICE DRILL        ")
    print("==================================================")
    print("This mode forces your brain to rapidly switch gears")
    print("between different subjects to prevent muscle memory.")
    print("--------------------------------------------------")
    input("Press Enter to begin the drill...")
    
    for i, problem in enumerate(pool, 1):
        clear_screen()
        print(f"⏱️ Context Switch #{i} | Current Topic: [{problem['cat']}]")
        print("--------------------------------------------------")
        print(f"PROBLEM: {problem['q']}")
        
        user_ans = input("Your Answer: ").strip()
        
        if user_ans.lower() == problem['a'].lower():
            print("✅ Correct! Excellent cognitive flexibility.")
            score += 10
        else:
            print(f"❌ Incorrect. The correct answer is: {problem['a']}")
        print(f"Running Score: {score} Points")
        time.sleep(2.5)
        
    clear_screen()
    print("==================================================")
    print("                DRILL COMPLETE                    ")
    print("==================================================")
    print(f"Total Cognitive Score: {score} / {len(pool)*10} Points")
    input("\nPress Enter to return to main menu...")

# =====================================================================
# SYSTEM 3: ACTIVE RECALL BLURTING WORKSPACE
# =====================================================================
def run_blurting_workspace():
    clear_screen()
    print("==================================================")
    print("       SYSTEM 3: ACTIVE RECALL BLURTING APP       ")
    print("==================================================")
    print("1. Review the text summary provided below for 20 sec.")
    print("2. The text will disappear.")
    print("3. You will have to 'blurt' out everything you recall.")
    print("==================================================")
    input("\nPress Enter to view the source text...")
    
    clear_screen()
    source_text = (
        "The Feynman Technique features four primary components:\n"
        "1. Select a concept to study deeply.\n"
        "2. Explain it to a completely non-technical toddler.\n"
        "3. Identify points of friction where explanation breaks.\n"
        "4. Review reference text to fill technical gaps."
    )
    print("--- 📖 STUDY THIS CAREFULLY (Countdown Starting) ---")
    print(source_text)
    print("----------------------------------------------------")
    
    for remaining in range(20, 0, -1):
        print(f"\rTime remaining to memorize: {remaining} seconds... ", end="", flush=True)
        time.sleep(1)
        
    clear_screen()
    print("==================================================")
    print("               🚨 TIME IS UP! 🚨                  ")
    print("==================================================")
    print("Type out everything you can remember from the text.")
    print("Do not look back at notes. Hit Enter when finished.\n")
    
    user_blurt = input("✏️ YOUR RECALL:\n> ")
    
    clear_screen()
    print("==================================================")
    print("             COMPARE AND EVALUATE                 ")
    print("==================================================")
    print("🔴 ORIGINAL MATERIAL:")
    print(source_text)
    print("\n🔵 YOUR ACTIVE RECALL OUTPUT:")
    print(user_blurt)
    print("--------------------------------------------------")
    print("INSTRUCTIONS FOR SELF-GRADING:")
    print("Take a red pen mentally. Identify items you completely missed,")
    print("or areas where your memory created false details.")
    input("\nPress Enter to return to main menu...")

# =====================================================================
# CORE PROGRAM CONTROLLER
# =====================================================================
def main_menu():
    while True:
        clear_screen()
        print("==================================================")
        print("       ADVANCED SCIENTIFIC LEARNING SUITE        ")
        print("==================================================")
        print("Select a learning engine framework to execute:")
        print("1. Spaced Repetition (Leitner Box Flashcards)")
        print("2. Context Flexibility (Interleaved Practice Drill)")
        print("3. Cognitive Retrieval (Active Recall Blurting)")
        print("4. Exit Application")
        print("==================================================")
        
        choice = input("Enter execution number (1-4): ").strip()
        if choice == '1':
            run_leitner_system()
        elif choice == '2':
            run_interleaved_drill()
        elif choice == '3':
            run_blurting_workspace()
        elif choice == '4':
            print("\nExiting Cognitive Suite. Keep learning!")
            break
        else:
            print("Invalid input choice!")
            time.sleep(1)

if __name__ == '__main__':
    main_menu()
