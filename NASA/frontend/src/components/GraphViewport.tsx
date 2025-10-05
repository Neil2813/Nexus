import React, { useRef, useEffect } from "react";
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';


interface Props {
  nodes: any[];
  edges: any[];
  onNodeClick?: (node: any) => void;
}

const GraphViewport: React.FC<Props> = ({ nodes, edges, onNodeClick }) => {
  const cyRef = useRef<any>(null);

  const elements = [
    ...nodes.map((n: any) => ({ data: { id: n.id, label: n.label, type: n.type } })),
    ...edges.map((e: any) => ({ data: { id: e.id, source: e.source, target: e.target, label: e.label } }))
  ];

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current.cy;
    const handleTap = (evt: any) => {
      const node = evt.target;
      if (node.isNode && onNodeClick) onNodeClick(node.data());
    };
    cy.on("tap", "node", handleTap);
    return () => {
      cy.off("tap", "node", handleTap);
    };
  }, [onNodeClick]);

  return (
    <div className="w-full h-[520px]">
      <CytoscapeComponent
        elements={elements}
        style={{ width: "100%", height: "100%" }}
        stylesheet={[
          { selector: "node", style: { "background-color": "#00d1d1", label: "data(label)", color: "#fff", "text-wrap": "wrap", "text-valign": "center", width: 40, height: 40, "font-size": 10 } },
          { selector: "edge", style: { width: 2, "line-color": "#f5d0fe", "target-arrow-color": "#f5d0fe", "target-arrow-shape": "triangle", "curve-style": "bezier" } }
        ]}
        cy={(cy) => {
          cyRef.current = { cy };
          cy.layout({ name: "cose", animate: true, fit: true }).run();
        }}
      />
    </div>
  );
};

export default GraphViewport;
