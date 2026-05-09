import type { CardData } from '../types';

interface Props {
  card: CardData;
  onChange: (updated: CardData) => void;
}

export default function CardEditor({ card, onChange }: Props) {
  const updateTitle = (value: string) => onChange({ ...card, title: value });
  const updateBody = (index: number, value: string) => {
    const newBody = [...card.body];
    newBody[index] = value;
    onChange({ ...card, body: newBody });
  };
  const addBodyLine = () => onChange({ ...card, body: [...card.body, ''] });
  const removeBodyLine = (index: number) => {
    onChange({ ...card, body: card.body.filter((_, i) => i !== index) });
  };
  const updateEmphasis = (value: string) => onChange({ ...card, emphasis: value });

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          제목
        </label>
        <textarea
          value={card.title}
          onChange={e => updateTitle(e.target.value)}
          rows={2}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm resize-none focus:outline-none focus:border-indigo-500 font-nanum"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          강조 문구
        </label>
        <input
          type="text"
          value={card.emphasis || ''}
          onChange={e => updateEmphasis(e.target.value)}
          placeholder="숫자, 날짜, 금액 등"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 font-nanum"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            본문 내용
          </label>
          <button
            onClick={addBodyLine}
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            + 줄 추가
          </button>
        </div>
        <div className="space-y-2">
          {card.body.map((line, i) => (
            <div key={i} className="flex gap-2">
              <input
                type="text"
                value={line}
                onChange={e => updateBody(i, e.target.value)}
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 font-nanum"
              />
              <button
                onClick={() => removeBodyLine(i)}
                className="text-gray-500 hover:text-red-400 transition-colors px-2"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
