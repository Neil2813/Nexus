import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Brain, Search, Sparkles, Activity } from "lucide-react";
import { Button } from "./ui/button";

export const Navbar: React.FC = () => {
  const location = useLocation();
  const isActive = (p: string) => location.pathname === p;
  const navLinks = [
    { path: "/", label: "Mission Control", icon: Activity },
    { path: "/laboratory", label: "Laboratory", icon: Brain },
    { path: "/search", label: "Neural Search", icon: Search },
    { path: "/publication", label: "Publication Analysis", icon: Sparkles }
  ];
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/95 backdrop-blur-md border-b border-nexuscyan/20">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="NEXUS" className="h-10 w-auto" />
            <div>
              <div className="text-lg font-bold text-nexuscyan">NEXUS</div>
              <div className="text-xs text-astronautwhite/70">NASA Space Biology Knowledge Engine</div>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-2">
            {navLinks.map((ln) => {
              const Icon = ln.icon;
              return (
                <Link key={ln.path} to={ln.path}>
                  <Button 
                    variant={isActive(ln.path) ? "default" : "ghost"} 
                    className={isActive(ln.path) ? "bg-nexuscyan/20 text-nexuscyan border border-nexuscyan/50" : "text-astronautwhite/70 hover:text-nexuscyan hover:bg-nexuscyan/10"}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{ln.label}</span>
                  </Button>
                </Link>
              );
            })}
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-nexuscyan/10 border border-nexuscyan/30">
              <div className="w-2 h-2 rounded-full bg-nexuscyan animate-pulse" />
              <span className="text-xs text-nexuscyan font-medium">AI ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
