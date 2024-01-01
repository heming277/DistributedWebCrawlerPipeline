import scrapy
import pika
import json
from datetime import datetime
import re
from scrapy import Selector

class MySpider(scrapy.Spider):

    FINAL_MESSAGE = {"type": "final_message"}
    name = 'ai_news_spider'
    ARTICLE_LIMIT = 6
    start_urls = [
        'https://openai.com/blog',
        'https://ai.meta.com/blog',
        'https://news.microsoft.com/source/view-all/?_categories=ai',
        'https://blog.research.google',
        'https://aws.amazon.com/blogs/machine-learning',
        'https://machinelearning.apple.com/research',
        'https://mistral.ai/news'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 2, #add some delay between crawl 
    }


    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        # Initialize dictionary to keep count
        self.article_count = {
            'openai.com/blog': 0,
            'ai.meta.com/blog': 0,
            'news.microsoft.com/source/view-all/?_categories=ai': 0,
            'blog.research.google': 0,
            'aws.amazon.com/blogs/machine-learning': 0,
            'machinelearning.apple.com/research': 0,
            'mistral.ai/news': 0
        }

    def start_requests(self):
        # Set up RabbitMQ connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='scrapy_queue')
        # Continue with starting requests
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse_article_page(self, response):
        title = response.meta.get('title')
        link = response.meta.get('link')
        source_url = response.meta.get('source_url')

        # Use XPath to deal with Apple not giving complete date 
        tout_texts = response.xpath('//div[contains(@class, "font-weight-bold") and contains(@class, "typography-tout")]//text()').extract()

        # Join the text nodes to form a complete string
        tout_text = ''.join(tout_texts)

        # Use a regular expression to find the date
        date_match = re.search(r'published\s+([A-Za-z]+)\s+(\d{4})', tout_text)
        if date_match:
            #  assuming the 15th as the day
            date_text = f"{date_match.group(1)} 15 {date_match.group(2)}"
            try:
                date = datetime.strptime(date_text, '%B %d %Y').strftime('%Y-%m-%d')
            except ValueError as e:
                self.logger.error(f"Error parsing date: {e}")
                date = None
        else:
            date = None
            self.logger.warning(f"No date found on the page: {response.url}")
        
        yield self.create_data_dict(title, date, source_url, link)


    def parse(self, response):
        # Determine which site we are scraping
        if 'openai.com/blog' in response.url:
            # Custom parsing logic for OpenAI blog
            articles = response.css('li[class*="mt-spacing-6"]')  
            for article in articles:
                if self.article_count['openai.com/blog'] >= self.ARTICLE_LIMIT:
                    break
                title = article.css('h3::text').get()
                date = article.css('span[aria-hidden="true"]::text').get()
                link = article.css('a::attr(href)').get()  
                # Make the link relative
                if link:
                    link = response.urljoin(link)
                # Parse the date
                if date:
                    try:
                        date = datetime.strptime(date.strip(), '%b %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        # If the date format is not recognized, log a warning
                        self.logger.warning(f"Date format not recognized: {date}")
                self.article_count['openai.com/blog'] += 1
                yield self.create_data_dict(title, date, response.url, link)

        elif 'ai.meta.com/blog' in response.url:
            articles = response.css('div._8xiz')  
            for article in articles:
                if self.article_count['ai.meta.com/blog'] >= self.ARTICLE_LIMIT:
                    break
                title = article.css('div._8wpz > h4._8w6a._8w6e._8w61::text').get()
                date_text = article.css('div._8xkq > div._8xkn > p._8w6f._8xm4._8wl0._8w6h::text').get()
                link = article.css('div._8xko > a._8xc5._8x97._8w61::attr(href)').get()  # Extract the hyperlink
                if link:
                    link = response.urljoin(link)
                if date_text:
                    try:
                        date = datetime.strptime(date_text.strip(), '%B %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Date format not recognized: {date_text}")
                        date = None  
                self.article_count['ai.meta.com/blog'] += 1
                yield self.create_data_dict(title, date, response.url, link) 
        
        elif 'news.microsoft.com/source/view-all/?_categories=ai' in response.url:
            articles = response.css('div.fwpl-col')  
            for article in articles:
                if self.article_count['news.microsoft.com/source/view-all/?_categories=ai'] >= self.ARTICLE_LIMIT:
                    break
                title = article.css('div.el-fz703r.h2 a::text').get()
                date_text = article.css('div.kicker::text').get()
                link = article.css('div.el-fz703r.h2 a::attr(href)').get()  
                if link:
                    link = response.urljoin(link)
                if date_text:
                    try:
                        date = datetime.strptime(date_text.strip(), '%B %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Date format not recognized: {date_text}")
                        date = None  
                self.article_count['news.microsoft.com/source/view-all/?_categories=ai'] += 1
                yield self.create_data_dict(title, date, response.url, link)
        
        elif 'https://blog.research.google' in response.url:
            articles = response.css('div.blog-posts.hfeed.container > a.post-outer-container')  
            for article in articles:
                if self.article_count['blog.research.google'] >= self.ARTICLE_LIMIT:
                    break  
                title = article.attrib.get('aria-label', '').strip()
                link = article.attrib.get('href', '').strip()
                date_text = article.css('time::attr(datetime)').get('').strip()
                if link:
                    link = response.urljoin(link)
                date = None
                if date_text:
                    try:
                        date = datetime.fromisoformat(date_text).strftime('%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Date format not recognized: {date_text}")
                self.article_count['blog.research.google'] += 1
                yield self.create_data_dict(title, date, response.url, link)

        elif 'aws.amazon.com/blogs/machine-learning' in response.url:
            articles = response.css('article.blog-post')  
            for article in articles:
                if self.article_count['aws.amazon.com/blogs/machine-learning'] >= self.ARTICLE_LIMIT:
                    break  
                title = article.css('h2.blog-post-title span::text').get()
                date_text = article.css('time::attr(datetime)').get()
                link = article.css('h2.blog-post-title a::attr(href)').get()  
                if link:
                    link = response.urljoin(link)
                if date_text:
                    try:
                        date = datetime.strptime(date_text.strip(), '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Date format not recognized: {date_text}")
                        date = None  
                self.article_count['aws.amazon.com/blogs/machine-learning'] += 1
                yield self.create_data_dict(title, date, response.url, link)
        
        elif 'machinelearning.apple.com/research' in response.url:
            articles = response.css('li.post-row')  
            for article in articles:
                if self.article_count['machinelearning.apple.com/research'] >= self.ARTICLE_LIMIT:
                    break  
                title = article.css('h3.post-title a::text').get().strip()
                link = article.css('h3.post-title a::attr(href)').get()  
                if link:
                    link = response.urljoin(link)
                # Instead of yielding the result here, make a request to the article page
                # Pass the partially extracted data using the meta parameter
                yield scrapy.Request(link, callback=self.parse_article_page, meta={'title': title, 'link': link, 'source_url': response.url})
                self.article_count['machinelearning.apple.com/research'] += 1

        elif 'mistral.ai/news' in response.url:
            articles = response.css('article.news-card') 
            for article in articles:
                if self.article_count['mistral.ai/news'] >= self.ARTICLE_LIMIT:
                    break 
                title = article.css('h4.mb-3 a::text').get().strip()
                description = article.css('p::text').get().strip()
                full_title = f"{title}: {description}"
                date_text = article.css('li.list-inline-item.pr-4::text').get()
                if date_text:
                    try:
                        date = datetime.strptime(date_text, '%b %d, %Y').strftime('%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Date format not recognized: {date_text}")
                        date = None 
                link = article.css('h4.mb-3 a::attr(href)').get()
                if link:
                    link = response.urljoin(link)
                self.article_count['mistral.ai/news'] += 1
                yield self.create_data_dict(full_title, date, response.url, link)

    def create_data_dict(self, title, date, response_url, link=None):
        # Determine the source and source URL based on the response URL
        if 'openai.com/blog' in response_url:
            source = 'OpenAI'
            source_url = 'https://openai.com/blog'
        elif 'ai.meta.com/blog' in response_url:
            source = 'Meta AI'
            source_url = 'https://ai.meta.com/blog'
        elif 'news.microsoft.com/source/view-all/?_categories=ai' in response_url:
            source = 'Microsoft AI'
            source_url = 'https://news.microsoft.com/source/view-all/?_categories=ai'
        elif 'blog.research.google' in response_url:
            source = 'Google AI'
            source_url = 'https://blog.research.google'
        elif 'aws.amazon.com/blogs/machine-learning' in response_url:
            source = 'AWS Machine Learning'
            source_url = 'https://aws.amazon.com/blogs/machine-learning'
        elif 'machinelearning.apple.com/research' in response_url:
            source = 'Apple Machine Learning'
            source_url = 'https://machinelearning.apple.com/research'
        elif 'mistral.ai/news' in response_url:
            source = 'Mistral AI'
            source_url = 'https://mistral.ai/news'
        else:
            source = 'Unknown'
            source_url = response_url  # Fallback to the response URL

        # Output the scraped data
        data = {
            'title': title,
            'date': date,
            'source': source,
            'source_url': source_url,  # Add the source URL field
            'link': link
        }
        self.channel.basic_publish(exchange='',
                                routing_key='scrapy_queue',
                                body=json.dumps(data))
        return data


    def closed(self, reason):
    # Send the final message to the queue
        self.channel.basic_publish(exchange='',
                                routing_key='scrapy_queue',
                                body=json.dumps(self.FINAL_MESSAGE))
        # Close RabbitMQ connection
        self.connection.close()
