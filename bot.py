# -*- coding: utf-8 -*-
import logging
import os
import random
import sqlite3
import threading
import http.server
import urllib.parse
import urllib.request
import urllib.error
import datetime
import asyncio
import json

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
#  НАСТРОЙКИ SLOTS BOT
# ============================================================
BOT_TOKEN = "9021684845:AAFod7HYNnQ3vlVAdmghDYmY0zwipXiFyaE" 
ADMIN_ID  = "6109042131"
WEB_PORT  = int(os.getenv("PORT", "5000"))

PARTNER_URL = "https://r1wagwk.com/casino/list?open=register&p=qksttrpxqi&sub1={uid}"

# ============================================================
BASE_DIR = os.getenv("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "DataBase.db")

LANG = {
    'ru': {
        'welcome': "🎰 <b>ДОСТУП К СЕКРЕТНОЙ БАЗЕ СЛОТОВ ПОЛУЧЕН</b> 🎰\n\nПриветствуем в <b>SLOT AI PREDICTOR</b>!\n\n😤 Устал сливать депозит в мертвых автоматах? Наша нейросеть сканирует серверы казино и находит <b>«горячие» слоты</b>.\n\n1. Введи банкролл\n2. Выбери риск\n3. ИИ выдаст слот и <b>тактику</b>",
        'btn_reg': "💳 Регистрация", 'btn_instr': "📖 Инструкция", 'btn_sign': "🎰 Выдать слот", 'btn_lang': "🌐 Язык", 'btn_ref': "👥 Конкурс", 'btn_support': "🆘 Поддержка",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Язык изменен на Русский 🇷🇺",
        'need_reg': "⚠️ <b>ДОСТУП ЗАБЛОКИРОВАН!</b>\n\nЗарегистрируйся в 1 клик:",
        'regged': "✅ <b>УСПЕХ!</b> Жми «Выдать слот»! 🚀",
        'ask_deposit': "💰 <b>Введите сумму вашего депозита:</b>\n\n<i>Например: 1000</i>\nНаш ИИ рассчитает безопасную тактику.",
        'invalid_deposit': "❌ <b>Ошибка!</b> Пожалуйста, введите число.",
        'ask_risk': "⚙️ <b>Выберите уровень риска:</b>\n\n🟢 Низкий (1%)\n🟡 Средний (2.5%)\n🔴 Высокий (5%)",
        'btn_risk_low': "🟢 Низкий", 'btn_risk_med': "🟡 Средний", 'btn_risk_high': "🔴 Высокий",
        'btn_main': "⬅️ Главное меню",
        'signal_title': "🎰 <b>Анализ завершен! Найден горячий слот:</b>\n\n",
        'signal_slot': "🔥 Слот: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Тактика: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Шаг 1: Сделай <b>{spins1} круток</b> по <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Шаг 2: Если пусто — поднимай до <b>{bet2}</b> и крути <b>{spins2} раз</b>.\n",
        'signal_tactic_step3': "3️⃣ Шаг 3: Занос: ставь <b>{bet3}</b> и делай <b>{spins3} круток</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Удачи!",
        'left_signals': "💡 <i>Осталось сигналов: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n\nПригласите друга!",
        'instr_text': "📖 <b>КАК ИГРАТЬ:</b>\n\n1️⃣ <b>Регистрация:</b> <a href='{url}'>КЛИКНИ СЮДА</a>\n2️⃣ <b>Депозит.</b>\n3️⃣ <b>Игра:</b> Слоты.\n4️⃣ <b>Настройка:</b> Открой слот и следуй тактике.",
        'admin_panel': "⚙️ <b>АДМИН ПАНЕЛЬ</b>\n\n👑 Статус: <b>GOD MODE</b>\n📊 Управление: /top",
        'not_admin': "❌ Вы не админ.",
        'support_text': "🆘 <b>Поддержка</b>\n\n👉 <a href='tg://user?id={admin_id}'>Написать админу</a>",
        'ref_title': "🏆 <b>КОНКУРС</b> 🏆\n\n1 друг = 1 билет.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Билеты: <b>{count}</b>\n\n🔗 Ссылка:\n<code>{link}</code>",
        'ref_notify': "🎉 Друг зарегистрировался! +1 билет. Всего: <b>{count}</b>.",
        'ref_success': "🔥 <b>Ты пригласил 3 друзей!</b> Доступ открыт!"
    },
    'en': {
        'welcome': "🎰 <b>SECRET SLOT DATABASE ACCESS GRANTED</b> 🎰\n\nWelcome to <b>SLOT AI PREDICTOR</b>!\n\nTired of losing deposits? Our neural network finds <b>Hot Slots</b>.\n\n1. Enter bankroll\n2. Choose risk\n3. AI gives slot & tactic",
        'btn_reg': "💳 Register", 'btn_instr': "📖 Instruction", 'btn_sign': "🎰 Get Slot", 'btn_lang': "🌐 Language", 'btn_ref': "👥 Contest", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Language changed to English 🇬🇧",
        'need_reg': "⚠️ <b>ACCESS BLOCKED!</b>\n\nRegister below:",
        'regged': "✅ <b>SUCCESS!</b> Click 'Get Slot'! 🚀",
        'ask_deposit': "💰 <b>Enter your deposit amount:</b>\n\n<i>Example: 100</i>",
        'invalid_deposit': "❌ <b>Error!</b> Please enter a number.",
        'ask_risk': "⚙️ <b>Choose risk level:</b>\n\n🟢 Low (1%)\n🟡 Medium (2.5%)\n🔴 High (5%)",
        'btn_risk_low': "🟢 Low", 'btn_risk_med': "🟡 Medium", 'btn_risk_high': "🔴 High",
        'btn_main': "⬅️ Main Menu",
        'signal_title': "🎰 <b>Analysis Complete! Hot Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Tactic: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Step 1: Make <b>{spins1} spins</b> at <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Step 2: If dry — increase to <b>{bet2}</b> and spin <b>{spins2} times</b>.\n",
        'signal_tactic_step3': "3️⃣ Step 3: Final push: bet <b>{bet3}</b> and make <b>{spins3} spins</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Good luck!",
        'left_signals': "💡 <i>Signals left: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMIT REACHED!</b>\n\nInvite a friend!",
        'instr_text': "📖 <b>HOW TO START:</b>\n\n1️⃣ <b>Register:</b> <a href='{url}'>CLICK HERE</a>\n2️⃣ <b>Deposit.</b>\n3️⃣ <b>Game:</b> Slots.",
        'admin_panel': "⚙️ <b>ADMIN PANEL</b>\n\n👑 Status: <b>GOD MODE</b>\n📊 Commands: /top",
        'not_admin': "❌ No rights.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Message Admin</a>",
        'ref_title': "🏆 <b>CONTEST</b> 🏆\n\n1 friend = 1 ticket.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Friend registered! +1 ticket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 friends invited!</b> Access open!"
    },
    'pt': {
        'welcome': "🎰 <b>ACESSO À BASE SECRETA DE SLOTS CONCEDIDO</b> 🎰\n\nBem-vindo ao <b>SLOT AI PREDICTOR</b>!\n\nCansado de perder depósitos? Nossa rede neural encontra <b>Hot Slots</b>.\n\n1. Insira o bankroll\n2. Escolha o risco\n3. IA dará o slot e a tática",
        'btn_reg': "💳 Registre-se", 'btn_instr': "📖 Instrução", 'btn_sign': "🎰 Obter Slot", 'btn_lang': "🌐 Idioma", 'btn_ref': "👥 Concurso", 'btn_support': "🆘 Suporte",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Idioma alterado para Português 🇵🇹",
        'need_reg': "⚠️ <b>ACESSO BLOQUEADO!</b>\n\nRegistre-se abaixo:",
        'regged': "✅ <b>SUCESSO!</b> Clique em 'Obter Slot'! 🚀",
        'ask_deposit': "💰 <b>Insira o valor do seu depósito:</b>\n\n<i>Exemplo: 100</i>",
        'invalid_deposit': "❌ <b>Erro!</b> Insira um número.",
        'ask_risk': "⚙️ <b>Escolha o nível de risco:</b>\n\n🟢 Baixo (1%)\n🟡 Médio (2.5%)\n🔴 Alto (5%)",
        'btn_risk_low': "🟢 Baixo", 'btn_risk_med': "🟡 Médio", 'btn_risk_high': "🔴 Alto",
        'btn_main': "⬅️ Menu Principal",
        'signal_title': "🎰 <b>Análise Concluída! Hot Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Tática: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Passo 1: Faça <b>{spins1} giros</b> a <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Passo 2: Se vazio — aumente para <b>{bet2}</b> e gire <b>{spins2} vezes</b>.\n",
        'signal_tactic_step3': "3️⃣ Passo 3: Push final: aposte <b>{bet3}</b> e faça <b>{spins3} giros</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Boa sorte!",
        'left_signals': "💡 <i>Sinais restantes: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMITE ATINGIDO!</b>\n\nConvide um amigo!",
        'instr_text': "📖 <b>COMO COMEÇAR:</b>\n\n1️⃣ <b>Registro:</b> <a href='{url}'>CLIQUE AQUI</a>\n2️⃣ <b>Depósito.</b>\n3️⃣ <b>Jogo:</b> Slots.",
        'admin_panel': "⚙️ <b>PAINEL ADMIN</b>\n\n👑 Status: <b>GOD MODE</b>\n📊 Comandos: /top",
        'not_admin': "❌ Sem direitos.",
        'support_text': "🆘 <b>Suporte</b>\n\n👉 <a href='tg://user?id={admin_id}'>Mensagem ao Admin</a>",
        'ref_title': "🏆 <b>CONCURSO</b> 🏆\n\n1 amigo = 1 bilhete.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Bilhetes: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Amigo registrado! +1 bilhete. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 amigos convidados!</b> Acesso aberto!"
    },
    'es': {
        'welcome': "🎰 <b>ACCESO A LA BASE SECRETA DE SLOTS CONCEDIDO</b> 🎰\n\n¡Bienvenido a <b>SLOT AI PREDICTOR</b>!\n\n¿Cansado de perder depósitos? Nuestra red neuronal encuentra <b>Hot Slots</b>.\n\n1. Ingresa bankroll\n2. Elige riesgo\n3. IA da el slot y la táctica",
        'btn_reg': "💳 Registrarse", 'btn_instr': "📖 Instrucción", 'btn_sign': "🎰 Obtener Slot", 'btn_lang': "🌐 Idioma", 'btn_ref': "👥 Concurso", 'btn_support': "🆘 Soporte",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Idioma cambiado a Español 🇪🇸",
        'need_reg': "⚠️ <b>¡ACCESO BLOQUEADO!</b>\n\nRegístrate abajo:",
        'regged': "✅ <b>¡ÉXITO!</b> ¡Haz clic en 'Obtener Slot'! 🚀",
        'ask_deposit': "💰 <b>Ingresa el monto de tu depósito:</b>\n\n<i>Ejemplo: 100</i>",
        'invalid_deposit': "❌ <b>¡Error!</b> Ingresa un número.",
        'ask_risk': "⚙️ <b>Elige el nivel de riesgo:</b>\n\n🟢 Bajo (1%)\n🟡 Medio (2.5%)\n🔴 Alto (5%)",
        'btn_risk_low': "🟢 Bajo", 'btn_risk_med': "🟡 Medio", 'btn_risk_high': "🔴 Alto",
        'btn_main': "⬅️ Menú Principal",
        'signal_title': "🎰 <b>¡Análisis Completado! Hot Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Táctica: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Paso 1: Haz <b>{spins1} giros</b> a <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Paso 2: Si está seco — sube a <b>{bet2}</b> y gira <b>{spins2} veces</b>.\n",
        'signal_tactic_step3': "3️⃣ Paso 3: Empuje final: apuesta <b>{bet3}</b> y haz <b>{spins3} giros</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}¡Buena suerte!",
        'left_signals': "💡 <i>Señales restantes: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>¡LÍMITE ALCANZADO!</b>\n\n¡Invita a un amigo!",
        'instr_text': "📖 <b>CÓMO EMPEZAR:</b>\n\n1️⃣ <b>Registro:</b> <a href='{url}'>HAZ CLIC AQUÍ</a>\n2️⃣ <b>Depósito.</b>\n3️⃣ <b>Juego:</b> Slots.",
        'admin_panel': "⚙️ <b>PANEL ADMIN</b>\n\n👑 Estado: <b>GOD MODE</b>\n📊 Comandos: /top",
        'not_admin': "❌ Sin derechos.",
        'support_text': "🆘 <b>Soporte</b>\n\n👉 <a href='tg://user?id={admin_id}'>Mensaje al Admin</a>",
        'ref_title': "🏆 <b>CONCURSO</b> 🏆\n\n1 amigo = 1 boleto.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Boletos: <b>{count}</b>\n\n🔗 Enlace:\n<code>{link}</code>",
        'ref_notify': "🎉 ¡Amigo registrado! +1 boleto. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>¡3 amigos invitados!</b> ¡Acceso abierto!"
    },
    'fr': {
        'welcome': "🎰 <b>ACCÈS À LA BASE DE DONNÉES SECRÈTE DES SLOTS ACCORDÉ</b> 🎰\n\nBienvenue sur <b>SLOT AI PREDICTOR</b> !\n\nFatigué de perdre des dépôts ? Notre réseau de neurones trouve les <b>Hot Slots</b>.\n\n1. Entrez votre bankroll\n2. Choisissez le risque\n3. L'IA donne le slot et la tactique",
        'btn_reg': "💳 S'inscrire", 'btn_instr': "📖 Instruction", 'btn_sign': "🎰 Obtenir un slot", 'btn_lang': "🌐 Langue", 'btn_ref': "👥 Concours", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Langue changée en Français 🇫🇷",
        'need_reg': "⚠️ <b>ACCÈS BLOQUÉ !</b>\n\nInscrivez-vous ci-dessous :",
        'regged': "✅ <b>SUCCÈS !</b> Cliquez sur 'Obtenir un slot' ! 🚀",
        'ask_deposit': "💰 <b>Entrez le montant de votre dépôt :</b>\n\n<i>Exemple : 100</i>",
        'invalid_deposit': "❌ <b>Erreur !</b> Veuillez entrer un nombre.",
        'ask_risk': "⚙️ <b>Choisissez le niveau de risque :</b>\n\n🟢 Faible (1%)\n🟡 Moyen (2.5%)\n🔴 Élevé (5%)",
        'btn_risk_low': "🟢 Faible", 'btn_risk_med': "🟡 Moyen", 'btn_risk_high': "🔴 Élevé",
        'btn_main': "⬅️ Menu Principal",
        'signal_title': "🎰 <b>Analyse terminée ! Hot Slot :</b>\n\n",
        'signal_slot': "🔥 Slot : <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Tactique : {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Étape 1 : Faites <b>{spins1} tours</b> à <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Étape 2 : Si sec — augmentez à <b>{bet2}</b> et tournez <b>{spins2} fois</b>.\n",
        'signal_tactic_step3': "3️⃣ Étape 3 : Poussée finale : pariez <b>{bet3}</b> et faites <b>{spins3} tours</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Bonne chance !",
        'left_signals': "💡 <i>Signaux restants : {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMITE ATTEINTE !</b>\n\nInvitez un ami !",
        'instr_text': "📖 <b>COMMENT COMMENCER :</b>\n\n1️⃣ <b>Inscription :</b> <a href='{url}'>CLIQUEZ ICI</a>\n2️⃣ <b>Dépôt.</b>\n3️⃣ <b>Jeu :</b> Slots.",
        'admin_panel': "⚙️ <b>PANNEAU ADMIN</b>\n\n👑 Statut : <b>GOD MODE</b>\n📊 Commandes : /top",
        'not_admin': "❌ Pas de droits.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Message à l'Admin</a>",
        'ref_title': "🏆 <b>CONCOURS</b> 🏆\n\n1 ami = 1 ticket.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Tickets : <b>{count}</b>\n\n🔗 Lien :\n<code>{link}</code>",
        'ref_notify': "🎉 Ami inscrit ! +1 ticket. Total : <b>{count}</b>.",
        'ref_success': "🔥 <b>3 amis invités !</b> Accès ouvert !"
    },
    'de': {
        'welcome': "🎰 <b>ZUGANG ZUR GEHEIMEN SLOT-DATENBANK GEWÄHRT</b> 🎰\n\nWillkommen bei <b>SLOT AI PREDICTOR</b>!\n\nMüde von verlorenen Einzahlungen? Unser neuronales Netzwerk findet <b>Hot Slots</b>.\n\n1. Bankroll eingeben\n2. Risiko wählen\n3. KI gibt Slot & Taktik",
        'btn_reg': "💳 Registrieren", 'btn_instr': "📖 Anleitung", 'btn_sign': "🎰 Slot holen", 'btn_lang': "🌐 Sprache", 'btn_ref': "👥 Gewinnspiel", 'btn_support': "🆘 Support",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Sprache auf Deutsch geändert 🇩🇪",
        'need_reg': "⚠️ <b>ZUGANG BLOCKIERT!</b>\n\nRegistrieren Sie sich unten:",
        'regged': "✅ <b>ERFOLG!</b> Klicken Sie auf 'Slot holen'! 🚀",
        'ask_deposit': "💰 <b>Geben Sie Ihren Einzahlungsbetrag ein:</b>\n\n<i>Beispiel: 100</i>",
        'invalid_deposit': "❌ <b>Fehler!</b> Bitte geben Sie eine Zahl ein.",
        'ask_risk': "⚙️ <b>Wählen Sie das Risikoniveau:</b>\n\n🟢 Niedrig (1%)\n🟡 Mittel (2.5%)\n🔴 Hoch (5%)",
        'btn_risk_low': "🟢 Niedrig", 'btn_risk_med': "🟡 Mittel", 'btn_risk_high': "🔴 Hoch",
        'btn_main': "⬅️ Hauptmenü",
        'signal_title': "🎰 <b>Analyse abgeschlossen! Hot Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Taktik: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Schritt 1: Machen Sie <b>{spins1} Spins</b> bei <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Schritt 2: Wenn trocken — erhöhen Sie auf <b>{bet2}</b> und drehen Sie <b>{spins2} Mal</b>.\n",
        'signal_tactic_step3': "3️⃣ Schritt 3: Letzter Stoß: setzen Sie <b>{bet3}</b> und machen Sie <b>{spins3} Spins</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Viel Glück!",
        'left_signals': "💡 <i>Verbleibende Signale: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LIMIT ERREICHT!</b>\n\nLaden Sie einen Freund ein!",
        'instr_text': "📖 <b>WIE MAN BEGINNT:</b>\n\n1️⃣ <b>Registrieren:</b> <a href='{url}'>HIER KLICKEN</a>\n2️⃣ <b>Einzahlen.</b>\n3️⃣ <b>Spiel:</b> Slots.",
        'admin_panel': "⚙️ <b>ADMIN-PANEL</b>\n\n👑 Status: <b>GOD MODE</b>\n📊 Befehle: /top",
        'not_admin': "❌ Keine Rechte.",
        'support_text': "🆘 <b>Support</b>\n\n👉 <a href='tg://user?id={admin_id}'>Nachricht an Admin</a>",
        'ref_title': "🏆 <b>GEWINNSPIEL</b> 🏆\n\n1 Freund = 1 Ticket.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Tickets: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Freund registriert! +1 Ticket. Gesamt: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 Freunde eingeladen!</b> Zugang offen!"
    },
    'tr': {
        'welcome': "🎰 <b>GİZLİ SLOT VERİ TABANINA ERİŞİM VERİLDİ</b> 🎰\n\n<b>SLOT AI PREDICTOR</b>'a Hoş Geldiniz!\n\nPara yatırmaktan yoruldunuz mu? Sinir ağımız <b>Sıcak Slotları</b> bulur.\n\n1. Bankroll girin\n2. Risk seçin\n3. Yapay zeka slot ve taktik verir",
        'btn_reg': "💳 Kayıt Ol", 'btn_instr': "📖 Talimatlar", 'btn_sign': "🎰 Slot Al", 'btn_lang': "🌐 Dil", 'btn_ref': "👥 Yarışma", 'btn_support': "🆘 Destek",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Dil Türkçe olarak değiştirildi 🇹🇷",
        'need_reg': "⚠️ <b>ERİŞİM ENGELLENDİ!</b>\n\nAşağıdan kayıt olun:",
        'regged': "✅ <b>BAŞARILI!</b> 'Slot Al' butonuna tıklayın! 🚀",
        'ask_deposit': "💰 <b>Yatırım miktarınızı girin:</b>\n\n<i>Örnek: 100</i>",
        'invalid_deposit': "❌ <b>Hata!</b> Lütfen bir sayı girin.",
        'ask_risk': "⚙️ <b>Risk seviyesini seçin:</b>\n\n🟢 Düşük (%1)\n🟡 Orta (%2.5)\n🔴 Yüksek (%5)",
        'btn_risk_low': "🟢 Düşük", 'btn_risk_med': "🟡 Orta", 'btn_risk_high': "🔴 Yüksek",
        'btn_main': "⬅️ Ana Menü",
        'signal_title': "🎰 <b>Analiz Tamamlandı! Sıcak Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Taktik: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Adım 1: <b>{bet1}</b> değerinde <b>{spins1} çevirme</b> yapın.\n",
        'signal_tactic_step2': "2️⃣ Adım 2: Eğer kuruysa — <b>{bet2}</b> değerine yükseltin ve <b>{spins2} kez</b> çevirin.\n",
        'signal_tactic_step3': "3️⃣ Adım 3: Son hamle: <b>{bet3}</b> bahis yapın ve <b>{spins3} çevirme</b> yapın.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Bol şans!",
        'left_signals': "💡 <i>Kalan sinyaller: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>LİMİT DOLDU!</b>\n\nBir arkadaşını davet et!",
        'instr_text': "📖 <b>NASIL BAŞLARIM:</b>\n\n1️⃣ <b>Kayıt:</b> <a href='{url}'>BURAYA TIKLA</a>\n2️⃣ <b>Yatırım.</b>\n3️⃣ <b>Oyun:</b> Slotlar.",
        'admin_panel': "⚙️ <b>ADMİN PANELİ</b>\n\n👑 Durum: <b>GOD MODE</b>\n📊 Komutlar: /top",
        'not_admin': "❌ Yetkiniz yok.",
        'support_text': "🆘 <b>Destek</b>\n\n👉 <a href='tg://user?id={admin_id}'>Admin'e Mesaj At</a>",
        'ref_title': "🏆 <b>YARIŞMA</b> 🏆\n\n1 arkadaş = 1 bilet.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Biletler: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Arkadaş kayıt oldu! +1 bilet. Toplam: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 arkadaş davet edildi!</b> Erişim açık!"
    },
    'id': {
        'welcome': "🎰 <b>AKSES BASIS DATA SLOT RAHASIA DIBERIKAN</b> 🎰\n\nSelamat datang di <b>SLOT AI PREDICTOR</b>!\n\nLelah kehilangan deposit? Jaringan saraf kami menemukan <b>Hot Slots</b>.\n\n1. Masukkan bankroll\n2. Pilih risiko\n3. AI memberikan slot & taktik",
        'btn_reg': "💳 Daftar", 'btn_instr': "📖 Instruksi", 'btn_sign': "🎰 Dapatkan Slot", 'btn_lang': "🌐 Bahasa", 'btn_ref': "👥 Kontes", 'btn_support': "🆘 Dukungan",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "Bahasa diubah ke Indonesia 🇮🇩",
        'need_reg': "⚠️ <b>AKSES DIBLOKIR!</b>\n\nDaftar di bawah ini:",
        'regged': "✅ <b>SUKSES!</b> Klik 'Dapatkan Slot'! 🚀",
        'ask_deposit': "💰 <b>Masukkan jumlah deposit Anda:</b>\n\n<i>Contoh: 100</i>",
        'invalid_deposit': "❌ <b>Kesalahan!</b> Silakan masukkan angka.",
        'ask_risk': "⚙️ <b>Pilih tingkat risiko:</b>\n\n🟢 Rendah (1%)\n🟡 Sedang (2.5%)\n🔴 Tinggi (5%)",
        'btn_risk_low': "🟢 Rendah", 'btn_risk_med': "🟡 Sedang", 'btn_risk_high': "🔴 Tinggi",
        'btn_main': "⬅️ Menu Utama",
        'signal_title': "🎰 <b>Analisis Selesai! Hot Slot:</b>\n\n",
        'signal_slot': "🔥 Slot: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>Taktik: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ Langkah 1: Lakukan <b>{spins1} putaran</b> pada <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ Langkah 2: Jika kering — naikkan ke <b>{bet2}</b> dan putar <b>{spins2} kali</b>.\n",
        'signal_tactic_step3': "3️⃣ Langkah 3: Dorongan akhir: bertaruh <b>{bet3}</b> dan lakukan <b>{spins3} putaran</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}Semoga berhasil!",
        'left_signals': "💡 <i>Sinyal tersisa: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>BATAS TERCAPAI!</b>\n\nUndang teman!",
        'instr_text': "📖 <b>CARA MEMULAI:</b>\n\n1️⃣ <b>Daftar:</b> <a href='{url}'>KLIK DI SINI</a>\n2️⃣ <b>Deposit.</b>\n3️⃣ <b>Game:</b> Slots.",
        'admin_panel': "⚙️ <b>PANEL ADMIN</b>\n\n👑 Status: <b>GOD MODE</b>\n📊 Perintah: /top",
        'not_admin': "❌ Tidak ada hak.",
        'support_text': "🆘 <b>Dukungan</b>\n\n👉 <a href='tg://user?id={admin_id}'>Pesan Admin</a>",
        'ref_title': "🏆 <b>KONTES</b> 🏆\n\n1 teman = 1 tiket.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 Tiket: <b>{count}</b>\n\n🔗 Link:\n<code>{link}</code>",
        'ref_notify': "🎉 Teman terdaftar! +1 tiket. Total: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 teman diundang!</b> Akses terbuka!"
    },
    'hi': {
        'welcome': "🎰 <b>गुप्त स्लॉट डेटाबेस तक पहुंच प्रदान की गई</b> 🎰\n\n<b>SLOT AI PREDICTOR</b> में आपका स्वागत है!\n\nजमा राशि खोने से थक गए? हमारा न्यूरल नेटवर्क <b>हॉट स्लॉट</b> ढूंढता है।\n\n1. बैंकरोल दर्ज करें\n2. जोखिम चुनें\n3. AI स्लॉट और रणनीति देगा",
        'btn_reg': "💳 पंजीकरण करें", 'btn_instr': "📖 निर्देश", 'btn_sign': "🎰 स्लॉट प्राप्त करें", 'btn_lang': "🌐 भाषा", 'btn_ref': "👥 प्रतियोगिता", 'btn_support': "🆘 सहायता",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "भाषा हिंदी में बदल गई 🇮🇳",
        'need_reg': "⚠️ <b>पहुंच अवरुद्ध!</b>\n\nनीचे पंजीकरण करें:",
        'regged': "✅ <b>सफलता!</b> 'स्लॉट प्राप्त करें' पर क्लिक करें! 🚀",
        'ask_deposit': "💰 <b>अपनी जमा राशि दर्ज करें:</b>\n\n<i>उदाहरण: 100</i>",
        'invalid_deposit': "❌ <b>त्रुटि!</b> कृपया एक संख्या दर्ज करें।",
        'ask_risk': "⚙️ <b>जोखिम स्तर चुनें:</b>\n\n🟢 कम (1%)\n🟡 मध्यम (2.5%)\n🔴 उच्च (5%)",
        'btn_risk_low': "🟢 कम", 'btn_risk_med': "🟡 मध्यम", 'btn_risk_high': "🔴 उच्च",
        'btn_main': "⬅️ मुख्य मेनू",
        'signal_title': "🎰 <b>विश्लेषण पूरा! हॉट स्लॉट:</b>\n\n",
        'signal_slot': "🔥 स्लॉट: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>रणनीति: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ चरण 1: <b>{bet1}</b> पर <b>{spins1} स्पिन</b> करें।\n",
        'signal_tactic_step2': "2️⃣ चरण 2: यदि खाली है — <b>{bet2}</b> तक बढ़ाएं और <b>{spins2} बार</b> स्पिन करें।\n",
        'signal_tactic_step3': "3️⃣ चरण 3: अंतिम दबाव: <b>{bet3}</b> दांव लगाएं और <b>{spins3} स्पिन</b> करें।\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}शुभकामनाएं!",
        'left_signals': "💡 <i>शेष सिग्नल: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>सीमा समाप्त!</b>\n\nदोस्त को आमंत्रित करें!",
        'instr_text': "📖 <b>कैसे शुरू करें:</b>\n\n1️⃣ <b>पंजीकरण:</b> <a href='{url}'>यहाँ क्लिक करें</a>\n2️⃣ <b>जमा।</b>\n3️⃣ <b>गेम:</b> स्लॉट।",
        'admin_panel': "⚙️ <b>एडमिन पैनल</b>\n\n👑 स्थिति: <b>GOD MODE</b>\n📊 कमांड: /top",
        'not_admin': "❌ कोई अधिकार नहीं।",
        'support_text': "🆘 <b>सहायता</b>\n\n👉 <a href='tg://user?id={admin_id}'>एडमिन को संदेश</a>",
        'ref_title': "🏆 <b>प्रतियोगिता</b> 🏆\n\n1 दोस्त = 1 टिकट।\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 टिकट: <b>{count}</b>\n\n🔗 लिंक:\n<code>{link}</code>",
        'ref_notify': "🎉 दोस्त पंजीकृत! +1 टिकट। कुल: <b>{count}</b>।",
        'ref_success': "🔥 <b>3 दोस्त आमंत्रित!</b> पहुंच खुली!"
    },
    'ar': {
        'welcome': "🎰 <b>تم منح الوصول إلى قاعدة بيانات الفتحات السرية</b> 🎰\n\nمرحبًا بك في <b>SLOT AI PREDICTOR</b>!\n\nسئمت من خسارة الودائع؟ شبكتنا العصبية تجد <b>الفتحات الساخنة</b>.\n\n1. أدخل رصيدك\n2. اختر المخاطر\n3. سيعطيك الذكاء الاصطناعي الفتحة والتكتيك",
        'btn_reg': "💳 التسجيل", 'btn_instr': "📖 تعليمات", 'btn_sign': "🎰 الحصول على فتحة", 'btn_lang': "🌐 اللغة", 'btn_ref': "👥 مسابقة", 'btn_support': "🆘 الدعم",
        'choose_lang': "🌐 Выберите язык / Choose language:",
        'lang_set': "تم تغيير اللغة إلى العربية 🇸🇦",
        'need_reg': "⚠️ <b>تم حظر الوصول!</b>\n\nسجل أدناه:",
        'regged': "✅ <b>نجاح!</b> انقر على 'الحصول على فتحة'! 🚀",
        'ask_deposit': "💰 <b>أدخل مبلغ الإيداع الخاص بك:</b>\n\n<i>مثال: 100</i>",
        'invalid_deposit': "❌ <b>خطأ!</b> يرجى إدخال رقم.",
        'ask_risk': "⚙️ <b>اختر مستوى المخاطرة:</b>\n\n🟢 منخفض (1%)\n🟡 متوسط (2.5%)\n🔴 مرتفع (5%)",
        'btn_risk_low': "🟢 منخفض", 'btn_risk_med': "🟡 متوسط", 'btn_risk_high': "🔴 مرتفع",
        'btn_main': "⬅️ القائمة الرئيسية",
        'signal_title': "🎰 <b>اكتمل التحليل! فتحة ساخنة:</b>\n\n",
        'signal_slot': "🔥 فتحة: <b>{slot}</b>\n\n",
        'signal_tactic_title': "📊 <b>تكتيك: {tactic_name}</b>\n",
        'signal_tactic_step1': "1️⃣ الخطوة 1: قم بـ <b>{spins1} دورة</b> عند <b>{bet1}</b>.\n",
        'signal_tactic_step2': "2️⃣ الخطوة 2: إذا كانت جافة — ارفع إلى <b>{bet2}</b> وقم بالتدوير <b>{spins2} مرات</b>.\n",
        'signal_tactic_step3': "3️⃣ الخطوة 3: الدفعة النهائية: راهن بـ <b>{bet3}</b> وقم بـ <b>{spins3} دورة</b>.\n",
        'signal_footer': "\n💡 <i>{tip}</i>\n\n{left}حظا سعيدا!",
        'left_signals': "💡 <i>الإشارات المتبقية: {left}</i>\n\n",
        'limit_msg': "⚠️ <b>تم الوصول إلى الحد الأقصى!</b>\n\nادعو صديقًا!",
        'instr_text': "📖 <b>كيف تبدأ:</b>\n\n1️⃣ <b>التسجيل:</b> <a href='{url}'>انقر هنا</a>\n2️⃣ <b>إيداع.</b>\n3️⃣ <b>لعبة:</b> فتحات.",
        'admin_panel': "⚙️ <b>لوحة المسؤول</b>\n\n👑 الحالة: <b>GOD MODE</b>\n📊 أوامر: /top",
        'not_admin': "❌ لا حقوق.",
        'support_text': "🆘 <b>الدعم</b>\n\n👉 <a href='tg://user?id={admin_id}'>مراسلة المسؤول</a>",
        'ref_title': "🏆 <b>مسابقة</b> 🏆\n\n1 صديق = 1 تذكرة.\n🥇 $100\n🥈 $50\n🥉 $20\n\n📊 تذاكر: <b>{count}</b>\n\n🔗 رابط:\n<code>{link}</code>",
        'ref_notify': "🎉 صديق مسجل! +1 تذكرة. الإجمالي: <b>{count}</b>.",
        'ref_success': "🔥 <b>3 أصدقاء مدعوون!</b> الوصول مفتوح!"
    }
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("slots")

class SlotState(StatesGroup):
    waiting_for_deposit = State()
    waiting_for_risk = State()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY, postback_id TEXT, language TEXT DEFAULT 'ru', referrer_id INTEGER, daily_signals INTEGER DEFAULT 0, last_signal_date TEXT, total_deposit REAL DEFAULT 0)")
        conn.commit()
        for col, typ in [("language", "TEXT DEFAULT 'ru'"), ("referrer_id", "INTEGER"), ("daily_signals", "INTEGER DEFAULT 0"), ("last_signal_date", "TEXT"), ("total_deposit", "REAL DEFAULT 0")]:
            try: conn.execute(f"ALTER TABLE user ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError: pass

def get_user(uid: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT postback_id, language, referrer_id, daily_signals, last_signal_date, total_deposit FROM user WHERE user_id = ?", (uid,)).fetchone()
        if row:
            lang = row[1] if row[1] in LANG else 'ru'
            ref_count = conn.execute("SELECT COUNT(*) FROM user WHERE referrer_id = ? AND postback_id IS NOT NULL AND postback_id != 'null'", (uid,)).fetchone()[0]
            return {"user_id": uid, "postback_id": row[0], "lang": lang, "referrer_id": row[2], "ref_count": ref_count, "daily_signals": row[3] or 0, "last_signal_date": row[4], "total_deposit": row[5] or 0}
    return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True))
dp = Dispatcher(storage=MemoryStorage())

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="🇵🇹 Português", callback_data="set_lang_pt"), InlineKeyboardButton(text="🇪🇸 Español", callback_data="set_lang_es")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="set_lang_fr"), InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="set_lang_de")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="set_lang_tr"), InlineKeyboardButton(text="🇮🇩 Indonesia", callback_data="set_lang_id")],
        [InlineKeyboardButton(text="🇮🇳 हिंदी", callback_data="set_lang_hi"), InlineKeyboardButton(text="🇸🇦 العربية", callback_data="set_lang_ar")]
    ])

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

