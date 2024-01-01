FROM python:3.8-slim

WORKDIR /usr/src/DistributedWebCrawlerPipeline

# Copy
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/DistributedWebCrawlerPipeline/webcrawler

# Run the crawler
CMD ["scrapy", "crawl", "ai_news_spider"]