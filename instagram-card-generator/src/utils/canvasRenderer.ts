import type { CardData, TemplateStyle } from '../types';

const CARD_WIDTH = 1080;
const CARD_HEIGHT = 1350;

function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number
): number {
  const lines = text.split('\n');
  let currentY = y;
  for (const line of lines) {
    const words = line.split('');
    let currentLine = '';
    for (const char of words) {
      const testLine = currentLine + char;
      const { width } = ctx.measureText(testLine);
      if (width > maxWidth && currentLine.length > 0) {
        ctx.fillText(currentLine, x, currentY);
        currentLine = char;
        currentY += lineHeight;
      } else {
        currentLine = testLine;
      }
    }
    ctx.fillText(currentLine, x, currentY);
    currentY += lineHeight;
  }
  return currentY;
}

function drawGradientBackground(
  ctx: CanvasRenderingContext2D,
  colors: string[],
  role: string
) {
  const gradient = ctx.createLinearGradient(0, 0, CARD_WIDTH, CARD_HEIGHT);
  gradient.addColorStop(0, colors[0]);
  gradient.addColorStop(1, colors[1]);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // Subtle diagonal overlay for depth
  const overlay = ctx.createLinearGradient(CARD_WIDTH, 0, 0, CARD_HEIGHT);
  overlay.addColorStop(0, 'rgba(255,255,255,0.03)');
  overlay.addColorStop(1, 'rgba(0,0,0,0.2)');
  ctx.fillStyle = overlay;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // CTA card gets special bottom-heavy gradient
  if (role === 'cta') {
    const radial = ctx.createRadialGradient(
      CARD_WIDTH / 2, CARD_HEIGHT * 0.8, 0,
      CARD_WIDTH / 2, CARD_HEIGHT * 0.8, CARD_WIDTH * 0.7
    );
    radial.addColorStop(0, 'rgba(255,255,255,0.08)');
    radial.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = radial;
    ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);
  }
}

function drawGrid(ctx: CanvasRenderingContext2D) {
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.04)';
  ctx.lineWidth = 1;
  for (let x = 0; x < CARD_WIDTH; x += 108) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, CARD_HEIGHT);
    ctx.stroke();
  }
  for (let y = 0; y < CARD_HEIGHT; y += 135) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(CARD_WIDTH, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawAccentLine(ctx: CanvasRenderingContext2D, style: TemplateStyle, y: number) {
  ctx.save();
  const grad = ctx.createLinearGradient(80, 0, CARD_WIDTH - 80, 0);
  grad.addColorStop(0, style.primaryColor);
  grad.addColorStop(0.5, style.accentColor);
  grad.addColorStop(1, style.primaryColor);
  ctx.fillStyle = grad;
  ctx.fillRect(80, y, CARD_WIDTH - 160, 4);
  ctx.restore();
}

function drawLabel(ctx: CanvasRenderingContext2D, style: TemplateStyle, text: string, y: number) {
  ctx.save();
  const padding = { x: 28, y: 14 };
  ctx.font = `700 32px "Nanum Gothic", sans-serif`;
  const textWidth = ctx.measureText(text).width;
  const boxW = textWidth + padding.x * 2;
  const boxH = 52;
  const x = 80;

  const grad = ctx.createLinearGradient(x, y, x + boxW, y);
  grad.addColorStop(0, style.primaryColor);
  grad.addColorStop(1, style.accentColor);
  ctx.fillStyle = grad;

  ctx.beginPath();
  ctx.roundRect(x, y, boxW, boxH, 8);
  ctx.fill();

  ctx.fillStyle = style.labelText;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x + padding.x, y + boxH / 2);
  ctx.restore();
}

function drawTitle(
  ctx: CanvasRenderingContext2D,
  style: TemplateStyle,
  text: string,
  role: string,
  startY: number
): number {
  ctx.save();
  const fontSize = role === 'hook' ? style.titleSize : style.titleSize - 6;
  ctx.font = `800 ${fontSize}px "Nanum Gothic", sans-serif`;
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';

  const lineHeight = fontSize * 1.35;
  const maxWidth = CARD_WIDTH - 160;
  const endY = wrapText(ctx, text, 80, startY, maxWidth, lineHeight);

  // Shadow glow on title
  ctx.shadowColor = style.primaryColor;
  ctx.shadowBlur = 20;
  wrapText(ctx, text, 80, startY, maxWidth, lineHeight);
  ctx.restore();

  return endY;
}

function drawEmphasis(ctx: CanvasRenderingContext2D, style: TemplateStyle, text: string, y: number): number {
  if (!text) return y;
  ctx.save();
  const boxH = 100;
  const boxW = CARD_WIDTH - 160;
  const x = 80;

  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.beginPath();
  ctx.roundRect(x, y, boxW, boxH, 12);
  ctx.fill();

  ctx.strokeStyle = style.accentColor;
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.font = `800 48px "Nanum Gothic", sans-serif`;
  ctx.fillStyle = style.accentColor;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = style.accentColor;
  ctx.shadowBlur = 15;
  ctx.fillText(text, CARD_WIDTH / 2, y + boxH / 2);
  ctx.restore();

  return y + boxH + 30;
}

