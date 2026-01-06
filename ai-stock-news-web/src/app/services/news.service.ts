import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { StockNewsResponse } from '../models/stock-news.model';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NewsService {

  // OPTION A: Use this for Local Development (Computer)
   //private API_URL = 'http://127.0.0.1:8000'; 
  
  // OPTION B: Use this for Android Emulator
  // private API_URL = 'http://10.0.2.2:8000';

  // OPTION C: Your AWS / Cloud IP (Use this only if deployed)
  //private API_URL = 'http://3.138.191.140:8000'; 
  private API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getNews(symbol: string): Observable<StockNewsResponse> {
    // We remove the hardcoded '/news/' from API_URL and add it here
    // to keep the base URL clean.
    return this.http.get<StockNewsResponse>(`${this.API_URL}/news/${symbol}`);
  }
}