// frontend_react/components/ArticleList.js
import React, { useState, useEffect } from 'react';
import Article from './Article';
import Filter from './Filter';
import './ArticleList.css';

function ArticleList() {
  const [articles, setArticles] = useState([]);
  const [filteredArticles, setFilteredArticles] = useState([]);
  const [filter, setFilter] = useState('All');
  const [sortCriteria, setSortCriteria] = useState('dateNewest');

  // Fetch articles from the server
  useEffect(() => {
    fetch('/api/articles')
      .then(response => response.json())
      .then(data => {
        setArticles(data);
        setFilteredArticles(data);
      })
      .catch(error => console.error('Error fetching data: ', error));
  }, []);

  // Function to sort articles
  const sortArticles = (articles, criteria) => {
    switch (criteria) {
      case 'dateNewest':
        return [...articles].sort((a, b) => new Date(b.date) - new Date(a.date));
      case 'dateOldest':
        return [...articles].sort((a, b) => new Date(a.date) - new Date(b.date));
      case 'company':
        return [...articles].sort((a, b) => a.source.localeCompare(b.source));
      default:
        return articles;
    }
  };

  useEffect(() => {
    let filtered = articles;
    if (filter !== 'All') {
      filtered = articles.filter(article => article.source === filter);
    }
    setFilteredArticles(sortArticles(filtered, sortCriteria));
  }, [filter, articles, sortCriteria]);

  const handleFilterChange = (source) => {
    setFilter(source);
  };

  const sources = [...new Set(articles.map(article => article.source))];

  return (
    <div className="article-list">
      <Filter sources={sources} onFilterChange={handleFilterChange} />
      <select className="sort-dropdown" value={sortCriteria} onChange={(e) => setSortCriteria(e.target.value)}>
        <option value="dateNewest">Sort by Date (Newest to Oldest)</option>
        <option value="dateOldest">Sort by Date (Oldest to Newest)</option>
        <option value="company">Sort by Company</option>
      </select>
      {filteredArticles.map(article => (
        <Article key={article.id} {...article} />
      ))}
    </div>
  );
}

export default ArticleList;
