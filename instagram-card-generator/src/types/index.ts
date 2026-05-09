export type TemplateType =
  | 'urgent'
  | 'government'
  | 'tax'
  | 'realestate'
  | 'economy'
  | 'welfare'
  | 'subsidy'
  | 'lifetip';

export type CardRole =
  | 'hook'
  | 'problem'
  | 'info'
  | 'caution'
  | 'cta';

export interface CardData {
  id: string;
  role: CardRole;
  category: string;
  title: string;
  body: string[];
  emphasis?: string;
  pageNum: number;
  totalPages: number;
  icon?: string;
}

export interface TemplateStyle {
  name: string;
  bgGradient: string[];
  bgType: 'gradient' | 'solid' | 'dark';
  primaryColor: string;
  accentColor: string;
  urgentColor: string;
  labelBg: string;
  labelText: string;
  icon: string;
  titleSize: number;
  emphasisColor: string;
}

export interface GeneratedContent {
  cards: CardData[];
  template: TemplateType;
}
