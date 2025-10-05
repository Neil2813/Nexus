import React from "react";
import { Card } from "./ui/card";

interface Props {
  title: string;
  subtitle?: string;
  description?: string;
  onClick?: () => void;
}

const MissionCard: React.FC<Props> = ({ title, subtitle, description, onClick }) => {
  return (
    <Card 
      className="p-4 cursor-pointer hover:scale-[1.02] transition-all duration-300 bg-space/40 border border-neural/10 hover:border-neural/30 backdrop-blur-sm" 
      onClick={onClick}
    >
      <div className="space-y-2">
        <div className="font-semibold text-astronautwhite text-sm line-clamp-2">
          {title || "Untitled Study"}
        </div>
        {subtitle && (
          <div className="text-xs text-neural/80 font-medium">
            Mission: {subtitle}
          </div>
        )}
        {description && (
          <div className="text-xs text-astronautwhite/60 line-clamp-3">
            {description.length > 120 ? `${description.slice(0, 120)}...` : description}
          </div>
        )}
      </div>
    </Card>
  );
};

export default MissionCard;
