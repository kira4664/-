import type { CardData, TemplateType } from '../types';
import { TEMPLATES } from '../data/templates';

const EMPHASIS_PATTERNS = [
  /\d{4}년\s*\d{1,2}월\s*\d{1,2}일/g,
  /\d{1,2}월\s*\d{1,2}일/g,
  /\d+,?\d*만?\s*원/g,
  /\d+\.?\d*%/g,
  /최대\s*\d+/g,
  /D-\d+/g,
  /마감/g,
  /긴급/g,
  /폐지/g,
  /부활/g,
  /시행/g,
  /신청/g,
];

const URGENT_WORDS = ['마감', '긴급', '폐지', '부활', '시행', '즉시', '당장', '오늘만', '한시적'];
const MONEY_WORDS = ['원', '%', '만원', '억'];
const DATE_WORDS = ['년', '월', '일', 'D-'];

export function detectEmphasisType(text: string): 'urgent' | 'money' | 'date' | 'normal' {
  if (URGENT_WORDS.some(w => text.includes(w))) return 'urgent';
  if (MONEY_WORDS.some(w => text.includes(w))) return 'money';
  if (DATE_WORDS.some(w => text.includes(w))) return 'date';
  return 'normal';
}

function splitSentences(text: string): string[] {
  return text
    .split(/[.。\n]+/)
    .map(s => s.trim())
    .filter(s => s.length > 3);
}

