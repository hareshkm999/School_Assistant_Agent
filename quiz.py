import time

def run_quiz():
    # Define the quiz questions, options, correct answers, and points
    questions = [
        {
            "question": "What is the capital city of Australia?",
            "options": ["A) Sydney", "B) Melbourne", "C) Canberra", "D) Brisbane"],
            "answer": "C",
            "points": 10
        },
        {
            "question": "Which gas makes up the majority of Earth's atmosphere?",
            "options": ["A) Oxygen", "B) Nitrogen", "C) Carbon Dioxide", "D) Argon"],
            "answer": "B",
            "points": 10
        },
        {
            "question": "Which planet in our solar system has the most confirmed moons?",
            "options": ["A) Jupiter", "B) Saturn", "C) Uranus", "D) Neptune"],
            "answer": "B",
            "points": 15
        },
        {
            "question": "In what year did the Berlin Wall fall?",
            "options": ["A) 1985", "B) 1987", "C) 1989", "D) 1991"],
            "answer": "C",
            "points": 15
        }
    ]

    score = 0
    max_possible_score = sum(q["points"] for q in questions)

    print("=========================================")
    print("      WELCOME TO THE PYTHON QUIZ!        ")
    print("=========================================")
    print(f"Total Questions: {len(questions)}")
    print(f"Max Possible Points: {max_possible_score}\n")
    time.sleep(1)

    for i, q in enumerate(questions, 1):
        print(f"--- Question {i} ({q['points']} Points) ---")
        print(q["question"])
        for option in q["options"]:
            print(option)
        
        # Get user input and validate it
        while True:
            user_answer = input("Your answer (A, B, C, or D): ").strip().upper()
            if user_answer in ["A", "B", "C", "D"]:
                break
            print("Invalid input! Please choose A, B, C, or D.")

        # Check if the answer is correct
        if user_answer == q["answer"]:
            print("✨ Correct!")
            score += q["points"]
        else:
            print(f"❌ Incorrect. The correct answer was {q['answer']}.")
        
        # Display current points live
        print(f"Current Score: {score} points\n")
        time.sleep(0.5)

    # Final Score Display
    print("=========================================")
    print("               GAME OVER                 ")
    print("=========================================")
    print(f"Your Final Score: {score} / {max_possible_score} points")
    
    percentage = (score / max_possible_score) * 100
    print(f"Success Rate: {percentage:.1f}%")
    
    if percentage == 100:
        print("🏆 Perfect score! You are a genius!")
    elif percentage >= 70:
        print("👍 Great job! You know your stuff.")
    else:
        print("📚 Better luck next time! Keep learning.")
    print("=========================================")

# Run the game
if __name__ == "__main__":
    run_quiz()
