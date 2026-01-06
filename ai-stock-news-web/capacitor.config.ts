import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.myapp.ai.stocknews',
  appName: 'AI STOCKS',
  webDir: 'dist/ai-stock-news-web/browser',

  plugins: {
    CapacitorHttp: {
      enabled: true
    }
  }
};

export default config;
