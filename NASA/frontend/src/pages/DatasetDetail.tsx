import React from "react";
import { useParams } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useDatasetMetadata, useDatasetFiles } from "@/hooks/useNasaData";
import { Card } from "@/components/ui/card";
import { FileText, Download, Database, Calendar, Microscope, Rocket } from "lucide-react";

const DatasetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const metaQ = useDatasetMetadata(id);
  const filesQ = useDatasetFiles(id);

  const meta = metaQ.data as any;
  const files = filesQ.data as any;

  return (
    <div className="min-h-screen bg-black pb-20">
      <Navbar />
      <div className="container mx-auto px-4 py-8 pt-24">
        <button 
          onClick={() => window.history.back()} 
          className="mb-6 text-sm text-astronautwhite/60 hover:text-astronautwhite transition-colors flex items-center gap-2"
        >
          ← Back to Dashboard
        </button>

        {/* Header Section */}
        <div className="mb-8 p-6 rounded-xl bg-black/30 backdrop-blur-md border border-neural/20">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-neural/20">
              <Database className="w-8 h-8 text-neural" />
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-astronautwhite mb-2">
                {meta?.title || meta?.['Study Title'] || id}
              </h1>
              <div className="flex flex-wrap gap-4 text-sm text-astronautwhite/70">
                <span className="flex items-center gap-1">
                  <Database className="w-4 h-4" />
                  Study ID: {id}
                </span>
                {meta?.organism && (
                  <span className="flex items-center gap-1">
                    <Microscope className="w-4 h-4" />
                    {meta.organism}
                  </span>
                )}
                {(meta?.mission || meta?.Mission?.Name) && (
                  <span className="flex items-center gap-1">
                    <Rocket className="w-4 h-4" />
                    {typeof meta.mission === 'string' ? meta.mission : meta.Mission?.Name}
                  </span>
                )}
                {meta?.release_date && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {new Date(meta.release_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Description & Objectives Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6 bg-black/30 backdrop-blur-md border-neural/20">
            <h2 className="text-xl font-semibold text-astronautwhite mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-neural" />
              Description
            </h2>
            {metaQ.isLoading ? (
              <div className="text-astronautwhite/60">Loading...</div>
            ) : (
              <div className="text-astronautwhite/80 leading-relaxed">
                {meta?.description || meta?.['Study Description'] || 'No description available.'}
              </div>
            )}
          </Card>

          <Card className="p-6 bg-black/30 backdrop-blur-md border-mission/20">
            <h2 className="text-xl font-semibold text-astronautwhite mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-mission" />
              Study Details
            </h2>
            {metaQ.isLoading ? (
              <div className="text-astronautwhite/60">Loading...</div>
            ) : (
              <div className="space-y-3 text-sm">
                {meta?.['Study Protocol Type'] && (
                  <div>
                    <span className="text-astronautwhite/60">Protocol Type:</span>
                    <div className="text-astronautwhite/90">{meta['Study Protocol Type']}</div>
                  </div>
                )}
                {meta?.['Study Assay Technology Type'] && (
                  <div>
                    <span className="text-astronautwhite/60">Assay Technology:</span>
                    <div className="text-astronautwhite/90">{meta['Study Assay Technology Type']}</div>
                  </div>
                )}
                {meta?.['Study Assay Measurement Type'] && (
                  <div>
                    <span className="text-astronautwhite/60">Measurement Type:</span>
                    <div className="text-astronautwhite/90">{meta['Study Assay Measurement Type']}</div>
                  </div>
                )}
                {meta?.['Study Factor Name'] && (
                  <div>
                    <span className="text-astronautwhite/60">Study Factor:</span>
                    <div className="text-astronautwhite/90">{meta['Study Factor Name']}</div>
                  </div>
                )}
                {meta?.['Managing NASA Center'] && (
                  <div>
                    <span className="text-astronautwhite/60">NASA Center:</span>
                    <div className="text-astronautwhite/90">{meta['Managing NASA Center']}</div>
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>

        {/* Metadata Section - Collapsible */}
        <details className="mb-6">
          <summary className="cursor-pointer text-lg font-semibold text-astronautwhite mb-2 hover:text-neural transition-colors">
            View Full Metadata (JSON)
          </summary>
          {metaQ.isLoading ? (
            <div className="text-astronautwhite/60">Loading metadata…</div>
          ) : meta ? (
            <pre className="bg-slate-900/50 p-4 rounded-lg overflow-auto text-xs text-astronautwhite/70 max-h-96">
              {JSON.stringify(meta, null, 2)}
            </pre>
          ) : (
            <div className="text-astronautwhite/60">No metadata found.</div>
          )}
        </details>

        {/* Files Section */}
        <Card className="p-6 bg-black/30 backdrop-blur-md border-neural/20">
          <h2 className="text-xl font-semibold text-astronautwhite mb-4 flex items-center gap-2">
            <Download className="w-5 h-5 text-neural" />
            Public Files
          </h2>
          {filesQ.isLoading ? (
            <div className="text-astronautwhite/60">Loading files…</div>
          ) : files && files.studies && Object.keys(files.studies).length > 0 ? (
            <>
              {Object.entries(files.studies).map(([k, v]: any) => (
                  <div key={k} className="mb-4">
                    <h3 className="font-medium text-astronautwhite mb-2">{k}</h3>
                    <div className="grid gap-2">
                      {(v.study_files || []).map((f: any, idx: number) => {
                        let url = f.remote_url || f.download_url || f.url || "";
                        if (url && url.startsWith("/")) {
                          // backend does not proxy files currently; we provide the backend path for user to call directly
                          url = `${(import.meta.env.VITE_API_BASE) || ""}/osdr/files/${encodeURIComponent(id || '')}`;
                        }
                        return (
                          <div key={idx} className="p-3 bg-slate-800/50 rounded-lg flex justify-between items-center hover:bg-slate-800 transition-colors border border-neural/10">
                            <div className="flex items-center gap-3">
                              <Download className="w-4 h-4 text-neural" />
                              <div>
                                <div className="font-medium text-astronautwhite">{f.file_name}</div>
                                <div className="text-xs text-astronautwhite/60">{f.category} • {f.file_size} bytes</div>
                              </div>
                            </div>
                            <div>
                              <a 
                                className="px-3 py-1 bg-neural/20 hover:bg-neural/30 rounded text-sm text-neural transition-colors" 
                                href={url.startsWith("http") ? url : `${(import.meta.env.VITE_API_BASE) || ""}/osdr/files/${encodeURIComponent(id || '')}`} 
                                target="_blank" 
                                rel="noreferrer"
                              >
                                Download
                              </a>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))
              }
            </>
          ) : (
            <div className="text-center py-8 text-astronautwhite/60">
              <Download className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-lg mb-2">No Public Files Available</p>
              <p className="text-sm">This study may have restricted access or files hosted externally.</p>
              <p className="text-xs mt-2">Visit <a href={`https://osdr.nasa.gov/bio/repo/data/studies/${id}`} target="_blank" rel="noreferrer" className="text-neural hover:underline">NASA OSDR</a> for more information.</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default DatasetDetail;
