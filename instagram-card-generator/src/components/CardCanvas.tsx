import { useEffect, useRef } from 'react';
import type { CardData, TemplateStyle } from '../types';
import { renderCard } from '../utils/canvasRenderer';

interface Props {
  card: CardData;
  style: TemplateStyle;
  scale?: number;
  onClick?: () => void;
  isSelected?: boolean;
}

export default function CardCanvas({ card, style, scale = 0.2, onClick, isSelected }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    renderCard(canvas, card, style, scale);
  }, [card, style, scale]);

  return (
    <div
      onClick={onClick}
      className={`
        relative cursor-pointer rounded-lg overflow-hidden transition-all duration-200
        ${isSelected
          ? 'ring-4 ring-indigo-500 ring-offset-2 ring-offset-gray-900 shadow-lg shadow-indigo-500/30'
          : 'hover:ring-2 hover:ring-white/30'
        }
      `}
    >
      <canvas ref={canvasRef} style={{ display: 'block', width: '100%' }} />
      {isSelected && (
        <div className="absolute top-2 right-2 w-5 h-5 bg-indigo-500 rounded-full flex items-center justify-center">
          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}
    </div>
  );
}
