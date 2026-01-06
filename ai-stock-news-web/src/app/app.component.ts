import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NewsService } from './services/news.service';
// Import the strong type we created
import { StockNewsResponse } from './models/stock-news.model';

@Component({
  selector: 'app-root',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  symbol = '';
  loading = false;
  error = '';
  
  // instead of separate variables, we hold the whole response here
  stockData: StockNewsResponse | null = null;

  constructor(
    private newsService: NewsService,
    private cdr: ChangeDetectorRef
  ) {}

  search() {
    const trimmedSymbol = this.symbol.trim().toUpperCase();

    if (!trimmedSymbol) {
      this.error = 'Please enter a stock symbol.';
      return;
    }

    // Reset State
    this.loading = true;
    this.error = '';
    this.stockData = null; 
    
    // Trigger UI update manually because of OnPush
    this.cdr.detectChanges(); 

    this.newsService.getNews(trimmedSymbol).subscribe({
      next: (data: StockNewsResponse) => {
        this.stockData = data;
        this.loading = false;
        
        console.log('API RESPONSE:', this.stockData);
        
        // Update UI
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('API ERROR:', err);
        this.error = 'Failed to load news. Check if Backend is running.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  // Helper function for HTML to color the badges
  getSentimentColor(sentiment: string): string {
    switch (sentiment) {
      case 'positive': return 'success'; // Green
      case 'negative': return 'danger';  // Red
      case 'BUY': return 'success';
      case 'SELL': return 'danger';
      default: return 'medium';          // Grey
    }
  }
}