function shortenSentence(sentence: string): string {
  sentence = sentence.trim();

  // Date patterns → compact
  sentence = sentence.replace(/(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일/g, '$1.$2.$3');
  sentence = sentence.replace(/(\d{1,2})월\s*(\d{1,2})일/g, '$1월 $2일');

  // Trim filler phrases
  const fillers = [
    '있습니다', '합니다', '됩니다', '것입니다', '하겠습니다',
    '예정입니다', '라고 합니다', '라고 밝혔습니다', '에 따르면',
    '따라서', '그러므로', '이에', '또한', '한편',
  ];
  fillers.forEach(f => {
    sentence = sentence.replace(new RegExp(f + '$'), '');
  });

  sentence = sentence.replace(/^(▶|•|·|\*|-)\s*/, '');

  if (sentence.length > 24) {
    // Find natural break
    const breakpoints = ['은 ', '는 ', '이 ', '가 ', '을 ', '를 ', '에서 ', '로 '];
    for (const bp of breakpoints) {
      const idx = sentence.indexOf(bp, 10);
      if (idx > 0 && idx < 20) {
        return sentence.slice(0, idx + bp.length - 1) + '\n' + sentence.slice(idx + bp.length);
      }
    }
    // Hard break at 20 chars
    return sentence.slice(0, 20) + '\n' + sentence.slice(20, 40);
  }

  return sentence;
}

function extractKeyNumbers(text: string): string[] {
  const patterns = [
    /\d{4}년\s*\d{1,2}월\s*\d{1,2}일/g,
    /\d{1,2}월\s*\d{1,2}일/g,
    /\d+,?\d*만\s*원/g,
    /\d+\.?\d*%/g,
    /최대\s*\d+[만억]?\s*원?/g,
    /D-\d+/g,
  ];
  const found: string[] = [];
  patterns.forEach(p => {
    const m = text.match(p);
    if (m) found.push(...m);
  });
  return [...new Set(found)].slice(0, 3);
}

function buildHookCard(sentences: string[], template: TemplateType, totalPages: number): CardData {
  const style = TEMPLATES[template];
  const firstSentence = sentences[0] || '';
  const numbers = extractKeyNumbers(sentences.slice(0, 3).join(' '));

  let title = '';
  let body: string[] = [];

  if (numbers.length > 0) {
    title = shortenSentence(firstSentence) || '놓치면 손해\n지금 확인하세요';
    body = [
      numbers[0] ? `📌 핵심 키워드: ${numbers[0]}` : '',
      numbers[1] ? `📌 ${numbers[1]}` : '',
      '👇 지금 바로 확인하세요',
    ].filter(Boolean);
  } else {
    const raw = firstSentence || sentences[1] || '';
    title = shortenSentence(raw) || '중요한 정보\n지금 확인';
    body = ['지금 확인 안 하면 손해', '저장 후 천천히 읽어보세요 💾'];
  }

  return {
    id: 'card-1',
    role: 'hook',
    category: style.name,
    title,
    body,
    emphasis: numbers[0],
    pageNum: 1,
    totalPages,
    icon: style.icon,
  };
}

function buildProblemCard(sentences: string[], template: TemplateType, totalPages: number): CardData {
  const style = TEMPLATES[template];
  const relevant = sentences.slice(1, 4);
  const title = shortenSentence(relevant[0] || '현재 상황');
  const body = relevant.slice(1, 4).map(s => `• ${shortenSentence(s)}`);

  if (body.length === 0) body.push('• 이 내용 모르면 손해입니다');

  return {
    id: 'card-2',
    role: 'problem',
    category: style.name,
    title: title || '왜 중요한가?',
    body,
    pageNum: 2,
    totalPages,
    icon: style.icon,
  };
}

function buildInfoCards(
  sentences: string[],
  template: TemplateType,
  count: number,
  startPage: number,
  totalPages: number
): CardData[] {
  const style = TEMPLATES[template];
  const infoSentences = sentences.slice(3);
  const chunkSize = Math.ceil(infoSentences.length / count);
  const cards: CardData[] = [];

  const infoLabels = ['조건', '일정', '금액', '대상', '신청방법', '체크포인트'];

  for (let i = 0; i < count; i++) {
    const chunk = infoSentences.slice(i * chunkSize, (i + 1) * chunkSize);
    if (chunk.length === 0) continue;

    const title = shortenSentence(chunk[0]) || infoLabels[i % infoLabels.length];
    const body = chunk.slice(1, 4).map(s => `✅ ${shortenSentence(s)}`);

    const numbers = extractKeyNumbers(chunk.join(' '));

    cards.push({
      id: `card-${startPage + i}`,
      role: 'info',
      category: style.name,
      title,
      body: body.length > 0 ? body : [`✅ ${infoLabels[i % infoLabels.length]} 확인 필수`],
      emphasis: numbers[0],
      pageNum: startPage + i,
      totalPages,
      icon: style.icon,
    });
  }

  return cards;
}

function buildCautionCard(sentences: string[], template: TemplateType, page: number, totalPages: number): CardData {
  const style = TEMPLATES[template];
  const cautionSentences = sentences.filter(s =>
    /주의|금지|안 되|하지 마|실수|놓치|조심|확인/.test(s)
  ).slice(0, 4);

  const body =
    cautionSentences.length > 0
      ? cautionSentences.map(s => `⚠️ ${shortenSentence(s)}`)
      : ['⚠️ 신청 기간 반드시 확인', '⚠️ 서류 미비 시 탈락 주의', '⚠️ 중복 신청 불가'];

  return {
    id: `card-${page}`,
    role: 'caution',
    category: style.name,
    title: '이것만은\n꼭 확인하세요',
    body,
    pageNum: page,
    totalPages,
    icon: style.icon,
  };
}

function buildCtaCard(template: TemplateType, totalPages: number): CardData {
  const style = TEMPLATES[template];
  return {
    id: `card-${totalPages}`,
    role: 'cta',
    category: style.name,
    title: '지금 저장하세요\n나중에 찾기 어렵습니다',
    body: [
      '💾 저장 필수',
      '🔔 팔로우하면 먼저 알 수 있어요',
      '📤 주변 사람들에게 공유해 주세요',
    ],
    emphasis: '저장 필수',
    pageNum: totalPages,
    totalPages,
    icon: style.icon,
  };
}

export function processText(
  blogText: string,
  template: TemplateType,
  cardCount: number
): CardData[] {
  const sentences = splitSentences(blogText);
  if (sentences.length === 0) return [];

  const totalPages = cardCount;
  const infoCardCount = Math.max(1, cardCount - 4); // hook + problem + caution + cta = 4

  const cards: CardData[] = [];

  cards.push(buildHookCard(sentences, template, totalPages));

  if (cardCount >= 3) {
    cards.push(buildProblemCard(sentences, template, totalPages));
  }

  const infoCards = buildInfoCards(sentences, template, infoCardCount, 3, totalPages);
  cards.push(...infoCards);

  if (cardCount >= 4) {
    cards.push(buildCautionCard(sentences, template, cards.length + 1, totalPages));
  }

  cards.push(buildCtaCard(template, totalPages));

  // Fix page numbers
  return cards.slice(0, totalPages).map((c, i) => ({
    ...c,
    pageNum: i + 1,
    totalPages,
    id: `card-${i + 1}`,
  }));
}

export function hasEmphasisPatterns(text: string): boolean {
  return EMPHASIS_PATTERNS.some(p => p.test(text));
}

export function highlightEmphasis(text: string): Array<{ text: string; highlight: boolean; type: string }> {
  const parts: Array<{ text: string; highlight: boolean; type: string }> = [];
  let lastIndex = 0;

  const allMatches: Array<{ start: number; end: number; text: string; type: string }> = [];

  const patterns: Array<{ re: RegExp; type: string }> = [
    { re: /\d{1,2}월\s*\d{1,2}일/g, type: 'date' },
    { re: /\d+,?\d*만?\s*원/g, type: 'money' },
    { re: /\d+\.?\d*%/g, type: 'money' },
    { re: /최대\s*\d+[만억]?\s*원?/g, type: 'money' },
    { re: /D-\d+/g, type: 'urgent' },
    { re: /마감|긴급|즉시|오늘만/g, type: 'urgent' },
  ];

  patterns.forEach(({ re, type }) => {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text)) !== null) {
      allMatches.push({ start: m.index, end: m.index + m[0].length, text: m[0], type });
    }
  });

  allMatches.sort((a, b) => a.start - b.start);

  for (const match of allMatches) {
    if (match.start > lastIndex) {
      parts.push({ text: text.slice(lastIndex, match.start), highlight: false, type: 'normal' });
    }
    if (match.start >= lastIndex) {
      parts.push({ text: match.text, highlight: true, type: match.type });
      lastIndex = match.end;
    }
  }

  if (lastIndex < text.length) {
    parts.push({ text: text.slice(lastIndex), highlight: false, type: 'normal' });
  }

  return parts.length > 0 ? parts : [{ text, highlight: false, type: 'normal' }];
}
