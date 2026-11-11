# -*- coding: utf-8 -*-
import logging
import os
import random
import sqlite3
import threading
import http.server
import urllib.parse
import urllib.request
import datetime
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
#  НАСТРОЙКИ SLOTS
# ============================================================
BOT_TOKEN = "9021684845:AAFod7HYNnQ3vlVAdmghDYmY0zwipXiFyaE"
ADMIN_ID  = "6109042131"
WEB_PORT  = int(os.getenv("PORT", "5000"))

# Твоя партнерская ссылка для слотов
PARTNER_URL = "https://r1wagwk.com/casino/list?open=register&p=qksttrpxqi&sub1={uid}"

# ============================================================
BASE_DIR = os.getenv("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DataBase.db")

LANG = {
    'ru': {
        'welcome': "🎰 <b>ДОСТУП К СЕКРЕТНОЙ БАЗЕ СЛОТОВ ПОЛУЧЕН</b> 🎰\n\nПриветствуем в <b>SLOT AI PREDICTOR</b>!\n\n😤 Устал сливать депозит в мертвых автоматах? Наша нейросеть сканирует серверы казино и находит <b>«горячие» слоты</b> (Hot Slots).\n\n🧠 <b>Как это работает?</b>\n1. Ты вводишь свой банкролл\n2. Выбираешь уровень риска\n3. ИИ выдает слот и <b>пошаговую тактику</b> с изменением ставки\n\n🎁 <i>Хочешь получать больше и участвовать в розыгрыше $100? Жми «👥 Конкурс и Рефералы».</i>",
        'btn_reg': "💳 Регистрация", 'btn_instr': "📖 Инструкция", 'btn_sign': "🎰 Выдать слот", 'btn_lang': "🌐 Язык", 'btn_ref': "👥 Конкурс и Рефералы", 'btn_support': "🆘 Поддержка",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Язык изменен на Русский 🇷🇺",
        'need_reg': "⚠️ <b>ДОСТУП ЗАБЛОКИРОВАН!</b>\n\nАлгоритм ИИ требует привязки аккаунта казино.\n\n👇 Зарегистрируйся в 1 клик, чтобы открыть доступ:",
        'regged': "✅ <b>УСПЕХ!</b> Аккаунт привязан. Нейросеть активирована. Жми «Выдать слот»! 🚀",
        'ask_deposit': "💰 <b>Введите сумму вашего депозита (в рублях или долларах):</b>\n\n<i>Например: 1000</i>\nНаш ИИ рассчитает безопасную тактику, чтобы вы не слили банк.",
        'invalid_deposit': "❌ <b>Ошибка!</b> Пожалуйста, введите число (например, 500 или 1000).",
        'ask_risk': "⚙️ <b>Выберите уровень риска:</b>\n\n🟢 <b>Низкий</b> — безопасная игра (базовая ставка 1%)\n🟡 <b>Средний</b> — золотая середина (базовая ставка 2.5%)\n🔴 <b>Высокий</b> — агрессивный занос (базовая ставка 5%)",
        'btn_risk_low': "🟢 Низкий риск", 'btn_risk_med': "🟡 Средний риск", 'btn_risk_high': "🔴 Высокий риск",
        'signal_title': "🎰 <b>Анализ завершен! Найден горячий слот:</b>\n\n",
        'signal_slot': "🔥 Слот: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Тактика: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Шаг 1: Сделай <b>{spins1} круток</b> по <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Шаг 2: Если пусто — поднимай до <b>{bet2}</b> и крути <b>{spins2} раз</b>.\n",
        'signal_tactic_step3': "3️⃣ Шаг 3: Финальный занос: ставь <b>{bet3}</b> и делай <b>{spins3} круток</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Удачи! Если поймал бонус — сразу сбрасывай ставку до базовой.",
        'left_signals': "💡 <i>Осталось сигналов на сегодня: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>ДНЕВНОЙ ЛИМИТ ИСЧЕРПАН!</b>\n\nВы использовали все {limit} сигналов на сегодня.\n\n👇 <b>Хотите больше?</b> Пригласите друга по кнопке «👥 Конкурс и Рефералы»!",
        'instr_text': "📖 <b>КАК ИГРАТЬ ПО СИГНАЛАМ:</b>\n\n1️⃣ <b>Регистрация:</b> <a href='{url}'>КЛИКНИ СЮДА</a>\n2️⃣ <b>Депозит:</b> Пополни баланс.\n3️⃣ <b>Игра:</b> Зайди в раздел Слоты.\n4️⃣ <b>Настройка:</b> Открой слот, который дал бот, и четко следуй тактике (Шаг 1, 2, 3).",
        'admin_panel': "⚙️ Админ панель. Команда /top - таблица лидеров.", 'not_admin': "❌ У вас нет прав администратора.",
        'support_text': "🆘 <b>Служба поддержки</b>\n\n👉 <a href='tg://user?id={admin_id}'>Написать администратору</a>",
        'ref_title': "🏆 <b>КОНКУРС С ПРИЗОВЫМ ФОНДОМ</b> 🏆\n\nПриглашай друзей и зарабатывай билеты! <b>1 зарегистрированный друг = 1 билет.</b>\n\n🥇 <b>1 место:</b> $100\n🥈 <b>2 место:</b> $50\n🥉 <b>3 место:</b> $20\n\n📊 Твои билеты: <b>{count}</b>\n\n🔗 Твоя ссылка:\n<code>{link}</code>",
        'ref_notify': "🎉 По твоей ссылке зарегистрировался друг! Ты получил +1 билет. Всего: <b>{count}</b>.",
        'ref_success': "🔥 <b>Ты пригласил 3 друзей!</b> Твой доступ открыт навсегда!"
    },
    'en': {
        'welcome': "🎰 <b>SECRET SLOT DATABASE ACCESS GRANTED</b> 🎰\n\nWelcome to <b>SLOT AI PREDICTOR</b>!\n\n😤 Tired of losing deposits in dead slots? Our neural network scans casino servers to find <b>Hot Slots</b>.\n\n🧠 <b>How it works?</b>\n1. You enter your bankroll\n2. You choose risk level\n3. AI gives you a slot and a <b>step-by-step betting tactic</b>\n\n🎁 <i>Want more? Click '👥 Contest & Refs'.</i>",
        'btn_reg': "💳 Register", 'btn_instr': "📖 Instruction", 'btn_sign': "🎰 Get Slot", 'btn_lang': "🌐 Language", 'btn_ref': "👥 Contest & Refs", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Language changed to English 🇬🇧",
        'need_reg': "⚠️ <b>ACCESS BLOCKED!</b>\n\nRegister below to unlock:",
        'regged': "✅ <b>SUCCESS!</b> Account linked. Click 'Get Slot'! 🚀",
        'ask_deposit': "💰 <b>Enter your deposit amount (in $ or €):</b>\n\n<i>Example: 100</i>\nOur AI will calculate a safe tactic.",
        'invalid_deposit': "❌ <b>Error!</b> Please enter a number (e.g., 50 or 100).",
        'ask_risk': "⚙️ <b>Choose your risk level:</b>\n\n🟢 <b>Low</b> — safe play (base bet 1%)\n🟡 <b>Medium</b> — balanced (base bet 2.5%)\n🔴 <b>High</b> — aggressive (base bet 5%)",
        'btn_risk_low': "🟢 Low Risk", 'btn_risk_med': "🟡 Medium Risk", 'btn_risk_high': "🔴 High Risk",
        'signal_title': "🎰 <b>Analysis Complete! Hot Slot Found:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Tactic: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Step 1: Make <b>{spins1} spins</b> at <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Step 2: If dry — increase to <b>{bet2}</b> and spin <b>{spins2} times</b>.\n",
        'signal_tactic_step3': "3️⃣ Step 3: Final push: bet <b>{bet3}</b> and make <b>{spins3} spins</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Good luck! If you catch a bonus — reset to the base bet.",
        'left_signals': "💡 <i>Signals left today: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>DAILY LIMIT REACHED!</b>\n\nInvite a friend via '👥 Contest & Refs' to get more!",
        'instr_text': "📖 <b>HOW TO START:</b>\n\n1️⃣ <b>Register:</b> <a href='{url}'>CLICK HERE</a>\n2️⃣ <b>Deposit:</b> Top up.\n3️⃣ <b>Game:</b> Go to Slots.\n4️⃣ <b>Setup:</b> Open the slot from the bot and follow the tactic (Step 1, 2, 3).",
        'admin_panel': "⚙️ Admin panel.", 'not_admin': "❌ No admin rights.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Message Admin</a>",
        'ref_title': "🏆 <b>PRIZE POOL CONTEST</b> 🏆\n\nInvite friends! <b>1 friend = 1 ticket.</b>\n\n🥇 <b>1st:</b> $100\n🥈 <b>2nd:</b> $50\n🥉 <b>3rd:</b> $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Friend registered! +1 ticket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 friends invited!</b> Access open forever!"
    }
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("slots")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY, postback_id TEXT, language TEXT DEFAULT 'ru', referrer_id INTEGER, daily_signals INTEGER DEFAULT 0, last_signal_date TEXT)")
        conn.commit()
        for col, typ in [("language", "TEXT DEFAULT 'ru'"), ("referrer_id", "INTEGER"), ("daily_signals", "INTEGER DEFAULT 0"), ("last_signal_date", "TEXT")]:
            try: conn.execute(f"ALTER TABLE user ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError: pass

def get_user(uid: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT postback_id, language, referrer_id, daily_signals, last_signal_date FROM user WHERE user_id = ?", (uid,)).fetchone()
        if row:
            lang = row[1] if row[1] in LANG else 'ru'
            ref_count = conn.execute("SELECT COUNT(*) FROM user WHERE referrer_id = ? AND postback_id IS NOT NULL", (uid,)).fetchone()[0]
            return {"user_id": uid, "postback_id": row[0], "lang": lang, "referrer_id": row[2], "ref_count": ref_count, "daily_signals": row[3] or 0, "last_signal_date": row[4]}
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True))
dp = Dispatcher(storage=MemoryStorage())

