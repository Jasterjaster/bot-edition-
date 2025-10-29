import time
import threading
import os
import base64
import uuid

# --- استيراد أدوات تيليجرام والخدمات الخارجية ---
import telegram_utils as tg
import services

# --- الإعدادات العامة ---
# لتتبع الحالة الحالية لكل مستخدم (ماذا ينتظر البوت منهم أن يفعلوا)
USER_STATES = {} 
# لتتبع مهام الفيديو القابلة للإلغاء
ACTIVE_VIDEO_JOBS = {} 


# --- لوحات المفاتيح (Keyboards) ---
MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🖼️ إنشاء صورة", "callback_data": "generate_image"}, {"text": "✨ تحسين الوصف (Prompt)", "callback_data": "enhance_prompt"}],
        [{"text": "📄 وصف صورة", "callback_data": "describe_image"}, {"text": "🎨 تعديل آخر صورة", "callback_data": "edit_last_image"}],
        [{"text": "🎞️ إنشاء فيديو", "callback_data": "create_video"}]
    ]
}

VIDEO_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🎬 من نص", "callback_data": "video_from_text"}, {"text": "🖼️ من آخر صورة", "callback_data": "video_from_image"}],
        [{"text": "⬅️ عودة للقائمة الرئيسية", "callback_data": "back_to_main"}]
    ]
}

