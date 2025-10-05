import React, { useState, useMemo } from "react";
import Navbar from "../components/Navbar";
import { useKnowledgeGraph } from "../hooks/useNasaData";
import GraphViewport from "../components/GraphViewport";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";

const Laboratory: React.FC = () => {
  const { data: graphData, isLoading } = useKnowledgeGraph(200);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [filterType, setFilterType] = useState<string>("all");

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  const filteredNodes = useMemo(() => {
    if (filterType === "all") return nodes;
    return nodes.filter((n: any) => (n.type || "").toLowerCase() === filterType);
  }, [nodes, filterType]);

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      <div className="container mx-auto px-4 py-8 pt-24">
        <div className="text-center mb-8">
          <div className="inline-block p-1 rounded-xl bg-gradient-to-r from-nexuscyan to-nexuscyan/50 mb-4">
            <h1 className="text-4xl font-bold text-nexuscyan px-6 py-3 bg-black rounded-lg">
              KNOWLEDGE GRAPH LABORATORY
            </h1>
          </div>
          <p className="text-lg text-astronautwhite/80">Interactive AI-powered biological relationship visualization</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <Card className="p-6 h-[680px] bg-black/40 backdrop-blur-sm border border-nexuscyan/20">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-astronautwhite flex items-center gap-2">
                  <div className="w-2 h-2 bg-neural rounded-full animate-pulse"></div>
                  Knowledge Graph Observatory
                </h3>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setFilterType("all")}
                    className="border-neural/30 text-neural hover:bg-neural/10"
                  >
                    Reset View
                  </Button>
                </div>
              </div>

              <div className="relative w-full h-[560px] rounded-lg border border-neural/20 overflow-hidden bg-gradient-to-br from-space/50 to-spacestation/50">
                {isLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="w-8 h-8 border-2 border-neural border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <div className="text-astronautwhite/70">Loading knowledge graph...</div>
                    </div>
                  </div>
                ) : (
                  <GraphViewport nodes={filteredNodes} edges={edges} onNodeClick={(n) => setSelectedNode(n)} />
                )}
              </div>

              <div className="flex items-center justify-between mt-4">
                <div className="flex gap-2">
                  {["all", "experiment", "organism", "mission", "publication"].map((t) => (
                    <Button key={t} variant={filterType === t ? "default" : "outline"} size="sm" onClick={() => setFilterType(t)}>{t === "all" ? "All" : `${t}s`}</Button>
                  ))}
                </div>
                <div className="text-sm text-astronautwhite/60">{graphData ? `${graphData.nodes.length} nodes • ${graphData.edges.length} connections` : ""}</div>
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            {selectedNode && (
              <Card className="p-4">
                <h4 className="font-medium text-astronautwhite mb-2">Selected Entity</h4>
                <div className="space-y-2">
                  <div className="text-sm"><span className="text-astronautwhite/60">Name: </span><span className="text-astronautwhite">{selectedNode.label}</span></div>
                  <div className="text-sm"><span className="text-astronautwhite/60">Type: </span><span className="text-astronautwhite">{selectedNode.type}</span></div>
                  <div className="text-sm"><span className="text-astronautwhite/60">ID: </span><span className="text-astronautwhite">{selectedNode.id}</span></div>
                </div>
              </Card>
            )}

            <Card className="p-4">
              <h4 className="font-medium text-astronautwhite mb-3">Graph Statistics</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded bg-neural/10">
                  <span className="text-sm text-astronautwhite/70">Total Nodes</span>
                  <span className="text-lg font-bold text-neural">{nodes.length}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-mission/10">
                  <span className="text-sm text-astronautwhite/70">Total Connections</span>
                  <span className="text-lg font-bold text-mission">{edges.length}</span>
                </div>
                <div className="space-y-1 pt-2 border-t border-astronautwhite/10">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-astronautwhite/60">Studies</span>
                    <span className="text-astronautwhite font-medium">{nodes.filter((n: any) => n.type === 'study').length}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-astronautwhite/60">Organisms</span>
                    <span className="text-astronautwhite font-medium">{nodes.filter((n: any) => n.type === 'organism').length}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-astronautwhite/60">Missions</span>
                    <span className="text-astronautwhite font-medium">{nodes.filter((n: any) => n.type === 'mission').length}</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <h4 className="font-medium text-astronautwhite mb-3">Top Organisms</h4>
              <div className="space-y-2">
                {nodes.filter((n: any) => n.type === 'organism').slice(0, 5).map((entity: any) => (
                  <div key={entity.id} className="p-2 rounded cursor-pointer hover:bg-accent/10 transition-colors border border-neural/10" onClick={() => setSelectedNode(entity)}>
                    <div className="text-sm font-medium text-astronautwhite truncate">{entity.label}</div>
                    <div className="text-xs text-neural">Organism</div>
                  </div>
                ))}
                {nodes.filter((n: any) => n.type === 'organism').length === 0 && (
                  <div className="text-xs text-astronautwhite/60 text-center py-2">No organisms in graph yet</div>
                )}
              </div>
            </Card>

            <Card className="p-4">
              <h4 className="font-medium text-astronautwhite mb-3">Active Missions</h4>
              <div className="space-y-2">
                {nodes.filter((n: any) => n.type === 'mission').slice(0, 5).map((entity: any) => (
                  <div key={entity.id} className="p-2 rounded cursor-pointer hover:bg-accent/10 transition-colors border border-mission/10" onClick={() => setSelectedNode(entity)}>
                    <div className="text-sm font-medium text-astronautwhite truncate">{entity.label}</div>
                    <div className="text-xs text-mission">Mission</div>
                  </div>
                ))}
                {nodes.filter((n: any) => n.type === 'mission').length === 0 && (
                  <div className="text-xs text-astronautwhite/60 text-center py-2">No missions in graph yet</div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Laboratory;