class SlotState(StatesGroup):
    waiting_for_deposit = State()
    waiting_for_risk = State()

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")]])

def main_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_reg'], callback_data="reg")],
        [InlineKeyboardButton(text=LANG[lang]['btn_instr'], callback_data="instr")],
        [InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")],
        [InlineKeyboardButton(text=LANG[lang]['btn_ref'], callback_data="ref_menu")],
        [InlineKeyboardButton(text=LANG[lang]['btn_support'], callback_data="support")],
        [InlineKeyboardButton(text=LANG[lang]['btn_lang'], callback_data="lang_menu")]
    ])

def reg_kb(uid, lang):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_reg'], url=PARTNER_URL.format(uid=uid))]])

def risk_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_low'], callback_data="set_risk_low")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_med'], callback_data="set_risk_med")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_high'], callback_data="set_risk_high")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])

def sign_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")], [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])

def generate_slot_signal(lang, deposit, risk_level, signals_left=0):
    slots = ["Sweet Bonanza", "Gates of Olympus", "The Dog House", "Sugar Rush", "Big Bass Bonanza", "Money Train 3", "San Quentin"]
    
    # Словарь тактик (Шаблоны)
    tactics = {
        'martingale': {
            'name_ru': "Мартингейл (Догон)", 'name_en': "Martingale",
            'tip_ru': "Крути строго по шагам. Поймал бонус — вернись к Шагу 1.",
            'tip_en': "Strictly follow the steps. Catch a bonus — reset to Step 1."
        },
        'ladder': {
            'name_ru': "Лесенка (Плавный подъем)", 'name_en': "Ladder",
            'tip_ru': "Плавно повышаем ставку. Если 3 шага в минус — меняй слот.",
            'tip_en': "Smoothly increase the bet. If 3 steps are dry — change the slot."
        },
        'sniper': {
            'name_ru': "Снайпер (Hit & Run)", 'name_en': "Sniper (Hit & Run)",
            'tip_ru': "Быстрый занос на высокой ставке. Если пусто — уходи с автомата.",
            'tip_en': "Quick high-bet push. If dry — leave the machine."
        }
    }
    
    slot = random.choice(slots)
    
    # Расчет базовой ставки
    if risk_level == "low":
        base_pct = 0.01
    elif risk_level == "high":
        base_pct = 0.05
    else:
        base_pct = 0.025
        
    bet1 = round(deposit * base_pct, 2)
    if bet1 < 1: bet1 = 1
    
    # Выбор тактики случайно
    tactic_key = random.choice(list(tactics.keys()))
    tactic = tactics[tactic_key]
    
    # Настройка шагов в зависимости от тактики
    if tactic_key == 'martingale':
        bet2 = round(bet1 * 2, 2)
        bet3 = round(bet1 * 4, 2)
        spins1, spins2, spins3 = 10, 5, 3
    elif tactic_key == 'ladder':
        bet2 = round(bet1 * 1.5, 2)
        bet3 = round(bet1 * 2, 2)
        spins1, spins2, spins3 = 15, 10, 5
    else: # sniper
        bet2 = bet1
        bet3 = bet1
        spins1, spins2, spins3 = 5, 5, 5
        
    tactic_name = tactic['name_ru'] if lang == 'ru' else tactic['name_en']
    tip = tactic['tip_ru'] if lang == 'ru' else tactic['tip_en']
    
    title = LANG[lang]['signal_title']
    slot_text = LANG[lang]['signal_slot'].format(slot=slot)
    t_title = LANG[lang]['signal_tactic_title'].format(tactic_name=tactic_name)
    
    if tactic_key == 'sniper':
        # Для снайпера все шаги одинаковые, но мы показываем 3 попытки
        step1 = LANG[lang]['signal_tactic_step1'].format(spins1=spins1, bet1=bet1)
        step2 = LANG[lang]['signal_tactic_step2'].format(spins2=spins2, bet2=bet1)
        step3 = LANG[lang]['signal_tactic_step3'].format(spins3=spins3, bet3=bet1)
    else:
        step1 = LANG[lang]['signal_tactic_step1'].format(spins1=spins1, bet1=bet1)
        step2 = LANG[lang]['signal_tactic_step2'].format(spins2=spins2, bet2=bet2)
        step3 = LANG[lang]['signal_tactic_step3'].format(spins3=spins3, bet3=bet3)
        
    left_text = LANG[lang]['left_signals'].format(left=signals_left) if signals_left > 0 else ""
    footer = LANG[lang]['signal_footer'].format(tip=tip, left=left_text)
    
    return f"{title}{slot_text}{t_title}{step1}{step2}{step3}{footer}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    uid = message.from_user.id
    ref = command.args
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO user (user_id) VALUES (?)", (uid,))
        if ref and ref.isdigit() and int(ref) != uid:
            conn.execute("UPDATE user SET referrer_id = ? WHERE user_id = ? AND referrer_id IS NULL", (int(ref), uid))
        conn.commit()
    await message.answer(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data == "lang_menu")
