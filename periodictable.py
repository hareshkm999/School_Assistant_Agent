import random
import time

# Dictionary containing the first 20 elements with their symbols and atomic numbers
PERIODIC_TABLE = {
    1: {"name": "Hydrogen", "symbol": "H"},
    2: {"name": "Helium", "symbol": "He"},
    3: {"name": "Lithium", "symbol": "Li"},
    4: {"name": "Beryllium", "symbol": "Be"},
    5: {"name": "Boron", "symbol": "B"},
    6: {"name": "Carbon", "symbol": "C"},
    7: {"name": "Nitrogen", "symbol": "N"},
    8: {"name": "Oxygen", "symbol": "O"},
    9: {"name": "Fluorine", "symbol": "F"},
    10: {"name": "Neon", "symbol": "Ne"},
    11: {"name": "Sodium", "symbol": "Na"},
    12: {"name": "Magnesium", "symbol": "Mg"},
    13: {"name": "Aluminium", "symbol": "Al"},
    14: {"name": "Silicon", "symbol": "Si"},
    15: {"name": "Phosphorus", "symbol": "P"},
    16: {"name": "Sulfur", "symbol": "S"},
    17: {"name": "Chlorine", "symbol": "Cl"},
    18: {"name": "Argon", "symbol": "Ar"},
    19: {"name": "Potassium", "symbol": "K"},
    20: {"name": "Calcium", "symbol": "Ca"}
}

def clear_screen():
    print("\n" * 20)

def get_periodic_hint(atomic_num, element_info, question_type):
    """Provides a structural mnemonic or positional hint based on the element."""
    name = element_info["name"]
    sym = element_info["symbol"]
    
    if question_type == "symbol":
        return f"💡 Hint: The name of this element is '{name}'."
    elif question_type == "name":
        return f"💡 Hint: The chemical symbol for this element is '{sym}'."
    else:
        # Give positional hints on the periodic table grid
        if atomic_num <= 2:
            period = 1
        elif atomic_num <= 10:
            period = 2
        else:
            period = 3
        return f"💡 Hint: This element is '{name}' ({sym}) and sits in Period {period}."

def run_periodic_game():
    clear_screen()
    print("=========================================")
    print("🧪 WELCOME TO THE PERIODIC TABLE MASTER! 🧪")
    print("=========================================")
    print("Master the first 20 elements through interactive active recall.\n")
    
    print("Choose your testing focus:")
    print("1. Guess the Chemical Symbol")
    print("2. Guess the Element Name")
    print("3. Guess the Atomic Number")
    print("4. Mixed Challenge (All of the above)")
    
    while True:
        choice = input("Enter mode (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break
        print("❌ Invalid selection. Choose a number between 1 and 4.")
        
    clear_screen()
    print("🎯 Game Mode Locked! Type 'exit' to finish or 'hint' if you get stuck.")
    print("⚠️ Note: Spelling and capitalisation matter for symbols (e.g., Na, not na)!\n")
    
    score = 0
    total_q = 0
    
    # Extract atomic numbers to sample questions randomly
    atomic_numbers = list(PERIODIC_TABLE.keys())
    
    while True:
        atomic_num = random.choice(atomic_numbers)
        element = PERIODIC_TABLE[atomic_num]
        
        # Determine question type based on user mode choice
        if choice == '1':
            q_type = "symbol"
        elif choice == '2':
            q_type = "name"
        elif choice == '3':
            q_type = "number"
        else:
            q_type = random.choice(["symbol", "name", "number"])
            
        # Formulate questions and answers dynamically
        if q_type == "symbol":
            question_text = f"What is the chemical SYMBOL for the element '{element['name']}' (Atomic Number {atomic_num})?"
            correct_ans = element["symbol"]
        elif q_type == "name":
            question_text = f"What is the full NAME of the element with the symbol '{element['symbol']}' (Atomic Number {atomic_num})?"
            correct_ans = element["name"]
        else:
            question_text = f"What is the ATOMIC NUMBER of the element '{element['name']}' (Symbol: {element['symbol']})?"
            correct_ans = str(atomic_num)
            
        print(f"✨ Question {total_q + 1}: {question_text}")
        
        while True:
            user_input = input("Your answer: ").strip()
            
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'hint':
                print(get_periodic_hint(atomic_num, element, q_type))
                continue
            break
            
        if user_input.lower() == 'exit':
            break
            
        total_q += 1
        
        # Validation checks (case-insensitive for names, case-sensitive for symbols)
        is_correct = False
        if q_type == "name" and user_input.lower() == correct_ans.lower():
            is_correct = True
        elif q_type == "symbol" and user_input == correct_ans:
            is_correct = True
        elif q_type == "number" and user_input == correct_ans:
            is_correct = True
            
        if is_correct:
            score += 10
            print("🎉 Correct! Outstanding chemistry knowledge!")
            print("-----------------------------------------")
        else:
            print(f"❌ Not quite. The correct answer was: {correct_ans}")
            print(f"💡 Fact Sheet: Atomic No. {atomic_num} | Element: {element['name']} | Symbol: {element['symbol']}")
            print("-----------------------------------------")
            
        time.sleep(1.5)
        
    # Final Results Screen Summary
    clear_screen()
    print("=========================================")
    print("🧪 SESSION COMPLETE! HERE ARE YOUR STATS: 🧪")
    print("=========================================")
    print(f"📋 Total Questions Faced: {total_q}")
    if total_q > 0:
        print(f"📋 Final Score: {score} points ({score // 10}/{total_q} correct)")
    print("=========================================")
    print("Keep playing to build bulletproof science recall! 🚀\n")

if __name__ == "__main__":
    run_periodic_game()
