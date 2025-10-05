import { useQuery } from "@tanstack/react-query";
import { nasaApi } from "@/services/nasaApi";

export const useDatasets = (limit = 50) =>
  useQuery(["datasets", limit], () => nasaApi.getDatasets(limit), { staleTime: 1000 * 60 * 5 });

export const useOrganisms = () =>
  useQuery(["organisms"], () => nasaApi.getOrganisms(), { staleTime: 1000 * 60 * 60 });

export const useMissions = () =>
  useQuery(["missions"], () => nasaApi.getMissions(), { staleTime: 1000 * 60 * 60 });

export const useSearch = (filters?: any) =>
  useQuery(["search", filters], () => nasaApi.searchStudies(filters || {}), {
    enabled: !!(filters && (filters.query || (filters.organisms && filters.organisms.length) || (filters.missions && filters.missions.length))),
    staleTime: 1000 * 60 * 2
  });

export const useKnowledgeGraph = (limit = 100) =>
  useQuery(["graph", limit], () => nasaApi.getGraph(limit), { staleTime: 1000 * 60 * 5 });

export const useTimeline = () =>
  useQuery(["timeline"], () => nasaApi.getTimeline(), { staleTime: 1000 * 60 * 60 });

export const useInsights = () =>
  useQuery(["insights"], () => nasaApi.getInsights(), { staleTime: 1000 * 60 * 10 });

export const useDatasetMetadata = (studyId?: string) =>
  useQuery(["meta", studyId], () => nasaApi.getMetadata(studyId || ""), { enabled: !!studyId });

export const useDatasetFiles = (studyId?: string, page = 0, size = 25) =>
  useQuery(["files", studyId, page, size], () => nasaApi.getFiles(studyId || "", page, size), { enabled: !!studyId });
