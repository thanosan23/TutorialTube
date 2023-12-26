//@ts-nocheck
import { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [addUrl, setAddUrl] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleAddSubmit = async (event : any) => {
    event.preventDefault();
    setIsLoading(true);
    const response = await fetch('http://localhost:5001/add_video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: addUrl }),
    });
    const data = await response.json();
    console.log(data);
    setIsLoading(false);
  };

  const handleSearchSubmit = async (event : any) => {
    event.preventDefault();
    setIsLoading(true);
    const response = await fetch(`http://localhost:5001/find_similar?query=${searchQuery}`, {
    });
    const data = await response.json();
    console.log(data);
    setSearchResults(data);
    setIsLoading(false);
  };

  return (
    <>
      <Head>
        <title>TutorialTube</title>
        <meta name="description" content="" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="p-10 bg-gray-100 min-h-screen">
        <h1 className="text-4xl font-bold mb-10">TutorialTube</h1>
        <form onSubmit={handleAddSubmit} className="mb-10">
          <input type="text" value={addUrl} onChange={(e) => setAddUrl(e.target.value)} placeholder="YouTube URL" required className="p-2 border border-gray-300 rounded w-full mb-4" />
          <button type="submit" className="p-2 bg-blue-500 text-white rounded w-full">Add Video</button>
        </form>
        <form onSubmit={handleSearchSubmit}>
          <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search Query" required className="p-2 border border-gray-300 rounded w-full mb-4" />
          <button type="submit" className="p-2 bg-blue-500 text-white rounded w-full">Search</button>
        </form>
        {isLoading ? (
          <div>Loading...</div>
        ) : searchResults.length === 0 ? (
          <div>No search results</div>
        ) : (
          searchResults.map((result, index) => (
            <div key={index} className="p-4 bg-white rounded shadow mt-10">
              <h2 className="text-xl font-bold mb-2">{result.video}</h2>
              <a href={result.url} className="text-blue-500 underline">Watch Video</a>
              <p className="mt-2">{result.answer}</p>
            </div>
          ))
        )}
      </main>
    </>
  );
}