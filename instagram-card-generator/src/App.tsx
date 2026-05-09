import { useState, useCallback } from 'react';
import type { CardData, TemplateType } from './types';
import { TEMPLATES } from './data/templates';
import { processText } from './utils/textProcessor';
import InputPanel from './components/InputPanel';
import PreviewPanel from './components/PreviewPanel';
import './index.css';

export default function App() {
  const [blogText, setBlogText] = useState('');
  const [template, setTemplate] = useState<TemplateType>('realestate');
  const [cardCount, setCardCount] = useState(7);
  const [cards, setCards] = useState<CardData[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = useCallback(async () => {
    if (!blogText.trim()) return;
    setIsGenerating(true);
    await new Promise(r => setTimeout(r, 500));
    const generated = processText(blogText, template, cardCount);
    setCards(generated);
    setIsGenerating(false);
  }, [blogText, template, cardCount]);

  const handleTemplateChange = (t: TemplateType) => {
    setTemplate(t);
    if (cards.length > 0) {
      const updated = cards.map(c => ({
        ...c,
        category: TEMPLATES[t].name,
        icon: TEMPLATES[t].icon,
      }));
      setCards(updated);
    }
  };

  const style = TEMPLATES[template];

  return (
    <div className="min-h-screen bg-[#0a0a0f] font-nanum">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#0d0d18] sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
              style={{
                background: `linear-gradient(135deg, ${style.primaryColor}, ${style.accentColor})`,
              }}
            >
              📱
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-none m-0 p-0">
                인스타 카드뉴스 생성기
              </h1>
              <p className="text-gray-500 text-xs mt-0.5 m-0">
                블로그 글 → 인스타 카드뉴스 자동 변환
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {cards.length > 0 && (
              <div className="flex items-center gap-1.5 bg-green-500/10 border border-green-500/30 rounded-full px-3 py-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-green-400 text-xs font-medium">
                  {cards.length}장 생성됨
                </span>
              </div>
            )}
            <div
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-white"
              style={{
                background: `linear-gradient(135deg, ${style.primaryColor}44, ${style.accentColor}44)`,
                border: `1px solid ${style.primaryColor}55`,
              }}
            >
              {style.icon} {style.name}
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="max-w-[1600px] mx-auto px-6 py-6">
        <div className="flex gap-6 items-start">
          {/* Left Panel */}
          <aside className="w-[380px] flex-shrink-0 bg-[#111120] border border-gray-800 rounded-2xl p-5 sticky top-[73px]">
            <InputPanel
              blogText={blogText}
              onBlogTextChange={setBlogText}
              template={template}
              onTemplateChange={handleTemplateChange}
              cardCount={cardCount}
              onCardCountChange={setCardCount}
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
            />
          </aside>

          {/* Right Panel */}
          <section className="flex-1 bg-[#111120] border border-gray-800 rounded-2xl p-5 min-h-[calc(100vh-130px)]">
            <PreviewPanel
              cards={cards}
              style={style}
              template={template}
              onCardsChange={setCards}
            />
          </section>
        </div>
      </main>
    </div>
  );
}