async def cb_lang_menu(call: types.CallbackQuery): await call.message.edit_text(LANG['ru']['choose_lang'], reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("set_lang_"))
async def cb_set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[-1]
    with sqlite3.connect(DB_PATH) as conn: conn.execute("UPDATE user SET language = ? WHERE user_id = ?", (lang, call.from_user.id)); conn.commit()
    await call.answer(LANG[lang]['lang_set'])
    await call.message.edit_text(LANG[lang]['welcome'], reply_markup=main_menu(lang))

@dp.callback_query(F.data == "main_menu")
async def cb_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    await call.message.edit_text(LANG[lang]['welcome'], reply_markup=main_menu(lang)); await call.answer()

@dp.callback_query(F.data == "support")
async def cb_sup(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
    await call.message.edit_text(LANG[lang]['support_text'].format(admin_id=ADMIN_ID), reply_markup=kb, disable_web_page_preview=True); await call.answer()

@dp.callback_query(F.data == "ref_menu")
async def cb_ref(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    b_info = await bot.get_me(); link = f"https://t.me/{b_info.username}?start={call.from_user.id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])
    await call.message.edit_text(LANG[lang]['ref_title'].format(link=link, count=u['ref_count']), reply_markup=kb, disable_web_page_preview=True); await call.answer()

@dp.callback_query(F.data == "instr")
async def cb_instr(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    await call.message.answer(LANG[lang]['instr_text'].format(url=PARTNER_URL.format(uid=call.from_user.id))); await call.answer()

@dp.callback_query(F.data == "reg")
async def cb_reg(call: types.CallbackQuery):
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang)); await call.answer()

@dp.callback_query(F.data == "sign")
async def cb_sign(call: types.CallbackQuery, state: FSMContext):
    u = get_user(call.from_user.id)
    if not u or not (u['postback_id'] or u['ref_count'] >= 3):
        lang = u['lang'] if u else 'ru'
        await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang)); await call.answer(); return
    
    lang = u['lang']
    today = datetime.date.today().isoformat()
    daily = 0 if u['last_signal_date'] != today else u['daily_signals']
    if daily >= 5:
        await call.answer("⚠️ Лимит исчерпан!", show_alert=True); await call.message.answer(LANG[lang]['limit_msg'].format(limit=5)); return
        
    await call.message.edit_text(LANG[lang]['ask_deposit'])
    await state.set_state(SlotState.waiting_for_deposit)
    await state.update_data(lang=lang, daily_signals=daily)
    await call.answer()

