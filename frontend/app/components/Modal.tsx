"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'primary' | 'warning';
}

export default function Modal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  type = 'primary'
}: ModalProps) {
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!mounted || !isOpen) return null;

  const confirmButtonColors = {
    danger: 'bg-danger text-white hover:bg-danger/90',
    primary: 'bg-primary text-white hover:bg-primary/90',
    warning: 'bg-warning text-white hover:bg-warning/90',
  };

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4 min-h-screen">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative glass-panel w-full max-w-md p-6 sm:p-8 animate-in zoom-in-95 fade-in slide-in-from-bottom-8 duration-300 shadow-2xl border border-white/10 z-[10001]">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-foreground/40 hover:text-white transition-colors"
          disabled={loading}
        >
          <X size={20} />
        </button>

        <div className="mb-8">
          <h3 className="text-xl sm:text-2xl font-bold text-white mb-3">{title}</h3>
          <p className="text-foreground/70 leading-relaxed text-sm sm:text-base">{message}</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-end">
          <button 
            onClick={onClose}
            disabled={loading}
            className="order-2 sm:order-1 px-6 py-3 rounded-xl text-sm font-bold border border-white/10 text-foreground/60 hover:text-white hover:bg-white/5 transition-all disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button 
            onClick={handleConfirm}
            disabled={loading}
            className={`order-1 sm:order-2 px-6 py-3 rounded-xl text-sm font-bold transition-all hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 ${confirmButtonColors[type]}`}
          >
            {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : null}
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
