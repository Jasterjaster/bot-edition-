import time
import threading
import os
import base64
import uuid

# --- استيراد أدوات تيليجرام والخدمات الخارجية ---
import telegram_utils as tg
import services

# --- الإعدادات العامة ---
USER_STATES = {} 
ACTIVE_VIDEO_JOBS = {} 


# --- لوحات المفاتيح (Keyboards) ---
MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🖼️ إنشاء صورة", "callback_data": "generate_image"}, {"text": "✨ تحسين الوصف (Prompt)", "callback_data": "enhance_prompt"}],
        [{"text": "📄 وصف صورة", "callback_data": "describe_image"}, {"text": "🎨 تعديل آخر صورة", "callback_data": "edit_last_image"}],
        [{"text": "🎞️ إنشاء فيديو", "callback_data": "create_video"}]
    ]
}

VIDEO_MODEL_SELECTION_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "VEO", "callback_data": "select_model:veo"}, {"text": "Kling", "callback_data": "select_model:kling"}],
        [{"text": "Sora", "callback_data": "select_model:sora"}, {"text": "Sora Pro ✨", "callback_data": "select_model:sora_pro"}],
        [{"text": "⬅️ عودة للقائمة الرئيسية", "callback_data": "back_to_main"}]
    ]
}

VEO_SORA_OPTIONS_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🎬 من نص فقط", "callback_data": "type_select:from_text"}, {"text": "🖼️ من صورة ونص", "callback_data": "type_select:from_image"}],
        [{"text": "⬅️ عودة لاختيار الموديل", "callback_data": "back_to_model_select"}]
    ]
}

KLING_OPTIONS_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🖼️ من صورة ونص", "callback_data": "type_select:from_image"}],
        [{"text": "⬅️ عودة لاختيار الموديل", "callback_data": "back_to_model_select"}]
    ]
}

# --- [جديد] لوحة مفاتيح تأكيد تحسين الوصف ---
PROMPT_ENHANCE_CONFIRM_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "✅ نعم، قم بالتحسين", "callback_data": "confirm_enhance:yes"},
            {"text": "✖️ لا، استخدم وصفي", "callback_data": "confirm_enhance:no"}
        ]
    ]
}


# --- دوال العمال (Workers) ---