function drawBodyLines(
  ctx: CanvasRenderingContext2D,
  style: TemplateStyle,
  lines: string[],
  startY: number,
  role: string
): number {
  ctx.save();
  const fontSize = role === 'hook' ? 38 : 36;
  const lineHeight = fontSize * 1.7;
  let y = startY;

  for (const line of lines) {
    if (y + lineHeight > CARD_HEIGHT - 200) break;

    const isEmoji = /^[🚨⚠️✅💾🔔📤📌💰🏠🏛️📈🤝💸💡👇]/.test(line);

    ctx.font = `${isEmoji ? '700' : '400'} ${fontSize}px "Nanum Gothic", sans-serif`;

    // Color for certain prefixes
    const isUrgent = /마감|긴급|⚠️/.test(line);
    const isMoney = /원|%/.test(line);
    const isCta = /💾|🔔|📤/.test(line);

    if (isUrgent) ctx.fillStyle = style.urgentColor;
    else if (isMoney) ctx.fillStyle = style.emphasisColor;
    else if (isCta) ctx.fillStyle = style.accentColor;
    else ctx.fillStyle = 'rgba(255,255,255,0.88)';

    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    const endY = wrapText(ctx, line, 80, y, CARD_WIDTH - 160, fontSize * 1.4);
    y = Math.max(endY, y + lineHeight);
  }

  ctx.restore();
  return y;
}

function drawPageNumber(ctx: CanvasRenderingContext2D, style: TemplateStyle, card: CardData) {
  ctx.save();
  const y = CARD_HEIGHT - 80;

  // Line
  ctx.strokeStyle = 'rgba(255,255,255,0.15)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(80, y - 20);
  ctx.lineTo(CARD_WIDTH - 80, y - 20);
  ctx.stroke();

  ctx.font = `400 28px "Nanum Gothic", sans-serif`;
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(card.category, 80, y + 10);

  ctx.textAlign = 'right';
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.fillText(`${card.pageNum} / ${card.totalPages}`, CARD_WIDTH - 80, y + 10);

  // Progress bar
  const barW = CARD_WIDTH - 160;
  const progress = (card.pageNum / card.totalPages) * barW;
  ctx.fillStyle = 'rgba(255,255,255,0.1)';
  ctx.fillRect(80, CARD_HEIGHT - 24, barW, 6);
  const barGrad = ctx.createLinearGradient(80, 0, 80 + progress, 0);
  barGrad.addColorStop(0, style.primaryColor);
  barGrad.addColorStop(1, style.accentColor);
  ctx.fillStyle = barGrad;
  ctx.fillRect(80, CARD_HEIGHT - 24, progress, 6);

  ctx.restore();
}

function drawHookDecoration(ctx: CanvasRenderingContext2D, style: TemplateStyle) {
  ctx.save();

  // Large icon background circle
  ctx.fillStyle = `${style.primaryColor}18`;
  ctx.beginPath();
  ctx.arc(CARD_WIDTH - 120, 180, 200, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = `${style.primaryColor}10`;
  ctx.beginPath();
  ctx.arc(CARD_WIDTH - 120, 180, 280, 0, Math.PI * 2);
  ctx.fill();

  // Corner accent
  ctx.strokeStyle = style.primaryColor;
  ctx.lineWidth = 3;
  ctx.globalAlpha = 0.3;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(120, 0);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(0, 120);
  ctx.stroke();

  ctx.restore();
}

function drawCtaDecoration(ctx: CanvasRenderingContext2D, style: TemplateStyle) {
  ctx.save();

  // Center glow
  const radial = ctx.createRadialGradient(
    CARD_WIDTH / 2, CARD_HEIGHT / 2, 0,
    CARD_WIDTH / 2, CARD_HEIGHT / 2, 500
  );
  radial.addColorStop(0, `${style.primaryColor}22`);
  radial.addColorStop(1, 'transparent');
  ctx.fillStyle = radial;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // Bottom save icon area
  ctx.font = '160px serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.globalAlpha = 0.15;
  ctx.fillText('💾', CARD_WIDTH / 2, CARD_HEIGHT * 0.65);

  ctx.restore();
}

export function renderCard(
  canvas: HTMLCanvasElement,
  card: CardData,
  style: TemplateStyle,
  scale = 1
) {
  canvas.width = CARD_WIDTH * scale;
  canvas.height = CARD_HEIGHT * scale;

  const ctx = canvas.getContext('2d')!;
  ctx.scale(scale, scale);

  // Background
  drawGradientBackground(ctx, style.bgGradient, card.role);
  drawGrid(ctx);

  // Role-specific decorations
  if (card.role === 'hook') drawHookDecoration(ctx, style);
  if (card.role === 'cta') drawCtaDecoration(ctx, style);

  let y = 80;

  // Label
  const labelText = `${card.icon} ${card.category}`;
  drawLabel(ctx, style, labelText, y);
  y += 80;

  // Accent line
  drawAccentLine(ctx, style, y);
  y += 30;

  // Title
  const titleEndY = drawTitle(ctx, style, card.title, card.role, y);
  y = titleEndY + 30;

  // Emphasis box
  if (card.emphasis) {
    y = drawEmphasis(ctx, style, card.emphasis, y) + 10;
  }

  // Body
  drawBodyLines(ctx, style, card.body, y, card.role);

  // Footer
  drawPageNumber(ctx, style, card);
}

export { CARD_WIDTH, CARD_HEIGHT };
