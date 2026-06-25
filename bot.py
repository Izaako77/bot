import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Your live configurations preserved
BOT_TOKEN = "8931595168:AAHSAaKz6ld4OKtb-fkS2C-raUlyevQ_zt8"
MINI_APP_URL = "https://myspace-amdb.onrender.com/" 
CHANNEL_ID = "@myspace_4all"  
CHANNEL_LINK = "https://t.me/myspace_4all" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    try:
        # 1. Check the user's status in your channel
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        # Allowed statuses
        allowed_statuses = ["member", "administrator", "creator"]
        
        if chat_member.status in allowed_statuses:
            # 🎉 USER HAS JOINED -> Show them the Mini App!
            welcome_text = (
                "✨ Welcome back to My Space! ✨\n\n"
                "Everything is ready for you. Tap below to step into your space."
            )
            keyboard = [[InlineKeyboardButton(text="⛺ Enter My Space", web_app=WebAppInfo(url=MINI_APP_URL))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)
            
        else:
            # ⛔ USER IS NOT A MEMBER -> Force join message
            await send_force_join_message(update)

    except BadRequest as e:
        logging.error(f"Error checking channel membership: {e}")
        await update.message.reply_text(
            "⚠️ System error: Make sure the bot is an administrator in the required channel."
        )

async def send_force_join_message(update: Update):
    """Helper function to send the lock-out message"""
    lock_text = (
        "👋 Welcome to My Space!\n\n"
        "To keep our campfire community cozy and safe, "
        "you need to **join our official channel** before entering the app. "
        "It takes 2 seconds! 👇"
    )
    
    keyboard = [
        [InlineKeyboardButton(text="📢 Join Channel", url=CHANNEL_LINK)],
        # This callback_data triggers the verify_membership_click handler below
        [InlineKeyboardButton(text="✅ I Have Joined! (Verify)", callback_data="check_again_start")] 
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=lock_text, reply_markup=reply_markup, parse_mode="Markdown")


# 🛠️ UPDATED: This handles the click action on your verify button
async def verify_membership_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        allowed_statuses = ["member", "administrator", "creator"]
        
        if chat_member.status in allowed_statuses:
            # Acknowledge the click to stop the Telegram loading spinner
            await query.answer(text="🎉 Access Granted! Welcome to the space.", show_alert=False)
            
            welcome_text = (
                "✨ Welcome to My Space! ✨\n\n"
                "Thanks for joining! Tap below to step into your space."
            )
            keyboard = [[InlineKeyboardButton(text="⛺ Enter My Space", web_app=WebAppInfo(url=MINI_APP_URL))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Cleanly swap out the lock text with the live Mini App link
            await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
            
        else:
            # Drop a native popup notice if they haven't joined yet
            await query.answer(
                text="❌ You haven't joined the channel yet! Please join and then tap verify again.", 
                show_alert=True
            )
            
    except BadRequest as e:
        logging.error(f"Error in callback verification: {e}")
        await query.answer(text="⚠️ Verification failed. Is the bot an admin in the channel?", show_alert=True)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    
    # 🌟 REGISTERED: Listens for the "check_again_start" action
    application.add_handler(CallbackQueryHandler(verify_membership_click, pattern="^check_again_start$"))
    
    print("Bot with Force-Join & Verify is running... 🔒🚀")
    application.run_polling()

if __name__ == "__main__":
    main()