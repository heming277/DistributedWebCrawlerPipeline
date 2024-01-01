// src/App.js
import React from 'react';
import './App.css';
import ArticleList from './components/ArticleList'; 

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI and Tech News</h1>
      </header>
      <main>
        <ArticleList />
      </main>
    </div>
  );
}

export default App;
