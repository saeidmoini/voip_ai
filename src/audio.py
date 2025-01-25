import logging
logger = logging.getLogger('agi_logger')

def record_audio(agi, output_path):
    logger.info("Starting recording...")
    try:
        agi.record_file(output_path, 'wav', timeout=10000, silence="s=300", beep='beep', escape_digits='#')
        logger.info("Recording completed.")
    except Exception as e:
        logger.error(f"Error during recording: {e}")
