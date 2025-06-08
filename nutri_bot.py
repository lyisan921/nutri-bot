from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

GENDER, AGE, WEIGHT, HEIGHT, ACTIVITY, GOAL = range(6)
TEST_START, TEST_Q1, TEST_Q2, TEST_Q3, TEST_Q4, TEST_Q5, TEST_Q6, TEST_Q7, TEST_Q8, TEST_Q9, TEST_Q10 = range(6, 17)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔢 Рассчитать калории")],
        [KeyboardButton("🧠 Пройти тест на личное ведение")]
    ]
    await update.message.reply_text(
        "Привет! Я помогу тебе рассчитать норму калорий и понять, подойдёт ли тебе личное ведение с нутрициологом 😊\n\n"
        "Выбери опцию снизу.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return GENDER

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "калории" in text:
        keyboard = [["м", "ж"]]
        await update.message.reply_text(
            "Выбери пол:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return GENDER
    elif "тест" in text:
        keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Хочешь пройти мини-тест на личное ведение?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return TEST_START
    else:
        keyboard = [
            [KeyboardButton("🔢 Рассчитать калории")],
            [KeyboardButton("🧠 Пройти тест на личное ведение")]
        ]
        await update.message.reply_text(
            "Пожалуйста, выбери один из вариантов:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text not in ("м", "ж"):
        keyboard = [["м", "ж"]]
        await update.message.reply_text(
            "Пожалуйста, выбери пол с помощью кнопок:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return GENDER
    user_data['gender'] = text
    await update.message.reply_text("Укажи возраст (целое число):", reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        if age < 10 or age > 120:
            raise ValueError
        user_data['age'] = age
    except:
        await update.message.reply_text("Пожалуйста, введи корректный возраст (например, 30):")
        return AGE

    await update.message.reply_text("Вес (кг):")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text.replace(',', '.'))
        if weight <= 0 or weight > 500:
            raise ValueError
        user_data['weight'] = weight
    except:
        await update.message.reply_text("Пожалуйста, введи корректный вес (например, 65):")
        return WEIGHT

    await update.message.reply_text("Рост (см):")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = float(update.message.text.replace(',', '.'))
        if height <= 50 or height > 300:
            raise ValueError
        user_data['height'] = height
    except:
        await update.message.reply_text("Пожалуйста, введи корректный рост (например, 170):")
        return HEIGHT

    keyboard = [["низкий", "средний", "высокий"]]
    await update.message.reply_text(
        "Уровень активности:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    level = update.message.text.lower()
    factor = {"низкий": 1.2, "средний": 1.55, "высокий": 1.9}.get(level)
    if not factor:
        keyboard = [["низкий", "средний", "высокий"]]
        await update.message.reply_text(
            "Пожалуйста, выбери уровень активности из вариантов:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return ACTIVITY
    user_data['activity_factor'] = factor
    keyboard = [["похудение", "поддержание", "набор"]]
    await update.message.reply_text(
        "Какая у тебя цель?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.lower()
    if goal not in ("похудение", "поддержание", "набор"):
        keyboard = [["похудение", "поддержание", "набор"]]
        await update.message.reply_text(
            "Пожалуйста, выбери цель из вариантов:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return GOAL
    user_data['goal'] = goal

    g = user_data
    gender = g['gender']
    weight = g['weight']
    height = g['height']
    age = g['age']
    activity = g['activity_factor']
    goal = g['goal']

    if gender == 'м':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity

    if goal == 'похудение':
        target = tdee - 300
    elif goal == 'набор':
        target = tdee + 300
    else:
        target = tdee

    protein_g = round(weight * 1.8)
    fat_g = round(weight * 1)
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carbs_kcal = target - (protein_kcal + fat_kcal)
    carbs_g = max(0, round(carbs_kcal / 4))

    await update.message.reply_text(
        f"🔍 Твоя базовая норма (BMR): {int(bmr)} ккал\n"
        f"🔥 С учётом активности (TDEE): {int(tdee)} ккал\n"
        f"🌟 Для цели «{goal}»: {int(target)} ккал/день\n\n"
        f"🍗 Белки: {protein_g} г\n🥑 Жиры: {fat_g} г\n🥔 Углеводы: {carbs_g} г"
    )

    keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "Хочешь пройти мини-тест на личное ведение?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return TEST_START

async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "да":
        keyboard = [["1", "2", "3"]]
        await update.message.reply_text(
            "❓ Вопрос 1:\nТы хочешь, чтобы нутрициолог был рядом на пути к цели?\n1 — Да, 2 — Не знаю, 3 — Нет",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return TEST_Q1
    else:
        await update.message.reply_text(
            "В любом случае ты можешь проконсультироваться лично и узнать подробности:\n"
            "@alisa_son"
        )
        return ConversationHandler.END

async def test_question(update: Update, context: ContextTypes.DEFAULT_TYPE, number: int, text: str, next_state: int):
    user_data[f'q{number}'] = update.message.text
    keyboard = [["1", "2", "3"]]
    await update.message.reply_text(
        f"❓ Вопрос {number+1}:\n{text}\n1 — Да, 2 — Иногда/не знаю, 3 — Нет",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return next_state

async def test_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 1, "Тебе нужна поддержка и контроль, чтобы не сдаться?", TEST_Q2)

async def test_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 2, "Тебе сложно разобраться, что подходит именно тебе?", TEST_Q3)

async def test_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 3, "Ты часто начинал(а) питание, но бросал(а)?", TEST_Q4)

async def test_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 4, "Ты хочешь индивидуальный подход к питанию?", TEST_Q5)

async def test_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 5, "Ты чувствовал(а), что теряешь мотивацию без поддержки?", TEST_Q6)

async def test_q6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 6, "Ты хочешь быстрее достичь результатов?", TEST_Q7)

async def test_q7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 7, "Ты чувствуешь, что тебе не хватает системы в питании?", TEST_Q8)

async def test_q8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 8, "Ты хочешь научиться правильно питаться на будущее?", TEST_Q9)

async def test_q9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await test_question(update, context, 9, "Ты готов(а) работать над собой вместе с наставником?", TEST_Q10)

async def test_q10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['q10'] = update.message.text
    total = 0
    for i in range(1, 11):
        ans = user_data.get(f'q{i}', '3')
        if ans == "1":
            total += 3
        elif ans == "2":
            total += 2
        else:
            total += 1

    if total >= 20:
        text = ("🎉 Поздравляю! По результатам теста тебе подходит личное ведение с нутрициологом.\n\n"
                "Напиши @alisa_son, чтобы начать.")
    else:
        text = "Спасибо за участие! Ты можешь в любое время обратиться за помощью или пройти тест снова."

    await update.message.reply_text(text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено. Если хочешь, можешь начать сначала — /start")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("5284761727:AAG5nQPZNpWLN4Gc3fCpYGtGBT83wYLNK0U").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [
                MessageHandler(filters.Regex("^(м|ж|М|Ж)$"), gender),
                MessageHandler(filters.Regex("^(🔢 Рассчитать калории|🧠 Пройти тест на личное ведение)$"), handle_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu),
            ],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            ACTIVITY: [MessageHandler(filters.Regex("^(низкий|средний|высокий)$"), activity)],
            GOAL: [MessageHandler(filters.Regex("^(похудение|поддержание|набор)$"), goal)],
            TEST_START: [MessageHandler(filters.Regex("^(да|нет|Да|Нет)$"), test_start)],
            TEST_Q1: [MessageHandler(filters.Regex("^[123]$"), test_q1)],
            TEST_Q2: [MessageHandler(filters.Regex("^[123]$"), test_q2)],
            TEST_Q3: [MessageHandler(filters.Regex("^[123]$"), test_q3)],
            TEST_Q4: [MessageHandler(filters.Regex("^[123]$"), test_q4)],
            TEST_Q5: [MessageHandler(filters.Regex("^[123]$"), test_q5)],
            TEST_Q6: [MessageHandler(filters.Regex("^[123]$"), test_q6)],
            TEST_Q7: [MessageHandler(filters.Regex("^[123]$"), test_q7)],
            TEST_Q8: [MessageHandler(filters.Regex("^[123]$"), test_q8)],
            TEST_Q9: [MessageHandler(filters.Regex("^[123]$"), test_q9)],
            TEST_Q10: [MessageHandler(filters.Regex("^[123]$"), test_q10)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
