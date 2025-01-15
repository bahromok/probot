import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Load the bot token from environment variable
TOKEN = "7543559673:AAE_ad73rESmhxARRddnuWzTBLhGsL2dTjg"

# Directory for storing user-specific task files
TASKS_DIR = "user_tasks/"

# Ensure the tasks directory exists
if not os.path.exists(TASKS_DIR):
    os.makedirs(TASKS_DIR)

# Function to get a random quote from ZenQuotes API
def get_quote():
    url = "https://zenquotes.io/api/random"
    response = requests.get(url)
    data = response.json()
    return f"{data[0]['q']} — {data[0]['a']}"

# Function to load tasks from a user's task file
def load_tasks(user_id):
    task_file = f"{TASKS_DIR}{user_id}_tasks.json"
    if os.path.exists(task_file):
        with open(task_file, "r") as file:
            return json.load(file)
    return []

# Function to save tasks to a user's task file
def save_tasks(user_id, tasks):
    task_file = f"{TASKS_DIR}{user_id}_tasks.json"
    with open(task_file, "w") as file:
        json.dump(tasks, file)

# Start command with reply keyboard buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Get Quote'], ['Tasks'], ['Help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Welcome! Choose an option from the buttons below:",
        reply_markup=reply_markup
    )

# Handle button presses for "Get Quote", "Tasks", and "Help"
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Load user-specific tasks
    user_id = str(update.message.from_user.id)
    tasks = load_tasks(user_id)

    if text == "Get Quote":
        await update.message.reply_text(get_quote())
    elif text == "Tasks":
        if tasks:
            task_list = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
            await update.message.reply_text(f"Here are your tasks:\n{task_list}\n\nUse '/deletetask [task_number]' to delete a task.")
        else:
            await update.message.reply_text("You have no tasks. Use '/addtask [task]' to add one.")
    elif text == "Help":
        await update.message.reply_text(
            "Available options:\n"
            "- 'Get Quote' for a motivational quote\n"
            "- 'Tasks' to view and manage your tasks\n"
            "- Use /start to see the menu again\n"
            "- Use '/deletetask [task_number]' to delete a task"
        )
    else:
        await update.message.reply_text("Please choose a valid option.")

# Add a new task
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_text = " ".join(context.args)
    user_id = str(update.message.from_user.id)
    
    if task_text:
        tasks = load_tasks(user_id)
        tasks.append(task_text)
        save_tasks(user_id, tasks)  # Save tasks after adding
        await update.message.reply_text(f"Task added: {task_text}")
    else:
        await update.message.reply_text("Please provide a task description. Use '/addtask [task]'.")

# Delete a task
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    tasks = load_tasks(user_id)
    
    try:
        task_index = int(context.args[0]) - 1  # Convert to 0-based index
        
        if 0 <= task_index < len(tasks):
            deleted_task = tasks.pop(task_index)
            save_tasks(user_id, tasks)  # Save tasks after deletion
            await update.message.reply_text(f"Task deleted: {deleted_task}")
        else:
            await update.message.reply_text("Invalid task number.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid task number. Use '/deletetask [task_number]'.")

# Main function to run the bot
def main():
    # Ensure the bot token is set
    if TOKEN is None:
        print("Error: Bot token not found.")
        return

    # Use the bot API token securely
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("deletetask", delete_task))

    # Message handler for button responses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
