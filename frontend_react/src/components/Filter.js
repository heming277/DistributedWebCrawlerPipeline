// frontend_react/components/Filter.js
import React from 'react';

const Filter = ({ sources, onFilterChange }) => {
    return (
        <select onChange={(e) => onFilterChange(e.target.value)}>
            <option value="All">All</option>
            {sources.map((source, index) => (
                <option key={index} value={source}>
                    {source}
                </option>
            ))}
        </select>
    );
};

export default Filter;