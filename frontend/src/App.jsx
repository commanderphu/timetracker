// src/App.jsx

import { useState, useEffect, useMemo } from 'react';

const API_BASE_URL = "https://timetracker-backend-f7hj.onrender.com";

// Hilfsfunktion zur Formatierung
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-';
  const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
  return new Date(dateTimeString).toLocaleString('de-DE', options);
};

function App() {
  const [user, setUser] = useState(null);
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Memoisierten Wert, um den aktuellen Status zu ermitteln.
  // Das verhindert unnötige Neuberechnungen.
  const activeEntry = useMemo(() => entries.find(entry => entry.end_time === null), [entries]);

  // Funktion zum Laden aller Daten
  const fetchAllData = async () => {
    // Fehler zurücksetzen, aber nicht den Ladezustand, um Flackern zu vermeiden
    setError(null);
    try {
      const [userResponse, entriesResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/user/me`),
        fetch(`${API_BASE_URL}/api/entries`)
      ]);
      if (!userResponse.ok) throw new Error('Benutzer konnte nicht geladen werden.');
      if (!entriesResponse.ok) throw new Error('Zeiteinträge konnten nicht geladen werden.');
      
      const userData = await userResponse.json();
      const entriesData = await entriesResponse.json();
      
      setUser(userData);
      setEntries(entriesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // Gemeinsame Handler-Logik
  const handleApiCall = async (endpoint) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Ein Fehler ist aufgetreten.');
      await fetchAllData(); // Alle Daten neu laden für einen konsistenten Zustand
    } catch (err) {
      setError(err.message);
      setIsLoading(false); // Ladezustand im Fehlerfall beenden
    }
  };

  const handleStart = () => handleApiCall('/api/start');
  const handleStop = () => handleApiCall('/api/stop');
  
  if (isLoading && !user) {
    return <div className="bg-gray-800 text-white min-h-screen flex items-center justify-center"><p>Lade TimeTracker...</p></div>;
  }

  return (
    <div className={`min-h-screen font-sans transition-colors ${activeEntry ? 'bg-green-800' : 'bg-gray-800'}`}>
      <div className="container mx-auto max-w-2xl p-4 text-white">
        
        <header className="text-center py-4">
          <h1 className="text-2xl font-bold">{user?.name || 'TimeTracker'}</h1>
          <div className="mt-4 text-5xl font-bold tracking-wider">
            {activeEntry ? 'AKTIV' : 'PAUSIERT'}
          </div>
          {activeEntry && <p className="mt-2">seit {formatDateTime(activeEntry.start_time)}</p>}
        </header>
        
        <main className="my-8">
           {/* Der große Start/Stop Button */}
           {activeEntry ? (
              <button onClick={handleStop} disabled={isLoading} className="w-full py-8 text-3xl font-bold bg-red-600 rounded-2xl shadow-lg hover:bg-red-700 disabled:bg-gray-500 transform active:scale-95">
                STOP
              </button>
           ) : (
             <button onClick={handleStart} disabled={isLoading} className="w-full py-8 text-3xl font-bold bg-green-600 rounded-2xl shadow-lg hover:bg-green-700 disabled:bg-gray-500 transform active:scale-95">
                START
              </button>
           )}
           {error && <div className="mt-4 p-3 rounded-lg bg-red-200 text-red-900 text-center font-semibold">{error}</div>}
        </main>
        
        <section>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold">Ihre Einträge</h2>
            <button onClick={fetchAllData} disabled={isLoading} className="p-2 rounded-full hover:bg-white/20 active:bg-white/30">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 110 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          <div className="space-y-2">
            {entries.length > 0 ? entries.map(entry => (
              <div key={entry.id} className="bg-white/10 p-3 rounded-lg flex justify-between items-center">
                <div>
                  <p className="font-semibold">{new Date(entry.start_time).toLocaleDateString('de-DE', {weekday: 'short', day: '2-digit', month: '2-digit'})}</p>
                  <p className="text-sm opacity-80">{formatDateTime(entry.start_time).split(', ')[1]} - {entry.end_time ? formatDateTime(entry.end_time).split(', ')[1] : '...'}</p>
                </div>
              </div>
            )) : <p className="text-center p-4 opacity-70">Keine Einträge vorhanden.</p>}
          </div>
        </section>

      </div>
    </div>
  );
}

export default App;
