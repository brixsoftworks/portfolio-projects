import React, { useState, useEffect } from 'react';
import { X, Image, Video, HardDrive, Calendar, MapPin, Download, RefreshCw, Play } from 'lucide-react';

interface MediaPhoto {
  filename: string;
  url: string;
  size_bytes: number;
  created_at: string;
  location?: {
    latitude?: number;
    longitude?: number;
    altitude_agl_m?: number;
    altitude_msl_m?: number;
    satellites?: number;
  };
}

interface MediaVideo {
  filename: string;
  url: string;
  size_bytes: number;
  has_srt: boolean;
  created_at: string;
}

interface MediaGalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MediaGalleryModal: React.FC<MediaGalleryModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'photos' | 'videos'>('photos');
  const [photos, setPhotos] = useState<MediaPhoto[]>([]);
  const [videos, setVideos] = useState<MediaVideo[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [previewPhoto, setPreviewPhoto] = useState<string | null>(null);
  const [previewVideo, setPreviewVideo] = useState<string | null>(null);

  const fetchMedia = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/media/list');
      const data = await res.json();
      if (data.ok) {
        setPhotos(data.photos || []);
        setVideos(data.videos || []);
      }
    } catch (e) {
      console.warn('Could not load media list:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMedia();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4">
      <div className="relative w-full max-w-5xl h-[85vh] bg-[#0b0f17] rounded-3xl overflow-hidden border border-white/20 shadow-2xl flex flex-col text-slate-100">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#111622] border-b border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
              <HardDrive className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-sm font-mono font-bold tracking-wider text-white">
                DRONE RECORDINGS & FLIGHT MEDIA
              </h2>
              <p className="text-[10px] font-mono text-slate-400">
                SAVED IN: <span className="text-cyan-300 font-semibold">/home/mullainathan/projects/mini-ai-drone/drone_recordings/</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={fetchMedia}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition-all active:scale-95"
              title="Refresh Media List"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-white/10 hover:bg-rose-500/20 border border-white/10 hover:border-rose-500/40 text-slate-300 hover:text-rose-300 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="px-6 py-2.5 bg-[#0e131d] border-b border-white/5 flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('photos')}
            className={`px-4 py-1.5 rounded-xl text-xs font-mono font-bold tracking-wider flex items-center space-x-2 transition-all ${
              activeTab === 'photos'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                : 'text-slate-400 hover:text-white border border-transparent'
            }`}
          >
            <Image className="w-4 h-4 text-cyan-400" />
            <span>CAPTURED PHOTOS ({photos.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('videos')}
            className={`px-4 py-1.5 rounded-xl text-xs font-mono font-bold tracking-wider flex items-center space-x-2 transition-all ${
              activeTab === 'videos'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-[0_0_12px_rgba(244,63,94,0.3)]'
                : 'text-slate-400 hover:text-white border border-transparent'
            }`}
          >
            <Video className="w-4 h-4 text-rose-400" />
            <span>RECORDED VIDEOS ({videos.length})</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'photos' ? (
            photos.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-3">
                <Image className="w-12 h-12 opacity-30 text-cyan-400" />
                <p className="text-xs font-mono uppercase tracking-widest">
                  No photos captured yet. Press [P] or click Shutter to take high-res photo with GPS.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {photos.map((p) => (
                  <div
                    key={p.filename}
                    onClick={() => setPreviewPhoto(p.url)}
                    className="p-3 rounded-2xl bg-[#141925]/90 border border-white/10 hover:border-cyan-500/50 shadow-xl transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    {/* Thumbnail Image */}
                    <div className="relative w-full h-44 rounded-xl overflow-hidden bg-black/50 mb-2.5">
                      <img
                        src={p.url}
                        alt={p.filename}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2.5">
                        <span className="text-[10px] font-mono text-cyan-300 font-bold">CLICK TO ENLARGE</span>
                      </div>
                    </div>

                    {/* Metadata Footer */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono font-bold text-white truncate max-w-[200px]">
                          {p.filename}
                        </span>
                        <span className="text-[9px] font-mono text-slate-400">
                          {(p.size_bytes / 1024).toFixed(0)} KB
                        </span>
                      </div>

                      {/* GPS Location Tag */}
                      <div className="p-1.5 rounded-lg bg-black/40 border border-white/5 text-[9px] font-mono text-cyan-300 flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-cyan-400 shrink-0" />
                        <span className="truncate">
                          {p.location?.latitude ? `${p.location.latitude.toFixed(6)}°N, ${p.location.longitude?.toFixed(6)}°E` : '10.810000°N, 78.693200°E'}
                        </span>
                        <span className="text-emerald-400 font-bold ml-auto shrink-0">
                          {p.location?.altitude_agl_m ? `${p.location.altitude_agl_m.toFixed(1)}m` : '18.5m'}
                        </span>
                      </div>

                      <div className="text-[8.5px] font-mono text-slate-500 flex items-center justify-between pt-0.5">
                        <span>{p.created_at}</span>
                        <a
                          href={p.url}
                          download={p.filename}
                          onClick={(e) => e.stopPropagation()}
                          className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                        >
                          <Download className="w-2.5 h-2.5" />
                          <span>SAVE</span>
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : videos.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-3">
              <Video className="w-12 h-12 opacity-30 text-rose-400" />
              <p className="text-xs font-mono uppercase tracking-widest">
                No videos recorded yet. Press [R] or click Record to capture MP4 with GPS subtitles (.srt).
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {videos.map((v) => (
                <div
                  key={v.filename}
                  onClick={() => setPreviewVideo(v.url)}
                  className="p-3.5 rounded-2xl bg-[#141925]/90 border border-white/10 hover:border-rose-500/50 shadow-xl transition-all cursor-pointer group flex flex-col justify-between"
                >
                  <div className="relative w-full h-40 rounded-xl overflow-hidden bg-black/80 flex items-center justify-center mb-2.5 border border-white/5">
                    <Video className="w-10 h-10 text-rose-500/60 group-hover:scale-110 transition-transform" />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/20 transition-colors">
                      <div className="w-10 h-10 rounded-full bg-rose-500/80 text-white flex items-center justify-center shadow-[0_0_15px_rgba(244,63,94,0.6)]">
                        <Play className="w-5 h-5 fill-white ml-0.5" />
                      </div>
                    </div>
                    {v.has_srt && (
                      <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[8px] font-mono font-bold bg-cyan-500/30 text-cyan-300 border border-cyan-500/50">
                        GPS SRT
                      </span>
                    )}
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-white truncate max-w-[200px]">
                        {v.filename}
                      </span>
                      <span className="text-[9px] font-mono text-slate-400">
                        {(v.size_bytes / (1024 * 1024)).toFixed(1)} MB
                      </span>
                    </div>

                    <div className="text-[9px] font-mono text-slate-400 flex items-center justify-between">
                      <span>{v.created_at}</span>
                      <a
                        href={v.url}
                        download={v.filename}
                        onClick={(e) => e.stopPropagation()}
                        className="text-rose-400 hover:text-rose-300 flex items-center space-x-1"
                      >
                        <Download className="w-3 h-3" />
                        <span>DOWNLOAD</span>
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modal Photo Full Preview */}
        {previewPhoto && (
          <div
            onClick={() => setPreviewPhoto(null)}
            className="fixed inset-0 z-[60] bg-black/90 backdrop-blur-md flex items-center justify-center p-4 cursor-pointer"
          >
            <div className="relative max-w-4xl max-h-[90vh] rounded-2xl overflow-hidden border border-white/20 shadow-2xl">
              <img src={previewPhoto} alt="Full Preview" className="max-w-full max-h-[85vh] object-contain" />
              <button
                onClick={() => setPreviewPhoto(null)}
                className="absolute top-3 right-3 p-2 rounded-xl bg-black/80 text-white hover:bg-rose-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Modal Video Player */}
        {previewVideo && (
          <div
            onClick={() => setPreviewVideo(null)}
            className="fixed inset-0 z-[60] bg-black/90 backdrop-blur-md flex items-center justify-center p-4 cursor-pointer"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-4xl rounded-2xl overflow-hidden border border-white/20 shadow-2xl bg-black"
            >
              <video src={previewVideo} controls autoPlay className="w-full max-h-[80vh]" />
              <button
                onClick={() => setPreviewVideo(null)}
                className="absolute top-3 right-3 p-2 rounded-xl bg-black/80 text-white hover:bg-rose-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
