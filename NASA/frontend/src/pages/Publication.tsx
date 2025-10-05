import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { nasaApi } from "../services/nasaApi";

const Publication: React.FC = () => {
  const [textToSummarize, setTextToSummarize] = useState("");
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    if (!textToSummarize.trim()) return;
    
    setLoading(true);
    try {
      const result = await nasaApi.summarize(textToSummarize);
      setSummary(result);
    } catch (error) {
      console.error('Summarization failed:', error);
      setSummary({ error: 'Failed to generate summary' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-space to-spacestation">
      <Navbar />
      <div className="pt-24 pb-12 container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-astronautwhite mb-2">AI PUBLICATION ANALYZER</h1>
          <p className="text-lg text-astronautwhite/80">AI-powered research paper summarization and analysis</p>
        </div>

        <Card className="p-6 mb-8 bg-space/40 backdrop-blur-sm border border-neural/20">
          <h2 className="text-xl font-bold text-astronautwhite mb-4 flex items-center gap-2">
            <div className="w-2 h-2 bg-neural rounded-full animate-pulse"></div>
            AI Text Analyzer
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-astronautwhite/70 mb-2 block">Enter research text or abstract:</label>
              <textarea
                className="w-full h-32 p-3 bg-space/60 border border-neural/30 rounded-lg text-astronautwhite placeholder-astronautwhite/40 resize-none focus:border-neural focus:outline-none"
                placeholder="Paste research paper abstract, methodology, or any scientific text here for AI analysis..."
                value={textToSummarize}
                onChange={(e) => setTextToSummarize(e.target.value)}
              />
            </div>
            <Button 
              onClick={handleSummarize} 
              disabled={!textToSummarize.trim() || loading}
              className="bg-neural hover:bg-neural/80 text-space"
            >
              {loading ? 'Analyzing...' : 'Generate AI Summary'}
            </Button>
          </div>
        </Card>

        {summary && (
          <Card className="p-6 mb-8 bg-space/40 backdrop-blur-sm border border-mission/20">
            <h2 className="text-xl font-bold text-astronautwhite mb-4 flex items-center gap-2">
              <div className="w-2 h-2 bg-mission rounded-full animate-pulse"></div>
              AI Analysis Results
            </h2>
            
            {summary.error ? (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400">Error: {summary.error}</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-mission/20 text-mission border-mission/30">
                    Provider: {summary.provider || 'AI'}
                  </Badge>
                  {summary.model && (
                    <Badge className="bg-neural/20 text-neural border-neural/30">
                      Model: {summary.model}
                    </Badge>
                  )}
                </div>
                
                <div className="bg-space/60 border border-neural/30 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-astronautwhite mb-2">Summary:</h3>
                  <div className="text-astronautwhite/80 whitespace-pre-wrap">
                    {summary.summary || 'No summary generated'}
                  </div>
                </div>
                
                {summary.note && (
                  <div className="text-sm text-astronautwhite/60 italic">
                    Note: {summary.note}
                  </div>
                )}
              </div>
            )}
          </Card>
        )}
        
        <Card className="p-6 bg-space/40 backdrop-blur-sm border border-neural/20">
          <h2 className="text-lg font-bold text-astronautwhite mb-4">About AI Publication Analyzer</h2>
          <div className="text-astronautwhite/70 space-y-2">
            <p>This tool uses advanced AI to analyze and summarize scientific research papers related to NASA space biology studies.</p>
            <p>Features include:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>AI-powered text summarization</li>
              <li>Key findings extraction</li>
              <li>Research methodology analysis</li>
              <li>Scientific context understanding</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Publication;
