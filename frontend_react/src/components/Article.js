function Article({ title, link, source, date, source_url }) { 
    // Function to format the date based on the source
    const formatDate = (source, date) => {
        const dateObject = new Date(date);
        // Convert the date object to UTC 
        const utcDate = new Date(dateObject.getTime() + dateObject.getTimezoneOffset() * 60000);
        return utcDate.toLocaleDateString();
    };
    return (
        <div className="article">
            <h2>
                <a href={link} target="_blank" rel="noopener noreferrer">
                    {title}
                </a>
            </h2>
            <p>
                <a href={source_url} target="_blank" rel="noopener noreferrer">
                    {source}
                </a> - {formatDate(source, date)}
            </p>
        </div>
    );
}

export default Article;
