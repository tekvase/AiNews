export interface SentimentSummary {
  positive: number;
  negative: number;
  neutral: number;
  buy_score: number;
  // We change 'string' to specific values for better autocomplete
  signal: 'BUY' | 'SELL' | 'NEUTRAL'; 
}

export interface NewsItem {
  category: string;
  datetime: number;
  headline: string;
  id: number;
  image: string;
  related: string;
  source: string;
  summary: string;
  url: string;
  // This matches the specific sentiment strings from Python
  sentiment: 'positive' | 'negative' | 'neutral';
}

export interface StockNewsResponse {
  symbol: string;
  price: number;
  alert: boolean; // <--- ADDED THIS (matches backend)
  sentiment: SentimentSummary;
  news: NewsItem[];
}