import React from "react";
import clsx from "clsx";

export const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "ghost" | "outline"; size?: "sm" | "md" | "lg" }> = ({
  children,
  variant = "default",
  size = "md",
  className,
  ...rest
}) => {
  return (
    <button
      {...rest}
      className={clsx(
        "rounded-xl transition-all font-semibold inline-flex items-center gap-2",
        variant === "default" && "bg-nexuscyan text-black px-4 py-2 hover:bg-nexuscyan/90",
        variant === "ghost" && "bg-transparent text-astronautwhite/70 hover:text-nexuscyan hover:bg-nexuscyan/10 px-3 py-1",
        variant === "outline" && "bg-transparent border border-nexuscyan/30 text-nexuscyan hover:bg-nexuscyan/10 px-3 py-1",
        size === "sm" && "text-sm",
        size === "lg" && "text-lg px-5 py-3",
        className
      )}
    >
      {children}
    </button>
  );
};
