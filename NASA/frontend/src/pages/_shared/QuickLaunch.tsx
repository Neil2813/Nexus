import React from "react";
import { Link } from "react-router-dom";

export const QuickLaunch: React.FC<{ to?: string; title: string; description: string }> = ({ to, title, description }) => {
  const inner = (
    <div className="p-4 rounded-xl border border-accent/10 bg-space/40 hover:shadow-lg transition-all">
      <div className="font-semibold text-astronautwhite">{title}</div>
      <div className="text-xs text-astronautwhite/70">{description}</div>
    </div>
  );
  if (to) return <Link to={to}>{inner}</Link>;
  return inner;
};