@dp.message(SlotState.waiting_for_deposit, F.text)
async def process_deposit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    try:
        deposit = float(message.text.replace(',', '.').replace(' ', '').strip())
        if deposit <= 0: raise ValueError
    except ValueError:
        await message.answer(LANG[lang]['invalid_deposit']); return
    
    await state.update_data(deposit=deposit)
    await message.answer(LANG[lang]['ask_risk'], reply_markup=risk_kb(lang))
    await state.set_state(SlotState.waiting_for_risk)

@dp.callback_query(SlotState.waiting_for_risk, F.data.startswith("set_risk_"))
async def process_risk(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    deposit = data.get('deposit', 100)
    daily = data.get('daily_signals', 0)
    
    risk_level = call.data.split("_")[-1]
    
    daily += 1
    today = datetime.date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE user SET daily_signals = ?, last_signal_date = ? WHERE user_id = ?", (daily, today, call.from_user.id))
        conn.commit()
    
    signal_text = generate_slot_signal(lang, deposit, risk_level, 5 - daily)
    
    await call.message.edit_text(text=signal_text, reply_markup=sign_kb(lang))
    await call.answer()
    await state.clear()

@dp.message(Command("admin"))
async def cmd_adm(msg: types.Message):
    if str(msg.from_user.id) == ADMIN_ID: await msg.answer("⚙️ Админ панель. /top")

@dp.message(Command("top"))
async def cmd_top(msg: types.Message):
    if str(msg.from_user.id) != ADMIN_ID: return
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT u1.user_id, COUNT(u2.user_id) FROM user u1 JOIN user u2 ON u1.user_id = u2.referrer_id WHERE u2.postback_id IS NOT NULL GROUP BY u1.user_id ORDER BY 2 DESC LIMIT 10").fetchall()
    text = "🏆 <b>ТОП-10</b>\n\n" + "".join([f"{i}. ID: <code>{r[0]}</code> — <b>{r[1]} билетов</b>\n" for i, r in enumerate(rows, 1)]) if rows else "Нет рефералов."
    await msg.answer(text)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/health': self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok": true}'); return
        if p.path == '/postback':
            q = urllib.parse.parse_qs(p.query); s1, s2 = q.get('sub1',[''])[0], q.get('subid',[''])[0]
            if not s1 or not s2: self.send_response(400); self.end_headers(); return
            try: uid = int(s1)
            except: self.send_response(400); self.end_headers(); return
            with sqlite3.connect(DB_PATH) as conn: conn.execute("INSERT INTO user (user_id, postback_id) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET postback_id = excluded.postback_id", (uid, s2)); conn.commit()
            u = get_user(uid); lang = u['lang'] if u else 'ru'
            try: urllib.request.urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={uid}&text={urllib.parse.quote(LANG[lang]['regged'])}&parse_mode=HTML", timeout=5)
            except: pass
            if u and u.get('referrer_id'):
                r_u = get_user(u['referrer_id'])
                if r_u:
                    t = LANG[r_u['lang']]['ref_success'] if r_u['ref_count'] >= 3 else LANG[r_u['lang']]['ref_notify'].format(count=r_u['ref_count'])
                    try: urllib.request.urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={r_u['user_id']}&text={urllib.parse.quote(t)}&parse_mode=HTML", timeout=5)
                    except: pass
            self.send_response(200); self.end_headers(); self.wfile.write(f"sub1={s1}; subid={s2}; OK".encode('utf-8')); return
        self.send_response(404); self.end_headers()

async def main():
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Start"))
    log.info("Bot starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: http.server.HTTPServer(('0.0.0.0', WEB_PORT), Handler).serve_forever(), daemon=True).start()
    log.info("Web server started on port %s", WEB_PORT)
    asyncio.run(main())