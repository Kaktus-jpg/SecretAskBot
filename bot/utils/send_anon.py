from aiogram import Bot
from aiogram.types import Message


async def send_anonymous_message(
    bot: Bot,
    target_chat_id: int,
    source_message: Message,
    header_text: str | None = None,
) -> None:
    caption_prefix = f"{header_text}\n\n" if header_text else ""

    if source_message.text:
        text = (
            f"{caption_prefix}{source_message.text}"
            if header_text
            else source_message.text
        )
        await bot.send_message(
            chat_id=target_chat_id,
            text=text,
        )
        return

    if source_message.photo:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_photo(
            chat_id=target_chat_id,
            photo=source_message.photo[-1].file_id,
            caption=caption,
        )
        return

    if source_message.video:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_video(
            chat_id=target_chat_id,
            video=source_message.video.file_id,
            caption=caption,
        )
        return

    if source_message.video_note:
        await bot.send_video_note(
            chat_id=target_chat_id,
            video_note=source_message.video_note.file_id,
        )
        if header_text:
            await bot.send_message(chat_id=target_chat_id, text=header_text)
        return

    if source_message.document:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_document(
            chat_id=target_chat_id,
            document=source_message.document.file_id,
            caption=caption,
        )
        return

    if source_message.voice:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_voice(
            chat_id=target_chat_id,
            voice=source_message.voice.file_id,
            caption=caption,
        )
        return

    if source_message.audio:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_audio(
            chat_id=target_chat_id,
            audio=source_message.audio.file_id,
            caption=caption,
        )
        return

    if source_message.animation:
        caption = (
            f"{caption_prefix}{source_message.caption}"
            if source_message.caption
            else (header_text or None)
        )
        await bot.send_animation(
            chat_id=target_chat_id,
            animation=source_message.animation.file_id,
            caption=caption,
        )
        return

    if source_message.sticker:
        if header_text:
            await bot.send_message(chat_id=target_chat_id, text=header_text)
        await bot.send_sticker(
            chat_id=target_chat_id,
            sticker=source_message.sticker.file_id,
        )
        return

    if source_message.contact:
        text = (
            f"{caption_prefix}"
            f"Контакт:\n"
            f"{source_message.contact.first_name}\n"
            f"{source_message.contact.phone_number}"
        )
        await bot.send_message(
            chat_id=target_chat_id,
            text=text,
        )
        return

    if source_message.location:
        if header_text:
            await bot.send_message(chat_id=target_chat_id, text=header_text)
        await bot.send_location(
            chat_id=target_chat_id,
            latitude=source_message.location.latitude,
            longitude=source_message.location.longitude,
        )
        return

    unsupported_type = (
        f"<i>Неподдерживаемый тип сообщения</i> -\n{source_message.content_type}"
    )
    await bot.send_message(
        chat_id=target_chat_id,
        text=(header_text + f"\n\n{unsupported_type}")
        if header_text
        else unsupported_type,
    )
