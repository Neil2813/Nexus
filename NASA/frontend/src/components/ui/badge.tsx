import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-nexuscyan focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-nexuscyan text-black hover:bg-nexuscyan/80",
        secondary: "border-transparent bg-nexuscyan/20 text-nexuscyan hover:bg-nexuscyan/30",
        destructive: "border-transparent bg-red-500 text-white hover:bg-red-600",
        outline: "text-nexuscyan border-nexuscyan/30 hover:bg-nexuscyan/10",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
