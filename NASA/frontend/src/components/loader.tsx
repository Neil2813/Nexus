import React from "react";

const Loader: React.FC<{ size?: number }> = ({ size = 28 }) => {
  return <div style={{ width: size, height: size }} className="animate-spin rounded-full border-4 border-accent/20 border-t-accent" />;
};

export default Loader;
