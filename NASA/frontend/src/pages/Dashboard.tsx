import React from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import MissionCard from "../components/MissionCard";
import { QuickLaunch } from "./_shared/QuickLaunch";
import { useDatasets, useInsights } from "../hooks/useNasaData";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: datasets, isLoading: datasetsLoading } = useDatasets(50);
  const { data: insights } = useInsights();
  const loadedCount = datasets?.count ?? datasets?.data?.length ?? 0;
  const totalCount = datasets?.total ?? 138000;

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-4 py-8 pt-24">
        <div className="relative mb-12 overflow-hidden rounded-2xl bg-black/20 backdrop-blur-md border border-neural/10 p-8">
          <div className="absolute inset-0 bg-gradient-to-r from-neural/5 to-mission/5"></div>
          <div className="relative z-10">
            <p className="text-lg text-astronautwhite/80 mb-6">Real-time exploration of {totalCount}+ NASA datasets with AI-powered insights</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-4 rounded-lg bg-nexuscyan/10 border border-nexuscyan/30">
                <div className="text-2xl font-bold text-nexuscyan">{loadedCount}</div>
                <div className="text-sm text-astronautwhite/70">Loaded Datasets</div>
              </div>
              <div className="p-4 rounded-lg bg-nexuscyan/10 border border-nexuscyan/30">
                <div className="text-2xl font-bold text-nexuscyan">{totalCount.toLocaleString()}</div>
                <div className="text-sm text-astronautwhite/70">Total in OSDR</div>
              </div>
              <div className="p-4 rounded-lg bg-nexuscyan/10 border border-nexuscyan/30">
                <div className="text-2xl font-bold text-nexuscyan">{(insights as any)?.insights?.length || 3}</div>
                <div className="text-sm text-astronautwhite/70">AI Insights</div>
              </div>
              <div className="p-4 rounded-lg bg-nexuscyan/10 border border-nexuscyan/30">
                <div className="text-2xl font-bold text-nexuscyan">LIVE</div>
                <div className="text-sm text-astronautwhite/70">System Status</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8 p-6 rounded-xl bg-space/40 border border-accent/10">
          <h2 className="text-xl font-semibold text-astronautwhite mb-2">AI Insights</h2>
          <div className="grid gap-2">
            {insights?.insights?.length ? (
              insights.insights.map((s: string, idx: number) => <p key={idx} className="text-astronautwhite/70">• {s}</p>)
            ) : (
              <p className="text-astronautwhite/70">No insights available</p>
            )}
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-astronautwhite mb-6">Recent Datasets</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {datasetsLoading ? (
              Array.from({ length: 12 }).map((_, i) => <div key={i} className="h-32 bg-nexuscyan/10 rounded-xl animate-pulse border border-nexuscyan/20" />)
            ) : (
              (datasets?.data || []).slice(0, 50).map((d: any) => (
                <MissionCard
                  key={d.id || JSON.stringify(d).slice(0, 6)}
                  title={d.title || d.name || "Untitled Dataset"}
                  subtitle={d.mission || d.mission_name}
                  description={d.description || d.summary || ""}
                  onClick={() => navigate(`/dataset/${encodeURIComponent(d.id || d._id || d.dataset_id || d.name)}`)}
                />
              ))
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <QuickLaunch to="/laboratory" title="Knowledge Graph Lab" description="Explore AI-powered biological relationships" />
          <QuickLaunch to="/search" title="Neural Search" description="Semantic search with natural language" />
          <QuickLaunch to="/training" title="AI Training Ground" description="Model management & insights" />
          <QuickLaunch to="/publication" title="Publication Analysis" description="AI-powered research summaries" />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
