import React from "react";
import { Link } from "react-router-dom";

export const QuickLaunchPod: React.FC<{ title: string; description: string; to?: string }> = ({ title, description, to }) => {
  const inner = (
    <div className="p-4 rounded-xl border border-accent/10 bg-space/40 hover:shadow-lg transition-all">
      <div className="font-semibold text-astronautwhite">{title}</div>
      <div className="text-xs text-astronautwhite/70">{description}</div>
    </div>
  );

  if (to) return <Link to={to}>{inner}</Link>;
  return inner;
};
