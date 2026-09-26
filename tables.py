import random
import time

def clear_screen():
    # Prints spaces to clear the console interface for a clean look
    print("\n" * 20)

def get_hint(num1, num2):
    """Generates an intuitive, tactile hint for kids based on the problem."""
    hint_type = random.choice([1, 2])
    if hint_type == 1:
        # Array representation
        return f"💡 Hint: Think of it as {num1} rows with {num2} items in each row!"
    else:
        # Repeated addition representation
        addition_str = " + ".join([str(num2)] * num1)
        return f"💡 Hint: Try adding the number {num2} together {num1} times: {addition_str}"

def run_math_game():
    clear_screen()
    print("=========================================")
    print("🌟 WELCOME TO THE SUPER MULTIPLICATION GAME! 🌟")
    print("=========================================")
    print("Let's practice your times tables and build a high score!\n")
    
    # Configure difficulty parameters
    print("Choose your level:")
    print("1. Easy   (Tables 1 to 5)")
    print("2. Medium (Tables 1 to 10)")
    print("3. Hard   (Tables 6 to 12)")
    
    while True:
        choice = input("Enter level number (1, 2, or 3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ Invalid choice. Please enter 1, 2, or 3.")
        
    if choice == '1':
        min_val, max_val = 1, 5
    elif choice == '2':
        min_val, max_val = 1, 10
    else:
        min_val, max_val = 6, 12
        
    clear_screen()
    print("🎯 Game Started! Type 'exit' at any time to finish and see your final score.")
    print("🎯 Type 'hint' if you get stuck on a tough problem.\n")
    
    score = 0
    streak = 0
    total_questions = 0
    
    while True:
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(1, 10) # Keeps second number within common limits
        correct_answer = num1 * num2
        
        print(f"✨ Question {total_questions + 1}: What is {num1} × {num2}? ✨")
        if streak >= 3:
            print(f"🔥 On fire! Current Streak: {streak}")
            
        start_time = time.time()
        asked_for_hint = False
        
        while True:
            user_input = input("Your answer: ").strip().lower()
            
            if user_input == 'exit':
                break
            
            if user_input == 'hint':
                print(get_hint(num1, num2))
                asked_for_hint = True
                continue
                
            try:
                user_answer = int(user_input)
                break
            except ValueError:
                print("❌ Please type a number, 'hint', or 'exit'.")
                
        if user_input == 'exit':
            break
            
        total_questions += 1
        elapsed_time = round(time.time() - start_time, 1)
        
        if user_answer == correct_answer:
            score += 10
            streak += 1
            print(f"🎉 Correct! Fantastic job! (Solved in {elapsed_time} seconds)")
            if not asked_for_hint and elapsed_time < 4:
                print("⚡ Lightning Fast Bonus! +5 extra points!")
                score += 5
            print("-----------------------------------------")
        else:
            streak = 0 # Reset streak on incorrect answer
            print(f"❌ Not quite! The correct answer was {correct_answer}.")
            print(f"Constructive tip: {num1} groups of {num2} make exactly {correct_answer}.")
            print("-----------------------------------------")
            
        # Give a small pause so the child can read the validation message
        time.sleep(1.5)

    # Final Summary Screen
    clear_screen()
    print("=========================================")
    print("🎮 GAME OVER! HERE ARE YOUR RESULTS: 🎮")
    print("=========================================")
    print(f"⭐ Total Questions Attempted: {total_questions}")
    if total_questions > 0:
        accuracy = round((score / (total_questions * 15 if choice=='1' else total_questions * 10)) * 100, 1)
        print(f"⭐ Final Score: {score} points")
    else:
        print("⭐ No questions completed this session.")
    print("=========================================")
    print("Keep practicing and you'll be a math master in no time! 🚀\n")

if __name__ == "__main__":
    run_math_game()
