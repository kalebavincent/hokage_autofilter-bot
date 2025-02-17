import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import Media, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Supprimer plusieurs fichiers de la base de données"""

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        logger.info('Le fichier a été supprimé avec succès de la base de données.')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            logger.info('Le fichier a été supprimé avec succès de la base de données.')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                logger.info('Le fichier a été supprimé avec succès de la base de données.')
            else:
                logger.info('Le fichier n\'a pas été trouvé dans la base de données.')