def risk_menu(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_low'], callback_data="set_risk_low")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_med'], callback_data="set_risk_med")],
        [InlineKeyboardButton(text=LANG[lang]['btn_risk_high'], callback_data="set_risk_high")],
        [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]
    ])

def sign_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LANG[lang]['btn_sign'], callback_data="sign")], [InlineKeyboardButton(text=LANG[lang]['btn_main'], callback_data="main_menu")]])

def generate_slot_signal(lang, deposit, risk_level, signals_left_str):
    slots = ["Sweet Bonanza", "Gates of Olympus", "The Dog House", "Sugar Rush", "Big Bass Bonanza", "Money Train 3", "San Quentin"]
    
    tactics = {
        'martingale': {
            'ru': ("Мартингейл", "Поймал бонус — вернись к Шагу 1."), 'en': ("Martingale", "Catch bonus — reset to Step 1."),
            'pt': ("Martingale", "Pegue o bônus — volte ao Passo 1."), 'es': ("Martingala", "Atrapa el bono — vuelve al Paso 1."),
            'fr': ("Martingale", "Attrapez le bonus — revenez à l'étape 1."), 'de': ("Martingale", "Bonus gefangen — zurück zu Schritt 1."),
            'tr': ("Martingale", "Bonusu yakala — 1. Adıma dön."), 'id': ("Martingale", "Tangkap bonus — kembali ke Langkah 1."),
            'hi': ("मार्टिंगेल", "बोनस पकड़ें — चरण 1 पर लौटें।"), 'ar': ("مارتينجال", "احصل على المكافأة — عد إلى الخطوة 1.")
        },
        'ladder': {
            'ru': ("Лесенка", "Плавный подъем. 3 шага в минус — меняй слот."), 'en': ("Ladder", "Smooth increase. 3 dry steps — change slot."),
            'pt': ("Escada", "Aumento suave. 3 passos secos — mude o slot."), 'es': ("Escalera", "Aumento suave. 3 pasos secos — cambia de slot."),
            'fr': ("Échelle", "Augmentation régulière. 3 étapes sèches — changez de slot."), 'de': ("Leiter", "Sanfte Erhöhung. 3 trockene Schritte — Slot wechseln."),
            'tr': ("Merdiven", "Kademeli artış. 3 kuru adım — slotu değiştir."), 'id': ("Tangga", "Peningkatan bertahap. 3 langkah kering — ganti slot."),
            'hi': ("सीढ़ी", "सुचारू वृद्धि। 3 सूखे कदम — स्लॉट बदलें।"), 'ar': ("سلم", "زيادة سلسة. 3 خطوات جافة — قم بتغيير الفتحة.")
        },
        'sniper': {
            'ru': ("Снайпер", "Быстрый занос. Пусто — уходи."), 'en': ("Sniper", "Quick push. Dry — leave."),
            'pt': ("Sniper", "Push rápido. Seco — saia."), 'es': ("Francotirador", "Empuje rápido. Seco — sal."),
            'fr': ("Sniper", "Poussée rapide. Sec — partez."), 'de': ("Sniper", "Schneller Vorstoß. Trocken — gehen."),
            'tr': ("Keskin Nişancı", "Hızlı hamle. Kuru — ayrıl."), 'id': ("Sniper", "Dorongan cepat. Kering — pergi."),
            'hi': ("स्नाइपर", "त्वरित धक्का। सूखा — छोड़ दें।"), 'ar': ("قناص", "دفعة سريعة. جاف — اترك.")
        }
    }
    
    slot = random.choice(slots)
    if risk_level == "low": base_pct = 0.01
    elif risk_level == "high": base_pct = 0.05
    else: base_pct = 0.025
    
    bet1 = round(deposit * base_pct, 2)
    if bet1 < 1: bet1 = 1
    
    tactic_key = random.choice(list(tactics.keys()))
    t_name, t_tip = tactics[tactic_key].get(lang, tactics[tactic_key]['en'])
    
    if tactic_key == 'martingale': bet2, bet3, spins1, spins2, spins3 = round(bet1*2, 2), round(bet1*4, 2), 10, 5, 3
    elif tactic_key == 'ladder': bet2, bet3, spins1, spins2, spins3 = round(bet1*1.5, 2), round(bet1*2, 2), 15, 10, 5
    else: bet2, bet3, spins1, spins2, spins3 = bet1, bet1, 5, 5, 5
        
    title = LANG[lang]['signal_title']
    slot_text = LANG[lang]['signal_slot'].format(slot=slot)
    t_title = LANG[lang]['signal_tactic_title'].format(tactic_name=t_name)
    
    if tactic_key == 'sniper':
        step1 = LANG[lang]['signal_tactic_step1'].format(spins1=spins1, bet1=bet1)
        step2 = LANG[lang]['signal_tactic_step2'].format(spins2=spins2, bet2=bet1)
        step3 = LANG[lang]['signal_tactic_step3'].format(spins3=spins3, bet3=bet1)
    else:
        step1 = LANG[lang]['signal_tactic_step1'].format(spins1=spins1, bet1=bet1)
        step2 = LANG[lang]['signal_tactic_step2'].format(spins2=spins2, bet2=bet2)
        step3 = LANG[lang]['signal_tactic_step3'].format(spins3=spins3, bet3=bet3)
        
    footer = LANG[lang]['signal_footer'].format(tip=t_tip, left=signals_left_str)
    return f"{title}{slot_text}{t_title}{step1}{step2}{step3}{footer}"

