"""Utility functions for v1"""

from yt_dlp_bonus import YoutubeDLBonus
from yt_dlp_bonus.models import ExtractedInfo
from app.utils import get_video_id, utc_now
from app.db import VideoInfo, engine
from sqlmodel import select, Session


def get_extracted_info(yt: YoutubeDLBonus, url: str) -> ExtractedInfo:
    """Get url's extracted_info from cache or youtube accordingly"""
    video_id = get_video_id(url)
    query = select(VideoInfo).where(VideoInfo.id == video_id)
    with Session(bind=engine) as session:
        cached_extracted_info: VideoInfo = session.exec(query).first()
        if cached_extracted_info:
            if cached_extracted_info.is_valid:
                return cached_extracted_info.extracted_info
            else:
                extracted_info = yt.extract_info_and_form_model(url)
                cached_extracted_info.info = extracted_info.model_dump_json()
                cached_extracted_info.updated_on = utc_now()
                session.add(cached_extracted_info)
                session.commit()
                return extracted_info
        else:
            extracted_info = yt.extract_info_and_form_model(url)
            new_video_info = VideoInfo(
                id=video_id, info=extracted_info.model_dump_json(), updated_on=utc_now()
            )
            session.add(new_video_info)
            session.commit()
            return extracted_info
