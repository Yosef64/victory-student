from http import HTTPStatus
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler,MessageHandler,CallbackQueryHandler,filters,CallbackContext
from telegram.ext._contexttypes import ContextTypes
from fastapi import FastAPI, Request, Response
from .providers import AddStudent, ApproveStudent, GetAgentTeleId,GetStudent, GetStudentInfo, getLastId,natural, setLastId, setStudentInfo,social,message,Banks,txt


BOT_TOKEN = os.getenv("BOT_TOKEN")
channal_link = "@VictoryTutor_7"
app = FastAPI()
Admin_id = "1656463485"

def getMainMarkup():
    keyboard = [["📚12th Natural Entrance Examinee student"],
                    ['📚11th Natural Student'],
                    ["📚Natural Remedial student"],
                    ["📚Social Remedial student"],
                    ['📚12th Social Entrance Examinee student'],
                    ['ከተማሪዎች የሚነሱ ተደጋጋሚ ጥያቄዎች❓']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    return reply_markup
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    try:
        referal = context.args[0] if context.args else ""
        userInfo = {"userName":update.message.from_user.full_name,"userId":str(update.message.from_user.id)}
        chat_member = await context.bot.get_chat_member(chat_id=channal_link, user_id=update.message.from_user.id, )
        if chat_member.status in ['left', 'kicked']:
            keyboard = [[
                InlineKeyboardButton("Ready", callback_data=f"check_user:{referal}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                """To use this bot, please join our channel and press 'Ready' when you are ready.
                channel : @VictoryTutor_7
                """,
                reply_markup=reply_markup
            )
        else:

            AddStudent(referal,userInfo=userInfo)

            reply_markup = getMainMarkup()
            await update.message.reply_text(txt, reply_markup=reply_markup,parse_mode="MarkdownV2")
            return
    except Exception as e:
        await update.message.reply_text(e)
async def check_user(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    queryData = query.data.split(":")
    referal = queryData[1] if len(queryData) == 2 else ""
    userInfo = {"userName":query.from_user.full_name,"userId":str(query.from_user.id)}
    chat_member = await context.bot.get_chat_member(chat_id=channal_link, user_id=query.from_user.id, )
    keyboard = [[
            InlineKeyboardButton("Ready", callback_data=f"check_user:{referal}")
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if chat_member.status in ['left', 'kicked']:
        await context.bot.send_message(chat_id=query.from_user.id, text="""You haven't joined our channel yet.Please join our channel and press 'Ready' when you are ready.
            channel : @VictoryTutor_7
            """,reply_markup=reply_markup)
    else:
        reply_markup = getMainMarkup()
        AddStudent(referal,userInfo=userInfo)
        await context.bot.send_message(chat_id=query.from_user.id, text=txt,reply_markup=reply_markup,parse_mode="MarkdownV2")
    return

async def payment(update: Update, context: CallbackContext,isNatural) -> None:
    keyboard = [['payment method 💳'], ['🔙 Back', "🔝 Main Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    Message = natural if isNatural else social
    await update.message.reply_text(Message,reply_markup=reply_markup,parse_mode="MarkdownV2")
async def banks(update: Update, context: CallbackContext) -> None:
    keyboard = [['CBE'], ['Tele Birr'], ['Awash Bank'], ['E-Birr'],['🔙 Back', "🔝 Main Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("ከታች ከተዘረዘሩት የክፍያ አማራጮች ለናንተ ሚመቻቹን ምረጡ 👇" , reply_markup=reply_markup)
async def forward_photo_to_bot_b(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if update.message.photo:
        
        studData = GetStudentInfo(str(userId))
        bank, grade = studData["bank"], studData["grade"]
        agentTeleId , agentReferalCode = GetAgentTeleId(str(update.message.from_user.id))
        textAgent = f"""
        Full Name: {update.message.from_user.full_name}
        User Name: @{update.message.from_user.username}
        User ID: #{str(userId)}
        Agent Referral Code: {agentReferalCode if agentReferalCode else "He/She Got here on her/his own"}
        Agent Telegram ID: {agentTeleId if agentTeleId else "The Agent has telegram Id"}
        """
        textAdmin = f"""
Full Name: {update.message.from_user.full_name}
User Name: @{update.message.from_user.username}
User ID: #{str(userId)}
Agent Referral Code: {agentReferalCode if agentReferalCode else "He/She Got here on her/his own"}
Agent Telegram ID: {agentTeleId if agentTeleId else "The Agent has telegram Id"}
Bank choice: {bank if bank else "didn't choose a bank" }
Grade choice: {grade if grade else "Didn't choose a grade"}
"""

        keyboard = [
        [InlineKeyboardButton("Approve 👍", callback_data=f"approve:{userId}:{agentTeleId}"),
             InlineKeyboardButton("Deny 🚫", callback_data=f"deny:{userId}:{agentTeleId}"),
             InlineKeyboardButton("Ask ⚠️", callback_data=f"ask:{userId}:{agentTeleId}")]
    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.forward(chat_id=Admin_id)
        await context.bot.send_message(chat_id=Admin_id, text=textAdmin, reply_markup=reply_markup)
        if agentTeleId:
            await update.message.forward(chat_id=agentTeleId)
            await context.bot.send_message(chat_id=agentTeleId, text=textAgent)
async def final(update:Update,context:CallbackContext,M):
    keyboard = [["🔝 Main Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(M , reply_markup=reply_markup,parse_mode="MarkdownV2")

async def handle_option(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    student_categories = {
        "📚12th Natural Entrance Examinee student": True,
        "📚Natural Remedial student": True,
        "📚12th Social Entrance Examinee student": False,
        "📚Social Remedial student": False,
    }
    bank = ['CBE', 'Tele Birr', 'Awash Bank', 'E-Birr']
    
    try:
        if text in student_categories:
            setStudentInfo(str(user_id), ["grade", text])
            await payment(update, context, student_categories[text])
        elif text == 'ከተማሪዎች የሚነሱ ተደጋጋሚ ጥያቄዎች❓':
            await update.message.reply_text(message, quote=True, parse_mode="MarkdownV2")
        elif text == "payment method 💳":
            await banks(update, context)
        elif text in bank:
            setStudentInfo(str(user_id), ["bank", text])
            await final(update, context, Banks[text])
        elif text in ['🔝 Main Menu', '🔙 Back']:
            await start(update, context)
        else:
            keyboard = [[InlineKeyboardButton("Send", callback_data=f"send:{user_id}:{text}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text=f"Your message is:\n{text}",
                reply_markup=reply_markup,
            )
    except Exception as e:
        await update.message.reply_text("An error occurred. Please try again.")

async def button(update:Update,context:CallbackContext):
    query = update.callback_query
    await query.answer()
    userId = query.from_user.id
    action, sender_user_id ,agentTeleId = query.data.split(":")
    stud = GetStudent(sender_user_id)
    if action == "approve":
        studInfo = GetStudentInfo(sender_user_id)
        if studInfo["approved"]:
            await context.bot.send_message(chat_id=query.from_user.id, text="You have already approve this student!")
            return 
        
        result = ApproveStudent(sender_user_id)
        if result['ok']:

            await context.bot.send_message(chat_id=sender_user_id, text="Your request has been approved!")
            await context.bot.send_message(chat_id=query.from_user.id, text="You have successfully approved the request!")
            await context.bot.send_message(chat_id=agentTeleId,text=f"User {stud} has successfully approved the request!")
        else:
            await context.bot.send_message(chat_id=query.from_user.id, text=result["error"])
    elif action == "deny":
        await context.bot.send_message(chat_id=sender_user_id, text="Your request has been denied.")
        await context.bot.send_message(chat_id=query.from_user.id, text="You have successfully deny the request!")
        await context.bot.send_message(chat_id=agentTeleId,text=f"User {stud} has denied!")
    elif action== "ask":
        if str(userId) == Admin_id:
            setLastId(sender_user_id)
        await context.bot.send_message(chat_id=query.from_user.id, text="Write you message")
    elif action == "send":
        keyboard = [[InlineKeyboardButton("Reply", callback_data=f"ask:{userId}:{" "}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if str(userId) == Admin_id:
            to = getLastId()
            await context.bot.send_message(chat_id=to,text=f"From admin:\n{agentTeleId}",reply_markup=reply_markup)
        else:
            await  context.bot.send_message(chat_id=Admin_id, text=f"From {query.from_user.username}:\n{agentTeleId}",reply_markup=reply_markup)
        
@app.post("/")
async def process_update(request: Request):
    application = (
    Application.builder()
    .updater(None)
    .token(BOT_TOKEN) 
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
   )
    await application.initialize()
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_option))
    application.add_handler(MessageHandler(filters.PHOTO, forward_photo_to_bot_b))
    application.add_handler(CallbackQueryHandler(check_user,pattern=r"^check_user"))
    application.add_handler(CallbackQueryHandler(button))
    
    application.add_handler(CommandHandler("start", start))
    req = await request.json()
    update = Update.de_json(req, application.bot)
    await application.process_update(update)
    return Response(status_code=HTTPStatus.OK)
@app.get("/")
async def index(request:Request):
    return {"message":"ok"}

#https://api.telegram.org/bot7756252447:AAH6fSVh8Q6s2hip4w4wCblqDuOtrLSWSR4/setWebhook?url=https://victory-student.vercel.app/
