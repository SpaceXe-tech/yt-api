"""Utility functions for v1"""

from yt_dlp_bonus import YoutubeDLBonus
from yt_dlp_bonus.models import ExtractedInfo
from app.utils import get_video_id, utc_now
from app.db import VideoInfo, engine
from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError


def get_extracted_info(yt: YoutubeDLBonus, url: str) -> ExtractedInfo:
    """Get url's extracted_info from cache or youtube accordingly"""
    video_id = get_video_id(url)
    raw_info = yt.extract_info(url, download=False)
    
    data = raw_info.copy()
    data.setdefault("channel", data.get("uploader") or "Unknown")
    data.setdefault("uploader", data.get("channel") or "Unknown")
    data.setdefault("channel_follower_count", 0)
    
    extracted_info = ExtractedInfo(**data)
    
    query = select(VideoInfo).where(VideoInfo.id == video_id)
    with Session(bind=engine) as session:
        cached_extracted_info: VideoInfo = session.exec(query).first()
        if cached_extracted_info:
            if cached_extracted_info.is_valid:
                return cached_extracted_info.extracted_info
            else:
                cached_extracted_info.info = extracted_info.model_dump_json()
                cached_extracted_info.updated_on = utc_now()
                try:
                    session.add(cached_extracted_info)
                    session.commit()
                except IntegrityError:
                    pass
                return extracted_info
        else:
            new_video_info = VideoInfo(
                id=video_id, info=extracted_info.model_dump_json(), updated_on=utc_now()
            )
            try:
                session.add(new_video_info)
                session.commit()
            except IntegrityError:
                pass

            return extracted_info
