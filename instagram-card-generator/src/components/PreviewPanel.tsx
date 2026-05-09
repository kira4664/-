import { useRef, useState, useEffect } from 'react';
import type { CardData, TemplateStyle, TemplateType } from '../types';
import CardEditor from './CardEditor';
import { renderCard } from '../utils/canvasRenderer';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

interface Props {
  cards: CardData[];
  style: TemplateStyle;
  template: TemplateType;
  onCardsChange: (cards: CardData[]) => void;
}

// Single card thumbnail using canvas ref callback
function CardThumbnail({
  card,
  style,
  scale,
  onClick,
  isSelected,
}: {
  card: CardData;
  style: TemplateStyle;
  scale: number;
  onClick?: () => void;
  isSelected?: boolean;
}) {
  const mountRef = (canvas: HTMLCanvasElement | null) => {
    if (canvas) renderCard(canvas, card, style, scale);
  };

  return (
    <div
      onClick={onClick}
      className={`relative cursor-pointer rounded-lg overflow-hidden transition-all duration-200 ${
        isSelected
          ? 'ring-2 ring-indigo-500 ring-offset-1 ring-offset-gray-900'
          : 'hover:ring-1 hover:ring-white/30'
      }`}
    >
      <canvas ref={mountRef} style={{ display: 'block', width: '100%' }} />
      {isSelected && (
        <div className="absolute top-1 right-1 w-4 h-4 bg-indigo-500 rounded-full flex items-center justify-center">
          <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}
    </div>
  );
}

// Main large preview canvas - re-renders when card/style changes
function MainPreview({ card, style }: { card: CardData; style: TemplateStyle }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) renderCard(canvasRef.current, card, style, 0.33);
  }, [card, style]);

  return (
    <canvas ref={canvasRef} style={{ display: 'block', width: '100%' }} />
  );
}

export default function PreviewPanel({ cards, style, onCardsChange }: Props) {
  const [selectedCard, setSelectedCard] = useState(0);
  const [viewMode, setViewMode] = useState<'slide' | 'grid'>('slide');
  const [isDownloading, setIsDownloading] = useState(false);

  // Clamp selectedCard when cards shrink
  const safeSelected = Math.min(selectedCard, Math.max(0, cards.length - 1));

  const updateCard = (index: number, updated: CardData) => {
    const newCards = [...cards];
    newCards[index] = updated;
    onCardsChange(newCards);
  };

  const downloadSingle = () => {
    const canvas = document.createElement('canvas');
    renderCard(canvas, cards[safeSelected], style, 1);
    canvas.toBlob(blob => {
      if (blob) saveAs(blob, `cardnews_${String(safeSelected + 1).padStart(2, '0')}.png`);
    });
  };

  const downloadAll = async () => {
    setIsDownloading(true);
    try {
      const zip = new JSZip();
      for (let i = 0; i < cards.length; i++) {
        const canvas = document.createElement('canvas');
        renderCard(canvas, cards[i], style, 1);
        const blob = await new Promise<Blob>(resolve => canvas.toBlob(b => resolve(b!)));
        zip.file(`cardnews_${String(i + 1).padStart(2, '0')}.png`, blob);
      }
      const zipBlob = await zip.generateAsync({ type: 'blob' });
      saveAs(zipBlob, 'cardnews_all.zip');
    } finally {
      setIsDownloading(false);
    }
  };

  if (cards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[500px] text-center">
        <div className="text-7xl mb-5">📱</div>
        <h3 className="text-xl font-bold text-gray-400 mb-2">카드뉴스 미리보기</h3>
        <p className="text-gray-600 text-sm max-w-xs leading-relaxed">
          좌측에 블로그 글을 입력하고<br />
          <span className="text-indigo-400 font-semibold">카드뉴스 자동 생성</span> 버튼을 눌러보세요
        </p>
        <div className="mt-6 grid grid-cols-3 gap-3 opacity-20">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="w-24 h-30 bg-gray-800 rounded-lg" style={{ height: 120 }} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1 bg-gray-800 p-1 rounded-lg">
          <button
            onClick={() => setViewMode('slide')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              viewMode === 'slide' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            슬라이드
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              viewMode === 'grid' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            전체 보기
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={downloadSingle}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-300 hover:text-white hover:border-gray-500 transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            PNG 저장
          </button>
          <button
            onClick={downloadAll}
            disabled={isDownloading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-sm text-white hover:bg-indigo-500 transition-all disabled:opacity-50"
          >
            {isDownloading ? (
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            )}
            ZIP 전체 다운로드
          </button>
        </div>
      </div>

      {viewMode === 'slide' ? (
        <>
          <div className="flex gap-4">
            {/* Main Preview */}
            <div className="flex-1 flex flex-col items-center">
              <div className="rounded-2xl overflow-hidden shadow-2xl" style={{ width: '100%', maxWidth: 360 }}>
                <MainPreview card={cards[safeSelected]} style={style} />
              </div>
              {/* Navigation */}
              <div className="flex items-center gap-4 mt-4">
                <button
                  onClick={() => setSelectedCard(Math.max(0, safeSelected - 1))}
                  disabled={safeSelected === 0}
                  className="w-9 h-9 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-gray-300 text-lg hover:text-white disabled:opacity-30 transition-all"
                >
                  ‹
                </button>
                <div className="text-sm text-gray-400 text-center min-w-[60px]">
                  {safeSelected + 1} / {cards.length}
                </div>
                <button
                  onClick={() => setSelectedCard(Math.min(cards.length - 1, safeSelected + 1))}
                  disabled={safeSelected === cards.length - 1}
                  className="w-9 h-9 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-gray-300 text-lg hover:text-white disabled:opacity-30 transition-all"
                >
                  ›
                </button>
              </div>
            </div>

            {/* Thumbnail Strip */}
            <div
              className="flex flex-col gap-2 overflow-y-auto scrollbar-hidden"
              style={{ width: 90, maxHeight: 600 }}
            >
              {cards.map((card, i) => (
                <div key={card.id}>
                  <CardThumbnail
                    card={card}
                    style={style}
                    scale={0.083}
                    onClick={() => setSelectedCard(i)}
                    isSelected={safeSelected === i}
                  />
                  <div className="text-center text-[10px] text-gray-600 mt-0.5">{i + 1}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Edit Panel */}
          <div className="border-t border-gray-800 pt-4 mt-2">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-300">
                {safeSelected + 1}번 카드 편집
              </h3>
              <span className="text-xs text-gray-500 bg-gray-800/80 px-2 py-0.5 rounded border border-gray-700">
                {cards[safeSelected]?.role === 'hook' ? '🎯 후킹' :
                 cards[safeSelected]?.role === 'problem' ? '❓ 문제' :
                 cards[safeSelected]?.role === 'info' ? '📋 정보' :
                 cards[safeSelected]?.role === 'caution' ? '⚠️ 주의' : '📣 CTA'}
              </span>
            </div>
            <CardEditor
              card={cards[safeSelected]}
              onChange={updated => updateCard(safeSelected, updated)}
            />
          </div>
        </>
      ) : (
        <div className="grid grid-cols-4 gap-3">
          {cards.map((card, i) => (
            <div key={card.id} className="flex flex-col gap-1">
              <CardThumbnail
                card={card}
                style={style}
                scale={0.16}
                onClick={() => { setSelectedCard(i); setViewMode('slide'); }}
                isSelected={safeSelected === i}
              />
              <div className="text-center text-xs text-gray-500">{i + 1}번 카드</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