def get_fake_win(lang='ru'):
    names = ["Alex", "Max", "Ivan", "Favour", "Joyce", "Murilo", "Lucas", "Gabriel", "Ahmet", "Budi"]
    name = random.choice(names)
    win = random.randint(500, 85000)
    mult = round(random.uniform(1.2, 9.5), 2)
    if lang in ['ru', 'ar']: curr = "₽"
    else: curr = "$"
    
    return f"🔥 <i>{name} just cashed out {curr}{win:,} in Slots (x{mult})!</i>"

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
    welcome_text = f"{LANG[lang]['welcome']}\n\n{get_fake_win(lang)}"
    await call.message.edit_text(welcome_text, reply_markup=main_menu(lang))

@dp.callback_query(F.data == "main_menu")
async def cb_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    u = get_user(call.from_user.id); lang = u['lang'] if u else 'ru'
    welcome_text = f"{LANG[lang]['welcome']}\n\n{get_fake_win(lang)}"
    await call.message.edit_text(welcome_text, reply_markup=main_menu(lang)); await call.answer()

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
    is_registered = u and u['postback_id'] and u['postback_id'].lower() != "null"
    
    if not u or (not is_registered and u['ref_count'] < 3):
        lang = u['lang'] if u else 'ru'
        await call.message.answer(LANG[lang]['need_reg'], reply_markup=reg_kb(call.from_user.id, lang))
        await call.answer()
        return
    
    lang = u['lang']
    today = datetime.date.today().isoformat()
    daily = 0 if u['last_signal_date'] != today else u['daily_signals']
    is_admin = (str(call.from_user.id) == str(ADMIN_ID))
    
    if not is_admin and daily >= 5:
        await call.answer("⚠️ Limit reached!", show_alert=True)
        await call.message.answer(LANG[lang]['limit_msg'].format(limit=5))
        return
        
    await call.message.edit_text(LANG[lang]['ask_deposit'])
    await state.set_state(SlotState.waiting_for_deposit)
    await state.update_data(lang=lang, daily=daily, is_admin=is_admin)
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
    await message.answer(LANG[lang]['ask_risk'], reply_markup=risk_menu(lang))
    await state.set_state(SlotState.waiting_for_risk)

