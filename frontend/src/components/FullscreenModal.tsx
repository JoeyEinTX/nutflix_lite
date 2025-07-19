import React from 'react';
import { X } from 'lucide-react';
import { Button } from './ui/button';

interface FullscreenModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  type: 'camera' | 'sighting';
  content: any;
}

export function FullscreenModal({ isOpen, onClose, title, type, content }: FullscreenModalProps) {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div 
      className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-6xl max-h-full bg-stone-900 rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-stone-700">
          <div>
            <h2 className="text-xl font-medium text-amber-200">{title}</h2>
            {type === 'camera' && content.location && (
              <p className="text-sm text-stone-400">{content.location}</p>
            )}
          </div>
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="text-stone-400 hover:text-white"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-4">
          {type === 'camera' ? (
            <div className="aspect-video bg-stone-800 rounded border border-stone-600">
              {content.streamUrl ? (
                <img
                  src={content.streamUrl}
                  alt={`${title} Live Stream`}
                  className="w-full h-full object-cover rounded"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-stone-400">
                  <div className="text-center">
                    <div className="text-4xl mb-4">📷</div>
                    <p>Live camera stream</p>
                    <p className="text-sm text-stone-500 mt-2">
                      Direct stream: {content.streamUrl || 'Not available'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            // Sighting details
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="aspect-video">
                <img
                  src={content.image}
                  alt={content.animal}
                  className="w-full h-full object-cover rounded border border-stone-600"
                />
              </div>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-amber-200 mb-2">Sighting Details</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-stone-400">Species:</span>
                      <span className="ml-2 text-white">{content.animal}</span>
                    </div>
                    <div>
                      <span className="text-stone-400">Location:</span>
                      <span className="ml-2 text-white">{content.location}</span>
                    </div>
                    <div>
                      <span className="text-stone-400">Time:</span>
                      <span className="ml-2 text-white">
                        {new Date(content.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
