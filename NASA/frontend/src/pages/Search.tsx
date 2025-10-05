import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { useSearch, useOrganisms, useMissions, useDatasets } from "../hooks/useNasaData";
import Loader from "../components/loader";
import { useNavigate } from "react-router-dom";

const Search: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [selectedOrganisms, setSelectedOrganisms] = useState<string[]>([]);
  const [selectedMissions, setSelectedMissions] = useState<string[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const { data: organisms } = useOrganisms();
  const { data: missions } = useMissions();
  const { data: initialDatasets, isLoading: initialLoading } = useDatasets(20); // Load initial datasets

  const filters = { query, organisms: selectedOrganisms, missions: selectedMissions };
  const { data: searchResults, isLoading: searchLoading } = useSearch(filters);
  
  // Use search results if searching, otherwise show initial datasets
  const hasFilters = query || selectedOrganisms.length > 0 || selectedMissions.length > 0;
  const results: any = hasFilters ? searchResults : initialDatasets;
  const isLoading = hasFilters ? searchLoading : initialLoading;

  // AI-powered search suggestions
  const suggestions = [
    "microgravity effects on cells",
    "radiation exposure studies", 
    "plant growth in space",
    "protein expression analysis",
    "bone density changes",
    "immune system response"
  ];
  
  const handleSearch = () => {
    setHasSearched(true);
  };

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-4 py-8 pt-24">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-nexuscyan mb-4">NEURAL SEARCH COMMAND</h1>
          <p className="text-lg text-astronautwhite/80">AI-powered semantic search</p>
        </div>

        <Card className="p-6 mb-8">
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Input placeholder="Search NASA OSDR..." value={query} onChange={(e) => setQuery(e.target.value)} />
            </div>
            <Button onClick={handleSearch} disabled={!query && selectedOrganisms.length === 0 && selectedMissions.length === 0}>Search</Button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-astronautwhite/70 mb-2 block">Organisms</label>
              <div className="flex flex-wrap gap-2">
                {((organisms as any)?.organisms || []).slice(0, 8).map((o: string) => (
                  <Badge key={o} className={`cursor-pointer ${selectedOrganisms.includes(o) ? "bg-accent text-space" : "border-accent/10"}`} onClick={() => {
                    setSelectedOrganisms(prev => prev.includes(o) ? prev.filter(x => x !== o) : [...prev, o]);
                  }}>{o}</Badge>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm text-astronautwhite/70 mb-2 block">Missions</label>
              <div className="flex flex-wrap gap-2">
                {((missions as any)?.missions || []).slice(0, 6).map((m: string) => (
                  <Badge key={m} className={`cursor-pointer ${selectedMissions.includes(m) ? "bg-accent text-space" : "border-accent/10"}`} onClick={() => {
                    setSelectedMissions(prev => prev.includes(m) ? prev.filter(x => x !== m) : [...prev, m]);
                  }}>{m}</Badge>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4">
            <label className="text-sm text-astronautwhite/70 mb-2 block">AI Suggestions</label>
            <div className="flex gap-2 flex-wrap">
              {suggestions.map(s => <Button key={s} variant="outline" onClick={() => setQuery(s)}>{s}</Button>)}
            </div>
          </div>
        </Card>

        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-astronautwhite">
              {isLoading ? "Loading..." : hasFilters ? "Search Results" : "Recent Datasets"}
            </h2>
            <div className="text-astronautwhite/60">
              {hasFilters 
                ? `${results?.count ?? results?.results?.length ?? 0} results`
                : `${results?.count ?? results?.data?.length ?? 0} datasets`
              }
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12"><Loader /></div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {/* Show search results or initial datasets */}
              {(hasFilters ? results?.results : results?.data)?.map((r: any) => (
                <Card 
                  key={r.id} 
                  className="p-4 hover:border-accent/30 cursor-pointer transition-all hover:scale-[1.02]"
                  onClick={() => navigate(`/dataset/${encodeURIComponent(r.id)}`)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-base font-medium text-astronautwhite line-clamp-2">{r.title}</h3>
                  </div>
                  <p className="text-sm text-astronautwhite/70 mb-3 line-clamp-2">{r.description || r.summary || "NASA space biology dataset"}</p>
                  <div className="flex items-center justify-between text-xs">
                    <div className="text-astronautwhite/60">ID: {r.id}</div>
                    {r.organism && <Badge variant="outline" className="text-xs">{r.organism}</Badge>}
                  </div>
                  {r.mission && <div className="text-xs text-neural mt-2">Mission: {r.mission}</div>}
                </Card>
              )) ?? []}
              {(hasFilters ? !results?.results?.length : !results?.data?.length) && (
                <Card className="p-8 text-center col-span-2">
                  <div className="text-astronautwhite/60">
                    {hasFilters ? "No results found. Try different search terms." : "No datasets available."}
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Search;