@dp.callback_query(SlotState.waiting_for_risk, F.data.startswith("set_risk_"))
async def process_risk(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru'); deposit = data.get('deposit', 100)
    daily = data.get('daily', 0); is_admin = data.get('is_admin', False)
    
    today = datetime.date.today().isoformat()
    if not is_admin:
        daily += 1
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE user SET daily_signals = ?, last_signal_date = ? WHERE user_id = ?", (daily, today, call.from_user.id)); conn.commit()
        signals_left_str = LANG[lang]['left_signals'].format(left=5 - daily)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE user SET last_signal_date = ? WHERE user_id = ?", (today, call.from_user.id)); conn.commit()
        signals_left_str = "💡 <i>Signals left: ∞ (God Mode)</i>\n\n"
    
    signal_text = generate_slot_signal(lang, deposit, call.data.split("_")[-1], signals_left_str)
    await call.message.edit_text(text=signal_text, reply_markup=sign_kb(lang))
    await call.answer(); await state.clear()

@dp.message(Command("admin"))
async def cmd_adm(msg: types.Message):
    u = get_user(msg.from_user.id); lang = u['lang'] if u else 'ru'
    if str(msg.from_user.id) == str(ADMIN_ID): await msg.answer(LANG[lang]['admin_panel'])
    else: await msg.answer(LANG[lang]['not_admin'])

@dp.message(Command("top"))
async def cmd_top(msg: types.Message):
    if str(msg.from_user.id) != ADMIN_ID: return
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT u1.user_id, COUNT(u2.user_id) FROM user u1 JOIN user u2 ON u1.user_id = u2.referrer_id WHERE u2.postback_id IS NOT NULL GROUP BY u1.user_id ORDER BY 2 DESC LIMIT 10").fetchall()
    text = "🏆 <b>TOP-10</b>\n\n" + "".join([f"{i}. ID: <code>{r[0]}</code> — <b>{r[1]} tickets</b>\n" for i, r in enumerate(rows, 1)]) if rows else "No referrals."
    await msg.answer(text)

# ============================================================
# ВСТРОЕННЫЙ ВЕБ-СЕРВЕР ДЛЯ ПОСТБЕКОВ И API
# ============================================================
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/health': self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok": true}'); return
        
        if p.path == '/api/stats':
            with sqlite3.connect(DB_PATH) as conn:
                total = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
                regs = conn.execute("SELECT COUNT(*) FROM user WHERE postback_id IS NOT NULL AND postback_id != 'null'").fetchone()[0]
                total_deposit = conn.execute("SELECT SUM(total_deposit) FROM user").fetchone()[0] or 0
                recent = conn.execute("SELECT user_id, postback_id FROM user WHERE postback_id IS NOT NULL ORDER BY rowid DESC LIMIT 10").fetchall()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"total": total, "regs": regs, "deposit": total_deposit, "recent": recent}).encode())
            return

        if p.path == '/postback':
            q = urllib.parse.parse_qs(p.query)
            s1 = q.get('sub1',[''])[0]
            s2 = q.get('subid',[''])[0]
            amount_str = q.get('amount',['0'])[0]
            
            if not s1 or not s2: self.send_response(400); self.end_headers(); return
            try: 
                uid = int(s1)
                amount = float(amount_str) if amount_str else 0.0
            except: self.send_response(400); self.end_headers(); return
            
            with sqlite3.connect(DB_PATH) as conn: 
                conn.execute("INSERT INTO user (user_id, postback_id, total_deposit) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET postback_id = excluded.postback_id, total_deposit = user.total_deposit + excluded.total_deposit", (uid, s2, amount))
                conn.commit()
            
            u = get_user(uid); lang = u['lang'] if u else 'ru'
            
            try:
                msg_text = LANG[lang]['regged']
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={uid}&text={urllib.parse.quote(msg_text)}&parse_mode=HTML"
                req = urllib.request.urlopen(url, timeout=10)
                log.info(f"Telegram API response for {uid}: {req.read().decode()}")
            except urllib.error.HTTPError as e:
                if e.code == 400: log.warning(f"User {uid} didn't press /start.")
                else: log.error(f"SEND ERROR FOR {uid}: {e}")
            except Exception as e:
                log.error(f"SEND ERROR FOR {uid}: {e}")
            
            if u and u.get('referrer_id'):
                r_u = get_user(u['referrer_id'])
                if r_u:
                    t = LANG[r_u['lang']]['ref_success'] if r_u['ref_count'] >= 3 else LANG[r_u['lang']]['ref_notify'].format(count=r_u['ref_count'])
                    try: 
                        ref_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={r_u['user_id']}&text={urllib.parse.quote(t)}&parse_mode=HTML"
                        urllib.request.urlopen(ref_url, timeout=5)
                    except: pass
                    
            self.send_response(200); self.end_headers(); self.wfile.write(f"sub1={s1}; subid={s2}; amount={amount}; OK".encode('utf-8')); return
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