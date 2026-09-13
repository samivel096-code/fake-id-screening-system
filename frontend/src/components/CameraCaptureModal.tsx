import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RefreshCw } from 'lucide-react';

interface Props {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export const CameraCaptureModal: React.FC<Props> = ({ onCapture, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function startCamera() {
      try {
        const s = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
          audio: false,
        });
        setStream(s);
        if (videoRef.current) {
          videoRef.current.srcObject = s;
        }
      } catch (err: any) {
        setError('Camera access denied or unavailable on this device.');
      }
    }
    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  const captureFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 1280;
    canvas.height = videoRef.current.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
      if (blob) {
        const file = new File([blob], `camera_capture_${Date.now()}.png`, { type: 'image/png' });
        if (stream) stream.getTracks().forEach(t => t.stop());
        onCapture(file);
        onClose();
      }
    }, 'image/png');
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-dialog" style={{ maxWidth: '680px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Camera size={18} color="#38bdf8" />
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>Camera Document Scanner</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body" style={{ textAlign: 'center' }}>
          {error ? (
            <div style={{ padding: '30px', color: '#f87171' }}>{error}</div>
          ) : (
            <div style={{ position: 'relative', background: '#000', borderRadius: 'var(--radius-md)', overflow: 'hidden', minHeight: '360px' }}>
              <video ref={videoRef} autoPlay playsInline style={{ width: '100%', maxHeight: '420px', objectFit: 'contain' }} />
              {/* Document alignment frame guide */}
              <div
                style={{
                  position: 'absolute',
                  inset: '10% 12%',
                  border: '2px dashed rgba(59, 130, 246, 0.7)',
                  borderRadius: '12px',
                  pointerEvents: 'none',
                }}
              />
            </div>
          )}
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px' }}>
            Align document completely within frame in good lighting without glare or blur.
          </p>
        </div>

        <div className="modal-footer" style={{ justifyContent: 'center' }}>
          <button type="button" className="btn btn-primary" onClick={captureFrame} disabled={!!error} style={{ minWidth: '160px' }}>
            <Camera size={16} /> Capture Image
          </button>
        </div>
      </div>
    </div>
  );
};
