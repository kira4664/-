import type { TemplateType } from '../types';
import { TEMPLATES } from '../data/templates';

interface Props {
  blogText: string;
  onBlogTextChange: (text: string) => void;
  template: TemplateType;
  onTemplateChange: (t: TemplateType) => void;
  cardCount: number;
  onCardCountChange: (n: number) => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

const TEMPLATE_KEYS = Object.keys(TEMPLATES) as TemplateType[];

const SAMPLE_TEXT = `2026년 5월 10일부터 다주택자 양도세 중과가 부활합니다. 현재 한시적으로 중과가 배제되어 있지만, 5월 9일까지만 혜택을 받을 수 있습니다. 5월 10일 이후에는 2주택자 기본세율에 20%p, 3주택자 이상은 30%p가 추가됩니다. 최대 세율은 82.5%까지 올라갑니다. 양도 차익이 1억원이면 세금이 8,250만원에 달할 수 있습니다. 오늘까지 계약하고 잔금까지 치르면 중과를 피할 수 있습니다. 단, 계약만 하고 잔금을 5월 10일 이후에 치르면 중과 대상이 됩니다. 지금 당장 부동산 전문가와 상담하세요.`;

export default function InputPanel({
  blogText,
  onBlogTextChange,
  template,
  onTemplateChange,
  cardCount,
  onCardCountChange,
  onGenerate,
  isGenerating,
}: Props) {
  return (
    <div className="flex flex-col gap-5 h-full">
      {/* Blog Text Input */}
      <div className="flex-1 min-h-0">
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            블로그 글 입력
          </label>
          <button
            onClick={() => onBlogTextChange(SAMPLE_TEXT)}
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            예시 텍스트 불러오기
          </button>
        </div>
        <textarea
          value={blogText}
          onChange={e => onBlogTextChange(e.target.value)}
          placeholder="블로그 글을 붙여넣으세요. 자동으로 인스타 카드뉴스 스타일로 변환됩니다..."
          className="w-full h-[280px] bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white text-sm resize-none focus:outline-none focus:border-indigo-500 font-nanum leading-relaxed placeholder-gray-600"
        />
        <div className="mt-1 text-right text-xs text-gray-600">
          {blogText.length}자
        </div>
      </div>

      {/* Template Selection */}
      <div>
        <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          템플릿 선택
        </label>
        <div className="grid grid-cols-2 gap-2">
          {TEMPLATE_KEYS.map(key => {
            const t = TEMPLATES[key];
            const isActive = template === key;
            return (
              <button
                key={key}
                onClick={() => onTemplateChange(key)}
                className={`
                  relative px-3 py-2.5 rounded-lg text-left transition-all duration-200 overflow-hidden
                  ${isActive
                    ? 'border-2 text-white shadow-lg'
                    : 'border border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200'
                  }
                `}
                style={isActive ? {
                  borderColor: t.primaryColor,
                  background: `linear-gradient(135deg, ${t.bgGradient[0]}, ${t.bgGradient[1]})`,
                  boxShadow: `0 0 20px ${t.primaryColor}33`,
                } : { background: '#1a1a2e' }}
              >
                <span className="text-base mr-1">{t.icon}</span>
                <span className="text-xs font-medium">{t.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Card Count */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            카드 수
          </label>
          <span className="text-sm font-bold text-indigo-400">{cardCount}장</span>
        </div>
        <input
          type="range"
          min={4}
          max={10}
          value={cardCount}
          onChange={e => onCardCountChange(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>4장</span>
          <span>10장</span>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={onGenerate}
        disabled={!blogText.trim() || isGenerating}
        className={`
          w-full py-4 rounded-xl font-bold text-base transition-all duration-200
          ${blogText.trim() && !isGenerating
            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 hover:shadow-lg hover:shadow-indigo-500/30 active:scale-[0.98]'
            : 'bg-gray-800 text-gray-600 cursor-not-allowed'
          }
        `}
      >
        {isGenerating ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            카드뉴스 생성 중...
          </span>
        ) : (
          '✨ 카드뉴스 자동 생성'
        )}
      </button>
    </div>
  );
}
