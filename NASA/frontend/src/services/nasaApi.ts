// centralised API client - uses backend you already have
const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8000/api";

async function handleResp<T>(r: Response): Promise<T> {
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`API ${r.status} ${r.statusText}: ${txt}`);
  }
  return (await r.json()) as T;
}

export interface Dataset {
  id: string;
  title?: string;
  description?: string;
  mission?: string;
  organism?: string;
  data_types?: string[];
  release_date?: string;
  study_type?: string;
  publications?: number;
  samples?: number;
  [k: string]: any;
}

export interface DatasetsResponse {
  data: Dataset[];
  count: number;  // Number of datasets in current response
  total?: number;  // Total available in OSDR (138,000+)
  page?: number;
  size?: number;
  limit?: number;
  source?: string;
  message?: string;
}

export interface InsightsResponse {
  insights?: string[];
  provider?: string;
  model?: string;
}

export interface SearchFilters {
  query?: string;
  organisms?: string[];
  missions?: string[];
}

class NasaApi {
  base = API_BASE;

  async getDatasets(limit = 50): Promise<DatasetsResponse> {
    const res = await fetch(`${this.base}/datasets?limit=${limit}`);
    return handleResp(res);
  }

  async searchStudies(filters: SearchFilters) {
    const res = await fetch(`${this.base}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filters || {})
    });
    return handleResp(res);
  }

  async getOrganisms() {
    const res = await fetch(`${this.base}/organisms`);
    return handleResp(res);
  }

  async getMissions() {
    const res = await fetch(`${this.base}/missions`);
    return handleResp(res);
  }

  async getGraph(limit = 100) {
    const res = await fetch(`${this.base}/graph?limit=${limit}`);
    return handleResp(res);
  }

  async getTimeline() {
    const res = await fetch(`${this.base}/timeline`);
    return handleResp(res);
  }

  async getInsights(): Promise<InsightsResponse> {
    const res = await fetch(`${this.base}/insights`, { method: "POST" });
    return handleResp(res);
  }

  async getMetadata(studyId: string) {
    const res = await fetch(`${this.base}/study/${encodeURIComponent(studyId)}`);
    return handleResp(res);
  }

  async getFiles(studyIds: string, page = 0, size = 25, all_files = false) {
    const url = `${this.base}/files/${encodeURIComponent(studyIds)}?page=${page}&size=${size}&all_files=${all_files}`;
    const res = await fetch(url);
    return handleResp(res);
  }

  async summarize(text: string) {
    const res = await fetch(`${this.base}/summarize?text=${encodeURIComponent(text)}`, { method: "POST" });
    return handleResp(res);
  }

  async health() {
    const res = await fetch(`${this.base}/health`);
    return handleResp(res);
  }
}

export const nasaApi = new NasaApi();
