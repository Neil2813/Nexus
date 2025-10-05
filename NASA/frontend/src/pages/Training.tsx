import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { useInsights } from "../hooks/useNasaData";
import { nasaApi } from "../services/nasaApi";

const Training: React.FC = () => {
  const { data: insights, refetch: refetchInsights } = useInsights();
  const [loading, setLoading] = useState(false);
  const [healthData, setHealthData] = useState<any>(null);

  const checkSystemHealth = async () => {
    setLoading(true);
    try {
      const health = await nasaApi.health();
      setHealthData(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthData({ error: 'Failed to check system health' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-space to-spacestation">
      <Navbar />
      <div className="container mx-auto px-4 py-8 pt-24">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-astronautwhite mb-2">AI TRAINING CONTROL CENTER</h1>
          <p className="text-lg text-astronautwhite/80">System monitoring and AI insights management</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6 bg-space/40 backdrop-blur-sm border border-neural/20">
            <h3 className="text-lg font-semibold text-astronautwhite mb-4 flex items-center gap-2">
              <div className="w-2 h-2 bg-neural rounded-full animate-pulse"></div>
              AI Insights System
            </h3>
            <p className="text-astronautwhite/70 mb-4">
              Real-time AI analysis of NASA space biology data with intelligent pattern recognition.
            </p>
            <div className="flex gap-2">
              <Button 
                onClick={() => refetchInsights()} 
                className="bg-neural hover:bg-neural/80 text-space"
              >
                Refresh Insights
              </Button>
            </div>
            {insights && (
              <div className="mt-4 p-3 bg-space/60 rounded-lg border border-neural/30">
                <p className="text-sm text-astronautwhite/80">
                  Current insights: {insights.insights?.length || 0} active
                </p>
                <Badge className="mt-2 bg-mission/20 text-mission border-mission/30">
                  Provider: {insights.provider || 'System'}
                </Badge>
              </div>
            )}
          </Card>

          <Card className="p-6 bg-space/40 backdrop-blur-sm border border-mission/20">
            <h3 className="text-lg font-semibold text-astronautwhite mb-4 flex items-center gap-2">
              <div className="w-2 h-2 bg-mission rounded-full animate-pulse"></div>
              System Health Monitor
            </h3>
            <p className="text-astronautwhite/70 mb-4">
              Monitor the health and status of all NASA data processing systems.
            </p>
            <div className="flex gap-2">
              <Button 
                onClick={checkSystemHealth} 
                disabled={loading}
                className="bg-mission hover:bg-mission/80 text-space"
              >
                {loading ? 'Checking...' : 'Run Health Check'}
              </Button>
            </div>
            {healthData && (
              <div className="mt-4 p-3 bg-space/60 rounded-lg border border-mission/30">
                {healthData.error ? (
                  <p className="text-red-400">Error: {healthData.error}</p>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        healthData.ok ? 'bg-green-400' : 'bg-red-400'
                      }`}></div>
                      <span className="text-sm text-astronautwhite">
                        System: {healthData.ok ? 'Healthy' : 'Issues Detected'}
                      </span>
                    </div>
                    <p className="text-xs text-astronautwhite/60">
                      Environment: {healthData.environment || 'Unknown'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Training;