def image_generation_worker(chat_id, message_id, image_prompt, session, waiting_message_id):
    tg.send_chat_action(chat_id, "upload_photo")
    image_urls = services.generate_image_from_prompt(image_prompt)
    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
    if image_urls:
        photo_message = tg.send_photo(chat_id, image_urls[0], caption=f"تم إنشاء الصورة بنجاح.", reply_to_message_id=message_id)
        if photo_message and photo_message.get('ok'):
            sent_message = photo_message['result']
            photo_file_id = sent_message['photo'][-1]['file_id']
            sent_message_id = sent_message['message_id']
            keyboard = {"inline_keyboard": [[{"text": "🎨 تعديل هذه الصورة", "callback_data": f"edit_image:{photo_file_id}"}]]}
            tg.edit_message_reply_markup(chat_id, sent_message_id, keyboard)
            session['last_image_file_id'] = photo_file_id
    else:
        tg.send_message(chat_id, "حدث خطأ أثناء إنشاء الصورة. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)
    # [مُعدل] إظهار القائمة الرئيسية في النهاية
    tg.send_message(chat_id, "اختر خدمة أخرى من القائمة:", reply_markup=MAIN_KEYBOARD)


def edit_image_worker(chat_id, message_id, image_file_id, edit_prompt, session, waiting_message_id):
    tg.send_chat_action(chat_id, "upload_photo")
    file_path = tg.get_file_path(image_file_id)
    if not file_path:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: لم أتمكن من تحميل الصورة من تيليجرام.", reply_to_message_id=message_id); return
    
    original_image_data = tg.download_image_as_bytes(file_path)
    if not original_image_data:
        if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
        tg.send_message(chat_id, "خطأ: فشل تحميل بيانات الصورة.", reply_to_message_id=message_id); return
        
    uploaded_url = services.upload_image_for_editing(original_image_data, file_name=f"{uuid.uuid4()}.jpg")
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
        photo_message = tg.send_photo(chat_id, final_image_url, caption=f"تم تعديل الصورة بنجاح.", reply_to_message_id=message_id)
        if photo_message and photo_message.get('ok'):
            sent_message = photo_message['result']
            photo_file_id = sent_message['photo'][-1]['file_id']
            sent_message_id = sent_message['message_id']
            keyboard = {"inline_keyboard": [[{"text": "🎨 تعديل هذه الصورة", "callback_data": f"edit_image:{photo_file_id}"}]]}
            tg.edit_message_reply_markup(chat_id, sent_message_id, keyboard)
            session['last_image_file_id'] = photo_file_id
    else:
        tg.send_message(chat_id, "فشل تعديل الصورة أو استغرق وقتاً طويلاً. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)
    # [مُعدل] إظهار القائمة الرئيسية في النهاية
    tg.send_message(chat_id, "اختر خدمة أخرى من القائمة:", reply_markup=MAIN_KEYBOARD)


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
    # [مُعدل] إظهار القائمة الرئيسية في النهاية
    tg.send_message(chat_id, "اختر خدمة أخرى من القائمة:", reply_markup=MAIN_KEYBOARD)


def enhance_prompt_worker(chat_id, message_id, simple_prompt, waiting_message_id):
    tg.send_chat_action(chat_id, "typing")
    enhanced_prompt, _ = services.generate_enhanced_prompt(simple_prompt)
    if waiting_message_id: tg.delete_message(chat_id, waiting_message_id)
    tg.send_message(chat_id, f"**الوصف المحسّن (Prompt):**\n\n`{enhanced_prompt}`\n\nيمكنك الآن نسخ هذا الوصف واستخدامه في 'إنشاء صورة'.", reply_to_message_id=message_id)
    # [مُعدل] إظهار القائمة الرئيسية في النهاية
    tg.send_message(chat_id, "اختر خدمة أخرى من القائمة:", reply_markup=MAIN_KEYBOARD)


# --- [مُعدل] دالة عامل الفيديو تقبل الآن وصفًا محسنًا كمعلمة اختيارية ---
def video_generation_worker(chat_id, message_id, prompt, start_job_function, file_id=None, enhanced_prompt=None):
    job_id = str(uuid.uuid4())
    cancel_event = threading.Event()
    ACTIVE_VIDEO_JOBS[job_id] = cancel_event
    
    keyboard = {"inline_keyboard": [[{"text": "❌ إلغاء", "callback_data": f"cancel_video:{job_id}"}]]}
    status_msg = tg.send_message(chat_id, "تم استلام الطلب 🎬\nجاري إنشاء الفيديو... قد تستغرق العملية عدة دقائق.", reply_to_message_id=message_id, reply_markup=keyboard)
    status_message_id = status_msg['result']['message_id']
    
    try:
        generation_info = None
        if file_id:
            file_path = tg.get_file_path(file_id)
            if not file_path:
                tg.edit_message_text(chat_id, status_message_id, "خطأ: لم أتمكن من تحميل الصورة من تيليجرام."); return
            image_bytes = tg.download_image_as_bytes(file_path)
            if not image_bytes:
                tg.edit_message_text(chat_id, status_message_id, "خطأ: حدث خطأ أثناء تحميل بيانات الصورة."); return
            upload_info = services.upload_image_for_video(image_bytes, f"{uuid.uuid4()}.jpg")
            if not upload_info:
                tg.edit_message_text(chat_id, status_message_id, "خطأ: فشل رفع الصورة لخدمة الفيديو."); return
            tg.send_chat_action(chat_id, "upload_video")
            generation_info = start_job_function(prompt, upload_info['cdnUrl'], upload_info['uploadId'])
        else:
            tg.send_chat_action(chat_id, "upload_video")
            generation_info = start_job_function(prompt)

        if not generation_info:
            tg.edit_message_text(chat_id, status_message_id, "خطأ: فشل بدء مهمة إنشاء الفيديو.")
            return

        video_url = services.poll_for_video_result(generation_info['request_id'], generation_info['history_id'], cancel_event)

        if video_url == "CANCELLED":
            tg.edit_message_text(chat_id, status_message_id, "تم إلغاء عملية إنشاء الفيديو.")
        elif video_url:
            tg.edit_message_text(chat_id, status_message_id, "اكتمل إنشاء الفيديو! جاري الإرسال...")
            tg.send_video(chat_id, video_url, caption=f"فيديو من: {start_job_function.__name__}", reply_to_message_id=message_id)
            tg.delete_message(chat_id, status_message_id)
            # --- [جديد] إرسال الوصف المحسن في رسالة منفصلة إذا تم استخدامه ---
            if enhanced_prompt:
                tg.send_message(chat_id, f"**الوصف المحسّن الذي تم استخدامه:**\n\n`{enhanced_prompt}`", reply_to_message_id=message_id)
        else:
            tg.edit_message_text(chat_id, status_message_id, "فشلت عملية إنشاء الفيديو أو استغرقت وقتاً طويلاً.")
    finally:
        if job_id in ACTIVE_VIDEO_JOBS:
            del ACTIVE_VIDEO_JOBS[job_id]
        # [مُعدل] إظهار القائمة الرئيسية في النهاية
        tg.send_message(chat_id, "اختر خدمة أخرى من القائمة:", reply_markup=MAIN_KEYBOARD)


# --- [جديد] دالة مساعدة لبدء عملية الفيديو بعد الحصول على الوصف ---
def handle_video_prompt(chat_id, message_id, prompt, model, file_id=None):
    # إذا كان الوصف قصيرًا، اسأل المستخدم إذا كان يريد تحسينه
    if len(prompt.split()) < 10:
        USER_STATES[chat_id] = {
            'state': 'awaiting_enhancement_confirmation',
            'original_prompt': prompt,
            'model': model,
            'file_id': file_id,
            'message_id': message_id
        }
        tg.send_message(chat_id, "يبدو وصفك بسيطاً. هل تود تحسينه للحصول على نتائج أفضل وأكثر إبداعاً؟", reply_markup=PROMPT_ENHANCE_CONFIRM_KEYBOARD, reply_to_message_id=message_id)
    else:
        # إذا كان الوصف طويلاً بما فيه الكفاية، ابدأ مباشرة
        gen_type = f"{model}_{'from_image' if file_id else 'from_text'}"
        job_map = {
            'veo_from_image': services.start_veo_image_to_video_job, 'veo_from_text': services.start_veo_text_to_video_job,
            'sora_from_image': services.start_sora_image_to_video_job, 'sora_from_text': services.start_sora_text_to_video_job,
            'sora_pro_from_image': services.start_sora_pro_image_to_video_job, 'sora_pro_from_text': services.start_sora_pro_text_to_video_job,
            'kling_from_image': services.start_kling_image_to_video_job,
        }
        start_job_function = job_map.get(gen_type)
        if start_job_function:
            threading.Thread(target=video_generation_worker, args=(chat_id, message_id, prompt, start_job_function, file_id)).start()


# --- المنطق الرئيسي للبوت ---
def process_update(update, chat_sessions):
    
    if 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = str(callback_query['message']['chat']['id'])
        message_id = callback_query['message']['message_id']
        callback_id = callback_query['id']
        data = callback_query['data']
        session = chat_sessions.setdefault(chat_id, {"last_image_file_id": None})

        tg.answer_callback_query(callback_id)

        if data == 'generate_image':
            USER_STATES[chat_id] = {'state': 'awaiting_prompt', 'type': 'image_gen'}
            tg.send_message(chat_id, "يرجى إرسال الوصف (prompt) لإنشاء الصورة.")
        elif data == 'enhance_prompt':
            USER_STATES[chat_id] = {'state': 'awaiting_prompt', 'type': 'prompt_enhance'}
            tg.send_message(chat_id, "يرجى إرسال فكرة بسيطة، وسأقوم بتحويلها إلى وصف احترافي.")
        elif data == 'describe_image':
            USER_STATES[chat_id] = {'state': 'awaiting_image'}
            tg.send_message(chat_id, "يرجى إرسال الصورة التي تريد وصفها.")
        elif data == 'edit_last_image':
            if session.get('last_image_file_id'):
                USER_STATES[chat_id] = {'state': 'awaiting_prompt', 'type': 'image_edit'}
                tg.send_message(chat_id, "يرجى إرسال تعليمات التعديل على آخر صورة.")
            else:
                tg.send_message(chat_id, "لم يتم العثور على صورة سابقة.")
        elif data.startswith("edit_image:"):
            file_id = data.split(":", 1)[1]
            session['last_image_file_id'] = file_id
            USER_STATES[chat_id] = {'state': 'awaiting_prompt', 'type': 'image_edit'}
            tg.send_message(chat_id, "يرجى إرسال تعليمات التعديل لهذه الصورة.")
        elif data == 'create_video':
            tg.edit_message_text(chat_id, message_id, "اختر موديل الفيديو:", reply_markup=VIDEO_MODEL_SELECTION_KEYBOARD)
        elif data.startswith("select_model:"):
            model = data.split(":", 1)[1]
            USER_STATES[chat_id] = {'state': 'awaiting_type_selection', 'model': model}
            if model in ['veo', 'sora', 'sora_pro']:
                tg.edit_message_text(chat_id, message_id, f"اختر نوع الإدخال لموديل {model.upper()}:", reply_markup=VEO_SORA_OPTIONS_KEYBOARD)
            elif model == 'kling':
                tg.edit_message_text(chat_id, message_id, "موديل Kling يدعم الإنشاء من صورة ونص فقط.", reply_markup=KLING_OPTIONS_KEYBOARD)
        
        elif data.startswith("type_select:"):
            gen_type = data.split(":", 1)[1]
            model_info = USER_STATES.get(chat_id)
            if model_info and model_info.get('state') == 'awaiting_type_selection':
                model = model_info['model']
                if gen_type == 'from_image':
                    USER_STATES[chat_id] = {'state': 'awaiting_video_image', 'model': model}
                    tg.edit_message_text(chat_id, message_id, f"تمام. يرجى الآن إرسال الصورة التي تريد تحريكها باستخدام موديل {model.upper()}.")
                else:
                    USER_STATES[chat_id] = {'state': 'awaiting_prompt', 'type': f'{model}_from_text'}
                    tg.edit_message_text(chat_id, message_id, f"أرسل الوصف لإنشاء فيديو من نص باستخدام موديل {model.upper()}.")

        # --- [جديد] التعامل مع رد المستخدم على تحسين الوصف ---
        elif data.startswith("confirm_enhance:"):
            decision = data.split(":", 1)[1]
            user_context = USER_STATES.get(chat_id)
            if not user_context or user_context.get('state') != 'awaiting_enhancement_confirmation':
                return
            
            tg.delete_message(chat_id, message_id) # حذف رسالة التأكيد
            
            original_prompt = user_context['original_prompt']
            model = user_context['model']
            file_id = user_context.get('file_id')
            original_message_id = user_context['message_id']
            
            USER_STATES.pop(chat_id, None)
            
            final_prompt = original_prompt
            enhanced_prompt_for_msg = None

            if decision == 'yes':
                wait_msg = tg.send_message(chat_id, "جاري تحسين الوصف...", reply_to_message_id=original_message_id)
                wait_msg_id = wait_msg['result']['message_id']
                enhanced_prompt, _ = services.enhance_video_prompt(original_prompt)
                tg.delete_message(chat_id, wait_msg_id)
                if enhanced_prompt != "تم حظر الاستجابة." and enhanced_prompt != "خطأ في الاتصال بالخدمة.":
                    final_prompt = enhanced_prompt
                    enhanced_prompt_for_msg = enhanced_prompt
                else: # في حالة فشل التحسين، استخدم الأصلي
                    tg.send_message(chat_id, "فشل تحسين الوصف، سيتم استخدام الوصف الأصلي.", reply_to_message_id=original_message_id)
            
            gen_type = f"{model}_{'from_image' if file_id else 'from_text'}"
            job_map = {
                'veo_from_image': services.start_veo_image_to_video_job, 'veo_from_text': services.start_veo_text_to_video_job,
                'sora_from_image': services.start_sora_image_to_video_job, 'sora_from_text': services.start_sora_text_to_video_job,
                'sora_pro_from_image': services.start_sora_pro_image_to_video_job, 'sora_pro_from_text': services.start_sora_pro_text_to_video_job,
                'kling_from_image': services.start_kling_image_to_video_job,
            }
            start_job_function = job_map.get(gen_type)
            if start_job_function:
                threading.Thread(target=video_generation_worker, args=(chat_id, original_message_id, final_prompt, start_job_function, file_id, enhanced_prompt_for_msg)).start()

        elif data == 'back_to_model_select':
            USER_STATES.pop(chat_id, None)
            tg.edit_message_text(chat_id, message_id, "اختر موديل الفيديو:", reply_markup=VIDEO_MODEL_SELECTION_KEYBOARD)
        elif data == 'back_to_main':
            USER_STATES.pop(chat_id, None)
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
    session = chat_sessions.setdefault(chat_id, {"last_image_file_id": None})
    user_context = USER_STATES.get(chat_id)
    
    prompt = (message.get('text') or message.get('caption', '')).strip()
    if prompt.lower() == '/start':
        USER_STATES.pop(chat_id, None)
        session['last_image_file_id'] = None
        tg.send_message(chat_id, "أهلاً بك. اختر إحدى الخدمات من القائمة:", reply_markup=MAIN_KEYBOARD)
        return
    if prompt.lower() == '/clear':
        USER_STATES.pop(chat_id, None)
        session['last_image_file_id'] = None
        tg.send_message(chat_id, "تم مسح الذاكرة والحالة. للبدء من جديد اضغط /start", reply_to_message_id=message_id)
        return

    if not user_context:
        tg.send_message(chat_id, "يرجى اختيار أمر من القائمة أو اضغط /start للبدء.", reply_markup=MAIN_KEYBOARD)
        return

    state = user_context.get('state')
    
    if state == 'awaiting_video_image':
        if 'photo' in message:
            file_id = message['photo'][-1]['file_id']
            model = user_context.get('model')
            USER_STATES[chat_id] = {'state': 'awaiting_video_prompt', 'model': model, 'file_id': file_id}
            tg.send_message(chat_id, "صورة ممتازة. الآن يرجى إرسال الوصف النصي للحركة التي تريد إضافتها.", reply_to_message_id=message_id)
        else:
            tg.send_message(chat_id, "الرجاء إرسال صورة.", reply_to_message_id=message_id)
        return

    elif state == 'awaiting_video_prompt':
        model = user_context.get('model')
        file_id = user_context.get('file_id')
        USER_STATES.pop(chat_id, None)
        handle_video_prompt(chat_id, message_id, prompt, model, file_id)
        return

    elif state == 'awaiting_image':
        USER_STATES.pop(chat_id, None)
        if 'photo' in message:
            file_id = message['photo'][-1]['file_id']
            session['last_image_file_id'] = file_id
            sent_msg = tg.send_message(chat_id, "جاري تحليل ووصف الصورة...", reply_to_message_id=message_id)
            waiting_message_id = sent_msg.get('result', {}).get('message_id')
            threading.Thread(target=describe_image_worker, args=(chat_id, message_id, file_id, waiting_message_id)).start()
        else:
            tg.send_message(chat_id, "لم يتم إرسال صورة. يرجى المحاولة مرة أخرى.", reply_to_message_id=message_id)

    elif state == 'awaiting_prompt':
        gen_type = user_context.get('type')
        
        # --- [مُعدل] اعتراض طلبات الفيديو هنا ---
        video_text_types = ['veo_from_text', 'sora_from_text', 'sora_pro_from_text']
        if gen_type in video_text_types:
            model = gen_type.replace('_from_text', '')
            USER_STATES.pop(chat_id, None)
            handle_video_prompt(chat_id, message_id, prompt, model)
            return
            
        USER_STATES.pop(chat_id, None)
        
        if gen_type == 'image_gen':
            sent_msg = tg.send_message(chat_id, "جاري إنشاء الصورة...", reply_to_message_id=message_id)
            waiting_message_id = sent_msg.get('result', {}).get('message_id')
            threading.Thread(target=image_generation_worker, args=(chat_id, message_id, prompt, session, waiting_message_id)).start()
        
        elif gen_type == 'image_edit':
            image_to_process_id = session.get('last_image_file_id')
            sent_msg = tg.send_message(chat_id, "جاري تعديل الصورة...", reply_to_message_id=message_id)
            waiting_message_id = sent_msg.get('result', {}).get('message_id')
            threading.Thread(target=edit_image_worker, args=(chat_id, message_id, image_to_process_id, prompt, session, waiting_message_id)).start()
        
        elif gen_type == 'prompt_enhance':
            sent_msg = tg.send_message(chat_id, "جاري تحليل الفكرة وتحسينها...", reply_to_message_id=message_id)
            waiting_message_id = sent_msg.get('result', {}).get('message_id')
            threading.Thread(target=enhance_prompt_worker, args=(chat_id, message_id, prompt, waiting_message_id)).start()
