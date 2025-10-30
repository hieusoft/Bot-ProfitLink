from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards.qa_menu import get_qa_menu
from services.qna_service import QnAService
from aiogram.fsm.context import FSMContext
import html
from config.settings import settings
qa_router = Router()

MAX_PAGE_LENGTH = settings.MAX_PAGE_LENGTH

def split_text(text: str, max_len: int = MAX_PAGE_LENGTH):
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

@qa_router.callback_query(F.data == "qa")
async def open_qa_menu(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id

    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    await bot.send_message(
        chat_id=chat_id,
        text=(
            "🧠 <b>Hieusoft Crypto Bot — Q&A Center</b>\n\n"
            "Welcome to our Help Center!\n\n"
            "Here you can find answers to common questions about subscriptions, affiliates, cashback, and technical support.\n\n"
            "Select a topic below to get started 👇"
        ),
        parse_mode="HTML",
        reply_markup=get_qa_menu()
    )
    await callback.answer()

@qa_router.callback_query(F.data.startswith("qa_category"))
async def handle_category_qa(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Invalid category data.", show_alert=True)
        return

    category_id = parts[2]
    category_slug = parts[3]

    qas = QnAService.get_qna_by_category(category_id)
    if not qas:
        await callback.message.edit_text(
            f"❌ No Q&A found for category <b>{html.escape(category_slug)}</b>.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = f"📚 <b>Q&A for {html.escape(category_slug)}</b>\n\n"
    for i, qa in enumerate(qas, start=1):
        text += f"{i}. {html.escape(qa.question)}\n"
    kb = InlineKeyboardBuilder()
    for i, qa in enumerate(qas, start=1):
        kb.button(
            text=f"{i}",
            callback_data=f"qa_show_{category_id}_{category_slug}_{qa.qna_id}"
        )

    kb.button(text="↩️ Back", callback_data="qa")
    kb.adjust(5)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@qa_router.callback_query(F.data.startswith("qa_show_"))
async def handle_show_answer(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Invalid data format.", show_alert=True)
        return

    category_id, category_slug, qna_id = parts[2], parts[3], parts[4]
    qa = QnAService.get_qna_by_id(qna_id)
    if not qa:
        await callback.answer("❌ Question not found.", show_alert=True)
        return

    question = html.escape(qa['question'])
    answer = html.escape(qa['answer'])
    pages = split_text(answer)

    await state.update_data(
        qa_pages=pages,
        qa_current_page=0,
        qa_category_id=category_id,
        qa_category_slug=category_slug,
        qa_question=question
    )

    kb = InlineKeyboardBuilder()
    if len(pages) > 1:
        kb.button(text="➡️ Next", callback_data="qa_page_1")
    kb.button(text="↩️ Back", callback_data=f"qa_category_{category_id}_{category_slug}")
    kb.adjust(1,1)

    await callback.message.edit_text(
        f"📌 <b>{category_slug}</b>\n\n<b>Question:</b> {question}\n\n<b>Answer:</b> {pages[0]}",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@qa_router.callback_query(F.data.startswith("qa_page_"))
async def handle_qa_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pages = data.get('qa_pages')
    question = data.get('qa_question')
    category_id = data.get('qa_category_id')
    category_slug = data.get('qa_category_slug')
    if not pages:
        await callback.answer("❌ No pages found.", show_alert=True)
        return

    current_page = int(callback.data.split("_")[2])

    kb = InlineKeyboardBuilder()
    if current_page > 0:
        kb.button(text="⬅️ Previous", callback_data=f"qa_page_{current_page-1}")
    if current_page < len(pages) - 1:
        kb.button(text="➡️ Next", callback_data=f"qa_page_{current_page+1}")
    kb.button(text="↩️ Back", callback_data=f"qa_category_{category_id}_{category_slug}")

    if current_page == len(pages) - 1:
        kb.adjust(1)
    else:
        kb.adjust(2, 1)

    await callback.message.edit_text(
        f"📌 <b>{category_slug}</b>\n\n<b>Question:</b> {question}\n\n<b>Answer:</b> {pages[current_page]}",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await callback.answer()
