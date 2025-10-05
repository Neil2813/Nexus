import React from "react";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-space/90">
      <div className="text-center">
        <h1 className="mb-4 text-6xl font-bold text-astronautwhite">404</h1>
        <p className="mb-4 text-xl text-astronautwhite/70">Oops! Page not found</p>
        <Link to="/" className="text-accent underline">Return to Home</Link>
      </div>
    </div>
  );
};

export default NotFound;