# --- دوال العمال (Workers) - تم تعديلها لتكون احترافية ---
def image_generation_worker(chat_id, message_id, image_prompt, session, waiting_message_id):
    tg.send_chat_action(chat_id, "upload_photo")
    image_urls = services.generate_image_from_prompt(image_prompt)
    
    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)

    if image_urls:
        photo_message = tg.send_photo(chat_id, image_urls[0], caption=f"تم إنشاء الصورة بنجاح.\n\n📝 الوصف: {image_prompt}", reply_to_message_id=message_id)

        if photo_message and photo_message.get('ok'):
            sent_message = photo_message['result']
            photo_file_id = sent_message['photo'][-1]['file_id']
            sent_message_id = sent_message['message_id']

            keyboard = {"inline_keyboard": [[{"text": "🎨 تعديل هذه الصورة", "callback_data": f"edit_image:{photo_file_id}"}]]}
            tg.edit_message_reply_markup(chat_id, sent_message_id, keyboard)
            session['last_image_file_id'] = photo_file_id
    else:
        tg.send_message(chat_id, "حدث خطأ أثناء إنشاء الصورة. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)


def edit_image_worker(chat_id, message_id, image_file_id, edit_prompt, session, waiting_message_id):
    tg.send_chat_action(chat_id, "upload_photo")
    file_path = tg.get_file_path(image_file_id)
    if not file_path:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: لم أتمكن من تحميل الصورة من تيليجرام.", reply_to_message_id=message_id); return
    
    original_image_data = tg.SESSION.get(f"https://api.telegram.org/file/bot{tg.BOT_TOKEN}/{file_path}").content
    uploaded_url = services.upload_image_for_editing(original_image_data)
    if not uploaded_url:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: فشل رفع الصورة لخدمة التعديل.", reply_to_message_id=message_id); return
    
    job_id = services.start_image_editing_job(uploaded_url, edit_prompt)
    if not job_id:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: فشل بدء مهمة تعديل الصورة.", reply_to_message_id=message_id); return
    
    final_image_url = services.poll_for_editing_result(job_id)

    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
    
    if final_image_url:
        photo_message = tg.send_photo(chat_id, final_image_url, caption=f"تم تعديل الصورة بنجاح.\n\n📝 تعليمات التعديل: {edit_prompt}", reply_to_message_id=message_id)
        
        if photo_message and photo_message.get('ok'):
            sent_message = photo_message['result']
            photo_file_id = sent_message['photo'][-1]['file_id']
            sent_message_id = sent_message['message_id']
            
            keyboard = {"inline_keyboard": [[{"text": "🎨 تعديل هذه الصورة", "callback_data": f"edit_image:{photo_file_id}"}]]}
            tg.edit_message_reply_markup(chat_id, sent_message_id, keyboard)
            session['last_image_file_id'] = photo_file_id
    else:
        tg.send_message(chat_id, "فشل تعديل الصورة. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)


def describe_image_worker(chat_id, message_id, file_id, waiting_message_id):
    tg.send_chat_action(chat_id, "typing")
    file_path = tg.get_file_path(file_id)
    if not file_path:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: لم أتمكن من تحميل الصورة.", reply_to_message_id=message_id); return

    image_base64 = tg.download_image_as_base64(file_path)
    if not image_base64:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: فشل في معالجة بيانات الصورة.", reply_to_message_id=message_id); return

    description, _ = services.describe_image_with_gemini(image_base64)
    
    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
    tg.send_message(chat_id, f"**وصف الصورة:**\n\n{description}", reply_to_message_id=message_id)

def enhance_prompt_worker(chat_id, message_id, simple_prompt, waiting_message_id):
    tg.send_chat_action(chat_id, "typing")
    enhanced_prompt, _ = services.generate_enhanced_prompt(simple_prompt)
    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
    tg.send_message(chat_id, f"**الوصف المحسّن (Prompt):**\n\n`{enhanced_prompt}`\n\nيمكنك الآن نسخ هذا الوصف واستخدامه في 'إنشاء صورة'.", reply_to_message_id=message_id)


def text_to_video_worker(chat_id, message_id, video_prompt):
    job_id = str(uuid.uuid4())
    cancel_event = threading.Event()
    ACTIVE_VIDEO_JOBS[job_id] = cancel_event
    
    keyboard = {"inline_keyboard": [[{"text": "❌ إلغاء", "callback_data": f"cancel_video:{job_id}"}]]}
    status_msg = tg.send_message(chat_id, "تم استلام الطلب 🎬\nجاري إنشاء الفيديو... قد تستغرق العملية عدة دقائق.", reply_to_message_id=message_id, reply_markup=keyboard)
    status_message_id = status_msg['result']['message_id']
    
    try:
        tg.send_chat_action(chat_id, "upload_video")
        generation_info = services.start_text_to_video_job(video_prompt)
        if not generation_info:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: فشل بدء مهمة إنشاء الفيديو.")
            return

        video_url = services.poll_for_video_result(generation_info['request_id'], generation_info['history_id'], cancel_event)

        if video_url == "CANCELLED":
            tg.edit_message_text(chat_id, status_message_id, "تم إلغاء عملية إنشاء الفيديو.")
        elif video_url:
            tg.edit_message_text(chat_id, status_message_id, "اكتمل إنشاء الفيديو! جاري الإرسال...")
            tg.send_video(chat_id, video_url, caption=f"فيديو من النص:\n\n📝: {video_prompt}", reply_to_message_id=message_id)
            tg.delete_message(chat_id, status_message_id)
        else:
            tg.edit_message_text(chat_id, status_message_id, "فشلت عملية إنشاء الفيديو أو استغرقت وقتاً طويلاً.")
    finally:
        if job_id in ACTIVE_VIDEO_JOBS:
            del ACTIVE_VIDEO_JOBS[job_id]

def image_to_video_worker(chat_id, message_id, video_prompt, session):
    image_to_process_id = session.get('last_image_file_id')
    if not image_to_process_id:
        tg.send_message(chat_id, "لم يتم العثور على صورة سابقة. يرجى إرسال صورة أولاً.", reply_to_message_id=message_id)
        return

    job_id = str(uuid.uuid4())
    cancel_event = threading.Event()
    ACTIVE_VIDEO_JOBS[job_id] = cancel_event

    keyboard = {"inline_keyboard": [[{"text": "❌ إلغاء", "callback_data": f"cancel_video:{job_id}"}]]}
    status_msg = tg.send_message(chat_id, "تم استلام الطلب 🤸‍♀️\nجاري تحريك الصورة... قد تستغرق العملية عدة دقائق.", reply_to_message_id=message_id, reply_markup=keyboard)
    status_message_id = status_msg['result']['message_id']

    try:
        file_path = tg.get_file_path(image_to_process_id)
        if not file_path:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: لم أتمكن من تحميل الصورة من تيليجرام."); return

        image_bytes = tg.download_image_as_bytes(file_path)
        if not image_bytes:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: حدث خطأ أثناء تحميل بيانات الصورة."); return

        upload_info = services.upload_image_for_video(image_bytes, f"{uuid.uuid4()}.jpg")
        if not upload_info:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: فشل رفع الصورة لخدمة الفيديو."); return
        
        tg.send_chat_action(chat_id, "upload_video")
        generation_info = services.start_image_to_video_job(video_prompt, upload_info['cdnUrl'], upload_info['uploadId'])
        if not generation_info:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: فشل بدء مهمة تحريك الصورة."); return

        video_url = services.poll_for_video_result(generation_info['request_id'], generation_info['history_id'], cancel_event)

        if video_url == "CANCELLED":
            tg.edit_message_text(chat_id, status_message_id, "تم إلغاء عملية إنشاء الفيديو.")
        elif video_url:
            tg.edit_message_text(chat_id, status_message_id, "اكتمل إنشاء الفيديو! جاري الإرسال...")
            tg.send_video(chat_id, video_url, caption=f"فيديو من صورة:\n\n📝: {video_prompt}", reply_to_message_id=message_id)
            tg.delete_message(chat_id, status_message_id)
        else:
            tg.edit_message_text(chat_id, status_message_id, "فشلت عملية تحريك الصورة أو استغرقت وقتاً طويلاً.")
    finally:
        if job_id in ACTIVE_VIDEO_JOBS:
            del ACTIVE_VIDEO_JOBS[job_id]


# --- المنطق الرئيسي للبوت ---
def process_update(update, chat_sessions):
    
    if 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = str(callback_query['message']['chat']['id'])
        message_id = callback_query['message']['message_id']
        callback_id = callback_query['id']
        data = callback_query['data']
        session = chat_sessions.setdefault(chat_id, {"history": [], "last_image_file_id": None})

        tg.answer_callback_query(callback_id)

        if data == 'generate_image':
            USER_STATES[chat_id] = 'awaiting_image_prompt'
            tg.send_message(chat_id, "يرجى إرسال الوصف (prompt) لإنشاء الصورة.")
        elif data == 'enhance_prompt':
            USER_STATES[chat_id] = 'awaiting_simple_prompt'
            tg.send_message(chat_id, "يرجى إرسال فكرة بسيطة، وسأقوم بتحويلها إلى وصف احترافي (prompt).")
        elif data == 'describe_image':
            USER_STATES[chat_id] = 'awaiting_image_for_description'
            tg.send_message(chat_id, "يرجى إرسال الصورة التي تريد وصفها.")
        elif data == 'edit_last_image':
            if session.get('last_image_file_id'):
                USER_STATES[chat_id] = 'awaiting_edit_prompt'
                tg.send_message(chat_id, "يرجى إرسال تعليمات التعديل على آخر صورة تم إنشاؤها.")
            else:
                tg.send_message(chat_id, "لم يتم العثور على صورة سابقة. يرجى إنشاء صورة أولاً.")
        elif data.startswith("edit_image:"):
            file_id = data.split(":", 1)[1]
            session['last_image_file_id'] = file_id
            USER_STATES[chat_id] = 'awaiting_edit_prompt'
            tg.send_message(chat_id, "يرجى إرسال تعليمات التعديل لهذه الصورة.")
        elif data == 'create_video':
            tg.edit_message_text(chat_id, message_id, "اختر نوع الفيديو:", reply_markup=VIDEO_KEYBOARD)
        elif data == 'video_from_text':
            USER_STATES[chat_id] = 'awaiting_video_prompt_text'
            tg.edit_message_text(chat_id, message_id, "يرجى إرسال الوصف (prompt) لإنشاء الفيديو.")
        elif data == 'video_from_image':
             if session.get('last_image_file_id'):
                USER_STATES[chat_id] = 'awaiting_video_prompt_image'
                tg.edit_message_text(chat_id, message_id, "يرجى إرسال وصف للحركة التي تريد إضافتها لآخر صورة.")
             else:
                tg.edit_message_text(chat_id, message_id, "لم يتم العثور على صورة سابقة. يرجى إنشاء صورة أولاً ثم العودة.", reply_markup=MAIN_KEYBOARD)
        elif data == 'back_to_main':
            tg.edit_message_text(chat_id, message_id, "القائمة الرئيسية:", reply_markup=MAIN_KEYBOARD)
        elif data.startswith("cancel_video:"):
            job_id = data.split(":", 1)[1]
            if job_id in ACTIVE_VIDEO_JOBS:
                ACTIVE_VIDEO_JOBS[job_id].set()
        return

    if 'message' not in update: return
    message = update['message']
    
    if message['chat']['type'] != 'private' or message.get('from', {}).get('is_bot'): return

    chat_id = str(message['chat']['id'])
    message_id = message['message_id']
    session = chat_sessions.setdefault(chat_id, {"history": [], "last_image_file_id": None})
    current_state = USER_STATES.get(chat_id)
    
    # التعامل مع الأوامر النصية الأساسية
    prompt = (message.get('text') or message.get('caption', '')).strip()
    if prompt.lower() == '/start':
        USER_STATES.pop(chat_id, None)
        session['history'] = []
        session['last_image_file_id'] = None
        tg.send_message(chat_id, "أهلاً بك. اختر إحدى الخدمات من القائمة:", reply_markup=MAIN_KEYBOARD)
        return
        
    if prompt.lower() == '/clear':
        USER_STATES.pop(chat_id, None)
        session['history'] = []
        session['last_image_file_id'] = None
        tg.send_message(chat_id, "تم مسح الذاكرة والحالة. للبدء من جديد اضغط /start", reply_to_message_id=message_id)
        return

    # توجيه الرسالة بناءً على حالة المستخدم
    if current_state == 'awaiting_image_prompt':
        USER_STATES.pop(chat_id, None)
        sent_msg = tg.send_message(chat_id, "جاري إنشاء الصورة...", reply_to_message_id=message_id)
        waiting_message_id = sent_msg.get('result', {}).get('message_id')
        threading.Thread(target=image_generation_worker, args=(chat_id, message_id, prompt, session, waiting_message_id)).start()
    
    elif current_state == 'awaiting_edit_prompt':
        USER_STATES.pop(chat_id, None)
        image_to_process_id = session.get('last_image_file_id')
        sent_msg = tg.send_message(chat_id, "جاري تعديل الصورة...", reply_to_message_id=message_id)
        waiting_message_id = sent_msg.get('result', {}).get('message_id')
        threading.Thread(target=edit_image_worker, args=(chat_id, message_id, image_to_process_id, prompt, session, waiting_message_id)).start()

    elif current_state == 'awaiting_image_for_description':
        USER_STATES.pop(chat_id, None)
        if 'photo' in message:
            file_id = message['photo'][-1]['file_id']
            session['last_image_file_id'] = file_id # نحفظها كآخر صورة
            sent_msg = tg.send_message(chat_id, "جاري تحليل ووصف الصورة...", reply_to_message_id=message_id)
            waiting_message_id = sent_msg.get('result', {}).get('message_id')
            threading.Thread(target=describe_image_worker, args=(chat_id, message_id, file_id, waiting_message_id)).start()
        else:
            tg.send_message(chat_id, "لم يتم إرسال صورة. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)

    elif current_state == 'awaiting_simple_prompt':
        USER_STATES.pop(chat_id, None)
        sent_msg = tg.send_message(chat_id, "جاري تحليل الفكرة وتحسينها...", reply_to_message_id=message_id)
        waiting_message_id = sent_msg.get('result', {}).get('message_id')
        threading.Thread(target=enhance_prompt_worker, args=(chat_id, message_id, prompt, waiting_message_id)).start()
    
    elif current_state == 'awaiting_video_prompt_text':
        USER_STATES.pop(chat_id, None)
        threading.Thread(target=text_to_video_worker, args=(chat_id, message_id, prompt)).start()

    elif current_state == 'awaiting_video_prompt_image':
        USER_STATES.pop(chat_id, None)
        threading.Thread(target=image_to_video_worker, args=(chat_id, message_id, prompt, session)).start()
        
    else:
        # إذا لم يكن المستخدم في حالة معينة، أظهر له القائمة الرئيسية
        tg.send_message(chat_id, "يرجى اختيار أمر من القائمة أو اضغط /start للبدء.", reply_markup=MAIN_KEYBOARD)